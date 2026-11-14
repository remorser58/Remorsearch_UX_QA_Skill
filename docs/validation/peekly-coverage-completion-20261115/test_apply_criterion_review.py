"""Offline contract regressions; synthetic files/SQLite only, no model/browser."""
import copy
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("completion_criterion_review", HERE / "apply_criterion_review.py")
reviewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewer)
old = reviewer.old
digest = reviewer.digest


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return value


def source(repo, path):
    sha, size = reviewer.file_hash(path)
    return dict(path=path.relative_to(repo).as_posix(), sha256=sha, bytes=size)


class ReviewFixture:
    def __init__(self, repo, *, unreviewed_inconclusive=False, reviewed_raw_status="passed",
                 final_judgment=True, result_problem=None, task_problem=None):
        self.repo = repo
        self.stage = repo / ".ux-loop/peekly-completion32-test/stage-32"
        self.stage.mkdir(parents=True)
        self.output = repo / "docs/validation/peekly-coverage-completion-20261115"
        self.output.mkdir(parents=True)
        self.local_script = self.output / "apply_criterion_review.py"
        self.local_script.write_bytes((HERE / "apply_criterion_review.py").read_bytes())
        jobs = []
        for n in range(1, 33):
            jid, pid = "J" + str(n).zfill(3), "PER-PEEKLY-V2-" + str(n).zfill(3)
            requirements = ["REQ-" + str(n).zfill(3) + "-" + str(i) for i in range(4 if n <= 8 else 3)]
            task = dict(id=jid, persona_id=pid, success_criteria=requirements, recovery_criteria=["conditional"],
                        requirement_coverage=[dict(requirement_id=rid, obligations=[
                            dict(criterion_refs=[dict(kind="success", index=i)])])
                            for i, rid in enumerate(requirements)])
            binding = dict(persona_id=pid, revision=1, profile_sha256="a" * 64, prd_sha256="b" * 64)
            jobs.append(dict(id=jid, task=task, binding=binding, provider="local-router"))
        plan = dict(schema_version="fixture-scale-plan", jobs=jobs, mode="live", build=dict(sha256="c" * 64))
        self.plan = dict(plan=plan, sha256=digest(plan))
        tasks, dbrows, audited = [], [], []
        self.observations = {}
        for job in jobs:
            jid, pid = job["id"], job["binding"]["persona_id"]
            context = "ctx-" + digest([self.plan["sha256"], jid])[:40]
            task = dict(job_id=jid, persona_id=pid, provider="local-router", context_id=context,
                        status="uncertain" if jid == "J002" else "complete", current_valid=jid != "J002",
                        current_ux_outcome=None, problem="model_delivery_uncertain" if jid == "J002" else None,
                        result=None, result_sha256=None)
            checkpoint = dict(observations=[])
            if jid != "J002":
                directory = self.stage / "sessions" / jid / "evidence" / jid / "1"
                directory.mkdir(parents=True)
                png = directory / "capture.png"; png.write_bytes(b"offline-png-byte-binding-" + jid.encode())
                png_artifact = dict(id="png-1-0", kind="screenshot",
                    path="evidence/" + jid + "/1/capture.png", sha256=reviewer.file_hash(png)[0])
                observation = dict(id="obs-1", action="Inspect synthetic result", text="Observed result",
                                   facts={"synthetic": True}, checks=[], captures=[png_artifact])
                self.observations[jid] = observation
                log = directory / "observation.json"
                write_json(log, dict(schema_version="ux-agent-observation.v1",
                    binding=job["binding"], context_id=context, observation=observation))
                log_artifact = dict(id="log-1", kind="execution_log",
                    path="evidence/" + jid + "/1/observation.json", sha256=reviewer.file_hash(log)[0])
                observation["artifacts"] = [log_artifact, png_artifact]
                criteria = [dict(kind="success", index=i, status="passed",
                    observation="Raw observed result", evidence_ids=["log-1"])
                    for i in range(len(job["task"]["success_criteria"]))]
                criteria.append(dict(kind="recovery", index=0, status="not_applicable",
                                     observation="No recoverable failure", evidence_ids=["log-1"]))
                if jid=="J001":
                    criteria[0]["status"]=reviewed_raw_status
                    task["problem"]=task_problem
                raw_outcome=reviewer.outcome(criteria)
                if (unreviewed_inconclusive and jid=="J003") or (
                    jid=="J001" and (not final_judgment or result_problem or task_problem)
                    and raw_outcome!="failed"):
                    raw_outcome="inconclusive"
                receipt = dict(task_id=jid, outcome=raw_outcome, persona_revision=1,
                    profile_sha256=job["binding"]["profile_sha256"], build_sha256=plan["build"]["sha256"],
                    artifacts=[log_artifact, png_artifact], criteria=criteria)
                first = {"outcome": raw_outcome, "synthetic_review": True}
                result = dict(operational_completed=True, receipt=receipt, ux_outcome=raw_outcome,
                              first_judgment=first, first_judgment_sha256=digest(first),
                              judgment=(None if jid=="J001" and not final_judgment
                                        else {"reason":"Synthetic valid final judgment"}),
                              problem=result_problem if jid=="J001" else None)
                checkpoint.update(observations=[observation], first_judgment=first, first_judgment_sha256=digest(first))
                task.update(result=result, result_sha256=digest(result), current_ux_outcome=raw_outcome)
                audited.append(dict(job_id=jid, persona_id=pid, result_sha256=digest(result),
                    checkpoint_sha256=digest(checkpoint), first_judgment_sha256=digest(first),
                    registered_artifacts=2, all_registered_artifacts_checked=True))
            tasks.append(task)
            dbrows.append((jid, task["status"], json.dumps(task["result"]) if task["result"] else None,
                           task["result_sha256"], json.dumps(checkpoint), digest(checkpoint)))
        self.report = dict(tasks=tasks, counts=dict(complete=31, uncertain=1, running=0, queued=0),
                           plan_sha256=self.plan["sha256"])
        completed = old.recompute_completed_summary(self.report)
        self.report["completed_receipt_summary"] = copy.deepcopy(completed)
        self.summary = dict(sessions=32, persona_ids=[j["binding"]["persona_id"] for j in jobs],
            counts=self.report["counts"], operational_completed_sessions=31,
            browser_shutdown_confirmed=True, completed_receipt_summary=copy.deepcopy(completed))
        write_json(self.stage / "plan.json", self.plan)
        write_json(self.stage / "report.json", self.report)
        write_json(self.stage / "stage-summary.json", self.summary)
        write_json(self.stage / "model-router-ledger.json", {"events": []})
        write_json(self.stage.parent / "input-provenance.json", {"fixture": "offline"})
        write_json(self.stage.parent / "run-status.json", {"state": "incomplete_preserved"})
        with sqlite3.connect(self.stage / "queue.sqlite") as db:
            db.execute("CREATE TABLE jobs(id TEXT,status TEXT,result TEXT,result_sha TEXT,checkpoint TEXT,checkpoint_sha TEXT)")
            db.executemany("INSERT INTO jobs VALUES(?,?,?,?,?,?)", dbrows)
            db.execute("CREATE TABLE meta(key TEXT,value TEXT)")
            db.execute("INSERT INTO meta VALUES('plan_sha',?)", (self.plan["sha256"],))
        self.candidate = old.summarize_candidate(self.report, self.summary, self.plan, 32,
                                                 self.stage.relative_to(repo).as_posix())
        def baseline_row(n, ident, kind="success"):
            return dict(id=ident, queue="old/stage", job="old-" + str(n),
                persona="PER-PEEKLY-V2-" + str(n).zfill(3), kind=kind,
                requirement=("CONDITIONAL-RECOVERY" if kind == "recovery" else "REQ-" + str(n).zfill(3) + "-0"),
                reason="Old not_run")
        self.original = dict(rows=[baseline_row(n, "NR46-" + str(i)) for i,n in enumerate(
            list(range(1,33)) + list(range(1,15)), 1)])
        self.remaining = dict(schema_version="peekly-remaining-baseline.v1",
            rows=[baseline_row(n, "NR23-" + str(n), "recovery" if n == 3 else "success") for n in range(1,24)])
        write_json(repo / old.NOT_RUN, self.original)
        write_json(self.output / "not-run-23-baseline.json", self.remaining)
        self.history = [reviewer.reporting.comparison_column("historical-" + str(n), self.candidate, [])
                        for n in range(4)]
        sourcepaths = [self.stage / name for name in ("queue.sqlite", "plan.json", "report.json",
                                                     "stage-summary.json", "model-router-ledger.json")]
        sourcepaths += [self.stage.parent / name for name in ("run-status.json", "input-provenance.json")]
        self.audit = dict(schema_version="peekly-artifact-byte-audit.v1",
            audit_passed=True, mismatches=0, source_files_unchanged=True, prior_queues_unchanged=True,
            stage=self.stage.relative_to(repo).as_posix(), new_model_calls=0, new_browser_calls=0, queue_writes=0,
            jobs=audited, assessed_sessions=31, sources=[source(repo,p) for p in sourcepaths])
        write_json(self.output / "artifact-audit.json", self.audit)
        delivery_audit = dict(valid=True, actual_attempt_receipts=0, known_reply_retry_count=0,
            known_quality_repair_count=0, quality_diagnostic_count=0, uncertain_resend_violations=0,
            uncertain_event_call_ids=[], uncertain_guard_call_ids=[], in_flight_guard_call_ids=[],
            violation_call_ids=[], errors=[])
        self.raw = dict(schema_version="peekly-completion-comparison.v1",
            candidate=self.candidate,
            comparison_columns=self.history + [reviewer.reporting.comparison_column("fresh",self.candidate,[])],
            baseline_46_mapping=old.map_baseline(self.original,self.candidate),
            baseline_23_mapping=old.map_baseline(self.remaining,self.candidate),
            provider_cost=dict(configured_routes=["free"], attempted_routes={}, fallback_model_attempts=0,
                policy_cost_usd=0, missing_cost_responses=0, provider_invoice_verified=False, disclosure="offline fixture"),
            router_delivery=dict(configured_policy=old.DELIVERY_POLICY, policy_matches_expected=True,
                audit=delivery_audit, zero_uncertain_resends_verified=True,
                ledger_source_ref=source(repo,self.stage / "model-router-ledger.json"), disclosure="offline fixture"),
            verification=dict.fromkeys(("terminal_queue","prior_queues_unchanged",
                                        "zero_uncertain_resends_verified","browser_shutdown_confirmed"),True),
            sources=[source(repo,p) for p in sourcepaths], limitations=[])
        self.refresh_raw()
        task = tasks[0]
        arts = task["result"]["receipt"]["artifacts"]
        self.review = dict(schema_version="peekly-completion-criterion-review.v1",
            stage_root=self.stage.relative_to(repo).as_posix(), plan_sha256=self.plan["sha256"],
            raw_summary_sha256=reviewer.file_hash(self.output / "summary.json")[0],
            artifact_audit_sha256=reviewer.file_hash(self.output / "artifact-audit.json")[0],
            scope="Offline contract fixture, never real product evidence.",
            raw_receipts_modified=False, new_model_calls=0, new_browser_calls=0, queue_writes=0,
            decisions=[dict(job_id="J001",persona_id="PER-PEEKLY-V2-001",kind="success",index=0,
                requirement_id="REQ-001-0",result_sha256=task["result_sha256"],
                expected_raw_status=reviewed_raw_status,reviewed_status="failed",
                reason="Authored test decision supported by admitted test evidence.",
                classifications=["product_defect","judge_false_pass"],
                evidence=[dict(artifact_id=a["id"],path=a["path"],sha256=a["sha256"],
                               observation_id="obs-1",purpose="result") for a in arts])])
        self.review_path = self.output / "criterion-review.json"
        self.save_review()

    def refresh_raw(self):
        self.raw=json.loads(json.dumps(self.raw,sort_keys=True))
        write_json(self.output / "summary.json",self.raw)
        (self.output / "comparison.md").write_text(reviewer.reporting.render_markdown(self.raw))
        paths = dict(provenance=self.stage.parent / "input-provenance.json",
                     status=self.stage.parent / "run-status.json",report=self.stage / "report.json",
                     summary=self.stage / "stage-summary.json",envelope=self.stage / "plan.json",
                     ledger=self.stage / "model-router-ledger.json")
        write_json(self.output / "automated-outcome.json",dict(
            schema_version="peekly-completion-automated-outcome.v1",
            semantic_review_status="pending_manual_review",
            postprocess_status="raw_report_and_byte_audit_completed",coverage_target_met=None,
            run_root=self.stage.parent.relative_to(self.repo).as_posix(),
            generated_files={name:reviewer.file_hash(self.output / name)[0] for name in reviewer.RAW_FILES[:-1]},
            source_hashes={name:reviewer.file_hash(path)[0] for name,path in paths.items()}))

    def save_review(self):
        write_json(self.review_path,self.review)

    def run(self):
        self.save_review()
        with patch.object(reviewer,"historical",return_value=(copy.deepcopy(self.history),copy.deepcopy(self.remaining))), \
             patch.object(reviewer,"__file__",str(self.local_script)):
            return reviewer.build(self.repo,self.stage,self.output,self.review_path)


class ReviewContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = ReviewFixture(Path(self.temp.name).resolve())

    def refuse(self, reason):
        with self.assertRaisesRegex((reviewer.ReviewError,old.ReportError),reason):
            self.fixture.run()
        self.assertFalse(any((self.fixture.output / name).exists() for name in reviewer.OUTPUTS))

    def test_five_columns_recomputed_raw_immutable_and_na_separate_from_uncertain(self):
        f=self.fixture
        rawhash={name:reviewer.file_hash(f.output / name) for name in reviewer.RAW_FILES}
        result=f.run()
        reviewed=json.loads((f.output / "reviewed-summary.json").read_text())
        self.assertEqual(result["changed_criteria"],1)
        self.assertEqual(reviewed["comparison_columns"][:4],f.history)
        self.assertEqual(reviewed["candidate"]["assessed_completed_sessions"],31)
        self.assertEqual(reviewed["candidate"]["session_outcomes"]["failed"],1)
        self.assertEqual(reviewed["candidate"]["session_outcomes"]["passed"],30)
        self.assertEqual(reviewed["candidate"]["unassessed_attempts"],f.candidate["unassessed_attempts"])
        changed=next(c for c in reviewed["candidate"]["criteria"] if c["job_id"]=="J001" and c["kind"]=="success" and c["index"]==0)
        self.assertEqual(len(changed["raw_evidence"]),1)
        self.assertEqual(len(changed["evidence"]),2)
        mapping=reviewed["reviewed_coverage"]["baseline_23"]
        self.assertEqual(mapping["weighted"]["counts"],dict(passed=20,failed=1,not_run=0,not_applicable=1,unassessed=1))
        self.assertEqual(mapping["weighted"]["executed"],21)
        self.assertEqual(mapping["weighted"]["independently_reviewed_executed"],1)
        self.assertEqual(reviewed["reviewed_coverage"]["baseline_46"]["weighted_count"],46)
        self.assertEqual(reviewed["reviewed_coverage"]["baseline_46"]["unique_count"],32)
        self.assertEqual(rawhash,{name:reviewer.file_hash(f.output / name) for name in reviewer.RAW_FILES})

    def test_unchanged_decision_records_scope_without_adding_coverage(self):
        self.fixture.review["decisions"][0]["reviewed_status"]="passed"
        self.fixture.review["decisions"][0]["classifications"]=["confirmed_raw_verdict"]
        result=self.fixture.run()
        self.assertEqual(result["changed_criteria"],0)
        self.assertEqual(result["old23"]["executed"],21)
        self.assertEqual(result["old23"]["independently_reviewed_executed"],1)

    def test_unlisted_session_outcome_is_never_implicitly_promoted(self):
        f=ReviewFixture(Path(self.temp.name).resolve()/"unlisted",unreviewed_inconclusive=True)
        result=f.run()
        value=json.loads((f.output/"reviewed-summary.json").read_text())
        session=next(s for s in value["candidate"]["sessions"] if s["job_id"]=="J003")
        self.assertEqual(session["outcome"],"inconclusive")
        self.assertEqual(result["session_outcomes"]["inconclusive"],1)
        self.assertEqual({row["job_id"] for row in value["independent_review"]["session_changes"]},{"J001"})

    def promotion_fixture(self, name, **changes):
        f=ReviewFixture(Path(self.temp.name).resolve()/name,reviewed_raw_status=changes.pop("reviewed_raw_status","not_run"),**changes)
        f.review["decisions"][0]["reviewed_status"]="passed"
        f.review["decisions"][0]["classifications"]=["judge_missed_execution"]
        result=f.run()
        value=json.loads((f.output/"reviewed-summary.json").read_text())
        session=next(s for s in value["candidate"]["sessions"] if s["job_id"]=="J001")
        return result,session

    def test_consistent_final_judgment_allows_supported_nr_to_passed(self):
        result,session=self.promotion_fixture("consistent")
        self.assertEqual(session["outcome"],"passed")
        self.assertNotIn("outcome_review_constraint",session)
        self.assertEqual(result["criteria_all"]["not_run"],0)

    def test_changed_criterion_cannot_manufacture_missing_final_judgment(self):
        for raw_status,raw_outcome in (("not_run","inconclusive"),("failed","failed")):
            with self.subTest(raw_status=raw_status):
                result,session=self.promotion_fixture("missing-"+raw_status,
                    reviewed_raw_status=raw_status,final_judgment=False)
                self.assertEqual(session["outcome"],raw_outcome)
                self.assertIn("missing_or_invalid_final_judgment",session["outcome_review_constraint"]["reasons"])
                self.assertEqual(result["criteria_all"]["not_run"],0)
                self.assertEqual(result["criteria_all"]["failed"],0)

    def test_changed_criterion_cannot_clear_a_bound_result_problem(self):
        _,session=self.promotion_fixture("result-problem",result_problem="host_protocol")
        self.assertEqual(session["outcome"],"inconclusive")
        self.assertIn("result_problem_missing_or_unresolved",session["outcome_review_constraint"]["reasons"])

    def test_changed_criterion_cannot_clear_a_bound_task_problem(self):
        _,session=self.promotion_fixture("task-problem",task_problem="host_protocol")
        self.assertEqual(session["outcome"],"inconclusive")
        self.assertIn("task_problem_unresolved",session["outcome_review_constraint"]["reasons"])

    def test_empty_review_cannot_claim_reviewed_output(self):
        self.fixture.review["decisions"]=[]
        self.refuse("bounded_review_decisions_required")

    def test_boolean_call_count_is_not_an_integer_zero(self):
        self.fixture.review["new_model_calls"]=False
        self.refuse("review_must_be_offline")

    def test_old_job_identity_cannot_transfer(self):
        self.fixture.review["decisions"][0]["job_id"]="OLD-J001"
        self.refuse("unassessed_unknown_or_duplicate")

    def test_uncertain_job_cannot_enter_reviewed_denominator(self):
        self.fixture.review["decisions"][0].update(job_id="J002",persona_id="PER-PEEKLY-V2-002")
        self.refuse("unassessed_unknown_or_duplicate")

    def test_raw_status_must_match(self):
        self.fixture.review["decisions"][0]["expected_raw_status"]="not_run"
        self.refuse("raw_status_or_reviewed_status")

    def test_requirement_index_binding_is_exact(self):
        self.fixture.review["decisions"][0]["requirement_id"]="REQ-001-1"
        self.refuse("review_requirement_or_index")

    def test_duplicate_decisions_refused(self):
        self.fixture.review["decisions"]*=2
        self.refuse("unassessed_unknown_or_duplicate")

    def test_result_seal_from_another_run_refused(self):
        self.fixture.review["decisions"][0]["result_sha256"]="0"*64
        self.refuse("review_result_seal")

    def test_unregistered_artifact_is_not_admitted(self):
        self.fixture.review["decisions"][0]["evidence"][0]["artifact_id"]="log-not-in-receipt"
        self.refuse("artifact_not_admitted")

    def test_wrong_observation_binding_refused(self):
        self.fixture.review["decisions"][0]["evidence"][0]["observation_id"]="obs-99"
        self.refuse("observation_not_admitted")

    def test_cited_artifact_tampering_refused(self):
        (self.fixture.stage / "sessions/J001/evidence/J001/1/observation.json").write_text("{}")
        self.refuse("input_sha256_mismatch")

    def test_checkpoint_extra_admission_metadata_is_verified_not_silently_dropped(self):
        f=self.fixture
        task=f.report["tasks"][0]
        job=dict(f.plan["plan"]["jobs"][0],build_sha256=f.plan["plan"]["build"]["sha256"])
        observation=copy.deepcopy(f.observations["J001"])
        observation["artifacts"]=[]
        with self.assertRaisesRegex(reviewer.ReviewError,"observation_artifact_registration_mismatch"):
            reviewer.verify_evidence(reviewer.Inputs(f.repo),f.stage,f.review["decisions"][0],
                                     task,job,{"obs-1":observation})

    def test_log_observation_body_must_match_the_sealed_checkpoint(self):
        f=self.fixture
        task=f.report["tasks"][0]
        job=dict(f.plan["plan"]["jobs"][0],build_sha256=f.plan["plan"]["build"]["sha256"])
        observation=copy.deepcopy(f.observations["J001"])
        observation["facts"]["synthetic"]="changed checkpoint facts"
        with self.assertRaisesRegex(reviewer.ReviewError,"observation_log_binding_mismatch"):
            reviewer.verify_evidence(reviewer.Inputs(f.repo),f.stage,f.review["decisions"][0],
                                     task,job,{"obs-1":observation})

    def test_screenshot_alone_cannot_replace_result_observation(self):
        decision=self.fixture.review["decisions"][0]
        decision["evidence"]=[e for e in decision["evidence"] if e["artifact_id"].startswith("png")]
        self.refuse("result_execution_log_required")

    def test_na_cannot_erase_success_coverage(self):
        self.fixture.review["decisions"][0]["reviewed_status"]="not_applicable"
        self.fixture.review["decisions"][0]["classifications"]=["conditional_not_applicable"]
        self.refuse("NA_requires_explicit_conditional_recovery")

    def test_modified_history_refused_even_if_raw_files_resealed(self):
        f=self.fixture
        f.raw["comparison_columns"]=copy.deepcopy(f.raw["comparison_columns"])
        f.raw["comparison_columns"][0]["label"]="tampered history"
        f.refresh_raw()
        f.review["raw_summary_sha256"]=reviewer.file_hash(f.output / "summary.json")[0]
        self.refuse("historical_columns_or_remaining_baseline")

    def test_queue_change_invalidates_bound_byte_audit(self):
        with sqlite3.connect(self.fixture.stage / "queue.sqlite") as db:
            db.execute("UPDATE jobs SET status='complete' WHERE id='J002'")
        self.refuse("input_sha256_mismatch")

    def test_existing_output_is_preserved(self):
        path=self.fixture.output / "comparison-reviewed.md"
        path.write_text("authored content")
        with self.assertRaisesRegex(reviewer.ReviewError,"reviewed_output_exists"):
            self.fixture.run()
        self.assertEqual(path.read_text(),"authored content")
        self.assertFalse((self.fixture.output / "reviewed-summary.json").exists())

    def test_commit_phase_input_change_rolls_back_only_owned_outputs(self):
        f=self.fixture
        original=reviewer.Inputs.unchanged
        calls=[]
        def race(inputs):
            calls.append(1)
            if len(calls)==2:
                (f.output / "criterion-review.json").write_text("changed after outputs linked")
            return original(inputs)
        with patch.object(reviewer.Inputs,"unchanged",race):
            self.refuse("input_changed_before_publication")
        self.assertEqual((f.output / "criterion-review.json").read_text(),"changed after outputs linked")


if __name__=="__main__":
    unittest.main()
