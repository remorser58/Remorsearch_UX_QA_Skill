#!/usr/bin/env python3
"""Apply a recorded independent review to an already audited, terminal cohort.

Usage:
  PYTHONDONTWRITEBYTECODE=1 python3 review_coverage_results.py STAGE OUTPUT_DIR

Requires raw summary.json/comparison.md, criterion-review.json, and
artifact-audit.json in OUTPUT_DIR unless their explicit options are supplied.
Only reviewed-summary.json and comparison-reviewed.md are created. No SQLite
connection, queue execution, source revalidation, browser, or model is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys


class ReviewError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ReviewError(message)


def file_hash(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def safe_relative(value):
    require(isinstance(value, str) and value and "\\" not in value,
            "invalid relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute()
            and all(part not in ("", ".", "..") for part in value.split("/")),
            "unsafe relative path")
    return path.as_posix()


class Inputs:
    def __init__(self, repo, loads):
        self.repo, self.loads, self.files = repo, loads, {}

    def pin(self, path, expected=None):
        path = Path(path).resolve(strict=True)
        require(path.is_relative_to(self.repo) and path.is_file(),
                "input outside repository or not a file")
        digest, size = file_hash(path)
        reference = {"path": path.relative_to(self.repo).as_posix(),
                     "sha256": digest, "bytes": size}
        require(path not in self.files or self.files[path] == reference,
                "input changed while reading: " + reference["path"])
        if expected is not None:
            require(digest == expected.get("sha256"), "source SHA mismatch: " + reference["path"])
            if "bytes" in expected:
                require(size == expected["bytes"], "source byte count mismatch")
        self.files[path] = reference
        return reference

    def read(self, path):
        reference = self.pin(path)
        value = self.loads(Path(path).resolve(strict=True).read_bytes())
        require(isinstance(value, dict), "input JSON must be an object")
        self.pin(path, reference)
        return value, reference

    def verify_unchanged(self):
        for path, reference in self.files.items():
            require(path.exists() and file_hash(path) == (reference["sha256"], reference["bytes"]),
                    "input changed during review: " + reference["path"])


def source_index(references):
    result = {}
    for reference in references:
        require(isinstance(reference, dict), "invalid source reference")
        key = (reference.get("commit"), safe_relative(reference["path"]))
        require(key not in result, "duplicate source reference")
        require(re.fullmatch(r"[0-9a-f]{64}", reference.get("sha256", "")),
                "invalid source digest")
        result[key] = reference
    return result


def delta(after, before, keys):
    return {key: after.get(key, 0) - before.get(key, 0) for key in keys}


def outcome(criteria):
    statuses = {item["status"] for item in criteria}
    if "failed" in statuses:
        return "failed"
    if "passed" in statuses and statuses <= {"passed", "not_applicable"}:
        return "passed"
    return "inconclusive"


def key_of(criterion):
    return criterion["job_id"], criterion["kind"], criterion["index"]


PRECONDITION_CLASS = "fixture_semantics_and_judge_cross_attempt_attribution"
SEARCH_CONTROL_CLASS = "judge_search_control_mismatch"
SEARCH_EXERCISED_CLASS = "judge_search_control_mismatch_with_exercised_query"
SIZE_EXERCISED_CLASS = "judge_size_alert_evidence_omission"
DELETE_KEY_ABSENCE_CLASS = "judge_delete_key_absence_misread"
EXECUTED_RECLASSIFICATION_CLASSES = (SEARCH_EXERCISED_CLASS, SIZE_EXERCISED_CLASS, DELETE_KEY_ABSENCE_CLASS)

# These are independently inspected saved observations, not newly executed tests.
# Explicit review items are still required; this table never selects overrides.
SEARCH_EXERCISED_CASES = {
    "PER-PEEKLY-V2-026": {
        "job_id": "S-ebhioimecepninpkpdilghkk",
        "resultsha": "e95e5355eee53677ab1cd817cd0694b5e1b69381ec2d3f0af0d20770230f9beb",
        "baseline_rows_reclassified": ["NR-12", "NR-39"],
        "observation_sha256": {
            "agent-observation-5.json": "a456dd421828f520f26dc40c8ee7e8b5b09d6c89a6e52a3725ecec2ff1d6d916",
            "agent-observation-6.json": "9b0991d3099a9f4693713175021a2fe28910b9badc6c115a79f9179b96aa91f5",
            "agent-observation-7.json": "bcf826cd1cd2a4b044ddd33c079050d4a2f968fba6e8a7c7c4b8883ed9a27c83",
        },
    },
    "PER-PEEKLY-V2-027": {
        "job_id": "S-lpghnnmpbapicjbemjpnjmdk",
        "resultsha": "f87021408221ab63db3e0ab1122ae2af5793231db0322e273e4bc2fa6305d391",
        "baseline_rows_reclassified": ["NR-14"],
        "observation_sha256": {
            "agent-observation-4.json": "16db474d32fa8a52d3e89b3d7e5b31db16e28f16f1e747c17b35dc3f19741f84",
            "agent-observation-5.json": "a457ac842dd0414ccb2e878da0ea6640b1ab057c058c89cd3d1e656dec67459b",
            "agent-observation-6.json": "d4e6f437c492b6539c7dd89e6ea5d2dabf0ca7fef18414680f1ad374361ab016",
        },
    },
    "PER-PEEKLY-V2-028": {
        "job_id": "S-kaknpddcajkpeekbgjeiahmd",
        "resultsha": "be73f02056ee27e56e17a3bb1648f798adf1c307cb08b7552d617500b112c5db",
        "baseline_rows_reclassified": [],
        "observation_sha256": {
            "agent-observation-6.json": "06bb32ab885c560cfd049495d9d4562068bba08f7be21d33b7a7f36e9b0704bd",
            "agent-observation-7.json": "8e3a59024d898e1154c9830cfe1c29769b235c969db2ae9c11f6ecca1777892c",
            "agent-observation-8.json": "def0e0a6b4c9f277c0e2dc1eae1254cf73d82fd25d280260bfed2c7ed9a627d4",
        },
    },
}
SEARCH_EXERCISED_SCOPE = {
    "evidence_basis": "independent inspection of saved, registered observations; this aggregator verifies identity and bytes",
    "fixture_sha256": "c1901b1151716053a5fc31ec9eb9dee7d51cbb3c665dbf8d7607849fdea8e6e2",
    "query_sha256": "cf12574baf4b6af9bc8ac4133367ad0e89ab059a2f32775053d92e6624c30dd5",
    "claims_bound_to_observation_hashes": [
        "actual fixture import with the same import attempt and persisted storage across list and type observations",
        "twelve exact sorted synthetic row keys before search; visible enabled current input[type=search]",
        "one actual type event, expected and actual query hashes equal, retained=true",
        "one exact matching row after filtering",
    ],
    "baseline_execution_credit_delta": 0,
    "session_outcomes_unchanged": True,
    "delete_criteria_preserved": True,
    "delete_scope_note": "The stored DELETE failure concerns the PRD final-key-removal contract; an empty reset key is not evidence of retained relationship data.",
}


SIZE_EXERCISED_CASE = {
    "persona_id": "PER-PEEKLY-V2-015", "job_id": "S-eoddcjbgpjchiikdllkckjcf",
    "resultsha": "798bc8a0fec90b2f6a02ce180af3b660507b077da13eb3177042c70fb761ae49",
    "observation_sha256": {
        "agent-observation-4.json": "de8489aafa25076aabee5840d313c1a035cbd81815a0570c64d3a72fde494ac9",
        "agent-observation-8.json": "b368a85c54e307f2a72e16866c0bf94168424d88faa390fbb896a5e0a7905dd5",
        "agent-observation-9.json": "7dd60383d2cc6363038017f1c0e08b01044a0651ae36d5c1068df1c8dc7c9fca",
        "agent-observation-10.json": "e766c4a990bbe71a8ee893fbece079d6efb07f7a2ae41569c9f7d91a25d23a00",
        "agent-observation-26.json": "08b91aef18464a40ed30472c42fec14fb6ab69e6b3f4d78d1a84f59ae2207f91",
    },
}
SIZE_EXERCISED_SCOPE = {
    "evidence_basis": "independent inspection of saved observations, receipt artifacts, fixture bytes, and pinned parser source",
    "storage_sha256": "7509f5e365a5c4dbac83578292fc66d42fd0a2599a4fd3adba698f9117d09730",
    "fixture_root": ".ux-loop/peekly-coverage-fixtures-v7-20261114",
    "manifest_sha256": "4df650d58c2105bc67ca3eec27c826b1f8129f8f1a846b396a4eb9e53c48f44a",
    "groups": {
        "peekly-loose-file-over": ["loose-file-over-32mib.json"],
        "peekly-loose-total-over": ["loose-total-a.json", "loose-total-b.json", "loose-total-c.json"],
    },
    "files": {
        "peekly-oversize-plus-one.zip": {"bytes": 134217729, "sha256": "7ea6ce492b9f2e83db0190808df466a16da53a11f25ba786f46c26821243c687"},
        "loose-file-over-32mib.json": {"bytes": 33554433, "sha256": "731c45e3c9c8745df747dd8681fcc66ee441a74a2c1b105e83ea7429b1a50f36"},
        "loose-total-a.json": {"bytes": 23068672, "sha256": "3ff845206ecc527b793b7133d1cc70aaf0991f2c753c69f17a5498c0861336ac"},
        "loose-total-b.json": {"bytes": 23068672, "sha256": "d653c362855eadd8c8ede2dc66856356c60dae1be25d4a8c64c384a187634ffb"},
        "loose-total-c.json": {"bytes": 23068672, "sha256": "ccef47ec2ff27446d89887df6d44f1e434d256612ff98e6988166aef1503ba93"},
    },
    "claims_bound_to_observation_hashes": [
        "obs-4 persisted a valid current baseline; obs-8/9/10 each show the corresponding 128MB/32MB/64MB rejection",
        "each size attempt preserves the baseline digest before and after; obs-26 repeats the 32MB rejection",
        "the loose aggregate is 66MiB; its import_attempt.fixture_sha256 is null, so binding uses the named manifest group and member hashes",
        "the ZIP is structurally unreadable, but pinned product 51110f4 zipParser.ts checks the 128MiB boundary before archive structure",
        "native checks omit SIZE; the raw failed explanation contradicts its own cited size alerts",
    ],
    "baseline_execution_credit_delta": 0, "session_outcomes_unchanged": True,
    "save_failure_criterion_preserved": True,
}


DELETE_KEY_ABSENCE_CASE = {
    "persona_id": "PER-PEEKLY-V2-025", "job_id": "S-lienlcpnibobddnaaekmmami",
    "resultsha": "65a77074cd29788022599df8d446d67c879313d0dcc9f03e9dd61e4ada4aa81a",
    "baseline_rows_reclassified": ["NR-38"],
    "observation_sha256": {
        "agent-observation-1.json": "db6056ba24042a41f89834ebf6bc6c980891b9f10d9b4e3ba149e8f499984b50",
        "agent-observation-5.json": "e7a4dd839707a55760eec63137de5f0627ebf4225e3766de2356d50058740a83",
        "agent-observation-12.json": "13a58570b6d0941b79947fc6a55337f6130dfc30a8cb064daed54eab78858ee8",
        "agent-observation-13.json": "41d1e52575ee1385feea1cb8d0466e9fc8bf805b5615f7b4cc5037c389fc8676",
        "agent-observation-14.json": "22bd27837ad52631c6ed75c5dd7281cf91bc49ee844fb88f66eb9934e6afe00a",
        "agent-observation-15.json": "9c24e8c6ef6141f2ffe8809d70aac4cb72364ef65d20ebf55a848b13762763ee",
    },
}
DELETE_KEY_ABSENCE_SCOPE = {
    "evidence_basis": "independent inspection of all fifteen saved observations and thirty registered artifacts",
    "contract": "pinned product 51110f4 PRD section 10 requires removal of local state keys, including current v7",
    "initial_and_final_storage_sha256": "7b3f3a770f0ac89471a660ccfe9a54f5de96b387ebb22d307e06fadb84f77355",
    "imported_storage_sha256": "29fe25eff90e28f1882b2fe1b7265005a4bc884e30b56c1ce70c23af42f6df70",
    "claims_bound_to_observation_hashes": [
        "obs-14 opens confirmation and exposes an enabled visible final erase control",
        "obs-15 final erase click is dispatched with hit_test=true and produces the completion message",
        "the final saved observation still contains peekly_state_v7 with the initial empty-state digest",
        "the evidence establishes key-absence failure, not retention of imported relationship data",
    ],
    "baseline_execution_credit_delta": 0,
    "raw_session_outcome": "failed", "intermediate_without_delete_review": "inconclusive",
    "fully_reviewed_session_outcome": "failed",
}


def verify_size_fixture_inputs(inputs):
    scope = SIZE_EXERCISED_SCOPE
    root = inputs.repo / safe_relative(scope["fixture_root"])
    manifest, reference = inputs.read(root / "fixture-manifest.json")
    require(reference["sha256"] == scope["manifest_sha256"], "SIZE proof fixture manifest differs")
    rows = {row["name"]: row for row in manifest["files"]}
    require(len(rows) == len(manifest["files"]), "duplicate fixture manifest names")
    for name, members in scope["groups"].items():
        require(manifest["groups"].get(name) == members, "SIZE proof group membership differs")
    sources = [reference]
    for name, expected in scope["files"].items():
        require(name in rows and all(rows[name].get(key) == value for key, value in expected.items()),
                "SIZE proof manifest member differs")
        sources.append(inputs.pin(root / safe_relative(name), expected))
    return sources


def baseline_change_rows(item):
    exercised = item.get("classification") in EXECUTED_RECLASSIFICATION_CLASSES
    name = "baseline_rows_reclassified" if exercised else "baseline_rows_excluded"
    other = "baseline_rows_excluded" if exercised else "baseline_rows_reclassified"
    rows = item.get(name)
    require(isinstance(rows, list) and all(isinstance(row, str) and row for row in rows)
            and len(rows) == len(set(rows)) and item.get(other, []) == [],
            "invalid or ambiguous baseline change declaration")
    return rows


def execution_reclassification(item):
    transition = item.get("oldstatus"), item.get("newstatus")
    if item.get("classification") == DELETE_KEY_ABSENCE_CLASS:
        return transition == ("passed", "failed")
    return item.get("classification") in (SEARCH_EXERCISED_CLASS, SIZE_EXERCISED_CLASS) and transition == ("failed", "passed")


def review_groups(review):
    """Preserve fourteen fixed decisions; admit only explicit, evidence-bound cases."""
    require(isinstance(review.get("changes"), list), "review changes must be a list")
    base, extra, search, exercised, size, deletion = [], [], [], [], [], []
    expected_signatures = set()
    for number in (17, 18, 19, 20):
        for index, suffix in enumerate(("RECIPROCITY", "REVERSE", "MUTUAL")):
            expected_signatures.add(("PER-PEEKLY-V2-" + str(number).zfill(3), "success", index,
                                     "PRD-RESULT-" + suffix, "passed", "not_run", "task_and_judge_scope"))
    for index, suffix in ((1, "HTML"), (2, "ACCOUNT")):
        expected_signatures.add(("PER-PEEKLY-V2-011", "success", index, "PRD-IMPORT-" + suffix,
                                 "not_run", "passed", "judge_rejection_phrase_mismatch"))
    actual_signatures = []
    for item in review["changes"]:
        require(isinstance(item, dict), "invalid review item")
        baseline_change_rows(item)
        if item.get("classification") == PRECONDITION_CLASS:
            require(item.get("requirement_id") == "PRD-IMPORT-SNAPSHOT-UNKNOWN"
                    and item.get("kind") == "success" and type(item.get("index")) is int
                    and item.get("oldstatus") in ("passed", "failed")
                    and item.get("newstatus") == "not_run", "unsupported precondition correction")
            extra.append(item)
        elif item.get("classification") == SEARCH_CONTROL_CLASS:
            require(item.get("requirement_id") == "PRD-RESULT-SEARCH"
                    and item.get("persona_id") in {"PER-PEEKLY-V2-" + str(n).zfill(3) for n in range(25, 29)}
                    and item.get("kind") == "success" and type(item.get("index")) is int
                    and item["index"] == 0 and item.get("oldstatus") == "failed"
                    and item.get("newstatus") == "not_run", "unsupported search-control correction")
            search.append(item)
        elif item.get("classification") == SEARCH_EXERCISED_CLASS:
            case = SEARCH_EXERCISED_CASES.get(item.get("persona_id"))
            require(case is not None and item.get("requirement_id") == "PRD-RESULT-SEARCH"
                    and item.get("kind") == "success" and type(item.get("index")) is int
                    and item["index"] == 0 and item.get("oldstatus") == "failed"
                    and item.get("newstatus") == "passed", "unsupported exercised-search correction")
            require(item.get("job_id") == case["job_id"] and item.get("resultsha") == case["resultsha"]
                    and set(item.get("evidencefiles", [])) >= set(case["observation_sha256"])
                    and sorted(baseline_change_rows(item)) == sorted(case["baseline_rows_reclassified"]),
                    "exercised-search case differs from independently inspected evidence")
            exercised.append(item)
        elif item.get("classification") == SIZE_EXERCISED_CLASS:
            case = SIZE_EXERCISED_CASE
            require(item.get("persona_id") == case["persona_id"] and item.get("job_id") == case["job_id"]
                    and item.get("resultsha") == case["resultsha"]
                    and item.get("requirement_id") == "PRD-IMPORT-SIZE" and item.get("kind") == "success"
                    and type(item.get("index")) is int and item["index"] == 1
                    and item.get("oldstatus") == "failed" and item.get("newstatus") == "passed"
                    and set(item.get("evidencefiles", [])) >= set(case["observation_sha256"])
                    and baseline_change_rows(item) == [], "unsupported or unbound SIZE correction")
            size.append(item)
        elif item.get("classification") == DELETE_KEY_ABSENCE_CLASS:
            case = DELETE_KEY_ABSENCE_CASE
            require(item.get("persona_id") == case["persona_id"] and item.get("job_id") == case["job_id"]
                    and item.get("resultsha") == case["resultsha"]
                    and item.get("requirement_id") == "PRD-PRIVACY-DELETE" and item.get("kind") == "success"
                    and type(item.get("index")) is int and item["index"] == 2
                    and item.get("oldstatus") == "passed" and item.get("newstatus") == "failed"
                    and set(item.get("evidencefiles", [])) >= set(case["observation_sha256"])
                    and sorted(baseline_change_rows(item)) == case["baseline_rows_reclassified"],
                    "unsupported or unbound DELETE key-absence correction")
            deletion.append(item)
        else:
            signature = tuple(item.get(key) for key in
                              ("persona_id", "kind", "index", "requirement_id", "oldstatus", "newstatus", "classification"))
            require(signature in expected_signatures, "original review decision differs")
            actual_signatures.append(signature)
            base.append(item)
    require(len(base) == 14 and set(actual_signatures) == expected_signatures,
            "original fourteen review decisions must be preserved exactly")
    groups = [("base", base), ("precondition", extra), ("search_control", search),
              ("search_exercised", exercised), ("size", size), ("delete_key_absence", deletion)]
    job_sets = [(name, {item["job_id"] for item in group}) for name, group in groups]
    for i, (left_name, left) in enumerate(job_sets):
        for right_name, right in job_sets[i + 1:]:
            allowed = ({DELETE_KEY_ABSENCE_CASE["job_id"]}
                       if {left_name, right_name} == {"search_control", "delete_key_absence"} else set())
            require(left.intersection(right) <= allowed, "unreviewed same-session group interaction")
    if deletion:
        paired_search = [item for item in search if item["job_id"] == DELETE_KEY_ABSENCE_CASE["job_id"]]
        require(len(paired_search) == 1, "DELETE correction requires its explicit paired search correction")
    require(review["expected_relationship_scope_effect"] == {
        "criterion_passed_to_not_run": 12, "session_passed_to_inconclusive": 4,
        "baseline_weighted_rows_excluded": 9, "baseline_unique_persona_requirement_keys_excluded": 7},
        "original scope expectations differ")
    require(review["expected_rejection_phrase_effect"] == {
        "criterion_not_run_to_passed": 2, "session_inconclusive_to_passed": 1, "baseline_46_effect": 0},
        "original rejection expectations differ")
    extra_counts = Counter(item["oldstatus"] for item in extra)
    extra_rows = [identifier for item in extra for identifier in item["baseline_rows_excluded"]]
    require(len(extra_rows) == len(set(extra_rows)), "duplicate precondition baseline row")
    if extra or "expected_unknown_precondition_effect" in review:
        declared = review["expected_unknown_precondition_effect"]
        require(declared.get("criterion_failed_to_not_run") == extra_counts["failed"]
                and declared.get("criterion_passed_to_not_run") == extra_counts["passed"]
                and sorted(declared.get("baseline_rows_excluded", [])) == sorted(extra_rows),
                "additional precondition expectations differ from review items")
    search_rows = [identifier for item in search for identifier in item["baseline_rows_excluded"]]
    require(len(search_rows) == len(set(search_rows)), "duplicate search-control baseline row")
    if search or "expected_search_control_effect" in review:
        declared = review["expected_search_control_effect"]
        require(declared.get("criterion_failed_to_not_run") == len(search)
                and declared.get("criterion_failed_to_passed", 0) == 0
                and sorted(declared.get("baseline_rows_excluded", [])) == sorted(search_rows),
                "search-control expectations differ from explicit review items")
    if exercised or "expected_search_exercised_effect" in review:
        declared = review["expected_search_exercised_effect"]
        require(declared.get("criterion_failed_to_passed") == len(exercised)
                and declared.get("baseline_46_execution_credit_delta") == 0,
                "exercised-search expectations differ from explicit review items")
    if size or "expected_size_exercised_effect" in review:
        declared = review["expected_size_exercised_effect"]
        require(declared.get("criterion_failed_to_passed") == len(size) <= 1
                and declared.get("baseline_46_execution_credit_delta") == 0,
                "SIZE expectations differ from explicit review item")
    if deletion or "expected_delete_key_absence_effect" in review:
        declared = review["expected_delete_key_absence_effect"]
        require(declared.get("criterion_passed_to_failed") == len(deletion) <= 1
                and declared.get("baseline_46_execution_credit_delta") == 0,
                "DELETE expectations differ from explicit review item")
    return base, extra, search, exercised, size, deletion


def expected_effect(changes, candidate, mapping, reporter):
    """Derive an independent delta from pinned decisions and immutable raw ledgers."""
    effect = {
        "criteria_all": dict.fromkeys(reporter.CRITERIA, 0),
        "criteria_by_kind": {kind: dict.fromkeys(reporter.CRITERIA, 0) for kind in ("success", "recovery")},
        "session_outcomes": dict.fromkeys(reporter.OUTCOMES, 0),
        "baseline_weighted": dict.fromkeys(reporter.MAPPING, 0),
        "baseline_unique": dict.fromkeys(reporter.MAPPING, 0),
    }
    overrides = {key_of(item): item for item in changes}
    require(len(overrides) == len(changes), "duplicate expected criterion override")
    originals = {key_of(item): item for item in candidate["criteria"]}
    raw_rows = {row["baseline_id"]: row for row in mapping["weighted_rows"]}
    used_rows, unique_rows, expected_sessions = set(), {}, {}
    for item in changes:
        key, old, new = key_of(item), item["oldstatus"], item["newstatus"]
        require(key in originals and originals[key]["status"] == old,
                "expected change does not match an assessed raw criterion")
        for vector in (effect["criteria_all"], effect["criteria_by_kind"][item["kind"]]):
            vector[old] -= 1
            vector[new] += 1
        for identifier in baseline_change_rows(item):
            require(identifier in raw_rows and identifier not in used_rows, "unknown/duplicate expected baseline row")
            used_rows.add(identifier)
            row = raw_rows[identifier]
            require(row["status"] == old
                    and (new == "not_run" or execution_reclassification(item))
                    and row["persona_id"] == item["persona_id"] and row["requirement_id"] == item["requirement_id"]
                    and len(row["candidate_criteria"]) == 1 and key_of(row["candidate_criteria"][0]) == key,
                    "expected baseline transition is not bound to the raw criterion")
            effect["baseline_weighted"][old] -= 1
            effect["baseline_weighted"][new] += 1
            unique_key = row["persona_id"], row["requirement_id"]
            require(unique_key not in unique_rows or unique_rows[unique_key] == (old, new),
                    "inconsistent expected unique baseline transition")
            unique_rows[unique_key] = (old, new)
    for old, new in unique_rows.values():
        effect["baseline_unique"][old] -= 1
        effect["baseline_unique"][new] += 1
    affected_jobs = {item["job_id"] for item in changes}
    for session in candidate["sessions"]:
        if session["job_id"] not in affected_jobs:
            continue
        require(session["outcome"] == outcome(session["criteria"]), "raw reviewed session outcome inconsistent")
        statuses = [{"status": overrides[key_of(c)]["newstatus"] if key_of(c) in overrides else c["status"]}
                    for c in session["criteria"]]
        old, new = session["outcome"], outcome(statuses)
        expected_sessions[session["job_id"]] = (old, new)
        effect["session_outcomes"][old] -= 1
        effect["session_outcomes"][new] += 1
    require(set(expected_sessions) == affected_jobs, "expected reviewed session is not assessed")
    return effect, expected_sessions


def crosscheck_candidate(candidate, reporter):
    aggregate = reporter._aggregate_sessions(candidate["sessions"])
    expected = {
        "assessed_completed_sessions": aggregate["completed_sessions"],
        "distinct_assessed_personas": aggregate["distinct_completed_personas"],
        "session_outcomes": aggregate["session_outcomes"],
        "criteria_all": aggregate["criteria_all"],
        "criteria_by_kind": aggregate["criteria_by_kind"],
    }
    for field, value in expected.items():
        require(candidate[field] == value, "candidate aggregate mismatch: " + field)
    flattened = [c for session in candidate["sessions"] for c in session["criteria"]]
    require(flattened == candidate["criteria"], "session/criterion ledgers differ")
    require(len({key_of(c) for c in flattened}) == len(flattened), "duplicate criterion")
    require(sum(candidate["session_outcomes"].values()) == len(candidate["sessions"]),
            "session total mismatch")
    require(sum(candidate["criteria_all"].values()) == len(flattened), "criterion total mismatch")
    for status in reporter.CRITERIA:
        require(candidate["criteria_all"][status] ==
                sum(candidate["criteria_by_kind"][kind][status] for kind in ("success", "recovery")),
                "success/recovery totals differ")
    require(candidate["host_protocol"]["assessed_completed"] ==
            aggregate["host_protocol_on_completed_receipts"], "host_protocol changed")
    require(candidate["failures"] == [c for c in flattened if c["status"] == "failed"],
            "failure list mismatch")
    require(candidate["not_run_by_requirement"] == reporter._not_run_by_requirement(flattened),
            "not_run groups mismatch")


def verify_artifact_audit(audit, tasks, candidate, stage, inputs, digest):
    """Bind the prior whole-receipt byte audit; rehash review citations separately."""
    require(audit.get("schema_version") == "peekly-artifact-byte-audit.v1"
            and audit.get("audit_passed") is True and audit.get("mismatches") == 0
            and audit.get("source_files_unchanged") is True, "artifact audit is not successful")
    require(audit.get("stage") == stage.relative_to(inputs.repo).as_posix(), "audit stage differs")
    require(all(audit.get(key) == 0 for key in ("new_model_calls", "new_browser_calls", "queue_writes")),
            "artifact audit records live work")
    audit_jobs = {job["job_id"]: job for job in audit["jobs"]}
    assessed_ids = {session["job_id"] for session in candidate["sessions"]}
    require(len(audit_jobs) == len(audit["jobs"]) and set(audit_jobs) == assessed_ids,
            "artifact audit assessed job set differs")
    require(audit["assessed_sessions"] == candidate["assessed_completed_sessions"],
            "artifact audit denominator differs")
    require({k: v for k, v in audit["queue_counts"].items() if v} ==
            {k: v for k, v in candidate["queue_counts"].items() if v}, "audit queue counts differ")
    require({row["job_id"] for row in audit["excluded_attempts"]} ==
            {row["job_id"] for row in candidate["unassessed_attempts"]},
            "artifact audit excluded job set differs")
    registered_by_job, physical_files = {}, {}
    kinds, reference_count = Counter(), 0
    sessions_root = (stage / "sessions").resolve(strict=True)
    require(sessions_root.is_relative_to(stage), "sessions directory escapes stage")
    for job_id in sorted(assessed_ids):
        task, saved = tasks[job_id], audit_jobs[job_id]
        result, receipt = task["result"], task["result"]["receipt"]
        require(saved["persona_id"] == task["persona_id"]
                and saved["result_sha256"] == task["result_sha256"] == digest(result),
                "artifact audit result binding differs: " + job_id)
        require(saved["first_judgment_sha256"] == result["first_judgment_sha256"]
                == digest(result["first_judgment"]), "first judgment binding differs")
        require(saved["all_registered_artifacts_checked"] is True, "partial artifact audit")
        session_root = (sessions_root / safe_relative(job_id)).resolve(strict=True)
        evidence_root = (session_root / "evidence" / safe_relative(job_id) / "1").resolve(strict=True)
        require(session_root.is_relative_to(sessions_root)
                and evidence_root.is_relative_to(session_root), "evidence directory escapes stage")
        by_path, ids, manifest = {}, set(), []
        for artifact in receipt["artifacts"]:
            relative = safe_relative(artifact["path"])
            real = (session_root / relative).resolve(strict=True)
            require(real.is_relative_to(evidence_root) and real.is_file(), "artifact containment failed")
            require(artifact["id"] not in ids and relative not in by_path, "duplicate artifact identity/path")
            require(artifact["kind"] in ("execution_log", "screenshot")
                    and re.fullmatch(r"[0-9a-f]{64}", artifact["sha256"]), "invalid artifact metadata")
            ids.add(artifact["id"])
            by_path[relative] = artifact
            size = real.stat().st_size
            require(size > 0, "empty artifact")
            manifest.append({"path": relative, "sha256": artifact["sha256"], "bytes": size})
            record = (artifact["sha256"], size)
            require(real not in physical_files or physical_files[real] == record,
                    "inconsistent physical artifact metadata")
            physical_files[real] = record
            kinds[artifact["kind"]] += 1
            reference_count += 1
        require(saved["registered_artifacts"] == len(manifest)
                and saved["artifact_manifest_sha256"] == digest(sorted(manifest, key=lambda row: row["path"])),
                "audited artifact manifest differs: " + job_id)
        registered_by_job[job_id] = (session_root, evidence_root, by_path)
    require(audit["registered_artifact_references"] == reference_count
            and audit["distinct_artifact_files"] == len(physical_files)
            and audit["artifact_bytes"] == sum(record[1] for record in physical_files.values())
            and audit["artifact_kinds"] == dict(kinds), "whole-receipt artifact totals differ")
    return registered_by_job


def reviewed_markdown(summary, reporter):
    body = reporter.render_markdown(summary)
    body = body.replace("# Peekly coverage comparison",
                        "# Peekly coverage comparison — 독립 증거 감사", 1)
    body = body.replace("summary.json의 not_run_by_requirement",
                        "reviewed-summary.json의 candidate.not_run_by_requirement")
    audit = summary["independent_review"]
    d = audit["delta"]
    extras = [item for item in audit["changes"] if item["classification"] == PRECONDITION_CLASS]
    extra_counts = Counter(item["oldstatus"] for item in extras)
    search = [item for item in audit["changes"] if item["classification"] == SEARCH_CONTROL_CLASS]
    exercised = [item for item in audit["changes"] if item["classification"] == SEARCH_EXERCISED_CLASS]
    size = [item for item in audit["changes"] if item["classification"] == SIZE_EXERCISED_CLASS]
    deletion = [item for item in audit["changes"] if item["classification"] == DELETE_KEY_ABSENCE_CLASS]
    session_counts = Counter((item["oldstatus"], item["newstatus"]) for item in audit["session_changes"])
    lines = [
        "## 원본 판정과 증거 감사의 차이", "",
        "첫 세 비교 열은 원본과 같습니다. 네 번째 열 '신규32명·증거감사'는 같은 완료·평가 세션에만 명시된 판정 변경을 적용합니다.",
        "raw summary.json, comparison.md, 원본 receipt·checkpoint는 보존했습니다. 새로운 관측·모델·브라우저 실행은 없습니다.",
        "목록에 없는 판정, 원본 N/A, 불확실·미평가 시도는 변경하거나 실행 성과로 인정하지 않았습니다.", "",
        "| 집계 | 통과 변화 | 실패 변화 | 미실행/미결론 변화 | N/A/미평가 변화 |",
        "|---|---:|---:|---:|---:|",
        "| 전체 기준 | {passed:+d} | {failed:+d} | {not_run:+d} | {not_applicable:+d} |".format(**d["criteria_all"]),
        "| 세션 | {passed:+d} | {failed:+d} | {inconclusive:+d} | 0 |".format(**d["session_outcomes"]),
        "| baseline 46행 | {passed:+d} | {failed:+d} | {not_run:+d} | {unassessed:+d} |".format(**d["baseline_weighted"]),
        "| baseline 고유 조합 | {passed:+d} | {failed:+d} | {not_run:+d} | {unassessed:+d} |".format(**d["baseline_unique"]),
        "",
        "기존 14개 검토 항목은 그대로 보존했습니다. 관계 목록 범위 혼동 12건은 PASS→미실행, 실제 파일 거절 증거를 놓친 2건은 미실행→PASS입니다.",
        "이 14개 항목만의 효과는 세션 PASS −3 / 미결론 +3, baseline 9행·고유 조합 7개 PASS→미실행입니다.",
        "추가 UNKNOWN 선행조건 검토 " + str(len(extras)) + "건은 PASS→미실행 " + str(extra_counts["passed"])
        + "건, 실패→미실행 " + str(extra_counts["failed"]) + "건입니다. 알려진 빈 목록은 알 수 없는 과거 형식의 전제를 충족하지 않으므로 실행 감소 성과를 추가하지 않습니다.",
        "검색 컨트롤 문구 오판으로 별도 확인된 " + str(len(search))
        + "건은 실패→미실행입니다. 입력·필터 동작을 실행하지 않은 개별 사례만 적용하며 검색 PASS를 만들거나 다른 페르소나에 일괄 적용하지 않습니다.",
        "실제 검색 실행이 별도로 검증된 " + str(len(exercised))
        + "건은 실패→PASS입니다. 같은 가져오기·저장 상태에서 정렬된 12행, 활성 검색 입력, query SHA 일치와 유지, 정확한 1행 필터 결과가 고정 증거에 있습니다.",
        "이 검색 PASS 보정은 원래도 실행된 실패의 판정 변경이므로 baseline 실행 성과 변화는 0입니다. 해당 세션 결과와 DELETE 기준도 유지했습니다.",
        "별도로 확인한 SIZE " + str(len(size))
        + "건은 실패→PASS입니다. 정상 저장 기준과 실제 크기 초과 fixture, 128MB·32MB·64MB 거절 안내, 시도별 저장 digest 유지 증거를 결합했습니다.",
        "SIZE 보정도 기존 실패의 재분류이며 미실행 감소를 추가하지 않습니다. SAVE-FAIL 실패와 세션 실패를 유지했고, 구조상 읽을 수 없는 ZIP의 용량 검사가 구조 검사보다 먼저 실행되는 범위를 명시했습니다.",
        "삭제 키 부재 조건을 다시 확인한 " + str(len(deletion))
        + "건은 PASS→실패입니다. 실제 최종 확인 뒤 빈 초기 상태의 v7 키가 남은 증거이며, 가져온 관계 데이터가 남았다는 주장이 아닙니다.",
        "025의 SEARCH와 DELETE는 같은 세션이므로 원본→전체 보정 결과를 함께 계산했습니다. SEARCH만 반영한 중간 미결론에서 DELETE가 실패를 복원하는 상호작용을 별도 기록하며 그룹별 세션 변화를 단순 합산하지 않습니다.",
        "전체 세션 전이: " + ", ".join(old + "→" + new + " " + str(count) + "건"
                                               for (old, new), count in sorted(session_counts.items())) + ".",
        "위 표의 전체 변화는 원본 집계와 SHA로 고정한 검토 항목에서 각각 계산해 대조했습니다. 반복 baseline 행의 가중치도 보존합니다.",
        "",
        "## 독립 변경 원장", "",
    ]
    for change in audit["changes"]:
        lines += [
            "### " + change["persona_id"] + " / " + change["requirement_id"], "",
            "- 판정: " + change["oldstatus"] + " → " + change["newstatus"]
            + "; 분류: " + change["classification"] + "; 심각도: " + change["severity"],
            "- 검토 사유: " + change["reason"],
            "- 원본 판정 위치: " + change["raw_report_source"]["path"] + " :: "
            + change["raw_criterion"]["report_selector"],
            "- 원본 result SHA-256: " + change["resultsha"],
            "- 변경 지시: " + change["review_source"]["path"] + " :: " + change["review_source"]["selector"],
            "- 등록·바이트 확인 증거: " + ", ".join(item["path"] for item in change["review_evidence"]), "",
        ]
    lines += [
        "## 검증 범위", "",
        "raw 집계와 baseline 대응을 원본 report/plan으로 재계산했고, 선행 전체 artifact 감사의 입력 SHA와 job/result/manifest 결합을 확인했습니다.",
        "변경 항목이 인용한 관측 JSON과 선택적 화면 증거는 등록 SHA와 실제 바이트를 다시 비교했습니다. 나머지 artifact의 바이트 판정은 명시된 선행 artifact 감사 시점의 결과입니다.",
        "이 파일은 별도 보고서 집계이며 유효한 새 실행 receipt를 만들거나 원본 receipt를 다시 봉인하지 않습니다.", "",
    ]
    return body.rstrip() + "\n\n" + "\n".join(lines)


def create_outputs(destination, contents, verify):
    paths = [destination / name for name, _ in contents]
    require(not any(os.path.lexists(path) for path in paths), "reviewed output already exists")
    streams, created = [], []
    try:
        for path in paths:
            stream = path.open("x", encoding="utf-8")
            streams.append(stream)
            created.append(path)
        for stream, (_, content) in zip(streams, contents):
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        verify()
    except BaseException:
        for stream in streams:
            stream.close()
        for path in created:
            path.unlink()
        raise
    finally:
        for stream in streams:
            stream.close()


def build_reviewed(repo, stage, destination, raw_path, review_path, audit_path):
    repo, stage = Path(repo).resolve(strict=True), Path(stage).resolve(strict=True)
    require(stage.is_relative_to(repo), "stage outside repository")
    destination = Path(destination)
    require(not destination.is_symlink() and destination.is_dir(), "output directory must already exist")
    destination = destination.resolve(strict=True)
    require(destination.is_relative_to(repo) and not destination.is_relative_to(stage),
            "output directory outside repository or inside immutable stage")
    require(not any(os.path.lexists(destination / name)
                    for name in ("reviewed-summary.json", "comparison-reviewed.md")), "reviewed output exists")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(repo / "skills/remorsearch-ux-qa"))
    sys.path.insert(0, str(repo / "scripts"))
    from uxresearch.canonical import digest, loads
    import report_peekly_coverage as reporter
    inputs = Inputs(repo, loads)
    for path in (Path(__file__), repo / "scripts/report_peekly_coverage.py",
                 repo / "scripts/run_peekly_coverage.py",
                 repo / "skills/remorsearch-ux-qa/uxresearch/canonical.py"):
        inputs.pin(path)
    raw, raw_ref = inputs.read(raw_path)
    review, review_ref = inputs.read(review_path)
    audit, audit_ref = inputs.read(audit_path)
    raw_markdown_path = Path(raw_path).parent / "comparison.md"
    inputs.pin(raw_markdown_path)
    require(raw.get("schema_version") == "peekly-coverage-comparison.v1", "unknown raw summary schema")
    require(review.get("schema_version") == "peekly-independent-criterion-review.v1", "unknown review schema")
    base_changes, extra_changes, search_changes, exercised_changes, size_changes, delete_changes = review_groups(review)
    require(review.get("raw_receipts_modified") is False
            and review.get("new_model_calls") == review.get("new_browser_calls") == 0,
            "review must preserve raw receipts and record no live calls")
    stage_name = stage.relative_to(repo).as_posix()
    require(review["stage_root"] == stage_name
            and review["evidence_base_format"] == "{stage_root}/sessions/{job_id}/evidence/{job_id}/1/",
            "review stage/evidence format mismatch")
    raw_sources, audit_sources = source_index(raw["sources"]), source_index(audit["sources"])
    for source in list(raw_sources.values()) + list(audit_sources.values()):
        if "commit" not in source:
            inputs.pin(repo / safe_relative(source["path"]), source)
    required_audit_paths = [stage / name for name in
                            ("queue.sqlite", "report.json", "plan.json", "stage-summary.json", "model-router-ledger.json")]
    required_audit_paths += [stage.parent / "run-status.json", stage.parent / "input-provenance.json"]
    for path in required_audit_paths:
        require((None, path.relative_to(repo).as_posix()) in audit_sources, "audit source binding missing")
    wal = stage / "queue.sqlite-wal"
    audited_wal_exists = (None, wal.relative_to(repo).as_posix()) in audit_sources
    require(wal.exists() == audited_wal_exists, "WAL presence differs from byte audit")
    report, report_ref = inputs.read(stage / "report.json")
    envelope, plan_ref = inputs.read(stage / "plan.json")
    stage_summary, stage_ref = inputs.read(stage / "stage-summary.json")
    ledger, ledger_ref = inputs.read(stage / "model-router-ledger.json")
    run_status, status_ref = inputs.read(stage.parent / "run-status.json")
    baseline, baseline_ref = inputs.read(repo / reporter.NOT_RUN)
    for reference in (report_ref, plan_ref, stage_ref, ledger_ref, status_ref, baseline_ref):
        require((None, reference["path"]) in raw_sources
                and raw_sources[(None, reference["path"])]["sha256"] == reference["sha256"],
                "raw summary source binding missing or different")
    require(digest(envelope["plan"]) == envelope["sha256"] == report["plan_sha256"], "plan seal mismatch")
    require(run_status.get("state") in ("complete", "incomplete_preserved", "stopped_preserved"),
            "terminal cohort status required")
    for key, path in (("report_sha256", stage / "report.json"),
                      ("summary_sha256", stage / "stage-summary.json"),
                      ("router_ledger_sha256", stage / "model-router-ledger.json"),
                      ("input_provenance_sha256", stage.parent / "input-provenance.json")):
        require(run_status.get(key) == inputs.pin(path)["sha256"], "terminal source seal mismatch")
    require(raw["candidate"]["requested_sessions"] == 32, "this review is for the requested 32-person cohort")
    candidate = reporter.summarize_candidate(report, stage_summary, envelope, 32, stage_name)
    require(candidate == raw["candidate"], "raw candidate differs from recomputed frozen report")
    crosscheck_candidate(candidate, reporter)
    raw_mapping = reporter.map_baseline(baseline, candidate)
    require(raw_mapping == raw["baseline_46_mapping"], "raw baseline mapping differs")
    require(raw_markdown_path.read_text(encoding="utf-8") == reporter.render_markdown(raw),
            "raw comparison Markdown differs from its summary")
    require(raw_mapping["weighted_count"] == 46
            and raw_mapping["unique_persona_requirement_count"] == 32, "baseline denominator differs")
    columns, _, historical_refs = reporter.load_baselines(repo, baseline)
    require(len(raw["comparison_columns"]) == 4 and columns == raw["comparison_columns"][:3],
            "historical comparison columns differ from pinned baselines")
    for reference in historical_refs:
        require((reference.get("commit"), reference["path"]) in raw_sources
                and raw_sources[(reference.get("commit"), reference["path"])]["sha256"] == reference["sha256"],
                "historical source reference differs")
    require(raw["provider_cost"] == reporter.summarize_cost(stage_summary), "provider/cost summary differs")
    require(raw["router_delivery"] == reporter.summarize_delivery(
        stage_summary, ledger, ledger_ref, run_status=run_status, run_status_ref=status_ref,
        report_ref=report_ref, stage_ref=stage_ref), "router delivery summary differs")
    tasks = {task["job_id"]: task for task in report["tasks"]}
    planned = {job["id"]: job for job in envelope["plan"]["jobs"]}
    registered = verify_artifact_audit(audit, tasks, candidate, stage, inputs, digest)
    size_fixture_sources = verify_size_fixture_inputs(inputs) if size_changes else []
    reviewed = copy.deepcopy(raw)
    current = reviewed["candidate"]
    session_index = {session["job_id"]: session for session in current["sessions"]}
    criterion_index = {key_of(c): c for session in current["sessions"] for c in session["criteria"]}
    original_index = {key_of(c): c for c in candidate["criteria"]}
    changes, seen, changed_jobs = [], set(), set()
    baseline_rows = {row["id"]: row for row in baseline["rows"]}
    expected_delta, expected_sessions = expected_effect(review["changes"], candidate, raw_mapping, reporter)
    base_delta, base_sessions = expected_effect(base_changes, candidate, raw_mapping, reporter)
    extra_delta, extra_sessions = expected_effect(extra_changes, candidate, raw_mapping, reporter)
    search_delta, search_sessions = expected_effect(search_changes, candidate, raw_mapping, reporter)
    exercised_delta, exercised_sessions = expected_effect(exercised_changes, candidate, raw_mapping, reporter)
    size_delta, size_sessions = expected_effect(size_changes, candidate, raw_mapping, reporter)
    delete_delta, delete_sessions = expected_effect(delete_changes, candidate, raw_mapping, reporter)
    session_interaction = dict.fromkeys(reporter.OUTCOMES, 0)
    delete_interaction = None
    if delete_changes:
        without_delete = [item for item in review["changes"] if item["classification"] != DELETE_KEY_ABSENCE_CLASS]
        intermediate_delta, intermediate_sessions = expected_effect(without_delete, candidate, raw_mapping, reporter)
        paired_job = DELETE_KEY_ABSENCE_CASE["job_id"]
        require(intermediate_sessions[paired_job] == ("failed", "inconclusive")
                and expected_sessions[paired_job] == ("failed", "failed")
                and delete_sessions[paired_job] == ("failed", "failed"),
                "025 SEARCH/DELETE interaction differs from reviewed scope")
        session_interaction = {
            key: expected_delta["session_outcomes"][key] - intermediate_delta["session_outcomes"][key]
                 - delete_delta["session_outcomes"][key] for key in reporter.OUTCOMES}
        require(session_interaction == dict(passed=0, failed=1, inconclusive=-1, blocked=0, skipped=0),
                "unexpected same-session interaction term")
        delete_interaction = {"job_id": paired_job, "raw_outcome": "failed",
                              "intermediate_without_delete_review": "inconclusive",
                              "fully_reviewed_outcome": "failed",
                              "adjustment_to_sum_of_standalone_group_session_deltas": dict(session_interaction)}
    for position, item in enumerate(review["changes"]):
        item = copy.deepcopy(item)
        job_id, kind, index = item["job_id"], item["kind"], item["index"]
        key = (job_id, kind, index)
        require(type(index) is int and key not in seen and key in criterion_index, "unassessed/duplicate/unknown override")
        seen.add(key)
        require((item["oldstatus"], item["newstatus"]) in
                (("passed", "not_run"), ("failed", "not_run"), ("not_run", "passed"),
                 ("failed", "passed"), ("passed", "failed")),
                "N/A or unsupported transition cannot earn execution credit")
        require(isinstance(item["reason"], str) and item["reason"].strip(), "review reason missing")
        task, job, record = tasks[job_id], planned[job_id], criterion_index[key]
        result, receipt = task["result"], task["result"]["receipt"]
        require(task["status"] == "complete" and result.get("operational_completed") is True
                and task.get("current_valid") is True and job_id in registered, "override is not assessed")
        require(item["persona_id"] == task["persona_id"] == job["binding"]["persona_id"]
                == job["task"]["persona_id"] and receipt["task_id"] == job_id == job["task"]["id"],
                "review persona/task binding differs")
        require(receipt["persona_revision"] == job["binding"]["revision"]
                and receipt["profile_sha256"] == job["binding"]["profile_sha256"]
                and receipt["build_sha256"] == envelope["plan"]["build"]["sha256"], "review receipt binding differs")
        require(item["resultsha"] == task["result_sha256"] == digest(result)
                == session_index[job_id]["result_sha256"], "review raw result seal differs")
        require(record["status"] == item["oldstatus"]
                and reporter._requirement_map(job["task"])[(kind, index)] == {item["requirement_id"]}
                and record["requirement_ids"] == [item["requirement_id"]], "review criterion binding/status differs")
        session_root, evidence_root, by_path = registered[job_id]
        require(isinstance(item["evidencefiles"], list) and item["evidencefiles"]
                and len(set(item["evidencefiles"])) == len(item["evidencefiles"]), "missing/duplicate review evidence")
        evidence = []
        for name in item["evidencefiles"]:
            require(safe_relative(name) == PurePosixPath(name).name, "review evidence must name one registered file")
            relative = "evidence/" + job_id + "/1/" + name
            require(relative in by_path and by_path[relative]["kind"] in ("execution_log", "screenshot"),
                    "review evidence is not a registered observation or screenshot")
            artifact = by_path[relative]
            path = (session_root / relative).resolve(strict=True)
            require(path.is_relative_to(evidence_root), "review evidence escapes owned root")
            reference = inputs.pin(path, {"sha256": artifact["sha256"]})
            if item["classification"] in EXECUTED_RECLASSIFICATION_CLASSES:
                if item["classification"] == SEARCH_EXERCISED_CLASS:
                    case = SEARCH_EXERCISED_CASES[item["persona_id"]]
                elif item["classification"] == SIZE_EXERCISED_CLASS:
                    case = SIZE_EXERCISED_CASE
                else:
                    case = DELETE_KEY_ABSENCE_CASE
                proof = case["observation_sha256"]
                if name in proof:
                    require(artifact["kind"] == "execution_log" and reference["sha256"] == proof[name],
                            "execution reclassification observation differs from inspected bytes")
            evidence.append(dict(reference, id=artifact["id"], kind=artifact["kind"]))
        require(any(ref["kind"] == "execution_log" and PurePosixPath(ref["path"]).suffix == ".json"
                    for ref in evidence), "review requires at least one registered observation JSON")
        for identifier in baseline_change_rows(item):
            require(identifier in baseline_rows, "unknown excluded baseline row")
            row = baseline_rows[identifier]
            require(row["persona"] == item["persona_id"] and row["requirement"] == item["requirement_id"]
                    and row["kind"] == kind
                    and ((item["oldstatus"] in ("passed", "failed") and item["newstatus"] == "not_run")
                         or execution_reclassification(item)),
                    "changed baseline row binding differs")
        item["raw_criterion"] = copy.deepcopy(original_index[key])
        item["raw_report_source"] = dict(report_ref, selector=record["report_selector"])
        item["review_source"] = dict(review_ref, selector="changes[" + str(position) + "]")
        item["review_evidence"] = evidence
        record.update(raw_status=record["status"], raw_reason=record["reason"],
                      raw_evidence=copy.deepcopy(record["evidence"]),
                      status=item["newstatus"], reason=item["reason"], evidence=evidence,
                      status_source_ref=item["review_source"],
                      independent_review={"classification": item["classification"], "severity": item["severity"],
                                          "raw_result_sha256": item["resultsha"], "raw_report_source": item["raw_report_source"]})
        changed_jobs.add(job_id)
        changes.append(item)
    require(len(changes) == 14 + len(extra_changes) + len(search_changes) + len(exercised_changes)
            + len(size_changes) + len(delete_changes),
            "reviewed change count differs")
    session_changes = []
    for session in current["sessions"]:
        if session["job_id"] in changed_jobs:
            original = next(s for s in candidate["sessions"] if s["job_id"] == session["job_id"])
            require(original["outcome"] == outcome(original["criteria"]), "raw reviewed session outcome inconsistent")
            session["raw_outcome"] = original["outcome"]
            session["outcome"] = outcome(session["criteria"])
            session_changes.append({"job_id": session["job_id"], "persona_id": session["persona_id"],
                                    "oldstatus": original["outcome"], "newstatus": session["outcome"],
                                    "resultsha": session["result_sha256"]})
    require({s["job_id"]: (s["oldstatus"], s["newstatus"]) for s in session_changes} == expected_sessions,
            "session changes differ from independently derived expectations")
    require(Counter(base_sessions.values()) == Counter({("passed", "inconclusive"): 4,
                                                       ("inconclusive", "passed"): 1}),
            "original fourteen decisions no longer have the reviewed session effects")
    require(all(new != "passed" for _, new in list(extra_sessions.values()) + list(search_sessions.values())),
            "additional not-run corrections cannot create a passed session")
    require(all(old == new for old, new in exercised_sessions.values())
            and all(value == 0 for value in exercised_delta["session_outcomes"].values()),
            "exercised-search correction unexpectedly changes a session outcome")
    require(all(old == new == "failed" for old, new in size_sessions.values())
            and all(value == 0 for value in size_delta["session_outcomes"].values()),
            "SIZE correction unexpectedly changes the failed session")
    require(all(old == new == "failed" for old, new in delete_sessions.values())
            and all(value == 0 for value in delete_delta["session_outcomes"].values()),
            "standalone DELETE correction unexpectedly changes the raw failed session")
    aggregate = reporter._aggregate_sessions(current["sessions"])
    current["criteria"] = [c for session in current["sessions"] for c in session["criteria"]]
    for field in ("session_outcomes", "criteria_all", "criteria_by_kind"):
        current[field] = aggregate[field]
    current["failures"] = [c for c in current["criteria"] if c["status"] == "failed"]
    current["not_run_by_requirement"] = reporter._not_run_by_requirement(current["criteria"])
    current["validation"] = {"raw_candidate_validation": candidate["validation"],
                             "reviewed_aggregates_crosschecked": True, "raw_receipts_unchanged": True}
    crosscheck_candidate(current, reporter)
    for record in current["criteria"]:
        if key_of(record) not in seen:
            require(record == original_index[key_of(record)], "unlisted criterion changed")
    if size_changes:
        save_failures = [record for record in current["criteria"]
                         if record["job_id"] == SIZE_EXERCISED_CASE["job_id"]
                         and record["requirement_ids"] == ["PRD-IMPORT-SAVE-FAIL"]]
        require(len(save_failures) == 1 and save_failures[0]["status"] == "failed"
                and save_failures[0] == original_index[key_of(save_failures[0])],
                "SIZE correction changed or lost the preserved SAVE-FAIL failure")
    for field in ("requested_sessions", "planned_unique_personas", "assessed_completed_sessions",
                  "distinct_assessed_personas", "queue_counts", "unassessed_attempts", "host_protocol"):
        require(current[field] == candidate[field], "review changed assessment denominator or exclusion")
    mapping = reporter.map_baseline(baseline, current)
    require(mapping["weighted_count"] == raw_mapping["weighted_count"]
            and mapping["unique_persona_requirement_count"] == raw_mapping["unique_persona_requirement_count"],
            "review changed baseline denominator")
    actual_rows = {after["baseline_id"] for before, after in zip(raw_mapping["weighted_rows"], mapping["weighted_rows"])
                   if before["status"] != after["status"]}
    excluded_rows = [identifier for change in changes if change["classification"] not in EXECUTED_RECLASSIFICATION_CLASSES
                     for identifier in baseline_change_rows(change)]
    reclassified_rows = [identifier for change in changes if change["classification"] in EXECUTED_RECLASSIFICATION_CLASSES
                         for identifier in baseline_change_rows(change)]
    declared_rows = excluded_rows + reclassified_rows
    require(len(declared_rows) == len(set(declared_rows)) and actual_rows == set(declared_rows),
            "baseline changed rows differ from the review")
    d = {
        "criteria_all": delta(current["criteria_all"], candidate["criteria_all"], reporter.CRITERIA),
        "criteria_by_kind": {kind: delta(current["criteria_by_kind"][kind], candidate["criteria_by_kind"][kind], reporter.CRITERIA)
                             for kind in ("success", "recovery")},
        "session_outcomes": delta(current["session_outcomes"], candidate["session_outcomes"], reporter.OUTCOMES),
        "baseline_weighted": delta(mapping["weighted_statuses"], raw_mapping["weighted_statuses"], reporter.MAPPING),
        "baseline_unique": delta(mapping["unique_statuses"], raw_mapping["unique_statuses"], reporter.MAPPING),
    }
    require(d == expected_delta, "actual net delta differs from pinned review decisions")
    require(base_delta["criteria_all"] == dict(passed=-10, failed=0, not_run=10, not_applicable=0)
            and base_delta["criteria_by_kind"]["success"] == base_delta["criteria_all"]
            and all(value == 0 for value in base_delta["criteria_by_kind"]["recovery"].values())
            and base_delta["session_outcomes"] == dict(passed=-3, failed=0, inconclusive=3, blocked=0, skipped=0)
            and base_delta["baseline_weighted"] == dict(passed=-9, failed=0, not_run=9, unassessed=0)
            and base_delta["baseline_unique"] == dict(passed=-7, failed=0, not_run=7, unassessed=0),
            "original fourteen-decision delta differs")
    for name, additional in (("precondition", extra_delta), ("search-control", search_delta)):
        for label in ("criteria_all", "baseline_weighted", "baseline_unique"):
            vector = additional[label]
            require(vector["passed"] <= 0 and vector["failed"] <= 0
                    and vector["not_run"] == -vector["passed"] - vector["failed"]
                    and vector.get("not_applicable", 0) == vector.get("unassessed", 0) == 0,
                    name + " review improperly adds exercise credit")
        require(additional["criteria_by_kind"]["success"] == additional["criteria_all"]
                and all(value == 0 for value in additional["criteria_by_kind"]["recovery"].values()),
                name + " review changed recovery criteria")
    require(search_delta["criteria_all"]["passed"] == 0, "search-control review cannot create a pass")
    for name, additional, items in (("exercised-search", exercised_delta, exercised_changes),
                                    ("SIZE", size_delta, size_changes)):
        require(additional["criteria_all"] == dict(passed=len(items), failed=-len(items), not_run=0, not_applicable=0)
                and additional["criteria_by_kind"]["success"] == additional["criteria_all"]
                and all(value == 0 for value in additional["criteria_by_kind"]["recovery"].values()),
                name + " criterion delta differs")
        for label in ("baseline_weighted", "baseline_unique"):
            vector = additional[label]
            require(vector["passed"] >= 0 and vector["failed"] == -vector["passed"]
                    and vector["not_run"] == vector["unassessed"] == 0,
                    name + " review changes baseline execution credit")
    require(all(value == 0 for label in ("baseline_weighted", "baseline_unique") for value in size_delta[label].values()),
            "SIZE correction has an unexpected baseline mapping")
    require(delete_delta["criteria_all"] == dict(passed=-len(delete_changes), failed=len(delete_changes),
                                                not_run=0, not_applicable=0)
            and delete_delta["criteria_by_kind"]["success"] == delete_delta["criteria_all"]
            and all(value == 0 for value in delete_delta["criteria_by_kind"]["recovery"].values()),
            "DELETE criterion delta differs")
    for label in ("baseline_weighted", "baseline_unique"):
        require(delete_delta[label] == dict(passed=-len(delete_changes), failed=len(delete_changes),
                                           not_run=0, unassessed=0),
                "DELETE reclassification changes execution credit or unexpected baseline rows")
    for label in ("criteria_all", "session_outcomes", "baseline_weighted", "baseline_unique"):
        require(all(d[label][key] == base_delta[label][key] + extra_delta[label][key] + search_delta[label][key]
                    + exercised_delta[label][key] + size_delta[label][key] + delete_delta[label][key]
                    + (session_interaction[key] if label == "session_outcomes" else 0)
                    for key in d[label]),
                "group deltas plus the explicit session interaction do not match the global recomputation")
    reviewed["schema_version"] = "peekly-reviewed-coverage-comparison.v1"
    reviewed["baseline_46_mapping"] = mapping
    column = reviewed["comparison_columns"][3]
    require(column["completed_sessions"] == candidate["assessed_completed_sessions"]
            and column["distinct_personas"] == candidate["distinct_assessed_personas"]
            and column["session_outcomes"] == candidate["session_outcomes"]
            and column["criteria_all"] == candidate["criteria_all"]
            and column["criteria_by_kind"] == candidate["criteria_by_kind"]
            and column["host_protocol_on_completed_receipts"] == candidate["host_protocol"]["assessed_completed"],
            "raw fourth comparison column inconsistent")
    column["label"] = "신규32명·증거감사"
    for field in ("session_outcomes", "criteria_all", "criteria_by_kind"):
        column[field] = copy.deepcopy(current[field])
    column["source_refs"] += [dict(review_ref, selector="changes"),
                              dict(audit_ref, selector="audit_passed; jobs; sources")]
    require(reviewed["comparison_columns"][:3] == raw["comparison_columns"][:3], "historical columns changed")
    reviewed["independent_review"] = {
        "review_source": review_ref, "raw_summary_source": raw_ref, "artifact_audit_source": audit_ref,
        "runtime_commit_recorded_by_review": review["runtime_commit"],
        "scope": review["scope"], "changes": changes, "session_changes": session_changes,
        "delta": d, "expected_delta": expected_delta, "original_fourteen_delta": base_delta,
        "additional_precondition_delta": extra_delta, "additional_precondition_change_count": len(extra_changes),
        "additional_search_control_delta": search_delta, "additional_search_control_change_count": len(search_changes),
        "additional_search_exercised_delta": exercised_delta,
        "additional_search_exercised_change_count": len(exercised_changes),
        "search_exercised_scope": copy.deepcopy(SEARCH_EXERCISED_SCOPE) if exercised_changes else None,
        "search_exercised_case_bindings": {item["persona_id"]: copy.deepcopy(SEARCH_EXERCISED_CASES[item["persona_id"]])
                                          for item in exercised_changes},
        "additional_size_exercised_delta": size_delta, "additional_size_exercised_change_count": len(size_changes),
        "size_exercised_scope": copy.deepcopy(SIZE_EXERCISED_SCOPE) if size_changes else None,
        "size_exercised_case_binding": copy.deepcopy(SIZE_EXERCISED_CASE) if size_changes else None,
        "size_fixture_sources": size_fixture_sources,
        "additional_delete_key_absence_delta": delete_delta,
        "additional_delete_key_absence_change_count": len(delete_changes),
        "delete_key_absence_scope": copy.deepcopy(DELETE_KEY_ABSENCE_SCOPE) if delete_changes else None,
        "delete_key_absence_case_binding": copy.deepcopy(DELETE_KEY_ABSENCE_CASE) if delete_changes else None,
        "session_group_interaction_delta": session_interaction, "delete_key_absence_interaction": delete_interaction,
        "baseline_rows_excluded": sorted(excluded_rows),
        "baseline_rows_reclassified": sorted(reclassified_rows), "baseline_rows_changed": sorted(actual_rows),
        "raw_receipts_modified": False, "unlisted_criteria_preserved": True,
        "artifact_audit_sources_verified": True, "referenced_observation_bytes_rechecked": True,
        "inputs_unchanged": True, "new_observations": 0, "new_model_calls": 0, "new_browser_calls": 0,
    }
    reviewed["limitations"] = [
        "Independent review changes only the listed criteria; other judgments retain their original limitations.",
        "Whole-receipt artifact bytes are bound to the separate byte-audit result; cited review observations are rehashed here.",
        "Different cohort sizes and repeated baseline people prevent an unqualified overall improvement rate.",
        "N/A and unassessed attempts earn no execution credit. Original receipts and prior comparison columns are preserved.",
    ]
    existing_sources = {(ref.get("commit"), ref["path"]) for ref in reviewed["sources"]}
    for reference in inputs.files.values():
        if (None, reference["path"]) not in existing_sources:
            reviewed["sources"].append(reference)
            existing_sources.add((None, reference["path"]))
    def unchanged():
        inputs.verify_unchanged()
        require(wal.exists() == audited_wal_exists, "WAL presence changed during review")
    unchanged()
    contents = [
        ("reviewed-summary.json", json.dumps(reviewed, ensure_ascii=False, sort_keys=True, indent=2) + "\n"),
        ("comparison-reviewed.md", reviewed_markdown(reviewed, reporter)),
    ]
    create_outputs(destination, contents, unchanged)
    return {"output": destination.relative_to(repo).as_posix(), "assessed_sessions": current["assessed_completed_sessions"],
            "changed_criteria": len(changes), "session_outcomes": current["session_outcomes"],
            "criteria_all": current["criteria_all"], "baseline_weighted": mapping["weighted_statuses"],
            "baseline_unique": mapping["unique_statuses"], "inputs_unchanged": True,
            "raw_receipts_modified": False, "new_model_calls": 0, "new_browser_calls": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--raw-summary", type=Path)
    parser.add_argument("--criterion-review", type=Path)
    parser.add_argument("--artifact-audit", type=Path)
    args = parser.parse_args()
    try:
        value = build_reviewed(args.repo, args.stage, args.output,
            args.raw_summary or args.output / "summary.json",
            args.criterion_review or args.output / "criterion-review.json",
            args.artifact_audit or args.output / "artifact-audit.json")
        print(json.dumps(value, ensure_ascii=False, sort_keys=True))
    except (ReviewError, ValueError, OSError, KeyError, TypeError, ImportError) as exc:
        print("Independent review refused: " + str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
