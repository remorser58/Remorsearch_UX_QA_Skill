"""Offline regressions for actual 017/021 evidence and authored scope positives.

Golden JSON is a minimal, hash-referenced projection of saved observations.
Positive cases and PNGs below are explicitly synthetic contract inputs; no
browser/model process or product success is asserted by these tests.
"""
import copy
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
    evaluate, result_scope_evidence,
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


if __name__ == "__main__":
    unittest.main()
