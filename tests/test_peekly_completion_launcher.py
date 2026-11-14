"""Offline admission and smoke regression; no provider or browser dispatch."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa"))
import run_peekly_completion as completion
from uxpersonas.swarm_queue import Queue, checkpoint_data
from uxresearch.canonical import EngineError
from test_swarm_queue import plan
from test_peekly_coverage_launcher import evidence, clean_ledger


def completion_evidence(statuses=("passed",) * 6):
    summary, report = evidence(statuses)
    summary["persona_ids"] = list(completion.SMOKE_IDS)
    for value in (summary["completed_receipt_summary"], report["completed_receipt_summary"]):
        value["persona_ids"] = list(completion.SMOKE_IDS)
    for row, pid in zip(report["tasks"], completion.SMOKE_IDS):
        row["persona_id"] = pid
        for criterion in row["result"]["receipt"]["criteria"]:
            criterion["evidence_ids"] = ["log-actual"]
    return summary, report


def gate(statuses=("passed",) * 6):
    summary, report = completion_evidence(statuses)
    return completion.smoke_gate(summary, report, completion.base.router_delivery_audit(clean_ledger()))


class CompletionGateTests(unittest.TestCase):
    def test_both_targeted_flows_and_all_six_executed(self):
        result = gate()
        self.assertTrue(result["pass_gate"])
        self.assertEqual(result["baseline_success_not_run"], 3)
        self.assertTrue(all(row["executed"] for row in result["targeted_flows"]))

    def test_one_remaining_target_blocks_even_if_aggregate_decreases(self):
        result = gate(("passed", "passed", "not_run", "passed", "passed", "passed"))
        self.assertFalse(result["pass_gate"])
        self.assertIn("target_not_exercised:PRD-IMPORT-SNAPSHOT-UNKNOWN", result["reasons"])

    def test_prior_smoke_personas_cannot_substitute_for_fresh_pair(self):
        for numbers in (("021", "029"), ("023", "030"), ("024", "032")):
            with self.subTest(prior=numbers):
                summary, report = completion_evidence()
                prior = ["PER-PEEKLY-V2-" + number for number in numbers]
                summary["persona_ids"] = prior
                for value in (summary["completed_receipt_summary"], report["completed_receipt_summary"]):
                    value["persona_ids"] = prior
                for row, pid in zip(report["tasks"], prior):
                    row["persona_id"] = pid
                result = completion.smoke_gate(summary, report,
                    completion.base.router_delivery_audit(clean_ledger()))
                self.assertFalse(result["pass_gate"])
                self.assertTrue(all(not row["executed"] for row in result["targeted_flows"]))

    def test_non_target_not_run_also_blocks(self):
        self.assertFalse(gate(("not_run", "passed", "passed", "passed", "passed", "passed"))["pass_gate"])

    def test_actual_product_failure_is_executed_but_na_is_not(self):
        self.assertTrue(gate(("passed", "passed", "failed", "passed", "passed", "failed"))["pass_gate"])
        self.assertFalse(gate(("passed", "passed", "not_applicable", "passed", "passed", "passed"))["pass_gate"])

    def test_missing_target_evidence_and_uncertainty_fail_closed(self):
        summary, report = completion_evidence()
        report["tasks"][0]["result"]["receipt"]["criteria"][2]["evidence_ids"] = []
        audit = completion.base.router_delivery_audit(clean_ledger())
        self.assertFalse(completion.smoke_gate(summary, report, audit)["pass_gate"])
        summary, report = completion_evidence()
        ledger = clean_ledger()
        ledger["call_delivery"]["call-a"] = "uncertain"
        self.assertFalse(completion.smoke_gate(summary, report,
                         completion.base.router_delivery_audit(ledger))["pass_gate"])

    def test_catalog_binds_actual_validation_and_fixture_hashes(self):
        validation = dict(product_commit=completion.PRODUCT_COMMIT, fixture_sha256=completion.SEED_SHA,
                          checks={key: True for key in completion.VALIDATION_CHECKS})
        raw = (json.dumps(validation, ensure_ascii=False, sort_keys=True, separators=(",", ":"))+"\n").encode()
        attestation = hashlib.sha256(raw).hexdigest()
        seed = dict(schema_version="peekly-legacy-seed-fixture.v1", storage_key="peekly_state_v6",
                    fixture_sha256=completion.SEED_SHA, product_commit=completion.PRODUCT_COMMIT,
                    product_validation_sha256=attestation, product_validation=validation)
        manifest = dict(coverage=dict(legacy_seed=seed))
        with mock.patch.object(completion, "VALIDATION_SHA", attestation):
            completion.validate_seed_catalog(manifest, dict(completion.PINNED_FILES))
            changed = copy.deepcopy(manifest)
            changed["coverage"]["legacy_seed"]["product_validation"]["checks"]["known_empty_is_known"] = False
            with self.assertRaises(RuntimeError):
                completion.validate_seed_catalog(changed, dict(completion.PINNED_FILES))
            changed_files = dict(completion.PINNED_FILES, **{"peekly-sample-previous.zip": "0" * 64})
            with self.assertRaises(RuntimeError):
                completion.validate_seed_catalog(manifest, changed_files)


class CheckpointBudgetTests(unittest.TestCase):
    def test_eighty_observations_and_queue_plan_are_admitted(self):
        state = {"observations": [{"text": str(i), "facts": {}, "checks": {}} for i in range(80)]}
        self.assertEqual(len(checkpoint_data(state, 80)["observations"]), 80)
        with tempfile.TemporaryDirectory() as directory:
            queue = Queue.create(Path(directory) / "queue", plan(count=1, turns=80))
            self.assertEqual(queue.plan["limits"]["turns"], 80)

    def test_eighty_one_turns_or_observations_are_rejected(self):
        with self.assertRaises(EngineError):
            checkpoint_data({"observations": []}, 81)
        with self.assertRaises(EngineError):
            checkpoint_data({"observations": [{}] * 81}, 80)
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(EngineError):
                Queue.create(Path(directory) / "queue", plan(count=1, turns=81))

    def test_existing_content_and_metadata_caps_are_not_raised(self):
        with self.assertRaises(EngineError):
            checkpoint_data({"observations": [{"text": "x" * 65536, "facts": {}, "checks": {}}]}, 80)
        with self.assertRaises(EngineError):
            checkpoint_data({"observations": [], "metadata": "x" * (1024 * 1024)}, 80)
        with self.assertRaises(EngineError):
            checkpoint_data({"observations": [{}] * 65}, 64)


if __name__ == "__main__":
    unittest.main()
