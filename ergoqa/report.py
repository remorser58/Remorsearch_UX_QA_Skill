"""Korean Markdown report for an ergonomic persona-swarm run."""

from __future__ import annotations

from typing import Any, Iterable

from . import checks
from .profiles import CONDITION_STRATA, CORE_POINTER_STRATA, CORE_TOUCH_STRATA
from .swarm import severity_counts

BASIS_KO = {
    "measured": "실측(화면에서 측정, observed)",
    "model": "모델 예측(inferred)",
    "judgment": "판단(LLM/사람, inferred)",
}


def _fmt_measure(measurement: dict[str, Any]) -> str:
    value = measurement.get("value")
    unit = measurement.get("unit", "")
    threshold = measurement.get("threshold")
    comparator = measurement.get("comparator", "")
    return f"{measurement.get('name')}={value} {unit} (기준 {comparator} {threshold})"


def render(
    findings: list[dict[str, Any]],
    profiles: Iterable[dict[str, Any]],
    analyses: Iterable[dict[str, Any]],
    title: str = "인간공학 페르소나 스웜 QA 보고서",
    limitations: Iterable[str] = (),
) -> str:
    profiles = list(profiles)
    analyses = list(analyses)
    counts = severity_counts(findings)
    lines: list[str] = [f"# {title}", ""]
    lines += [
        "## 1. 범위와 증거 경계",
        "",
        f"- 실행(run) {len(analyses)}건, 시뮬레이션 프로필 {len(profiles)}개, 발견 {len(findings)}건 "
        f"(P0 {counts['P0']} · P1 {counts['P1']} · P2 {counts['P2']} · P3 {counts['P3']}).",
        "- 모든 조작은 드라이버가 실제 화면(브라우저/기기)에서 수행한 기록을 분석했습니다. 인간공학 수치는 결정론적 모델이 계산했고, LLM 페르소나가 연기하지 않았습니다.",
        "- 'k/n 시뮬레이션 프로필'은 **커버리지**이며 실제 사용자 비율(유병률·선호)을 뜻하지 않습니다.",
        "- 실측(observed)과 모델 예측(inferred)을 분리해 표기했습니다. 모델 예측은 실제 사용자 테스트로 확인해야 하는 가설입니다.",
        "- 엄지 도달 모델은 보정 전 휴리스틱(thumb-reach-v3-uncalibrated)이므로 단독으로 P2를 넘기지 않습니다.",
        "",
    ]
    for item in limitations:
        lines.append(f"- {item}")
    if limitations:
        lines.append("")
    lines += ["## 2. 실행 목록", "", "| run | 시나리오 | 기기 | 상태 | 성공 | 평가 프로필 |", "|---|---|---|---|---|---|"]
    for a in analyses:
        lines.append(f"| {a['run_id']} | {a.get('scenario_id')} | {a.get('device_id')} ({a.get('orientation')}) | {a.get('run_status')} | {a.get('run_success')} | {', '.join(a['profiles_evaluated'])} |")
    lines += ["", "## 3. 시뮬레이션 프로필 (시나리오 가정)", "", "| ID | 설명 | 기기 | 표본 방식 |", "|---|---|---|---|"]
    for p in profiles:
        a = p["attributes"]
        origin = p.get("origin", "")
        if p.get("coverage_stratum"):
            origin += f" ({p['coverage_stratum']})"
        lines.append(f"| {p['profile_id']} | {p.get('label_ko', '')} | {a.get('device_id')} | {origin} |")
    covered = {p.get("coverage_stratum") for p in profiles}
    touch = any(p["attributes"]["grip"] in ("one_hand_right", "one_hand_left", "two_thumbs", "cradle_right", "cradle_left") for p in profiles)
    wanted = [name for name, _ in (CORE_TOUCH_STRATA if touch else CORE_POINTER_STRATA) + CONDITION_STRATA]
    missing = [name for name in wanted if name not in covered]
    devices = sorted({p["attributes"]["device_id"] for p in profiles})
    lines += ["", f"- 테스트한 기기: {', '.join(devices)}", f"- 이번 실행에서 다루지 않은 커버리지 층: {', '.join(missing) if missing else '없음'}",
              "- 페르소나 데이터셋에 없는 인간공학 속성(손잡이·파지·손 크기·시력·운동·기기)은 모두 시나리오 가정입니다."]
    limits = [n for a in analyses for n in a.get("limitations", [])]
    if limits:
        lines += ["", "실행 한계(에이전트 한계/환경 문제로 분류되어 발견에서 제외):"] + [f"- {n}" for n in limits]
    lines += ["", "## 4. 발견 요약", "", "| ID | 심각도 | 범주 | 근거 | 대상 | 커버리지 | 차이 조건 |", "|---|---|---|---|---|---|---|"]
    for f in findings:
        diff = ", ".join(f"{k}={v}" for k, v in f["profile_specific"].items()) or "-"
        target = f["element_key"].replace("|", " / ")[:48]
        lines.append(f"| {f['id']} | {f['severity']} | {f['category']} | {BASIS_KO[f['basis']].split('(')[0]} | {target} | {f['coverage_label'].split(' (')[0]} | {diff} |")
    lines += ["", "## 5. 발견 상세", ""]
    for f in findings:
        lines += [
            f"### {f['id']} [{f['severity']}] {f['title_ko']}",
            "",
            f"- 체크: `{f['check_id']}` · 범주: {f['category']} · 근거: {BASIS_KO[f['basis']]}" + (f" · 모델: `{f['model']}`" if f.get("model") else ""),
            f"- 시나리오: `{f['scenario_id']}` · 대상: `{f['element_key']}`",
            f"- 관찰: {f['summary_ko']}",
            f"- 측정: {_fmt_measure(f['measurement'])}",
            f"- 커버리지: {f['coverage_label']} — 발생 {', '.join(f['triggered_profiles'])}",
        ]
        if f["profile_specific"]:
            lines.append("- 차이 조건(발생 프로필에만 공통): " + ", ".join(f"`{k}={v}`" for k, v in f["profile_specific"].items()))
        lines += [
            f"- 권장 수정({f['fix_layer']}): {f['recommendation_ko']}",
            f"- 근거 문헌: {', '.join(f['refs'])}",
            f"- 증거 ID: {', '.join(f['observation_ids'][:6])}" + (" …" if len(f["observation_ids"]) > 6 else ""),
            "",
        ]
    lines += [
        "## 6. 자동화하지 않은 판단 (사람/비전 LLM 확인 필요)",
        "",
        "- WCAG 2.5.8 예외(인라인·동등 대안·필수) 해당 여부, 동작의 비가역성, 시각적 위계가 실제로 주요 버튼처럼 읽히는지.",
        "- 실제 파지 습관·파지 전환, 손에 가려진 메시지를 실제로 놓쳤는지, 피로·통증.",
        "- 게임 의도(QTE·연타가 설계 의도인지), 좌우 반전 HUD의 품질, 광고처럼 보이는지(배너 블라인드니스).",
        "",
        "## 7. 다음 검증",
        "",
        "- P0/P1 및 모델 기반 P2는 해당 조건의 실제 사용자(예: 왼손 한 손 파지, 노안, 색각이상) 과제 테스트로 확인하세요.",
        "- 커뮤니티 리서치(aside-community-ux-research)로 같은 문제의 실제 사용자 언급을 교차 확인하세요.",
        "- 수정 후 같은 시나리오·기기·프로필로 재실행해 회귀를 확인하세요.",
        "",
    ]
    return "\n".join(lines)


def catalog_markdown() -> str:
    lines = ["| ID | 범주 | 근거 | 이름 | 문헌 |", "|---|---|---|---|---|"]
    for spec in checks.iter_catalog():
        lines.append(f"| {spec.check_id} | {spec.category} | {spec.basis} | {spec.title_ko} | {', '.join(spec.refs)} |")
    return "\n".join(lines)
