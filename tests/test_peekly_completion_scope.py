"""Authored offline contracts for coverage completion; never live UX evidence."""
import copy
import unittest

import _paths
from uxpersonas.peekly_criteria import (
    LEGACY_ACCOUNT_SHA256, LEGACY_PRODUCT_COMMIT, LEGACY_PRODUCT_LOADER_SHA256,
    LEGACY_PRODUCT_VALIDATION_SHA256, LEGACY_SEED_FIXTURE, LEGACY_SEED_FIXTURE_SHA256,
    LEGACY_SNAPSHOT_ID, LEGACY_UNKNOWN_REQUIREMENT,
    PAIR_FIXTURE_SHA256, PAYWALL_REQUIREMENT, RESULT_CURRENT_FIXTURE,
    evaluate, legacy_scope_evidence, paywall_scope_evidence,
)
from uxpersonas.agent_run import _validated_observation_facts
from uxresearch.canonical import EngineError


def storage(digit):
    return {"available": True, "keys": ["peekly_state_v7"], "sha256": digit * 64}


def imported(fixture, before, after, attempt_id):
    return {"text": "결과를 불러왔어요.", "facts": {
        "last_action": "upload", "uploaded_fixture": fixture,
        "fixture_uploads": [fixture], "import_attempt_id": attempt_id,
        "storage_snapshot": copy.deepcopy(after),
        "import_attempt": {
            "schema_version": "peekly-import-attempt.v1", "tool": "upload",
            "fixture": fixture, "fixture_sha256": PAIR_FIXTURE_SHA256[fixture],
            "attempt_id": attempt_id, "storage_before": copy.deepcopy(before),
            "storage_after": copy.deepcopy(after), "persistence_unchanged": False,
            "cancel_dispatched": False, "phase_samples": [{"text": "결과를 불러왔어요."}],
        }}, "checks": []}


def paywall_rows():
    """Explicitly authored pair/DOM contract, not a replayed positive run."""
    previous = imported("peekly-sample-previous.zip", storage("a"), storage("b"), "upload-previous")
    current = imported(RESULT_CURRENT_FIXTURE, storage("b"), storage("c"), "upload-current")
    def observed(text, **facts):
        return {"text": text, "facts": {
            "last_action": "observe", "import_attempt_id": "upload-current",
            "storage_snapshot": storage("c"),
            "fixture_uploads": list(PAIR_FIXTURE_SHA256), **facts}, "checks": []}
    free = observed("팔로워에서 빠진 사람 2명", list_rows=[{"key": "synthetic-account"}])
    # Real product puts the accessible names on <select>, not in body text.
    history = observed("변화 기록 이전 기록 이후 기록 원하는 두 시점을 골라 비교해요", controls=[
        {"tag": "select", "label": "비교 시작 기록", "disabled": True},
        {"tag": "select", "label": "비교 종료 기록", "disabled": True},
    ])
    pro = observed("Pro 변화 타임라인 두 시점 비교 사람별 관계 이력", controls=[])
    return [previous, current, free, history, pro]


def legacy_rows():
    """Authored validated host ABI plus product readback and visible exclusion."""
    legacy = {"id": LEGACY_SNAPSHOT_ID, "account_sha256": LEGACY_ACCOUNT_SHA256,
              "is_sample": False, "list_completeness": "unknown", "included_files": ["followers", "following"]}
    receipt = {
        "schema_version": "peekly-legacy-seed.v1", "attempt_id": "legacy-seed-synthetic",
        "fixture": LEGACY_SEED_FIXTURE, "fixture_sha256": LEGACY_SEED_FIXTURE_SHA256,
        "product_commit": LEGACY_PRODUCT_COMMIT, "product_loader_sha256": LEGACY_PRODUCT_LOADER_SHA256,
        "product_validation_sha256": LEGACY_PRODUCT_VALIDATION_SHA256,
        "storage_before": storage("a"), "storage_after": storage("b"),
        "fresh_owned_profile": True, "initial_storage_match": True,
        "source_key": "peekly_state_v6", "target_key": "peekly_state_v7",
        "source_snapshot_ids": [LEGACY_SNAPSHOT_ID], "source_included_files_absent": True,
        "source_list_completeness_absent": True, "reload_observed": True,
        "migration_validated": True, "status": "validated",
    }
    state = {"schema_version": "peekly-legacy-state.v1", "seed_attempt_id": receipt["attempt_id"],
             "available": True, "storage_sha256": "b" * 64, "snapshots": [legacy],
             "active_snapshot_id": None, "comparison_snapshot_id": None}
    seed = {"text": "Validated synthetic legacy setup.", "facts": {
        "last_action": "seed_legacy_unknown", "legacy_seed": receipt,
        "legacy_state": state, "storage_snapshot": storage("b")}, "checks": []}
    current = imported(RESULT_CURRENT_FIXTURE, storage("b"), storage("c"), "upload-current")
    imported_state = copy.deepcopy(state)
    imported_state.update(storage_sha256="c" * 64,
                          active_snapshot_id="synthetic-current", comparison_snapshot_id="synthetic-current")
    imported_state["snapshots"].append({**legacy, "id": "synthetic-current", "list_completeness": None})
    current["facts"].update(legacy_seed=copy.deepcopy(receipt), legacy_state=imported_state)
    visible = {"text": "이전 기록 1개 보관 중 예전 기록을 보관했어요. 이전 버전에서 저장한 불완전한 기록은 분석에 쓰지 않아요. 다음에는 달라진 계정도 보여드려요. 다음에 새로 확인하면 지금 기록과 비교해요.",
               "facts": {"last_action": "observe", "import_attempt_id": "upload-current",
                         "storage_snapshot": storage("c"), "legacy_seed": copy.deepcopy(receipt),
                         "legacy_state": copy.deepcopy(imported_state), "controls": []}, "checks": []}
    return [seed, current, visible]


class PaywallCompletionScopeTests(unittest.TestCase):
    def test_actual_control_names_work_without_labels_in_visible_body(self):
        rows = paywall_rows()
        proof = paywall_scope_evidence(rows)
        self.assertEqual(proof["status"], "passed")
        self.assertEqual(proof["indices"], [0, 1, 2, 3, 4])
        for field in ("pair_imported", "free_comparison", "history_open", "locked_selectors", "pro_features"):
            self.assertIs(proof[field], True)
        self.assertEqual(evaluate({"requirement_ids": [PAYWALL_REQUIREMENT]}, {}, "", (), rows)[0]["status"], "passed")

    def test_cumulative_fixture_names_alone_cannot_supply_pair(self):
        self.assertEqual(paywall_scope_evidence(paywall_rows()[2:])["status"], "not_run")

    def test_controls_from_separate_screens_cannot_be_joined(self):
        rows = paywall_rows()
        second = copy.deepcopy(rows[3])
        second["facts"]["controls"] = second["facts"]["controls"][1:]
        rows[3]["facts"]["controls"] = rows[3]["facts"]["controls"][:1]
        rows.insert(4, second)
        self.assertEqual(paywall_scope_evidence(rows)["status"], "not_run")

    def test_old_names_or_pro_copy_before_pair_does_not_satisfy_current_pair(self):
        rows = paywall_rows()
        for missing_index in (2, 4):
            reordered = copy.deepcopy(rows)
            reordered.insert(0, reordered.pop(missing_index))
            self.assertEqual(paywall_scope_evidence(reordered)["status"], "not_run")

    def test_digest_storage_sample_and_attempt_mismatches_are_not_run(self):
        mutations = (
            lambda r: r[0]["facts"]["import_attempt"].update(fixture_sha256="d" * 64),
            lambda r: r[1]["facts"]["import_attempt"]["storage_before"].update(sha256="d" * 64),
            lambda r: r[3]["facts"]["storage_snapshot"].update(sha256="d" * 64),
            lambda r: r[3]["facts"].update(import_attempt_id="upload-unrelated"),
            lambda r: r[3].update(text="샘플을 보고 있어요."),
            lambda r: r[4].update(text="Pro 다른 기능"),
        )
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                rows = paywall_rows()
                mutate(rows)
                self.assertEqual(paywall_scope_evidence(rows)["status"], "not_run")

    def test_enabled_controls_are_a_proven_failure_in_either_order(self):
        rows = paywall_rows()
        failed = copy.deepcopy(rows[3])
        for control in failed["facts"]["controls"]:
            control["disabled"] = False
        for order in ([*rows, failed], [*rows[:3], failed, *rows[3:]]):
            self.assertEqual(paywall_scope_evidence(order)["status"], "failed")

    def test_progress_points_to_remaining_actual_steps(self):
        rows = paywall_rows()
        proof = paywall_scope_evidence(rows[:3])
        self.assertIs(proof["pair_imported"], True)
        self.assertIs(proof["free_comparison"], True)
        self.assertIs(proof["locked_selectors"], False)
        self.assertIs(proof["pro_features"], False)


class LegacyCompletionScopeTests(unittest.TestCase):
    def test_validated_migration_and_actual_product_exclusion_pass(self):
        rows = legacy_rows()
        proof = legacy_scope_evidence(rows)
        self.assertEqual(proof["status"], "passed")
        self.assertEqual(proof["indices"], [0, 1, 2])
        self.assertTrue(all(proof[k] for k in ("seed_validated", "current_imported", "exclusion_visible")))
        self.assertEqual(evaluate({"requirement_ids": [LEGACY_UNKNOWN_REQUIREMENT]}, {}, "", (), rows)[0]["status"], "passed")

    def test_seed_alone_is_setup_not_product_pass(self):
        for end in (1, 2):
            proof = legacy_scope_evidence(legacy_rows()[:end])
            self.assertEqual(proof["status"], "not_run")
            self.assertIs(proof["seed_validated"], True)
            self.assertIs(proof["exclusion_visible"], False)

    def test_optional_current_completeness_matches_product_import_and_reload(self):
        for completeness in (None, "known"):
            rows = legacy_rows()
            rows[2]["facts"]["legacy_state"]["snapshots"][1]["list_completeness"] = completeness
            self.assertEqual(legacy_scope_evidence(rows)["status"], "passed")

    def test_every_seed_precondition_and_pinned_source_is_required(self):
        mutations = [
            lambda r: r[0]["facts"]["legacy_seed"].update(status="uncertain"),
            lambda r: r[0]["facts"]["legacy_seed"].update(fixture_sha256="d" * 64),
            lambda r: r[0]["facts"]["legacy_seed"].update(product_validation_sha256="d" * 64),
            lambda r: r[0]["facts"]["legacy_seed"].update(product_loader_sha256="d" * 64),
            lambda r: r[0]["facts"]["legacy_seed"].update(product_commit="d" * 40),
            lambda r: r[0]["facts"]["legacy_seed"].update(source_snapshot_ids=["another-record"]),
            lambda r: r[0]["facts"]["legacy_seed"].update(source_key="peekly_state_v7"),
            lambda r: r[0]["facts"]["legacy_state"]["snapshots"][0].update(list_completeness="known"),
            lambda r: r[0]["facts"]["legacy_state"]["snapshots"][0].update(included_files=None),
            lambda r: r[0]["facts"]["legacy_state"].update(active_snapshot_id=LEGACY_SNAPSHOT_ID),
            lambda r: r[0]["facts"]["legacy_state"].update(storage_sha256="d" * 64),
        ]
        for field in ("fresh_owned_profile", "initial_storage_match", "source_included_files_absent",
                      "source_list_completeness_absent", "reload_observed", "migration_validated"):
            mutations.append(lambda r, field=field: r[0]["facts"]["legacy_seed"].update({field: False}))
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                rows = legacy_rows()
                mutate(rows)
                self.assertEqual(legacy_scope_evidence(rows)["status"], "not_run")

    def test_current_import_state_and_visible_exclusion_must_all_match(self):
        mutations = (
            lambda r: r[1]["facts"]["import_attempt"].update(fixture_sha256="d" * 64),
            lambda r: r[1]["facts"]["import_attempt"]["storage_before"].update(sha256="d" * 64),
            lambda r: r[2]["facts"]["legacy_state"].update(seed_attempt_id="another-seed"),
            lambda r: r[2]["facts"]["legacy_state"].update(storage_sha256="d" * 64),
            lambda r: r[2]["facts"]["legacy_state"]["snapshots"][0].update(account_sha256="d" * 64),
            lambda r: r[2]["facts"]["legacy_state"]["snapshots"][0].update(list_completeness="known"),
            lambda r: r[2]["facts"]["legacy_state"]["snapshots"][1].update(is_sample=True),
            lambda r: r[2]["facts"]["legacy_state"]["snapshots"][1].update(list_completeness="unknown"),
            lambda r: r[2]["facts"]["legacy_state"]["snapshots"][1].update(included_files=[]),
            lambda r: r[2]["facts"]["legacy_state"].update(comparison_snapshot_id=LEGACY_SNAPSHOT_ID),
            lambda r: r[2].update(text="비교할 수 없어요. 기록이 없어요."),
        )
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                rows = legacy_rows()
                mutate(rows)
                self.assertEqual(legacy_scope_evidence(rows)["status"], "not_run")

    def test_normal_pair_after_setup_does_not_substitute_for_exclusion(self):
        rows = legacy_rows()
        later = imported("peekly-sample-previous.zip", storage("c"), storage("d"), "upload-later")
        self.assertEqual(legacy_scope_evidence([*rows[:2], later, rows[2]])["status"], "not_run")
        self.assertEqual(legacy_scope_evidence([*rows, later])["status"], "passed")

    def test_real_comparison_of_legacy_pair_is_failure_even_with_later_exclusion(self):
        rows = legacy_rows()
        failed = copy.deepcopy(rows[2])
        failed["text"] = "팔로워에서 빠진 사람 2명"
        failed["facts"]["list_rows"] = [{"key": "synthetic-account"}]
        for ordered in ([*rows, failed], [*rows[:2], failed, rows[2]]):
            self.assertEqual(legacy_scope_evidence(ordered)["status"], "failed")

    def test_typed_hash_admission_retains_proof_but_not_arbitrary_private_prose(self):
        facts = legacy_rows()[0]["facts"]
        self.assertEqual(_validated_observation_facts(facts), facts)
        facts["private_note"] = "Call 010-1234-5678"
        with self.assertRaises(EngineError):
            _validated_observation_facts(facts)


class CompletionReceiptTests(unittest.TestCase):
    def harness(self, rows, requirement):
        # Reuse the existing synthetic PNG admission fixture, not its tests.
        from test_peekly_result_scope import ReceiptScopeTests
        harness = ReceiptScopeTests()
        harness.setUp()
        self.addCleanup(harness.temporary.cleanup)
        task = harness.worker["claim"]["task"]
        task["requirement_ids"] = [requirement]
        task["success_criteria"] = ["Authored scope contract"]
        harness.admit(rows)
        return harness

    def test_paywall_both_receipts_bind_complete_evidence_and_veto_unbound_pass(self):
        for rows, expected in ((paywall_rows(), "passed"), (paywall_rows()[2:], "not_run")):
            with self.subTest(expected=expected):
                harness = self.harness(rows, PAYWALL_REQUIREMENT)
                for receipt in harness.receipts(harness.judgment()):
                    self.assertEqual(receipt["criteria"][0]["status"], expected)

    def test_paywall_real_failure_survives_model_pass_in_both_receipts(self):
        rows = paywall_rows()
        for control in rows[3]["facts"]["controls"]:
            control["disabled"] = False
        rows[3]["checks"] = [{"kind": "success", "index": 0, "status": "failed"}]
        harness = self.harness(rows, PAYWALL_REQUIREMENT)
        for receipt in harness.receipts(harness.judgment()):
            self.assertEqual(receipt["criteria"][0]["status"], "failed")
            self.assertEqual(receipt["outcome"], "failed")

    def test_legacy_both_receipts_require_seed_and_actual_exclusion(self):
        for rows, expected in ((legacy_rows(), "passed"), (legacy_rows()[:2], "not_run")):
            with self.subTest(expected=expected):
                harness = self.harness(rows, LEGACY_UNKNOWN_REQUIREMENT)
                for receipt in harness.receipts(harness.judgment()):
                    self.assertEqual(receipt["criteria"][0]["status"], expected)

    def test_legacy_real_failure_survives_model_pass_in_both_receipts(self):
        rows = legacy_rows()
        rows[2]["text"] = "팔로워에서 빠진 사람 2명"
        rows[2]["facts"]["list_rows"] = [{"key": "synthetic-account"}]
        rows[2]["checks"] = [{"kind": "success", "index": 0, "status": "failed"}]
        harness = self.harness(rows, LEGACY_UNKNOWN_REQUIREMENT)
        for receipt in harness.receipts(harness.judgment()):
            self.assertEqual(receipt["criteria"][0]["status"], "failed")
            self.assertEqual(receipt["outcome"], "failed")


if __name__ == "__main__":
    unittest.main()
