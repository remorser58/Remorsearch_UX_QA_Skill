"""Read-only evidence audit of saved ScaleExecution stages; no model/browser calls."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "skills/remorsearch-ux-qa"))
from uxpersonas.scale_report import current_report
from uxpersonas.swarm_queue import Queue
from uxresearch.storage import safe_path

MODEL = "TOKENMAXX/deepseek-v4.1-flash-free"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_stage(root: Path) -> dict:
    queue = Queue(root)
    report = current_report(queue)  # Includes event chain, operation, PRD, persona and receipt audit.
    saved = json.loads((root / "stage-summary.json").read_text())
    ledger_path = root / "model-router-ledger.json"
    ledger = json.loads(ledger_path.read_text())
    if set(ledger["routes"]) != {MODEL} or ledger["fallback_order"] != [MODEL]:
        raise ValueError("unexpected_model_route")
    events = [event for event in ledger["events"] if event["status"] != "quality_rejected"]
    stats = ledger["routes"][MODEL]
    if stats["attempts"] != len(events):
        raise ValueError("unsettled_or_missing_attempt_receipt")
    if any(event.get("requested_model") != MODEL or event.get("provider") != "TOKENMAXX" for event in events):
        raise ValueError("unexpected_provider_receipt")
    input_tokens = sum(event.get("input_tokens") or 0 for event in events)
    output_tokens = sum(event.get("output_tokens") or 0 for event in events)
    if (input_tokens, output_tokens) != (stats["input_tokens"], stats["output_tokens"]):
        raise ValueError("token_ledger_mismatch")
    failure_count = stats["failures"] + stats["quality_rejections"]
    db = sqlite3.connect(f"file:{root / 'queue.sqlite'}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        checkpoints = {row["id"]: json.loads(row["checkpoint"])
            for row in db.execute("SELECT id, checkpoint FROM jobs")}
        operations = [dict(row) for row in db.execute(
            "SELECT id,job_id,kind,state,request,reply FROM operations ORDER BY started,id")]
    finally:
        db.close()
    sessions, evidence_index = [], []
    for task in report["tasks"]:
        job = task["job_id"]
        state = checkpoints[job]
        result = task.get("result") or {}
        receipt = result.get("receipt") or task.get("receipt_preview") or {}
        session_root = root / "sessions" / job
        observations = state.get("observations", [])
        png_count = log_count = uploads = 0
        actions = []
        for operation in operations:
            if operation["job_id"] != job or operation["kind"] != "tool":
                continue
            payload = json.loads(operation["request"])["payload"]
            name = payload["name"]
            actions.append({"operation_id": operation["id"], "tool": name, "state": operation["state"]})
            uploads += int(name == "upload" and operation["state"] == "done")
        for observation in observations:
            artifacts = []
            for artifact in observation["artifacts"]:
                path = safe_path(session_root / artifact["path"], session_root)
                if sha(path) != artifact["sha256"]:
                    raise ValueError("artifact_hash_mismatch")
                if artifact["kind"] == "screenshot":
                    if not path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
                        raise ValueError("capture_is_not_png")
                    png_count += 1
                elif artifact["kind"] == "execution_log":
                    log_count += 1
                artifacts.append({"kind": artifact["kind"], "path": str(path.relative_to(root)),
                                  "sha256": artifact["sha256"]})
            evidence_index.append({"job_id": job, "persona_id": task["persona_id"],
                "observation_id": observation["id"], "artifacts": artifacts})
        criteria_counts = Counter(item["status"] for item in receipt.get("criteria", []))
        sessions.append({"job_id": job, "persona_id": task["persona_id"],
            "status": task["status"], "problem": task["problem"] or result.get("problem"),
            "operational_completed": result.get("operational_completed") is True,
            "current_valid": task["current_valid"], "ux_outcome": task["current_ux_outcome"],
            "observations": len(observations), "pngs": png_count, "execution_logs": log_count,
            "completed_uploads": uploads, "criterion_status_counts": dict(criteria_counts),
            "actions": actions, "judgment": result.get("judgment")})
    normal = sum(row["operational_completed"] for row in sessions)
    ready = (normal == len(sessions) and report["counts"]["complete"] == len(sessions)
        and report["evidence_validation"]["current_valid_sessions"] == len(sessions)
        and saved["browser_shutdown_confirmed"] is True)
    return {"stage_endpoint": saved["stage_cumulative_sessions"], "new_sessions": len(sessions),
        "source_run_name": root.parent.name, "stage_name": root.name,
        "plan_sha256": queue.plan_sha256, "ledger_sha256": sha(ledger_path),
        "event_chain_head": report["event_chain_head"],
        "elapsed_seconds": saved["elapsed_seconds"], "counts": report["counts"],
        "operational_completed_sessions": normal, "expansion_gate_passed": ready,
        "current_evidence_validation": report["evidence_validation"],
        "model_attempts": stats["attempts"], "accepted_model_calls": report["actual_model_calls"],
        "model_failures": failure_count, "model_failure_rate": failure_count / stats["attempts"] if stats["attempts"] else None,
        "http_429": stats["rate_limits"], "input_tokens": input_tokens, "output_tokens": output_tokens,
        "unknown_usage_attempts": sum(type(e.get("input_tokens")) is not int or type(e.get("output_tokens")) is not int for e in events),
        "requested_model": MODEL, "provider": "TOKENMAXX",
        "served_models": dict(Counter(e.get("served_model") or "not_reported" for e in events)),
        "cost": {"policy_usd": 0, "basis": "user_confirmed_free_exact_request_route",
            "provider_reported_values": [e.get("provider_reported_cost") for e in events],
            "billing_source_values": [e.get("billing_source") for e in events],
            "missing_cost_responses": sum(e.get("provider_reported_cost") is None for e in events),
            "invoice_verified": False},
        "browser_shutdown_confirmed": saved["browser_shutdown_confirmed"],
        "sessions": sessions, "evidence_index": evidence_index}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = args.run_root.resolve()
    stages = [audit_stage(path) for path in sorted(root.glob("stage-*"),
        key=lambda path: int(path.name.split("-")[-1])) if (path / "stage-summary.json").exists()]
    ids = [session["persona_id"] for stage in stages for session in stage["sessions"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_persona_in_cohort")
    summary = {"schema_version": "peekly-live-scale-audit.v1", "stages": stages,
        "total_unique_personas": len(ids), "all_stage_gates_passed": bool(stages) and all(s["expansion_gate_passed"] for s in stages),
        "input_tokens": sum(s["input_tokens"] for s in stages),
        "output_tokens": sum(s["output_tokens"] for s in stages),
        "model_attempts": sum(s["model_attempts"] for s in stages),
        "model_failures": sum(s["model_failures"] for s in stages),
        "pngs_rehashed": sum(t["pngs"] for s in stages for t in s["sessions"]),
        "real_user_evidence": False, "product_ready": False}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({key: value for key, value in summary.items() if key != "stages"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
