#!/usr/bin/env python3
"""Fresh legacy/coverage verification: 021+029 gate, then a distinct 32 cohort.

Only new owned output roots are accepted. Prior queues are read-only; uncertain
deliveries are never resumed. --check-only does not call a model or browser.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import run_peekly_coverage as base

ROOT, SKILL = base.ROOT, base.SKILL
SMOKE_IDS = ("PER-PEEKLY-V2-021", "PER-PEEKLY-V2-029")
SMOKE_BASELINE_NOT_RUN = 2
DEFAULT_SMOKE = ROOT / ".ux-loop/peekly-completion-smoke-20261115"
DEFAULT_COHORT = ROOT / ".ux-loop/peekly-completion32-20261115"
FIXTURES = ROOT / ".ux-loop/peekly-coverage-fixtures-v8-20261115"
FIXTURE_MANIFEST_SHA = "9654fa6b07da5d443fbc97df16ab8885e170084ceda23399a36fbbd721997941"
SEED_SHA = "f4ea8b627d7b305552cf326205096aa244cf40a873fcbf275807947feec1a6f5"
VALIDATION_SHA = "8812e073064029937aaecb1908d0301eff96c2bee8794e3ee8ec6a6ddc46871c"
PRODUCT_COMMIT = "51110f4c569673faa8d242d5b85c4b47afb54cbb"
TURN_POLICY = dict(approved_ceiling=80, default_peekly=64, retention_and_paywall=80)
PINNED_FILES = {
    "peekly-sample-current.zip": "938514f0010f47ace5c2a2fdae17d2c237fd82838cedd78829e0915d367ca186",
    "peekly-sample-previous.zip": "b06f0fd115ab74703087e11f0c025df3791a09664cd03922a9fe182760fdc823",
    "peekly-legacy-unknown-state.json": SEED_SHA,
}
VALIDATION_CHECKS = (
    "known_empty_is_known", "legacy_excluded_from_selection",
    "legacy_snapshot_retained", "malformed_v7_rejected_without_legacy_fallback",
    "plain_v7_under_compression_threshold", "v6_missing_metadata_migrates_unknown",
    "v7_roundtrip_valid",
)


def validate_seed_catalog(manifest, frozen_files):
    """Verify the immutable, actual-product validation attestation offline."""
    seed = manifest.get("coverage", {}).get("legacy_seed", {})
    validation = seed.get("product_validation", {})
    raw = (json.dumps(validation, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n").encode()
    if (seed.get("schema_version") != "peekly-legacy-seed-fixture.v1"
            or seed.get("storage_key") != "peekly_state_v6"
            or seed.get("fixture_sha256") != SEED_SHA
            or seed.get("product_validation_sha256") != VALIDATION_SHA
            or hashlib.sha256(raw).hexdigest() != VALIDATION_SHA
            or seed.get("product_commit") != PRODUCT_COMMIT
            or validation.get("product_commit") != PRODUCT_COMMIT
            or validation.get("fixture_sha256") != SEED_SHA
            or any(validation.get("checks", {}).get(key) is not True for key in VALIDATION_CHECKS)
            or any(frozen_files.get(name) != sha for name, sha in PINNED_FILES.items())):
        raise RuntimeError("validated_legacy_seed_catalog_required")
    return dict(fixture_sha256=SEED_SHA, validation_sha256=VALIDATION_SHA,
                product_commit=PRODUCT_COMMIT, checks=validation["checks"])


def capture_freeze():
    value = base.capture_freeze(fixtures=FIXTURES, library=base.LIBRARY, build=base.BUILD)
    if value["fixtures"]["manifest_sha256"] != FIXTURE_MANIFEST_SHA:
        raise RuntimeError("completion_fixture_manifest_changed")
    manifest = base.read_json(FIXTURES / "fixture-manifest.json")
    value["legacy_seed_validation"] = validate_seed_catalog(manifest, value["fixtures"]["files"])
    for name in ("scripts/run_peekly_completion.py", "scripts/build_peekly_coverage_fixtures.py",
                 "scripts/validate_peekly_legacy_seed.mjs"):
        value["additional_sources"][name] = base.digest_file(ROOT / name)
    value["turn_policy"] = TURN_POLICY
    return value


def smoke_gate(summary, report, audit, *, router_ledger_sha256=None):
    gate = base.smoke_gate(summary, report, audit,
        router_ledger_sha256=router_ledger_sha256, persona_ids=SMOKE_IDS,
        baseline_not_run=SMOKE_BASELINE_NOT_RUN, success_units=6)
    reasons = list(gate["reasons"])
    targets = []
    for pid, requirement in zip(SMOKE_IDS, ("PRD-IMPORT-SNAPSHOT-UNKNOWN", "PRD-PAYWALL-BOUNDARY")):
        rows = [row for row in report.get("tasks", []) if row.get("persona_id") == pid]
        criteria = (rows[0].get("result") or {}).get("receipt", {}).get("criteria", []) if len(rows) == 1 else []
        target = [row for row in criteria if row.get("kind") == "success" and row.get("index") == 2]
        executed = (len(target) == 1 and target[0].get("status") in ("passed", "failed")
                    and bool(target[0].get("evidence_ids")))
        targets.append(dict(persona_id=pid, requirement=requirement, executed=executed,
                            criterion=target[0] if len(target) == 1 else None))
        if not executed:
            reasons.append("target_not_exercised:" + requirement)
    if gate["success_criteria"].get("not_run") != 0:
        reasons.append("all_six_success_criteria_must_be_exercised")
    gate.update(pass_gate=not reasons, reasons=sorted(set(reasons)), targeted_flows=targets,
                baseline_commit="65f52f78918d097c39ac8eb5ec49ed6daea537bc",
                policy="Both validated UNKNOWN and PAYWALL plus all six success criteria must be exercised. N/A and uncertainty earn no credit.")
    return gate


def require_passed_smoke(smoke_root, freeze):
    status = base.read_json(smoke_root / "run-status.json")
    provenance = base.read_json(smoke_root / "input-provenance.json")
    if status.get("state") != "smoke_passed" or provenance.get("stage") != "smoke":
        raise RuntimeError("passed_completion_smoke_required")
    base.require_same_freeze(provenance["freeze"], freeze)
    stage = smoke_root / "stage-2"
    for name, key in (("report.json", "report_sha256"), ("stage-summary.json", "summary_sha256"),
                      ("model-router-ledger.json", "router_ledger_sha256")):
        if base.digest_file(stage / name) != status.get(key):
            raise RuntimeError("completion_smoke_evidence_changed")
    audit = base.router_delivery_audit(base.read_json(stage / "model-router-ledger.json"))
    if audit != status.get("router_delivery_audit"):
        raise RuntimeError("completion_smoke_delivery_audit_changed")
    gate = smoke_gate(base.read_json(stage / "stage-summary.json"), base.read_json(stage / "report.json"),
                      audit, router_ledger_sha256=status["router_ledger_sha256"])
    if not gate["pass_gate"]:
        raise RuntimeError("completion_smoke_gate_failed:" + ",".join(gate["reasons"]))
    return dict(run_root=str(smoke_root), gate=gate, report_sha256=status["report_sha256"],
                summary_sha256=status["summary_sha256"], router_ledger_sha256=status["router_ledger_sha256"])


async def run(args):
    root = base.owned_output(args.run_root or (DEFAULT_SMOKE if args.stage == "smoke" else DEFAULT_COHORT))
    if root.exists():
        raise RuntimeError("run_root_exists_preserved")
    ids = list(SMOKE_IDS if args.stage == "smoke" else base.ALL_IDS)
    live = base.load_live()
    with live.Library(base.LIBRARY) as library:
        saved = [row for row in library.list("peekly")["personas"] if row.get("reusable")]
    base.exact_personas([row["persona_id"] for row in saved], base.ALL_IDS)
    freeze = capture_freeze()
    prior = base.snapshot_prior_queues(ROOT / ".ux-loop")
    forbidden = sorted({row["id"] for queue in prior for row in queue["jobs"]})
    goal = ("Coverage completion " + args.stage + " " + root.name
        + ": execute the complete saved current-PRD v3 journey in a fresh isolated owned context. "
        "Follow every per-criterion required-step checklist and validated fixture catalog. "
        "UNKNOWN personas must seed the validated legacy state first, then import only one current snapshot "
        "and verify exclusion before importing a second known snapshot. "
        "Do not skip applicable criteria or relabel unexecuted success N/A. "
        "This is a new independent evaluation, never a retry or resume of an uncertain operation. "
        "Use only TOKENMAXX/deepseek-v4.1-flash-free, concurrency 2, zero budget; "
        "64 turns per ordinary task, up to 80 for RETENTION plus PAYWALL. "
        "No real accounts, login, payment, external destination, deployment or paid fallback.")
    build_id = "peekly-completion-" + args.stage + "-" + root.name
    build = dict(id=build_id, artifact_path=str(base.BUILD.resolve()), sha256=base.BUILD_SHA256)
    revisions = {row["persona_id"]: row["revision"] for row in saved}
    job_ids = [live.scale_job_id("peekly", pid, revisions[pid], goal, build) for pid in ids]
    base.reject_reused_jobs(job_ids, forbidden)
    smoke = require_passed_smoke(base.owned_output(args.smoke_root), freeze) if args.stage == "cohort" else None
    provenance = dict(schema_version="peekly-completion-run.v1", created_at=base.now(), stage=args.stage,
        persona_ids=ids, job_ids=job_ids, build=build, freeze=freeze, library=str(base.LIBRARY),
        fixtures=str(FIXTURES), prior_queues=prior, forbidden_job_ids=forbidden, smoke=smoke,
        route=base.MODEL, parallel=2, turns=80, turn_policy=TURN_POLICY, budget_microusd=0,
        prior_queues_opened_read_only=True, uncertain_resend_authorized=False)
    compact = dict(stage=args.stage, run_root=str(root), sessions=len(ids), prior_queues=len(prior),
        forbidden_job_ids=len(forbidden), prior_uncertain_jobs=sum(len(q["uncertain_job_ids"]) for q in prior))
    if args.check_only:
        print(json.dumps(dict(compact, state="offline_preflight_passed", turn_policy=TURN_POLICY)), flush=True)
        return 0
    root.mkdir(mode=0o700)
    base.write_json(root / "input-provenance.json", provenance)
    state = dict(compact, state="running", started_at=base.now(),
                 input_provenance_sha256=base.digest_file(root / "input-provenance.json"))
    base.write_json(root / "run-status.json", state)
    print(json.dumps(state), flush=True)
    stage_args = SimpleNamespace(run_root=root, library=base.LIBRARY, product_id="peekly",
        url="http://127.0.0.1:4174/", target="Peekly owned local preview; pinned current PRD build 51110f4",
        goal=goal, build_id=build_id, build_artifact=base.BUILD, fixtures=FIXTURES,
        node=Path(live.NODE_DEFAULT), chrome=Path(live.CHROME_DEFAULT), turns=80, forbidden_job_ids=forbidden)
    try:
        try:
            with (root / "run.log").open("x") as log, contextlib.redirect_stdout(log):
                summary = await live.run_stage(stage_args, ids, len(ids))
        finally:
            state.update(base.prior_queue_integrity(prior))
        if not state["prior_queues_unchanged"]:
            raise RuntimeError("prior_queue_snapshot_changed_preserved")
        base.require_same_freeze(freeze, capture_freeze())
        stage = root / ("stage-" + str(len(ids)))
        report = base.read_json(stage / "report.json")
        audit = base.router_delivery_audit(base.read_json(stage / "model-router-ledger.json"))
        state.update(finished_at=base.now(), counts=report.get("counts"),
            completed_receipt_summary=report.get("completed_receipt_summary"),
            report_sha256=base.digest_file(stage / "report.json"),
            summary_sha256=base.digest_file(stage / "stage-summary.json"),
            router_ledger_sha256=base.digest_file(stage / "model-router-ledger.json"), router_delivery_audit=audit)
        if args.stage == "smoke":
            gate = smoke_gate(summary, report, audit, router_ledger_sha256=state["router_ledger_sha256"])
            base.write_json(root / "smoke-gate.json", gate)
            state.update(state="smoke_passed" if gate["pass_gate"] else "smoke_failed", gate_reasons=gate["reasons"])
            code = 0 if gate["pass_gate"] else 2
        else:
            if not audit["valid"] or audit["uncertain_resend_violations"] or summary.get("delivery_policy") != base.DELIVERY_POLICY:
                raise RuntimeError("completion_delivery_audit_failed_preserved")
            complete = report.get("completed_receipt_summary", {}).get("assessed_completed_sessions", 0)
            finished = (complete == 32 and report.get("counts", {}).get("complete") == 32
                        and audit["actual_attempt_receipts"] > 0 and audit["unsettled_guard_call_count"] == 0)
            state["state"] = "complete" if finished else "incomplete_preserved"
            code = 0 if finished else 2
        base.write_json(root / "run-status.json", state)
        print(json.dumps(dict(compact, state=state["state"], counts=state.get("counts"),
                             gate_reasons=state.get("gate_reasons"), finished_at=state["finished_at"])), flush=True)
        return code
    except Exception as exc:
        state.update(state="stopped_preserved", finished_at=base.now(), error_type=type(exc).__name__, reason=str(exc)[:240])
        base.write_json(root / "run-status.json", state)
        raise


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("smoke", "cohort"))
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--smoke-root", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(run(parse_args())))
    except Exception as exc:
        print(json.dumps(dict(state="blocked_preserved", error_type=type(exc).__name__, reason=str(exc)[:240])), file=sys.stderr)
        raise SystemExit(2)
