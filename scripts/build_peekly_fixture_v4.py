#!/usr/bin/env python3
"""Build hash-pinned, synthetic boundary fixtures for the Peekly desktop run."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(source: Path, destination: Path) -> None:
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if destination.exists() or not (source / "fixture-manifest.json").is_file():
        raise SystemExit("fixture_source_invalid_or_destination_exists")
    original = json.loads((source / "fixture-manifest.json").read_text())
    if original.get("schema_version") != "peekly-synthetic-fixtures.v1":
        raise SystemExit("fixture_manifest_schema_invalid")
    destination.mkdir(parents=True, mode=0o700)
    files = []
    for row in original["files"]:
        name = row["name"]
        source_file = source / name
        if source_file.is_symlink() or not source_file.is_file() or source_file.stat().st_size != row["bytes"] or sha256(source_file) != row["sha256"]:
            raise SystemExit("source_fixture_integrity_failed:" + name)
        shutil.copyfile(source_file, destination / name)
        files.append(dict(name=name, bytes=(destination / name).stat().st_size,
                          sha256=sha256(destination / name), scenario=row.get("scenario", "existing-v3")))

    progress_name = "peekly-progress-sample.zip"
    sample = source / "peekly-sample-current.zip"
    progress = destination / progress_name
    with zipfile.ZipFile(sample, "r") as incoming, zipfile.ZipFile(progress, "w", compression=zipfile.ZIP_STORED) as outgoing:
        for info in incoming.infolist():
            outgoing.writestr(info.filename, incoming.read(info.filename), compress_type=zipfile.ZIP_STORED)
        with outgoing.open("padding.bin", "w") as padding:
            block = bytes(1024 * 1024)
            for _ in range(64):
                padding.write(block)
    files.append(dict(name=progress_name, bytes=progress.stat().st_size,
                      sha256=sha256(progress), scenario="large-valid-progress"))

    oversized_name = "peekly-oversize-plus-one.zip"
    oversized = destination / oversized_name
    fd = os.open(oversized, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.ftruncate(fd, 128 * 1024 * 1024 + 1)
    finally:
        os.close(fd)
    files.append(dict(name=oversized_name, bytes=oversized.stat().st_size,
                      sha256=sha256(oversized), scenario="oversize-128mib-plus-one"))

    manifest = dict(schema_version="peekly-synthetic-fixtures.v1", version="peekly-explicit-success-v4",
        created_at=original.get("created_at"), product_id="peekly",
        source=dict(path="src/core/zipParser.ts", sha256="synthetic-only-boundary-fixtures-no-product-source-modification"),
        files=files)
    (destination / "fixture-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    os.chmod(destination / "fixture-manifest.json", 0o600)
    print(json.dumps({"fixture_count": len(files), "progress_fixture_bytes": progress.stat().st_size,
        "oversize_fixture_bytes": oversized.stat().st_size,
        "manifest_sha256": sha256(destination / "fixture-manifest.json")}, ensure_ascii=False))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    main(args.source, args.destination)
