#!/usr/bin/env python3
"""Build immutable, hash-pinned synthetic inputs for Peekly coverage runs.

Only a new destination is written. The old fixture directories remain evidence.
Large progress fixtures contain recognized relationship JSON, not ignored padding;
their size does not guarantee a processing duration on any particular host.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import zipfile

MIB = 1024 * 1024
SCHEMA = "peekly-synthetic-fixtures.v1"
ZIP_DATE = (2020, 1, 1, 0, 0, 0)
TIMESTAMP = 1765152000
PERSONAL = "personal_information/personal_information/personal_information.json"
RELATIONS = "connections/followers_and_following/"
SAMPLES = ("peekly-sample-previous.zip", "peekly-sample-current.zip")
PROGRESS = "peekly-progress-sample.zip"
SEARCH = "peekly-search-ready.zip"
LEGACY_SEED = "peekly-legacy-unknown-state.json"
LEGACY_SNAPSHOT_ID = "peekly_legacy_unknown_v6"
LEGACY_PRODUCT_COMMIT = "51110f4c569673faa8d242d5b85c4b47afb54cbb"
LEGACY_PRODUCT_LOADER_SHA256 = "401759c4ef2d11efcf7b710292ba6269ce66653cd3d19fd2164fa6f54883559a"
RETENTION = tuple(f"peekly-retention-snapshot-{i:02d}.zip" for i in range(1, 12))
REQUIRED = {*SAMPLES, PROGRESS, "peekly-format-json.zip",
            "peekly-empty-previous.zip", "peekly-account-mismatch.zip"}
PROGRESS_HANDLES = tuple(f"synthetic_progress_{i:02d}" for i in range(16))
PROGRESS_FOLLOWER_ROWS = 300_000
PROGRESS_FOLLOWING_ROWS = 120_000
MAX_RECOGNIZED_JSON_BYTES = 64 * MIB


class FixtureBuildError(ValueError):
    """A fixture input or output cannot satisfy the frozen-input contract."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(MIB), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _safe_name(value: str) -> str:
    if (not isinstance(value, str) or not value or "\\" in value
            or not re.fullmatch(r"[A-Za-z0-9._/-]+", value)
            or any(part in ("", ".", "..") for part in value.split("/"))
            or PurePosixPath(value).is_absolute()):
        raise FixtureBuildError("unsafe_fixture_path")
    return value


def _source_file(source: Path, name: str) -> Path:
    name = _safe_name(name)
    path = source
    for part in PurePosixPath(name).parts:
        path = path / part
        if path.is_symlink():
            raise FixtureBuildError("source_fixture_symlink:" + name)
    if not path.is_file() or not path.resolve().is_relative_to(source):
        raise FixtureBuildError("source_fixture_missing:" + name)
    return path


def _verify_file(path: Path, row: dict) -> None:
    if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
        raise FixtureBuildError("source_fixture_integrity_failed:" + row["name"])


def _load_source(source: Path):
    manifest_path = _source_file(source, "fixture-manifest.json")
    if manifest_path.stat().st_size > 8 * MIB:
        raise FixtureBuildError("fixture_manifest_too_large")
    manifest_bytes = manifest_path.read_bytes()
    try:
        manifest = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FixtureBuildError("fixture_manifest_invalid") from exc
    if (not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA
            or not str(manifest.get("version", "")).startswith("peekly-explicit-success-v5")
            or not isinstance(manifest.get("files"), list)
            or not isinstance(manifest.get("groups"), dict)):
        raise FixtureBuildError("fixture_manifest_schema_invalid")
    files = {}
    case_names = set()
    for row in manifest["files"]:
        if not isinstance(row, dict):
            raise FixtureBuildError("fixture_entry_invalid")
        name = _safe_name(row.get("name"))
        if (name == "fixture-manifest.json" or name.casefold() in case_names
                or type(row.get("bytes")) is not int or row["bytes"] < 0
                or not isinstance(row.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])):
            raise FixtureBuildError("fixture_entry_invalid:" + name)
        case_names.add(name.casefold())
        path = _source_file(source, name)
        _verify_file(path, row)
        files[name] = copy.deepcopy(row)
    if not REQUIRED <= files.keys():
        raise FixtureBuildError("required_source_fixture_missing")
    if SEARCH in files or set(RETENTION) & files.keys():
        raise FixtureBuildError("coverage_fixture_already_present_in_source")
    for name, members in manifest["groups"].items():
        _safe_name(name)
        if (not isinstance(members, list) or not members
                or any(not isinstance(member, str) or member not in files
                       for member in members)):
            raise FixtureBuildError("fixture_group_invalid:" + name)
    return manifest, files, hashlib.sha256(manifest_bytes).hexdigest()


def _zip_contents(path: Path) -> dict[str, bytes]:
    """Read only the small source archives that need semantic inspection."""
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if len(infos) > 512:
                raise FixtureBuildError("source_archive_member_count:" + path.name)
            result = {}
            folded = set()
            total = 0
            for info in infos:
                name = _safe_name(info.filename.rstrip("/") if info.is_dir()
                                  else info.filename)
                if name.casefold() in folded:
                    raise FixtureBuildError("source_archive_duplicate_member:" + path.name)
                folded.add(name.casefold())
                mode = info.external_attr >> 16
                if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise FixtureBuildError("source_archive_special_member:" + path.name)
                if info.is_dir():
                    continue
                total += info.file_size
                if info.file_size >= 32 * MIB or total >= 128 * MIB:
                    raise FixtureBuildError("source_archive_member_size:" + path.name)
                result[name] = archive.read(info)
            return result
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise FixtureBuildError("source_archive_invalid:" + path.name) from exc


def _owner_slot(document):
    try:
        users = document["profile_user"]
        if not isinstance(users, list) or len(users) != 1:
            raise KeyError("profile_user")
        slot = users[0]["string_map_data"]["Username"]
        owner = slot["value"]
    except (KeyError, IndexError, TypeError) as exc:
        raise FixtureBuildError("source_owner_shape_invalid") from exc
    if not isinstance(owner, str) or not re.fullmatch(r"[A-Za-z0-9._]{1,30}", owner):
        raise FixtureBuildError("source_owner_invalid")
    return slot


def _owner_document(contents):
    paths = [name for name in contents
             if PurePosixPath(name).name == "personal_information.json"]
    if len(paths) != 1:
        raise FixtureBuildError("source_personal_information_ambiguous")
    try:
        document = json.loads(contents[paths[0]])
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FixtureBuildError("source_personal_information_invalid") from exc
    slot = _owner_slot(document)
    return paths[0], document, slot["value"]


def _personal(owner):
    return {"profile_user": [{"string_map_data": {"Username": {"value": owner}}}]}


def _relation_row(handle, timestamp=TIMESTAMP):
    return {"string_list_data": [{"value": handle,
                                  "href": "https://www.instagram.com/" + handle + "/",
                                  "timestamp": timestamp}]}


def _counts(followers, following):
    followers, following = set(followers), set(following)
    return {"followers": len(followers), "following": len(following),
            "mutual": len(followers & following),
            "not_following_me": len(following - followers),
            "i_dont_follow": len(followers - following)}


def _sample_counts(contents):
    found = {"followers": set(), "following": set()}
    row_counts = {"followers": 0, "following": 0}
    seen = set()
    for name, raw in contents.items():
        basename = PurePosixPath(name).name
        kind = ("followers" if re.fullmatch(r"followers(?:_\d+)?\.json", basename)
                else "following" if basename == "following.json" else None)
        if kind is None:
            continue
        seen.add(kind)
        try:
            rows = json.loads(raw)
            if isinstance(rows, dict):
                rows = rows["relationships_" + kind]
            if not isinstance(rows, list):
                raise ValueError("rows")
            row_counts[kind] += len(rows)
            for row in rows:
                values = row.get("string_list_data", [])
                handle = row.get("title") or (values[0].get("value") if values else None)
                if not handle:
                    raise ValueError("handle")
                found[kind].add(handle)
        except (KeyError, TypeError, AttributeError, ValueError) as exc:
            raise FixtureBuildError("source_relationship_shape_invalid:" + name) from exc
    if seen != {"followers", "following"}:
        raise FixtureBuildError("source_relationship_members_missing")
    return {"row_counts": row_counts, "expected_counts": _counts(**found)}


def _zip_info(name):
    info = zipfile.ZipInfo(_safe_name(name), ZIP_DATE)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o600) << 16
    return info


def _write_zip(path, contents):
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_STORED,
                         allowZip64=False) as archive:
        for name in sorted(contents):
            archive.writestr(_zip_info(name), contents[name])
    os.chmod(path, 0o600)


def _make_relationship_archive(path, owner, followers, following, timestamp):
    contents = {PERSONAL: _json_bytes(_personal(owner)),
                RELATIONS + "followers_1.json":
                    _json_bytes([_relation_row(x, timestamp) for x in followers]),
                RELATIONS + "following.json":
                    _json_bytes([_relation_row(x, timestamp) for x in following])}
    _write_zip(path, contents)


def _progress_layout(follower_rows, following_rows, chunk_rows):
    if any(type(n) is not int or n <= 0
           for n in (follower_rows, following_rows, chunk_rows)):
        raise FixtureBuildError("progress_row_count_invalid")
    parts = (follower_rows + chunk_rows - 1) // chunk_rows
    if parts > 510:
        raise FixtureBuildError("progress_member_count_exceeded")
    templates = tuple(_json_bytes(_relation_row(name)).rstrip(b"\n")
                      for name in PROGRESS_HANDLES)
    if len({len(row) for row in templates}) != 1:
        raise FixtureBuildError("progress_template_size_mismatch")
    row_size = len(templates[0])
    layout = [(RELATIONS + f"followers_{i + 1}.json",
               min(chunk_rows, follower_rows - i * chunk_rows))
              for i in range(parts)]
    layout.append((RELATIONS + "following.json", following_rows))
    sizes = {name: n * (row_size + 1) + 2 for name, n in layout}
    if any(size >= 32 * MIB for size in sizes.values()):
        raise FixtureBuildError("progress_member_limit_exceeded")
    if sum(sizes.values()) > MAX_RECOGNIZED_JSON_BYTES:
        raise FixtureBuildError("progress_recognized_json_total_limit_exceeded")
    # Conservative ZIP headers plus the small personal-information member.
    projected = sum(sizes.values()) + sum(2 * len(name) + 256 for name in sizes) + 4096
    if projected >= 128 * MIB:
        raise FixtureBuildError("progress_archive_limit_exceeded")
    return templates, layout, sizes


def _progress_json_bytes(sizes, owner):
    # Pinned product 51110f4 zipParser accumulates every recognized JSON member,
    # including personal information, and rejects strictly above 64 MiB.
    total = sum(sizes.values()) + len(_json_bytes(_personal(owner)))
    if total > MAX_RECOGNIZED_JSON_BYTES:
        raise FixtureBuildError("progress_recognized_json_total_limit_exceeded")
    return total


def _write_progress(path, owner, templates, layout):
    with zipfile.ZipFile(path, "x", compression=zipfile.ZIP_STORED,
                         allowZip64=False) as archive:
        archive.writestr(_zip_info(PERSONAL), _json_bytes(_personal(owner)))
        follower_offset = 0
        for name, count in layout:
            offset = 0 if PurePosixPath(name).name == "following.json" else follower_offset
            with archive.open(_zip_info(name), "w") as stream:
                stream.write(b"[")
                for start in range(0, count, 4096):
                    if start:
                        stream.write(b",")
                    stop = min(start + 4096, count)
                    stream.write(b",".join(templates[(offset + i) % len(templates)]
                                           for i in range(start, stop)))
                stream.write(b"]\n")
            if PurePosixPath(name).name != "following.json":
                follower_offset += count
    os.chmod(path, 0o600)
    if path.stat().st_size >= 128 * MIB:
        raise FixtureBuildError("progress_archive_limit_exceeded")


def _copy_verified(source, destination, row):
    path = destination / row["name"]
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    size = 0
    with _source_file(source, row["name"]).open("rb") as incoming, path.open("xb") as outgoing:
        for block in iter(lambda: incoming.read(MIB), b""):
            digest.update(block)
            size += len(block)
            outgoing.write(block)
    os.chmod(path, 0o600)
    if size != row["bytes"] or digest.hexdigest() != row["sha256"]:
        raise FixtureBuildError("source_changed_during_copy:" + row["name"])


def legacy_seed_state(owner):
    """A genuine pre-provenance snapshot, not an empty current-format import."""
    if not isinstance(owner, str) or not re.fullmatch(r"[a-z0-9._]{1,30}", owner):
        raise FixtureBuildError("legacy_seed_owner_invalid")
    def user(name):
        return {"pk": name, "username": name, "timestamp": TIMESTAMP - 86400}
    snapshot = {
        "id": LEGACY_SNAPSHOT_ID, "accountHandle": owner,
        "label": "합성 이전 버전 기록", "createdAt": (TIMESTAMP - 86400) * 1000,
        "isSample": False,
        "followers": [user("synthetic_legacy_mutual"), user("synthetic_legacy_follower")],
        "following": [user("synthetic_legacy_mutual"), user("synthetic_legacy_following")],
        "pendingFollowRequests": [], "recentlyUnfollowed": [], "closeFriends": [],
        "blockedProfiles": [], "restrictedProfiles": [], "hideStoryFrom": [],
        "likesGivenByAuthor": {}, "commentsGivenByAuthor": {},
    }
    # Both provenance fields are deliberately absent. The real product normalizer
    # must infer includedFiles and assign UNKNOWN; the host never assigns it.
    return {
        "snapshots": [snapshot], "activeSnapshotId": LEGACY_SNAPSHOT_ID,
        "comparisonSnapshotId": LEGACY_SNAPSHOT_ID, "whitelistedUsernames": [],
        "customTagsByUsername": {}, "unfollowLog": [], "cleanupQueueUsernames": [],
        "profileChecks": {}, "entitlement": {
            "tier": "FREE", "secretPassExpiresAt": None, "rewardUnlockedItemIds": [],
            "whitelistLimit": 20, "customTagLimit": 2, "maxAccounts": 1},
    }


def _validated_legacy_seed(destination, owner, product_path, node):
    path = destination / LEGACY_SEED
    with path.open("xb") as stream:
        stream.write(_json_bytes(legacy_seed_state(owner)))
    os.chmod(path, 0o600)
    command = [str(node), str(Path(__file__).with_name("validate_peekly_legacy_seed.mjs")),
               str(Path(product_path).resolve(strict=True)), str(path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30,
                                check=False)
        validation = json.loads(result.stdout) if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise FixtureBuildError("legacy_product_validation_unavailable") from exc
    required = {"v6_missing_metadata_migrates_unknown", "legacy_snapshot_retained",
                "legacy_excluded_from_selection", "v7_roundtrip_valid",
                "known_empty_is_known", "malformed_v7_rejected_without_legacy_fallback",
                "plain_v7_under_compression_threshold"}
    if (not isinstance(validation, dict)
            or validation.get("schema_version") != "peekly-legacy-product-validation.v1"
            or validation.get("product_commit") != LEGACY_PRODUCT_COMMIT
            or validation.get("product_loader_sha256") != LEGACY_PRODUCT_LOADER_SHA256
            or validation.get("fixture_sha256") != sha256(path)
            or set(validation.get("checks", {})) != required
            or any(value is not True for value in validation["checks"].values())):
        raise FixtureBuildError("legacy_product_validation_failed")
    return {"schema_version": "peekly-legacy-seed-fixture.v1",
            "fixture": LEGACY_SEED, "fixture_sha256": sha256(path),
            "storage_key": "peekly_state_v6", "snapshot_ids": [LEGACY_SNAPSHOT_ID],
            "owner_sha256": hashlib.sha256(owner.encode("utf-8")).hexdigest(),
            "source_included_files_absent": True,
            "source_list_completeness_absent": True,
            "product_commit": LEGACY_PRODUCT_COMMIT,
            "product_loader_sha256": LEGACY_PRODUCT_LOADER_SHA256,
            "product_validation_sha256": hashlib.sha256(_json_bytes(validation)).hexdigest(),
            "product_validation": validation}


def build_fixtures(source, destination, *, progress_follower_rows=PROGRESS_FOLLOWER_ROWS,
                   progress_following_rows=PROGRESS_FOLLOWING_ROWS, progress_chunk_rows=100_000,
                   legacy_product_path=None, legacy_node="node"):
    source, destination = Path(source), Path(destination)
    if source.is_symlink():
        raise FixtureBuildError("source_directory_symlink")
    source = source.resolve(strict=True)
    if not source.is_dir():
        raise FixtureBuildError("source_directory_invalid")
    if os.path.lexists(destination):
        raise FixtureBuildError("destination_exists")
    destination = destination.resolve()
    if destination.is_relative_to(source):
        raise FixtureBuildError("destination_inside_source")
    templates, layout, sizes = _progress_layout(
        progress_follower_rows, progress_following_rows, progress_chunk_rows)
    original, files, manifest_sha = _load_source(source)
    inspected = {name: _zip_contents(source / name)
                 for name in (*SAMPLES, "peekly-format-json.zip",
                              "peekly-empty-previous.zip", "peekly-account-mismatch.zip")}
    owner = _owner_document(inspected["peekly-format-json.zip"])[2]
    progress_json_bytes = _progress_json_bytes(sizes, owner)
    if _owner_document(inspected["peekly-empty-previous.zip"])[2] != owner:
        raise FixtureBuildError("reference_fixture_accounts_disagree")
    mismatch_owner = _owner_document(inspected["peekly-account-mismatch.zip"])[2]
    if mismatch_owner.casefold() == owner.casefold():
        raise FixtureBuildError("mismatch_fixture_has_matching_account")
    sample_metadata = {}
    for name in SAMPLES:
        member, personal, _ = _owner_document(inspected[name])
        sample_metadata[name] = _sample_counts(inspected[name])
        _owner_slot(personal)["value"] = owner
        inspected[name][member] = _json_bytes(personal)
    # Validate every source before reserving a new destination. mkdir is exclusive:
    # a concurrently-created destination cannot be overwritten.
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir(mode=0o700)
    legacy = (_validated_legacy_seed(destination, owner, legacy_product_path, legacy_node)
              if legacy_product_path is not None else None)
    modified = {*SAMPLES, PROGRESS}
    for name, row in files.items():
        if name not in modified:
            _copy_verified(source, destination, row)
    for name in SAMPLES:
        _write_zip(destination / name, inspected[name])
        _verify_file(source / name, files[name])
    _write_progress(destination / PROGRESS, owner, templates, layout)

    owner_sha = hashlib.sha256(owner.encode("utf-8")).hexdigest()
    expectations = copy.deepcopy(sample_metadata)
    retention_meta = {}
    common = [f"synthetic_retention_common_{i:02d}" for i in range(12)]
    for number, name in enumerate(RETENTION, 1):
        extra = [f"synthetic_retention_added_{i:02d}" for i in range(1, number + 1)]
        followers, following = common + extra, common
        timestamp = TIMESTAMP + number * 86400
        _make_relationship_archive(destination / name, owner, followers, following, timestamp)
        retention_meta[name] = {"sequence": number, "timestamp": timestamp,
                               "row_counts": {"followers": len(followers),
                                              "following": len(following)},
                               "expected_counts": _counts(followers, following)}
        expectations[name] = retention_meta[name]
    common_search = [f"synthetic_search_common_{i:02d}" for i in range(16)]
    outgoing = [f"synthetic_search_outgoing_{i:02d}" for i in range(12)]
    incoming = [f"synthetic_search_incoming_{i:02d}" for i in range(4)]
    search_followers, search_following = common_search + incoming, common_search + outgoing
    _make_relationship_archive(destination / SEARCH, owner, search_followers,
                               search_following, TIMESTAMP)
    search_counts = _counts(search_followers, search_following)
    expectations[SEARCH] = {"row_counts": {"followers": len(search_followers),
                                         "following": len(search_following)},
                            "expected_counts": search_counts}
    progress_counts = _counts(PROGRESS_HANDLES[:min(progress_follower_rows, 16)],
                              PROGRESS_HANDLES[:min(progress_following_rows, 16)])
    expectations[PROGRESS] = {"row_counts": {"followers": progress_follower_rows,
                                           "following": progress_following_rows},
                              "expected_counts": progress_counts}

    all_names = set(files) | set(RETENTION) | {SEARCH}
    if legacy:
        all_names.add(LEGACY_SEED)
    generated_scenarios = {PROGRESS: "recognized-relationship-json-progress",
                           SEARCH: "search-ready-12-following-only-rows",
                           LEGACY_SEED: "validated-legacy-state-missing-provenance"}
    generated_scenarios.update({name: f"retention-snapshot-{i:02d}"
                                for i, name in enumerate(RETENTION, 1)})
    output_rows = []
    for name in sorted(all_names):
        row = copy.deepcopy(files.get(name, {"name": name}))
        path = destination / name
        row.update(bytes=path.stat().st_size, sha256=sha256(path))
        if name in generated_scenarios:
            row["scenario"] = generated_scenarios[name]
        output_rows.append(row)
    if len({row["sha256"] for row in output_rows if row["name"] in RETENTION}) != 11:
        raise FixtureBuildError("retention_snapshots_not_distinct")
    manifest = copy.deepcopy(original)
    manifest.update(version="peekly-coverage-fixtures-v2" if legacy else "peekly-coverage-fixtures-v1", files=output_rows,
                    source={"path": "synthetic-coverage-derived-from-v5",
                            "manifest_sha256": manifest_sha,
                            "preserves": "source directory unchanged; groups preserved"})
    manifest["coverage"] = {
        "schema_version": "peekly-coverage-fixture-metadata.v1",
        "source_manifest_sha256": manifest_sha,
        "owner_sha256": owner_sha,
        "mismatch_owner_sha256": hashlib.sha256(mismatch_owner.encode("utf-8")).hexdigest(),
        "account_pairs": {"previous_current": list(SAMPLES),
                          "empty_current": ["peekly-empty-previous.zip", SAMPLES[1]]},
        "fixture_expectations": expectations,
        "retention": {"fixtures": list(RETENTION), "distinct_snapshots": 11,
                      "same_account_sha256": owner_sha},
        "search": {"fixture": SEARCH, "category": "not_following_me",
                   "label": "나를 맞팔 안 한 사람", "rows": 12,
                   "search_handle": outgoing[5], "expected_filtered_rows": 1,
                   "expected_counts": search_counts},
        "progress": {"fixture": PROGRESS, "compression": "ZIP_STORED",
                     "recognized_relationship_members": len(layout),
                     "member_rows": dict(layout), "member_bytes": sizes,
                     "recognized_json_bytes": progress_json_bytes,
                     "recognized_json_limit_bytes": MAX_RECOGNIZED_JSON_BYTES,
                     "personal_information_bytes": len(_json_bytes(_personal(owner))),
                     "row_counts": {"followers": progress_follower_rows,
                                    "following": progress_following_rows},
                     "expected_counts": progress_counts,
                     "repeated_synthetic_handles": 16,
                     "archive_bytes": (destination / PROGRESS).stat().st_size,
                     "ignored_padding": False, "latency_guaranteed": False},
        "modified_source_files": sorted(modified),
    }
    if legacy:
        manifest["coverage"]["legacy_seed"] = legacy
    # Only a fully built, verified directory receives its final manifest.
    manifest_path = destination / "fixture-manifest.json"
    with manifest_path.open("xb") as stream:
        stream.write(_json_bytes(manifest))
    os.chmod(manifest_path, 0o600)
    return {"fixture_count": len(output_rows),
            "manifest_sha256": sha256(manifest_path),
            "progress_fixture_bytes": (destination / PROGRESS).stat().st_size,
            "owner_sha256": owner_sha, "retention_fixture_count": 11}


def main(source, destination, **options):
    result = build_fixtures(source, destination, **options)
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--progress-followers", type=int, default=PROGRESS_FOLLOWER_ROWS)
    parser.add_argument("--progress-following", type=int, default=PROGRESS_FOLLOWING_ROWS)
    parser.add_argument("--progress-chunk-rows", type=int, default=100_000)
    parser.add_argument("--legacy-product-path", type=Path,
                        help="Validate the new seed with the pinned product loader; never modifies product files.")
    parser.add_argument("--legacy-node", default="node")
    args = parser.parse_args()
    try:
        main(args.source, args.destination,
             progress_follower_rows=args.progress_followers,
             progress_following_rows=args.progress_following,
             progress_chunk_rows=args.progress_chunk_rows,
             legacy_product_path=args.legacy_product_path, legacy_node=args.legacy_node)
    except (FixtureBuildError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
