#!/usr/bin/env python3
"""Fresh Peekly coverage stages: offline checks, two-person gate, then unique 32.

No resume or retry mode exists. Prior queues are read using SQLite mode=ro;
only run_stage creates and authorizes the new queue. --check-only contacts
neither the model gateway nor a browser.
"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/remorsearch-ux-qa"
MODEL = "TOKENMAXX/deepseek-v4.1-flash-free"
BUILD = Path("/Volumes/SanDisk2TB/m4mini/CodeProjects/insta-tracker/.omo/worktrees/peekly-import-ux-20261113/.ux-loop/peekly-build-manifest.json")
BUILD_SHA256 = "d5755c8912660cf80c0c9f48d18cc8952a3e7b46fe04e82e673f1eaa96b10beb"
ALL_IDS = tuple(f"PER-PEEKLY-V2-{i:03d}" for i in range(1, 33))
SMOKE_IDS = ("PER-PEEKLY-V2-016", "PER-PEEKLY-V2-029")
SMOKE_BASELINE_NOT_RUN = 3
SMOKE_SUCCESS_UNITS = 6
DEFAULT_SMOKE = ROOT / ".ux-loop/peekly-coverage-smoke-20261114"
DEFAULT_COHORT = ROOT / ".ux-loop/peekly-coverage32-20261114"
DEFAULT_FIXTURES = ROOT / ".ux-loop/peekly-coverage-fixtures-v6-20261114"
LIBRARY = ROOT / ".ux-loop/peekly-persona-library-v3"


def read_json(path):
    return json.loads(Path(path).read_text())


def digest_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_value(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    temporary.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def exact_personas(actual, expected):
    if len(actual) != len(set(actual)) or set(actual) != set(expected):
        raise RuntimeError("persona_cohort_identity_mismatch")


def reject_reused_jobs(job_ids, forbidden):
    if len(job_ids) != len(set(job_ids)):
        raise RuntimeError("duplicate_new_job_identity")
    if set(job_ids) & set(forbidden):
        raise RuntimeError("prior_job_identity_overlap")


def snapshot_prior_queues(base, *, paths=None):
    """Read a consistent metadata-only snapshot; never instantiate Queue here."""
    snapshots = []
    selected = Path(base).rglob("queue.sqlite") if paths is None else (Path(path) for path in paths)
    for path in sorted(selected):
        if not path.parent.name.startswith("stage-"):
            continue
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=2) as db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA query_only = ON")
            db.execute("BEGIN")
            jobs = [dict(row) for row in db.execute("SELECT id,status,problem FROM jobs ORDER BY id")]
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            pending = []
            if "operations" in tables:
                pending = [dict(row) for row in db.execute(
                    "SELECT id,job_id,kind,state,problem FROM operations "
                    "WHERE state IN ('intent','uncertain') ORDER BY id")]
        value = dict(path=str(path.resolve()), counts=dict(sorted(Counter(row["status"] for row in jobs).items())),
                     jobs=jobs, uncertain_job_ids=[row["id"] for row in jobs if row["status"] == "uncertain"],
                     pending_operations=pending)
        value["snapshot_sha256"] = digest_value(value)
        snapshots.append(value)
    return snapshots


def prior_queue_integrity(prior):
    """Compare only pre-existing queues; the fresh stage is intentionally excluded."""
    before = {row["path"]: row["snapshot_sha256"] for row in prior}
    after = snapshot_prior_queues(ROOT / ".ux-loop", paths=before)
    after = {row["path"]: row["snapshot_sha256"] for row in after}
    return dict(prior_queues_unchanged=before == after,
                prior_snapshot_before_sha256=digest_value(before),
                prior_snapshot_after_sha256=digest_value(after))


def fixture_freeze(fixtures):
    fixtures = Path(fixtures).resolve()
    manifest_path = fixtures / "fixture-manifest.json"
    manifest = read_json(manifest_path)
    rows = manifest.get("files")
    if manifest.get("schema_version") != "peekly-synthetic-fixtures.v1" or not isinstance(rows, list) or not rows:
        raise RuntimeError("peekly_fixture_manifest_invalid")
    hashes = {}
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or name in hashes:
            raise RuntimeError("fixture_name_invalid_or_duplicate")
        path = (fixtures / name).resolve()
        if not path.is_relative_to(fixtures) or not path.is_file():
            raise RuntimeError("fixture_file_missing_or_outside_root")
        if type(row.get("bytes")) is not int or path.stat().st_size != row["bytes"]:
            raise RuntimeError("fixture_size_mismatch:" + name)
        actual = digest_file(path)
        if actual != row.get("sha256"):
            raise RuntimeError("fixture_digest_mismatch:" + name)
        hashes[name] = actual
    return dict(manifest_sha256=digest_file(manifest_path), files=hashes)


def capture_freeze(fixtures=DEFAULT_FIXTURES, library=LIBRARY, build=BUILD):
    from uxpersonas.scale_entry import engine_manifest
    if not Path(build).is_file() or digest_file(build) != BUILD_SHA256:
        raise RuntimeError("pinned_product_build_artifact_missing_or_changed")
    extra_sources = (
        "scripts/run_peekly_coverage.py",
        "skills/remorsearch-ux-qa/scripts/live_scale_browser.py",
        "skills/remorsearch-ux-qa/uxpersonas/scale_browser_host.py",
        "skills/remorsearch-ux-qa/drivers/web/scale_browser_cdp.mjs",
    )
    return dict(engine_manifest=engine_manifest(),
                additional_sources={name: digest_file(ROOT / name) for name in extra_sources},
                fixtures=fixture_freeze(fixtures), library_sha256=digest_file(Path(library) / "library.json"),
                build_sha256=digest_file(build))


def require_same_freeze(before, after):
    if before != after:
        changed = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
        raise RuntimeError("coverage_inputs_changed:" + ",".join(changed))


def smoke_gate(summary, report):
    """Coverage gate: failed product criteria count as executed; N/A cannot hide them."""
    reasons = []
    counts = report.get("counts", {})
    completed = report.get("completed_receipt_summary", {})
    tasks = report.get("tasks", [])
    if counts != summary.get("counts") or counts.get("complete") != 2:
        reasons.append("queue_completion_mismatch")
    if any(counts.get(key) != 0 for key in ("queued", "running", "uncertain", "blocked", "cancelled")):
        reasons.append("unsettled_or_excluded_sessions")
    if sum(counts.values()) != 2:
        reasons.append("unexpected_queue_denominator")
    if summary.get("sessions") != 2 or sorted(summary.get("persona_ids", [])) != list(SMOKE_IDS):
        reasons.append("stage_personas_mismatch")
    if completed != summary.get("completed_receipt_summary"):
        reasons.append("completed_summary_mismatch")
    if any(completed.get(key) != 2 for key in
           ("completed_sessions", "assessed_completed_sessions", "distinct_completed_personas")):
        reasons.append("completed_valid_receipts_required")
    if completed.get("persona_ids") != list(SMOKE_IDS) or completed.get("excluded_attempt_statuses"):
        reasons.append("completed_personas_or_exclusions_mismatch")
    if sorted(row.get("persona_id", "") for row in tasks) != list(SMOKE_IDS):
        reasons.append("receipt_personas_mismatch")
    actual = Counter()
    for row in tasks:
        result = row.get("result") or {}
        receipt = result.get("receipt")
        if row.get("status") != "complete" or row.get("current_valid") is not True or result.get("operational_completed") is not True or not isinstance(receipt, dict):
            reasons.append("invalid_or_partial_receipt")
            continue
        criteria = [criterion for criterion in receipt.get("criteria", []) if criterion.get("kind") == "success"]
        if sorted(criterion.get("index", -1) for criterion in criteria) != [0, 1, 2]:
            reasons.append("missing_or_duplicate_success_criterion")
        actual.update(criterion.get("status") for criterion in criteria)
    success = completed.get("criteria_by_kind", {}).get("success", {})
    expected_statuses = ("passed", "failed", "not_run", "not_applicable")
    if any(type(success.get(key)) is not int or success[key] < 0 for key in expected_statuses):
        reasons.append("invalid_success_counts")
    elif (sum(success.values()) != SMOKE_SUCCESS_UNITS
          or any(actual[key] != success[key] for key in expected_statuses)
          or any(key not in expected_statuses for key in actual)):
        reasons.append("success_denominator_mismatch")
    else:
        if success["not_applicable"] != 0:
            reasons.append("success_na_relabel_forbidden")
        if success["not_run"] >= SMOKE_BASELINE_NOT_RUN:
            reasons.append("not_run_did_not_decrease")
    host = sum(any("host_protocol" in str(value) for value in
                   (row.get("problem"), row.get("current_issue"), (row.get("result") or {}).get("problem")))
               for row in tasks)
    if host or completed.get("host_protocol_on_completed_receipts") != 0:
        reasons.append("host_protocol_present")
    if any(op.get("state") in ("intent", "uncertain") for op in report.get("operations", [])):
        reasons.append("unsettled_operation_preserved")
    if summary.get("configured_routes") != [MODEL] or summary.get("fallback_model_attempts") != 0:
        reasons.append("free_route_mismatch")
    if summary.get("browser_shutdown_confirmed") is not True:
        reasons.append("browser_shutdown_unconfirmed")
    return dict(pass_gate=not reasons, reasons=sorted(set(reasons)), persona_ids=list(SMOKE_IDS),
                baseline_success_not_run=SMOKE_BASELINE_NOT_RUN, success_criteria=success,
                completed_receipt_summary=completed, host_protocol_count=host)


def require_passed_smoke(smoke_root, freeze):
    smoke_root = Path(smoke_root)
    status = read_json(smoke_root / "run-status.json")
    provenance = read_json(smoke_root / "input-provenance.json")
    if status.get("state") != "smoke_passed" or provenance.get("stage") != "smoke":
        raise RuntimeError("passed_smoke_required")
    require_same_freeze(provenance["freeze"], freeze)
    stage = smoke_root / "stage-2"
    if any(digest_file(stage / name) != status.get(key) for name, key in
           (("report.json", "report_sha256"), ("stage-summary.json", "summary_sha256"))):
        raise RuntimeError("smoke_evidence_changed")
    gate = smoke_gate(read_json(stage / "stage-summary.json"), read_json(stage / "report.json"))
    if not gate["pass_gate"]:
        raise RuntimeError("smoke_coverage_gate_failed:" + ",".join(gate["reasons"]))
    return dict(run_root=str(smoke_root.resolve()), report_sha256=status["report_sha256"],
                summary_sha256=status["summary_sha256"], gate=gate)


def load_live():
    # Importing the runner is offline; its _route is invoked only by run_stage.
    path = SKILL / "scripts/live_scale_browser.py"
    spec = importlib.util.spec_from_file_location("peekly_coverage_live", path)
    live = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(live)
    return live


def owned_output(path):
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT / ".ux-loop").resolve()) or path == (ROOT / ".ux-loop").resolve():
        raise RuntimeError("coverage_output_must_be_under_owned_ux_loop")
    return path


async def run(args):
    run_root = owned_output(args.run_root or (DEFAULT_SMOKE if args.stage == "smoke" else DEFAULT_COHORT))
    if run_root.exists():
        raise RuntimeError("run_root_exists_preserved")
    ids = list(SMOKE_IDS if args.stage == "smoke" else ALL_IDS)
    exact_personas(ids, SMOKE_IDS if args.stage == "smoke" else ALL_IDS)
    live = load_live()
    with live.Library(LIBRARY) as library:
        saved = [row for row in library.list("peekly")["personas"] if row.get("reusable")]
    exact_personas([row["persona_id"] for row in saved], ALL_IDS)
    freeze = capture_freeze()
    prior = snapshot_prior_queues(ROOT / ".ux-loop")
    forbidden = sorted({row["id"] for queue in prior for row in queue["jobs"]})
    label = run_root.name
    goal = ("Coverage repair " + args.stage + " " + label + ": execute the complete saved current-PRD v3 journey in a fresh isolated owned context. "
            "Follow the per-criterion required-step checklist and verified fixture catalog. Do not skip applicable success criteria or relabel unexecuted criteria N/A. "
            "This is a new independent reviewed evaluation, never a retry or resume of a prior uncertain operation. "
            "Only TOKENMAXX/deepseek-v4.1-flash-free, concurrency 2, 64 bounded turns, zero budget. "
            "No real accounts, login, payment, external destination, deployment, paid fallback or native iOS action.")
    build_id = "peekly-coverage-" + args.stage + "-" + label
    build = dict(id=build_id, artifact_path=str(BUILD.resolve()), sha256=BUILD_SHA256)
    revisions = {row["persona_id"]: row["revision"] for row in saved}
    job_ids = [live.scale_job_id("peekly", pid, revisions[pid], goal, build) for pid in ids]
    reject_reused_jobs(job_ids, forbidden)
    prior_smoke = require_passed_smoke(owned_output(args.smoke_root), freeze) if args.stage == "cohort" else None
    provenance = dict(schema_version="peekly-coverage-run.v1", created_at=now(), stage=args.stage,
                      persona_ids=ids, job_ids=job_ids, build=build, freeze=freeze,
                      library=str(LIBRARY.resolve()), fixtures=str(DEFAULT_FIXTURES.resolve()),
                      prior_queues=prior, forbidden_job_ids=forbidden, smoke=prior_smoke,
                      route=MODEL, parallel=2, turns=64, budget_microusd=0,
                      prior_queues_opened_read_only=True, uncertain_resend_authorized=False)
    compact = dict(stage=args.stage, run_root=str(run_root), sessions=len(ids),
                   prior_queues=len(prior), forbidden_job_ids=len(forbidden),
                   prior_uncertain_jobs=sum(len(queue["uncertain_job_ids"]) for queue in prior))
    if args.check_only:
        print(json.dumps(dict(compact, state="offline_preflight_passed"), ensure_ascii=False), flush=True)
        return 0
    run_root.mkdir(mode=0o700)
    write_json(run_root / "input-provenance.json", provenance)
    state = dict(compact, state="running", started_at=now(), input_provenance_sha256=digest_file(run_root / "input-provenance.json"))
    write_json(run_root / "run-status.json", state)
    print(json.dumps(state, ensure_ascii=False), flush=True)
    stage_args = SimpleNamespace(run_root=run_root, library=LIBRARY, product_id="peekly",
        url="http://127.0.0.1:4174/", target="Peekly owned local web preview; exact current PRD build 51110f4",
        goal=goal, build_id=build_id, build_artifact=BUILD, fixtures=DEFAULT_FIXTURES,
        node=Path(live.NODE_DEFAULT), chrome=Path(live.CHROME_DEFAULT), turns=64, forbidden_job_ids=forbidden)
    try:
        try:
            with (run_root / "run.log").open("x") as log, contextlib.redirect_stdout(log):
                summary = await live.run_stage(stage_args, ids, len(ids))
        finally:
            state.update(prior_queue_integrity(prior))
        if not state["prior_queues_unchanged"]:
            raise RuntimeError("prior_queue_snapshot_changed_preserved")
        require_same_freeze(freeze, capture_freeze())
        stage_root = run_root / ("stage-" + str(len(ids)))
        report = read_json(stage_root / "report.json")
        state.update(finished_at=now(), counts=report.get("counts"),
                     completed_receipt_summary=report.get("completed_receipt_summary"),
                     report_sha256=digest_file(stage_root / "report.json"),
                     summary_sha256=digest_file(stage_root / "stage-summary.json"))
        if args.stage == "smoke":
            gate = smoke_gate(summary, report)
            write_json(run_root / "smoke-gate.json", gate)
            state["state"] = "smoke_passed" if gate["pass_gate"] else "smoke_failed"
            state["gate_reasons"] = gate["reasons"]
            code = 0 if gate["pass_gate"] else 2
        else:
            complete = report.get("completed_receipt_summary", {}).get("assessed_completed_sessions", 0)
            state["state"] = "complete" if complete == 32 and report.get("counts", {}).get("complete") == 32 else "incomplete_preserved"
            code = 0 if state["state"] == "complete" else 2
        write_json(run_root / "run-status.json", state)
        print(json.dumps(state, ensure_ascii=False), flush=True)
        return code
    except Exception as exc:
        state.update(state="stopped_preserved", finished_at=now(), error_type=type(exc).__name__, reason=str(exc)[:240])
        write_json(run_root / "run-status.json", state)
        raise


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("smoke", "cohort"))
    parser.add_argument("--run-root", type=Path, help="Fresh owned .ux-loop root; never reuse an existing root.")
    parser.add_argument("--smoke-root", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--check-only", action="store_true", help="Run offline gates only, with no model or browser call.")
    return parser.parse_args(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(run(parse_args())))
    except Exception as exc:
        print(json.dumps(dict(state="blocked_preserved", error_type=type(exc).__name__, reason=str(exc)[:240]), ensure_ascii=False), file=sys.stderr, flush=True)
        raise SystemExit(2)
