"""Finalizer contracts with authored SQLite/files and mocked publish commands.

No real cohort is watched, no model/browser is launched, and no project commit,
push or external Git operation occurs in these tests.
"""
import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import finalize_peekly_completion as finalizer


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


class FinalizerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        self.run_root = self.repo / ".ux-loop/peekly-completion32-authored"
        self.stage = self.run_root / "stage-32"
        self.stage.mkdir(parents=True)
        self.output = self.repo / finalizer.OUTPUT
        self.log = self.repo / "authored-events.jsonl"
        self.freeze = dict(fixtures=dict(manifest_sha256="a" * 64), engine_manifest={"owned.py": "b" * 64})
        self.fixtures, self.library, self.build = (self.repo / name for name in ("fixtures", "library", "build.json"))
        self.prior = self.repo / ".ux-loop/old-authored/stage-32/queue.sqlite"
        self.prior.parent.mkdir(parents=True)
        with sqlite3.connect(self.prior) as db:
            db.execute("CREATE TABLE jobs(id TEXT,status TEXT,problem TEXT)")
            db.execute("INSERT INTO jobs VALUES('old-job','uncertain','preserved')")
        prior = finalizer.base.snapshot_prior_queues(self.repo / ".ux-loop", paths=[self.prior])
        self.provenance = dict(schema_version="peekly-completion-run.v1", stage="cohort",
            route=finalizer.base.MODEL, parallel=2, turns=80,
            turn_policy=finalizer.completion.TURN_POLICY, budget_microusd=0,
            prior_queues_opened_read_only=True, uncertain_resend_authorized=False,
            persona_ids=list(finalizer.base.ALL_IDS), job_ids=["job-" + str(i) for i in range(32)],
            forbidden_job_ids=["old-job"], prior_queues=prior, freeze=self.freeze,
            fixtures=str(self.fixtures), library=str(self.library),
            build=dict(artifact_path=str(self.build)))
        provider = dict(mode="live",
            spec=dict(model="tokenmaxx-deepseek-v4-1-flash-free",
                      input_price_per_million=0, output_price_per_million=0),
            billing_review=dict(requested_model=finalizer.base.MODEL, free_tier=True, billing_source="free",
                                input_price_per_million=0, output_price_per_million=0))
        jobs = [dict(id="job-" + str(i), task=dict(persona_id=pid))
                for i, pid in enumerate(finalizer.base.ALL_IDS)]
        self.plan = dict(mode="live", limits=dict(budget_microusd=0, parallel=2, turns=80),
                         providers={"local-router": provider}, jobs=jobs)
        self.ledger = dict(
            events=[dict(call_id="op-" + str(i), status="success", provider="TOKENMAXX",
                         requested_model=finalizer.base.MODEL, served_model="deepseek-v4.1-flash",
                         provider_reported_cost=None) for i in range(32)],
            call_delivery={"op-" + str(i): "reply_received" for i in range(32)},
            fallback_order=[finalizer.base.MODEL], routes={finalizer.base.MODEL: {
                "attempts": 32, "failures": 0, "quality_rejections": 0}})
        self.counts = dict(complete=32, uncertain=0, blocked=0, cancelled=0, queued=0, running=0)
        self.summary = dict(counts=self.counts, sessions=32, persona_ids=list(finalizer.base.ALL_IDS),
            browser_shutdown_confirmed=True, fixture_manifest_sha256="a" * 64,
            configured_routes=[finalizer.base.MODEL], fallback_model_attempts=0,
            delivery_policy=finalizer.base.DELIVERY_POLICY,
            model_attempts={route: dict(stats, failure_rate=0.0)
                            for route, stats in self.ledger["routes"].items()},
            cost_record=dict(authorized_route="user_confirmed_free_TOKENMAXX", policy_cost_usd=0,
                             provider_reported_cost_values=[None] * 32),
            provider_usage=[dict(provider="TOKENMAXX", model="deepseek-v4.1-flash",
                                 charged_or_estimated_microusd=0)])
        self.report = dict(counts=self.counts, plan_sha256=finalizer.digest(self.plan),
            tasks=[dict(job_id="job-" + str(i), persona_id=pid, provider="local-router", status="complete")
                   for i, pid in enumerate(finalizer.base.ALL_IDS)])
        with sqlite3.connect(self.stage / "queue.sqlite") as db:
            db.execute("CREATE TABLE jobs(id TEXT,status TEXT,provider TEXT)")
            db.execute("CREATE TABLE operations(id TEXT,job_id TEXT,kind TEXT,state TEXT)")
            db.execute("CREATE TABLE meta(key TEXT,value TEXT)")
            db.executemany("INSERT INTO jobs VALUES(?,?,?)",
                [("job-" + str(i), "complete", "local-router") for i in range(32)])
            db.executemany("INSERT INTO operations VALUES(?,?,?,?)",
                [("op-" + str(i), "job-" + str(i), "model", "done") for i in range(32)])
            db.execute("INSERT INTO meta VALUES('plan_sha',?)", (finalizer.digest(self.plan),))
        self.state = "complete"
        self.seal()
        for patcher in (
                mock.patch.object(finalizer.completion, "capture_freeze", side_effect=lambda: copy.deepcopy(self.freeze)),
                mock.patch.object(finalizer.completion, "FIXTURES", self.fixtures),
                mock.patch.object(finalizer.base, "LIBRARY", self.library),
                mock.patch.object(finalizer.base, "BUILD", self.build)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def seal(self):
        write(self.run_root / "input-provenance.json", self.provenance)
        write(self.stage / "plan.json", dict(plan=self.plan, sha256=finalizer.digest(self.plan)))
        write(self.stage / "report.json", self.report)
        write(self.stage / "stage-summary.json", self.summary)
        write(self.stage / "model-router-ledger.json", self.ledger)
        status = dict(state=self.state, counts=self.counts,
            router_delivery_audit=finalizer.base.router_delivery_audit(self.ledger),
            **finalizer.base.prior_queue_integrity(self.provenance["prior_queues"]))
        for field, path in (
            ("input_provenance_sha256", self.run_root / "input-provenance.json"),
            ("report_sha256", self.stage / "report.json"),
            ("summary_sha256", self.stage / "stage-summary.json"),
            ("router_ledger_sha256", self.stage / "model-router-ledger.json")):
            status[field] = finalizer.sha(path)
        write(self.run_root / "run-status.json", status)

    def inspect(self):
        return finalizer.inspect_terminal(self.repo, self.run_root)

    def uncertain(self):
        self.state = "incomplete_preserved"
        self.counts.update(complete=31, uncertain=1)
        self.report["tasks"][-1]["status"] = "uncertain"
        event = self.ledger["events"][-1]
        event.update(status="delivery_uncertain", delivery_state="uncertain", served_model=None)
        self.ledger["call_delivery"][event["call_id"]] = "uncertain"
        with sqlite3.connect(self.stage / "queue.sqlite") as db:
            db.execute("UPDATE jobs SET status='uncertain' WHERE id='job-31'")
            db.execute("UPDATE operations SET state='uncertain' WHERE id='op-31'")
        self.seal()

    def generated(self, bundle):
        def report(repo, stage, output, requested):
            self.assertEqual(requested, 32)
            write(output / "summary.json", dict(
                verification={key: True for key in ("terminal_queue", "prior_queues_unchanged",
                    "zero_uncertain_resends_verified", "browser_shutdown_confirmed")},
                candidate=dict(assessed_completed_sessions=self.counts["complete"],
                               criteria_all=dict(passed=88, failed=7, not_run=2, not_applicable=19)),
                baseline_23_mapping=dict(weighted_statuses=dict(passed=19, failed=1, not_run=2, unassessed=1))))
            (output / "comparison.md").write_text("Authored raw comparison.\n")
            write(output / "not-run-23-baseline.json", {"authored": True})
            return {"assessed": self.counts["complete"]}

        def audit(arguments, **kwargs):
            self.assertEqual(arguments[1], str(self.repo / finalizer.AUDITOR))
            self.assertEqual(arguments[2], str(self.stage))
            write(Path(arguments[3]), dict(audit_passed=True, mismatches=0,
                source_files_unchanged=True, prior_queues_unchanged=True,
                new_model_calls=0, new_browser_calls=0, queue_writes=0))
            return subprocess.CompletedProcess(arguments, 0, "", "")

        with mock.patch.object(finalizer.reporting, "build_report", side_effect=report), \
                mock.patch.object(finalizer.subprocess, "run", side_effect=audit):
            return finalizer.generate(self.repo, self.output, bundle, self.log)

    def test_read_only_terminal_accepts_actual_32_identity_and_preserves_db_bytes(self):
        before = {path: finalizer.sha(path) for path in (self.prior, self.stage / "queue.sqlite")}
        bundle = self.inspect()
        self.assertEqual(bundle["counts"]["complete"], 32)
        self.assertEqual(bundle["audit"]["uncertain_resend_violations"], 0)
        self.assertEqual(before, {path: finalizer.sha(path) for path in before})

    def test_summary_derived_rate_is_checked_without_inventing_a_raw_ledger_field(self):
        route = finalizer.base.MODEL
        self.assertNotIn("failure_rate", self.ledger["routes"][route])
        self.assertEqual(self.summary["model_attempts"][route]["failure_rate"], 0.0)
        self.assertTrue(finalizer.free_delivery(self.plan, self.summary, self.ledger)["valid"])
        self.summary["model_attempts"][route]["failure_rate"] = 0.25
        with self.assertRaises(finalizer.FinalizerError):
            finalizer.free_delivery(self.plan, self.summary, self.ledger)
        self.summary["model_attempts"][route]["failure_rate"] = 0.0
        self.ledger["routes"][route]["attempts"] = 33
        with self.assertRaises(finalizer.FinalizerError):
            finalizer.free_delivery(self.plan, self.summary, self.ledger)

    def test_uncertain_terminal_is_reported_raw_without_coverage_success_claim(self):
        self.uncertain()
        bundle = self.inspect()
        outcome = self.generated(bundle)
        self.assertEqual(outcome["queue_counts"]["uncertain"], 1)
        self.assertEqual(outcome["raw_candidate"]["assessed_sessions"], 31)
        self.assertEqual(outcome["semantic_review_status"], "pending_manual_review")
        self.assertIsNone(outcome["coverage_target_met"])
        self.assertFalse(outcome["automatic_verdict_overrides"])
        before = {name: (self.output / name).read_bytes() for name in finalizer.FILES}
        self.assertEqual(finalizer.generate(self.repo, self.output, bundle, self.log), outcome)
        self.assertEqual(before, {name: (self.output / name).read_bytes() for name in finalizer.FILES})

    def test_queued_job_or_missing_closure_fails_closed(self):
        self.counts.update(complete=31, queued=1)
        self.report["tasks"][-1]["status"] = "queued"
        with sqlite3.connect(self.stage / "queue.sqlite") as db:
            db.execute("UPDATE jobs SET status='queued' WHERE id='job-31'")
        self.seal()
        with self.assertRaisesRegex(finalizer.FinalizerError, "queue_not_terminal"):
            self.inspect()
        self.counts.update(complete=32, queued=0)
        self.report["tasks"][-1]["status"] = "complete"
        with sqlite3.connect(self.stage / "queue.sqlite") as db:
            db.execute("UPDATE jobs SET status='complete' WHERE id='job-31'")
        self.summary["browser_shutdown_confirmed"] = False
        self.seal()
        with self.assertRaisesRegex(finalizer.FinalizerError, "browser_closure"):
            self.inspect()

    def test_stale_hash_changed_source_and_changed_prior_queue_fail_closed(self):
        (self.stage / "report.json").write_text("{}")
        with self.assertRaisesRegex(finalizer.FinalizerError, "stale_terminal_hash"):
            self.inspect()
        self.seal()
        with mock.patch.object(finalizer.completion, "capture_freeze", return_value={}):
            with self.assertRaisesRegex(RuntimeError, "coverage_inputs_changed"):
                self.inspect()
        with sqlite3.connect(self.prior) as db:
            db.execute("UPDATE jobs SET status='complete'")
        with self.assertRaisesRegex(finalizer.FinalizerError, "prior_queue_snapshot_changed"):
            self.inspect()

    def test_unapproved_route_or_nonzero_cost_is_not_published_as_free(self):
        self.ledger["events"][0]["requested_model"] = "unapproved-model"
        self.seal()
        with self.assertRaisesRegex(finalizer.FinalizerError, "unapproved_or_priced_router_event"):
            self.inspect()
        self.ledger["events"][0]["requested_model"] = finalizer.base.MODEL
        self.summary["cost_record"]["provider_reported_cost_values"][0] = 0.01
        self.seal()
        with self.assertRaisesRegex(finalizer.FinalizerError, "cost_policy"):
            self.inspect()

    def test_uncertain_resend_and_live_queue_intent_are_rejected(self):
        self.uncertain()
        self.ledger["events"].append(dict(self.ledger["events"][-1], status="success"))
        self.seal()
        with self.assertRaisesRegex(finalizer.FinalizerError, "uncertain_resend"):
            self.inspect()
        self.ledger["events"].pop()
        self.seal()
        with sqlite3.connect(self.stage / "queue.sqlite") as db:
            db.execute("UPDATE operations SET state='intent' WHERE id='op-31'")
        with self.assertRaisesRegex(finalizer.FinalizerError, "unsettled_active_queue_intent"):
            self.inspect()

    def test_partial_output_is_preserved_and_existing_sealed_report_rejects_tampering(self):
        bundle = self.inspect()
        self.output.mkdir(parents=True)
        sentinel = self.output / "summary.json"
        sentinel.write_text("keep original")
        with mock.patch.object(finalizer.reporting, "build_report") as build:
            with self.assertRaisesRegex(finalizer.FinalizerError, "partial_output"):
                finalizer.generate(self.repo, self.output, bundle, self.log)
            build.assert_not_called()
        self.assertEqual(sentinel.read_text(), "keep original")
        sentinel.unlink()
        self.generated(bundle)
        sentinel.write_text("{}")
        with self.assertRaisesRegex(finalizer.FinalizerError, "existing_generated_file_changed"):
            finalizer.generate(self.repo, self.output, bundle, self.log)

    def test_check_only_never_waits_writes_or_calls_git_remote(self):
        args = finalizer.parse_args(["--run-root", str(self.run_root), "--check-only"])
        before = sorted(p.relative_to(self.repo).as_posix() for p in self.repo.rglob("*"))
        with mock.patch.object(finalizer.time, "sleep", side_effect=AssertionError("no wait")), \
                mock.patch.object(finalizer, "git", side_effect=AssertionError("no git")):
            result = finalizer.run(args, repo=self.repo)
        self.assertTrue(result["ready"])
        self.assertEqual(result["mutations"], 0)
        self.assertEqual(before, sorted(p.relative_to(self.repo).as_posix() for p in self.repo.rglob("*")))
        self.state = "running"
        self.seal()
        self.assertEqual(finalizer.run(args, repo=self.repo)["state"], "waiting_for_terminal")

    def test_bounded_wait_does_not_stop_or_mutate_worker(self):
        self.state = "running"
        self.seal()
        sleeps = []
        def settle(seconds):
            sleeps.append(seconds)
            status = finalizer.read_json(self.run_root / "run-status.json")
            status["state"] = "complete"
            write(self.run_root / "run-status.json", status)
        before = finalizer.sha(self.stage / "queue.sqlite")
        with mock.patch.object(finalizer.time, "sleep", side_effect=settle):
            status = finalizer.wait_terminal(self.run_root, self.log, poll_seconds=30)
        self.assertEqual(sleeps, [30])
        self.assertEqual(status["state"], "complete")
        self.assertEqual(before, finalizer.sha(self.stage / "queue.sqlite"))
        with self.assertRaisesRegex(finalizer.FinalizerError, "bounded_polling"):
            finalizer.wait_terminal(self.run_root, self.log, poll_seconds=31)

    def test_wrong_root_output_symlink_and_publish_branch_are_rejected(self):
        with self.assertRaises(finalizer.FinalizerError):
            finalizer.validate_paths(self.repo, self.repo / ".ux-loop/old-authored", self.output)
        with self.assertRaises(finalizer.FinalizerError):
            finalizer.validate_paths(self.repo, self.run_root, self.repo / "scripts")
        link = self.repo / ".ux-loop/peekly-completion32-link"
        link.symlink_to(self.run_root, target_is_directory=True)
        with self.assertRaisesRegex(finalizer.FinalizerError, "symlink"):
            finalizer.validate_paths(self.repo, link, self.output)
        with mock.patch.object(finalizer, "git", return_value=SimpleNamespace(stdout="wrong-branch\n")) as command:
            with self.assertRaisesRegex(finalizer.FinalizerError, "publish_branch_mismatch"):
                finalizer.publish_preflight(self.repo, self.output, finalizer.BRANCH)
            self.assertEqual(command.call_count, 1)
        with self.assertRaisesRegex(finalizer.FinalizerError, "explicit_exact_expected_branch"):
            finalizer.publish_preflight(self.repo, self.output, None)

    def test_unrelated_staged_and_unstaged_runtime_changes_are_preserved(self):
        def commands(repo, *args, **kwargs):
            output = finalizer.BRANCH + "\n" if args[0] == "branch" else ""
            if args[:3] == ("diff", "--cached", "--name-only"):
                output = "unrelated.txt\0"
            return SimpleNamespace(stdout=output, returncode=0, stderr="")
        with mock.patch.object(finalizer, "git", side_effect=commands):
            with self.assertRaisesRegex(finalizer.FinalizerError, "unrelated_staged"):
                finalizer.publish_preflight(self.repo, self.output, finalizer.BRANCH)
        def runtime(repo, *args, **kwargs):
            output = finalizer.BRANCH + "\n" if args[0] == "branch" else ""
            if args[:2] == ("diff", "--name-only"):
                output = "skills/remorsearch-ux-qa/uxpersonas/scale_run.py\0"
            return SimpleNamespace(stdout=output, returncode=0, stderr="")
        with mock.patch.object(finalizer, "git", side_effect=runtime):
            with self.assertRaisesRegex(finalizer.FinalizerError, "runtime_or_tests_dirty"):
                finalizer.publish_preflight(self.repo, self.output, finalizer.BRANCH)

    def test_publish_adds_only_generated_docs_and_requires_remote_sha_readback(self):
        bundle = self.inspect()
        self.generated(bundle)
        calls, staged = [], set()
        paths = sorted((self.output / name).relative_to(self.repo).as_posix() for name in finalizer.FILES)
        commit, old_remote = "c" * 40, "b" * 40
        state = {"committed": False, "pushed": False}
        def commands(repo, *args, **kwargs):
            calls.append(args)
            output = ""
            if args[0] == "branch":
                output = finalizer.BRANCH + "\n"
            elif args[:3] == ("diff", "--cached", "--name-only"):
                output = "\0".join(sorted(staged))
            elif args[0] == "status":
                output = "" if state["committed"] else "?? " + paths[0] + "\0"
            elif args[0] == "add":
                self.assertEqual(list(args[2:]), paths)
                staged.update(args[2:])
            elif args[0] == "commit":
                self.assertEqual(list(args[args.index("--")+1:]), paths)
                self.assertIn("--only", args)
                staged.clear()
                state["committed"] = True
            elif args[0] == "rev-parse":
                output = commit + "\n"
            elif args[0] == "log":
                output = "docs: record raw Peekly completion " + self.run_root.name + "\n"
            elif args[0] == "diff-tree":
                output = "\0".join(paths)
            elif args[0] == "ls-remote":
                output = (commit if state["pushed"] else old_remote) + "\trefs/heads/" + finalizer.BRANCH + "\n"
            elif args[0] == "push":
                self.assertEqual(args[1:], ("origin", commit + ":refs/heads/" + finalizer.BRANCH))
                state["pushed"] = True
            return SimpleNamespace(stdout=output, returncode=0, stderr="")
        before = {name: finalizer.sha(self.output / name) for name in finalizer.FILES}
        with mock.patch.object(finalizer, "git", side_effect=commands):
            result = finalizer.publish(self.repo, self.output, bundle, finalizer.BRANCH, self.log)
        self.assertEqual(result, commit)
        self.assertEqual(sum(args[0] == "push" for args in calls), 1)
        self.assertEqual(sum(args[0] == "ls-remote" for args in calls), 2)
        self.assertEqual(before, {name: finalizer.sha(self.output / name) for name in finalizer.FILES})
        event = json.loads(self.log.read_text().splitlines()[-1])
        self.assertEqual(event["state"], "published")
        self.assertEqual(event["remote_sha"], commit)
        self.assertEqual(event["semantic_review_status"], "pending_manual_review")

    def test_remote_mismatch_never_records_publication_or_retries_push(self):
        bundle = self.inspect()
        self.generated(bundle)
        paths = sorted((self.output / name).relative_to(self.repo).as_posix() for name in finalizer.FILES)
        calls, commit = [], "c" * 40
        def commands(repo, *args, **kwargs):
            calls.append(args)
            value = ""
            if args[0] == "branch":
                value = finalizer.BRANCH + "\n"
            elif args[0] == "log":
                value = "docs: record raw Peekly completion " + self.run_root.name + "\n"
            elif args[0] == "diff-tree":
                value = "\0".join(paths)
            elif args[0] == "rev-parse":
                value = commit + "\n"
            return SimpleNamespace(stdout=value, stderr="", returncode=0)
        with mock.patch.object(finalizer, "git", side_effect=commands), \
                mock.patch.object(finalizer, "remote_sha", side_effect=["b" * 40, "d" * 40]):
            with self.assertRaisesRegex(finalizer.FinalizerError, "remote_sha_not_confirmed"):
                finalizer.publish(self.repo, self.output, bundle, finalizer.BRANCH, self.log)
        self.assertEqual(sum(args[0] == "push" for args in calls), 1)
        self.assertFalse(any(args[0] in {"add", "commit"} for args in calls))
        events = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertFalse(any(event["state"] == "published" for event in events))


if __name__ == "__main__":
    unittest.main()
