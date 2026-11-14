"""Offline regression tests: no provider, browser, or historical queue mutation."""
from __future__ import annotations

import asyncio
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("coverage_launcher", ROOT / "scripts/run_peekly_coverage.py")
launcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(launcher)


def clean_ledger():
    return dict(events=[dict(call_id="call-a", status="success"),
                        dict(call_id="call-b", status="success")],
                call_delivery={"call-a": "reply_received", "call-b": "reply_received"})


def audited_gate(summary, report, ledger=None):
    return launcher.smoke_gate(summary, report,
        launcher.router_delivery_audit(clean_ledger() if ledger is None else ledger))


def evidence(statuses=("failed", "passed", "not_run", "passed", "passed", "passed")):
    counts = dict(complete=2, queued=0, running=0, uncertain=0, blocked=0, cancelled=0)
    tasks = []
    for index, pid in enumerate(launcher.SMOKE_IDS):
        criteria = [dict(kind="success", index=i, status=value)
                    for i, value in enumerate(statuses[index * 3:index * 3 + 3])]
        tasks.append(dict(persona_id=pid, status="complete", current_valid=True,
                          result=dict(operational_completed=True, receipt=dict(outcome="failed", criteria=criteria))))
    success = {key: statuses.count(key) for key in ("passed", "failed", "not_run", "not_applicable")}
    completed = dict(completed_sessions=2, assessed_completed_sessions=2,
                     distinct_completed_personas=2, persona_ids=list(launcher.SMOKE_IDS),
                     excluded_attempt_statuses={}, host_protocol_on_completed_receipts=0,
                     criteria_by_kind=dict(success=success))
    report = dict(counts=counts, tasks=tasks, completed_receipt_summary=completed, operations=[])
    summary = dict(counts=copy.deepcopy(counts), sessions=2, persona_ids=list(launcher.SMOKE_IDS),
                   completed_receipt_summary=copy.deepcopy(completed), configured_routes=[launcher.MODEL],
                   fallback_model_attempts=0, browser_shutdown_confirmed=True,
                   delivery_policy=copy.deepcopy(launcher.DELIVERY_POLICY))
    return summary, report


class SmokeGateTests(unittest.TestCase):
    def test_reduced_not_run_passes_even_with_product_failure(self):
        summary, report = evidence()
        self.assertTrue(audited_gate(summary, report)["pass_gate"])

    def test_baseline_does_not_pass(self):
        summary, report = evidence(("failed", "passed", "not_run", "passed", "not_run", "not_run"))
        self.assertIn("not_run_did_not_decrease", audited_gate(summary, report)["reasons"])

    def test_na_cannot_replace_unexecuted_success(self):
        summary, report = evidence(("failed", "passed", "not_applicable", "passed", "passed", "passed"))
        self.assertIn("success_na_relabel_forbidden", audited_gate(summary, report)["reasons"])

    def test_partial_or_duplicate_personas_are_rejected(self):
        for mutation in ("partial", "duplicate"):
            with self.subTest(mutation=mutation):
                summary, report = evidence()
                if mutation == "partial":
                    report["tasks"][0]["current_valid"] = False
                else:
                    report["tasks"][1]["persona_id"] = launcher.SMOKE_IDS[0]
                self.assertFalse(audited_gate(summary, report)["pass_gate"])

    def test_host_and_uncertain_operation_are_not_ignored(self):
        summary, report = evidence()
        report["tasks"][0]["result"]["problem"] = "host_protocol"
        report["operations"] = [dict(state="uncertain")]
        gate = audited_gate(summary, report)
        self.assertIn("host_protocol_present", gate["reasons"])
        self.assertIn("unsettled_operation_preserved", gate["reasons"])

    def test_unsettled_queue_and_missing_criterion_are_rejected(self):
        summary, report = evidence()
        report["counts"]["uncertain"] = 1
        report["tasks"][0]["result"]["receipt"]["criteria"].pop()
        gate = audited_gate(summary, report)
        self.assertIn("unsettled_or_excluded_sessions", gate["reasons"])
        self.assertIn("missing_or_duplicate_success_criterion", gate["reasons"])

    def test_free_route_and_shutdown_are_required(self):
        summary, report = evidence()
        summary["configured_routes"] = ["unapproved"]
        summary["browser_shutdown_confirmed"] = False
        self.assertFalse(audited_gate(summary, report)["pass_gate"])


class RouterDeliveryAuditTests(unittest.TestCase):
    def test_timeout_then_success_and_other_uncertain_resends_are_rejected(self):
        uncertain_events = [dict(status="transport_or_protocol_error", error_type="TimeoutError"),
            dict(status="delivery_uncertain"), dict(status="http_error", http_status=408),
            dict(status="http_error", http_status=503), dict(status="success", delivery_state="uncertain")]
        for first in uncertain_events:
            with self.subTest(first=first):
                ledger = dict(events=[dict(first, call_id="call-a"),
                    dict(call_id="call-b", status="success"), dict(call_id="call-a", status="success")],
                    call_delivery={"call-a": "uncertain", "call-b": "reply_received"})
                audit = launcher.router_delivery_audit(ledger)
                self.assertEqual(audit["actual_attempt_receipts"], 3)
                self.assertEqual(audit["uncertain_resend_violations"], 1)
                self.assertEqual(audit["violation_call_ids"], ["call-a"])
                self.assertEqual(audit["violations"][0]["later_attempt_event_index"], 2)
                summary, report = evidence()
                self.assertIn("router_uncertain_resend_violation", audited_gate(summary, report, ledger)["reasons"])

    def test_known_quality_repair_is_distinct_from_uncertain_resend(self):
        ledger = dict(events=[dict(call_id="call-a", status="success", response_id="known-a"),
            dict(call_id="call-a", status="quality_rejected", response_id="known-a"),
            dict(call_id="call-a", status="success", response_id="known-b")],
            call_delivery={"call-a": "reply_received"})
        original = copy.deepcopy(ledger)
        audit = launcher.router_delivery_audit(ledger)
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["actual_attempt_receipts"], 2)
        self.assertEqual(audit["quality_diagnostic_count"], 1)
        self.assertEqual(audit["known_quality_repair_count"], 1)
        self.assertEqual(audit["uncertain_resend_violations"], 0)
        self.assertTrue(audited_gate(*evidence(), ledger)["pass_gate"])
        self.assertEqual(ledger, original)
        ledger["events"] = [dict(call_id="call-a", status="http_error", http_status=429),
                            dict(call_id="call-a", status="success")]
        self.assertEqual(launcher.router_delivery_audit(ledger)["known_reply_retry_count"], 1)
        self.assertTrue(audited_gate(*evidence(), ledger)["pass_gate"])

    def test_durable_intent_blocks_expansion_even_without_uncertain_receipt(self):
        ledger = clean_ledger()
        ledger["call_delivery"]["call-in-flight"] = "intent"
        audit = launcher.router_delivery_audit(ledger)
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["uncertain_resend_violations"], 0)
        self.assertEqual(audit["in_flight_guard_call_ids"], ["call-in-flight"])
        self.assertIn("router_unsettled_delivery_guard", audited_gate(*evidence(), ledger)["reasons"])

    def test_missing_or_invalid_guard_and_missing_audit_fail_closed(self):
        for guard in (None, [], {"call-a": "unknown"}, {"call-a": []}, {}):
            ledger = clean_ledger()
            ledger["call_delivery"] = guard
            self.assertFalse(launcher.router_delivery_audit(ledger)["valid"])
        summary, report = evidence()
        self.assertFalse(launcher.smoke_gate(summary, report)["pass_gate"])
        summary["delivery_policy"]["uncertain_resends"] = 1
        self.assertIn("router_delivery_policy_mismatch", audited_gate(summary, report)["reasons"])


class ProvenanceTests(unittest.TestCase):
    def test_default_smoke_uses_fresh_r3_and_cohort_references_it(self):
        self.assertEqual(launcher.DEFAULT_SMOKE.name, "peekly-coverage-smoke-r3-20261114")
        self.assertNotIn(launcher.DEFAULT_SMOKE.name,
                         ("peekly-coverage-smoke-20261114", "peekly-coverage-smoke-r2-20261114"))
        self.assertEqual(launcher.parse_args(["cohort"]).smoke_root, launcher.DEFAULT_SMOKE)

    def test_prior_queues_are_opened_read_only_and_uncertain_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stage = root / "old-run/stage-33"
            stage.mkdir(parents=True)
            path = stage / "queue.sqlite"
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE jobs(id TEXT,status TEXT,problem TEXT)")
                db.execute("CREATE TABLE operations(id TEXT,job_id TEXT,kind TEXT,state TEXT,problem TEXT)")
                db.executemany("INSERT INTO jobs VALUES(?,?,?)", [("old-a", "complete", None), ("old-b", "uncertain", "delivery_unknown")])
                db.execute("INSERT INTO operations VALUES('op-b','old-b','tool','uncertain','delivery_unknown')")
            before = path.read_bytes(), path.stat().st_mtime_ns
            original = sqlite3.connect
            opened = []
            def read_only_connect(database_uri, **kwargs):
                opened.append((database_uri, kwargs))
                db = original(database_uri, **kwargs)
                with self.assertRaises(sqlite3.OperationalError):
                    db.execute("UPDATE jobs SET status='queued'")
                db.rollback()
                return db
            with mock.patch.object(launcher.sqlite3, "connect", side_effect=read_only_connect):
                snapshots = launcher.snapshot_prior_queues(root)
            self.assertTrue(all(uri.endswith("?mode=ro") and options["uri"] for uri, options in opened))
            self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns), before)
            self.assertEqual(snapshots[0]["uncertain_job_ids"], ["old-b"])
            self.assertEqual(snapshots[0]["pending_operations"][0]["id"], "op-b")
            self.assertEqual(snapshots[0]["counts"], dict(complete=1, uncertain=1))
            fresh = root / "fresh-run/stage-2"
            fresh.mkdir(parents=True)
            # A newly created queue must not enter the old-queue integrity check.
            (fresh / "queue.sqlite").write_bytes(b"not an old queue")
            integrity = launcher.prior_queue_integrity(snapshots)
            self.assertTrue(integrity["prior_queues_unchanged"])
            self.assertEqual(integrity["prior_snapshot_before_sha256"], integrity["prior_snapshot_after_sha256"])
            with original(path) as db:
                db.execute("UPDATE jobs SET status='queued' WHERE id='old-b'")
            self.assertFalse(launcher.prior_queue_integrity(snapshots)["prior_queues_unchanged"])

    def test_duplicate_personas_and_reused_job_ids_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "identity_mismatch"):
            launcher.exact_personas([launcher.SMOKE_IDS[0]] * 2, launcher.SMOKE_IDS)
        with self.assertRaisesRegex(RuntimeError, "prior_job_identity_overlap"):
            launcher.reject_reused_jobs(["fresh", "old"], ["old"])
        with self.assertRaisesRegex(RuntimeError, "duplicate_new_job_identity"):
            launcher.reject_reused_jobs(["fresh", "fresh"], [])
        launcher.reject_reused_jobs(["fresh"], ["old"])

    def test_fixture_bytes_and_freeze_changes_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture = root / "fixture.zip"
            fixture.write_bytes(b"aaaa")
            manifest = dict(schema_version="peekly-synthetic-fixtures.v1",
                            files=[dict(name=fixture.name, bytes=4, sha256=hashlib.sha256(b"aaaa").hexdigest())])
            (root / "fixture-manifest.json").write_text(json.dumps(manifest))
            frozen = launcher.fixture_freeze(root)
            fixture.write_bytes(b"bbbb")
            with self.assertRaisesRegex(RuntimeError, "fixture_digest_mismatch"):
                launcher.fixture_freeze(root)
            with self.assertRaisesRegex(RuntimeError, "coverage_inputs_changed:engine_manifest"):
                launcher.require_same_freeze(dict(engine_manifest={"driver": "a"}, fixtures=frozen),
                                             dict(engine_manifest={"driver": "b"}, fixtures=frozen))

    def test_smoke_report_is_digest_bound_and_frozen_for_cohort(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stage = root / "stage-2"
            stage.mkdir()
            summary, report = evidence()
            launcher.write_json(stage / "report.json", report)
            launcher.write_json(stage / "stage-summary.json", summary)
            ledger = clean_ledger()
            launcher.write_json(stage / "model-router-ledger.json", ledger)
            freeze = dict(engine_manifest={"engine": "old"}, fixtures={"fixture": "hash"})
            launcher.write_json(root / "input-provenance.json", dict(stage="smoke", freeze=freeze))
            launcher.write_json(root / "run-status.json",
                                dict(state="smoke_passed", report_sha256=launcher.digest_file(stage / "report.json"),
                                     summary_sha256=launcher.digest_file(stage / "stage-summary.json"),
                                     router_ledger_sha256=launcher.digest_file(stage / "model-router-ledger.json"),
                                     router_delivery_audit=launcher.router_delivery_audit(ledger)))
            self.assertTrue(launcher.require_passed_smoke(root, freeze)["gate"]["pass_gate"])
            with self.assertRaisesRegex(RuntimeError, "coverage_inputs_changed"):
                launcher.require_passed_smoke(root, dict(freeze, engine_manifest={"engine": "new"}))
            modified = copy.deepcopy(ledger)
            modified["call_delivery"]["new-intent"] = "intent"
            launcher.write_json(stage / "model-router-ledger.json", modified)
            with self.assertRaisesRegex(RuntimeError, "smoke_evidence_changed"):
                launcher.require_passed_smoke(root, freeze)
            launcher.write_json(stage / "model-router-ledger.json", ledger)
            report["tasks"][0]["current_valid"] = False
            launcher.write_json(stage / "report.json", report)
            with self.assertRaisesRegex(RuntimeError, "smoke_evidence_changed"):
                launcher.require_passed_smoke(root, freeze)

    def test_check_only_never_calls_route_or_run_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".ux-loop").mkdir()
            saved = [dict(persona_id=pid, reusable=True, revision=2) for pid in launcher.ALL_IDS]
            library = mock.MagicMock()
            library.__enter__.return_value.list.return_value = dict(personas=saved)
            live = SimpleNamespace(Library=mock.Mock(return_value=library),
                                   scale_job_id=lambda product, pid, revision, goal, build: "new-" + pid,
                                   _route=mock.Mock(side_effect=AssertionError("provider_call_forbidden")),
                                   run_stage=mock.AsyncMock(side_effect=AssertionError("live_run_forbidden")))
            args = SimpleNamespace(stage="smoke", run_root=root / ".ux-loop/fresh", smoke_root=root / ".ux-loop/smoke",
                                   check_only=True)
            with mock.patch.object(launcher, "ROOT", root), mock.patch.object(launcher, "load_live", return_value=live), \
                 mock.patch.object(launcher, "capture_freeze", return_value={"engine": "frozen"}), \
                 mock.patch.object(launcher, "snapshot_prior_queues", return_value=[]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(asyncio.run(launcher.run(args)), 0)
                self.assertFalse(args.run_root.exists())
                args.run_root.mkdir()
                with self.assertRaisesRegex(RuntimeError, "run_root_exists_preserved"):
                    asyncio.run(launcher.run(args))
            live._route.assert_not_called()
            live.run_stage.assert_not_called()

    def test_cohort_preserves_uncertainty_but_never_completes_after_a_resend(self):
        for resend in (False, True):
            with self.subTest(resend=resend), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / ".ux-loop").mkdir()
                saved = [dict(persona_id=pid, reusable=True, revision=2) for pid in launcher.ALL_IDS]
                library = mock.MagicMock()
                library.__enter__.return_value.list.return_value = dict(personas=saved)
                ledger = dict(events=[dict(call_id="call-a", status="transport_or_protocol_error")],
                              call_delivery={"call-a": "uncertain"})
                if resend:
                    ledger["events"].append(dict(call_id="call-a", status="success"))
                report = dict(counts=dict(complete=32 if resend else 31, uncertain=0 if resend else 1),
                              completed_receipt_summary=dict(assessed_completed_sessions=32 if resend else 31))
                summary = dict(delivery_policy=copy.deepcopy(launcher.DELIVERY_POLICY))
                async def finish_owned_stage(args, ids, count):
                    stage = args.run_root / ("stage-" + str(count))
                    stage.mkdir()
                    for name, value in (("report.json", report), ("stage-summary.json", summary),
                                        ("model-router-ledger.json", ledger)):
                        launcher.write_json(stage / name, value)
                    return summary
                live = SimpleNamespace(Library=mock.Mock(return_value=library),
                    scale_job_id=lambda product, pid, revision, goal, build: "new-" + pid,
                    NODE_DEFAULT="/offline/node", CHROME_DEFAULT="/offline/chrome",
                    run_stage=mock.AsyncMock(side_effect=finish_owned_stage))
                args = SimpleNamespace(stage="cohort", run_root=root / ".ux-loop/fresh",
                                       smoke_root=root / ".ux-loop/smoke", check_only=False)
                with mock.patch.object(launcher, "ROOT", root), \
                     mock.patch.object(launcher, "load_live", return_value=live), \
                     mock.patch.object(launcher, "capture_freeze", return_value={"engine": "frozen"}), \
                     mock.patch.object(launcher, "snapshot_prior_queues", return_value=[]), \
                     mock.patch.object(launcher, "require_passed_smoke", return_value={"pass_gate": True}), \
                     contextlib.redirect_stdout(io.StringIO()):
                    if resend:
                        with self.assertRaisesRegex(RuntimeError, "router_delivery_audit_failed_preserved"):
                            asyncio.run(launcher.run(args))
                    else:
                        self.assertEqual(asyncio.run(launcher.run(args)), 2)
                status = launcher.read_json(args.run_root / "run-status.json")
                self.assertEqual(status["state"], "stopped_preserved" if resend else "incomplete_preserved")
                self.assertEqual(status["router_delivery_audit"]["uncertain_resend_violations"], int(resend))
                self.assertEqual(status["router_delivery_audit"]["uncertain_guard_call_ids"], ["call-a"])
                self.assertEqual(status["router_ledger_sha256"],
                                 launcher.digest_file(args.run_root / "stage-32/model-router-ledger.json"))


if __name__ == "__main__":
    unittest.main()
