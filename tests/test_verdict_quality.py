"""Verdict-state semantics and per-persona task design regressions."""
import unittest
from unittest.mock import patch

import _paths
from uxpersonas.agent_run import Execution, Tool
from uxpersonas.scale_entry import _persona_journey_goal
from uxpersonas.peekly_criteria import CRITERIA, evaluate
from uxpersonas.scale_run import Evidence


class VerdictQualityTests(unittest.TestCase):
    def test_structural_dom_selectors_are_typed_metadata_not_free_user_text(self):
        tool = Tool("upload", "Select an owned fixture.", {
            "selector": "string", "file": "string"}, "owned_fixture_write")
        valid = {"selector": "body>div:nth-of-type(2)>section:nth-of-type(1)>input:nth-of-type(1)",
                 "file": "peekly-sample-current.zip"}
        self.assertEqual(tool.validate(valid), valid)
        with self.assertRaises(Exception):
            tool.validate({"selector": "#account-123456", "file": "peekly-sample-current.zip"})

    def test_only_conditional_recovery_can_be_not_applicable(self):
        task = {"success_criteria": ["Show imported result"],
                "recovery_criteria": ["Recover from a real failure"]}
        judgment = {"reason": "No failure occurred.", "criteria": [
            {"kind": "success", "index": 0, "status": "passed",
             "observation": "Imported result is visible.", "observation_ids": ["obs-1"]},
            {"kind": "recovery", "index": 0, "status": "not_applicable",
             "observation": "No triggering failure occurred in this run.", "observation_ids": []}]}
        observation = {"id": "obs-1", "artifacts": [
            {"id": "log-1", "kind": "execution_log"},
            {"id": "png-1", "kind": "screenshot"}]}
        result = Execution.criteria(None, {"claim": {"task": task}}, judgment, [observation])
        self.assertEqual([x["status"] for x in result], ["passed", "not_applicable"])

    def test_success_criterion_cannot_be_not_applicable(self):
        task = {"success_criteria": ["Show imported result"], "recovery_criteria": []}
        judgment = {"reason": "Not tested.", "criteria": [
            {"kind": "success", "index": 0, "status": "not_applicable",
             "observation": "The fixture was not available.", "observation_ids": []}]}
        with self.assertRaises(Exception):
            Execution.criteria(None, {"claim": {"task": task}}, judgment, [])

    def test_saved_persona_requirements_expand_into_specific_execution_actions(self):
        goal = _persona_journey_goal("Use the owned Peekly preview.", [
            "PRD-RESULT-SNAPSHOT", "PRD-IMPORT-FORMATS", "PRD-IMPORT-MISSING",
            "PRD-IMPORT-ACCOUNT", "PRD-RESULT-SEARCH", "PRD-PRIVACY-DELETE"])
        for expected in ("peekly-sample-previous.zip", "peekly-sample-current.zip",
                         "peekly-format-html.zip", "peekly-format-json.zip",
                         "peekly-missing-followers.zip", "peekly-missing-following.zip",
                         "peekly-account-mismatch.zip", "검색", "별도 브라우저 프로필"):
            self.assertIn(expected, goal)
        self.assertIn("not_applicable", goal)
        self.assertIn("not_run", goal)

    def test_unobserved_success_condition_remains_not_run(self):
        goal = _persona_journey_goal("Use Peekly.", ["PRD-IMPORT-SIZE"])
        self.assertIn("32MiB+1 loose file", goal)
        self.assertIn("not_run", goal)

    def test_every_saved_peekly_prd_requirement_has_an_explicit_acceptance_contract(self):
        expected = {
            "PRD-START-SAMPLE", "PRD-START-IMPORT", "PRD-START-SKIP", "PRD-IMPORT-FORMATS",
            "PRD-IMPORT-MULTI", "PRD-IMPORT-HTML", "PRD-IMPORT-PROGRESS", "PRD-IMPORT-ACCOUNT",
            "PRD-IMPORT-MISSING", "PRD-IMPORT-SIZE", "PRD-RESULT-RECIPROCITY", "PRD-RESULT-REVERSE",
            "PRD-RESULT-MUTUAL", "PRD-RESULT-SNAPSHOT", "PRD-RESULT-SEARCH", "PRD-SAMPLE-EXPORT",
            "PRD-PRIVACY-LOCAL", "PRD-PRIVACY-DELETE", "PRD-IDENTITY-LIMIT", "PRD-IMPORT-SNAPSHOT-UNKNOWN",
            "PRD-IMPORT-ALLTIME", "PRD-IMPORT-SAVE-FAIL", "PRD-IMPORT-REOPEN", "PRD-SNAPSHOT-RETENTION",
            "PRD-PAYWALL-BOUNDARY",
        }
        self.assertEqual(set(CRITERIA), expected)
        for rid, spec in CRITERIA.items():
            for field in ("screen", "selector", "text", "value", "precondition", "action", "timeout_seconds", "scope"):
                self.assertIn(field, spec, rid)
            self.assertGreater(spec["timeout_seconds"], 0)

    def test_machine_judgment_requires_actual_uploads_and_visible_result(self):
        task = {"requirement_ids": ["PRD-IMPORT-FORMATS"]}
        facts = {"controls": [], "file_inputs": [], "network_policy": {"external_requests_blocked": True}}
        text = "결과를 불러왔어요. 나를 맞팔 안 한 사람 1명 내가 맞팔 안 한 사람 1명 맞팔 중인 사람 0명"
        self.assertEqual(evaluate(task, facts, text, ()), [])
        checks = evaluate(task, facts, text,
            ("peekly-format-html.zip", "peekly-format-json.zip"))
        self.assertEqual(checks, [{"kind": "success", "index": 0, "status": "passed"}])

    def test_native_failure_is_emitted_only_after_triggering_fixture(self):
        task = {"requirement_ids": ["PRD-IMPORT-MISSING"]}
        facts = {"controls": [], "file_inputs": [], "network_policy": {}}
        self.assertEqual(evaluate(task, facts, "결과를 불러왔어요", ()), [])
        checks = evaluate(task, facts, "결과를 불러왔어요",
            ("peekly-missing-followers.zip", "peekly-missing-following.zip"))
        self.assertEqual(checks, [{"kind": "success", "index": 0, "status": "failed"}])

    def test_progress_requires_both_phases_and_an_observed_cancel(self):
        facts = {"controls": [], "file_inputs": [], "network_policy": {}}
        history = [
            {"text": "파일을 읽고 있어요", "facts": {"upload_progress_samples": [{"text": "파일을 읽고 있어요"}]}},
            {"text": "팔로우 목록을 확인하고 있어요", "facts": {"upload_progress_samples": [{"text": "팔로우 목록을 확인하고 있어요"}]}},
        ]
        uploads = ("peekly-progress-sample.zip",)
        self.assertEqual(evaluate({"requirement_ids": ["PRD-IMPORT-PROGRESS"]}, facts, "", uploads, history), [])
        history.append({"text": "읽기 멈추기", "facts": {"last_action_label": "읽기 멈추기"}})
        self.assertEqual(evaluate({"requirement_ids": ["PRD-IMPORT-PROGRESS"]}, facts, "", uploads, history),
            [{"kind": "success", "index": 0, "status": "passed"}])

    def test_size_criteria_requires_all_three_boundary_uploads_and_messages(self):
        task = {"requirement_ids": ["PRD-IMPORT-SIZE"]}
        facts = {"controls": [], "file_inputs": [], "network_policy": {}}
        uploads = ("peekly-oversize-plus-one.zip", "@group:peekly-loose-file-over", "@group:peekly-loose-total-over")
        text = "ZIP 파일이 너무 커요. 최대 128MB까지 불러올 수 있어요. 파일 하나는 최대 32MB까지 불러올 수 있어요. 파일은 모두 합쳐 최대 64MB까지 불러올 수 있어요."
        self.assertEqual(evaluate(task, facts, text, uploads), [{"kind": "success", "index": 0, "status": "passed"}])
        self.assertEqual(evaluate(task, facts, text, uploads[:1]), [])

    def test_multi_file_criterion_requires_every_real_group_and_outcomes(self):
        task = {"requirement_ids": ["PRD-IMPORT-MULTI"]}
        facts = {"controls": [], "file_inputs": [{"multiple": True}], "network_policy": {}}
        uploads = ("@group:peekly-mixed-loose-valid", "@group:peekly-loose-512-valid",
            "@group:peekly-loose-513-rejected", "@group:peekly-zip-plus-loose-rejected")
        text = "팔로우 목록을 찾았어요. 파일이 너무 많아요. 최대 512개까지 골라 주세요. ZIP 파일은 다른 파일과 함께 고를 수 없어요."
        self.assertEqual(evaluate(task, facts, text, uploads), [{"kind": "success", "index": 0, "status": "passed"}])
        self.assertEqual(evaluate(task, facts, text, uploads[:2]), [])

    def test_native_browser_pass_closes_model_not_run(self):
        worker = {"claim": {"task": {"id": "task", "success_criteria": ["show result"],
            "recovery_criteria": []}, "binding": {"revision": 1, "profile_sha256": "a" * 64}},
            "queue_claim": {"owner": "worker", "lease_token": "b" * 64}}
        observation = {"id": "obs-1", "action": "observe", "text": "deterministic result", "checks": [
            {"kind": "success", "index": 0, "status": "passed"}],
            "artifacts": [{"id": "png-1", "kind": "screenshot"}]}
        judgment = {"reason": "No model judgment for this criterion.", "criteria": [
            {"kind": "success", "index": 0, "status": "not_run",
             "observation": "Not observed by model.", "observation_ids": []}]}
        with patch("uxpersonas.scale_run.swarm._receipt", side_effect=lambda root, job, value: value):
            receipt = Evidence(".").receipt(worker, {"observations": [observation]},
                {"build": {"sha256": "c" * 64}}, judgment=judgment)
        self.assertEqual(receipt["criteria"][0]["status"], "passed")
        self.assertEqual(receipt["criteria"][0]["evidence_ids"], ["png-1"])
