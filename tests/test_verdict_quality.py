"""Verdict-state semantics and per-persona task design regressions."""
import unittest
from unittest.mock import patch

import _paths
from uxpersonas.agent_run import Execution
from uxpersonas.scale_entry import _persona_journey_goal
from uxpersonas.peekly_criteria import CRITERIA, evaluate
from uxpersonas.scale_run import Evidence


class VerdictQualityTests(unittest.TestCase):
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
                         "peekly-account-mismatch.zip", "검색", "격리 브라우저"):
            self.assertIn(expected, goal)
        self.assertIn("not_applicable", goal)
        self.assertIn("not_run", goal)

    def test_unobserved_success_condition_remains_not_run(self):
        goal = _persona_journey_goal("Use Peekly.", ["PRD-IMPORT-SIZE"])
        self.assertIn("전용 합성 fixture로 실제 업로드", goal)
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

    def test_progress_and_size_criteria_require_their_exact_boundary_fixtures(self):
        facts = {"controls": [{"label": "읽기 멈추기"}], "file_inputs": [],
            "network_policy": {}, "uploaded_fixture": "peekly-progress-sample.zip",
            "upload_progress_samples": [
                {"text": "파일을 읽고 있어요"}, {"text": "팔로우 목록을 확인하고 있어요"}]}
        progress = evaluate({"requirement_ids": ["PRD-IMPORT-PROGRESS"]}, facts, "processing")
        self.assertEqual(progress, [{"kind": "success", "index": 0, "status": "passed"}])
        size_facts = {"controls": [], "file_inputs": [], "network_policy": {},
            "uploaded_fixture": "peekly-oversize-plus-one.zip"}
        size = evaluate({"requirement_ids": ["PRD-IMPORT-SIZE"]}, size_facts,
            "ZIP 파일이 너무 커요. 최대 128MB까지 불러올 수 있어요. 팔로워 1명 팔로잉 1명",
            history=[{"text": "기존 팔로워 1명 팔로잉 1명 결과"}])
        self.assertEqual(size, [{"kind": "success", "index": 0, "status": "passed"}])

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
