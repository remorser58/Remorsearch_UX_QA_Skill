#!/usr/bin/env python3
"""Read-only audit of saved live Peekly queues; never dispatch a model/browser.

Keep queue closure, operational completion, evidence validity and UX outcomes
separate. Export hashes and scrubbed observations, never credentials or leases.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "skills/remorsearch-ux-qa"))
from uxpersonas.scale_report import current_report
from uxpersonas.swarm_queue import Queue
from uxresearch.canonical import EngineError

MODEL = "TOKENMAXX/deepseek-v4.1-flash-free"
SERVED = {MODEL, "deepseek-v4.1-flash-free", "deepseek-v4.1-flash"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(text):
    # Older capture adapters retained escaped line breaks/non-breaking spaces.
    text = str(text).replace("\\n", " ").replace("\\xa0", " ")
    return " ".join(unicodedata.normalize("NFKC", text).split())


def artifact_bytes(root, descriptor):
    root = Path(root).resolve(strict=True)
    relative = Path(descriptor["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("unsafe_artifact_path")
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("artifact_symlink")
    raw = path.read_bytes()
    if sha(raw) != descriptor["sha256"]:
        raise ValueError("artifact_digest_mismatch")
    if descriptor["kind"] == "screenshot" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("screenshot_not_png")
    return raw


def completion_counts(tasks):
    """A closed turn-limit task is NOT a successfully completed execution."""
    statuses = Counter(row["status"] for row in tasks)
    operational = sum((row.get("result") or {}).get("operational_completed") is True
                      for row in tasks)
    valid = sum(row.get("current_valid") is True for row in tasks)
    ux = Counter(row.get("current_ux_outcome") or "unassessed" for row in tasks)
    return {"assigned_sessions": len(tasks), "queue_statuses": dict(statuses),
        "queue_closed_complete": statuses["complete"],
        "operational_completed": operational,
        "not_operationally_completed": len(tasks) - operational,
        "current_valid_evidence_sessions": valid, "ux_outcomes": dict(ux)}


def usage_summary(ledger):
    """Quality rejection annotates an existing response, not a second send."""
    attempts = [event for event in ledger.get("events", [])
                if event.get("status") != "quality_rejected"]
    quality = [event for event in ledger.get("events", [])
               if event.get("status") == "quality_rejected"]
    recorded_attempts = sum(row["attempts"] for row in ledger.get("routes", {}).values())
    input_tokens = sum(event["input_tokens"] for event in attempts
                       if type(event.get("input_tokens")) is int)
    output_tokens = sum(event["output_tokens"] for event in attempts
                        if type(event.get("output_tokens")) is int)
    failures = sum(event.get("status") != "success" for event in attempts) + len(quality)
    known_requests = {event.get("requested_model") for event in attempts}
    providers = {event.get("provider") for event in attempts}
    errors = Counter(event.get("error_reason") or event.get("quality_reason") or event["status"]
                     for event in ledger.get("events", []) if event.get("status") != "success")
    known_usage = all(type(event.get("input_tokens")) is int and
                      type(event.get("output_tokens")) is int for event in attempts)
    discrepancies = []
    if recorded_attempts != len(attempts):
        discrepancies.append("dispatch_count_differs_from_terminal_attempt_receipts")
    for field, total in (("input_tokens", input_tokens), ("output_tokens", output_tokens)):
        if total != sum(row[field] for row in ledger.get("routes", {}).values()):
            discrepancies.append(field + "_counter_mismatch")
    receipts = [{key: event.get(key) for key in (
        "call_id", "response_id", "provider", "requested_model", "served_model",
        "status", "http_status", "input_tokens", "output_tokens",
        "provider_reported_cost", "billing_source", "elapsed_seconds")} for event in attempts]
    return {"recorded_dispatch_attempts": recorded_attempts,
        "terminal_attempt_receipts": len(attempts),
        "known_input_tokens": input_tokens, "known_output_tokens": output_tokens,
        "usage_complete": known_usage and not discrepancies,
        "transport_or_protocol_failures": sum(e.get("status") != "success" for e in attempts),
        "quality_rejections": len(quality), "failed_attempts_including_quality": failures,
        "failure_rate": failures / recorded_attempts if recorded_attempts else None,
        "http_429": sum(e.get("http_status") == 429 for e in attempts),
        "requested_models": sorted(x for x in known_requests if x),
        "providers": sorted(x for x in providers if x),
        "served_models": dict(Counter(e.get("served_model") or "not_reported" for e in attempts)),
        "approved_route_only": known_requests <= {MODEL} and providers <= {"TOKENMAXX"},
        "unexpected_served_names": sorted({e["served_model"] for e in attempts
            if e.get("served_model") and e["served_model"] not in SERVED}),
        "cost": {"basis": "user_confirmed_free_route_not_invoice_verification",
            "policy_usd": 0 if known_requests <= {MODEL} and providers <= {"TOKENMAXX"} else None,
            "missing_provider_cost_responses": sum(e.get("provider_reported_cost") is None for e in attempts),
            "provider_reported_cost_values": dict(Counter(json.dumps(e.get("provider_reported_cost")) for e in attempts)),
            "billing_source_values": dict(Counter(json.dumps(e.get("billing_source")) for e in attempts)),
            "provider_invoice_verified": False},
        "errors": dict(errors), "discrepancies": discrepancies, "attempt_receipts": receipts}


def latest_ledger(root):
    candidates = []
    for name in ("model-router-ledger.json", "model-router-ledger.live.json"):
        path = root / name
        if path.exists():
            raw = path.read_bytes()
            candidates.append((name, json.loads(raw), sha(raw)))
    if not candidates:
        raise ValueError("missing_model_usage_ledger")
    if len(candidates) == 2:
        a, b = candidates[0][1]["events"], candidates[1][1]["events"]
        if a != b[:len(a)] and b != a[:len(b)]:
            raise ValueError("ledger_histories_diverged")
    selected = max(candidates, key=lambda row: len(row[1]["events"]))
    return selected[1], {"selected": selected[0], "sha256": selected[2],
        "snapshots": {name: value for name, _, value in candidates},
        "late_ledger_append_observed": len({row[2] for row in candidates}) > 1}


def evidence_summary(root, task):
    result = task.get("result") or {}
    receipt = result.get("receipt") or task.get("receipt_preview") or {}
    session_root = root / "sessions" / task["job_id"]
    artifacts, observations, screenshots = [], [], 0
    for artifact in receipt.get("artifacts", []):
        raw = artifact_bytes(session_root, artifact)
        artifacts.append({**artifact, "path": (Path("sessions") / task["job_id"] / artifact["path"]).as_posix()})
        if artifact["kind"] == "screenshot":
            screenshots += 1
        elif artifact["kind"] == "execution_log":
            document = json.loads(raw)
            if document["context_id"] != task["context_id"] or document["binding"]["persona_id"] != task["persona_id"]:
                raise ValueError("observation_binding_mismatch")
            observation = document["observation"]
            observations.append((observation, artifacts[-1]))
    observations.sort(key=lambda pair: int(pair[0]["id"].split("-")[-1]))
    milestone = {"sample_result_seen": [], "manual_import_entry_seen": [],
        "management_control_offscreen": [], "import_result_seen": [],
        "post_import_connection_prompt": [], "single_snapshot_message_seen": []}
    viewports = set()
    for observation, log in observations:
        facts = observation["facts"]
        text = normalized(observation["text"])
        controls = facts.get("controls", [])
        viewport = facts.get("viewport", {})
        if viewport:
            viewports.add((viewport.get("width"), viewport.get("height")))
        anchor = {"observation_id": observation["id"], "log": log["path"],
            "log_sha256": log["sha256"],
            "captures": [{"id": c["id"], "sha256": c["sha256"]} for c in observation["captures"]]}
        has_relations = all(label in text for label in ("나를 맞팔", "내가 맞팔", "맞팔 중인"))
        if has_relations and "샘플" in text:
            milestone["sample_result_seen"].append(anchor)
        if any("이미 받은 자료로 확인하기" == normalized(c.get("label", "")) for c in controls):
            milestone["manual_import_entry_seen"].append(anchor)
        if any(normalized(c.get("label", "")) == "연결 관리와 다른 방법"
               and c.get("visible") is False for c in controls):
            milestone["management_control_offscreen"].append(anchor)
        imported = facts.get("last_action") == "upload" and "결과를 불러왔어요" in text and has_relations
        if imported:
            milestone["import_result_seen"].append(anchor)
        if has_relations and "샘플" not in text and "인스타를 한 번 연결" in text:
            milestone["post_import_connection_prompt"].append(anchor)
        if has_relations and "다음에 확인할 때" in text:
            milestone["single_snapshot_message_seen"].append(anchor)
    return {"png_files_verified": screenshots, "observation_logs_verified": len(observations),
        "viewports": [{"width": w, "height": h} for w, h in sorted(viewports)],
        "milestones": milestone, "artifacts": artifacts}


def audit_run(root):
    root = Path(root).resolve(strict=True)
    queue = Queue(root)
    with queue._db() as db:
        if db.execute("SELECT count(*) FROM jobs WHERE status='running'").fetchone()[0] or db.execute(
                "SELECT count(*) FROM operations WHERE state='intent'").fetchone()[0]:
            raise ValueError("run_still_inflight")
    report = current_report(queue)
    ledger, ledger_source = latest_ledger(root)
    usage = usage_summary(ledger)
    summary_path = root / "stage-summary.json"
    original_summary = json.loads(summary_path.read_bytes()) if summary_path.exists() else {}
    rows = []
    for task in report["tasks"]:
        result = task.get("result") or {}
        receipt = result.get("receipt") or task.get("receipt_preview") or {}
        rows.append({"persona_id": task["persona_id"], "job_id": task["job_id"],
            "context_id": task["context_id"], "queue_status": task["status"],
            "operational_completed": result.get("operational_completed") is True,
            "problem": result.get("problem") or task.get("problem"),
            "current_valid": task.get("current_valid"),
            "current_issue": task.get("current_issue"),
            "ux_outcome": task.get("current_ux_outcome") or "unassessed",
            "criterion_counts": dict(Counter(c["status"] for c in receipt.get("criteria", []))),
            "criteria": receipt.get("criteria", []),
            "first_judgment_sha256": result.get("first_judgment_sha256"),
            "same_persona_review": result.get("review"),
            "evidence": evidence_summary(root, task)})
    output = {"run_name": root.parent.name, "stage_name": root.name,
        "local_run_root": str(root), "mode": report["mode"],
        "counts": completion_counts(report["tasks"]),
        "elapsed_seconds": original_summary.get("elapsed_seconds"),
        "model_decisions_admitted": report["actual_model_calls"],
        "browser_calls_admitted": sum(o["kind"] == "tool" and o["state"] == "done" for o in report["operations"]),
        "close_receipts": sum(o["kind"] == "close" and o["state"] == "done" for o in report["operations"]),
        "browser_shutdown_confirmed": original_summary.get("browser_shutdown_confirmed"),
        "plan_sha256": queue.plan_sha256, "event_chain_head": queue.audit_events(),
        "engine_manifest": queue.plan["engine_manifest"],
        "build": queue.plan["build"], "limits": queue.plan["limits"],
        "fixture_manifest_sha256": original_summary.get("fixture_manifest_sha256"),
        "usage_ledger": ledger_source, "usage": usage, "sessions": rows,
        "product_ready": False, "real_user_evidence": False}
    output["evidence_totals"] = {key: sum(row["evidence"][key] for row in rows)
        for key in ("png_files_verified", "observation_logs_verified")}
    output["milestone_session_counts"] = {key: sum(bool(row["evidence"]["milestones"][key]) for row in rows)
        for key in ("sample_result_seen", "manual_import_entry_seen", "management_control_offscreen",
                    "import_result_seen", "post_import_connection_prompt", "single_snapshot_message_seen")}
    return output


def audit_many(roots):
    return {"schema_version": "peekly-live-scale-audit.v1",
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "audit_code_sha256": sha(Path(__file__).read_bytes()),
        "read_only": True, "new_model_or_browser_calls": 0,
        "runs": [audit_run(root) for root in roots],
        "limitations": [
            "Queue complete is not operational completion or a UX pass.",
            "Synthetic PRD-hypothesis personas are not human participants.",
            "Models receive text/DOM metadata, not screenshot pixels.",
            "Same-persona review is not independent assessment.",
            "These counts describe fixed synthetic tasks, not population prevalence.",
            "Raw provider cost omissions remain null; free policy comes from user authorization."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output_exists_preserved")
    result = audit_many(args.run)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"audit_output": str(args.output), "runs": len(result["runs"]),
        "sessions": sum(len(r["sessions"]) for r in result["runs"]),
        "new_model_calls": 0}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, EngineError) as exc:
        print(json.dumps({"audit": "blocked", "error_type": type(exc).__name__,
            "reason": getattr(exc, "issue", {}).get("code", str(exc))[:160]}), file=sys.stderr)
        raise SystemExit(2)
