"""Old R1 navigation facts + authored safe next-step tests; no browser/model run."""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import _paths
from uxpersonas import scale_run, swarm
from uxpersonas.scale_entry import _persona_journey_goal, criterion_checklist
from test_peekly_completion_scope import paywall_rows


RID = "PRD-PAYWALL-BOUNDARY"
TASK = {"requirement_ids": [RID]}
TOOLS = {"observe", "click", "scroll"}
ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests/fixtures/peekly_history_navigation_029_r1.json"


def saved(number):
    return next(row for row in json.loads(GOLDEN.read_text())["observations"]
                if row["id"] == "obs-" + str(number))


def authored_chain(row):
    """Bind saved controls to an authored pair; never claim a new live result."""
    prefix = paywall_rows()[:3]
    current = prefix[1]["facts"]
    row = copy.deepcopy(row)
    row["facts"].update(import_attempt_id=current["import_attempt_id"],
                        storage_snapshot=copy.deepcopy(current["storage_snapshot"]))
    return prefix + [row]


def action(row, prefix=None):
    rows = authored_chain(row) if prefix is None else prefix + [row]
    return scale_run._completion_action(RID, TASK, rows, TOOLS)


class HistoryNavigationTests(unittest.TestCase):
    def test_saved_results_history_is_clicked_without_more_detour(self):
        row = saved(51)
        before = copy.deepcopy(row)
        next_step, blocker = action(row)
        self.assertIsNone(blocker)
        self.assertEqual(next_step["tool"], "click")
        self.assertTrue(next_step["label"].startswith("변화 기록"))
        control = next(c for c in row["facts"]["controls"] if c["label"].startswith("변화 기록"))
        self.assertIs(control["visible"], True)
        self.assertEqual(next_step["selector"], control["selector"])
        self.assertEqual(row, before)

    def test_saved_more_hidden_history_is_above_visible_later_controls(self):
        for number in (52, 53):
            with self.subTest(observation=number):
                row = saved(number)
                direction, reason = scale_run._history_scroll_direction(row)
                self.assertEqual(direction, -400)
                self.assertIn("More", reason)
                self.assertIn("above", reason)
                next_step, blocker = action(row)
                self.assertIsNone(blocker)
                self.assertEqual(next_step["tool"], "scroll")
                self.assertEqual(next_step["delta"], -400)
        scroll = saved(53)["facts"]["scroll_attempt"]
        self.assertEqual((scroll["before"]["scroll_top"], scroll["after"]["scroll_top"]), (286, 616))
        self.assertGreater(scroll["observed_delta"], 0)

    def test_more_top_and_results_earlier_cards_still_scroll_down(self):
        row = saved(52)
        for control in row["facts"]["controls"]:
            control["visible"] = "이미" in control["label"]
        self.assertEqual(action(row)[0]["delta"], 400)
        row = saved(51)
        for control in row["facts"]["controls"]:
            control["visible"] = control["label"].startswith("나를 맞팔")
        self.assertEqual(action(row)[0]["delta"], 400)

    def test_ambiguous_unknown_or_modal_background_does_not_get_guessed_scroll(self):
        row = saved(52)
        for control in row["facts"]["controls"]:
            control["visible"] = control["label"] in {"Pro", "더보기", "결과"}
        self.assertIsNone(action(row)[0])
        row["facts"]["controls"] = [c for c in row["facts"]["controls"] if c["label"].startswith("변화 기록")]
        self.assertIsNone(action(row)[0])
        row = saved(53)
        row["facts"]["scroll_attempt"]["scope"] = "modal"
        self.assertIsNone(action(row)[0])
        row["facts"]["controls"].append(dict(selector="body>button:nth-of-type(99)",
            label="닫기", visible=True, disabled=False))
        next_step, blocker = action(row)
        self.assertIsNone(blocker)
        self.assertEqual(next_step["tool"], "click")
        self.assertEqual(next_step["label"], "닫기")

    def test_history_modal_tab_remains_inside_modal_and_keeps_downward_navigation(self):
        row = saved(52)
        row["facts"]["controls"] = [
            dict(selector="body>button:nth-of-type(1)", label="기간 비교", visible=False, disabled=False),
            dict(selector="body>button:nth-of-type(2)", label="닫기", visible=True, disabled=False)]
        row["facts"]["scroll_attempt"] = {"scope": "modal"}
        next_step, blocker = action(row)
        self.assertIsNone(blocker)
        self.assertEqual(next_step["tool"], "scroll")
        self.assertEqual(next_step["delta"], 400)
        self.assertEqual(next_step["target_label"], "기간 비교")

    def test_disabled_history_and_two_unchanged_scrolls_remain_blocked(self):
        row = saved(51)
        for control in row["facts"]["controls"]:
            if control["label"].startswith("변화 기록"):
                control["disabled"] = True
        self.assertIn("disabled", action(row)[1])
        rows = authored_chain(saved(53))
        for number in (1, 2):
            row = copy.deepcopy(rows[-1])
            row["id"] = "authored-up-no-movement-" + str(number)
            scroll = row["facts"]["scroll_attempt"]
            scroll.update(requested_delta=-400, moved=False, outcome="no_scrollable_area")
            scroll["after"]["scroll_top"] = scroll["before"]["scroll_top"]
            rows.append(row)
        next_step, blocker = scale_run._completion_action(RID, TASK, rows, TOOLS)
        self.assertIsNone(next_step)
        self.assertIn("Two admitted scroll attempts", blocker)

    def test_new_task_prefers_current_results_and_all_32_actual_requirement_sets_fit(self):
        steps = criterion_checklist([RID])[0]["steps"]
        self.assertIn("Prefer the visible 변화 기록 control already on Results", steps[2])
        self.assertIn("scroll(delta=-400)", steps[2])
        self.assertIn("scroll(delta=400) in the active modal body", steps[2])
        tree = ast.parse((ROOT / "scripts/run_peekly_completion.py").read_text())
        value = next(n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                     and any(isinstance(target, ast.Name) and target.id == "goal" for target in n.targets))
        base = eval(compile(ast.Expression(value), "owned-launcher-goal", "eval"),
                    {"__builtins__": {}, "args": SimpleNamespace(stage="cohort"),
                     "root": Path(".ux-loop/peekly-completion32-20261115-r2")})
        requirements = json.loads(GOLDEN.read_text())["cohort_requirement_ids"]
        self.assertEqual(len(requirements), 32)
        for pid, ids in requirements.items():
            with self.subTest(persona=pid):
                goal = _persona_journey_goal(base, ids)
                self.assertLessEqual(len(goal), 8000)
                self.assertEqual(swarm.clean(goal), goal)
                self.assertEqual({row["index"]: row["requirement_id"] for row in criterion_checklist(ids)},
                                 dict(enumerate(ids)))


if __name__ == "__main__":
    unittest.main()

