#!/usr/bin/env python3
"""Apply explicitly authored, artifact-bound review decisions to a fresh cohort.

No model/browser/runner/Queue mutation is available. Raw finalizer outputs and
all historical columns remain immutable. New verdicts are authored decisions:
hash/identity checks validate their evidence bindings, not their semantics.

Input schema: peekly-completion-criterion-review.v1. Required top-level fields:
stage_root, plan_sha256, raw_summary_sha256, artifact_audit_sha256, scope,
raw_receipts_modified:false, new_model_calls:0, new_browser_calls:0, queue_writes:0,
decisions:[{job_id,persona_id,kind,index,requirement_id,result_sha256,
expected_raw_status,reviewed_status,reason,classifications:[...],
evidence:[{artifact_id,path,sha256,observation_id,purpose}]}].
A decision may retain its raw status to record a positively reviewed criterion.
Purpose is setup/action/result/context; each decision needs a result execution log.
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
import sqlite3
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa"))
import report_peekly_completion as reporting
from uxresearch.canonical import digest

old = reporting.old
RAW_FILES = ("summary.json", "comparison.md", "not-run-23-baseline.json",
             "artifact-audit.json", "automated-outcome.json")
OUTPUTS = ("reviewed-summary.json", "comparison-reviewed.md", "evidence-review.md")
COVERAGE = ("passed", "failed", "not_run", "not_applicable", "unassessed")
CLASSIFICATIONS = {
    "product_defect", "runner_limitation", "fixture_precondition",
    "judge_false_pass", "judge_false_failure", "judge_missed_execution",
    "judge_unfounded_execution", "conditional_not_applicable",
    "confirmed_raw_verdict",
}
PURPOSES = {"setup", "action", "result", "context"}
EXPECTED_PERSONAS = {"PER-PEEKLY-V2-" + str(n).zfill(3) for n in range(1, 33)}


class ReviewError(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise ReviewError(reason)


def relative(value):
    require(isinstance(value, str) and value and "\\" not in value, "invalid_relative_path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(p not in ("", ".", "..") for p in value.split("/")),
            "unsafe_relative_path")
    return path.as_posix()


def safe(repo, value, *, existing=True):
    value = Path(value)
    value = value if value.is_absolute() else repo / value
    require(".." not in value.parts, "parent_path_forbidden")
    require(value.is_relative_to(repo), "path_outside_repository")
    require(not any(p.is_symlink() for p in (value, *value.parents)
                    if p.is_relative_to(repo)), "symlink_path_forbidden")
    resolved = value.resolve(strict=existing)
    require(resolved.is_relative_to(repo), "resolved_path_outside_repository")
    return resolved


def file_hash(path):
    sha, size = hashlib.sha256(), 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
            size += len(chunk)
    return sha.hexdigest(), size


class Inputs:
    def __init__(self, repo):
        self.repo, self.files = repo, {}

    def pin(self, path, expected=None):
        path = safe(self.repo, path)
        require(path.is_file(), "input_not_regular_file")
        sha, size = file_hash(path)
        ref = dict(path=path.relative_to(self.repo).as_posix(), sha256=sha, bytes=size)
        require(path not in self.files or self.files[path] == ref, "input_changed_during_review")
        if expected is not None:
            require(expected.get("sha256") == sha, "input_sha256_mismatch:" + ref["path"])
            require("bytes" not in expected or expected["bytes"] == size, "input_byte_count_mismatch")
        self.files[path] = ref
        return ref

    def read(self, path, expected=None):
        ref = self.pin(path, expected)
        require(ref["bytes"] <= 64 * 1024 * 1024, "json_read_limit")
        result = old._json(safe(self.repo, path).read_bytes())
        require(isinstance(result, dict), "json_object_required")
        self.pin(path, ref)
        return result, ref

    def unchanged(self):
        for path, ref in self.files.items():
            require(path.is_file() and not path.is_symlink()
                    and file_hash(path) == (ref["sha256"], ref["bytes"]),
                    "input_changed_before_publication:" + ref["path"])


def historical(repo, original):
    columns, _, _ = old.load_baselines(repo, original)
    reviewed, reference, remaining = reporting.load_reviewed(repo)
    columns.append(reporting.comparison_column("65f52f7·직전 증거감사", reviewed["candidate"],
        [dict(reference, selector="candidate: independent evidence review of the previous 29 completed sessions")]))
    return columns, remaining


def outcome(criteria):
    statuses = {row["status"] for row in criteria}
    if "failed" in statuses:
        return "failed"
    if "passed" in statuses and statuses <= {"passed", "not_applicable"}:
        return "passed"
    return "inconclusive"


def key_of(row):
    return row["job_id"], row["kind"], row["index"]


def coverage_mapping(baseline, candidate, reviewed_keys):
    """Keep N/A separate from absent/excluded matches; only P/F earns credit."""
    index = {}
    for criterion in candidate["criteria"]:
        for requirement in criterion["requirement_ids"]:
            key = criterion["persona_id"], criterion["kind"], requirement
            require(key not in index, "ambiguous_coverage_requirement")
            index[key] = criterion
    weighted, unique = [], {}
    for row in baseline["rows"]:
        key = row["persona"], row["kind"], row["requirement"]
        criterion = index.get(key)
        status = criterion["status"] if criterion else "unassessed"
        item = dict(baseline_id=row["id"], persona_id=key[0], kind=key[1], requirement_id=key[2],
                    status=status, executed=status in {"passed", "failed"},
                    independently_reviewed=bool(criterion and key_of(criterion) in reviewed_keys),
                    candidate_key=(dict(job_id=criterion["job_id"], kind=criterion["kind"],
                                        index=criterion["index"]) if criterion else None),
                    reason=("no_assessed_matching_criterion" if criterion is None
                            else criterion["reason"]))
        weighted.append(item)
        if key not in unique:
            unique[key] = dict(item, baseline_ids=[], baseline_weight=0)
            unique[key].pop("baseline_id")
        require(unique[key]["status"] == status, "ambiguous_weighted_mapping")
        unique[key]["baseline_ids"].append(row["id"])
        unique[key]["baseline_weight"] += 1
    unique_rows = list(unique.values())
    def total(rows):
        counts = {status: sum(row["status"] == status for row in rows) for status in COVERAGE}
        return dict(counts=counts, executed=counts["passed"] + counts["failed"],
                    independently_reviewed=sum(row["independently_reviewed"] for row in rows),
                    independently_reviewed_executed=sum(row["independently_reviewed"] and row["executed"]
                                                        for row in rows))
    return dict(weighted_count=len(weighted), weighted=total(weighted), weighted_rows=weighted,
                unique_count=len(unique_rows), unique=total(unique_rows), unique_rows=unique_rows,
                counting_rule="P/F only; N/A and unassessed remain separate and receive no execution credit.")


def verify_audit_and_queue(inputs, stage, report, plan, candidate, audit):
    require(audit.get("schema_version") == "peekly-artifact-byte-audit.v1"
            and audit.get("audit_passed") is True and audit.get("mismatches") == 0
            and audit.get("source_files_unchanged") is True and audit.get("prior_queues_unchanged") is True
            and audit.get("stage") == stage.relative_to(inputs.repo).as_posix()
            and all(audit.get(k) == 0 for k in ("new_model_calls", "new_browser_calls", "queue_writes")),
            "clean_bound_artifact_audit_required")
    sources = {}
    for ref in audit["sources"]:
        name = relative(ref["path"])
        require(name not in sources, "duplicate_audit_source")
        sources[name] = inputs.pin(inputs.repo / name, ref)
    required = [stage / name for name in ("queue.sqlite", "plan.json", "report.json",
                                        "stage-summary.json", "model-router-ledger.json")]
    required += [stage.parent / name for name in ("run-status.json", "input-provenance.json")]
    require(all(p.relative_to(inputs.repo).as_posix() in sources for p in required),
            "required_audit_source_missing")
    wal = stage / "queue.sqlite-wal"
    require(wal.exists() == (wal.relative_to(inputs.repo).as_posix() in sources), "audit_wal_presence_changed")
    with sqlite3.connect((stage / "queue.sqlite").as_uri() + "?mode=ro", uri=True, timeout=5) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        rows = {row["id"]: dict(row) for row in db.execute(
            "SELECT id,status,result,result_sha,checkpoint,checkpoint_sha FROM jobs")}
        meta = dict(db.execute("SELECT key,value FROM meta WHERE key='plan_sha'"))
    tasks = {task["job_id"]: task for task in report["tasks"]}
    require(set(rows) == set(tasks) == {job["id"] for job in plan["plan"]["jobs"]}
            and meta.get("plan_sha") == plan["sha256"], "queue_plan_report_identity_mismatch")
    require(not any(row["status"] in {"queued", "running"} for row in rows.values()), "queue_not_terminal")
    audited = {job["job_id"]: job for job in audit["jobs"]}
    sessions = {session["job_id"]: session for session in candidate["sessions"]}
    require(len(audited) == len(audit["jobs"]) == audit["assessed_sessions"] == len(sessions)
            and set(audited) == set(sessions), "audited_session_set_mismatch")
    checkpoints = {}
    for job_id, row in rows.items():
        task = tasks[job_id]
        result = old._json(row["result"]) if row["result"] is not None else None
        checkpoint = old._json(row["checkpoint"]) if row["checkpoint"] is not None else None
        require(task["status"] == row["status"] and task.get("result") == result, "queue_result_changed")
        if result is not None:
            require(digest(result) == row["result_sha"] == task["result_sha256"], "result_seal_mismatch")
        if checkpoint is not None:
            require(digest(checkpoint) == row["checkpoint_sha"], "checkpoint_seal_mismatch")
        if job_id not in sessions:
            continue
        receipt = result["receipt"]
        job = audited[job_id]
        require(job["result_sha256"] == row["result_sha"]
                and job["checkpoint_sha256"] == row["checkpoint_sha"]
                and job["all_registered_artifacts_checked"] is True
                and job["registered_artifacts"] == len(receipt["artifacts"])
                and job["persona_id"] == task["persona_id"], "audited_receipt_binding_mismatch")
        first = result.get("first_judgment")
        require(isinstance(first, dict) and first and digest(first) == result.get("first_judgment_sha256")
                == job["first_judgment_sha256"] == checkpoint.get("first_judgment_sha256")
                and first == checkpoint.get("first_judgment"), "first_judgment_seal_mismatch")
        observations = checkpoint.get("observations", [])
        require(len({o["id"] for o in observations}) == len(observations), "duplicate_observation_id")
        checkpoints[job_id] = {o["id"]: o for o in observations}
    return tasks, checkpoints


def verify_evidence(inputs, stage, item, task, job, observations):
    receipt = task["result"]["receipt"]
    artifacts = {a["id"]: a for a in receipt["artifacts"]}
    require(len(artifacts) == len(receipt["artifacts"]), "duplicate_receipt_artifact")
    require(receipt["task_id"] == task["job_id"] == job["task"]["id"]
            and receipt["persona_revision"] == job["binding"]["revision"]
            and receipt["profile_sha256"] == job["binding"]["profile_sha256"]
            and receipt["build_sha256"] == job["build_sha256"], "receipt_identity_mismatch")
    evidence = item.get("evidence")
    require(isinstance(evidence, list) and evidence
            and len({e["artifact_id"] for e in evidence}) == len(evidence), "missing_or_duplicate_evidence")
    verified, result_log = [], False
    base = stage / "sessions" / task["job_id"]
    evidence_root = base / "evidence" / task["job_id"] / "1"
    for reference in evidence:
        require(reference.get("purpose") in PURPOSES, "evidence_purpose_invalid")
        artifact = artifacts.get(reference["artifact_id"])
        require(artifact is not None and artifact["kind"] in {"execution_log", "screenshot"},
                "artifact_not_admitted_to_receipt")
        require(reference.get("path") == artifact["path"]
                and reference.get("sha256") == artifact["sha256"], "review_artifact_binding_mismatch")
        path = safe(inputs.repo, base / relative(artifact["path"]))
        require(path.is_relative_to(evidence_root), "artifact_outside_owned_evidence")
        source = inputs.pin(path, artifact)
        observation = observations.get(reference["observation_id"])
        require(observation is not None, "observation_not_admitted")
        admitted = observation.get("artifacts", [])
        require(isinstance(admitted, list) and admitted
                and len({a["id"] for a in admitted}) == len(admitted)
                and all(artifacts.get(a["id"]) == a for a in admitted)
                and artifact in admitted, "observation_artifact_registration_mismatch")
        if artifact["kind"] == "execution_log":
            record, _ = inputs.read(path, artifact)
            # The adapter writes the log before registering its own log artifact,
            # then adds exactly this admission metadata to the sealed checkpoint.
            projection = {k: v for k, v in observation.items() if k != "artifacts"}
            require(record.get("schema_version") == "ux-agent-observation.v1"
                    and record.get("binding") == job["binding"]
                    and record.get("context_id") == task["context_id"]
                    and record.get("observation") == projection,
                    "observation_log_binding_mismatch")
            result_log |= reference["purpose"] == "result"
        else:
            require(any(c == artifact for c in observation.get("captures", [])), "capture_not_in_observation")
        verified.append(dict(reference, source_ref=source, artifact_kind=artifact["kind"]))
    require(result_log, "result_execution_log_required")
    return verified


def apply_decisions(inputs, stage, raw, review, report, plan, audit):
    require(review.get("schema_version") == "peekly-completion-criterion-review.v1"
            and review.get("stage_root") == stage.relative_to(inputs.repo).as_posix()
            and review.get("plan_sha256") == plan["sha256"], "review_stage_or_schema_mismatch")
    require(review.get("raw_receipts_modified") is False
            and all(type(review.get(k)) is int and review[k] == 0
                    for k in ("new_model_calls", "new_browser_calls", "queue_writes")),
            "review_must_be_offline_and_preserve_receipts")
    require(isinstance(review.get("scope"), str) and review["scope"].strip(), "review_scope_required")
    decisions = review.get("decisions")
    require(isinstance(decisions, list) and 0 < len(decisions) <= 136, "bounded_review_decisions_required")
    candidate = copy.deepcopy(raw["candidate"])
    sessions = {s["job_id"]: s for s in candidate["sessions"]}
    records = {key_of(c): c for s in candidate["sessions"] for c in s["criteria"]}
    require(len(records) == len(candidate["criteria"]), "duplicate_candidate_criterion")
    tasks, checkpoints = verify_audit_and_queue(inputs, stage, report, plan, candidate, audit)
    jobs = {j["id"]: dict(j, build_sha256=plan["plan"]["build"]["sha256"]) for j in plan["plan"]["jobs"]}
    seen, applied = set(), []
    for item in decisions:
        key = key_of(item)
        require(type(item["index"]) is int and key in records and key not in seen,
                "unassessed_unknown_or_duplicate_review_criterion")
        seen.add(key)
        record, task, job = records[key], tasks[item["job_id"]], jobs[item["job_id"]]
        require(item["persona_id"] == task["persona_id"] == job["binding"]["persona_id"]
                == record["persona_id"], "review_persona_mismatch")
        require(record["requirement_ids"] == [item["requirement_id"]]
                and old._requirement_map(job["task"])[key[1:]] == {item["requirement_id"]},
                "review_requirement_or_index_mismatch")
        require(item["result_sha256"] == task["result_sha256"] == sessions[item["job_id"]]["result_sha256"],
                "review_result_seal_mismatch")
        require(item["expected_raw_status"] == record["status"] and item["reviewed_status"] in old.CRITERIA,
                "raw_status_or_reviewed_status_mismatch")
        require(isinstance(item.get("reason"), str) and item["reason"].strip(), "review_reason_required")
        classes = item.get("classifications")
        require(isinstance(classes, list) and classes and len(classes) == len(set(classes))
                and set(classes) <= CLASSIFICATIONS, "review_classifications_invalid")
        if item["reviewed_status"] == "not_applicable":
            require(item["kind"] == "recovery" and "conditional_not_applicable" in classes,
                    "NA_requires_explicit_conditional_recovery")
        evidence = verify_evidence(inputs, stage, item, task, job, checkpoints[item["job_id"]])
        record["raw_reason"] = record["reason"]
        record["raw_evidence"] = copy.deepcopy(record["evidence"])
        record["status"] = item["reviewed_status"]
        record["reason"] = item["reason"]
        record["evidence"] = [dict(id=e["artifact_id"], path=e["source_ref"]["path"],
                                   sha256=e["source_ref"]["sha256"]) for e in evidence]
        record["raw_status"] = item["expected_raw_status"]
        record["independent_review"] = dict(classifications=classes, evidence=evidence)
        applied.append(dict(item, evidence=evidence, changed=item["expected_raw_status"] != item["reviewed_status"]))
    session_changes = []
    changed_jobs = {item["job_id"] for item in applied if item["changed"]}
    original_sessions = {session["job_id"]: session for session in raw["candidate"]["sessions"]}
    for session in candidate["sessions"]:
        if session["job_id"] not in changed_jobs:
            continue
        before = session["outcome"]
        proposed = outcome(session["criteria"])
        if proposed == "passed" and before != "passed":
            # Normal ScaleExecution excludes problem-bearing results through
            # operational_completed. Defend against inconsistent bound metadata:
            # a criterion-only review cannot resolve a separate session problem
            # or manufacture the missing final judgment required by its producer.
            task = tasks[session["job_id"]]
            result = task["result"]
            constraints = []
            if not isinstance(result.get("judgment"), dict) or not result["judgment"]:
                constraints.append("missing_or_invalid_final_judgment")
            if "problem" not in result or result["problem"] is not None:
                constraints.append("result_problem_missing_or_unresolved")
            if task.get("problem") is not None:
                constraints.append("task_problem_unresolved")
            raw_criteria_outcome = outcome(original_sessions[session["job_id"]]["criteria"])
            if before != raw_criteria_outcome:
                constraints.append("raw_session_has_independent_outcome")
            if constraints:
                session["outcome_review_constraint"] = dict(
                    promotion_to_passed_blocked=True, raw_outcome=before,
                    raw_criteria_outcome=raw_criteria_outcome,
                    reviewed_criteria_outcome=proposed, reasons=constraints)
                proposed = before
        session["outcome"] = proposed
        if session["outcome"] != before:
            session_changes.append(dict(job_id=session["job_id"], before=before, after=session["outcome"]))
    aggregate = old._aggregate_sessions(candidate["sessions"])
    candidate["criteria"] = [c for s in candidate["sessions"] for c in s["criteria"]]
    for field in ("session_outcomes", "criteria_all", "criteria_by_kind"):
        candidate[field] = aggregate[field]
    candidate["failures"] = [c for c in candidate["criteria"] if c["status"] == "failed"]
    candidate["not_run_by_requirement"] = old._not_run_by_requirement(candidate["criteria"])
    for field in ("requested_sessions", "planned_unique_personas", "assessed_completed_sessions",
                  "distinct_assessed_personas", "queue_counts", "unassessed_attempts", "host_protocol"):
        require(candidate[field] == raw["candidate"][field], "review_changed_assessment_denominator")
    original = {key_of(c): c for c in raw["candidate"]["criteria"]}
    require(all(c == original[key_of(c)] for c in candidate["criteria"] if key_of(c) not in seen),
            "unlisted_criterion_changed")
    return candidate, applied, seen, session_changes


def markdown(summary):
    # The standard renderer preserves the four historical columns and all raw
    # cost/delivery disclosures. The explicit five-bin section below separates N/A.
    text = reporting.render_markdown(summary)
    text = text.replace("# Peekly coverage comparison", "# Peekly coverage comparison — listed criteria reviewed", 1)
    text = text.replace("summary.json의 not_run_by_requirement",
                        "reviewed-summary.json의 candidate.not_run_by_requirement")
    text = text.replace("## 저장된 실패 판정", "## 독립 검토를 반영한 실패 판정")
    text = text.replace("신규 영수증의 N/A를 임의로 재분류하지 않았습니다.",
                        "신규 기준은 명시된 독립 검토 결정만 반영했습니다.")
    text = text.replace("실패 목록은 저장된 판정이며 제품 결함·실행기 결함·판정기 오판의 최종 분류는 별도 검토가 필요합니다.",
                        "명시된 검토 기준의 분류와 원본 대비 변경은 evidence-review.md에 있습니다. 나머지 판정은 원본 상태를 유지합니다.")
    lines = ["", "## 독립 검토 및 N/A 분리", "",
             "기존 4개 비교 열과 원본 영수증은 그대로 보존했습니다. 이번 검토에 명시된 기준만 재판정했고 나머지는 원본 판정을 유지합니다.",
             "위 호환용 대응표의 미평가에는 N/A가 포함됩니다. 아래 표는 N/A를 별도로 분리한 최종 대응 수치입니다.", "",
             "| 대응 범위 | 기준 수 | 통과 | 실패 | 미실행 | N/A | 미평가 | 실행 확인 | 독립 검토된 실행 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, mapping in summary["reviewed_coverage"].items():
        for scope, count in (("weighted", mapping["weighted_count"]), ("unique", mapping["unique_count"])):
            value = mapping[scope]
            values = [count] + [value["counts"][k] for k in COVERAGE] + [value["executed"], value["independently_reviewed_executed"]]
            lines.append("| " + name + "·" + scope + " | " + " | ".join(map(str, values)) + " |")
    lines += ["", "실행 확인은 통과와 실패의 합입니다. N/A·미평가는 감소 성과에 포함하지 않습니다.",
              "원래 46행의 반복 가중치는 새 사람이나 새 실행으로 세지 않습니다. 기존 23개와 신규 전체 분모는 별도입니다.",
              "제품 개선율이나 전체 기준의 독립 검토 완료를 주장하지 않습니다.",
              "", "검토 입력·변경 목록·증거 해시는 evidence-review.md 및 reviewed-summary.json의 independent_review에 있습니다.", ""]
    return text + "\n".join(lines)


def evidence_markdown(summary):
    review = summary["independent_review"]
    lines = ["# Peekly independent criterion review", "", review["scope"], "",
             "- 검토 상태: 명시된 기준만 독립 검토. 나머지 원본 판정의 한계는 유지.",
             "- 원본 영수증·집계·큐 변경: 없음. 새 모델·브라우저 호출: 0.",
             "- 새 결정 수: " + str(len(review["decisions"])),
             "- 실제 판정 변경 수: " + str(sum(d["changed"] for d in review["decisions"])), ""]
    for item in review["decisions"]:
        lines += ["## " + item["persona_id"] + " / " + item["requirement_id"], "",
                  "- 신규 job: " + item["job_id"] + "; " + item["kind"] + "[" + str(item["index"]) + "]",
                  "- 판정: " + item["expected_raw_status"] + " → " + item["reviewed_status"],
                  "- 분류: " + ", ".join(item["classifications"]),
                  "- 근거: " + item["reason"], ""]
        for evidence in item["evidence"]:
            ref = evidence["source_ref"]
            lines.append("- " + evidence["purpose"] + " / " + evidence["observation_id"]
                         + " / " + evidence["artifact_id"] + ": " + ref["path"]
                         + " — SHA256 " + ref["sha256"])
        lines.append("")
    lines += ["## 검증 범위", "",
              "전체 등록 artifact는 고정된 별도 byte 감사에 결합했습니다. 여기서 인용한 artifact bytes, 관측/checkpoint/receipt 결합은 다시 검증했습니다.",
              "해시와 식별자 일치는 판정 의미의 자동 검증이 아닙니다. 작성된 독립 검토 사유와 실제 관측을 함께 읽어야 합니다.", ""]
    return "\n".join(lines)


def publish_outputs(destination, contents, verify):
    require(not any(os.path.lexists(destination / name) for name in OUTPUTS), "reviewed_output_exists")
    created = []
    with tempfile.TemporaryDirectory(prefix=".review-staged-", dir=destination) as directory:
        staged = Path(directory)
        for name, content in contents.items():
            with (staged / name).open("x", encoding="utf-8") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
        verify()
        try:
            for name in OUTPUTS:
                os.link(staged / name, destination / name)  # Atomic no-overwrite.
                created.append((destination / name, file_hash(staged / name)))
            verify()
        except BaseException:
            for path, expected in created:
                if path.is_file() and not path.is_symlink() and file_hash(path) == expected:
                    path.unlink()  # Only files created by this failed transaction.
            raise


def build(repo, stage, output, review_path):
    repo = Path(repo).resolve(strict=True)
    stage = safe(repo, stage)
    output = safe(repo, output)
    require(stage.name == "stage-32" and stage.parent.name.startswith("peekly-completion32-"),
            "fresh_completion32_stage_required")
    require(output.is_dir() and output.is_relative_to(repo / "docs/validation/peekly-coverage-completion-20261115")
            and not output.is_relative_to(stage), "review_output_scope_invalid")
    require(not any(os.path.lexists(output / name) for name in OUTPUTS), "reviewed_output_exists")
    inputs = Inputs(repo)
    for name in RAW_FILES:
        inputs.pin(output / name)
    raw, raw_ref = inputs.read(output / "summary.json")
    audit, audit_ref = inputs.read(output / "artifact-audit.json")
    automated, automated_ref = inputs.read(output / "automated-outcome.json")
    review, review_ref = inputs.read(review_path)
    require(review.get("raw_summary_sha256") == raw_ref["sha256"]
            and review.get("artifact_audit_sha256") == audit_ref["sha256"], "review_raw_source_hash_mismatch")
    require(raw.get("schema_version") == "peekly-completion-comparison.v1"
            and len(raw.get("comparison_columns", [])) == 5, "fresh_five_column_raw_report_required")
    require(automated.get("schema_version") == "peekly-completion-automated-outcome.v1"
            and automated.get("semantic_review_status") == "pending_manual_review"
            and automated.get("postprocess_status") == "raw_report_and_byte_audit_completed"
            and automated.get("coverage_target_met") is None
            and automated.get("run_root") == stage.parent.relative_to(repo).as_posix()
            and set(automated.get("generated_files", {})) == set(RAW_FILES[:-1]),
            "sealed_raw_finalizer_outcome_required")
    for name, sha in automated["generated_files"].items():
        inputs.pin(output / name, {"sha256": sha})
    paths = dict(provenance=stage.parent / "input-provenance.json",
                 status=stage.parent / "run-status.json", report=stage / "report.json",
                 summary=stage / "stage-summary.json", envelope=stage / "plan.json",
                 ledger=stage / "model-router-ledger.json")
    require(set(automated.get("source_hashes", {})) == set(paths), "automated_source_set_mismatch")
    values = {key: inputs.read(path, {"sha256": automated["source_hashes"][key]})[0]
              for key, path in paths.items()}
    report, stage_summary, plan = values["report"], values["summary"], values["envelope"]
    require(digest(plan["plan"]) == plan["sha256"] == report["plan_sha256"], "plan_seal_mismatch")
    require(values["status"].get("state") in {"complete", "incomplete_preserved", "stopped_preserved"}
            and stage_summary.get("browser_shutdown_confirmed") is True, "terminal_closed_cohort_required")
    candidate = old.summarize_candidate(report, stage_summary, plan, 32, stage.relative_to(repo).as_posix())
    require(candidate == raw["candidate"]
            and {job["task"]["persona_id"] for job in plan["plan"]["jobs"]} == EXPECTED_PERSONAS,
            "raw_candidate_or_persona_set_mismatch")
    require(sum(len(job["task"]["success_criteria"]) for job in plan["plan"]["jobs"]) == 104
            and sum(len(job["task"]["recovery_criteria"]) for job in plan["plan"]["jobs"]) == 32,
            "fresh_plan_criterion_denominator_mismatch")
    original, _ = inputs.read(repo / old.NOT_RUN)
    history, remaining = historical(repo, original)
    saved_remaining, _ = inputs.read(output / "not-run-23-baseline.json")
    require(history == raw["comparison_columns"][:4] and saved_remaining == remaining,
            "historical_columns_or_remaining_baseline_changed")
    require(len(remaining["rows"]) == 23 and len(original["rows"]) == 46,
            "baseline_denominator_mismatch")
    for key, baseline in (("baseline_23_mapping", remaining), ("baseline_46_mapping", original)):
        require(raw[key] == old.map_baseline(baseline, candidate), "raw_baseline_mapping_mismatch")
    require(old.map_baseline(original, candidate)["unique_persona_requirement_count"] == 32,
            "original_unique_baseline_denominator_mismatch")
    require((output / "comparison.md").read_text(encoding="utf-8") == reporting.render_markdown(raw),
            "raw_comparison_differs_from_summary")
    for reference in raw["sources"]:
        if "commit" not in reference:
            inputs.pin(repo / relative(reference["path"]), reference)
    require(all(raw.get("verification", {}).get(key) is True for key in
                ("terminal_queue", "prior_queues_unchanged", "zero_uncertain_resends_verified",
                 "browser_shutdown_confirmed")), "raw_integrity_verification_missing")
    reviewed, applied, seen, session_changes = apply_decisions(
        inputs, stage, raw, review, report, plan, audit)
    result = copy.deepcopy(raw)
    result["schema_version"] = "peekly-reviewed-completion-comparison.v1"
    result["candidate"] = reviewed
    result["baseline_23_mapping"] = old.map_baseline(remaining, reviewed)
    result["baseline_46_mapping"] = old.map_baseline(original, reviewed)
    result["reviewed_coverage"] = {
        "baseline_23": coverage_mapping(remaining, reviewed, seen),
        "baseline_46": coverage_mapping(original, reviewed, seen),
    }
    column = result["comparison_columns"][4]
    expected_column = reporting.comparison_column(column["label"], candidate, column["source_refs"])
    require(column == expected_column, "raw_fifth_column_mismatch")
    column["label"] = "신규32명·명시 기준 증거감사"
    for field in ("session_outcomes", "criteria_all", "criteria_by_kind"):
        column[field] = copy.deepcopy(reviewed[field])
    column["source_refs"] += [dict(review_ref, selector="decisions"),
                              dict(audit_ref, selector="audit_passed; jobs; sources")]
    require(result["comparison_columns"][:4] == raw["comparison_columns"][:4], "history_changed")
    result["independent_review"] = dict(
        schema_version="peekly-completion-applied-review.v1", semantic_review_status="listed_criteria_reviewed",
        scope=review["scope"], review_source=review_ref, raw_summary_source=raw_ref,
        artifact_audit_source=audit_ref, automated_outcome_source=automated_ref,
        decisions=applied, session_changes=session_changes,
        delta={field: {status: reviewed[field].get(status, 0) - candidate[field].get(status, 0)
                       for status in (old.OUTCOMES if field == "session_outcomes" else old.CRITERIA)}
               for field in ("session_outcomes", "criteria_all")},
        raw_receipts_modified=False, raw_finalizer_outputs_modified=False,
        unlisted_criteria_preserved=True, referenced_artifact_bytes_rechecked=True,
        observed_checkpoint_bindings_verified=True, assessment_denominator_unchanged=True,
        new_model_calls=0, new_browser_calls=0, queue_writes=0)
    result["limitations"] += [
        "Only explicitly listed criteria were independently reviewed; unlisted verdicts remain raw.",
        "The five-bin reviewed_coverage tables separate N/A from truly unassessed matches.",
        "Semantics are authored review decisions; this application verifies identities, bytes and arithmetic.",
        "A criterion-only review cannot promote a session to passed when a separate raw problem, missing final judgment or independent outcome remains.",
        "No unqualified near-zero, full product correctness, or provider-invoice claim is made."]
    existing = {(ref.get("commit"), ref["path"]) for ref in result["sources"]}
    for ref in list(inputs.files.values()) + [inputs.pin(Path(__file__))]:
        if (None, ref["path"]) not in existing:
            result["sources"].append(ref)
            existing.add((None, ref["path"]))
    contents = {"reviewed-summary.json": json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                "comparison-reviewed.md": markdown(result),
                "evidence-review.md": evidence_markdown(result)}
    publish_outputs(output, contents, inputs.unchanged)
    return dict(output=output.relative_to(repo).as_posix(), assessed_sessions=reviewed["assessed_completed_sessions"],
                listed_decisions=len(applied), changed_criteria=sum(d["changed"] for d in applied),
                session_outcomes=reviewed["session_outcomes"], criteria_all=reviewed["criteria_all"],
                old23=result["reviewed_coverage"]["baseline_23"]["weighted"],
                original46=result["reviewed_coverage"]["baseline_46"]["weighted"],
                raw_files_unchanged=True, new_model_calls=0, new_browser_calls=0, queue_writes=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--stage", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.repo, args.stage, args.output, args.review), ensure_ascii=False, sort_keys=True))
    except (ReviewError, old.ReportError, OSError, KeyError, TypeError, sqlite3.Error) as exc:
        print("Offline criterion review refused: " + str(exc), file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
