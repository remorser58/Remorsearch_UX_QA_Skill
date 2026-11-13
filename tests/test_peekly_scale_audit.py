"""Offline audit tests; no provider or browser is invoked."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("peekly_audit", Path(__file__).resolve().parents[1] / "scripts/audit_peekly_scale.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ScaleAuditTests(unittest.TestCase):
    def test_closed_failed_job_is_not_operational_success(self):
        rows = [{"status": "complete", "current_valid": True,
                 "current_ux_outcome": "inconclusive",
                 "result": {"operational_completed": False, "problem": "turn_limit"}}]
        result = audit.completion_counts(rows)
        self.assertEqual(result["queue_closed_complete"], 1)
        self.assertEqual(result["operational_completed"], 0)
        self.assertEqual(result["current_valid_evidence_sessions"], 1)
        self.assertEqual(result["ux_outcomes"], {"inconclusive": 1})

    def test_quality_rejection_does_not_double_count_tokens(self):
        event = {"provider": "TOKENMAXX", "requested_model": audit.MODEL,
                 "served_model": "deepseek-v4.1-flash", "response_id": "response",
                 "input_tokens": 20, "output_tokens": 7, "status": "success"}
        result = audit.usage_summary({"routes": {audit.MODEL: {"attempts": 1,
            "input_tokens": 20, "output_tokens": 7}},
            "events": [event, {**event, "status": "quality_rejected"}]})
        self.assertEqual(result["known_input_tokens"], 20)
        self.assertEqual(result["known_output_tokens"], 7)
        self.assertEqual(result["failure_rate"], 1)
        self.assertEqual(result["cost"]["missing_provider_cost_responses"], 1)
        self.assertIsNone(result["attempt_receipts"][0]["provider_reported_cost"])
        self.assertTrue(result["usage_complete"])

    def test_unfinished_attempts_make_usage_incomplete(self):
        result = audit.usage_summary({"routes": {"r": {"attempts": 1, "input_tokens": 0, "output_tokens": 0}}, "events": []})
        self.assertFalse(result["usage_complete"])
        self.assertTrue(result["discrepancies"])

    def test_capture_tampering_and_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            raw = b"\x89PNG\r\n\x1a\nfixture"
            path = root / "capture.png"
            path.write_bytes(raw)
            descriptor = {"path": path.name, "kind": "screenshot",
                "sha256": hashlib.sha256(raw).hexdigest()}
            self.assertEqual(audit.artifact_bytes(root, descriptor), raw)
            path.write_bytes(raw + b"tampered")
            with self.assertRaisesRegex(ValueError, "digest_mismatch"):
                audit.artifact_bytes(root, descriptor)
            with self.assertRaisesRegex(ValueError, "unsafe_artifact_path"):
                audit.artifact_bytes(root, {**descriptor, "path": "../capture.png"})

    def test_labels_normalize_real_and_escaped_whitespace(self):
        self.assertEqual(audit.normalized("이미\xa0받은\n자료"), "이미 받은 자료")
        self.assertEqual(audit.normalized(r"이미\xa0받은\n자료"), "이미 받은 자료")


if __name__ == "__main__":
    unittest.main()
