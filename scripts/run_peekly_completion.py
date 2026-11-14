#!/usr/bin/env python3
"""Fresh legacy/coverage verification: a two-person gate, then a distinct 32 cohort.

Only new owned output roots are accepted. Prior queues are read-only; uncertain
deliveries are never resumed. --check-only does not call a model or browser.
"""
from __future__ import annotations

import argparse
import asyncio
import contextlib
from datetime import datetime
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import sys
from types import SimpleNamespace
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler, Request

import run_peekly_coverage as base

ROOT, SKILL = base.ROOT, base.SKILL
TARGET_ROOT = ROOT / ".ux-loop/peekly-pinned-product-51110f4-20261115"
SOURCE = TARGET_ROOT / "source"
DIST = SOURCE / "dist"
BUILD = TARGET_ROOT / "build-manifest.json"
BUILD_SHA256 = "c8adccb882b4bba6592e11f3792b8779809f771e66ea169118b5db84a7100d17"
SOURCE_MANIFEST_SHA256 = "9ce11a5c0486813db91072d27d540f60d386ceb24501cfd1bca08f38953dff8b"
BUILD_PROVENANCE_SHA256 = "5cde3d5a03ef0542ff29416ec559cbe7bf6d8aed8bd3d42a5c07f9bd219a77db"
SOURCE_FILE_COUNT = 319
TARGET_URL = "http://127.0.0.1:4175/"
LIBRARY = ROOT / ".ux-loop/peekly-persona-library-v4-pinned-20261115"
LIBRARY_SHA256 = "02c728a1b750d86164e035d88c096ffa7feca42f363cb68ed697a3beec7fa616"
SOURCE_TREE_SHA256 = "fa8c54630cfdef4260230d7b41a6a8a54405a97079961f66d2d43b47bd70c99e"
HISTORICAL_INDEX_SHA256 = "848b334a6affa5c6a578911819aaf127da34bc2e6ae2f04899022872b7d0f6f5"
# R1-R5 stay preserved. R4's 024/032 operations settled before its known pause;
# use new jobs/contexts for this pair's six obligations and two-not-run baseline.
SMOKE_IDS = ("PER-PEEKLY-V2-024", "PER-PEEKLY-V2-032")
SMOKE_BASELINE_NOT_RUN = 2
DEFAULT_SMOKE = ROOT / ".ux-loop/peekly-completion-smoke-r6-20261115"
DEFAULT_COHORT = ROOT / ".ux-loop/peekly-completion32-pinned-20261115"
FIXTURES = ROOT / ".ux-loop/peekly-coverage-fixtures-v8-20261115"
FIXTURE_MANIFEST_SHA = "9654fa6b07da5d443fbc97df16ab8885e170084ceda23399a36fbbd721997941"
SEED_SHA = "f4ea8b627d7b305552cf326205096aa244cf40a873fcbf275807947feec1a6f5"
VALIDATION_SHA = "8812e073064029937aaecb1908d0301eff96c2bee8794e3ee8ec6a6ddc46871c"
PRODUCT_COMMIT = "51110f4c569673faa8d242d5b85c4b47afb54cbb"
TURN_POLICY = dict(approved_ceiling=80, default_peekly=64, retention_and_paywall=80)
PINNED_FILES = {
    "peekly-sample-current.zip": "938514f0010f47ace5c2a2fdae17d2c237fd82838cedd78829e0915d367ca186",
    "peekly-sample-previous.zip": "b06f0fd115ab74703087e11f0c025df3791a09664cd03922a9fe182760fdc823",
    "peekly-legacy-unknown-state.json": SEED_SHA,
}
VALIDATION_CHECKS = (
    "known_empty_is_known", "legacy_excluded_from_selection",
    "legacy_snapshot_retained", "malformed_v7_rejected_without_legacy_fallback",
    "plain_v7_under_compression_threshold", "v6_missing_metadata_migrates_unknown",
    "v7_roundtrip_valid",
)


def target_require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def relative_file(root, name):
    """A manifest may name a file, never traverse or follow a symlink."""
    target_require(isinstance(name, str) and name and "\\" not in name,
                   "target_manifest_path_invalid")
    relative = PurePosixPath(name)
    target_require(not relative.is_absolute() and str(relative) == name
                   and all(part not in {".", ".."} for part in relative.parts),
                   "target_manifest_path_invalid")
    path = root / name
    target_require(path.is_file() and path.resolve().is_relative_to(root.resolve())
                   and not any((root / Path(*relative.parts[:i])).is_symlink()
                               for i in range(1, len(relative.parts) + 1)),
                   "target_file_missing_or_symlink:" + name)
    return path


class EntryAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.modules, self.assets = [], []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "script" and attrs.get("type") == "module" and attrs.get("src"):
            self.modules.append(attrs["src"])
            self.assets.append(attrs["src"])
        if tag == "link" and set((attrs.get("rel") or "").split()) & {"stylesheet", "modulepreload"}:
            self.assets.append(attrs.get("href"))


def entry_assets(index_bytes, files):
    parser = EntryAssets()
    parser.feed(index_bytes.decode("utf-8", errors="strict"))
    target_require(parser.modules, "target_module_entry_missing")
    paths = []
    for item in parser.assets:
        target_require(isinstance(item, str) and item and "\\" not in item,
                       "target_entry_asset_invalid")
        parsed = urlsplit(item)
        name = parsed.path.removeprefix("/")
        target_require(not parsed.scheme and not parsed.netloc and not parsed.query
                       and not parsed.fragment and unquote(name) == name
                       and name == str(PurePosixPath(name))
                       and all(part not in {".", ".."} for part in PurePosixPath(name).parts)
                       and name in files, "target_entry_asset_outside_pin")
        paths.append(name)
    target_require(len(paths) == len(set(paths)), "target_entry_asset_duplicate")
    return sorted(paths)


class NoTargetRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, message, headers, new_url):
        raise RuntimeError("target_http_redirect_rejected")


def fetch_target_bytes(url, maximum):
    # No proxies, redirects, credentials, browser or provider. Only our owned preview.
    target_require(url.startswith(TARGET_URL) and urlsplit(url).netloc == "127.0.0.1:4175",
                   "target_http_origin_not_owned")
    request = Request(url, headers={"Cache-Control": "no-cache", "Accept-Encoding": "identity"})
    opener = build_opener(ProxyHandler({}), NoTargetRedirect())
    with opener.open(request, timeout=5) as response:
        target_require(response.status == 200 and response.geturl() == url,
                       "target_http_response_invalid")
        data = response.read(maximum + 1)
    target_require(len(data) <= maximum, "target_http_size_limit")
    return data


def target_receipt_core(target):
    names = ["index.html", *target["entry_assets"]]
    return dict(schema_version="peekly-served-target-check.v1", target_url=TARGET_URL,
                build_sha256=target["build_sha256"], source_commit=PRODUCT_COMMIT,
                source_tree_sha256=target["source_tree_sha256"],
                entry_assets=target["entry_assets"],
                files={name: target["files"][name] for name in names})


def verify_served_target(target, phase, *, fetch=None):
    """Hash actual HTTP bytes, including assets selected by the served index."""
    target_require(phase in {"before", "after"}, "target_check_phase_invalid")
    target_require(target.get("target_url") == TARGET_URL, "target_url_pin_mismatch")
    fetch = fetch or fetch_target_bytes
    expected = target_receipt_core(target)
    actual = {}
    for name, pin in expected["files"].items():
        target_require(type(pin.get("bytes")) is int and 0 < pin["bytes"] <= 20 * 1024 * 1024,
                       "target_http_expected_size_invalid")
        url = TARGET_URL if name == "index.html" else urljoin(TARGET_URL, name)
        raw = fetch(url, pin["bytes"])
        target_require(isinstance(raw, bytes) and len(raw) == pin["bytes"]
                       and hashlib.sha256(raw).hexdigest() == pin["sha256"],
                       "served_target_digest_mismatch:" + name)
        if name == "index.html":
            target_require(entry_assets(raw, target["files"]) == target["entry_assets"],
                           "served_target_entry_mismatch")
        actual[name] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    return dict(expected, files=actual, phase=phase, checked_at=base.now())


def require_target_receipts(provenance, status):
    target = provenance.get("freeze", {}).get("product_target")
    target_require(isinstance(target, dict) and provenance.get("target_url") == TARGET_URL
                   and target.get("target_url") == TARGET_URL, "served_target_provenance_missing")
    expected, times = target_receipt_core(target), []
    for phase, receipt in (("before", provenance.get("target_before")), ("after", status.get("target_after"))):
        target_require(isinstance(receipt, dict) and receipt.get("phase") == phase
                       and {key: receipt.get(key) for key in expected} == expected,
                       "served_target_receipt_missing_or_changed:" + phase)
        try:
            checked = datetime.fromisoformat(receipt["checked_at"].replace("Z", "+00:00"))
            target_require(checked.tzinfo is not None, "served_target_receipt_time_invalid")
        except (KeyError, AttributeError, TypeError, ValueError) as exc:
            raise RuntimeError("served_target_receipt_time_invalid") from exc
        times.append(checked)
    target_require(times[0] <= times[1], "served_target_receipt_order_invalid")
    return dict(before_and_after_served_bytes_verified=True, **expected)


def checked_manifest_file(root, row):
    path = relative_file(root, row.get("path"))
    target_require(type(row.get("bytes")) is int and path.stat().st_size == row["bytes"]
                   and base.digest_file(path) == row.get("sha256"),
                   "target_file_digest_mismatch:" + row["path"])
    return path


def tree_files(root, *, ignored_roots=()):
    paths = set()
    for directory, dirs, files in os.walk(root, followlinks=False):
        if Path(directory) == root:
            dirs[:] = [name for name in dirs if name not in ignored_roots]
        target_require(not any((Path(directory) / name).is_symlink() for name in dirs),
                       "target_source_directory_symlink")
        paths.update((Path(directory) / name).relative_to(root).as_posix() for name in files)
    return paths


def capture_target_freeze():
    """Validate the archive itself; Git in an archive would find the QA parent."""
    target_require(BUILD.is_file() and base.digest_file(BUILD) == BUILD_SHA256,
                   "pinned_product_build_artifact_missing_or_changed")
    manifest = base.read_json(BUILD)
    target_require(manifest.get("source_commit") == PRODUCT_COMMIT
                   and manifest.get("target_url") == TARGET_URL
                   and manifest.get("source_root") == str(SOURCE.resolve())
                   and manifest.get("dist_root") == str(DIST.resolve())
                   and manifest.get("artifact") == "source/dist/index.html"
                   and not SOURCE.is_symlink() and not DIST.is_symlink(),
                   "pinned_product_target_path_or_source_mismatch")
    source_row, provenance_row = manifest.get("source_manifest", {}), manifest.get("provenance", {})
    target_require(source_row.get("path") == "source-manifest.json"
                   and source_row.get("sha256") == SOURCE_MANIFEST_SHA256
                   and provenance_row.get("path") == "build-provenance.json"
                   and provenance_row.get("sha256") == BUILD_PROVENANCE_SHA256,
                   "target_source_attestation_pin_mismatch")
    source_manifest = base.read_json(checked_manifest_file(TARGET_ROOT, source_row))
    build_provenance = base.read_json(checked_manifest_file(TARGET_ROOT, provenance_row))
    rows = source_manifest.get("files", [])
    target_require(source_manifest.get("schema_version") == "peekly-pinned-source.v1"
                   and source_manifest.get("source_commit") == PRODUCT_COMMIT
                   and source_manifest.get("source_root") == str(SOURCE.resolve())
                   and source_manifest.get("file_count") == len(rows) == SOURCE_FILE_COUNT
                   and source_manifest.get("source_tree_sha256") == SOURCE_TREE_SHA256
                   and base.digest_value(rows) == SOURCE_TREE_SHA256,
                   "target_source_manifest_invalid")
    source_paths, actual_rows = set(), []
    for row in rows:
        path = checked_manifest_file(SOURCE, row)
        target_require(row["path"] not in source_paths, "target_source_duplicate_path")
        raw = path.read_bytes()
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        target_require(git_blob == row.get("git_blob") and mode == row.get("mode"),
                       "target_archive_blob_or_mode_mismatch:" + row["path"])
        actual_rows.append(dict(path=row["path"], mode=mode, git_blob=git_blob,
                                bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
        source_paths.add(row["path"])
    # TypeScript creates this compiler cache during the recorded build. It is
    # separately frozen, never counted as an archived product source file.
    generated_metadata = {name: base.digest_file(relative_file(SOURCE, name))
        for name in ("tsconfig.tsbuildinfo",) if (SOURCE / name).exists()}
    target_require(base.digest_value(actual_rows) == SOURCE_TREE_SHA256
                   and tree_files(SOURCE, ignored_roots={"node_modules", "dist"})
                       == source_paths | set(generated_metadata),
                   "target_source_tree_changed")
    files = {}
    for row in manifest.get("assets", []):
        checked_manifest_file(DIST, row)
        target_require(row["path"] not in files, "target_dist_duplicate_path")
        files[row["path"]] = dict(bytes=row["bytes"], sha256=row["sha256"])
    target_require("index.html" in files and tree_files(DIST) == set(files)
                   and manifest.get("sha256") == files["index.html"]["sha256"] == HISTORICAL_INDEX_SHA256,
                   "target_dist_inventory_or_index_mismatch")
    entries = entry_assets((DIST / "index.html").read_bytes(), files)
    main = manifest.get("main_asset", {})
    target_require(main.get("path") in entries and main.get("path", "").endswith(".js")
                   and files.get(main.get("path")) == {key: main.get(key) for key in ("bytes", "sha256")},
                   "target_main_asset_pin_mismatch")
    prd_sha = base.digest_file(SOURCE / "docs/PRD.md")
    target_require(build_provenance.get("source_commit") == PRODUCT_COMMIT
                   and build_provenance.get("prd_sha256") == prd_sha
                   and build_provenance.get("historical_index_reproduced") is True
                   and build_provenance.get("expected_historical_index_sha256") == HISTORICAL_INDEX_SHA256,
                   "target_build_provenance_mismatch")
    return dict(target_url=TARGET_URL, build_sha256=BUILD_SHA256,
        source_root=str(SOURCE.resolve()), dist_root=str(DIST.resolve()),
        source_commit=PRODUCT_COMMIT, source_tree_sha256=SOURCE_TREE_SHA256,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256, source_file_count=len(rows),
        generated_build_metadata=generated_metadata,
        build_provenance_sha256=BUILD_PROVENANCE_SHA256, prd_sha256=prd_sha,
        files=files, entry_assets=entries, main_asset=main,
        historical_comparison=dict(source_commit_matches=True, index_bytes_match=True,
            historical_main_asset_hash_available=False,
            full_historical_dist_byte_identity="not_established"))


def validate_seed_catalog(manifest, frozen_files):
    """Verify the immutable, actual-product validation attestation offline."""
    seed = manifest.get("coverage", {}).get("legacy_seed", {})
    validation = seed.get("product_validation", {})
    raw = (json.dumps(validation, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n").encode()
    if (seed.get("schema_version") != "peekly-legacy-seed-fixture.v1"
            or seed.get("storage_key") != "peekly_state_v6"
            or seed.get("fixture_sha256") != SEED_SHA
            or seed.get("product_validation_sha256") != VALIDATION_SHA
            or hashlib.sha256(raw).hexdigest() != VALIDATION_SHA
            or seed.get("product_commit") != PRODUCT_COMMIT
            or validation.get("product_commit") != PRODUCT_COMMIT
            or validation.get("fixture_sha256") != SEED_SHA
            or any(validation.get("checks", {}).get(key) is not True for key in VALIDATION_CHECKS)
            or any(frozen_files.get(name) != sha for name, sha in PINNED_FILES.items())):
        raise RuntimeError("validated_legacy_seed_catalog_required")
    return dict(fixture_sha256=SEED_SHA, validation_sha256=VALIDATION_SHA,
                product_commit=PRODUCT_COMMIT, checks=validation["checks"])


def capture_freeze():
    value = base.capture_freeze(fixtures=FIXTURES, library=LIBRARY, build=BUILD,
                               expected_build_sha256=BUILD_SHA256)
    target_require(value["library_sha256"] == LIBRARY_SHA256, "completion_library_pin_changed")
    if value["fixtures"]["manifest_sha256"] != FIXTURE_MANIFEST_SHA:
        raise RuntimeError("completion_fixture_manifest_changed")
    manifest = base.read_json(FIXTURES / "fixture-manifest.json")
    value["legacy_seed_validation"] = validate_seed_catalog(manifest, value["fixtures"]["files"])
    for name in ("scripts/run_peekly_completion.py", "scripts/build_peekly_coverage_fixtures.py",
                 "scripts/validate_peekly_legacy_seed.mjs"):
        value["additional_sources"][name] = base.digest_file(ROOT / name)
    value["turn_policy"] = TURN_POLICY
    value["product_target"] = capture_target_freeze()
    return value


def smoke_gate(summary, report, audit, *, router_ledger_sha256=None):
    gate = base.smoke_gate(summary, report, audit,
        router_ledger_sha256=router_ledger_sha256, persona_ids=SMOKE_IDS,
        baseline_not_run=SMOKE_BASELINE_NOT_RUN, success_units=6)
    reasons = list(gate["reasons"])
    targets = []
    for pid, requirement in zip(SMOKE_IDS, ("PRD-IMPORT-SNAPSHOT-UNKNOWN", "PRD-PAYWALL-BOUNDARY")):
        rows = [row for row in report.get("tasks", []) if row.get("persona_id") == pid]
        criteria = (rows[0].get("result") or {}).get("receipt", {}).get("criteria", []) if len(rows) == 1 else []
        target = [row for row in criteria if row.get("kind") == "success" and row.get("index") == 2]
        executed = (len(target) == 1 and target[0].get("status") in ("passed", "failed")
                    and bool(target[0].get("evidence_ids")))
        targets.append(dict(persona_id=pid, requirement=requirement, executed=executed,
                            criterion=target[0] if len(target) == 1 else None))
        if not executed:
            reasons.append("target_not_exercised:" + requirement)
    if gate["success_criteria"].get("not_run") != 0:
        reasons.append("all_six_success_criteria_must_be_exercised")
    gate.update(pass_gate=not reasons, reasons=sorted(set(reasons)), targeted_flows=targets,
                baseline_commit="65f52f78918d097c39ac8eb5ec49ed6daea537bc",
                policy="Both validated UNKNOWN and PAYWALL plus all six success criteria must be exercised. N/A and uncertainty earn no credit.")
    return gate


def require_passed_smoke(smoke_root, freeze):
    status = base.read_json(smoke_root / "run-status.json")
    provenance = base.read_json(smoke_root / "input-provenance.json")
    if status.get("state") != "smoke_passed" or provenance.get("stage") != "smoke":
        raise RuntimeError("passed_completion_smoke_required")
    if status.get("input_provenance_sha256") != base.digest_file(smoke_root / "input-provenance.json"):
        raise RuntimeError("completion_smoke_provenance_changed")
    base.require_same_freeze(provenance["freeze"], freeze)
    require_target_receipts(provenance, status)
    stage = smoke_root / "stage-2"
    for name, key in (("report.json", "report_sha256"), ("stage-summary.json", "summary_sha256"),
                      ("model-router-ledger.json", "router_ledger_sha256")):
        if base.digest_file(stage / name) != status.get(key):
            raise RuntimeError("completion_smoke_evidence_changed")
    audit = base.router_delivery_audit(base.read_json(stage / "model-router-ledger.json"))
    if audit != status.get("router_delivery_audit"):
        raise RuntimeError("completion_smoke_delivery_audit_changed")
    gate = smoke_gate(base.read_json(stage / "stage-summary.json"), base.read_json(stage / "report.json"),
                      audit, router_ledger_sha256=status["router_ledger_sha256"])
    if not gate["pass_gate"]:
        raise RuntimeError("completion_smoke_gate_failed:" + ",".join(gate["reasons"]))
    return dict(run_root=str(smoke_root), gate=gate, report_sha256=status["report_sha256"],
                summary_sha256=status["summary_sha256"], router_ledger_sha256=status["router_ledger_sha256"])


async def run(args):
    root = base.owned_output(args.run_root or (DEFAULT_SMOKE if args.stage == "smoke" else DEFAULT_COHORT))
    if root.exists():
        raise RuntimeError("run_root_exists_preserved")
    ids = list(SMOKE_IDS if args.stage == "smoke" else base.ALL_IDS)
    live = base.load_live()
    with live.Library(LIBRARY) as library:
        saved = [row for row in library.list("peekly")["personas"] if row.get("reusable")]
    base.exact_personas([row["persona_id"] for row in saved], base.ALL_IDS)
    target_require(all(row.get("revision") == 1 for row in saved),
                   "completion_rebound_library_revision_mismatch")
    freeze = capture_freeze()
    prior = base.snapshot_prior_queues(ROOT / ".ux-loop")
    forbidden = sorted({row["id"] for queue in prior for row in queue["jobs"]})
    goal = ("Coverage completion " + args.stage + " " + root.name
        + ": execute the complete saved original-PRD journey on owned loopback port 4175 in a fresh isolated context. "
        "Follow every per-criterion required-step checklist and validated fixture catalog. "
        "UNKNOWN personas must seed the validated legacy state first, then import only one current snapshot "
        "and verify exclusion before importing a second known snapshot. "
        "Do not skip applicable criteria or relabel unexecuted success N/A. "
        "This is a new independent evaluation, never a retry or resume of an uncertain operation. "
        "Use only TOKENMAXX/deepseek-v4.1-flash-free, concurrency 2, zero budget; "
        "64 turns per ordinary task, up to 80 for RETENTION plus PAYWALL. "
        "No real accounts, login, payment, external destination, deployment or paid fallback.")
    build_id = "peekly-completion-" + args.stage + "-" + root.name
    build = dict(id=build_id, artifact_path=str(BUILD.resolve()), sha256=BUILD_SHA256)
    revisions = {row["persona_id"]: row["revision"] for row in saved}
    job_ids = [live.scale_job_id("peekly", pid, revisions[pid], goal, build) for pid in ids]
    base.reject_reused_jobs(job_ids, forbidden)
    smoke = require_passed_smoke(base.owned_output(args.smoke_root), freeze) if args.stage == "cohort" else None
    provenance = dict(schema_version="peekly-completion-run.v1", created_at=base.now(), stage=args.stage,
        persona_ids=ids, job_ids=job_ids, build=build, freeze=freeze, library=str(LIBRARY),
        target_url=TARGET_URL,
        fixtures=str(FIXTURES), prior_queues=prior, forbidden_job_ids=forbidden, smoke=smoke,
        route=base.MODEL, parallel=2, turns=80, turn_policy=TURN_POLICY, budget_microusd=0,
        prior_queues_opened_read_only=True, uncertain_resend_authorized=False)
    compact = dict(stage=args.stage, run_root=str(root), sessions=len(ids), prior_queues=len(prior),
        forbidden_job_ids=len(forbidden), prior_uncertain_jobs=sum(len(q["uncertain_job_ids"]) for q in prior))
    if args.check_only:
        print(json.dumps(dict(compact, state="offline_preflight_passed", turn_policy=TURN_POLICY,
            target_url=TARGET_URL, source_commit=PRODUCT_COMMIT,
            source_files=freeze["product_target"]["source_file_count"],
            library_sha256=freeze["library_sha256"],
            served_bytes_check="required_immediately_before_and_after_actual_run")), flush=True)
        return 0
    provenance["target_before"] = verify_served_target(freeze["product_target"], "before")
    root.mkdir(mode=0o700)
    base.write_json(root / "input-provenance.json", provenance)
    state = dict(compact, state="running", started_at=base.now(),
                 input_provenance_sha256=base.digest_file(root / "input-provenance.json"))
    base.write_json(root / "run-status.json", state)
    print(json.dumps(state), flush=True)
    stage_args = SimpleNamespace(run_root=root, library=LIBRARY, product_id="peekly",
        url=TARGET_URL, target="Peekly owned isolated preview on loopback port 4175; original PRD and archive source 51110f4",
        goal=goal, build_id=build_id, build_artifact=BUILD, fixtures=FIXTURES,
        node=Path(live.NODE_DEFAULT), chrome=Path(live.CHROME_DEFAULT), turns=80, forbidden_job_ids=forbidden)
    try:
        try:
            with (root / "run.log").open("x") as log, contextlib.redirect_stdout(log):
                summary = await live.run_stage(stage_args, ids, len(ids))
        finally:
            state.update(base.prior_queue_integrity(prior))
            base.require_same_freeze(freeze, capture_freeze())
            state["target_after"] = verify_served_target(freeze["product_target"], "after")
            require_target_receipts(provenance, state)
        if not state["prior_queues_unchanged"]:
            raise RuntimeError("prior_queue_snapshot_changed_preserved")
        stage = root / ("stage-" + str(len(ids)))
        report = base.read_json(stage / "report.json")
        audit = base.router_delivery_audit(base.read_json(stage / "model-router-ledger.json"))
        state.update(finished_at=base.now(), counts=report.get("counts"),
            completed_receipt_summary=report.get("completed_receipt_summary"),
            report_sha256=base.digest_file(stage / "report.json"),
            summary_sha256=base.digest_file(stage / "stage-summary.json"),
            router_ledger_sha256=base.digest_file(stage / "model-router-ledger.json"), router_delivery_audit=audit)
        if args.stage == "smoke":
            gate = smoke_gate(summary, report, audit, router_ledger_sha256=state["router_ledger_sha256"])
            base.write_json(root / "smoke-gate.json", gate)
            state.update(state="smoke_passed" if gate["pass_gate"] else "smoke_failed", gate_reasons=gate["reasons"])
            code = 0 if gate["pass_gate"] else 2
        else:
            if not audit["valid"] or audit["uncertain_resend_violations"] or summary.get("delivery_policy") != base.DELIVERY_POLICY:
                raise RuntimeError("completion_delivery_audit_failed_preserved")
            complete = report.get("completed_receipt_summary", {}).get("assessed_completed_sessions", 0)
            finished = (complete == 32 and report.get("counts", {}).get("complete") == 32
                        and audit["actual_attempt_receipts"] > 0 and audit["unsettled_guard_call_count"] == 0)
            state["state"] = "complete" if finished else "incomplete_preserved"
            code = 0 if finished else 2
        base.write_json(root / "run-status.json", state)
        print(json.dumps(dict(compact, state=state["state"], counts=state.get("counts"),
                             gate_reasons=state.get("gate_reasons"), finished_at=state["finished_at"])), flush=True)
        return code
    except Exception as exc:
        state.update(state="stopped_preserved", finished_at=base.now(), error_type=type(exc).__name__, reason=str(exc)[:240])
        base.write_json(root / "run-status.json", state)
        raise


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("smoke", "cohort"))
    parser.add_argument("--run-root", type=Path)
    parser.add_argument("--smoke-root", type=Path, default=DEFAULT_SMOKE)
    parser.add_argument("--check-only", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(run(parse_args())))
    except Exception as exc:
        print(json.dumps(dict(state="blocked_preserved", error_type=type(exc).__name__, reason=str(exc)[:240])), file=sys.stderr)
        raise SystemExit(2)
