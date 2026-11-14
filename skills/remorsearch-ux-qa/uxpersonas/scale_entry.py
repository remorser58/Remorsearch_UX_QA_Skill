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
from .peekly_criteria import CRITERIA as PEEKLY_CRITERIA
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
        for name, low, high in (("parallel", 1, 64), ("turns", 1, 64),
                ("call_seconds", 1, 180), ("task_seconds", 1, 3600),
                ("lease_seconds", 10, 600), ("budget_microusd", 0, 10**12),
                ("max_model_calls", 1, 50000)):
            bounded(getattr(self, name), low, high, name)
        return vars(self).copy()


def engine_manifest():
    root = Path(__file__).resolve().parent
    files = ("swarm_queue.py", "swarm_providers.py", "model_router.py", "scale_run.py", "scale_entry.py", "scale_report.py", "peekly_criteria.py",
             "agent_run.py", "swarm.py", "library.py")
    return {name: byte_digest(read_bytes(root / name)) for name in files}


PEEKLY_FIXTURE_REQUIREMENTS = {
    "PRD-IMPORT-FORMATS": ("peekly-format-html.zip", "peekly-format-json.zip"),
    "PRD-IMPORT-ACCOUNT": ("peekly-sample-current.zip", "peekly-account-mismatch.zip"),
    "PRD-IMPORT-HTML": ("peekly-malformed-html.zip",),
    "PRD-IMPORT-MISSING": ("peekly-missing-followers.zip", "peekly-missing-following.zip"),
    "PRD-IMPORT-MULTI": ("@group:peekly-mixed-loose-valid", "@group:peekly-loose-512-valid",
                         "@group:peekly-loose-513-rejected", "@group:peekly-zip-plus-loose-rejected"),
    "PRD-IMPORT-SIZE": ("peekly-oversize-plus-one.zip", "@group:peekly-loose-file-over",
                        "@group:peekly-loose-total-over"),
    "PRD-IMPORT-PROGRESS": ("peekly-sample-current.zip", "peekly-progress-sample.zip"),
    "PRD-IMPORT-SAVE-FAIL": ("peekly-sample-previous.zip", "peekly-sample-current.zip"),
    "PRD-IMPORT-SNAPSHOT-UNKNOWN": ("peekly-empty-previous.zip", "peekly-sample-current.zip"),
    "PRD-RESULT-SNAPSHOT": ("peekly-sample-previous.zip", "peekly-sample-current.zip"),
    "PRD-PAYWALL-BOUNDARY": ("peekly-sample-previous.zip", "peekly-sample-current.zip"),
    "PRD-IDENTITY-LIMIT": ("peekly-sample-previous.zip", "peekly-sample-current.zip"),
    "PRD-RESULT-SEARCH": ("peekly-search-ready.zip",),
    "PRD-SNAPSHOT-RETENTION": tuple(f"peekly-retention-snapshot-{i:02d}.zip" for i in range(1, 12)),
}

_PEEKLY_STEPS = {
    "PRD-RESULT-RECIPROCITY": ("Import the valid relationship fixture or enter sample mode.", "Open the required relationship card, inspect count and actual rows, then close its modal before another card."),
    "PRD-RESULT-REVERSE": ("Close any existing modal using its visible close control.", "Open the reverse relationship card; inspect count and row set."),
    "PRD-RESULT-MUTUAL": ("Close any existing modal; the mutual card must be visible:true.", "Open the mutual card and inspect count plus row set; a person-detail sheet is not the mutual list."),
    "PRD-RESULT-SNAPSHOT": ("Import peekly-sample-previous.zip, reopen the import entry, then import peekly-sample-current.zip.", "Open the latest comparison and its departed-follower list; inspect both count and names."),
    "PRD-IDENTITY-LIMIT": ("Import both complete previous/current snapshots and open the latest comparison explanation.", "Inspect the username-change limitation there; the first-record preview is not this screen."),
    "PRD-RESULT-SEARCH": ("Import peekly-search-ready.zip and open a relationship list with at least nine rows.", "Check unfiltered username order, enter an exact observed row key in the visible search input, and verify only that row remains."),
    "PRD-SAMPLE-EXPORT": ("Enter sample mode before importing real synthetic snapshots.", "Open More > 관계 목록 (MatrixTab); inspect both copy/save disabled states and sample titles. Do not click disabled controls.", "When a later criterion requires import, proceed directly to the More import entry after recording export evidence; do not add a separate 샘플 닫기 prerequisite."),
    "PRD-SNAPSHOT-RETENTION": ("Verify all eleven manifest keys before executing any retention step.", "For each snapshot 01 through11: open the current import entry, upload that one ZIP, inspect completion; never mix ZIPs.", "After the eleventh import open saved history and inspect retained count/oldest record; do not substitute repeated imports of the same ZIP."),
    "PRD-PAYWALL-BOUNDARY": ("Import the complete previous/current pair and inspect free latest comparison names.", "Open history, inspect both date selectors and Pro restrictions; inspect timeline/person-history entry without purchasing."),
    "PRD-IMPORT-PROGRESS": ("First save a small baseline with peekly-sample-current.zip if no actual saved snapshot exists; sample mode alone is insufficient.", "Open the current file input and use reviewed upload_cancel with peekly-progress-sample.zip; inspect captured reading and analysis phases, real stop dispatch and unchanged saved-result digest.", "Only if the cancel attempt lacks a required phase, try normal upload of that fixture to observe the missing phase within the remaining budget; never require a large completed import before cancellation."),
    "PRD-IMPORT-SAVE-FAIL": ("Preserve an actual small saved baseline; if absent, import peekly-sample-previous.zip.", "Reopen the file input and use upload_save_failure with the distinct snapshot: current after previous, or previous after current. Inspect consumed fault, prior-result preservation and the visible 다시 저장 action.", "Click the visible retry after the one-shot fault clears, and inspect successful save. Without the reviewed capability report not_run; never simulate a pass."),
}


def criterion_checklist(requirement_ids):
    """Return an ordered execution checklist, never a fabricated verdict."""
    rows = []
    for index, rid in enumerate(requirement_ids):
        spec = PEEKLY_CRITERIA.get(rid)
        if spec is None:
            continue
        rows.append(dict(kind="success", index=index, requirement_id=rid,
            precondition=spec["precondition"], scope=spec["scope"],
            required_fixtures=list(PEEKLY_FIXTURE_REQUIREMENTS.get(rid, ())),
            steps=list(_PEEKLY_STEPS.get(rid, (spec["action"],)))))
    priority = {"PRD-SAMPLE-EXPORT": 0, "PRD-START-SAMPLE": 1,
                "PRD-START-IMPORT": 2, "PRD-START-SKIP": 2,
                "PRD-SNAPSHOT-RETENTION": 30, "PRD-RESULT-SNAPSHOT": 40,
                "PRD-PAYWALL-BOUNDARY": 45, "PRD-IDENTITY-LIMIT": 45,
                "PRD-PRIVACY-DELETE": 100}
    return sorted(rows, key=lambda row: (priority.get(row["requirement_id"], 20), row["index"]))


def required_fixture_keys(requirement_ids):
    return sorted({name for rid in requirement_ids
                   for name in PEEKLY_FIXTURE_REQUIREMENTS.get(rid, ())})


def _criterion_actions(requirement_ids):
    return [f"[{row['requirement_id']}] Required fixtures: "
            + (", ".join(name.replace("@group:", "manifest group ") for name in row["required_fixtures"]) or "none")
            + ". Steps: " + " -> ".join(row["steps"])
            for row in criterion_checklist(requirement_ids)]

def _persona_journey_goal(base_goal, requirement_ids):
    """Turn each saved persona's mapped PRD requirements into executable actions.

    Do not declare unrelated, untriggered recovery paths as success requirements.
    Missing evidence for an applicable success requirement remains not_run.
    """
    actions = []
    ids = set(requirement_ids)
    if ids & {"PRD-START-SAMPLE", "PRD-RESULT-RECIPROCITY", "PRD-RESULT-REVERSE", "PRD-RESULT-MUTUAL"}:
        actions.append("샘플로 둘러보기를 열고 요구된 관계 카드의 설명·숫자를 확인한다. 목록이 해당 기준에 포함되면 직접 열어 목록도 확인한다.")
    if ids & {"PRD-START-IMPORT", "PRD-START-SKIP"}:
        actions.append("현재 PRD 기준으로 More 첫 화면의 '이미 받은 자료로 확인하기'를 눌러 실제 파일 선택 단계까지 이동한다. 별도의 요청 안내 shortcut '이미 파일을 받았어요'는 현재 PRD 요구가 아니므로 찾거나 실패로 판정하지 않는다.")
    if "PRD-RESULT-SNAPSHOT" in ids:
        actions.append("동일 계정의 두 완전한 합성 스냅샷을 이전→최신 순서로 가져온다. 무료 결과 화면에서 '팔로워에서 빠진 사람'의 숫자와 이름 목록을 확인하고, 목록 변화만으로 원인을 단정하지 않는지 확인한다.")
    if "PRD-IMPORT-FORMATS" in ids:
        actions.append("HTML 형식과 JSON 형식의 동등성이 기준이면 두 fixture를 각각 가져와 결과 범주와 수를 대조한다. HTML fixture의 complete html/body 문서 검증이 실패하면 fixture 결함으로 기록하고 제품 실패로 판정하지 않는다.")
    if "PRD-IMPORT-MISSING" in ids:
        actions.append("필수 관계 파일 누락 기준이면 peekly-missing-followers.zip과 peekly-missing-following.zip을 각각 넣고 파일 누락 안내가 실제 표시되는지 확인한다. 정상 ZIP으로 대체하지 않는다.")
    if "PRD-IMPORT-ACCOUNT" in ids:
        actions.append("계정 불일치 기준이면 peekly-account-mismatch.zip을 넣고 계정 불일치 차단 안내를 확인한다.")
    if "PRD-IMPORT-HTML" in ids:
        actions.append("읽을 수 없는 HTML 관계 항목 기준이면 peekly-malformed-html.zip을 넣고 가져오기 중단 안내를 확인한다.")
    if "PRD-IMPORT-SNAPSHOT-UNKNOWN" in ids:
        actions.append("비어 있는 이전 백업의 비교 제외 기준이면 peekly-empty-previous.zip을 먼저 넣고 peekly-sample-current.zip을 이어 넣어 비교가 제외되는지 확인한다.")
    if "PRD-RESULT-SEARCH" in ids:
        actions.append("9명 이상 관계 목록을 열어 username 순서와 현재 UI placeholder '아이디나 이름으로 찾기'가 있는 text input을 확인한다. 합성 아이디를 검색해 대상 행만 남는지 확인한다.")
    if "PRD-PRIVACY-LOCAL" in ids:
        actions.append("현재 PRD의 자체 서버 없음·기기 내 처리 고지를 확인한다. 결과 공유는 사용자가 고른 목적지로 전달될 수 있고 샘플 공유는 비활성화된다는 경계를 구분한다. desktop 브라우저의 외부 요청 차단은 테스트 격리 정책이지 제품 자체의 데이터 흐름 증거라고 주장하지 않는다.")
    if "PRD-PRIVACY-DELETE" in ids:
        actions.append("합성 데이터만 든 별도 브라우저 프로필에서 데이터 삭제 확인 단계를 실행하고 localStorage 앱 상태·onboarding 키 제거를 확인한다. iOS 알림 취소와 WKWebView/cookie 삭제는 desktop 검증 범위 밖이므로 N/A로 기록한다.")
    if "PRD-SAMPLE-EXPORT" in ids:
        actions.append("샘플 둘러보기에서 More > 관계 목록(MatrixTab)을 실제로 연다. 목록 복사와 목록 저장 버튼의 disabled 상태와 샘플 전용 title 안내를 확인한다. 비활성 버튼을 억지로 클릭하지 않으며, 실데이터 목록의 활성 버튼을 샘플 기준 실패로 판정하지 않는다.")
    if "PRD-SNAPSHOT-RETENTION" in ids:
        actions.append("서로 다른 유효 합성 스냅샷 11개를 개별 import하고 기록 목록에서 최대 10개 보관을 확인한다. 저장 공간 압박으로 더 적게 보관되면 최신 두 기록 보존을 확인한다. 고정 turn budget으로 11회 import를 끝낼 수 없으면 retention은 not_run으로 남기고 통과/실패를 만들지 않는다.")
    if "PRD-PAYWALL-BOUNDARY" in ids:
        actions.append("동일 계정 두 스냅샷의 현재 관계 목록과 최신 두 기록 비교 이름까지 무료로 보이는지 확인한다. 두 기록 미만이면 upsell을 요구하지 않는다. 여러 기록 timeline·두 날짜 선택·사람별 이력만 Pro 경계로 확인하고 결제는 누르지 않는다.")
    if "PRD-IMPORT-MULTI" in ids:
        actions.append("파일 선택에서 manifest group peekly-mixed-loose-valid의 정확한 catalog key를 실제 input[type=file][multiple]에 넣고, 512개 허용·513개 거절 및 ZIP+loose 혼합 거절 group을 각각 실행한다.")
    if "PRD-IMPORT-SIZE" in ids:
        actions.append("128MiB+1 ZIP, 32MiB+1 loose file, 64MiB 초과 loose aggregate group을 각각 업로드한다. 각 경계별 오류와 이전 결과 보존을 확인한다.")
    if "PRD-IMPORT-PROGRESS" in ids:
        actions.append("작은 합성 스냅샷을 실제 저장한 기준 상태에서 upload_cancel로 대용량 valid ZIP의 reading→analyzing 진행과 실제 취소·기존 저장 결과 보존을 확인한다. 전체 대용량 import 완료를 먼저 요구하지 않으며 부족한 phase만 필요 시 별도 관찰한다.")
    if ids & {"PRD-IMPORT-PROGRESS", "PRD-IMPORT-SIZE", "PRD-IMPORT-SAVE-FAIL"}:
        actions.append("가져오기 진행·크기 제한 기준은 실제 저장된 작은 합성 기준 결과를 보존하며 전용 해시 고정 fixture로 실행한다. 저장 실패 기준에는 제공된 upload_save_failure의 한 번만 발생하는 격리 저장 오류와 실제 보이는 다시 저장 버튼을 사용한다. 도구가 없으면 not_run으로 남긴다.")
    if not actions:
        actions.append("이 페르소나의 요구사항에 직접 대응하는 화면 흐름을 관찰하고 각 성공 기준을 개별적으로 확인한다.")
    criteria = []
    for rid in requirement_ids:
        spec = PEEKLY_CRITERIA.get(rid)
        if spec:
            criteria.append(f"- [{rid}] 화면={spec['screen']}; 셀렉터={spec['selector']}; 필수 텍스트={', '.join(spec['text'])}; 기대값={spec['value']}; 선행조건={spec['precondition']}; 행동={spec['action']}; 제한시간={spec['timeout_seconds']}초; 범위={spec['scope']}")
    return (base_goal + "\n\n이 페르소나의 요구사항별 실행 과제:\n" + "\n".join("- " + action for action in actions)
        + "\n\n명시적 성공 기준과 기계 판정 계약:\n" + "\n".join(criteria)
        + "\n\n기준별 필수 단계 체크리스트:\n" + "\n".join(_criterion_actions(requirement_ids))
        + "\n\n실행 규칙: 새 브라우저의 현재 DOM을 먼저 관찰하고 기준마다 선행조건을 충족한 뒤 제한시간 안에 지정 행동을 실제 수행한다. "
        "업로드 기준은 이름이 지정된 모든 fixture를 실제 input[type=file]에 업로드하고 결과 화면까지 확인한다. "
        "기준에 적힌 텍스트만 보였다는 이유로 통과시키지 말고 숫자·상태·목록까지 확인한다. "
        "기계 판정 checks가 존재하면 그 결과를 반드시 따른다. 기계 판정이 없는 기준은 관측 ID와 스크린샷을 인용한다. "
        "필수 fixture나 하위 흐름을 건너뛰고 최종 판단하지 않는다. 성공 기준을 실행하지 않았거나 전제조건이 확인되지 않으면 not_run으로 남기고 다음 실행 행동을 먼저 시도한다. "
        "조건부 복구 기준은 실제 실패가 발생했을 때만 실행하며 실패가 전혀 발생하지 않았으면 not_applicable로 남긴다. 실행하지 않은 조건을 failed로 판정하지 않는다. "
        "현재 관측에서 visible:true인 control만 클릭한다. 모달이 열렸으면 먼저 보이는 닫기 control로 닫고 새 관측에서 다음 대상을 찾는다. "
        "모달이 없고 현재 More 관측에 '이미 받은 자료로 확인하기'가 있으나 visible:false이면, 다른 탭으로 이동하지 말고 scroll(delta=-400) 후 반환된 최신 관측을 확인한다. 필요하면 한 번 더 반복하고 visible:true가 확인된 뒤에만 클릭한다. "
        "체크리스트 순서로 남은 기준을 하나씩 처리하며, 완료한 경로를 반복하지 않는다. 샘플 export는 데이터 import 전에, 데이터 삭제는 마지막에 한다. "
        "행동 도구가 이미 최신 DOM을 반환했으면 같은 화면의 observe를 반복하지 않는다. 파일 이름/selector는 현재 fixture_catalog와 controls에서만 고른다.")


def scale_job_id(product_id, persona_id, revision, goal, build):
    """Use the same reviewed identity for preparation and no-replay preflight."""
    return "S-" + digest([product_id, persona_id, revision, goal, build])[:24].translate(
        str.maketrans("0123456789abcdef", "abcdefghijklmnop"))


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
        jid = scale_job_id(product_id, pid, profile["revision"], goal, build)
        requirement_ids = [r["id"] for r in requirements]
        task = dict(id=jid, persona_id=pid, requirement_ids=requirement_ids,
            goal=_persona_journey_goal(goal, requirement_ids),
            starting_state="Fresh isolated owned context for the reviewed product.",
            actions=["Choose a permitted next action from your own current observations."]
                    + _criterion_actions(requirement_ids),
            decisions=copy.deepcopy(profile["profile"]["behaviors"]),
            success_criteria=[r["excerpt"] + (" [" + r["id"] + "] " + PEEKLY_CRITERIA[r["id"]]["value"]
                if r["id"] in PEEKLY_CRITERIA else "") for r in requirements],
            recovery_criteria=["If a recoverable browser/import failure actually occurs, perform the safe recovery and verify it. If no triggering failure occurs, report not_applicable; do not manufacture a failure."],
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
