"""Bounded legacy fixture/host checks; no browser or model is started."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import _paths
from uxpersonas.scale_browser_host import (
    ScaleBrowserHost, _authorize_legacy_seed, _preserve_driver_hashes,
)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_peekly_coverage_fixtures import (
    FixtureBuildError, LEGACY_SEED, LEGACY_SNAPSHOT_ID, legacy_seed_state,
    _validated_legacy_seed,
)


class LegacyFixtureTests(unittest.TestCase):
    def test_seed_is_nonempty_legacy_without_provenance_not_known_empty(self):
        state = legacy_seed_state("peekly_fixture_owner")
        row, = state["snapshots"]
        self.assertEqual(row["id"], LEGACY_SNAPSHOT_ID)
        self.assertNotIn("includedFiles", row)
        self.assertNotIn("listCompleteness", row)
        self.assertTrue(row["followers"])
        self.assertTrue(row["following"])
        self.assertFalse(row["isSample"])
        self.assertEqual(state["activeSnapshotId"], row["id"])
        self.assertEqual(state["comparisonSnapshotId"], row["id"])
        self.assertLess(len(json.dumps(state).encode()), 65536)
        with self.assertRaises(FixtureBuildError):
            legacy_seed_state("not a synthetic handle")

    def test_product_validation_failure_never_publishes_attestation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = type("Result", (), {"returncode": 1, "stdout": "", "stderr": "assertion"})()
            with patch("build_peekly_coverage_fixtures.subprocess.run", return_value=result):
                with self.assertRaisesRegex(FixtureBuildError, "legacy_product_validation_failed"):
                    _validated_legacy_seed(root, "peekly_fixture_owner", root, "node")
            self.assertTrue((root / LEGACY_SEED).is_file())
            self.assertFalse((root / "fixture-manifest.json").exists())
            # No output path is silently reused after any failure.
            with self.assertRaises(FileExistsError):
                _validated_legacy_seed(root, "peekly_fixture_owner", root, "node")

    def test_unreviewed_state_write_and_unrelated_tasks_are_rejected(self):
        task = {"requirement_ids": ["PRD-IMPORT-SNAPSHOT-UNKNOWN"]}
        args = {"file": LEGACY_SEED}
        _authorize_legacy_seed(task, args, set(), False)
        for changed in (
            ({}, args, set(), False),
            ({"requirement_ids": "PRD-IMPORT-SNAPSHOT-UNKNOWN"}, args, set(), False),
            (task, {"file": "another.json"}, set(), False),
            (task, {**args, "storage_key": "user-data"}, set(), False),
            (task, args, {"peekly-sample-current.zip"}, False),
            (task, args, set(), True),
        ):
            with self.subTest(changed=changed), self.assertRaises(RuntimeError):
                _authorize_legacy_seed(*changed)

    def test_only_typed_seed_and_readback_hashes_survive_scrubbing(self):
        sha = "1234567890123456" * 4
        original = {"legacy_seed": {"fixture_sha256": sha, "product_loader_sha256": sha,
            "product_validation_sha256": sha, "product_commit": "1234567890" * 4,
            "storage_before": {"sha256": sha}, "storage_after": {"sha256": sha}},
            "legacy_state": {"schema_version": "peekly-legacy-state.v1",
                "storage_sha256": sha, "snapshots": [{"id": LEGACY_SNAPSHOT_ID, "account_sha256": sha}]}}
        cleaned = json.loads(json.dumps(original).replace(sha, "[redacted]").replace("1234567890" * 4, "[redacted]"))
        _preserve_driver_hashes(original, cleaned)
        self.assertEqual(cleaned, original)
        original["legacy_state"]["snapshots"][0]["account_sha256"] = "private handle"
        cleaned["legacy_state"]["snapshots"][0]["account_sha256"] = "[redacted]"
        _preserve_driver_hashes(original, cleaned)
        self.assertEqual(cleaned["legacy_state"]["snapshots"][0]["account_sha256"], "[redacted]")


class LegacyHostTests(unittest.IsolatedAsyncioTestCase):
    async def test_lost_seed_response_is_never_retransmitted(self):
        with tempfile.TemporaryDirectory() as directory:
            host = object.__new__(ScaleBrowserHost)
            host.processes = {"owned": object()}
            host._exchange = AsyncMock(side_effect=RuntimeError("browser_transport_closed"))
            request = {"context_id": "owned", "operation_id": "seed-attempt",
                "request_sha256": "a" * 64, "payload": {
                    "name": "seed_legacy_unknown", "arguments": {"file": LEGACY_SEED},
                    "task": {"requirement_ids": ["PRD-IMPORT-SNAPSHOT-UNKNOWN"]},
                    "evidence_path": str(Path(directory).resolve())}}
            with self.assertRaisesRegex(RuntimeError, "browser_transport_closed"):
                await host.call("tool", request)
            with self.assertRaisesRegex(RuntimeError, "legacy_seed_already_attempted"):
                await host.call("tool", request)
            self.assertEqual(host._exchange.await_count, 1)
            self.assertEqual(host.context_uploads["owned"], set())

    async def test_seed_authorization_is_checked_before_browser_start(self):
        with tempfile.TemporaryDirectory() as directory:
            host = object.__new__(ScaleBrowserHost)
            host.processes = {}
            host._exchange = AsyncMock()
            request = {"context_id": "not-owned", "payload": {
                "name": "seed_legacy_unknown", "arguments": {"file": LEGACY_SEED},
                "task": {"requirement_ids": ["PRD-IMPORT-VALID"]},
                "evidence_path": str(Path(directory).resolve())}}
            with self.assertRaisesRegex(RuntimeError, "legacy_seed_task_not_authorized"):
                await host.call("tool", request)
            host._exchange.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
