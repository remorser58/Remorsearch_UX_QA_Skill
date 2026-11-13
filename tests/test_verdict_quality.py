"""Verdict-state semantics and per-persona task design regressions."""
import unittest

import _paths
from uxpersonas.agent_run import Execution
from uxpersonas.scale_entry import _persona_journey_goal


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
        self.assertIn("제공된 해당 시나리오 fixture가 manifest에 실제로 있을 때만", goal)
        self.assertIn("not_run", goal)
