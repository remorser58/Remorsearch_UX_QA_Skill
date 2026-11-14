"""Evidence-bound coverage checks: no synthetic success from labels or stale UI."""
import unittest

import _paths
from uxpersonas.peekly_criteria import evaluate


def snapshot(char="a", keys=None, available=True):
    return {"available": available,
            "keys": ["peekly_state_v7"] if keys is None else keys,
            "sha256": char * 64 if available else None}


def observation(text="", **facts):
    return {"text": text, "facts": facts}


def attempt(tool="upload_cancel", **overrides):
    value = {
        "schema_version": "peekly-import-attempt.v1", "attempt_id": "upload-7",
        "tool": tool, "fixture": "peekly-progress-sample.zip",
        "fixture_sha256": "f" * 64,
        "storage_before": snapshot(), "storage_after": snapshot(),
        "persistence_unchanged": True,
        "phase_samples": [{"text": "파일을 읽고\u00a0있어요"},
                          {"text": "팔로우 목록을 확인하고\u00a0있어요"}],
        "cancel_active": True, "cancel_dispatched": True,
        "terminal_state": "cancelled_without_new_result",
    }
    value.update(overrides)
    return value


def status(requirement, history, facts=None, text=""):
    return evaluate({"requirement_ids": [requirement]}, facts or {}, text,
                    (), history)[0]["status"]


class CoverageEvidenceTests(unittest.TestCase):
    def test_missing_lists_each_need_their_own_nbsp_normalized_rejection(self):
        message = "팔로워와 팔로잉\u00a0목록이 모두\u00a0들어 있는 파일이 필요해요"
        rows = [observation(message, uploaded_fixture=name) for name in
                ("peekly-missing-followers.zip", "peekly-missing-following.zip")]
        self.assertEqual(status("PRD-IMPORT-MISSING", rows), "passed")
        rows[1]["text"] = "파일을 읽고 있어요"
        self.assertEqual(status("PRD-IMPORT-MISSING", rows), "not_run")

    def test_one_rejected_missing_list_does_not_hide_other_accepted_upload(self):
        rows = [
            observation("팔로워와 팔로잉 목록이 모두 들어 있는 파일이 필요해요",
                        uploaded_fixture="peekly-missing-followers.zip"),
            observation("결과를 불러왔어요.", uploaded_fixture="peekly-missing-following.zip"),
        ]
        self.assertEqual(status("PRD-IMPORT-MISSING", rows), "failed")

    def test_progress_scoped_receipt_is_not_poisoned_by_prior_setup_result(self):
        rows = [observation("결과를 불러왔어요.", uploaded_fixture="peekly-sample-current.zip"),
                observation("가져오기를 멈췄어요.", import_attempt=attempt())]
        self.assertEqual(status("PRD-IMPORT-PROGRESS", rows), "passed")

    def test_requested_cancel_label_cannot_prove_a_dispatch_or_persistence(self):
        rows = [observation("파일을 읽고 있어요 팔로우 목록을 확인하고 있어요",
                            last_action_label="읽기 멈추기")]
        self.assertEqual(status("PRD-IMPORT-PROGRESS", rows), "not_run")

    def test_missed_cancel_window_is_not_product_failure(self):
        a = attempt(cancel_active=False, cancel_dispatched=False,
                    terminal_state="already_completed", storage_after=snapshot("b"))
        self.assertEqual(status("PRD-IMPORT-PROGRESS",
                                [observation("결과를 불러왔어요", import_attempt=a)]), "not_run")

    def test_late_completion_after_actual_active_cancel_is_failed(self):
        a = attempt(terminal_state="completed_after_cancel", storage_after=snapshot("b"))
        self.assertEqual(status("PRD-IMPORT-PROGRESS", [observation(import_attempt=a)]), "failed")

    def test_denied_storage_does_not_prove_unchanged_result(self):
        a = attempt(storage_before=snapshot(available=False),
                    storage_after=snapshot(available=False))
        self.assertEqual(status("PRD-IMPORT-PROGRESS", [observation(import_attempt=a)]), "not_run")

    def test_old_completion_copy_without_changed_persistence_is_not_failure(self):
        for after in (snapshot(), snapshot(available=False)):
            a = attempt(terminal_state="completed_after_cancel", storage_after=after)
            self.assertEqual(status("PRD-IMPORT-PROGRESS", [observation(import_attempt=a)]), "not_run")

    def test_later_cancel_success_does_not_erase_verified_failure(self):
        failed = attempt(terminal_state="completed_after_cancel", storage_after=snapshot("b"))
        passed = attempt(attempt_id="upload-8")
        rows = [observation(import_attempt=failed), observation(import_attempt=passed)]
        self.assertEqual(status("PRD-IMPORT-PROGRESS", rows), "failed")
        self.assertEqual(status("PRD-IMPORT-PROGRESS", list(reversed(rows))), "failed")

    def test_another_fixture_phase_cannot_complete_progress_contract(self):
        a = attempt(phase_samples=[{"text": "파일을 읽고 있어요"}])
        b = attempt(tool="upload", fixture="another.zip",
                    phase_samples=[{"text": "팔로우 목록을 확인하고 있어요"}])
        rows = [observation(import_attempt=b), observation(import_attempt=a)]
        self.assertEqual(status("PRD-IMPORT-PROGRESS", rows), "not_run")

    def save_failure_rows(self):
        a = attempt(tool="upload_save_failure", fixture="peekly-sample-previous.zip",
                    terminal_state="storage_fault_consumed",
                    storage_fault={"key": "peekly_state_v7", "consumed": True, "restored": True})
        error = observation("결과를 저장하지 못했어요. 다시 저장",
                            import_attempt=a, import_attempt_id="upload-7",
                            storage_snapshot=snapshot())
        retry = observation("결과를 불러왔어요.",
                            import_attempt_id="upload-7", storage_snapshot=snapshot("b"),
                            click_dispatch={"dispatched": True, "hit_test": True,
                                            "label": "다시 저장"})
        return [error, retry]

    def test_save_failure_requires_same_attempt_consumed_fault_preservation_and_retry(self):
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", self.save_failure_rows()), "passed")

    def test_later_unrelated_upload_cannot_prove_retry_success(self):
        rows = self.save_failure_rows()
        rows[1]["facts"]["import_attempt_id"] = "upload-8"
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "not_run")

    def test_same_attempt_unrelated_click_cannot_prove_retry_success(self):
        rows = self.save_failure_rows()
        rows[1]["text"] = "저장 중"
        rows[1]["facts"]["storage_snapshot"] = snapshot()
        rows.append(observation("결과를 불러왔어요.", last_action="click",
                                import_attempt_id="upload-7", storage_snapshot=snapshot("b"),
                                click_dispatch={"dispatched": True, "hit_test": True, "label": "샘플로 둘러보기"}))
        rows.append(observation("결과를 불러왔어요.", last_action="wait",
                                import_attempt_id="upload-7", storage_snapshot=snapshot("b")))
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "not_run")

    def test_retry_can_settle_on_subsequent_observe_without_other_action(self):
        rows = self.save_failure_rows()
        rows[1]["text"] = "저장 중"
        rows[1]["facts"]["storage_snapshot"] = snapshot()
        rows.append(observation("결과를 불러왔어요.", last_action="observe",
                                import_attempt_id="upload-7", storage_snapshot=snapshot("b")))
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "passed")

    def test_save_failure_must_restore_fault_and_actually_dispatch_retry(self):
        for mutate in (
            lambda rows: rows[0]["facts"]["import_attempt"]["storage_fault"].update(restored=False),
            lambda rows: rows[1]["facts"].update(click_dispatch={"dispatched": False}),
            lambda rows: rows[0]["facts"]["import_attempt"]["storage_fault"].update(consumed=False),
        ):
            rows = self.save_failure_rows()
            mutate(rows)
            self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "not_run")

    def test_visible_save_error_with_changed_previous_result_is_failure(self):
        rows = self.save_failure_rows()
        rows[0]["facts"]["import_attempt"]["storage_after"] = snapshot("c")
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "failed")

    def missing_retry_rows(self):
        rows = self.save_failure_rows()[:1]
        rows[0]["text"] = "저장 공간이 부족해서 저장하지 못했어요. 지금 결과는 그대로 있어요. 공간을 비운 뒤 다시 불러와 주세요."
        rows[0]["facts"]["controls"] = [
            {"tag": "button", "label": "다른 파일 고르기", "visible": True, "disabled": False}
        ]
        return rows

    def test_observed_write_failure_without_required_retry_is_executed_failure(self):
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", self.missing_retry_rows()), "failed")

    def test_error_wording_without_consumed_fault_is_not_execution_evidence(self):
        rows = self.missing_retry_rows()
        rows[0]["facts"]["import_attempt"]["storage_fault"]["consumed"] = False
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "not_run")

    def test_transitional_or_truncated_controls_cannot_prove_missing_retry(self):
        for controls in ([], [{"label": "다른 파일 고르기", "visible": True}] * 100,
                         [{"label": "다른 파일 고르기", "visible": False}]):
            rows = self.missing_retry_rows()
            rows[0]["facts"]["controls"] = controls
            self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "not_run")

    def test_reupload_workaround_does_not_erase_missing_direct_retry(self):
        rows = self.missing_retry_rows()
        rows.append(observation("결과를 불러왔어요.", import_attempt_id="upload-8",
                                last_action="upload", storage_snapshot=snapshot("b")))
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "failed")

    def test_visible_write_error_after_retry_cannot_become_a_pass(self):
        rows = self.save_failure_rows()
        rows[0]["text"] = "저장 공간이 부족해서 저장하지 못했어요. 다시 저장"
        rows[1]["text"] = "저장 공간이 부족해서 저장하지 못했어요. 나를 맞팔 안 한 사람 1명 내가 맞팔 안 한 사람 1명 맞팔 중인 사람 0명"
        self.assertEqual(status("PRD-IMPORT-SAVE-FAIL", rows), "not_run")

    def test_identity_first_record_preview_cannot_be_failed_for_missing_comparison_copy(self):
        self.assertEqual(status("PRD-IDENTITY-LIMIT", [
            observation("다음에 새로 확인하면 달라진 관계를 비교해요. 변화 기록 보기")
        ]), "not_run")
        text = "팔로워에서 빠진\u00a0사람 6명 아이디 변경이나 계정 삭제 때문일 수도 있어요"
        self.assertEqual(status("PRD-IDENTITY-LIMIT", [
            observation(text, list_rows=[{"key": "synthetic_member"}])
        ]), "passed")
        self.assertEqual(status("PRD-IDENTITY-LIMIT", [
            observation("팔로워에서 빠진 사람 6명", list_rows=[{"key": "synthetic_member"}])
        ]), "failed")

    def test_retention_uses_only_history_after_eleventh_distinct_import(self):
        task = {"requirement_ids": ["PRD-SNAPSHOT-RETENTION"]}
        names = [f"peekly-retention-snapshot-{i:02d}.zip" for i in range(1, 12)]
        earlier = observation("3번의 관계 기록", fixture_uploads=names[:3])
        latest = observation("10번의\u00a0관계 기록", fixture_uploads=names)
        result = evaluate(task, latest["facts"], latest["text"], names, [earlier])
        self.assertEqual(result[0]["status"], "passed")
        earlier["text"] = "10번의 관계 기록"
        result = evaluate(task, {"fixture_uploads": names}, "기록 화면을 아직 열지 않음",
                          names, [earlier])
        self.assertEqual(result[0]["status"], "not_run")


if __name__ == "__main__":
    unittest.main()
