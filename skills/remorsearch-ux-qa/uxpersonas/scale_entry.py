"""Host-resolved entry from a goal and saved personas to a reviewable swarm.

The user supplies product and goal. Provider routing, current source checks,
owned tools and Python bindings are host work. This entry never approves cost.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import copy

from uxresearch.canonical import byte_digest, canonical, digest
from uxresearch.storage import atomic, read_bytes, read_json, safe_path
from .agent_run import Tool, _host_info
from . import swarm
from .swarm_queue import Queue, SCHEMA, bounded, fail, quote


@dataclass(frozen=True)
class ScaleLimits:
    parallel: int = 4
    turns: int = 12
    call_seconds: int = 30
    task_seconds: int = 600
    lease_seconds: int = 60
    budget_microusd: int = 0
    max_model_calls: int = 10000

    def validate(self):
        for name, low, high in (("parallel", 1, 64), ("turns", 1, 24),
                ("call_seconds", 1, 180), ("task_seconds", 1, 3600),
                ("lease_seconds", 10, 600), ("budget_microusd", 0, 10**12),
                ("max_model_calls", 1, 50000)):
            bounded(getattr(self, name), low, high, name)
        return vars(self).copy()


def engine_manifest():
    root = Path(__file__).resolve().parent
    files = ("swarm_queue.py", "swarm_providers.py", "model_router.py", "scale_run.py", "scale_entry.py", "scale_report.py",
             "agent_run.py", "swarm.py", "library.py")
    return {name: byte_digest(read_bytes(root / name)) for name in files}


def prepare_scale_goal(library, run_path, providers, tool_host, tools, *, product_id,
                       target, goal, build, limits=ScaleLimits(), persona_ids=None,
                       assignments=None, credential_scopes=None, reviewed=False,
                       tool_provenance="authored_fixture", billing_reviews=None,
                       provider_destinations=None):
    if reviewed is not True:
        fail("review_required", "The host must review task fit, current persona sources, data destinations and owned tools.")
    swarm.ident(product_id)
    swarm.text(target)
    swarm.text(goal)
    if swarm.clean(goal) != goal:
        fail("goal_privacy", "Supply a goal without personal identifiers.")
    if tool_provenance not in {"authored_fixture", "owned_browser", "reviewed_host_tools"}:
        fail("tool_provenance", "Name the actual tool evidence origin.")
    limits_dict = limits.validate()
    build = swarm._build(build)
    host_info = _host_info(tool_host)
    if not host_info["parallel_safe"] and limits.parallel != 1:
        fail("tool_parallel", "This tool host requires a serial plan.")
    if not providers or not isinstance(providers, dict):
        fail("provider_required", "A reviewed provider route is required; no default paid provider is chosen.")
    modes = {provider.mode for provider in providers.values()}
    if len(modes) != 1 or not modes <= {"fixture", "live"}:
        fail("mixed_provenance", "Fixture and actual-provider execution require separate runs.")
    mode = next(iter(modes))
    if host_info["mode"] != ("fixture" if mode == "fixture" else "model_tools"):
        fail("mixed_provenance", "The tool host must disclose the same execution mode as the plan.")
    specs = {}
    credential_scopes = credential_scopes or {}
    billing_reviews = billing_reviews or {}
    provider_destinations = provider_destinations or {}
    for key, provider in sorted(providers.items()):
        swarm.ident(key)
        spec = provider.spec.validate()
        if spec["key"] != key:
            fail("provider_binding", "Provider routing key differs from its reviewed specification.")
        scope = credential_scopes.get(key, "offline-no-credential" if mode == "fixture" else None)
        if not scope or not isinstance(scope, str) or len(scope) > 160:
            fail("credential_scope", "Resolve a non-secret account scope before presenting paid-call approval.")
        destination = spec["endpoint"] or provider_destinations.get(key, "offline authored callback" if mode == "fixture" else None)
        review = copy.deepcopy(billing_reviews.get(key, {}))
        if mode == "live":
            fields = ("input_token_cap", "output_token_cap", "input_price_per_million", "output_price_per_million")
            if (not isinstance(destination, str) or not destination.strip()
                    or not isinstance(review, dict) or any(review.get(name) != spec[name] for name in fields)
                    or review.get("no_unpriced_features") is not True
                    or not isinstance(review.get("source"), str) or not review["source"].strip()
                    or not isinstance(review.get("checked_at"), str) or not review["checked_at"].strip()):
                fail("billing_review_required", "Resolve documented model context limits, current prices, unpriced features and provider destination before live preparation.")
            if spec["input_price_per_million"] == 0 or spec["output_price_per_million"] == 0:
                if not (key == "local-router" and spec["protocol"] == "callback"
                        and spec["model"] == "tokenmaxx-deepseek-v4-1-flash-free"
                        and spec["input_price_per_million"] == 0 and spec["output_price_per_million"] == 0
                        and review.get("free_tier") is True
                        and review.get("billing_source") == "free"
                        and review.get("requested_model") == "TOKENMAXX/deepseek-v4.1-flash-free"):
                    fail("billing_review_required", "Zero-priced live routes require the exact reviewed free TOKENMAXX model and billing source.")
        specs[key] = dict(spec=spec, mode=mode, adapter_sha256=provider.adapter_sha256, credential_scope=scope,
                         destination=destination, billing_review=review)
    tools = [tool.spec() for tool in tools]
    if not 1 <= len(tools) <= 16 or len({t["name"] for t in tools}) != len(tools):
        fail("tool_scope", "Select one to sixteen uniquely named owned tools.")
    candidates = library.list(product_id)["personas"]
    eligible = {p["persona_id"]: p for p in candidates if p["reusable"]}
    selected = sorted(eligible) if persona_ids is None else list(persona_ids)
    if (not 1 <= len(selected) <= 1000 or len(selected) != len(set(selected))
            or any(pid not in eligible for pid in selected)):
        fail("personas_required", "Select current saved personas. Missing or stale personas are not cloned to inflate session count.")
    assignments = assignments or {pid: list(specs)[i % len(specs)] for i, pid in enumerate(selected)}
    if set(assignments) != set(selected) or any(key not in specs for key in assignments.values()):
        fail("provider_binding", "Every selected persona needs exactly one reviewed provider assignment.")
    # Identical profiles retain independent execution but do not become diverse
    # research evidence merely through new IDs or labels.
    behavioral_hashes, jobs = [], []
    for pid in selected:
        profile = library.get(product_id, pid, eligible[pid]["revision"])
        requirements = [r for r in profile["context"]["requirements"] if r["id"] in profile["profile"]["requirement_ids"]]
        if not 1 <= len(requirements) <= 16:
            fail("requirement_scope", "Review one to sixteen applicable requirements per persona.")
        # Typed internal identifiers contain no digit runs that could resemble
        # phone/account identifiers in the existing whole-task privacy gate.
        jid = "S-" + digest([product_id, pid, profile["revision"], goal, build])[:24].translate(
            str.maketrans("0123456789abcdef", "abcdefghijklmnop"))
        task = dict(id=jid, persona_id=pid, requirement_ids=[r["id"] for r in requirements], goal=goal,
            starting_state="Fresh isolated owned context for the reviewed product.",
            actions=["Choose a permitted next action from your own current observations."],
            decisions=copy.deepcopy(profile["profile"]["behaviors"]),
            success_criteria=[r["excerpt"] for r in requirements],
            recovery_criteria=["Exercise an applicable safe recovery and verify it; otherwise report not_run."],
            data_namespace=jid, resource_id=jid,
            side_effects="owned_fixture_write" if any(t["effect"] == "owned_fixture_write" for t in tools) else "read_only",
            stop_conditions=["Stop at real accounts, payment, unapproved resources, uncertain effects or exhausted limits."],
            requirement_coverage=[dict(requirement_id=r["id"], obligations=[dict(id=f"O-PRD-{i+1}", description=r["excerpt"],
                criterion_refs=[dict(kind="success", index=i)], exclusion_reason=None)]) for i, r in enumerate(requirements)])
        # Reuse the existing plan/PRD/research gates in bounded single-task chunks;
        # the new queue, not a raised old eight-worker constant, schedules them.
        prepared = swarm._prepare_plan(library, dict(schema_version=swarm.SCHEMA, product_id=product_id,
            build=build, max_parallel=1, lease_seconds=30, max_attempts=1, tasks=[task]))
        entry = prepared["tasks"][0]
        jobs.append(dict(id=jid, provider=assignments[pid], task=entry["task"], binding=entry["binding"]))
        behavioral_hashes.append(digest({k: v for k, v in profile["profile"].items() if k != "label"}))
    limits_dict["max_model_calls"] = min(limits.max_model_calls, len(jobs) * (limits.turns + 1))
    plan = dict(schema_version=SCHEMA, mode=mode, library_path=str(library.root), product_id=product_id,
        target=target, goal=goal, build=build, limits=limits_dict, providers=specs, tools=tools,
        tool_host=host_info, tool_provenance=tool_provenance, jobs=jobs, engine_manifest=engine_manifest(),
        diversity=dict(distinct_saved_personas=len(jobs), distinct_behavioral_profiles=len(set(behavioral_hashes)),
                       population_representativeness=False),
        evidence_policy="current_sources_own_observations_png_and_native_checks_no_peer_answers")
    run = safe_path(run_path)
    # Reservation is held by the caller's Library single-writer context. A new
    # folder cannot silently reset the same goal's unknown effects or budget.
    reservation = library.root / "scale-goals.json"
    saved = {}
    if reservation.exists():
        envelope = read_json(reservation, private=True)
        if envelope.get("schema_version") != SCHEMA or digest(envelope.get("payload")) != envelope.get("sha256"):
            fail("goal_integrity", "The goal reservation changed; preserve it for inspection.")
        saved = envelope["payload"]
    key = digest(dict(product_id=product_id, target=target, goal=goal, build=build, mode=mode,
                      personas=[j["binding"] for j in jobs]))
    if key in saved:
        record = saved[key]
        if record != dict(run=str(run), plan_sha256=digest(plan)):
            fail("goal_reserved", "This goal and persona set already has a run. Review it instead of resetting budget or uncertain sends.")
        if not (run / "queue.sqlite").exists():
            fail("partial_goal", "The reserved run was interrupted during creation; preserve and inspect its files.")
        queue = Queue(run)
        if queue.plan_sha256 != digest(plan):
            fail("plan_integrity", "The reserved run no longer matches the reviewed plan.")
        return queue
    if run.exists():
        fail("run_exists", "The destination already exists and will not be replaced.")
    saved[key] = dict(run=str(run), plan_sha256=digest(plan))
    atomic(reservation, canonical(dict(schema_version=SCHEMA, payload=saved, sha256=digest(saved))))
    return Queue.create(run, plan)


def preview(queue):
    plan = queue.plan
    rows = []
    maximum = 0
    for key, provider in plan["providers"].items():
        sessions = sum(job["provider"] == key for job in plan["jobs"])
        calls = sessions * (plan["limits"]["turns"] + 1)
        cost = calls * quote(provider["spec"])
        maximum += cost
        rows.append(dict(provider=key, model=provider["spec"]["model"], destination=provider.get("destination", provider["spec"]["endpoint"]),
            credential_scope=provider["credential_scope"], sessions=sessions,
            concurrency=provider["spec"]["concurrency"], request_ceiling=calls, conservative_microusd=cost))
    return dict(plan_sha256=queue.plan_sha256, mode=plan["mode"], sessions=len(plan["jobs"]),
        parallel_calls=plan["limits"]["parallel"], provider_routes=rows,
        approved_budget_microusd=plan["limits"]["budget_microusd"],
        full_run_conservative_microusd=maximum,
        may_stop_before_all_sessions=maximum > plan["limits"]["budget_microusd"],
        data_sent="Each persona's scrubbed profile, cited requirements, allowed tool schema and own observations only.",
        diversity=plan["diversity"], tool_provenance=plan["tool_provenance"],
        cost_approval_required=plan["mode"] == "live",
        no_automatic_retry_after_uncertain_send=True,
        next_action="실제 실행은 이 계획과 최대 비용을 확인한 사용자 승인 후 시작합니다." if plan["mode"] == "live"
                    else "유료 호출 없는 모의 실행입니다. 실제 모델 성능·사용자 효과를 입증하지 않습니다.")


def render_status(report):
    counts, budget = report["counts"], report["budget"]
    title = "모의 페르소나 실행" if report["mode"] == "fixture" else "실제 모델 페르소나 실행"
    lines = [f"# {title}", "",
        f"전체 {report['total_sessions']} · 완료 {counts['complete']} · 실행 {counts['running']} · 대기 {counts['queued']}",
        f"확인 필요 {counts['uncertain']} · 중단 {counts['blocked']} · 취소 {counts['cancelled']}",
        f"비용: 기록/보수적 정산 USD {budget['charged_or_settled']/1000000:.6f} · 예약 USD {budget['reserved']/1000000:.6f} · 한도 USD {budget['ceiling']/1000000:.6f}",
        f"실제 모델 완료 호출 {report['actual_model_calls']} · 작성된 모의 응답 {report['authored_model_calls']}",
        "", report["next_action"], "", "실행 완료는 제품 UX 통과나 실제 사용자 효과를 의미하지 않습니다.", ""]
    validation = report.get("evidence_validation")
    if validation:
        outcomes = validation["ux_outcomes"]
        lines += [f"현재 근거: 유효 {validation['current_valid_sessions']} · 확인 필요 {validation['blocked_sessions']} · 미관측 {validation['unassessed_sessions']}",
                  f"현재 과업 관측: 통과 {outcomes['passed']} · 실패 {outcomes['failed']} · 판정 보류 {outcomes['inconclusive']}", ""]
    status_names = {"queued": "대기", "running": "실행 중", "complete": "실행 완료", "blocked": "중단", "uncertain": "결과 확인 필요", "cancelled": "취소"}
    outcomes_ko = {"passed": "관측 기준 통과", "failed": "실패 관측", "inconclusive": "판정 보류", "blocked": "검증 중단", "skipped": "미실행"}
    for task in report["tasks"]:
        result = task.get("result") or {}
        verdict = ("원본 자료 또는 관측 근거를 다시 확인해야 합니다" if task.get("current_valid") is False
                   else outcomes_ko.get(result.get("ux_outcome"), "실행 상태 확인 필요" if task.get("problem") else "판정 대기"))
        lines.append(f"- {task['persona_id']}: {status_names[task['status']]} · {verdict}")
    return "\n".join(lines) + "\n"


def render_preview(value):
    lines = ["# 페르소나 실행 계획", "", f"독립 세션 {value['sessions']}개 · 동시 요청 최대 {value['parallel_calls']}개",
        "실행 방식: " + ("유료 호출 없는 모의 실행" if value["mode"] == "fixture" else "승인이 필요한 실제 모델 실행"),
        f"실행 예산 한도: USD {value['approved_budget_microusd']/1000000:.6f}",
        f"모든 허용 턴을 끝낼 때의 보수적 계산: USD {value['full_run_conservative_microusd']/1000000:.6f}", ""]
    for route in value["provider_routes"]:
        lines.append(f"- {route['provider']} / {route['model']}: {route['sessions']}세션 · 동시 {route['concurrency']} · 전송 대상 {route['destination']}")
    if value["may_stop_before_all_sessions"]:
        lines += ["", "모든 세션이 끝나기 전에 예산 한도에서 멈출 수 있습니다."]
    lines += ["", "전송 내용: 각 페르소나의 비식별 프로필, 관련 요구사항, 허용된 도구 정보와 자신의 관측.",
              value["next_action"]]
    return "\n".join(lines) + "\n"
