"""Owned binary/worker admission tests; no product or real browser observations."""
import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa"))
from uxpersonas import browser_run, local_run, workspace
from uxresearch.canonical import EngineError, byte_digest, canonical
from uxresearch.storage import atomic

_spec = importlib.util.spec_from_file_location(
    "owned_input_fixture", ROOT / "skills/remorsearch-ux-qa/examples/journey/browser_fixture.py")
fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fixture)


class OwnedBrowserInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.__dict__.update(fixture.build(self.root / "case"))
        (self.source / "inputs").mkdir()
        atomic(self.source / "inputs/previous.zip", b"PK-owned-synthetic")
        atomic(self.source / "parse.js", b"onmessage = () => postMessage('owned');")
        self.adapter["uploads"] = [dict(id="previous", path="inputs/previous.zip",
                                       name="previous.zip", mime_type="application/zip")]
        self.adapter["workers"] = ["parse.js"]
        self.files = fixture.FILES + ["inputs/previous.zip", "parse.js"]

    def freeze(self):
        atomic(self.source / "browser-adapter.json", canonical(self.adapter))
        workspace.prepare(self.source, self.work, reviewed_files=self.files)
        return browser_run.manifest(workspace._state(self.work), self.plan)

    def test_exact_binary_and_worker_inputs_are_frozen_separately(self):
        result = self.freeze()
        self.assertNotIn("inputs/previous.zip", result["files"])
        self.assertEqual(result["workers"], {"parse.js": byte_digest((self.source / "parse.js").read_bytes())})
        self.assertEqual(result["uploads"], [dict(
            **self.adapter["uploads"][0], sha256=byte_digest(b"PK-owned-synthetic"), size_bytes=18)])

    def test_undeclared_and_duplicate_uploads_are_refused(self):
        self.adapter["uploads"].append(copy.deepcopy(self.adapter["uploads"][0]))
        with self.assertRaises(EngineError) as caught:
            self.freeze()
        self.assertEqual(caught.exception.issue["code"], "browser_uploads")

    def test_worker_must_be_an_exact_reviewed_javascript_asset(self):
        self.adapter["workers"] = ["index.html"]
        with self.assertRaises(EngineError) as caught:
            self.freeze()
        self.assertEqual(caught.exception.issue["code"], "browser_workers")

    def test_policy_and_launcher_are_frozen_not_just_executable_hash(self):
        config = {"node": "/owned/node", "isolation": {
            "policy": browser_run.WORKER_POLICY, "launcher": browser_run.SANDBOX,
            "profile": browser_run.NETWORK_PROFILE,
            "profile_sha256": byte_digest(browser_run.NETWORK_PROFILE.encode())}}
        command = browser_run.command(config, "--validate")
        self.assertEqual(command, [browser_run.SANDBOX, "-p", browser_run.NETWORK_PROFILE,
                                  "/owned/node", str(browser_run.BRIDGE), "--validate"])
        config["isolation"]["profile"] = "(version 1)(allow default)"
        with self.assertRaises(EngineError):
            browser_run.command(config)


if __name__ == "__main__":
    unittest.main()

