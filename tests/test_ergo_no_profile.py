"""Device-only runs can reuse recorded evidence for matching profile analysis."""

from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from _paths import SKILL  # noqa: F401 (makes the skill importable)
from ergoqa import analyze, cli
from ergoqa.profiles import sample_profiles
from test_ergo_pipeline import make_run


class NoProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run_dir = make_run(self.root)
        self.run_path = self.run_dir / "run.json"
        self.run = json.loads(self.run_path.read_text(encoding="utf-8"))
        self.run["profile_id"] = "no-profile"
        self.run_path.write_text(json.dumps(self.run), encoding="utf-8")
        self.profiles = sample_profiles(3, 7, ["galaxy-s24"])
        self.other_device = copy.deepcopy(self.profiles[0])
        self.other_device["profile_id"] = "EP-other-device"
        self.other_device["attributes"]["device_id"] = "iphone-15"
        self.other_orientation = copy.deepcopy(self.profiles[0])
        self.other_orientation["profile_id"] = "EP-other-orientation"
        self.other_orientation["attributes"]["orientation"] = "landscape"

    def test_cross_profile_uses_recorded_device_and_orientation(self) -> None:
        original = self.run_path.read_bytes()
        result = analyze.analyze_run(
            self.run_dir, [self.other_device, *self.profiles, self.other_orientation],
            cross_profile=True, gaze_enabled=False,
        )
        self.assertEqual(result["profiles_evaluated"], [p["profile_id"] for p in self.profiles])
        self.assertEqual(result["device_id"], "galaxy-s24")
        self.assertEqual(result["orientation"], "portrait")
        self.assertTrue(result["observations"])
        self.assertEqual(self.run_path.read_bytes(), original)

    def test_operator_judgment_is_not_assigned_to_a_profile(self) -> None:
        result = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)
        self.assertFalse(any(o["check_id"] == "PJ-01" for o in result["observations"]))
        self.assertFalse(any(key.startswith("PJ-01||") for key in result["coverage"]))

    def test_without_cross_profile_names_the_fix(self) -> None:
        with self.assertRaisesRegex(ValueError, r"recorded with --device.*add --cross-profile.*--profiles.*--profile"):
            analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False)

    def test_no_matching_device_names_the_recorded_device_and_fix(self) -> None:
        with self.assertRaisesRegex(ValueError, r"no supplied profiles match.*galaxy-s24.*portrait.*--profiles.*--cross-profile"):
            analyze.analyze_run(self.run_dir, [self.other_device], cross_profile=True, gaze_enabled=False)

    def test_no_matching_orientation_and_empty_profiles_fail_clearly(self) -> None:
        for profiles in ([self.other_orientation], []):
            with self.subTest(profiles=profiles):
                with self.assertRaisesRegex(ValueError, r"no supplied profiles match.*orientation 'portrait'"):
                    analyze.analyze_run(self.run_dir, profiles, cross_profile=True, gaze_enabled=False)

    def test_detector_results_match_the_existing_profile_path(self) -> None:
        device_only = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)
        self.run["profile_id"] = self.profiles[0]["profile_id"]
        self.run_path.write_text(json.dumps(self.run), encoding="utf-8")
        named = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)

        def detector_observations(result):
            return [{k: v for k, v in o.items() if k != "id"}
                    for o in result["observations"] if o["check_id"] != "PJ-01"]

        self.assertEqual(detector_observations(device_only), detector_observations(named))
        self.assertEqual(device_only["health"], named["health"])
        self.assertEqual(device_only["profiles_evaluated"], named["profiles_evaluated"])

    def test_missing_named_profile_still_fails(self) -> None:
        self.run["profile_id"] = "EP-missing"
        self.run_path.write_text(json.dumps(self.run), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "profile 'EP-missing'.*not supplied"):
            analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)

    def test_cli_round_trip_without_copying_or_rewriting_the_run(self) -> None:
        profiles_path = self.root / "profiles.json"
        profiles_path.write_text(json.dumps({"profiles": self.profiles}), encoding="utf-8")
        output = self.root / "analysis.json"
        args = ["analyze", "--runs", str(self.run_dir), "--profiles", str(profiles_path), "--no-gaze", "--out", str(output)]
        original = self.run_path.read_bytes()
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(cli.main(args), cli.EXIT_USAGE)
        self.assertIn("add --cross-profile", stderr.getvalue())
        self.assertFalse(output.exists())
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(cli.main([*args, "--cross-profile"]), cli.EXIT_OK)
        result = json.loads(output.read_text(encoding="utf-8"))["analyses"][0]
        self.assertEqual(result["profiles_evaluated"], [p["profile_id"] for p in self.profiles])
        self.assertEqual(self.run_path.read_bytes(), original)
        self.assertEqual([p.name for p in self.root.iterdir() if p.is_dir()], ["R-1"])


if __name__ == "__main__":
    unittest.main()
