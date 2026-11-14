"""Archived source and actual HTTP bytes, using only authored local fixtures."""
import asyncio
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa"))
import run_peekly_completion as completion


def pin(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def authored_target():
    data = {"index.html": b'<script type="module" src="/assets/main.js"></script>'
             b'<link rel="modulepreload" href="/assets/vendor.js">'
             b'<link rel="stylesheet" href="/assets/style.css">',
            "assets/main.js": b"import './vendor.js';", "assets/vendor.js": b"export const x=1;",
            "assets/style.css": b"body{color:black}"}
    return dict(target_url=completion.TARGET_URL, build_sha256="b" * 64,
                source_commit=completion.PRODUCT_COMMIT, source_tree_sha256="c" * 64,
                files={name: pin(raw) for name, raw in data.items()},
                entry_assets=sorted(name for name in data if name != "index.html")), data


class TargetFreezeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source, self.dist = self.root / "source", self.root / "source/dist"
        self.target, self.data = authored_target()
        rows = []
        for name, raw in (("docs/PRD.md", b"Original requirements"), ("src/App.tsx", b"Product source")):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            rows.append(dict(path=name, mode="100644", **pin(raw),
                             git_blob=hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()))
        (self.source / "tsconfig.tsbuildinfo").write_bytes(b"build metadata")
        tree_sha = completion.base.digest_value(rows)
        source_manifest = dict(schema_version="peekly-pinned-source.v1",
            source_commit=completion.PRODUCT_COMMIT, source_root=str(self.source),
            source_tree_sha256=tree_sha, file_count=len(rows), files=rows)
        source_row = self.write_json("source-manifest.json", source_manifest)
        provenance = dict(source_commit=completion.PRODUCT_COMMIT,
            prd_sha256=completion.base.digest_file(self.source / "docs/PRD.md"),
            historical_index_reproduced=True,
            expected_historical_index_sha256=pin(self.data["index.html"])["sha256"])
        provenance_row = self.write_json("build-provenance.json", provenance)
        for name, raw in self.data.items():
            path = self.dist / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        manifest = dict(source_commit=completion.PRODUCT_COMMIT, target_url=completion.TARGET_URL,
            source_root=str(self.source), dist_root=str(self.dist), artifact="source/dist/index.html",
            source_manifest=source_row, provenance=provenance_row,
            sha256=pin(self.data["index.html"])["sha256"],
            assets=[dict(path=name, **pin(raw)) for name, raw in self.data.items()],
            main_asset=dict(path="assets/main.js", **pin(self.data["assets/main.js"])))
        build_row = self.write_json("build-manifest.json", manifest)
        for key, value in dict(TARGET_ROOT=self.root, SOURCE=self.source, DIST=self.dist,
                BUILD=self.root / "build-manifest.json", BUILD_SHA256=build_row["sha256"],
                SOURCE_MANIFEST_SHA256=source_row["sha256"], BUILD_PROVENANCE_SHA256=provenance_row["sha256"],
                SOURCE_TREE_SHA256=tree_sha, SOURCE_FILE_COUNT=len(rows),
                HISTORICAL_INDEX_SHA256=manifest["sha256"]).items():
            patcher = mock.patch.object(completion, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_json(self, name, value):
        raw = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
        (self.root / name).write_bytes(raw)
        return dict(path=name, **pin(raw))

    def test_archive_proof_is_local_and_preserves_historical_asset_uncertainty(self):
        with mock.patch("subprocess.run", side_effect=AssertionError("Never ask parent Git for archive HEAD")), \
                mock.patch.object(completion, "fetch_target_bytes", side_effect=AssertionError("Offline freeze")):
            frozen = completion.capture_target_freeze()
        self.assertEqual(frozen["source_file_count"], 2)
        self.assertEqual(frozen["entry_assets"], self.target["entry_assets"])
        self.assertEqual(set(frozen["generated_build_metadata"]), {"tsconfig.tsbuildinfo"})
        self.assertTrue(frozen["historical_comparison"]["index_bytes_match"])
        self.assertFalse(frozen["historical_comparison"]["historical_main_asset_hash_available"])
        self.assertEqual(frozen["historical_comparison"]["full_historical_dist_byte_identity"], "not_established")

    def test_stale_manifest_cannot_hide_source_or_dist_drift(self):
        for name in ("src/App.tsx", "dist/assets/main.js"):
            path = self.source / name
            before = path.read_bytes()
            path.write_bytes(b"changed" + before)
            with self.assertRaisesRegex(RuntimeError, "target_file_digest_mismatch"):
                completion.capture_target_freeze()
            path.write_bytes(before)
        completion.capture_target_freeze()

    def test_untracked_source_changed_manifest_and_symlink_are_rejected(self):
        extra = self.source / "unrecorded-source.js"
        extra.write_bytes(b"unexpected source")
        with self.assertRaisesRegex(RuntimeError, "target_source_tree_changed"):
            completion.capture_target_freeze()
        extra.unlink()
        path = self.source / "src/App.tsx"
        raw = path.read_bytes()
        path.unlink()
        other = self.root / "outside.tsx"
        other.write_bytes(raw)
        path.symlink_to(other)
        with self.assertRaisesRegex(RuntimeError, "missing_or_symlink"):
            completion.capture_target_freeze()
        path.unlink()
        path.write_bytes(raw)
        with (self.root / "build-manifest.json").open("a") as stream:
            stream.write(" ")
        with self.assertRaisesRegex(RuntimeError, "build_artifact_missing_or_changed"):
            completion.capture_target_freeze()


class ServedTargetTests(unittest.TestCase):
    def setUp(self):
        self.target, self.data = authored_target()
        self.urls = []

    def fetch(self, url, maximum):
        self.urls.append(url)
        name = url.removeprefix(completion.TARGET_URL) or "index.html"
        return self.data[name]

    def test_actual_index_and_every_referenced_entry_asset_are_hashed(self):
        receipt = completion.verify_served_target(self.target, "before", fetch=self.fetch)
        self.assertEqual(len(self.urls), 4)
        self.assertTrue(all(url.startswith("http://127.0.0.1:4175/") for url in self.urls))
        self.assertEqual(receipt["files"], self.target["files"])

    def test_changed_served_main_is_rejected_even_with_identical_index_and_manifest(self):
        before_index = self.data["index.html"]
        self.data["assets/main.js"] = b"different executable"
        with self.assertRaisesRegex(RuntimeError, "served_target_digest_mismatch:assets/main.js"):
            completion.verify_served_target(self.target, "after", fetch=self.fetch)
        self.assertEqual(self.data["index.html"], before_index)

    def test_index_mutation_missing_bytes_and_unowned_asset_are_rejected(self):
        original = self.data["index.html"]
        self.data["index.html"] += b"<!-- changed -->"
        with self.assertRaisesRegex(RuntimeError, "served_target_digest_mismatch:index.html"):
            completion.verify_served_target(self.target, "before", fetch=self.fetch)
        self.data["index.html"] = original
        for path in ("https://example.invalid/main.js", "//example.invalid/main.js",
                     "/../assets/main.js", "/%61ssets/main.js", "/assets/main.js?bypass=1"):
            with self.subTest(path=path), self.assertRaisesRegex(RuntimeError, "outside_pin"):
                completion.entry_assets(('<script type="module" src="' + path + '"></script>').encode(),
                                        self.target["files"])

    def test_wrong_origin_redirects_and_http_size_are_not_silently_accepted(self):
        with mock.patch.object(completion, "build_opener") as opener:
            with self.assertRaisesRegex(RuntimeError, "origin_not_owned"):
                completion.fetch_target_bytes("http://127.0.0.1:4174/", 20)
            opener.assert_not_called()
        with self.assertRaisesRegex(RuntimeError, "redirect_rejected"):
            completion.NoTargetRedirect().redirect_request(None, None, 302, "redirect", {},
                                                          "http://127.0.0.1:4174/")
        response = mock.MagicMock()
        response.status, response.geturl.return_value = 200, completion.TARGET_URL
        response.read.return_value = b"123456"
        response.__enter__.return_value = response
        opener = mock.Mock()
        opener.open.return_value = response
        with mock.patch.object(completion, "build_opener", return_value=opener):
            with self.assertRaisesRegex(RuntimeError, "size_limit"):
                completion.fetch_target_bytes(completion.TARGET_URL, 5)

    def test_both_ordered_receipts_must_match_the_frozen_target(self):
        provenance = dict(target_url=completion.TARGET_URL, freeze=dict(product_target=self.target),
            target_before=completion.verify_served_target(self.target, "before", fetch=self.fetch))
        status = dict(target_after=completion.verify_served_target(self.target, "after", fetch=self.fetch))
        completion.require_target_receipts(provenance, status)
        for change in ("missing", "asset", "order"):
            value = copy.deepcopy(status)
            if change == "missing":
                value.clear()
            elif change == "asset":
                value["target_after"]["files"]["assets/main.js"]["sha256"] = "0" * 64
            else:
                value["target_after"]["checked_at"] = "2000-01-01T00:00:00+00:00"
            with self.subTest(change=change), self.assertRaisesRegex(RuntimeError, "served_target_receipt"):
                completion.require_target_receipts(provenance, value)


class CompletionConfigurationTests(unittest.TestCase):
    def run_authored_stage(self, *, mutate_served_asset=False):
        from test_peekly_completion_launcher import completion_evidence
        from test_peekly_coverage_launcher import clean_ledger
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "fresh"
        target, data = authored_target()
        target.update(build_sha256=completion.BUILD_SHA256, source_file_count=319)
        freeze = dict(product_target=target, library_sha256=completion.LIBRARY_SHA256)
        library = mock.MagicMock()
        library.__enter__.return_value = library
        library.list.return_value = dict(personas=[dict(persona_id=pid, revision=1, reusable=True)
                                                   for pid in completion.base.ALL_IDS])
        seen = []
        async def stage(arguments, ids, count):
            self.assertEqual((arguments.url, arguments.library, arguments.build_artifact),
                             (completion.TARGET_URL, completion.LIBRARY, completion.BUILD))
            self.assertIn("loopback port 4175", arguments.target)
            self.assertIn("loopback port 4175", arguments.goal)
            seen.append((ids, count))
            folder = root / "stage-2"
            folder.mkdir()
            summary, report = completion_evidence()
            for name, value in (("report.json", report), ("stage-summary.json", summary),
                                ("model-router-ledger.json", clean_ledger())):
                completion.base.write_json(folder / name, value)
            if mutate_served_asset:
                data["assets/main.js"] = b"server changed during run"
            return summary
        live = SimpleNamespace(Library=lambda _: library, run_stage=stage,
            scale_job_id=lambda product, pid, revision, goal, build: "fresh-" + pid,
            NODE_DEFAULT="/authored/node", CHROME_DEFAULT="/authored/chrome")
        fetch = lambda url, maximum: data[url.removeprefix(completion.TARGET_URL) or "index.html"]
        patches = (
            mock.patch.object(completion.base, "owned_output", return_value=root),
            mock.patch.object(completion.base, "load_live", return_value=live),
            mock.patch.object(completion.base, "snapshot_prior_queues", return_value=[]),
            mock.patch.object(completion.base, "prior_queue_integrity", return_value=dict(prior_queues_unchanged=True)),
            mock.patch.object(completion, "capture_freeze", side_effect=lambda: copy.deepcopy(freeze)),
            mock.patch.object(completion, "fetch_target_bytes", side_effect=fetch),
        )
        with contextlib.ExitStack() as stack, contextlib.redirect_stdout(io.StringIO()):
            for patch in patches:
                stack.enter_context(patch)
            if mutate_served_asset:
                with self.assertRaisesRegex(RuntimeError, "served_target_digest_mismatch:assets/main.js"):
                    asyncio.run(completion.run(completion.parse_args(["smoke"])))
            else:
                self.assertEqual(asyncio.run(completion.run(completion.parse_args(["smoke"]))), 0)
        self.assertEqual(seen, [(list(completion.SMOKE_IDS), 2)])
        return root

    def test_live_stage_wiring_uses_new_url_library_and_build_and_seals_both_checks(self):
        root = self.run_authored_stage()
        provenance = completion.base.read_json(root / "input-provenance.json")
        status = completion.base.read_json(root / "run-status.json")
        self.assertEqual(status["state"], "smoke_passed")
        self.assertEqual(status["input_provenance_sha256"],
                         completion.base.digest_file(root / "input-provenance.json"))
        completion.require_target_receipts(provenance, status)

    def test_postrun_actual_http_drift_preserves_run_and_blocks_success(self):
        root = self.run_authored_stage(mutate_served_asset=True)
        status = completion.base.read_json(root / "run-status.json")
        self.assertEqual(status["state"], "stopped_preserved")
        self.assertIn("served_target_digest_mismatch:assets/main.js", status["reason"])
        self.assertTrue((root / "stage-2/report.json").is_file())

    def test_old_launcher_defaults_remain_old_and_new_launcher_has_own_pins(self):
        self.assertEqual(completion.base.BUILD_SHA256,
                         "d5755c8912660cf80c0c9f48d18cc8952a3e7b46fe04e82e673f1eaa96b10beb")
        self.assertEqual(completion.base.LIBRARY.name, "peekly-persona-library-v3")
        self.assertNotEqual(completion.LIBRARY, completion.base.LIBRARY)
        self.assertNotEqual(completion.BUILD, completion.base.BUILD)
        self.assertEqual(completion.base.capture_freeze.__kwdefaults__["expected_build_sha256"],
                         completion.base.BUILD_SHA256)

    def test_old_revision_cannot_be_relabelled_as_new_library(self):
        library = mock.MagicMock()
        library.__enter__.return_value = library
        library.list.return_value = dict(personas=[dict(persona_id=pid, revision=2, reusable=True)
                                                   for pid in completion.base.ALL_IDS])
        with tempfile.TemporaryDirectory() as folder, \
                mock.patch.object(completion.base, "owned_output", return_value=Path(folder) / "fresh"), \
                mock.patch.object(completion.base, "load_live", return_value=SimpleNamespace(Library=lambda _: library)), \
                mock.patch.object(completion, "verify_served_target", side_effect=AssertionError("No HTTP/model/browser")):
            args = completion.parse_args(["smoke", "--check-only"])
            with self.assertRaisesRegex(RuntimeError, "rebound_library_revision_mismatch"):
                asyncio.run(completion.run(args))


if __name__ == "__main__":
    unittest.main()
