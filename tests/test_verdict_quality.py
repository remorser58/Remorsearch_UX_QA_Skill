"""Verdict-state semantics and per-persona task design regressions."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import _paths
from uxpersonas.agent_run import Execution, Tool
from uxpersonas.scale_entry import _persona_journey_goal
from uxpersonas.peekly_criteria import CRITERIA, evaluate
from uxpersonas.scale_run import Evidence, ScaleExecution, _project_model_observations
from uxpersonas.scale_browser_host import ScaleBrowserHost


class VerdictQualityTests(unittest.TestCase):
    def test_model_observation_projection_deduplicates_fixture_catalog_and_cumulative_uploads(self):
        catalog = [f"boundary-extra-{i:03d}.json" for i in range(531)]
        observations = []
        for i in range(16):
            observations.append({
                "id": f"obs-{i + 1}", "action": "observe", "text": "A bounded synthetic observation.",
                "facts": {
                    "available_fixtures": catalog,
                    "fixture_uploads": [f"fixture-{j}.zip" for j in range(i + 1)],
                    "fixture_validation": [{"fixture": f"fixture-{j}.zip", "archive_valid": True}
                                           for j in range(i + 1)],
                    "viewport": {"width": 756, "height": 413},
                },
                "checks": [], "captures": [{"id": f"png-{i}", "kind": "screenshot", "sha256": "a" * 64,
                                               "path": f"private-{i}.png"}],
                "artifacts": [{"id": f"png-{i}", "kind": "screenshot", "sha256": "a" * 64,
                               "path": f"private-{i}.png"}],
            })
        execution = ScaleExecution.__new__(ScaleExecution)
        execution.plan = {"tools": [], "limits": {"turns": 24}}
        task = {"id": "S-test", "goal": "test bounded request", "requirement_ids": []}
        state = {"observations": observations, "turn": 10}
        record = {"profile": {}, "provenance": {"mode": "synthetic", "research": {"claims": []}},
                  "context": {"requirements": []}}
        payload = execution.payload({"job": {"task": task}}, state, record, "model")
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        projected = payload["observations"]
        projected_catalog = payload["fixture_catalog"]
        self.assertLess(len(encoded), 262144)
        self.assertEqual(projected_catalog, catalog)
        self.assertEqual(sum(len(row["facts"]["fixture_uploads_delta"]) for row in projected), 16)
        self.assertEqual([row["facts"]["fixture_uploads_delta"] for row in projected[:3]],
                         [["fixture-0.zip"], ["fixture-1.zip"], ["fixture-2.zip"]])
        self.assertEqual(sum(len(row["facts"]["fixture_validation_delta"]) for row in projected), 16)
        self.assertNotIn("available_fixtures", projected[-1]["facts"])
        self.assertNotIn("fixture_uploads", projected[-1]["facts"])
        self.assertNotIn("path", projected[-1]["captures"][0])

    def test_structural_dom_selectors_are_typed_metadata_not_free_user_text(self):
        tool = Tool("upload", "Select an owned fixture.", {
            "selector": "string", "file": "string"}, "owned_fixture_write")
        valid = {"selector": "body>div:nth-of-type(2)>section:nth-of-type(1)>input:nth-of-type(1)",
                 "file": "@group:peekly-loose-512-valid"}
        self.assertEqual(tool.validate(valid), valid)
        with self.assertRaises(Exception):
            tool.validate({"selector": "#account-123456", "file": "peekly-sample-current.zip"})
        with self.assertRaises(Exception):
            tool.validate({"selector": "body>input:nth-of-type(1)", "file": "../outside.zip"})

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
        self.assertIn("아이디나 이름으로 찾기", _persona_journey_goal("Use Peekly.", ["PRD-RESULT-SEARCH"]))
        self.assertIn("MatrixTab", _persona_journey_goal("Use Peekly.", ["PRD-SAMPLE-EXPORT"]))
        self.assertIn("not_run", _persona_journey_goal("Use Peekly.", ["PRD-SNAPSHOT-RETENTION"]))

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
        uploads = ("peekly-format-html.zip", "peekly-format-json.zip")
        validation = [{"fixture": "peekly-format-html.zip", "archive_valid": True,
                       "complete_html_documents": True, "html_documents": [
                           {"member": "followers.html", "complete_html_document": True}]}]
        history = [{"text": text, "facts": {"fixture_uploads": ["peekly-format-html.zip"],
            "fixture_validation": validation}}]
        current = dict(facts, fixture_uploads=list(uploads), fixture_validation=validation)
        checks = evaluate(task, current, text, uploads, history)
        self.assertEqual(checks, [{"kind": "success", "index": 0, "status": "passed"}])

    def test_incomplete_html_fixture_is_not_misreported_as_a_product_failure(self):
        task = {"requirement_ids": ["PRD-IMPORT-FORMATS"]}
        uploads = ("peekly-format-html.zip", "peekly-format-json.zip")
        validation = [{"fixture": "peekly-format-html.zip", "archive_valid": True,
                       "complete_html_documents": False, "html_documents": [
                           {"member": "followers.html", "complete_html_document": False}]}]
        history = [{"text": "파일에서 팔로워·팔로잉 목록을 읽지 못했어요.",
                    "facts": {"fixture_uploads": ["peekly-format-html.zip"],
                              "fixture_validation": validation}}]
        facts = {"fixture_uploads": list(uploads), "fixture_validation": validation}
        checks = evaluate(task, facts, "JSON 결과 1명 1명 0명", uploads, history)
        self.assertEqual(checks[0]["status"], "not_run")
        self.assertIn("fixture", checks[0]["reason"])

    def test_browser_fixture_audit_detects_incomplete_and_complete_html_documents(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            host = ScaleBrowserHost.__new__(ScaleBrowserHost)
            host.fixtures = root
            with zipfile.ZipFile(root / "incomplete.zip", "w") as archive:
                archive.writestr("followers.html", "<!doctype html><div>followers</div>")
            with zipfile.ZipFile(root / "complete.zip", "w") as archive:
                archive.writestr("followers.html", "<!doctype html><html><body>followers</body></html>")
            incomplete = host._validate_fixture_upload("incomplete.zip")
            complete = host._validate_fixture_upload("complete.zip")
        self.assertFalse(incomplete["complete_html_documents"])
        self.assertTrue(complete["complete_html_documents"])

    def test_current_more_import_route_replaces_legacy_request_guide_shortcut(self):
        task = {"requirement_ids": ["PRD-START-IMPORT", "PRD-START-SKIP"]}
        facts = {"file_inputs": [{"accept": ".zip,.json,.html"}], "controls": []}
        text = "더보기 이미 받은 자료로 확인하기 파일 고르기"
        checks = evaluate(task, facts, text)
        self.assertEqual([row["status"] for row in checks], ["passed", "passed"])
        legacy_only = evaluate({"requirement_ids": ["PRD-START-SKIP"]},
            {"file_inputs": [], "controls": []}, "이미 파일을 받았어요")
        self.assertEqual(legacy_only[0]["status"], "not_run")

    def test_sample_export_is_only_judged_on_sample_matrix_tab(self):
        task = {"requirement_ids": ["PRD-SAMPLE-EXPORT"]}
        buttons = [
            {"tag": "button", "label": "목록 복사", "disabled": True,
             "title": "샘플 목록은 복사할 수 없어요."},
            {"tag": "button", "label": "목록 저장", "disabled": True,
             "title": "샘플 목록은 저장할 수 없어요."},
        ]
        history = [{"text": "샘플로 먼저 둘러보기", "facts": {
            "last_action_label": "샘플로 먼저 둘러보기", "fixture_uploads": []}}]
        sample_facts = {"controls": buttons, "fixture_uploads": [], "list_rows": []}
        sample_text = "미맞팔 3 나만 팔로우 2 맞팔 해제 1 목록 복사 목록 저장"
        self.assertEqual(evaluate(task, sample_facts, sample_text, (), history),
                         [{"kind": "success", "index": 0, "status": "passed"}])
        real_facts = {"controls": [dict(buttons[0], disabled=False, title=""),
                                    dict(buttons[1], disabled=False, title="")],
                      "fixture_uploads": ["peekly-sample-current.zip"]}
        real = evaluate(task, real_facts, sample_text, ("peekly-sample-current.zip",), ())
        self.assertEqual(real[0]["status"], "not_run")
        missing = evaluate(task, {"controls": [], "fixture_uploads": [], "list_rows": []},
                           sample_text, (), history)
        self.assertEqual(missing[0]["status"], "failed")

    def test_search_uses_current_text_input_placeholder(self):
        task = {"requirement_ids": ["PRD-RESULT-SEARCH"]}
        large = {"text": "관계 목록", "facts": {
            "controls": [{"tag": "input", "type": "text", "placeholder": "아이디나 이름으로 찾기"}],
            "list_rows": [{"key": f"user-{i:02d}"} for i in range(9)]}}
        filtered = {"text": "검색 결과", "facts": {
            "controls": [{"tag": "input", "type": "text", "placeholder": "아이디나 이름으로 찾기"}],
            "list_rows": [{"key": "synthetic_user"}],
            "typed_input_checks": [{"retained": True}]}}
        checks = evaluate(task, filtered["facts"], filtered["text"], (), [large])
        self.assertEqual(checks[0]["status"], "passed")

    def test_retention_requires_eleven_distinct_uploads_and_current_history_count(self):
        task = {"requirement_ids": ["PRD-SNAPSHOT-RETENTION"]}
        names = [f"peekly-retention-snapshot-{i:02d}.zip" for i in range(1, 12)]
        facts = {"fixture_uploads": names, "controls": []}
        checks = evaluate(task, facts, "10번의 관계 기록 최근 10번까지 이 기기에 보관해요.", names)
        self.assertEqual(checks[0]["status"], "passed")
        checks = evaluate(task, dict(facts, fixture_uploads=names[:-1]),
                          "10번의 관계 기록 최근 10번까지 이 기기에 보관해요.", names[:-1])
        self.assertEqual(checks[0]["status"], "not_run")

    def test_paywall_boundary_requires_free_latest_comparison_and_pro_history_evidence(self):
        task = {"requirement_ids": ["PRD-PAYWALL-BOUNDARY"]}
        uploads = ("peekly-sample-previous.zip", "peekly-sample-current.zip")
        free = {"text": "팔로워에서 빠진 사람 2명", "facts": {"list_rows": [{"key": "[handle]"}]}}
        history = {"text": "기록 살펴보기 비교 시작 기록 비교 종료 기록", "facts": {
            "controls": [
                {"tag": "select", "label": "비교 시작 기록", "disabled": True},
                {"tag": "select", "label": "비교 종료 기록", "disabled": True},
            ]}}
        pro = {"text": "변화 타임라인 두 시점 비교 사람별 관계 이력", "facts": {"controls": []}}
        checks = evaluate(task, pro["facts"], pro["text"], uploads, [free, history])
        self.assertEqual(checks[0]["status"], "passed")
        checks = evaluate(task, free["facts"], free["text"], uploads, [free])
        self.assertEqual(checks[0]["status"], "not_run")

    def test_product_privacy_requires_product_notice_not_host_network_block(self):
        task = {"requirement_ids": ["PRD-PRIVACY-LOCAL"]}
        facts = {"file_inputs": [{"accept": ".zip"}], "network_policy": {"external_requests_blocked": True}}
        self.assertEqual(evaluate(task, facts, "기기 안에서 처리", ())[0]["status"], "failed")
        self.assertEqual(evaluate(task, facts, "파일은 이 기기 안에서만 읽어요. 어디로도 보내지 않아요.", ())[0]["status"], "passed")

    def test_native_failure_is_emitted_only_after_triggering_fixture(self):
        task = {"requirement_ids": ["PRD-IMPORT-MISSING"]}
        facts = {"controls": [], "file_inputs": [], "network_policy": {}}
        checks = evaluate(task, facts, "결과를 불러왔어요", ())
        self.assertEqual(checks[0]["status"], "not_run")
        history = [
            {"text": "결과를 불러왔어요", "facts": {"uploaded_fixture": "peekly-missing-followers.zip"}},
            {"text": "결과를 불러왔어요", "facts": {"uploaded_fixture": "peekly-missing-following.zip"}},
        ]
        checks = evaluate(task, facts, "결과를 불러왔어요",
            ("peekly-missing-followers.zip", "peekly-missing-following.zip"), history)
        self.assertEqual([(row["kind"], row["index"], row["status"]) for row in checks],
                         [("success", 0, "failed")])

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

    def test_native_not_run_reason_is_preserved_in_receipt(self):
        worker = {"claim": {"task": {"id": "task", "success_criteria": ["retention"],
            "recovery_criteria": []}, "binding": {"revision": 1, "profile_sha256": "a" * 64}},
            "queue_claim": {"owner": "worker", "lease_token": "b" * 64}}
        observation = {"id": "obs-1", "action": "observe", "text": "History not opened.",
            "checks": [{"kind": "success", "index": 0, "status": "not_run",
                        "reason": "Eleven distinct snapshots were not imported."}],
            "artifacts": [{"id": "png-1", "kind": "screenshot"}]}
        with patch("uxpersonas.scale_run.swarm._receipt", side_effect=lambda root, job, value: value):
            receipt = Evidence(".").receipt(worker, {"observations": [observation]},
                {"build": {"sha256": "c" * 64}}, judgment=None)
        self.assertEqual(receipt["criteria"][0]["status"], "not_run")
        self.assertEqual(receipt["criteria"][0]["observation"], "Eleven distinct snapshots were not imported.")
        self.assertEqual(receipt["criteria"][0]["evidence_ids"], [])

    def test_native_not_run_reason_is_admitted_but_reason_cannot_mask_a_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence_root = root / "evidence" / "task-test" / "1"
            evidence_root.mkdir(parents=True)
            execution = Execution.__new__(Execution)
            execution.root = root
            worker = {"context_id": "ctx-test", "observations": [], "claim": {
                "task": {"id": "task-test", "success_criteria": ["Open history"], "recovery_criteria": []},
                "binding": {"revision": 1, "profile_sha256": "a" * 64},
                "evidence_path": str(evidence_root), "attempt": 1}}
            valid = {"text": "History was not opened.", "facts": {}, "captures": [],
                "checks": [{"kind": "success", "index": 0, "status": "not_run",
                            "reason": "History screen was not reached; click action unavailable."}]}
            observed = execution.observation(worker, "inspect history", valid, 1)
            self.assertEqual(observed["checks"][0]["reason"], valid["checks"][0]["reason"])
            invalid = {**valid, "checks": [{"kind": "success", "index": 0, "status": "passed",
                                             "reason": "This must not hide missing evidence."}]}
            with self.assertRaises(Exception):
                execution.observation(worker, "inspect history", invalid, 2)
