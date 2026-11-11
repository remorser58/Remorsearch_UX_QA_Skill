"""Explicitly reviewed local adapters -> existing swarm receipts -> current report.

This is bounded trusted-code execution, not an OS/network sandbox. The host must
review the exact copied Python adapter and its selected inputs before approval.
No shell, package installation, automatic personas, browser or model transport.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import threading
import time

from uxresearch.canonical import EngineError, byte_digest, canonical, digest, loads
from uxresearch.storage import Store, atomic, safe_path
from .library import Library, SCHEMA as LIBRARY_SCHEMA
from . import swarm, workspace

PLAN = "ux-journey-local-plan.v1"
STATE = "ux-journey-local-state.v1"
MARKER = "local-execution.json"
DIRECTORY = "local-execution"
MAX_OUTPUT = 256 * 1024


def stop(code, reason):
    workspace.stop(code, reason, "호스트가 고정한 입력·실행 범위와 기존 근거를 확인합니다. 기존 작업을 자동 반복하지 않습니다.")


def _private(path):
    path = safe_path(path)
    if path.exists() and path.stat().st_mode & 0o077:
        stop("execution_permissions", "실행 상태와 페르소나 복사본은 비공개 경로여야 합니다.")
    return path


def _read(work):
    _private(work / MARKER)
    envelope = loads(workspace.read_file(work, MARKER))
    state = envelope.get("payload")
    if envelope.get("schema_version") != STATE or not isinstance(state, dict) or digest(state) != envelope.get("sha256"):
        stop("execution_integrity", "실행 상태의 무결성을 확인할 수 없습니다.")
    return state


def _save(work, state):
    atomic(work / MARKER, canonical(dict(schema_version=STATE, payload=state, sha256=digest(state))))


def _immutable(root, name, raw):
    dest = safe_path(root / name, root)
    dest.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _private(dest.parent)
    if dest.exists():
        if workspace.read_file(root, name) != raw:
            stop("execution_conflict", "기존 실행 파일을 덮어쓰지 않았습니다.")
    else:
        atomic(dest, raw)


def _plan(path, prepared):
    path = safe_path(path)
    plan = loads(workspace.read_file(path.parent, path.name, sensitive_check=True))
    if (not isinstance(plan, dict) or set(plan) != {"schema_version", "product_id", "runner", "timeout_seconds", "tasks"}
            or plan["schema_version"] != PLAN):
        stop("execution_plan", "호스트가 검토한 실행 계획 형식이 맞지 않습니다.")
    workspace.relative(plan["runner"])
    if (not plan["runner"].endswith(".py") or plan["runner"] not in prepared["inputs"]
            or prepared["destinations"][plan["runner"]] != "product/" + plan["runner"]):
        stop("runner_scope", "실행 어댑터가 검토하고 복사한 Python 파일이 아닙니다.")
    swarm.ident(plan["product_id"])
    swarm.number(plan["timeout_seconds"], 1, 30)
    if (not isinstance(plan["tasks"], list) or not 1 <= len(plan["tasks"]) <= 16
            or len(plan["tasks"]) * plan["timeout_seconds"] > 240):
        stop("execution_budget", "과제 수 또는 전체 실행 한도가 너무 큽니다.")
    for task in plan["tasks"]:
        if not isinstance(task, dict) or "requirement_coverage" not in task:
            stop("execution_coverage", "실행 전에 목표별 PRD 의무와 성공·복구 기준 연결을 고정해야 합니다.")
    if swarm.clean(plan) != plan:
        stop("execution_privacy", "실행 계획에 개인 식별 형식이 있습니다.")
    return plan


def _selection(library_path, prepared, plan):
    library_path = _private(library_path)
    _private(library_path / "library.json")
    raw = workspace.read_file(library_path, "library.json", sensitive_check=True)
    envelope = loads(raw)
    state = envelope.get("state")
    if not isinstance(state, dict) or state.get("schema_version") != LIBRARY_SCHEMA or digest(state) != envelope.get("sha256"):
        stop("persona_integrity", "기존 페르소나 저장소 무결성을 확인할 수 없습니다.")
    selected = dict(schema_version=LIBRARY_SCHEMA, entries={})
    for task in plan["tasks"]:
        key = Library._key(plan["product_id"], task["persona_id"])
        history = state["entries"].get(key, [])
        if not history:
            stop("persona_missing", "목표에 맞게 검토된 기존 페르소나가 없습니다. 자동 생성하지 않았습니다.")
        record = history[-1]
        # Check scope BEFORE Library validators can open PRD/research references.
        if (record.get("basis") != "synthetic" or record.get("provenance") != {"mode": "prd_hypothesis", "claim_ids": []}
                or "research_scenarios" in record.get("profile", {})):
            stop("persona_scope", "이 로컬 실행 경로는 검토한 PRD 가설만 재사용합니다. 외부 연구 근거를 자동으로 따라가지 않습니다.")
        prd = safe_path(record["context"]["prd_path"])
        source = safe_path(prepared["source"])
        if not prd.is_relative_to(source) or str(prd.relative_to(source)) not in prepared["inputs"]:
            stop("persona_scope", "페르소나 PRD가 검토한 입력 범위 밖에 있습니다.")
        if record.get("product_id") != plan["product_id"] or record.get("persona_id") != task["persona_id"]:
            stop("persona_integrity", "페르소나 식별자가 저장소 연결과 다릅니다.")
        Library(library_path)._validate(record)
        if swarm.clean(record["profile"]) != record["profile"]:
            stop("persona_privacy", "페르소나에 개인 식별 형식이 있습니다.")
        selected["entries"][key] = [copy.deepcopy(record)]
    return byte_digest(raw), dict(state=selected, sha256=digest(selected))


class _SelectedLibrary:
    """Read-only validated selection for preflight; never lock/write the original."""
    def __init__(self, selected):
        self.selected = selected

    def get(self, product, persona, revision=None, revalidate=True):
        record = self.selected["state"]["entries"][Library._key(product, persona)][-1]
        if revision is not None and record["revision"] != revision:
            stop("stale_persona_revision", "페르소나 버전이 달라졌습니다.")
        return copy.deepcopy(record)


def _copy_scope(work, prepared):
    """Inspect only the owned copy's names; never walk the original or follow links."""
    expected = set()
    for name in prepared["destinations"].values():
        path = Path(name)
        if path.parts[0] != "product":
            continue
        while path != Path("."):
            expected.add(path.as_posix())
            path = path.parent
    pending = ["product"]
    while pending:
        name = pending.pop()
        with os.scandir(safe_path(work / name, work)) as entries:
            for entry in entries:
                relative = name + "/" + entry.name
                if relative not in expected or entry.is_symlink():
                    stop("reviewed_copy_scope", "복사본에 검토하지 않은 파일·디렉터리·링크가 있습니다. 삭제하거나 실행하지 않았습니다.")
                if entry.is_dir(follow_symlinks=False):
                    pending.append(relative)


def _verify(work, prepared, state):
    _copy_scope(work, prepared)
    workspace._verify(work, prepared)
    if byte_digest(workspace.read_file(work, "workspace.json")) != state["workspace_sha256"]:
        stop("execution_build", "실행에 연결된 준비 상태가 달라졌습니다.")
    current_hash, selected = _selection(Path(state["library"]), prepared, state["plan"])
    if current_hash != state["library_sha256"] or selected != state["personas"]:
        stop("execution_persona_changed", "실행을 고정한 뒤 기존 페르소나 저장소가 변경됐습니다.")
    if state["phase"] == "ready":
        _private(work / DIRECTORY)
        _private(work / DIRECTORY / "personas")
        if loads(workspace.read_file(work, DIRECTORY + "/personas/library.json")) != selected:
            stop("execution_persona_changed", "복사한 페르소나 버전이 변경됐습니다.")


def _initialize(work, prepared, library_path, input_path, approved):
    if not approved:
        stop("runner_approval", "호스트의 정확한 코드·범위 검토 확인이 없어 실행하지 않았습니다.")
    if library_path is None or input_path is None:
        stop("execution_input", "호스트가 기존 페르소나와 목표·기준을 연결해야 합니다. 사용자가 매니페스트를 작성할 필요는 없습니다.")
    if prepared["saved"]:
        stop("prior_run_preserved", "기존 실험이 있는 작업공간에서 실행 한도를 초기화하지 않습니다. 검토된 replay 흐름을 사용합니다.")
    plan = _plan(input_path, prepared)
    library_path = safe_path(library_path)
    if library_path.is_relative_to(work) or work.is_relative_to(library_path):
        stop("execution_overlap", "기존 페르소나 저장소와 실행 작업공간은 분리되어야 합니다.")
    library_hash, personas = _selection(library_path, prepared, plan)
    build_hash = byte_digest(workspace.read_file(work, "workspace.json"))
    spec = dict(schema_version=swarm.SCHEMA, product_id=plan["product_id"],
                build=dict(id="reviewed-" + build_hash[:16], artifact_path=str(work / "workspace.json"), sha256=build_hash),
                max_parallel=1, lease_seconds=120, max_attempts=1, tasks=plan["tasks"])
    seed = swarm._prepare_plan(_SelectedLibrary(personas), spec)
    if (work / DIRECTORY).exists():
        stop("execution_conflict", "기존 파일이 있는 실행 폴더를 사용하지 않았습니다.")
    state = dict(plan=plan, library=str(library_path), library_sha256=library_hash, personas=personas,
                 workspace_sha256=build_hash, seed=seed, phase="preparing", dispatches={})
    _save(work, state)  # Durable ownership and fixed criteria before any run files.
    return state


def _finish_preparation(work, state):
    base = _private(work / DIRECTORY)
    base.mkdir(mode=0o700, exist_ok=True)
    if set(p.name for p in base.iterdir()) - {"personas", "run"}:
        stop("execution_conflict", "실행 준비 폴더에 소유하지 않은 파일이 있습니다.")
    _immutable(base, "personas/library.json", canonical(state["personas"]))
    if set(p.name for p in (base / "personas").iterdir()) - {"library.json", "engine.lock"}:
        stop("execution_conflict", "페르소나 복사 폴더에 소유하지 않은 파일이 있습니다.")
    run = _private(base / "run")
    if not run.exists():
        swarm._create_plan(run, state["seed"])
    elif not (run / "swarm-state.json").exists():
        # Recover only our empty interrupted mkdir, never prior evidence/state.
        if set(p.name for p in run.iterdir()) - {"engine.lock", "evidence"}:
            stop("execution_conflict", "실행 준비 도중 기존 파일을 발견했습니다.")
        evidence = _private(run / "evidence")
        evidence.mkdir(mode=0o700, exist_ok=True)
        if any(evidence.iterdir()):
            stop("execution_conflict", "초기 상태 없이 남은 근거를 덮어쓰지 않았습니다.")
        with Store(run):
            swarm._save(run, state["seed"])
    else:
        with Library(base / "personas") as library:
            with Store(run):
                if swarm._load(run, library, expire_leases=False) != state["seed"]:
                    stop("execution_conflict", "준비가 끝나기 전에 실행 상태가 바뀌었습니다.")
    state["phase"] = "ready"
    _save(work, state)


@contextmanager
def _cancellation():
    prior = {}
    if threading.current_thread() is threading.main_thread():
        def cancel(*_):
            raise KeyboardInterrupt
        for sig in (signal.SIGTERM, signal.SIGINT):
            prior[sig] = signal.signal(sig, cancel)
    try:
        yield
    finally:
        for sig, handler in prior.items():
            signal.signal(sig, handler)


def _stop_owned(process):
    # Only the Popen child owned by this call, never groups or saved/reused PIDs.
    # Reviewed adapters must not launch background workers; this is not a sandbox.
    try:
        if process.poll() is not None:
            return True
        process.terminate()
        try:
            process.wait(timeout=0.3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=0.5)
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def _invoke(runner, cwd, request, seconds, on_spawn):
    payload = canonical(request)
    if len(payload) > MAX_OUTPUT:
        stop("execution_request", "실행 요청이 허용 크기를 넘었습니다.")
    start, process, output, error = time.monotonic(), None, bytearray(), bytearray()
    problem, cleanup_confirmed = None, True
    try:
        with _cancellation(), selectors.DefaultSelector() as selector:
            process = subprocess.Popen([sys.executable, "-I", "-S", "-B", str(runner)], cwd=cwd,
                env={"PATH": os.defpath, "HOME": str(cwd), "TMPDIR": str(cwd), "LANG": "C", "LC_ALL": "C"},
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True, close_fds=True)
            on_spawn()
            for pipe, events in ((process.stdin, selectors.EVENT_WRITE), (process.stdout, selectors.EVENT_READ), (process.stderr, selectors.EVENT_READ)):
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, events)
            offset = 0
            while selector.get_map():
                remaining = seconds - (time.monotonic() - start)
                if remaining <= 0:
                    problem = "timeout"
                    break
                for key, _ in selector.select(min(remaining, 0.05)):
                    pipe = key.fileobj
                    if pipe is process.stdin:
                        try:
                            offset += os.write(pipe.fileno(), payload[offset:offset + 16384])
                        except BrokenPipeError:
                            offset = len(payload)
                        if offset == len(payload):
                            selector.unregister(pipe)
                            pipe.close()
                    else:
                        chunk = os.read(pipe.fileno(), 16384)
                        if not chunk:
                            selector.unregister(pipe)
                            pipe.close()
                        else:
                            (output if pipe is process.stdout else error).extend(chunk)
                            if len(output) + len(error) > MAX_OUTPUT:
                                problem = "output_limit"
                                break
                if problem:
                    break
            if not problem:
                try:
                    process.wait(timeout=max(0.001, seconds - (time.monotonic() - start)))
                except subprocess.TimeoutExpired:
                    problem = "timeout"
    except KeyboardInterrupt:
        problem = "cancelled"
    except OSError:
        problem = "process_unavailable"
    finally:
        if process is not None:
            cleanup_confirmed = _stop_owned(process)
            for pipe in (process.stdin, process.stdout, process.stderr):
                if pipe is not None and not pipe.closed:
                    pipe.close()
    if not problem and process.returncode != 0:
        problem = "nonzero_exit"
    return bytes(output), dict(problem=problem, cleanup_confirmed=cleanup_confirmed, returncode=process.returncode if process else None,
        elapsed_seconds=round(time.monotonic() - start, 6), stdout_bytes=len(output), stderr_bytes=len(error),
        stdout_sha256=byte_digest(output), stderr_sha256=byte_digest(error))


def _observation(raw, binding, task):
    if workspace.SECRET.search(raw):
        stop("observation_private", "실행 출력에 비밀 형식이 있어 원문을 저장하지 않았습니다.")
    doc = loads(raw)
    if (not isinstance(doc, dict) or set(doc) != {"schema_version", "binding", "reason", "steps", "criteria"}
            or doc["schema_version"] != "ux-journey-observation.v1" or doc["binding"] != binding):
        stop("observation_binding", "관측이 현재 과제·시도·빌드·페르소나와 일치하지 않습니다.")
    swarm.text(doc["reason"])
    if not isinstance(doc["steps"], list) or not 1 <= len(doc["steps"]) <= 256:
        stop("observation_steps", "실제 수행 단계가 없습니다.")
    for step in doc["steps"]:
        if not isinstance(step, dict) or set(step) != {"action", "observation"}:
            stop("observation_steps", "관측 단계 형식이 맞지 않습니다.")
        swarm.text(step["action"])
        swarm.text(step["observation"])
    expected = {(kind, i) for kind in ("success", "recovery") for i in range(len(task[kind + "_criteria"]))}
    if not isinstance(doc["criteria"], list) or len(doc["criteria"]) != len(expected):
        stop("observation_criteria", "고정한 성공·복구 기준마다 실제 관측 또는 미실행 사유가 필요합니다.")
    seen = set()
    for row in doc["criteria"]:
        if (not isinstance(row, dict) or set(row) != {"kind", "index", "status", "observation"}
                or type(row["index"]) is not int or row["status"] not in {"passed", "failed", "not_run"}
                or (row["kind"], row["index"]) not in expected or (row["kind"], row["index"]) in seen):
            stop("observation_criteria", "관측 기준이 누락·중복되거나 고정한 기준과 다릅니다.")
        seen.add((row["kind"], row["index"]))
        swarm.text(row["observation"])
    if swarm.clean({k: doc[k] for k in ("reason", "steps", "criteria")}) != {k: doc[k] for k in ("reason", "steps", "criteria")}:
        stop("observation_private", "관측에 개인 식별 형식이 있어 원문을 저장하지 않았습니다.")
    return doc


def _record(work, library, state, claim, request, raw, diagnostic):
    run = work / DIRECTORY / "run"
    receipt = swarm.receipt_starter(library, run, claim)
    receipt.pop("drafting_guidance")
    receipt["schema_version"] = "ux-persona-swarm-receipt.v1"
    observation = None
    if diagnostic["problem"] is None:
        try:
            observation = _observation(raw, request["binding"], claim["task"])
        except (EngineError, ValueError, KeyError, TypeError, AttributeError):
            diagnostic["problem"] = "invalid_or_private_observation"
    evidence = dict(schema_version="ux-journey-execution-log.v1", binding=request["binding"], diagnostic=diagnostic,
                    observation=observation, ui_observed=False, real_user_evidence=False)
    log = Path(claim["evidence_path"]) / "observation.json"
    log_raw = canonical(evidence)
    _immutable(run, str(log.relative_to(run)), log_raw)
    receipt["artifacts"] = [dict(id="execution", kind="execution_log", path=str(log.relative_to(run)), sha256=byte_digest(log_raw))]
    if observation:
        receipt["steps"] = [{**step, "evidence_ids": ["execution"]} for step in observation["steps"]]
        receipt["criteria"] = [{**row, "evidence_ids": [] if row["status"] == "not_run" else ["execution"]} for row in observation["criteria"]]
        receipt["outcome"] = "failed" if any(row["status"] == "failed" for row in observation["criteria"]) else "inconclusive"
        receipt["reason"] = observation["reason"] if receipt["outcome"] == "failed" else "Local core observations recorded; UI and real-user behavior remain unobserved."
    else:
        receipt["outcome"] = "inconclusive"
        receipt["reason"] = "Local execution could not supply valid observations: " + diagnostic["problem"] + ". No product verdict."
        for row in receipt["criteria"]:
            row["observation"] = "No valid observation; infrastructure uncertainty."
    swarm.record(library, run, receipt)


def _reconcile(state, current):
    """ACK recovery only: never convert dispatch intent into permission to spawn."""
    changed = False
    rows = {row["task_id"]: row for row in current["tasks"]}
    for task_id, dispatch in state["dispatches"].items():
        row = rows[task_id]
        if dispatch["phase"] == "intent" and row["result"] is not None:
            if row["attempts"] != dispatch["claim"]["attempt"] or row["operation_id"] != dispatch["claim"]["operation_id"]:
                stop("execution_attempt", "실행 시도 연결이 달라졌습니다.")
            dispatch["phase"] = "recorded"
            changed = True
    return changed


def execute(work, *, library_path=None, input_path=None, approved=False, fault=None):
    work = safe_path(work)
    if not (work / "workspace.json").is_file():
        stop("workspace_missing", "대상 코드를 먼저 안전하게 준비해야 합니다.")
    if work.stat().st_mode & 0o022:
        stop("workspace_permissions", "다른 사용자가 쓸 수 있는 작업공간에서는 실행하지 않습니다.")
    with Store(work):
        prepared = workspace._state(work)
        if prepared["phase"] != "ready":
            stop("preparation_interrupted", "입력 준비가 끝나지 않았습니다. 같은 start로 먼저 준비를 이어갑니다.")
        _copy_scope(work, prepared)
        workspace._verify(work, prepared)
        state = _read(work) if (work / MARKER).exists() else _initialize(work, prepared, library_path, input_path, approved)
        if input_path is not None and _plan(input_path, prepared) != state["plan"]:
            stop("execution_contract", "실행을 고정한 뒤 목표·기준·어댑터를 바꿀 수 없습니다.")
        if library_path is not None and str(safe_path(library_path)) != state["library"]:
            stop("execution_contract", "기존 실행과 다른 페르소나 저장소입니다.")
        _verify(work, prepared, state)
        if state["phase"] == "preparing":
            _finish_preparation(work, state)
        with Library(work / DIRECTORY / "personas") as library:
            run = work / DIRECTORY / "run"
            current = swarm.report(library, run)
            if _reconcile(state, current):
                _save(work, state)
            # Includes a crash between claim and journal: attempts are never reset.
            if any(row["attempts"] and row["result"] is None for row in current["tasks"]):
                return report_locked(work, prepared, state, current)
            for task in state["plan"]["tasks"]:
                if next(row for row in current["tasks"] if row["task_id"] == task["id"])["status"] != "pending":
                    continue
                _verify(work, prepared, state)
                claim = swarm.claim(library, run, "reviewed-local-runner", task["id"])
                if not claim["claimed"]:
                    break
                dispatch = dict(phase="intent", spawned=False, claim=claim)
                state["dispatches"][task["id"]] = dispatch
                _save(work, state)
                if fault:
                    fault("intent")
                cwd = safe_path(Path(claim["evidence_path"]) / "scratch", run)
                cwd.mkdir(mode=0o700)
                binding = dict(task_id=task["id"], attempt=claim["attempt"], operation_id=claim["operation_id"],
                               build_sha256=claim["build"]["sha256"], **claim["binding"])
                request = dict(schema_version="ux-journey-request.v1", binding=binding, task=claim["task"],
                               profile=claim["profile"], requirement_context=claim["requirement_context"], source=str(work / "product"))
                def spawned():
                    dispatch["spawned"] = True
                    _save(work, state)
                raw, diagnostic = _invoke(work / "product" / state["plan"]["runner"], cwd, request, state["plan"]["timeout_seconds"], spawned)
                if not diagnostic["cleanup_confirmed"]:
                    stop("execution_cleanup", "소유 실행 프로세스의 종료를 확인하지 못했습니다. 결과를 확정하거나 다음 과제를 시작하지 않았습니다.")
                _verify(work, prepared, state)
                _record(work, library, state, claim, request, raw, diagnostic)
                if fault:
                    fault("recorded")
                dispatch.update(phase="recorded", diagnostic=diagnostic)
                _save(work, state)
                current = swarm.report(library, run)
                if diagnostic["problem"]:
                    break
            return report_locked(work, prepared, state, current)


def report_locked(work, prepared, state=None, current=None):
    state = state or _read(work)
    _verify(work, prepared, state)
    if current is None and state["phase"] == "ready":
        with Library(work / DIRECTORY / "personas") as library:
            current = swarm.report(library, work / DIRECTORY / "run")
    tasks = []
    for task in state["plan"]["tasks"]:
        row = next((row for row in (current or {}).get("tasks", []) if row["task_id"] == task["id"]), None)
        tasks.append(dict(goal=task["goal"], starting_state=task["starting_state"], actions=task["actions"],
            success_criteria=task["success_criteria"], recovery_criteria=task["recovery_criteria"],
            **(row or dict(task_id=task["id"], persona_id=task["persona_id"], status="pending", attempts=0, result=None, reason="Preparation interrupted."))))
    uncertain = [row["task_id"] for row in tasks if row["attempts"] and row["result"] is None]
    quarantined = [row["task_id"] for row in tasks if row.get("resource_quarantined")]
    personas = [{k: record[k] for k in ("persona_id", "revision", "profile_sha256", "basis")} |
                {"label": record["profile"]["label"], "provenance_mode": record["provenance"]["mode"], "prd_sha256": record["context"]["prd_sha256"]}
                for history in state["personas"]["state"]["entries"].values() for record in history]
    counts = current["counts"] if current else {k: len(tasks) if k == "pending" else 0 for k in ("pending", "running", "passed", "failed", "blocked", "inconclusive", "skipped")}
    summary = dict(schema_version="ux-journey-run-report.v1", preparation_complete=True,
        execution_performed=True if any(row["spawned"] for row in state["dispatches"].values()) else (None if uncertain else False),
        execution_complete=not uncertain and counts["pending"] == 0 and counts["running"] == 0,
        uncertain_dispatches=uncertain, quarantined_tasks=quarantined, counts=counts, tasks=tasks, personas_reused=personas,
        source_files=prepared["source_files"], plan_sha256=digest(state["plan"]), workspace_sha256=state["workspace_sha256"],
        evidence_kind="owned_local_core_observations", ui_observed=False, real_user_evidence=False, product_ready=False,
        coverage=current["coverage_summary"] if current else None,
        next_action=("중단된 실행의 실제 프로세스·근거·영향을 호스트가 먼저 확인해야 합니다. 자동 재실행하지 않습니다." if uncertain else
                     "쓰기 결과가 불확실한 자원이 격리되어 있습니다. 호스트가 실제 상태를 검사하고 기존 settle 규칙을 적용하기 전에는 같은 자원을 재사용하지 않습니다." if quarantined else
                     "남은 과제가 있습니다. 실행 장애를 확인한 뒤 같은 run으로 아직 시작하지 않은 과제만 이어갑니다." if counts["pending"] else
                     "관측된 실패를 재현하고 수정 후보를 별도 검토합니다. 실제 UI·사용자 검증이 남아 있습니다."),
        limitations=["재사용한 페르소나는 PRD 기반 합성 가설이며 실제 참가자가 아닙니다.",
                     "관측은 명시적으로 검토한 로컬 어댑터의 코어 실행 범위입니다. UI·서비스 수용·실사용자 효과를 검증하지 않았습니다.",
                     "어댑터 실행은 OS·네트워크 샌드박스가 아닙니다. 호스트의 코드·소유 입력 검토가 필수입니다.",
                     "검토한 단일 Python 프로세스만 지원합니다. 별도 자식·백그라운드 작업을 실행하는 어댑터는 지원하지 않습니다.",
                     "해시와 receipt는 연결·무결성을 검사하며 어댑터 관측의 진실성이나 PRD 해석의 완전성을 증명하지 않습니다.",
                     "실패 없는 코어 관측도 최종 통과가 아닙니다. 미실행 기준과 근거 부족을 그대로 표시합니다."])
    return workspace.publish_report(work, summary, render(summary))


def render(summary):
    def text(value):
        return str(value).replace("|", "\\|").replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;")
    labels = dict(failed="실패", inconclusive="판정 보류", pending="대기", running="실행 확인 필요", blocked="차단", skipped="미실행", passed="통과")
    c = summary["counts"]
    lines = ["# 사용자 목표별 로컬 QA 결과", "", f"실패 {c['failed']} · 판정 보류 {c['inconclusive']} · 대기 {c['pending']} · 통과 {c['passed']}.",
             "실제 UI와 사용자 효과는 미검증입니다. 코어 실행 완료와 제품 통과를 구분합니다.", "", "## 재사용한 페르소나", ""]
    for persona in summary["personas_reused"]:
        lines.append(f"- {text(persona['label'])} — {persona['persona_id']} v{persona['revision']}, PRD 합성 가설, profile `{persona['profile_sha256']}`")
    for task in summary["tasks"]:
        lines += ["", "## " + text(task["goal"]), "", f"결과: {labels[task['status']]} · 시도 {task['attempts']} · {task['task_id']} / {task['persona_id']}",
                  "시작 상태: " + text(task["starting_state"]), "판정 근거: " + text(task["reason"])]
        result = task["result"]
        observed = {(row["kind"], row["index"]): row for row in result["criteria"]} if result else {}
        lines += ["", "| 고정한 기준 | 관측 상태 | 관측 / 미실행 사유 |", "| --- | --- | --- |"]
        for kind in ("success", "recovery"):
            for index, criterion in enumerate(task[kind + "_criteria"]):
                row = observed.get((kind, index), dict(status="not_run", observation="관측 없음"))
                lines.append(f"| {text(criterion)} | {row['status']} | {text(row['observation'])} |")
        if result:
            lines += ["", "재현 단계 및 근거:", ""]
            lines += ["- " + text(step["action"]) + ": " + text(step["observation"]) for step in result["steps"]]
            lines += [f"- [실행 근거](../{DIRECTORY}/run/{artifact['path']}) · SHA-256 `{artifact['sha256']}`" for artifact in result["artifacts"]]
    lines += ["", "## 다음 단계", "", summary["next_action"], "", "## 검증 경계", ""]
    lines += ["- " + row for row in summary["limitations"]]
    return "\n".join(lines) + "\n"
