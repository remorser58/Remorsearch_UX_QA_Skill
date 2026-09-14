import json
import unittest
from pathlib import Path

from scripts.validate_bundle import validate_bundle


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ValidateBundleTests(unittest.TestCase):
    def test_valid_bundle_passes(self):
        self.assertEqual(validate_bundle(load_fixture("valid-bundle.json")), [])

    def test_broken_reference_is_rejected(self):
        errors = validate_bundle(load_fixture("invalid-broken-ref.json"))
        self.assertTrue(any("unknown record" in error for error in errors))

    def test_synthetic_persona_cannot_support_real_user_preference(self):
        errors = validate_bundle(load_fixture("invalid-synthetic-claim.json"))
        self.assertTrue(any("synthetic persona" in error for error in errors))

    def test_verified_finding_requires_observation(self):
        errors = validate_bundle(load_fixture("invalid-verified-no-observation.json"))
        self.assertTrue(any("without an observation" in error for error in errors))

    def test_missing_id_is_rejected(self):
        errors = validate_bundle(load_fixture("invalid-missing-id.json"))
        self.assertTrue(any("id is required" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
