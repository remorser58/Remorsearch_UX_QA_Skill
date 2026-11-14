#!/usr/bin/env python3
"""Read-only byte/seal audit for a terminal Peekly coverage cohort.

Usage: PYTHONDONTWRITEBYTECODE=1 python3 audit_final_artifacts.py STAGE OUTPUT
No runner, browser, model, queue mutation, or old receipt rewriting occurs.
The output must be a new file outside the immutable stage.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import sqlite3
import sys


def require(ok, message):
    if not ok:
        raise ValueError(message)


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage")
    parser.add_argument("output")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo / "skills/remorsearch-ux-qa"))
    from uxresearch.canonical import digest, loads
    stage = Path(args.stage).resolve(strict=True)
    output = Path(args.output).resolve()
    require(stage.is_relative_to(repo), "stage outside repository")
    require(output.is_relative_to(repo) and not output.is_relative_to(stage),
            "output must be inside repository and outside stage")
    require(not output.exists(), "audit output already exists")
    sources = [stage / name for name in (
        "queue.sqlite", "plan.json", "report.json", "stage-summary.json",
        "model-router-ledger.json")]
    sources += [stage.parent / "run-status.json",
                stage.parent / "input-provenance.json", Path(__file__).resolve()]
    wal = stage / "queue.sqlite-wal"
    wal_existed = wal.exists()
    if wal_existed:
        sources.append(wal)
    before = {p: file_sha(p) for p in sources}
    envelope = loads((stage / "plan.json").read_bytes())
    report = loads((stage / "report.json").read_bytes())
    summary = loads((stage / "stage-summary.json").read_bytes())
    run_status = loads((stage.parent / "run-status.json").read_bytes())
    require(summary.get("browser_shutdown_confirmed") is True,
            "terminal browser shutdown summary required")
    require(run_status.get("state") not in (None, "running"),
            "cohort has not reached terminal state")
    require(digest(envelope["plan"]) == envelope["sha256"]
            == report["plan_sha256"], "plan seal mismatch")
    for key, path in (
            ("report_sha256", stage / "report.json"),
            ("summary_sha256", stage / "stage-summary.json"),
            ("router_ledger_sha256", stage / "model-router-ledger.json"),
            ("input_provenance_sha256", stage.parent / "input-provenance.json")):
        require(run_status.get(key) == before[path], "terminal provenance mismatch: " + key)
    planned = {p["id"]: p for p in envelope["plan"]["jobs"]}
    tasks = {t["job_id"]: t for t in report["tasks"]}
    require(len(planned) == len(envelope["plan"]["jobs"])
            and len(tasks) == len(report["tasks"]), "duplicate job")
    connection = sqlite3.connect((stage / "queue.sqlite").as_uri() + "?mode=ro",
                                 uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = {r["id"]: dict(r) for r in connection.execute("SELECT * FROM jobs")}
        meta = dict(connection.execute("SELECT key,value FROM meta WHERE key IN ('plan_sha','schema')"))
    finally:
        connection.close()
    require(set(planned) == set(tasks) == set(rows), "plan/report/DB job sets differ")
    require(meta.get("plan_sha") == envelope["sha256"]
            and meta.get("schema") == envelope["plan"]["schema_version"],
            "queue metadata differs from plan")
    require(not any(r["status"] == "running" for r in rows.values()),
            "queue still has running jobs")
    require(len({p["binding"]["persona_id"] for p in planned.values()}) == len(planned),
            "planned persona repeated")
    artifact_files = {}
    artifact_kinds = Counter()
    outcome_counts = Counter()
    criterion_counts = Counter()
    audited = []
    excluded = []
    sealed_results = 0
    sealed_checkpoints = 0
    first_seals = 0
    for job_id, row in sorted(rows.items(), key=lambda item: item[1]["ordinal"]):
        task, plan = tasks[job_id], planned[job_id]
        binding = plan["binding"]
        require(plan["task"]["id"] == job_id, job_id + ": task ID mismatch")
        require(task["status"] == row["status"], job_id + ": status mismatch")
        require(task["provider"] == row["provider"] == plan["provider"],
                job_id + ": provider mismatch")
        require(task["context_id"] == row["context_id"]
                == "ctx-" + digest([envelope["sha256"], job_id])[:40],
                job_id + ": context binding mismatch")
        require(task["persona_id"] == binding["persona_id"]
                == plan["task"]["persona_id"], job_id + ": persona mismatch")
        result = loads(row["result"]) if row["result"] is not None else None
        checkpoint = loads(row["checkpoint"]) if row["checkpoint"] is not None else None
        require(task.get("result") == result, job_id + ": report/result mismatch")
        if result is not None:
            require(digest(result) == row["result_sha"] == task["result_sha256"],
                    job_id + ": result seal mismatch")
            sealed_results += 1
        if checkpoint is not None:
            require(digest(checkpoint) == row["checkpoint_sha"],
                    job_id + ": checkpoint seal mismatch")
            sealed_checkpoints += 1
        R, C = result or {}, checkpoint or {}
        for label, value in (("result", R), ("checkpoint", C)):
            first = value.get("first_judgment")
            seal = value.get("first_judgment_sha256")
            if seal is not None:
                require(isinstance(first, dict) and first and digest(first) == seal,
                        job_id + ": " + label + " first judgment seal mismatch")
            else:
                require(first is None or first == {},
                        job_id + ": " + label + " nonempty first judgment lacks seal")
        require(task.get("first_judgment_sha256") == C.get("first_judgment_sha256"),
                job_id + ": report first seal mismatch")
        if R.get("operational_completed") is True:
            require(R.get("first_judgment") and R.get("first_judgment_sha256") and
                    R["first_judgment"] == C.get("first_judgment") and
                    R["first_judgment_sha256"] == C.get("first_judgment_sha256"),
                    job_id + ": missing/different completed first judgment")
        receipt = R.get("receipt")
        assessed = (row["status"] == "complete" and R.get("operational_completed") is True
                    and isinstance(receipt, dict) and task.get("current_valid") is True)
        if not assessed:
            excluded.append({"job_id": job_id, "persona_id": task["persona_id"],
                             "queue_status": row["status"], "problem": row["problem"],
                             "operational_completed": R.get("operational_completed"),
                             "current_valid": task.get("current_valid")})
            continue
        first_seals += 1
        require(receipt["task_id"] == plan["task"]["id"]
                and receipt["persona_revision"] == binding["revision"]
                and receipt["profile_sha256"] == binding["profile_sha256"]
                and receipt["build_sha256"] == envelope["plan"]["build"]["sha256"],
                job_id + ": receipt identity mismatch")
        registered = receipt.get("artifacts", [])
        ids = {a["id"] for a in registered}
        require(len(ids) == len(registered), job_id + ": duplicate artifact ID")
        manifest = []
        sessions_root = (stage / "sessions").resolve(strict=True)
        base = (sessions_root / job_id).resolve(strict=True)
        require(sessions_root.is_relative_to(stage) and base.is_relative_to(sessions_root),
                job_id + ": session escapes stage")
        evidence_root = (base / "evidence" / plan["task"]["id"] / "1").resolve(strict=True)
        require(evidence_root.is_relative_to(base), job_id + ": evidence root escapes session")
        require(R["evidence_root"] == str(base) and R["mode"] == envelope["plan"]["mode"]
                and R["ux_outcome"] == receipt["outcome"] == task["current_ux_outcome"],
                job_id + ": result binding mismatch")
        for artifact in registered:
            relative = artifact["path"]
            path = PurePosixPath(relative)
            require(not path.is_absolute() and "\\" not in relative
                    and all(p not in ("", ".", "..") for p in relative.split("/")),
                    job_id + ": unsafe artifact path")
            real = (base / relative).resolve(strict=True)
            require(real.is_relative_to(evidence_root) and real.is_file(),
                    job_id + ": artifact escapes owned evidence root")
            existing = artifact_files.get(real)
            if existing is None:
                existing = (file_sha(real), real.stat().st_size)
                artifact_files[real] = existing
            require(existing[0] == artifact["sha256"],
                    job_id + ": artifact bytes mismatch: " + relative)
            artifact_kinds[artifact["kind"]] += 1
            manifest.append({"path": relative, "sha256": existing[0], "bytes": existing[1]})
        for criterion in receipt["criteria"]:
            require(set(criterion.get("evidence_ids", [])) <= ids,
                    job_id + ": unregistered criterion evidence")
            criterion_counts[criterion["status"]] += 1
        outcome_counts[receipt["outcome"]] += 1
        audited.append({"job_id": job_id, "persona_id": task["persona_id"],
                        "result_sha256": row["result_sha"],
                        "checkpoint_sha256": row["checkpoint_sha"],
                        "first_judgment_sha256": R["first_judgment_sha256"],
                        "registered_artifacts": len(registered),
                        "artifact_manifest_sha256": digest(sorted(manifest, key=lambda m: m["path"])),
                        "all_registered_artifacts_checked": True})
    require(len(audited) == report["completed_receipt_summary"]["assessed_completed_sessions"],
            "assessed count differs from report")
    require(dict(outcome_counts) == {k: v for k, v in report["completed_receipt_summary"]
                                    ["session_outcomes"].items() if v},
            "assessed outcomes differ from report")
    require(dict(criterion_counts) == {k: v for k, v in report["completed_receipt_summary"]
                                      ["criteria_all"].items() if v},
            "assessed criteria differ from report")
    require(wal.exists() == wal_existed
            and all(p.exists() and file_sha(p) == value for p, value in before.items()),
            "input changed during read-only audit")
    value = {
        "schema_version": "peekly-artifact-byte-audit.v1",
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "stage": stage.relative_to(repo).as_posix(),
        "audit_passed": True,
        "scope": "All registered artifacts of assessed completed receipts, plus all stored result/checkpoint seals.",
        "limitations": ["Hash equality proves stored bytes, not independent visual correctness.",
                        "Excluded attempts are not credited as evaluated sessions or criteria."],
        "queue_counts": dict(Counter(r["status"] for r in rows.values())),
        "assessed_sessions": len(audited), "excluded_attempts": excluded,
        "result_seals_checked": sealed_results, "checkpoint_seals_checked": sealed_checkpoints,
        "completed_first_judgment_seals_checked": first_seals,
        "registered_artifact_references": sum(j["registered_artifacts"] for j in audited),
        "distinct_artifact_files": len(artifact_files),
        "artifact_kinds": dict(artifact_kinds),
        "artifact_bytes": sum(v[1] for v in artifact_files.values()),
        "mismatches": 0, "source_files_unchanged": True,
        "prior_queues_unchanged": run_status.get("prior_queues_unchanged"),
        "jobs": audited,
        "sources": [{"path": p.relative_to(repo).as_posix(), "sha256": value}
                    for p, value in before.items()],
        "new_model_calls": 0, "new_browser_calls": 0, "queue_writes": 0,
    }
    with output.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({k: value[k] for k in (
        "audit_passed", "assessed_sessions", "result_seals_checked",
        "checkpoint_seals_checked", "completed_first_judgment_seals_checked",
        "registered_artifact_references", "distinct_artifact_files", "mismatches",
        "source_files_unchanged", "prior_queues_unchanged")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
