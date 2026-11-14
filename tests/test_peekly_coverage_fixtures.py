"""Offline fixture-builder regressions; no model, browser, or product execution."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_peekly_coverage_fixtures import (  # noqa: E402
    FixtureBuildError, PROGRESS, RETENTION, SEARCH, build_fixtures,
)

OWNER = "peekly_fixture_owner"
SMALL = dict(progress_follower_rows=35, progress_following_rows=19,
             progress_chunk_rows=10)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def personal(owner):
    return {"profile_user": [{"string_map_data": {"Username": {"value": owner}}}]}


def row(handle, timestamp=1765152000):
    return {"string_list_data": [{"value": handle, "timestamp": timestamp,
                                  "href": "https://www.instagram.com/" + handle + "/"}]}


def write_zip(path, owner, followers, following, *, nested=False, padding=False):
    prefix = "connections/followers_and_following/" if nested else ""
    info_name = ("personal_information/personal_information/personal_information.json"
                 if nested else "personal_information.json")
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(info_name, json.dumps(personal(owner)))
        archive.writestr(prefix + "followers_1.json", json.dumps([row(x) for x in followers]))
        following_rows = [{"title": x, "string_list_data": [
            {"href": "https://www.instagram.com/_u/" + x, "timestamp": 1765152000}]}
            for x in following]
        archive.writestr(prefix + "following.json",
                         json.dumps({"relationships_following": following_rows}))
        archive.writestr("notes.json", '{"preserve":"unrelated metadata"}')
        if padding:
            archive.writestr("padding.bin", b"\0" * 128)


def make_source(path):
    path.mkdir()
    write_zip(path / "peekly-format-json.zip", OWNER, ["synthetic_a"], ["synthetic_b"])
    write_zip(path / "peekly-empty-previous.zip", OWNER, [], [])
    write_zip(path / "peekly-account-mismatch.zip", "different_synthetic_owner",
              ["synthetic_a"], ["synthetic_b"])
    write_zip(path / "peekly-sample-previous.zip", "legacy_sample_owner",
              ["synthetic_a", "synthetic_b", "synthetic_c"],
              ["synthetic_a", "synthetic_b", "synthetic_d"], nested=True)
    write_zip(path / "peekly-sample-current.zip", "legacy_sample_owner",
              ["synthetic_a", "synthetic_b"],
              ["synthetic_a", "synthetic_c", "synthetic_d"], nested=True)
    write_zip(path / PROGRESS, "legacy_sample_owner", ["synthetic_a"],
              ["synthetic_a"], padding=True)
    (path / "followers.json").write_text(json.dumps([row("synthetic_a")]))
    (path / "following.json").write_text(json.dumps([row("synthetic_b")]))
    (path / "personal_information.json").write_text(json.dumps(personal(OWNER)))
    (path / "retained.json").write_text('{"original":true}\n')
    files = [{"name": p.name, "bytes": p.stat().st_size, "sha256": digest(p),
              "scenario": "source-fixture"}
             for p in sorted(path.iterdir())]
    manifest = {"schema_version": "peekly-synthetic-fixtures.v1",
                "version": "peekly-explicit-success-v5-test",
                "created_at": "2026-11-14T00:00:00Z", "product_id": "peekly",
                "source": {"path": "authored-test-input"},
                "files": files,
                "groups": {"peekly-loose-pair": ["followers.json", "following.json"],
                           "keep-note": ["retained.json"]}}
    (path / "fixture-manifest.json").write_text(json.dumps(manifest))
    return manifest


def archive_data(path):
    with zipfile.ZipFile(path) as archive:
        return {i.filename: archive.read(i) for i in archive.infolist()}


def archive_owner(path):
    parts = archive_data(path)
    name = next(n for n in parts if Path(n).name == "personal_information.json")
    return json.loads(parts[name])["profile_user"][0]["string_map_data"]["Username"]["value"]


def relationships(path):
    followers, following = [], []
    for name, raw in archive_data(path).items():
        base = Path(name).name
        if not (base.startswith("followers_") or base == "following.json"):
            continue
        parsed = json.loads(raw)
        rows = parsed if isinstance(parsed, list) else parsed["relationships_following"]
        target = followers if base.startswith("followers_") else following
        for item in rows:
            target.append(item.get("title") or item["string_list_data"][0]["value"])
    return followers, following


def update_source_row(source, name):
    p = source / "fixture-manifest.json"
    data = json.loads(p.read_text())
    record = next(r for r in data["files"] if r["name"] == name)
    record.update(bytes=(source / name).stat().st_size, sha256=digest(source / name))
    p.write_text(json.dumps(data))


class CoverageFixtureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.original = make_source(self.source)
        self.dest = self.root / "new-output"

    def build(self, destination=None, **options):
        args = dict(SMALL)
        args.update(options)
        return build_fixtures(self.source, destination or self.dest, **args)

    def test_normalizes_sample_owner_preserves_payloads_groups_and_source(self):
        before = {str(p.relative_to(self.source)):
                  (digest(p), p.stat().st_mtime_ns, stat.S_IMODE(p.stat().st_mode))
                  for p in self.source.rglob("*") if p.is_file()}
        result = self.build()
        manifest = json.loads((self.dest / "fixture-manifest.json").read_text())
        self.assertEqual(manifest["groups"], self.original["groups"])
        self.assertEqual(result["retention_fixture_count"], 11)
        self.assertEqual(manifest["coverage"]["owner_sha256"],
                         hashlib.sha256(OWNER.encode()).hexdigest())
        for name in ("peekly-sample-previous.zip", "peekly-sample-current.zip",
                     "peekly-empty-previous.zip", "peekly-format-json.zip"):
            self.assertEqual(archive_owner(self.dest / name), OWNER)
        self.assertNotEqual(archive_owner(self.dest / "peekly-account-mismatch.zip"), OWNER)
        for name in ("peekly-sample-previous.zip", "peekly-sample-current.zip"):
            original, changed = archive_data(self.source / name), archive_data(self.dest / name)
            self.assertEqual(original.keys(), changed.keys())
            for member in original:
                if Path(member).name != "personal_information.json":
                    self.assertEqual(original[member], changed[member])
            self.assertEqual(relationships(self.source / name), relationships(self.dest / name))
            self.assertNotEqual(digest(self.source / name), digest(self.dest / name))
        after = {str(p.relative_to(self.source)):
                 (digest(p), p.stat().st_mtime_ns, stat.S_IMODE(p.stat().st_mode))
                 for p in self.source.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        for record in manifest["files"]:
            self.assertEqual(record["sha256"], digest(self.dest / record["name"]))
            self.assertEqual(record["bytes"], (self.dest / record["name"]).stat().st_size)

    def test_registers_eleven_distinct_same_account_recognized_snapshots(self):
        self.build()
        manifest = json.loads((self.dest / "fixture-manifest.json").read_text())
        names = [r["name"] for r in manifest["files"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(set(RETENTION) <= set(names))
        self.assertEqual(manifest["coverage"]["retention"]["fixtures"], list(RETENTION))
        hashes, sets, timestamps = set(), set(), set()
        for i, name in enumerate(RETENTION, 1):
            self.assertEqual(archive_owner(self.dest / name), OWNER)
            followers, following = relationships(self.dest / name)
            self.assertEqual(len(followers), 12 + i)
            self.assertEqual(len(following), 12)
            hashes.add(digest(self.dest / name))
            sets.add(tuple(sorted(followers)))
            meta = manifest["coverage"]["fixture_expectations"][name]
            timestamps.add(meta["timestamp"])
            self.assertEqual(meta["expected_counts"]["mutual"], 12)
        self.assertEqual((len(hashes), len(sets), len(timestamps)), (11, 11, 11))

    def test_search_fixture_has_twelve_rows_and_exact_safe_search_handle(self):
        self.build()
        manifest = json.loads((self.dest / "fixture-manifest.json").read_text())
        search = manifest["coverage"]["search"]
        followers, following = map(set, relationships(self.dest / SEARCH))
        outgoing = following - followers
        self.assertEqual(len(outgoing), 12)
        self.assertEqual((len(followers), len(following), len(followers & following)),
                         (20, 28, 16))
        self.assertEqual(search["rows"], 12)
        self.assertEqual(search["expected_filtered_rows"], 1)
        self.assertIn(search["search_handle"], outgoing)
        self.assertTrue(search["search_handle"].startswith("synthetic_"))
        self.assertEqual(sum(name == search["search_handle"] for name in outgoing), 1)

    def test_progress_stream_is_recognized_json_with_exact_rows_and_no_padding(self):
        self.build()
        manifest = json.loads((self.dest / "fixture-manifest.json").read_text())
        meta = manifest["coverage"]["progress"]
        data = archive_data(self.dest / PROGRESS)
        self.assertFalse(any("padding" in n for n in data))
        self.assertEqual(meta["row_counts"], {"followers": 35, "following": 19})
        self.assertEqual(meta["recognized_relationship_members"], 5)
        followers, following = relationships(self.dest / PROGRESS)
        self.assertEqual((len(followers), len(following)), (35, 19))
        self.assertEqual((len(set(followers)), len(set(following))), (16, 16))
        self.assertEqual(meta["expected_counts"]["mutual"], 16)
        for name, size in meta["member_bytes"].items():
            self.assertEqual(len(data[name]), size)
            self.assertLess(size, 32 * 1024 * 1024)
            self.assertEqual(len(json.loads(data[name])), meta["member_rows"][name])
        self.assertEqual(meta["archive_bytes"], (self.dest / PROGRESS).stat().st_size)
        self.assertFalse(meta["latency_guaranteed"])
        with zipfile.ZipFile(self.dest / PROGRESS) as archive:
            self.assertTrue(all(i.compress_type == zipfile.ZIP_STORED
                                for i in archive.infolist()))

    def test_identical_inputs_produce_identical_manifests_and_zip_bytes(self):
        self.build()
        second = self.root / "second-output"
        self.build(second)
        self.assertEqual((self.dest / "fixture-manifest.json").read_bytes(),
                         (second / "fixture-manifest.json").read_bytes())
        for path in self.dest.rglob("*"):
            if path.is_file():
                self.assertEqual(digest(path), digest(second / path.relative_to(self.dest)))

    def test_rejects_bad_hash_even_for_otherwise_unused_file_before_creating_output(self):
        (self.source / "retained.json").write_text('{"tampered":true}')
        with self.assertRaisesRegex(FixtureBuildError, "integrity"):
            self.build()
        self.assertFalse(self.dest.exists())

    def test_existing_destination_and_dangling_symlink_are_not_overwritten(self):
        self.dest.mkdir()
        sentinel = self.dest / "keep"
        sentinel.write_text("untouched")
        with self.assertRaisesRegex(FixtureBuildError, "destination_exists"):
            self.build()
        self.assertEqual(sentinel.read_text(), "untouched")
        link = self.root / "dangling"
        link.symlink_to(self.root / "nonexistent")
        with self.assertRaisesRegex(FixtureBuildError, "destination_exists"):
            self.build(link)
        self.assertTrue(link.is_symlink())
        self.assertFalse((self.root / "nonexistent").exists())

    def test_refuses_output_inside_source(self):
        child = self.source / "new-output"
        with self.assertRaisesRegex(FixtureBuildError, "inside_source"):
            self.build(child)
        self.assertFalse(child.exists())

    def test_rejects_manifest_traversal_and_duplicate_file_entries(self):
        manifest_path = self.source / "fixture-manifest.json"
        data = json.loads(manifest_path.read_text())
        data["files"].append({"name": "../escape.json", "bytes": 0, "sha256": "0" * 64})
        manifest_path.write_text(json.dumps(data))
        with self.assertRaisesRegex(FixtureBuildError, "unsafe_fixture_path"):
            self.build()
        self.assertFalse(self.dest.exists())
        data["files"].pop()
        data["files"].append(dict(data["files"][0]))
        manifest_path.write_text(json.dumps(data))
        with self.assertRaisesRegex(FixtureBuildError, "fixture_entry_invalid"):
            self.build()
        self.assertFalse(self.dest.exists())

    def test_rejects_source_symlink_and_unregistered_group_member(self):
        victim = self.source / "retained.json"
        target = self.root / "external-owned-test.json"
        target.write_bytes(victim.read_bytes())
        victim.unlink()
        victim.symlink_to(target)
        with self.assertRaisesRegex(FixtureBuildError, "symlink"):
            self.build()
        self.assertFalse(self.dest.exists())
        victim.unlink()
        victim.write_bytes(target.read_bytes())
        manifest_path = self.source / "fixture-manifest.json"
        data = json.loads(manifest_path.read_text())
        data["groups"]["bad"] = ["not-registered.json"]
        manifest_path.write_text(json.dumps(data))
        with self.assertRaisesRegex(FixtureBuildError, "group_invalid"):
            self.build()
        self.assertFalse(self.dest.exists())

    def test_rejects_traversal_inside_modified_zip_without_extracting_it(self):
        archive = self.source / "peekly-sample-current.zip"
        with zipfile.ZipFile(archive, "a") as output:
            output.writestr("../escaped.json", "{}")
        update_source_row(self.source, archive.name)
        with self.assertRaisesRegex(FixtureBuildError, "unsafe_fixture_path"):
            self.build()
        self.assertFalse(self.dest.exists())
        self.assertFalse((self.root / "escaped.json").exists())

    def test_refuses_reference_account_disagreement_and_fake_mismatch(self):
        empty = self.source / "peekly-empty-previous.zip"
        write_zip(empty, "other_synthetic_owner", [], [])
        update_source_row(self.source, empty.name)
        with self.assertRaisesRegex(FixtureBuildError, "reference_fixture_accounts_disagree"):
            self.build()
        self.assertFalse(self.dest.exists())
        write_zip(empty, OWNER, [], [])
        update_source_row(self.source, empty.name)
        mismatch = self.source / "peekly-account-mismatch.zip"
        write_zip(mismatch, OWNER, ["synthetic_a"], ["synthetic_b"])
        update_source_row(self.source, mismatch.name)
        with self.assertRaisesRegex(FixtureBuildError, "mismatch_fixture_has_matching"):
            self.build()
        self.assertFalse(self.dest.exists())

    def test_progress_limits_fail_before_output_creation(self):
        for overrides in ({"progress_follower_rows": 0},
                          {"progress_follower_rows": True},
                          {"progress_following_rows": 400_000},
                          {"progress_follower_rows": 1_000_000, "progress_chunk_rows": 1},
                          {"progress_follower_rows": 10**100,
                           "progress_chunk_rows": 10**100}):
            with self.subTest(overrides=overrides):
                with self.assertRaises(FixtureBuildError):
                    self.build(**overrides)
                self.assertFalse(self.dest.exists())


if __name__ == "__main__":
    unittest.main()
