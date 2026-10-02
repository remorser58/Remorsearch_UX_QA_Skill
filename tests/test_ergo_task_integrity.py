"""Explicit task checks preserve execution evidence without claiming product success."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401
from ergoqa import analyze, checks, report, swarm
from ergoqa.profiles import sample_profiles
from ergoqa.qa_attach import AttachError, attach_run
from ergoqa.snapshot import SnapshotError, load_run_dir, validate_run, validate_scenario
from test_ergo_pipeline import make_run
from validate_bundle import validate_bundle


def task_result(**updates):
    result = {"kind": "task_check", "id": "request-retained", "selector": "#pay", "property": "text",
              "checkpoint": 1, "step_index": 1, "snapshot_id": "S-R-1-001", "element_id": "pay",
              "passed": False, "result": "fail", "reason": None, "severity": "P1",
              "consequence": "필수 요청사항이 최종 결과에 유지되지 않았습니다."}
    return {**result, **updates}


class TaskValidationTests(unittest.TestCase):
    def test_scenario_contract_is_typed_bounded_and_fail_closed(self):
        fixture = Path(__file__).parent / "fixtures/ergo/sample_scenario.json"
        scenario = json.loads(fixture.read_text())
        scenario["steps"] = [{"action": "type", "target": "#memo", "text": "fixture", "redact": True}]
        authored = {"id": "memo-retained", "selector": "#memo", "property": "value", "from_step": 1,
                    "after_step": 1, "severity": "P2", "consequence": "요청사항을 유지해야 합니다."}
        scenario["success"] = {"task_checks": [authored]}
        self.assertEqual(validate_scenario(scenario), [])
        for changes in ({"expected": "duplicate"}, {"from_step": 2}, {"after_step": 2}, {"property": "checked"},
                        {"selector": "input[value='private']"}, {"selector": "input[ value='private']"},
                        {"selector": "input[v\\61lue='private']"}, {"selector": "#password"}, {"guess": True}):
            candidate = copy.deepcopy(scenario)
            candidate["success"]["task_checks"][0].update(changes)
            self.assertTrue(validate_scenario(candidate), changes)
        scenario["success"]["task_checks"].append(authored)
        self.assertTrue(validate_scenario(scenario))
        promoted = copy.deepcopy(scenario)
        promoted["success"]["task_checks"] = [{**authored, "redact": True}]
        del promoted["steps"][0]["target"]
        del promoted["steps"][0]["redact"]
        self.assertTrue(validate_scenario(promoted))

    def test_completed_task_failure_preserves_coverage_and_uncertainty(self):
        run = {"run_id": "R", "status": "completed", "success": False, "steps": [], "success_detail": {"criteria": [task_result()]}}
        health, notes = analyze.run_health(run, [], None)
        self.assertEqual(health, "ok")
        self.assertFalse(any("이후 화면은 검사되지" in note for note in notes))
        run["success_detail"]["criteria"] = [task_result(result="unevaluable", passed=None, reason="missing_target")]
        self.assertEqual(analyze.run_health(run, [], None)[0], "degraded")
        run["status"] = "blocked"
        self.assertEqual(analyze.run_health(run, [], None)[0], "failed")


class TaskEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.run_dir = make_run(self.root)
        self.profiles = sample_profiles(3, 7, ["galaxy-s24"])
        for path in [self.run_dir / "run.json", *self.run_dir.glob("S-*.json")]:
            doc = json.loads(path.read_text())
            doc.setdefault("surface", {})["build_id"] = "task-integrity-fixture-v1"
            path.write_text(json.dumps(doc))
        self.run = json.loads((self.run_dir / "run.json").read_text())
        self.run.update(success=False, success_basis="measured", success_detail={"criteria": [task_result()], "unevaluable": []})
        self.save_run()
        self.qa = json.loads((Path(__file__).parent / "fixtures/valid-bundle.json").read_text())
        self.qa["records"]["findings"][0]["severity"] = "P2"

    def tearDown(self):
        self.tmp.cleanup()

    def save_run(self):
        (self.run_dir / "run.json").write_text(json.dumps(self.run))

    def test_observed_failure_attaches_with_receipt_owner_and_second_pass(self):
        before = copy.deepcopy(self.qa)
        analysis = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)
        task = [obs for obs in analysis["observations"] if obs["check_id"] == "TI-01"]
        self.assertEqual(len(task), 1)
        self.assertEqual(task[0]["profile_id"], "EP-01")
        self.assertEqual(task[0]["basis"], "measured")
        self.assertEqual(task[0]["measurement"]["snapshot_id"], "S-R-1-001")
        findings = swarm.aggregate([analysis], self.profiles)
        task_findings = [f for f in findings if f["check_id"] == "TI-01"]
        self.assertEqual(task_findings[0]["triggered_profiles"], ["EP-01"])
        self.assertEqual(task_findings[0]["tested_profiles"], ["EP-01"])
        self.assertEqual(task_findings[0]["profile_specific"], {})
        self.assertIn("명시한", report.render(findings, self.profiles, [analysis]))
        self.assertIn("값 비공개", report.render(findings, self.profiles, [analysis]))
        with self.assertRaisesRegex(AttachError, "P0/P1"):
            attach_run(self.qa, self.run_dir, self.profiles, {"scenario-1": "EP-01"}, receipts_root=self.root / "receipts", gaze_enabled=False)
        self.assertFalse((self.root / "receipts").exists())
        owner_analysis = analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False)
        reviews = [{"finding_id": f"ERGO-{f['id']}@R-1@EP-01", "reviewer": "self", "task_completed": False,
                    "control_name": "결제하기", "omitted": ["필수 요청사항"], "severity": "agree", "inconclusive": False}
                   for f in swarm.aggregate([owner_analysis], self.profiles) if f["severity"] in ("P0", "P1")]
        attached = attach_run(self.qa, self.run_dir, self.profiles, {"scenario-1": "EP-01"}, receipts_root=self.root / "receipts",
                              second_pass=reviews, gaze_enabled=False)
        self.assertEqual(validate_bundle(attached, artifacts_root=self.root / "receipts"), [])
        self.assertEqual(self.qa, before)
        records = attached["records"]
        execution = next(r for r in records["runs"] if r.get("recorded_run_id") == "R-1")
        self.assertEqual(execution["status"], "completed")
        self.assertIs(execution["task_success"], False)
        observation = next(o for o in records["observations"] if o.get("check_id") == "TI-01")
        self.assertEqual(observation["receipt"]["build_id"], "task-integrity-fixture-v1")
        self.assertEqual(observation["snapshot_id"], "S-R-1-001")
        self.assertTrue((self.root / "receipts" / observation["receipt"]["artifact_path"]).is_file())
        model_findings = [f for f in records["findings"] if f.get("check_id") and checks.CATALOG[f["check_id"]].basis == "model"]
        self.assertTrue(all(f["verification_status"] == "unverified" for f in model_findings))

    def test_unknown_or_incomplete_failure_does_not_attach(self):
        for status, criterion in (("blocked", task_result()), ("failed", task_result()), ("completed", None),
                                  ("completed", task_result(passed=None, result="unevaluable", reason="missing_target"))):
            self.run.update(status=status, success_detail={"criteria": [criterion] if criterion else [], "unevaluable": []})
            self.save_run()
            with self.assertRaises(AttachError):
                attach_run(self.qa, self.run_dir, self.profiles, {"scenario-1": "EP-01"}, receipts_root=self.root / "receipts", gaze_enabled=False)

    def test_missing_capture_and_value_bearing_results_are_rejected(self):
        self.assertEqual(validate_run(self.run), [])
        self.run["success_detail"]["criteria"][0]["actual"] = "PRIVATE-SENTINEL"
        errors = validate_run(self.run)
        self.assertTrue(errors)
        self.assertNotIn("PRIVATE-SENTINEL", " ".join(errors))
        del self.run["success_detail"]["criteria"][0]["actual"]
        self.run["success_detail"]["criteria"][0]["snapshot_id"] = "S-missing"
        self.save_run()
        with self.assertRaisesRegex(SnapshotError, "task check capture"):
            load_run_dir(self.run_dir)

    def test_malformed_criteria_validate_without_crashing_the_loader(self):
        for criteria in (None, 1, True, [None], [1], ["untrusted criterion"]):
            with self.subTest(criteria=criteria):
                self.run["success_detail"]["criteria"] = criteria
                self.assertTrue(validate_run(self.run))
                self.save_run()
                with self.assertRaises(SnapshotError):
                    load_run_dir(self.run_dir)

    def test_direct_analysis_rejects_wrong_scenario_and_preserves_omitted_input(self):
        self.assertTrue(analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False))
        for scenario in ({"schema_version": "ergo-scenario.v1", "scenario_id": "wrong"},
                         {"schema_version": "unknown", "scenario_id": self.run["scenario_id"]}):
            with self.assertRaisesRegex(ValueError, "scenario"):
                analyze.analyze_run(self.run_dir, self.profiles, scenario, gaze_enabled=False)

    def test_task_truth_and_capture_crossrefs_fail_closed(self):
        self.run["success"] = True
        self.assertTrue(validate_run(self.run))
        self.run["success_detail"]["criteria"][0].update(passed=None, result="unevaluable", reason="missing_target")
        self.assertTrue(validate_run(self.run))
        self.run["success"] = False
        self.run["success_detail"]["criteria"] = [task_result(checkpoint="final", step_index=0, snapshot_id="S-R-1-000")]
        self.save_run()
        with self.assertRaisesRegex(SnapshotError, "final task check"):
            load_run_dir(self.run_dir)
        self.run["success_detail"]["criteria"] = [task_result()]
        self.run["steps"][0]["after"] = "S-R-1-000"
        self.save_run()
        with self.assertRaisesRegex(SnapshotError, "after-capture"):
            load_run_dir(self.run_dir)


if __name__ == "__main__":
    unittest.main()
