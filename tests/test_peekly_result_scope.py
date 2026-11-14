"""Offline regressions for saved Peekly evidence and authored scope positives.

Golden JSON is a minimal, hash-referenced projection of saved observations.
Actual 026 includes a saved positive search. Authored variants and unit PNGs are
explicitly synthetic contract inputs; these tests run no browser/model process.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import _paths
from ergoqa.png import encode, new_image
from uxpersonas.agent_run import Execution
from uxpersonas.peekly_criteria import (
    CRITERIA, LEGACY_UNKNOWN_REASON, LEGACY_UNKNOWN_REQUIREMENT,
    RESULT_CURRENT_FIXTURE, RESULT_CURRENT_SHA256, RESULT_SCOPE_KEYS,
    SEARCH_FIXTURE, SEARCH_KEYS, SEARCH_QUERY, SEARCH_QUERY_SHA256, SEARCH_REQUIREMENT,
    SIZE_REQUIREMENT, evaluate, result_scope_evidence, search_scope_evidence, size_scope_evidence,
    DELETE_REQUIRED_KEYS, DELETE_REQUIREMENT, delete_scope_evidence,
)
from uxpersonas.scale_run import Evidence
from uxresearch.canonical import EngineError, byte_digest


FIXTURES = Path(__file__).with_name("fixtures")
RESULT_IDS = list(RESULT_SCOPE_KEYS)


def golden(name="peekly_result_scope_017.json"):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))["observations"]


def original(number):
    return next(row for row in golden() if row["id"] == f"obs-{number}")


def synthetic_visit(requirement=RESULT_IDS[0]):
    """Authored same-attempt positive, not an actual post-import browser visit."""
    anchor = original(16)
    row = original({RESULT_IDS[0]: 4, RESULT_IDS[1]: 6, RESULT_IDS[2]: 8}[requirement])
    row["id"] = "synthetic-category"
    row["text"] = "\n".join(line for line in row["text"].splitlines() if "샘플" not in line)
    row["facts"].update(import_attempt_id=anchor["facts"]["import_attempt_id"],
                        storage_snapshot=copy.deepcopy(anchor["facts"]["storage_snapshot"]),
                        fixture_uploads=[RESULT_CURRENT_FIXTURE])
    anchor["checks"] = row["checks"] = []
    return [anchor, row]


def statuses(rows, ids=RESULT_IDS):
    return {check["index"]: check["status"] for check in evaluate(
        {"requirement_ids": ids}, {}, "", rows[-1]["facts"].get("fixture_uploads", []), rows)}


class RelationshipScopeTests(unittest.TestCase):
    def test_actual_017_sample_lists_do_not_replace_imported_category_visits(self):
        self.assertEqual(statuses(golden(), RESULT_IDS + ["PRD-RESULT-SNAPSHOT"]),
                         {0: "not_run", 1: "not_run", 2: "not_run", 3: "passed"})

    def test_current_oracle_names_equal_sample_names_so_provenance_is_essential(self):
        for rid, number in zip(RESULT_IDS, (4, 6, 8)):
            with self.subTest(requirement=rid):
                self.assertEqual({person["key"] for person in original(number)["facts"]["list_rows"]},
                                 RESULT_SCOPE_KEYS[rid])
                self.assertEqual(result_scope_evidence([original(number)], rid)["status"], "not_run")

    def test_authored_valid_current_visit_passes_only_its_own_category(self):
        for index, rid in enumerate(RESULT_IDS):
            with self.subTest(requirement=rid):
                expected = {i: "passed" if i == index else "not_run" for i in range(3)}
                self.assertEqual(statuses(synthetic_visit(rid)), expected)

    def test_actual_departed_list_is_not_any_relationship_category(self):
        self.assertEqual(statuses([original(16), original(18)]),
                         {0: "not_run", 1: "not_run", 2: "not_run"})

    def test_old_list_before_import_cannot_be_retroactively_bound(self):
        anchor, row = synthetic_visit()
        self.assertEqual(statuses([row, anchor])[0], "not_run")

    def test_attempt_digest_fixture_and_real_dispatch_are_all_required(self):
        mutations = (
            lambda a, r: r["facts"].update(import_attempt_id="upload-other"),
            lambda a, r: r["facts"]["storage_snapshot"].update(sha256="a" * 64),
            lambda a, r: a["facts"]["import_attempt"].update(fixture_sha256="b" * 64),
            lambda a, r: a["facts"]["import_attempt"].update(fixture="peekly-sample-previous.zip"),
            lambda a, r: a["facts"].pop("import_attempt"),
            lambda a, r: r["facts"].pop("click_dispatch"),
            lambda a, r: r["facts"]["click_dispatch"].update(dispatched=False),
            lambda a, r: r["facts"]["click_dispatch"].update(hit_test=False),
            lambda a, r: r["facts"]["click_dispatch"].update(verified_selector=""),
            lambda a, r: r["facts"].update(last_action_label="Different card"),
            lambda a, r: a["facts"]["import_attempt"].update(phase_samples=[]),
            lambda a, r: a["facts"]["storage_snapshot"].update(available=False),
        )
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                anchor, row = synthetic_visit()
                mutate(anchor, row)
                self.assertEqual(statuses([anchor, row])[0], "not_run")

    def test_sample_state_invalidates_even_matching_attempt_and_names(self):
        anchor, row = synthetic_visit()
        row["text"] = "샘플을 보고\u00a0있어요.\n" + row["text"]
        self.assertEqual(statuses([anchor, row])[0], "not_run")

    def test_upload_label_or_cumulative_fixture_membership_is_not_an_import_anchor(self):
        _, row = synthetic_visit()
        fake = {"text": "결과를 불러왔어요.", "facts": {
            "fixture_uploads": [RESULT_CURRENT_FIXTURE], "uploaded_fixture": RESULT_CURRENT_FIXTURE,
            "last_action": "upload"}}
        self.assertEqual(statuses([fake, row])[0], "not_run")

    def test_delayed_list_observation_can_complete_only_the_same_open_interval(self):
        anchor, click = synthetic_visit()
        observed = copy.deepcopy(click)
        observed["facts"]["last_action"] = "observe"
        click["facts"]["list_rows"] = []
        click["text"] = "Category click dispatched; rendering not yet observed."
        proof = result_scope_evidence([anchor, click, observed], RESULT_IDS[0])
        self.assertEqual(proof["status"], "passed")
        self.assertEqual(proof["indices"], [0, 1, 2])
        closed = copy.deepcopy(observed)
        closed["facts"].update(last_action="click", last_action_label="닫기",
            click_dispatch={"dispatched": True, "hit_test": True,
                            "label": "닫기", "verified_selector": "body>button"})
        self.assertEqual(statuses([anchor, click, closed, observed])[0], "not_run")

    def test_unrelated_upload_ends_the_old_import_and_list_interval(self):
        anchor, row = synthetic_visit()
        interrupted = {"text": "Upload rejected.", "facts": {
            "last_action": "upload", "uploaded_fixture": "peekly-malformed-html.zip",
            "import_attempt_id": "upload-new"}}
        self.assertEqual(statuses([anchor, interrupted, row])[0], "not_run")

    def test_dashboard_labels_and_empty_or_unobserved_list_do_not_complete_criterion(self):
        for missing in ("heading", "people"):
            with self.subTest(missing=missing):
                anchor, row = synthetic_visit()
                if missing == "heading":
                    row["text"] = "나를 맞팔 안 한 사람\n5\n명"
                else:
                    row["facts"]["list_rows"] = []
                self.assertEqual(statuses([anchor, row])[0], "not_run")

    def test_bound_wrong_card_count_list_count_or_keys_is_a_failure(self):
        mutations = (
            lambda r: r["facts"]["list_rows"].pop(),
            lambda r: r["facts"]["list_rows"][0].update(key="synthetic_wrong_account"),
            lambda r: r["facts"]["list_rows"][0].update(key=r["facts"]["list_rows"][1]["key"]),
            lambda r: r.update(text=r["text"].replace("사람 5명", "사람 4명")),
        )
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                anchor, row = synthetic_visit()
                mutate(row)
                self.assertEqual(statuses([anchor, row])[0], "failed")
        anchor, row = synthetic_visit()
        for key in ("label",):
            row["facts"]["click_dispatch"][key] = row["facts"]["click_dispatch"][key].replace("5 명", "4 명")
        row["facts"]["last_action_label"] = row["facts"]["click_dispatch"]["label"]
        self.assertEqual(statuses([anchor, row])[0], "failed")

    def test_later_correct_visit_cannot_erase_a_bound_category_failure(self):
        anchor, wrong = synthetic_visit()
        correct = copy.deepcopy(wrong)
        wrong["facts"]["list_rows"][0]["key"] = "synthetic_wrong_account"
        self.assertEqual(statuses([anchor, wrong, correct])[0], "failed")

    def test_unchanged_digest_requires_a_previously_bound_current_import(self):
        anchor, row = synthetic_visit()
        repeated = copy.deepcopy(anchor)
        repeated["facts"]["import_attempt_id"] = "upload-repeat"
        repeated["facts"]["import_attempt"].update(
            attempt_id="upload-repeat", storage_before=copy.deepcopy(anchor["facts"]["storage_snapshot"]))
        row["facts"]["import_attempt_id"] = "upload-repeat"
        self.assertEqual(statuses([repeated, row])[0], "not_run")
        self.assertEqual(statuses([anchor, repeated, row])[0], "passed")


class ReceiptScopeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.evidence_path = self.root / "evidence/task-scope/1"
        self.evidence_path.mkdir(parents=True)
        raw = encode(new_image(2, 2))  # Authored unit PNG, never a browser capture.
        screen = self.evidence_path / "synthetic-screen.png"
        screen.write_bytes(raw)
        screen.chmod(0o600)
        self.capture = {"path": screen.name, "sha256": byte_digest(raw)}
        self.worker = {
            "context_id": "ctx-scope", "observations": [],
            "claim": {"task": {"id": "task-scope", "requirement_ids": RESULT_IDS + ["PRD-RESULT-SNAPSHOT"],
                              "success_criteria": ["Category A", "Category B", "Category C", "Snapshot"],
                              "recovery_criteria": []},
                      "binding": {"revision": 1, "profile_sha256": "a" * 64},
                      "evidence_path": str(self.evidence_path), "attempt": 1},
            "queue_claim": {"owner": "worker", "lease_token": "b" * 64},
        }
        self.scale = Evidence(self.root)
        self.execution = Execution.__new__(Execution)
        self.execution.root = self.root
        self.execution.validate_claim = lambda worker: {
            "drafting_guidance": {}, "outcome": "inconclusive",
            "criteria": [{"kind": "success", "index": i, "status": "not_run",
                          "observation": "Not observed.", "evidence_ids": []}
                         for i in range(len(worker["claim"]["task"]["success_criteria"]))]}

    def admit(self, rows):
        admitted = []
        for number, row in enumerate(rows, 1):
            result = {"text": row["text"], "facts": copy.deepcopy(row["facts"]),
                      "checks": copy.deepcopy(row.get("checks", [])), "captures": [self.capture]}
            admitted.append(self.scale.observation(self.worker, "offline authored admission", result, number))
        self.worker["observations"] = admitted
        return admitted

    def judgment(self, statuses=None):
        count = len(self.worker["claim"]["task"]["success_criteria"])
        statuses = statuses or ["passed"] * count
        return {"reason": "Authored model proposal for offline boundary regression.",
                "criteria": [{"kind": "success", "index": i, "status": status,
                              "observation": "Model proposal.",
                              "observation_ids": [f"obs-{min(i + 1, len(self.worker['observations']))}"]
                                  if status in {"passed", "failed"} else []}
                             for i, status in enumerate(statuses)]}

    def receipts(self, judgment):
        with patch("uxpersonas.scale_run.swarm._receipt", side_effect=lambda root, job, value: value):
            yield self.execution.make_receipt(self.worker, judgment=judgment)
            yield self.scale.receipt(self.worker, {"observations": self.worker["observations"]},
                                     {"build": {"sha256": "c" * 64}}, judgment=judgment)

    def test_both_receipts_veto_actual_sample_only_model_pass_without_job_error(self):
        self.admit(golden())
        for receipt in self.receipts(self.judgment()):
            self.assertEqual([c["status"] for c in receipt["criteria"]],
                             ["not_run", "not_run", "not_run", "passed"])
            self.assertTrue(all(not c["evidence_ids"] for c in receipt["criteria"][:3]))
            self.assertEqual(receipt["outcome"], "inconclusive")

    def test_valid_positive_rebinds_model_sample_references_to_import_and_list(self):
        rows = [original(4), *synthetic_visit()]
        for row in rows:
            row["checks"] = []
        observed = self.admit(rows)
        expected = [a["id"] for ob in observed[1:] for a in ob["artifacts"]]
        for receipt in self.receipts(self.judgment()):
            first = receipt["criteria"][0]
            self.assertEqual(first["status"], "passed")
            self.assertEqual(first["evidence_ids"], expected)
            self.assertEqual(receipt["criteria"][1]["status"], "not_run")

    def test_every_positive_step_needs_its_own_admitted_png(self):
        observed = self.admit(synthetic_visit())
        observed[0]["artifacts"] = []
        judgment = self.judgment()
        for criterion in judgment["criteria"]:
            criterion["observation_ids"] = ["obs-2"]
        for receipt in self.receipts(judgment):
            self.assertEqual(receipt["criteria"][0]["status"], "not_run")

    def test_legacy_native_pass_cannot_repromote_the_scoped_not_run(self):
        rows = golden()
        rows[0]["checks"] += [{"kind": "success", "index": i, "status": "passed"} for i in range(3)]
        self.admit(rows)
        for judgment in (None, self.judgment(["not_run", "not_run", "not_run", "passed"])):
            for receipt in self.receipts(judgment):
                self.assertEqual([c["status"] for c in receipt["criteria"][:3]], ["not_run"] * 3)

    def test_relationship_and_unrelated_native_failures_remain_immutable(self):
        rows = golden()
        rows[0]["checks"] += [{"kind": "success", "index": 0, "status": "failed"}]
        self.admit(rows)
        for receipt in self.receipts(None):
            self.assertEqual(receipt["criteria"][0]["status"], "failed")
        with self.assertRaises(EngineError) as execution_error:
            self.execution.make_receipt(self.worker, judgment=self.judgment())
        self.assertEqual(execution_error.exception.issue["code"], "erased_failure")
        with patch("uxpersonas.scale_run.swarm._receipt", side_effect=lambda root, job, value: value):
            with self.assertRaises(EngineError) as scale_error:
                self.scale.receipt(self.worker, {"observations": self.worker["observations"]},
                                   {"build": {"sha256": "c" * 64}}, judgment=self.judgment())
        self.assertEqual(scale_error.exception.issue["code"], "erased_failure")

    def test_model_failure_and_unrelated_model_pass_are_not_globally_overridden(self):
        self.admit(golden())
        for receipt in self.receipts(self.judgment(["failed", "not_run", "not_run", "passed"])):
            self.assertEqual(receipt["criteria"][0]["status"], "failed")
            self.assertEqual(receipt["criteria"][3]["status"], "passed")

    def test_actual_021_unsupported_unknown_is_nr_even_with_old_native_failed(self):
        rows = golden("peekly_legacy_unknown_021.json")
        self.worker["claim"]["task"].update(
            requirement_ids=["PRD-IMPORT-ALLTIME", "PRD-IDENTITY-LIMIT", LEGACY_UNKNOWN_REQUIREMENT],
            success_criteria=["Guide", "Identity caveat", "Unknown legacy source"])
        self.admit(rows)
        for judgment in (None, self.judgment(["passed", "passed", "failed"]),
                         self.judgment(["passed", "passed", "passed"])):
            for receipt in self.receipts(judgment):
                unknown = receipt["criteria"][2]
                self.assertEqual(unknown["status"], "not_run")
                self.assertEqual(unknown["evidence_ids"], [])
                self.assertEqual(unknown["observation"], LEGACY_UNKNOWN_REASON)



    def search_task(self):
        self.worker["claim"]["task"].update(
            requirement_ids=[SEARCH_REQUIREMENT, "PRD-PRIVACY-LOCAL", "PRD-PRIVACY-DELETE"],
            success_criteria=["Search ordered imported list", "Local notice", "Owned data deletion"])

    def test_actual_025_missing_query_vetoes_both_model_and_legacy_native_decisions(self):
        self.search_task()
        self.admit(golden("peekly_search_scope_025.json"))
        for judgment in (None, *(self.judgment([status, "passed", "not_run"])
                                 for status in ("passed", "failed", "not_run"))):
            for receipt in self.receipts(judgment):
                self.assertEqual([c["status"] for c in receipt["criteria"]],
                                 ["not_run", "passed", "not_run"])
                self.assertEqual(receipt["criteria"][0]["evidence_ids"], [])

    def test_actual_026_exact_query_corrects_legacy_placeholder_failure_in_both_receipts(self):
        self.search_task()
        observed = self.admit(golden("peekly_search_scope_026.json"))
        expected = [artifact["id"] for row in observed for artifact in row["artifacts"]]
        for judgment in (None, *(self.judgment([status, "passed", "not_run"])
                                 for status in ("passed", "failed", "not_run"))):
            for receipt in self.receipts(judgment):
                self.assertEqual([c["status"] for c in receipt["criteria"]],
                                 ["passed", "passed", "not_run"])
                self.assertEqual(receipt["criteria"][0]["evidence_ids"], expected)

    def test_search_bound_filter_failure_cannot_be_erased_by_a_model_pass(self):
        self.search_task()
        rows = golden("peekly_search_scope_026.json")
        rows[-1]["facts"]["list_rows"] = [{"key": "synthetic_wrong_account"}]
        self.admit(rows)
        for judgment in (None, self.judgment(["passed", "passed", "not_run"])):
            for receipt in self.receipts(judgment):
                self.assertEqual(receipt["criteria"][0]["status"], "failed")

    def test_search_positive_requires_png_for_import_list_and_type(self):
        self.search_task()
        observed = self.admit(golden("peekly_search_scope_026.json"))
        for missing in range(3):
            with self.subTest(missing=missing):
                saved = observed[missing]["artifacts"]
                observed[missing]["artifacts"] = []
                judgment = self.judgment(["passed", "passed", "not_run"])
                for criterion in judgment["criteria"][:2]:
                    criterion["observation_ids"] = [observed[(missing + 1) % 3]["id"]]
                for receipt in self.receipts(judgment):
                    self.assertEqual(receipt["criteria"][0]["status"], "not_run")
                observed[missing]["artifacts"] = saved

    def test_search_correction_does_not_exempt_unrelated_native_failures(self):
        self.search_task()
        rows = golden("peekly_search_scope_026.json")
        rows[-1]["checks"].append({"kind": "success", "index": 2, "status": "failed"})
        self.admit(rows)
        with self.assertRaises(EngineError) as error:
            list(self.receipts(self.judgment(["passed", "passed", "passed"])))
        self.assertEqual(error.exception.issue["code"], "erased_failure")



    def size_task(self):
        self.worker["claim"]["task"].update(
            requirement_ids=["PRD-IMPORT-PROGRESS", SIZE_REQUIREMENT, "PRD-IMPORT-SAVE-FAIL"],
            success_criteria=["Cancel active import", "Three size boundaries", "Save failure recovery"])

    def test_actual_015_size_triad_corrects_only_size_and_keeps_save_failure(self):
        self.size_task()
        observed = self.admit(golden("peekly_size_scope_015.json"))
        expected = [artifact["id"] for row in observed[:3] for artifact in row["artifacts"]]
        for judgment in (None, *(self.judgment(["passed", status, "failed"])
                                 for status in ("passed", "failed", "not_run"))):
            for receipt in self.receipts(judgment):
                self.assertEqual([c["status"] for c in receipt["criteria"]],
                                 ["passed", "passed", "failed"])
                self.assertEqual(receipt["criteria"][1]["evidence_ids"], expected)

    def test_missing_size_boundary_cannot_be_promoted_by_model_or_legacy_native_pass(self):
        self.size_task()
        rows = golden("peekly_size_scope_015.json")[:2]
        rows[-1]["checks"].append({"kind": "success", "index": 1, "status": "passed"})
        self.admit(rows)
        for judgment in (None, self.judgment(["passed", "passed", "not_run"])):
            for receipt in self.receipts(judgment):
                self.assertEqual(receipt["criteria"][1]["status"], "not_run")
                self.assertEqual(receipt["criteria"][1]["evidence_ids"], [])

    def test_accepted_invalid_size_boundary_failure_survives_later_triad_and_model_pass(self):
        self.size_task()
        rows = golden("peekly_size_scope_015.json")
        accepted = RejectionWordingScopeTests.synthetic_acceptance(rows[0])
        accepted["checks"] = [{"kind": "success", "index": 1, "status": "failed"}]
        self.admit([accepted, *rows])
        for judgment in (None, self.judgment(["passed", "passed", "failed"])):
            for receipt in self.receipts(judgment):
                self.assertEqual(receipt["criteria"][1]["status"], "failed")

    def test_size_triad_needs_a_capture_for_each_boundary(self):
        self.size_task()
        observed = self.admit(golden("peekly_size_scope_015.json"))
        observed[2]["artifacts"] = []
        judgment = self.judgment(["passed", "passed", "failed"])
        judgment["criteria"][2]["observation_ids"] = ["obs-4"]
        for receipt in self.receipts(judgment):
            self.assertEqual(receipt["criteria"][1]["status"], "not_run")



    def test_actual_025_confirmed_delete_fails_only_key_absence_in_both_receipts(self):
        self.search_task()
        observed = self.admit(golden("peekly_delete_scope_025.json"))
        expected = [artifact["id"] for index in (0, 1, 4, 5)
                    for artifact in observed[index]["artifacts"]]
        for judgment in (None, self.judgment(["not_run", "passed", "passed"]),
                         self.judgment(["not_run", "passed", "not_run"])):
            for receipt in self.receipts(judgment):
                self.assertEqual([c["status"] for c in receipt["criteria"]],
                                 ["not_run", "passed", "failed"])
                self.assertEqual(receipt["criteria"][2]["evidence_ids"], expected)
                self.assertIn("key presence only", receipt["criteria"][2]["observation"])

    def test_before_delete_confirmation_model_pass_remains_not_run(self):
        self.search_task()
        self.admit(golden("peekly_delete_scope_025.json")[:-1])
        for receipt in self.receipts(self.judgment(["not_run", "passed", "passed"])):
            self.assertEqual(receipt["criteria"][2]["status"], "not_run")
            self.assertEqual(receipt["criteria"][2]["evidence_ids"], [])

    def test_actual_delete_failure_survives_later_import_and_model_pass(self):
        self.search_task()
        rows = golden("peekly_delete_scope_025.json")
        rows[-1]["checks"].append({"kind": "success", "index": 2, "status": "failed"})
        self.admit([*rows, copy.deepcopy(rows[1])])
        for receipt in self.receipts(self.judgment(["not_run", "passed", "passed"])):
            self.assertEqual(receipt["criteria"][2]["status"], "failed")

    def test_delete_outcome_requires_a_capture_for_the_own_post_confirmation(self):
        self.search_task()
        observed = self.admit(golden("peekly_delete_scope_025.json"))
        observed[-1]["artifacts"] = []
        judgment = self.judgment(["not_run", "passed", "passed"])
        for receipt in self.receipts(judgment):
            self.assertEqual(receipt["criteria"][2]["status"], "not_run")


class LegacyUnknownScopeTests(unittest.TestCase):
    def test_actual_021_known_empty_then_normal_pair_does_not_exercise_legacy_unknown(self):
        rows = golden("peekly_legacy_unknown_021.json")
        self.assertEqual(rows[-1]["checks"][-1]["status"], "failed")  # Preserve the historical bug.
        self.assertEqual(statuses(rows, [LEGACY_UNKNOWN_REQUIREMENT]), {0: "not_run"})

    def test_unrelated_language_or_claimed_seed_cannot_fake_an_unsupported_setup(self):
        for text in ("언팔로우 6명", "비교할 수 없어요", "기록이 없어요"):
            row = {"text": text, "facts": {"legacy_unknown_seeded": True,
                   "fixture_uploads": ["peekly-empty-previous.zip", RESULT_CURRENT_FIXTURE]}}
            check = evaluate({"requirement_ids": [LEGACY_UNKNOWN_REQUIREMENT]},
                             row["facts"], row["text"], row["facts"]["fixture_uploads"])[0]
            self.assertEqual(check["status"], "not_run")
            self.assertEqual(check["reason"], LEGACY_UNKNOWN_REASON)

    def test_definition_separates_recognized_empty_input_from_unconfigured_legacy_state(self):
        spec = CRITERIA[LEGACY_UNKNOWN_REQUIREMENT]
        self.assertIn("includedFiles", spec["precondition"])
        self.assertNotIn("upload peekly-empty-previous.zip", spec["action"])
        self.assertIn("known-empty", spec["value"])


class RejectionWordingScopeTests(unittest.TestCase):
    IDS = ["PRD-IMPORT-HTML", "PRD-IMPORT-ACCOUNT"]

    @staticmethod
    def synthetic_acceptance(rejected):
        """Authored second attempt with a real completion/new-save contract."""
        accepted = copy.deepcopy(rejected)
        accepted["id"] = "synthetic-accepted-import"
        accepted["text"] = "결과를 불러왔어요."
        accepted["checks"] = []
        facts = accepted["facts"]
        new_state = copy.deepcopy(facts["import_attempt"]["storage_after"])
        new_state["sha256"] = "c" * 64
        facts["import_attempt_id"] = "upload-synthetic-accepted"
        facts["storage_snapshot"] = copy.deepcopy(new_state)
        facts["import_attempt"].update(
            attempt_id=facts["import_attempt_id"], persistence_unchanged=False,
            storage_after=new_state,
            phase_samples=[{"text": "파일을 읽고 있어요"}, {"text": "결과를 불러왔어요."}])
        return accepted

    def test_bound_acceptance_overrides_rejection_in_both_orders(self):
        rows = golden("peekly_rejection_wording_011.json")
        for rid, rejected in zip(self.IDS, (rows[1], rows[2])):
            accepted = self.synthetic_acceptance(rejected)
            for observations in ([accepted], [rejected, accepted], [accepted, rejected]):
                with self.subTest(requirement=rid, order=[row["id"] for row in observations]):
                    self.assertEqual(statuses(observations, [rid]), {0: "failed"})

    def test_stale_success_copy_without_same_attempt_completion_and_new_save_is_nr(self):
        rows = golden("peekly_rejection_wording_011.json")
        for rid, rejected in zip(self.IDS, (rows[1], rows[2])):
            stale = copy.deepcopy(rejected)
            stale["text"] = "결과를 불러왔어요."
            stale["checks"] = []
            with self.subTest(requirement=rid):
                self.assertEqual(statuses([stale], [rid]), {0: "not_run"})
                bare = {"text": "결과를 불러왔어요.", "facts": {
                    "last_action": "upload", "uploaded_fixture": rejected["facts"]["uploaded_fixture"]}}
                self.assertEqual(statuses([bare], [rid]), {0: "not_run"})

    def test_acceptance_requires_its_own_fixture_attempt_completion_and_current_saved_digest(self):
        rows = golden("peekly_rejection_wording_011.json")
        mutations = (
            lambda r: r["facts"].update(uploaded_fixture="peekly-sample-current.zip"),
            lambda r: r["facts"]["import_attempt"].update(fixture="peekly-sample-current.zip"),
            lambda r: r["facts"]["import_attempt"].update(fixture_sha256="f" * 64),
            lambda r: r["facts"].update(import_attempt_id="upload-unrelated"),
            lambda r: r["facts"]["import_attempt"].update(phase_samples=[{"text": "파일을 읽고 있어요"}]),
            lambda r: r["facts"]["import_attempt"].update(persistence_unchanged=True),
            lambda r: r["facts"]["import_attempt"].update(cancel_dispatched=True),
            lambda r: r["facts"]["import_attempt"]["storage_before"].update(available=False),
            lambda r: r["facts"]["import_attempt"]["storage_after"].update(available=False),
            lambda r: r["facts"]["storage_snapshot"].update(sha256="f" * 64),
        )
        for rid, rejected in zip(self.IDS, (rows[1], rows[2])):
            for number, mutate in enumerate(mutations):
                accepted = self.synthetic_acceptance(rejected)
                mutate(accepted)
                with self.subTest(requirement=rid, case=number):
                    self.assertEqual(statuses([accepted], [rid]), {0: "not_run"})
                    self.assertEqual(statuses([rejected, accepted], [rid]), {0: "passed"})
            accepted = self.synthetic_acceptance(rejected)
            accepted["facts"]["import_attempt"]["storage_before"] = copy.deepcopy(
                accepted["facts"]["import_attempt"]["storage_after"])
            self.assertEqual(statuses([accepted], [rid]), {0: "not_run"})

    def test_unrelated_or_separate_attempt_success_cannot_supply_completion(self):
        rows = golden("peekly_rejection_wording_011.json")
        for rid, rejected in zip(self.IDS, (rows[1], rows[2])):
            unrelated = self.synthetic_acceptance(rejected)
            unrelated["facts"]["uploaded_fixture"] = "peekly-sample-current.zip"
            later = self.synthetic_acceptance(rejected)
            later["facts"]["import_attempt"]["phase_samples"] = [{"text": "파일을 읽고 있어요"}]
            with self.subTest(requirement=rid):
                self.assertEqual(statuses([unrelated, later], [rid]), {0: "not_run"})
                self.assertEqual(statuses([rejected, unrelated, later], [rid]), {0: "passed"})

    def test_actual_011_nbsp_rejections_pass_with_their_own_preserved_attempt(self):
        rows = golden("peekly_rejection_wording_011.json")
        self.assertEqual(statuses(rows, self.IDS), {0: "passed", 1: "passed"})
        self.assertEqual(statuses([rows[0]], [self.IDS[0]]), {0: "passed"})
        self.assertEqual(statuses([rows[1]], [self.IDS[0]]), {0: "passed"})

    def test_new_wording_needs_named_fixture_id_sha_and_preserved_available_storage(self):
        rows = golden("peekly_rejection_wording_011.json")
        mutations = (
            lambda r: r["facts"].update(uploaded_fixture="peekly-sample-current.zip"),
            lambda r: r["facts"].update(import_attempt_id="upload-other"),
            lambda r: r["facts"]["import_attempt"].update(fixture_sha256="f" * 64),
            lambda r: r["facts"]["import_attempt"].update(tool="upload_cancel"),
            lambda r: r["facts"]["import_attempt"].update(persistence_unchanged=False),
            lambda r: r["facts"]["import_attempt"]["storage_after"].update(sha256="f" * 64),
            lambda r: r["facts"]["import_attempt"]["storage_before"].update(available=False),
            lambda r: r["facts"]["storage_snapshot"].update(sha256="f" * 64),
            lambda r: r["facts"].pop("import_attempt"),
        )
        for rid, base in zip(self.IDS, (rows[1], rows[2])):
            for number, mutate in enumerate(mutations):
                with self.subTest(requirement=rid, case=number):
                    row = copy.deepcopy(base)
                    mutate(row)
                    self.assertEqual(statuses([row], [rid]), {0: "not_run"})

    def test_unrelated_previous_error_cannot_score_a_later_named_upload(self):
        rows = golden("peekly_rejection_wording_011.json")
        for rid, base in zip(self.IDS, (rows[1], rows[2])):
            previous = copy.deepcopy(base)
            previous["facts"]["uploaded_fixture"] = "peekly-sample-current.zip"
            later = copy.deepcopy(base)
            later["text"] = "파일을 읽고 있어요"
            with self.subTest(requirement=rid):
                self.assertEqual(statuses([previous, later], [rid]), {0: "not_run"})

    def test_current_rejection_phrase_without_its_companion_context_stays_not_run(self):
        rows = golden("peekly_rejection_wording_011.json")
        html, account = copy.deepcopy(rows[1]), copy.deepcopy(rows[2])
        html["text"] = html["text"].replace("[followers.html]", "[unrelated.html]")
        account["text"] = "계정의 파일이에요. 다른 파일 고르기"
        self.assertEqual(statuses([html], [self.IDS[0]]), {0: "not_run"})
        self.assertEqual(statuses([account], [self.IDS[1]]), {0: "not_run"})



class SearchScopeTests(unittest.TestCase):
    def assert_search(self, rows, status):
        self.assertEqual(search_scope_evidence(rows)["status"], status)
        self.assertEqual(statuses(rows, [SEARCH_REQUIREMENT]), {0: status})

    def test_saved_025_has_an_actual_search_field_but_no_query(self):
        rows = golden("peekly_search_scope_025.json")
        field = rows[1]["facts"]["controls"][0]
        self.assertEqual((field["type"], field["label"], field["visible"], field["disabled"]),
                         ("search", "이름 또는 아이디 찾기", True, False))
        self.assertEqual(len(rows[1]["facts"]["list_rows"]), 12)
        self.assertEqual(rows[-1]["facts"]["typed_input_checks"], [])
        self.assertEqual(rows[-1]["checks"][0]["status"], "failed")  # Historical bug retained.
        self.assert_search(rows, "not_run")

    def test_saved_026_import_list_and_fresh_exact_query_pass(self):
        rows = golden("peekly_search_scope_026.json")
        self.assertEqual([r["key"] for r in rows[1]["facts"]["list_rows"]], list(SEARCH_KEYS))
        self.assertEqual(rows[2]["facts"]["typed_input_checks"][0]["actual_sha256"], SEARCH_QUERY_SHA256)
        self.assertEqual(search_scope_evidence(rows)["indices"], [0, 1, 2])
        self.assert_search(rows, "passed")

    def test_synthetic_search_does_not_require_a_particular_placeholder(self):
        rows = golden("peekly_search_scope_026.json")
        for row in rows:
            row["checks"] = []
            row["id"] = "synthetic-" + row["id"]
            for control in row["facts"]["controls"]:
                control.update(label="관계 검색", placeholder="검색할 계정")
        self.assert_search(rows, "passed")
        self.assertEqual(CRITERIA[SEARCH_REQUIREMENT]["selector"], "input[type='search']")

    def test_wrong_field_hidden_disabled_or_ambiguous_input_does_not_count(self):
        for name, mutate in (
            ("wrong field", lambda rows: rows[-1]["facts"]["typed_input_checks"][0].update(selector="#other-field")),
            ("hidden baseline", lambda rows: rows[1]["facts"]["controls"][0].update(visible=False)),
            ("hidden query", lambda rows: rows[-1]["facts"]["controls"][0].update(visible=False)),
            ("disabled", lambda rows: rows[-1]["facts"]["controls"][0].update(disabled=True)),
            ("readonly", lambda rows: rows[-1]["facts"]["controls"][0].update(readonly=True)),
            ("other input type", lambda rows: rows[-1]["facts"]["controls"][0].update(type="text")),
            ("ambiguous input", lambda rows: rows[-1]["facts"]["controls"].append(
                dict(rows[-1]["facts"]["controls"][0], selector="#other-search"))),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_search_scope_026.json")
                mutate(rows)
                self.assert_search(rows, "not_run")

    def test_retained_hash_without_a_fresh_exact_query_is_not_execution(self):
        for name, mutate in (
            ("observe only", lambda rows: rows[-1]["facts"].update(last_action="observe")),
            ("wrong expected query", lambda rows: rows[-1]["facts"]["typed_input_checks"][0].update(expected_sha256="a" * 64)),
            ("wrong actual query", lambda rows: rows[-1]["facts"]["typed_input_checks"][0].update(actual_sha256="a" * 64)),
            ("not retained", lambda rows: rows[-1]["facts"]["typed_input_checks"][0].update(retained=False)),
            ("no checks", lambda rows: rows[-1]["facts"].update(typed_input_checks=[])),
            ("stale retained query", lambda rows: rows[1]["facts"].update(
                typed_input_checks=copy.deepcopy(rows[-1]["facts"]["typed_input_checks"]))),
            ("missing prior checks", lambda rows: rows[1]["facts"].pop("typed_input_checks")),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_search_scope_026.json")
                mutate(rows)
                rows[-1]["text"] += "\n검색 성공: " + SEARCH_QUERY
                self.assert_search(rows, "not_run")

    def test_import_attempt_fixture_and_saved_state_cannot_be_borrowed(self):
        for name, mutate in (
            ("wrong fixture hash", lambda rows: rows[0]["facts"]["import_attempt"].update(fixture_sha256="a" * 64)),
            ("wrong uploaded fixture", lambda rows: rows[0]["facts"].update(uploaded_fixture="peekly-sample-current.zip")),
            ("no import completion", lambda rows: rows[0]["facts"]["import_attempt"].update(phase_samples=[])),
            ("unchanged saved state", lambda rows: rows[0]["facts"]["import_attempt"].update(persistence_unchanged=True)),
            ("other query attempt", lambda rows: rows[-1]["facts"].update(import_attempt_id="upload-unrelated")),
            ("changed saved state", lambda rows: rows[-1]["facts"]["storage_snapshot"].update(sha256="a" * 64)),
            ("unavailable saved state", lambda rows: rows[-1]["facts"]["storage_snapshot"].update(available=False)),
            ("sample mode", lambda rows: rows[1].update(text="샘플을 보고 있어요")),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_search_scope_026.json")
                mutate(rows)
                self.assert_search(rows, "not_run")
        self.assert_search(golden("peekly_search_scope_026.json")[1:], "not_run")

    def test_closed_list_cannot_supply_a_baseline_for_a_later_unrelated_type(self):
        rows = golden("peekly_search_scope_026.json")
        closed = copy.deepcopy(rows[1])
        closed["facts"].update(controls=[], list_rows=[], last_action="click", last_action_label="닫기")
        self.assert_search([*rows[:2], closed, rows[2]], "not_run")

    def test_actual_query_can_fail_order_or_filter_and_later_pass_does_not_erase_it(self):
        for name, mutate in (
            ("unordered baseline", lambda rows: rows[1]["facts"]["list_rows"].reverse()),
            ("wrong account", lambda rows: rows[-1]["facts"].update(list_rows=[{"key": "synthetic_wrong_account"}])),
            ("no match", lambda rows: rows[-1]["facts"].update(list_rows=[])),
            ("not filtered", lambda rows: rows[-1]["facts"].update(
                list_rows=copy.deepcopy(rows[1]["facts"]["list_rows"]))),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_search_scope_026.json")
                mutate(rows)
                self.assert_search(rows, "failed")
                self.assert_search(rows + golden("peekly_search_scope_026.json"), "failed")



class SizeScopeTests(unittest.TestCase):
    def assert_size(self, rows, status):
        self.assertEqual(size_scope_evidence(rows)["status"], status)
        self.assertEqual(statuses(rows, [SIZE_REQUIREMENT]), {0: status})

    def test_actual_015_rejection_triad_passes_without_fabricating_group_sha(self):
        rows = golden("peekly_size_scope_015.json")
        self.assertIsNone(rows[2]["facts"]["import_attempt"]["fixture_sha256"])
        self.assertEqual(size_scope_evidence(rows)["indices"], [0, 1, 2])
        self.assert_size(rows, "passed")
        self.assert_size([rows[0], rows[2], rows[3]], "passed")  # The later 32 MiB attempt is also real.

    def test_frozen_member_provenance_exercises_three_distinct_boundaries(self):
        value = json.loads((FIXTURES / "peekly_size_scope_015.json").read_text())
        provenance = value["fixture_provenance"]
        self.assertEqual(provenance["manifest_sha256"],
                         "4df650d58c2105bc67ca3eec27c826b1f8129f8f1a846b396a4eb9e53c48f44a")
        files = {row["name"]: row for row in provenance["files"]}
        self.assertEqual(files["peekly-oversize-plus-one.zip"]["bytes"], 128 * 1024 ** 2 + 1)
        self.assertEqual(files["loose-file-over-32mib.json"]["bytes"], 32 * 1024 ** 2 + 1)
        group = [files[name] for name in provenance["groups"]["peekly-loose-total-over"]]
        self.assertEqual(sum(row["bytes"] for row in group), 66 * 1024 ** 2)
        self.assertTrue(all(row["bytes"] < 32 * 1024 ** 2 for row in group))

    def test_only_the_two_reviewed_redacted_group_aliases_are_accepted(self):
        rows = golden("peekly_size_scope_015.json")[:3]
        for row in rows[1:]:
            facts = row["facts"]
            facts["uploaded_fixture"] = facts["uploaded_fixture"].replace("[handle]:", "@group:")
            facts["import_attempt"]["fixture"] = facts["uploaded_fixture"]
        self.assert_size(rows, "passed")
        for name in ("[other]:peekly-loose-total-over", "[handle]:unreviewed-total-over"):
            altered = copy.deepcopy(rows)
            altered[2]["facts"]["uploaded_fixture"] = name
            altered[2]["facts"]["import_attempt"]["fixture"] = name
            self.assert_size(altered, "not_run")

    def test_missing_boundary_or_notice_stays_not_run(self):
        baseline = golden("peekly_size_scope_015.json")[:3]
        for missing in range(3):
            with self.subTest(missing=missing):
                self.assert_size([r for i, r in enumerate(baseline) if i != missing], "not_run")
                rows = copy.deepcopy(baseline)
                rows[missing]["text"] = "파일 고르기"
                self.assert_size(rows, "not_run")
        rows = copy.deepcopy(baseline)
        rows[0]["text"] = "ZIP 파일이 너무 커요. 최대 128MB"
        self.assert_size(rows, "not_run")  # A guide/limit mention is not the observed import error.

    def test_unbound_fixture_attempt_or_unavailable_changed_state_cannot_pass(self):
        for name, mutate in (
            ("wrong sha", lambda row: row["facts"]["import_attempt"].update(fixture_sha256="a" * 64)),
            ("other fixture", lambda row: row["facts"].update(uploaded_fixture="peekly-sample-current.zip")),
            ("other attempt", lambda row: row["facts"].update(import_attempt_id="upload-unrelated")),
            ("other tool", lambda row: row["facts"]["import_attempt"].update(tool="upload_cancel")),
            ("stale action", lambda row: row["facts"].update(last_action="observe")),
            ("unavailable before", lambda row: row["facts"]["import_attempt"]["storage_before"].update(available=False)),
            ("no preserved state", lambda row: row["facts"]["import_attempt"].update(persistence_unchanged=False)),
            ("changed after", lambda row: row["facts"]["import_attempt"]["storage_after"].update(sha256="b" * 64)),
            ("changed current", lambda row: row["facts"]["storage_snapshot"].update(sha256="b" * 64)),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_size_scope_015.json")[:3]
                mutate(rows[0])
                self.assert_size(rows, "not_run")
        for remove in (True, False):
            rows = golden("peekly_size_scope_015.json")[:3]
            if remove:
                rows[2]["facts"]["import_attempt"].pop("fixture_sha256")
            else:
                rows[2]["facts"]["import_attempt"]["fixture_sha256"] = "a" * 64
            self.assert_size(rows, "not_run")

    def test_other_attempt_or_accumulated_text_cannot_supply_the_missing_notice(self):
        rows = golden("peekly_size_scope_015.json")[:3]
        unrelated = copy.deepcopy(rows[0])
        unrelated["facts"].update(last_action="observe", uploaded_fixture="peekly-sample-current.zip")
        rows[0]["text"] = "파일을 읽고 있어요"
        self.assert_size([unrelated, *rows], "not_run")
        rows[1]["text"] += "\n" + unrelated["text"]
        self.assert_size(rows, "not_run")

    def test_each_actual_acceptance_has_failure_priority_before_or_after_rejections(self):
        baseline = golden("peekly_size_scope_015.json")[:3]
        for boundary in baseline:
            accepted = RejectionWordingScopeTests.synthetic_acceptance(boundary)
            for rows in ([accepted], [accepted, *baseline], [*baseline, accepted]):
                self.assert_size(rows, "failed")

    def test_bare_completion_copy_or_unsaved_completion_is_not_acceptance(self):
        for boundary in golden("peekly_size_scope_015.json")[:3]:
            bare = copy.deepcopy(boundary)
            bare["text"] = "결과를 불러왔어요."
            self.assert_size([bare], "not_run")
            accepted = RejectionWordingScopeTests.synthetic_acceptance(boundary)
            accepted["facts"]["import_attempt"]["phase_samples"] = []
            self.assert_size([accepted], "not_run")
            accepted = RejectionWordingScopeTests.synthetic_acceptance(boundary)
            accepted["facts"]["import_attempt"]["storage_after"]["available"] = False
            self.assert_size([accepted], "not_run")



class DeleteScopeTests(unittest.TestCase):
    def assert_delete(self, rows, status):
        self.assertEqual(delete_scope_evidence(rows)["status"], status)
        self.assertEqual(statuses(rows, [DELETE_REQUIREMENT]), {0: status})

    @staticmethod
    def confirm_control(rows):
        return next(control for control in rows[-2]["facts"]["controls"]
                    if " ".join(control["label"].split()) == "모두 지우기")

    @staticmethod
    def synthetic_removed_keys():
        rows = golden("peekly_delete_scope_025.json")
        facts = rows[-1]["facts"]
        facts["storage_keys"] = ["peekly_theme_preference"]
        facts["storage_snapshot"] = {"available": True, "keys": [],
                                    "sha256": hashlib.sha256(b"[]").hexdigest()}
        return rows

    def test_actual_025_empty_state_key_recreation_is_not_key_absence(self):
        rows = golden("peekly_delete_scope_025.json")
        self.assertEqual(rows[0]["facts"]["storage_snapshot"], rows[-1]["facts"]["storage_snapshot"])
        self.assertNotEqual(rows[1]["facts"]["storage_snapshot"], rows[-1]["facts"]["storage_snapshot"])
        self.assertIn("peekly_state_v7", rows[-1]["facts"]["storage_keys"])
        self.assertNotIn("peekly_theme_preference", DELETE_REQUIRED_KEYS)
        self.assertEqual(delete_scope_evidence(rows)["indices"], [0, 1, 4, 5])
        self.assert_delete(rows, "failed")

    def test_authored_key_absence_can_pass_desktop_scope_with_theme_preserved(self):
        rows = self.synthetic_removed_keys()
        self.assert_delete(rows, "passed")
        self.assertIn("native iOS", CRITERIA[DELETE_REQUIREMENT]["value"])
        self.assertEqual(CRITERIA[DELETE_REQUIREMENT]["scope"], "desktop-partial+native-ios")
        rows[-1]["facts"]["storage_keys"].append("peekly_onboarding_v1")
        self.assert_delete(rows, "failed")

    def test_visible_final_confirm_dispatch_is_required(self):
        for name, mutate in (
            ("hidden", lambda rows: self.confirm_control(rows).update(visible=False)),
            ("disabled", lambda rows: self.confirm_control(rows).update(disabled=True)),
            ("ambiguous", lambda rows: rows[-2]["facts"]["controls"].append(copy.deepcopy(self.confirm_control(rows)))),
            ("not dispatched", lambda rows: rows[-1]["facts"]["click_dispatch"].update(dispatched=False)),
            ("no hit", lambda rows: rows[-1]["facts"]["click_dispatch"].update(hit_test=False)),
            ("wrong selector", lambda rows: rows[-1]["facts"]["click_dispatch"].update(verified_selector="#unrelated")),
            ("cancel", lambda rows: rows[-1]["facts"].update(last_action_label="취소")),
            ("open only", lambda rows: rows[-1]["facts"].update(last_action_label="기록 모두 지우기")),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_delete_scope_025.json")
                mutate(rows)
                self.assert_delete(rows, "not_run")
        self.assert_delete(golden("peekly_delete_scope_025.json")[:-1], "not_run")

    def test_initial_owned_fixture_and_same_saved_import_scope_are_required(self):
        original_rows = golden("peekly_delete_scope_025.json")
        self.assert_delete(original_rows[1:], "not_run")
        self.assert_delete([original_rows[0], *original_rows[2:]], "not_run")
        for name, mutate in (
            ("wrong fixture", lambda rows: rows[1]["facts"].update(uploaded_fixture="peekly-sample-current.zip")),
            ("wrong sha", lambda rows: rows[1]["facts"]["import_attempt"].update(fixture_sha256="a" * 64)),
            ("different starting state", lambda rows: rows[1]["facts"]["import_attempt"]["storage_before"].update(sha256="a" * 64)),
            ("different confirm attempt", lambda rows: rows[-1]["facts"].update(import_attempt_id="upload-other")),
            ("changed pre-confirm state", lambda rows: rows[-2]["facts"]["storage_snapshot"].update(sha256="a" * 64)),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_delete_scope_025.json")
                mutate(rows)
                self.assert_delete(rows, "not_run")

    def test_unavailable_or_inconsistent_storage_is_not_a_product_verdict(self):
        for name, mutate in (
            ("denied", lambda rows: rows[-1]["facts"].update(storage_access="denied")),
            ("unavailable", lambda rows: rows[-1]["facts"]["storage_snapshot"].update(available=False)),
            ("missing keys", lambda rows: rows[-1]["facts"].pop("storage_keys")),
            ("key disagreement", lambda rows: rows[-1]["facts"]["storage_snapshot"].update(keys=[])),
            ("unavailable before", lambda rows: rows[-2]["facts"]["storage_snapshot"].update(available=False)),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_delete_scope_025.json")
                mutate(rows)
                self.assert_delete(rows, "not_run")

    def test_stale_ack_and_later_import_cannot_supply_delete_evidence(self):
        for name, mutate in (
            ("observe only", lambda rows: rows[-1]["facts"].update(last_action="observe")),
            ("no current ack", lambda rows: rows[-1].update(text="내 팔로우 관계를 한눈에 확인해요")),
            ("stale prior ack", lambda rows: rows[-2].update(text=rows[-2]["text"] + "\n" + rows[-1]["text"])),
            ("later import", lambda rows: rows[-1]["facts"].update(last_action="upload", uploaded_fixture=SEARCH_FIXTURE)),
        ):
            with self.subTest(case=name):
                rows = golden("peekly_delete_scope_025.json")
                mutate(rows)
                self.assert_delete(rows, "not_run")


if __name__ == "__main__":
    unittest.main()
