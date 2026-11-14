"""Offline regressions from an unadmitted smoke observation, never run credit."""
import copy
import json
from pathlib import Path
import unicodedata
import unittest

import _paths
from uxpersonas.peekly_criteria import (
    LEGACY_UNKNOWN_REQUIREMENT, PAYWALL_REQUIREMENT,
    legacy_scope_evidence, paywall_scope_evidence,
)
from test_peekly_completion_scope import legacy_rows


def golden():
    return json.loads((Path(__file__).with_name("fixtures") /
                       "peekly_paywall_copy_029.json").read_text(encoding="utf-8"))


def normalized(value):
    return " ".join(unicodedata.normalize("NFKC", value).split())


class PaywallCopyTests(unittest.TestCase):
    def test_actual_copy_replays_as_pass_without_crediting_failed_source(self):
        source = golden()
        self.assertIs(source["original_session_completed"], False)
        self.assertIs(source["original_outcome_credit"], False)
        self.assertIs(source["sources"][-1]["admitted_in_original_checkpoint"], False)
        self.assertEqual(source["observations"][-1]["checks"][-1]["status"], "not_run")
        proof = paywall_scope_evidence(source["observations"])
        self.assertEqual(proof["status"], "passed")
        self.assertEqual(proof["indices"], [0, 1, 2, 3, 4])
        self.assertIs(proof["pro_features"], True)

    def test_original_admitted_evidence_without_observation_65_remains_nr(self):
        proof = paywall_scope_evidence(golden()["observations"][:-1])
        self.assertEqual(proof["status"], "not_run")
        self.assertIs(proof["locked_selectors"], True)
        self.assertIs(proof["pro_features"], False)

    def test_unicode_and_whitespace_variants_preserve_actual_meaning(self):
        rows = golden()["observations"]
        for row in rows:
            row["text"] = unicodedata.normalize("NFD", row["text"]).replace(" ", "\u202f").replace("\n", "\u2028")
            for control in row["facts"].get("controls", []):
                control["label"] = unicodedata.normalize("NFD", control["label"]).replace(" ", "\u00a0")
        self.assertEqual(paywall_scope_evidence(rows)["status"], "passed")

    def test_each_feature_and_the_actual_sheet_boundary_are_required(self):
        phrases = ("Peekly Pro", "현재 관계와 최근 변화는 무료예요",
                   "변화를 시간순으로", "여러 번 확인한 관계 변화를 한곳에서 봐요",
                   "원하는 두 시점 비교", "저장한 날짜를 골라 달라진 사람을 확인해요",
                   "한 사람의 관계 이력", "보관된 기록에서 그 사람과의 관계를 따라봐요")
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                rows = golden()["observations"]
                rows[-1]["text"] = normalized(rows[-1]["text"]).replace(phrase, "[missing]")
                self.assertEqual(paywall_scope_evidence(rows)["status"], "not_run")
        for label in ("닫기", "확인"):
            rows = golden()["observations"]
            for control in rows[-1]["facts"]["controls"]:
                if normalized(control["label"]) == label:
                    control["visible"] = False
            self.assertEqual(paywall_scope_evidence(rows)["status"], "not_run")

    def test_features_cannot_be_combined_across_separate_sheets(self):
        rows = golden()["observations"]
        other = copy.deepcopy(rows[-1])
        rows[-1]["text"] = normalized(rows[-1]["text"]).replace("변화를 시간순으로", "[missing]")
        other["text"] = normalized(other["text"]).replace("한 사람의 관계 이력", "[missing]")
        self.assertEqual(paywall_scope_evidence([*rows, other])["status"], "not_run")

    def test_pair_names_storage_and_visible_disabled_selects_still_required(self):
        mutations = (
            lambda r: r[0]["facts"]["import_attempt"].update(fixture_sha256="d" * 64),
            lambda r: r[-1]["facts"]["storage_snapshot"].update(sha256="d" * 64),
            lambda r: r[2]["facts"].update(list_rows=[]),
            lambda r: r[3]["facts"].update(controls=[]),
            lambda r: [c.update(visible=False) for c in r[3]["facts"]["controls"] if c["tag"] == "select"],
        )
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                rows = golden()["observations"]
                mutate(rows)
                self.assertEqual(paywall_scope_evidence(rows)["status"], "not_run")

    def test_visible_enabled_date_failure_wins_before_or_after_valid_sheet(self):
        rows = golden()["observations"]
        enabled = copy.deepcopy(rows[3])
        for control in enabled["facts"]["controls"]:
            if control["tag"] == "select":
                control["disabled"] = False
        for ordered in ([*rows, enabled], [*rows[:3], enabled, *rows[3:]]):
            self.assertEqual(paywall_scope_evidence(ordered)["status"], "failed")

    def test_hidden_controls_behind_pro_sheet_do_not_replace_visible_proof(self):
        rows = golden()["observations"]
        hidden = copy.deepcopy(rows[3]["facts"]["controls"])
        for control in hidden:
            control.update(visible=False, disabled=False)
        rows[-1]["facts"]["controls"] += hidden
        proof = paywall_scope_evidence(rows)
        self.assertEqual(proof["status"], "passed")
        self.assertIn(3, proof["indices"])


class PaywallCopyReceiptTests(unittest.TestCase):
    def harness(self, rows):
        from test_peekly_completion_scope import CompletionReceiptTests
        # New unit admissions use synthetic PNGs and re-evaluate only PAYWALL.
        # They do not change the failed source job or its original native checks.
        rows = copy.deepcopy(rows)
        for row in rows:
            row["checks"] = []
        return CompletionReceiptTests.harness(self, rows, PAYWALL_REQUIREMENT)

    def test_both_receipts_bind_actual_copy_or_keep_missing_sheet_nr(self):
        rows = golden()["observations"]
        for observed, expected in ((rows, "passed"), (rows[:-1], "not_run")):
            harness = self.harness(observed)
            for receipt in harness.receipts(harness.judgment()):
                self.assertEqual(receipt["criteria"][0]["status"], expected)

    def test_both_receipts_keep_real_visible_failure_over_model_pass(self):
        rows = golden()["observations"]
        for control in rows[3]["facts"]["controls"]:
            if control["tag"] == "select":
                control["disabled"] = False
        harness = self.harness(rows)
        for receipt in harness.receipts(harness.judgment()):
            self.assertEqual(receipt["criteria"][0]["status"], "failed")


class LegacyWhitespaceTests(unittest.TestCase):
    def test_primary_exclusion_copy_survives_product_nonbreaking_spaces(self):
        rows = legacy_rows()
        rows[-1]["text"] = rows[-1]["text"].replace(" ", "\u00a0")
        self.assertEqual(legacy_scope_evidence(rows)["status"], "passed")

    def test_departed_button_with_actual_product_nbsp_is_not_ignored(self):
        rows = legacy_rows()
        rows[-1]["facts"]["controls"] = [{"tag": "button", "visible": True,
            "label": "팔로워에서 빠진\u00a0사람\n6명"}]
        self.assertEqual(legacy_scope_evidence(rows)["status"], "failed")


if __name__ == "__main__":
    unittest.main()
