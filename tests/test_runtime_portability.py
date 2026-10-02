"""A relocated CLI must load its own helpers and reject unsupported interpreters."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import _paths


class RuntimePortabilityTests(unittest.TestCase):
    def test_unrelated_scripts_package_cannot_shadow_bundled_validator(self):
        with tempfile.TemporaryDirectory() as directory:
            other = Path(directory) / "scripts"
            other.mkdir()
            (other / "__init__.py").write_text("raise RuntimeError('unrelated scripts loaded')\n")
            environment = {**os.environ, "PYTHONPATH": directory, "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(
                [sys.executable, str(_paths.SKILL / "scripts/ux_loop.py"), "--help"],
                cwd=directory, env=environment, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("usage:", result.stdout)

    def test_every_main_cli_rejects_old_python_before_engine_import(self):
        probe = (
            "import runpy,sys; path=sys.argv[1]; "
            "sys.argv=[path,'--help']; sys.version_info=(3,9,6); "
            "runpy.run_path(path,run_name='__main__')"
        )
        for script in ("ux_research.py", "ux_loop.py", "ergo_qa.py"):
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, "-c", probe, str(_paths.SKILL / "scripts" / script)],
                    capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Python 3.10 or newer is required", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
