"""Ergonomic check catalog and per-snapshot evaluation.

Each check reads measured inputs from a snapshot/run (geometry, colour, timing)
and a profile, applies a model from ergoqa.hf, and emits observations
(docs/ergonomic-swarm-spec.md section 6). Checks never role-play a user.

Basis/epistemic mapping:
- ``measured`` -> ``observed``: the value is read from the surface and compared
  with a fixed standard threshold (e.g. WCAG contrast, 24 px target size).
- ``model`` -> ``inferred``: a published model predicts an outcome for a
  profile (reach difficulty, miss probability, gaze priority, reading time).
- ``judgment`` -> ``inferred``: an LLM persona's note or a human judgment.
"""

from __future__ import annotations

import math
import zlib
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from . import params
from .hf import cognition, game, gaze, perception, pointing, reach

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


@dataclass(frozen=True)
class CheckSpec:
    check_id: str
    category: str
    basis: str
    title_ko: str
    title_en: str
    refs: tuple[str, ...]
    applies_to: tuple[str, ...] = ("web", "android", "ios", "desktop", "game")
    fix_layer: str = "interaction"
    recommendation_ko: str = ""


CATALOG: dict[str, CheckSpec] = {}


def _register(spec: CheckSpec) -> CheckSpec:
    CATALOG[spec.check_id] = spec
    return spec


RH01 = _register(CheckSpec(
    "RH-01", "reach", "model", "한 손 엄지 도달이 어려운 위치의 조작 대상",
    "Action target outside the comfortable thumb zone for this grip",
    ("REF-bergstrom2014", "REF-hoober2013"), ("web", "android", "ios", "game"), "interaction",
    "주요 조작을 파지 손 엄지의 편한 영역(화면 하단 중앙부)으로 옮기거나 하단 고정 바/대체 경로를 제공하세요. 좌우 대칭 배치 또는 손잡이 설정을 검토하세요.",
))
RH02 = _register(CheckSpec(
    "RH-02", "reach", "model", "편한 엄지 영역에 놓인 파괴적 동작",
    "Destructive action sits in the easiest thumb zone",
    ("REF-bergstrom2014", "REF-hoober2013"), ("web", "android", "ios"), "interaction",
    "삭제/탈퇴 같은 파괴적 동작은 편한 영역에서 빼고 확인 단계나 실행 취소를 두세요.",
))
PT01 = _register(CheckSpec(
    "PT-01", "pointing", "measured", "WCAG 2.5.8 최소 타깃 크기(24px) 미달",
    "Target smaller than WCAG 2.5.8 minimum without spacing exception",
    ("REF-wcag22-258",), fix_layer="accessibility",
    recommendation_ko="타깃을 최소 24×24 CSS px 이상(권장 44–48)으로 키우거나 주변 간격을 확보하세요.",
))
PT02 = _register(CheckSpec(
    "PT-02", "pointing", "measured", "터치 타깃 물리 크기가 플랫폼 권장치 미만",
    "Touch target physically smaller than platform guidance",
    ("REF-apple-hig-44pt", "REF-material-48dp", "REF-parhi2006"), ("web", "android", "ios", "game"), "visual",
    "터치 타깃을 44pt/48dp(약 7–9mm) 이상으로 키우세요.",
))
PT03 = _register(CheckSpec(
    "PT-03", "pointing", "model", "주요 동작 옆 파괴적 동작 오터치 위험",
    "Accidental activation risk: destructive action adjacent to a primary/path action",
    ("REF-bi-zhai2013", "REF-henze2011"), fix_layer="interaction",
    recommendation_ko="주요 동작과 파괴적 동작 사이 간격을 충분히 두고(최소 8mm 권장) 파괴적 동작에는 확인/실행 취소를 두세요.",
))
PT04 = _register(CheckSpec(
    "PT-04", "pointing", "model", "예측 오터치 확률이 높은 조작 대상",
    "High predicted touch-miss probability for this profile",
    ("REF-bi-zhai2013", "REF-henze2011", "REF-parhi2006"), ("web", "android", "ios", "game"), "visual",
    "타깃 크기와 간격을 키우고, 이동 중·손떨림 사용자를 위한 여유 영역(hit slop)을 두세요.",
))
PT05 = _register(CheckSpec(
    "PT-05", "pointing", "model", "연속 조작 간 포인팅 난이도(Fitts ID)가 높음",
    "High Fitts index of difficulty between consecutive steps",
    ("REF-fitts1954", "REF-mackenzie1992"), ("web", "desktop", "game"), "ia",
    "연속으로 누르는 조작을 가깝게 두고 타깃을 키우세요.",
))
GZ01 = _register(CheckSpec(
    "GZ-01", "gaze", "model", "주요 동작이 초기 시선 경로에 들어오지 않음",
    "Primary action unlikely to be among the first predicted fixations",
    ("REF-itti1998", "REF-ueyes2023", "REF-nngroup-f-pattern"), fix_layer="visual",
    recommendation_ko="주요 동작의 시각적 위계(크기·대비·위치)를 높이고 경쟁하는 강조 요소를 줄이세요.",
))
GZ02 = _register(CheckSpec(
    "GZ-02", "gaze", "model", "조작 지점에서 멀리 뜨는 피드백/오류 메시지(변화맹 위험)",
    "Feedback or error appears far from where the user just acted",
    ("REF-rensink1997", "REF-ball-ufov"), fix_layer="interaction",
    recommendation_ko="오류·상태 메시지를 조작한 위치 가까이(인라인) 표시하고, 필요하면 포커스를 이동하거나 라이브 영역으로 알리세요.",
))
GZ03 = _register(CheckSpec(
    "GZ-03", "gaze", "model", "중요 정보가 광고처럼 보이는 위치/형태(배너 블라인드니스)",
    "Critical information placed where users habitually ignore ads",
    ("REF-benway1998", "REF-nngroup-banner-blindness"), ("web", "desktop"), "visual",
    "중요 알림을 광고 영역 밖, 작업 흐름 안에 표시하고 광고와 다른 형태를 쓰세요.",
))
GZ04 = _register(CheckSpec(
    "GZ-04", "gaze", "model", "주요 동작보다 눈에 띄는 경쟁 요소가 많음",
    "Many elements out-compete the primary action for attention",
    ("REF-itti1998", "REF-ueyes2023"), fix_layer="visual",
    recommendation_ko="보조 요소의 강조를 낮추고 한 화면의 주요 동작을 하나로 모으세요.",
))
PC01 = _register(CheckSpec(
    "PC-01", "perception", "measured", "텍스트 명도 대비 부족(WCAG 1.4.3)",
    "Text contrast below WCAG 1.4.3",
    ("REF-wcag22-143",), fix_layer="visual",
    recommendation_ko="본문 4.5:1, 큰 글씨 3:1 이상으로 전경/배경 대비를 높이세요.",
))
PC02 = _register(CheckSpec(
    "PC-02", "perception", "measured", "UI 컴포넌트 경계 대비 부족(WCAG 1.4.11)",
    "Non-text contrast of component boundary below 3:1",
    ("REF-wcag22-1411",), fix_layer="visual",
    recommendation_ko="입력창 테두리·버튼 경계를 인접 색과 3:1 이상 대비로 만드세요.",
))
PC03 = _register(CheckSpec(
    "PC-03", "perception", "model", "색각이상에서 구분되지 않는 색상 전용 상태 구분",
    "Colour-only distinction collapses under simulated colour-vision deficiency",
    ("REF-machado2009", "REF-wcag22-141"), fix_layer="visual",
    recommendation_ko="색 외에 텍스트·아이콘·패턴으로 상태를 함께 표시하세요.",
))
PC04 = _register(CheckSpec(
    "PC-04", "perception", "model", "시청 거리 대비 글자가 너무 작음(노안/저시력 프로필)",
    "Text subtends too small a visual angle for this profile",
    ("REF-legge2007", "REF-kwcag22"), fix_layer="visual",
    recommendation_ko="본문 글자 크기를 키우고(모바일 16px 이상 권장) 시스템 글자 크기 확대를 지원하세요.",
))
PC05 = _register(CheckSpec(
    "PC-05", "perception", "model", "강한 햇빛 환경에서 대비 여유 부족",
    "Insufficient contrast margin for bright-light context",
    ("REF-wcag22-146",), ("web", "android", "ios", "game"), "visual",
    "야외 사용이 잦은 화면의 핵심 텍스트는 7:1 이상 대비를 권장합니다.",
))
CG01 = _register(CheckSpec(
    "CG-01", "cognition", "model", "동등한 선택지가 너무 많음(선택 과부하)",
    "Too many equally weighted choices on one decision screen",
    ("REF-hick1952", "REF-hyman1953"), fix_layer="ia",
    recommendation_ko="선택지를 묶거나 추천/기본값을 제시하고 단계적으로 공개하세요.",
))
CG02 = _register(CheckSpec(
    "CG-02", "cognition", "model", "읽기 전에 사라지는 일시 메시지",
    "Transient message disappears before it can be read",
    ("REF-wcag22-221",), fix_layer="content",
    recommendation_ko="토스트 표시 시간을 글자 수에 맞춰 늘리거나 사용자가 닫을 때까지 유지하세요.",
))
CG03 = _register(CheckSpec(
    "CG-03", "cognition", "measured", "조작 후 응답/피드백 지연",
    "Slow or missing feedback after an action",
    ("REF-miller1968", "REF-nielsen1993"), fix_layer="interaction",
    recommendation_ko="100ms 안에 눌림 피드백, 1초 이상 걸리면 진행 표시를 보여주세요.",
))
GM01 = _register(CheckSpec(
    "GM-01", "game", "model", "HUD/자막 글자가 시청 거리 대비 작음",
    "HUD or subtitle text too small for viewing distance",
    ("REF-xag", "REF-gag"), ("game", "web", "android", "ios"), "visual",
    "HUD/자막 크기를 키우고 크기 조절 옵션을 제공하세요.",
))
GM02 = _register(CheckSpec(
    "GM-02", "game", "model", "가로 두 엄지 파지에서 닿기 어려운 게임 조작부",
    "Game control hard to reach in landscape two-thumb grip",
    ("REF-bergstrom2014",), ("game", "web", "android", "ios"), "interaction",
    "자주 쓰는 조작부를 하단 좌우 엄지 영역에 두고 위치/크기 커스터마이즈를 제공하세요.",
))
GM03 = _register(CheckSpec(
    "GM-03", "game", "model", "반응 시간보다 짧은 입력 제한 시간(QTE)",
    "Timed input window shorter than the profile's reaction + motor + latency",
    ("REF-der-deary2006", "REF-xag", "REF-gag"), ("game", "web"), "service",
    "제한 시간을 늘리거나 끄는 옵션, 자동 성공 옵션을 제공하세요.",
))
GM04 = _register(CheckSpec(
    "GM-04", "game", "measured", "초당 3회 초과 섬광(광과민성 발작 위험)",
    "More than three flashes in one second over a large area",
    ("REF-wcag22-231", "REF-itu-bt1702"), ("game", "web", "android", "ios", "desktop"), "visual",
    "섬광 빈도를 초당 3회 이하로 낮추고 면적을 줄이세요. 인증된 도구(PEAT/Harding)로 재검사하세요.",
))
PJ01 = _register(CheckSpec(
    "PJ-01", "heuristic", "judgment", "페르소나 에이전트가 기대와 다른 결과/혼란을 기록",
    "Persona agent recorded an expectation mismatch or confusion",
    ("REF-norman2013", "REF-nielsen1994"), fix_layer="interaction",
    recommendation_ko="해당 단계의 기대-결과 불일치를 실제 사용자 테스트로 확인하세요.",
))


@dataclass
class Observation:
    check_id: str
    run_id: str
    profile_id: str
    snapshot_id: str | None
    step_index: int | None
    element_ids: list[str]
    element_key: str
    measurement: dict[str, Any]
    passed: bool
    severity: str | None
    message_ko: str
    model: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self, index: int) -> dict[str, Any]:
        spec = CATALOG[self.check_id]
        basis = spec.basis
        return {
            "id": f"OB-{self.run_id}-{self.profile_id}-{index:04d}",
            "check_id": self.check_id,
            "category": spec.category,
            "run_id": self.run_id,
            "profile_id": self.profile_id,
            "snapshot_id": self.snapshot_id,
            "step_index": self.step_index,
            "element_ids": self.element_ids,
            "element_key": self.element_key,
            "basis": basis,
            "epistemic_status": "observed" if basis == "measured" else "inferred",
            "model": self.model,
            "measurement": self.measurement,
            "passed": self.passed,
            "severity": self.severity if not self.passed else None,
            "message_ko": self.message_ko,
            "message_en": spec.title_en,
            "refs": list(spec.refs),
            **({"extra": self.extra} if self.extra else {}),
        }


@dataclass
class Context:
    run: dict[str, Any]
    snapshot: dict[str, Any]
    previous: dict[str, Any] | None
    step: dict[str, Any] | None
    profile: dict[str, Any]
    device: Any
    scenario: dict[str, Any] | None
    conspicuity: list[list[float]] | None = None
    path_element_ids: set[str] = field(default_factory=set)

    @property
    def elements(self) -> list[dict[str, Any]]:
        return [e for e in self.snapshot.get("elements", []) if isinstance(e, dict) and e.get("box")]

    @property
    def viewport(self) -> tuple[float, float]:
        vp = self.snapshot.get("device", {}).get("viewport_css") or [0, 0]
        return float(vp[0]), float(vp[1])

    @property
    def surface_kind(self) -> str:
        return self.snapshot.get("surface", {}).get("kind", "web")

    @property
    def is_touch(self) -> bool:
        return getattr(self.device, "input", "touch") == "touch"

    @property
    def attrs(self) -> dict[str, Any]:
        return self.profile.get("attributes", {})


def element_key(element: dict[str, Any]) -> str:
    selector = element.get("selector") or element.get("id") or "?"
    name = (element.get("name") or element.get("text") or "").strip().replace("\n", " ")[:40]
    return f"{selector}|{name}"


def _roles(element: dict[str, Any]) -> set[str]:
    return set(element.get("roles") or [])


def _visible(element: dict[str, Any]) -> bool:
    return bool(element.get("visible", True)) and element.get("in_viewport", True) is not False


def _escalate(severity: str, element: dict[str, Any]) -> str:
    """Raise one level (not above P1) for primary/destructive targets."""
    if _roles(element) & {"primary", "destructive"} and SEVERITY_ORDER[severity] > 1:
        return f"P{SEVERITY_ORDER[severity] - 1}"
    return severity


def _box_mm(ctx: Context, box: dict[str, float]) -> tuple[float, float]:
    from .devices import css_px_to_mm
    return css_px_to_mm(ctx.device, box["w"], "x"), css_px_to_mm(ctx.device, box["h"], "y")


def _point_mm(ctx: Context, x: float, y: float) -> tuple[float, float]:
    from .devices import css_px_to_mm
    return css_px_to_mm(ctx.device, x, "x"), css_px_to_mm(ctx.device, y, "y")


def _display_mm(ctx: Context) -> tuple[float, float]:
    vw, vh = ctx.viewport
    return _point_mm(ctx, vw, vh)


# ---------------------------------------------------------------- reach

def check_reach(ctx: Context) -> list[Observation]:
    """Reach/grip checks (HGR-3/5/11). Model-only severities are capped at P2."""
    if not ctx.is_touch:
        return []
    grip = ctx.attrs.get("grip")
    orientation = ctx.snapshot.get("device", {}).get("orientation", "portrait")
    landscape_game = orientation == "landscape" and grip == "two_thumbs"
    if grip not in reach.SUPPORTED_GRIPS or grip.startswith("cradle"):
        return []
    out: list[Observation] = []
    geom = reach.geometry_for_device(ctx.device)
    thumb = float(ctx.attrs.get("thumb_length_mm") or params.THUMB_LENGTH_MM["all"][0])
    for element in ctx.elements:
        roles = _roles(element)
        is_game = "game_control" in roles
        on_path = element.get("id") in ctx.path_element_ids
        if not (element.get("interactive") or is_game) or not _visible(element):
            continue
        if not (roles & {"primary", "destructive", "game_control"} or on_path):
            continue
        cx, cy = pointing.centre(element["box"])
        pt = _point_mm(ctx, cx, cy)
        label = element.get("name") or element.get("text") or element.get("selector")
        base = (ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"))
        if landscape_game and is_game:
            cost = reach.landscape_control_cost(pt[0], pt[1], geom, *params.LANDSCAPE_REST_INSET_MM)
            far = cost["travel_mm"] > params.LANDSCAPE_TRAVEL_MAX_MM
            failed = cost["top_band"] or far
            severity = ("P2" if cost["top_band"] else "P3") if failed else None
            out.append(Observation(
                "GM-02", *base, [element["id"]], element_key(element),
                {"name": "thumb_travel_mm", "value": cost["travel_mm"], "unit": "mm", "threshold": params.LANDSCAPE_TRAVEL_MAX_MM, "comparator": "<=",
                 "top_band": cost["top_band"], "thumb": cost["thumb"]},
                not failed, severity,
                f"게임 조작 '{label}'은(는) {cost['thumb']} 엄지 휴지 위치에서 {cost['travel_mm']:.0f}mm"
                + (" 떨어진 상단 영역에 있습니다(자주 쓰는 조작은 엄지 근처, 상단은 보조 메뉴용: Apple HIG)." if cost["top_band"] else " 떨어져 있습니다."),
                "landscape-thumb-rest-v1",
                {"point_mm": [round(pt[0], 1), round(pt[1], 1)]},
            ))
            continue
        score = reach.reach_score(pt[0], pt[1], geom, grip, thumb)
        difficulty = score["difficulty"]
        extra = {"point_mm": [round(pt[0], 1), round(pt[1], 1)], "zone": score["zone"], "rho": score["rho"], "theta_deg": score["theta_deg"],
                 "screen_mm": [round(geom.screen_w, 1), round(geom.screen_h, 1)], "calibration": "uncalibrated"}
        if grip.startswith("one_hand"):
            extra["asymmetry_L_minus_R"] = round(reach.asymmetry(pt[0], pt[1], geom, thumb), 3)
        if "destructive" in roles and not on_path:
            failed = score["zone"] == "natural" and not score["cramped"]
            out.append(Observation(
                "RH-02", *base, [element["id"]], element_key(element),
                {"name": "reach_difficulty", "value": difficulty, "unit": "0-1", "threshold": params.REACH_EASY_MAX, "comparator": ">"},
                not failed, "P3" if failed else None,
                f"파괴적 동작 '{label}'이(가) {grip} 파지에서 가장 편한 엄지 영역에 있습니다.",
                reach.MODEL_ID, extra,
            ))
            continue
        severity = None
        if score["zone"] == "out":
            severity = "P2"
        elif score["zone"] == "stretch":
            severity = "P3" if not (roles & {"primary"} or on_path) else "P2"
            if difficulty < params.REACH_HARD:
                severity = "P3"
        elif score["cramped"] and min(_box_mm(ctx, element["box"])) < params.TOUCH_TARGET_CORNER_MM:
            severity = "P3"
        zone_ko = {"out": "파지를 바꿔야 닿는", "stretch": "엄지를 크게 뻗어야 하는", "mild": "약간 불편한", "natural": "편한"}[score["zone"]]
        out.append(Observation(
            "RH-01", *base, [element["id"]], element_key(element),
            {"name": "reach_difficulty", "value": difficulty, "unit": "0-1", "threshold": params.REACH_HARD, "comparator": "<"},
            severity is None, severity,
            f"'{label}'은(는) {grip} 파지·엄지 {thumb:.0f}mm 기준 {zone_ko} 위치입니다(난이도 {difficulty:.2f}"
            + (", 손바닥 가까운 좁은 영역" if score["cramped"] else "") + ").",
            reach.MODEL_ID, extra,
        ))
    return out


# ---------------------------------------------------------------- pointing

def _interactive(ctx: Context) -> list[dict[str, Any]]:
    return [e for e in ctx.elements if (e.get("interactive") or "game_control" in _roles(e)) and _visible(e) and e.get("enabled", True)]


def _critical(ctx: Context, element: dict[str, Any]) -> bool:
    return bool(_roles(element) & {"primary", "destructive", "game_control"}) or element.get("id") in ctx.path_element_ids


def check_target_size(ctx: Context) -> list[Observation]:
    out: list[Observation] = []
    targets = _interactive(ctx)
    boxes = [t["box"] for t in targets]
    one_handed = str(ctx.attrs.get("grip", "")).startswith("one_hand")
    for element in targets:
        if element.get("tag") in ("canvas",) and not _roles(element):
            continue
        critical = _critical(ctx, element)
        label = element.get("name") or element.get("text") or element.get("selector")
        ok, reason = pointing.wcag_target_size_ok(element["box"], [b for b in boxes if b is not element["box"]], params.WCAG_TARGET_MIN_CSS_PX)
        if not ok:
            out.append(Observation(
                "PT-01", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                [element["id"]], element_key(element),
                {"name": "target_css_px", "value": [round(element["box"]["w"], 1), round(element["box"]["h"], 1)], "unit": "css_px", "threshold": params.WCAG_TARGET_MIN_CSS_PX, "comparator": ">=", "reason": reason},
                False, "P1" if critical else "P2",
                f"'{label}' 크기 {element['box']['w']:.0f}×{element['box']['h']:.0f}px로 WCAG 2.5.8 최소 24px 미달, 간격 예외도 불충족({reason}).",
            ))
        if ctx.is_touch:
            w_mm, h_mm = _box_mm(ctx, element["box"])
            side = min(w_mm, h_mm)
            severity = None
            threshold = params.TOUCH_TARGET_MIN_MM
            if side < params.TOUCH_TARGET_PLATFORM_FLOOR_MM and critical:
                severity, threshold = "P1", params.TOUCH_TARGET_PLATFORM_FLOOR_MM
            elif side < params.TOUCH_TARGET_MIN_MM:
                severity = "P2" if critical else "P3"
            elif one_handed and critical and side < params.TOUCH_TARGET_ONE_HAND_MM:
                severity, threshold = "P3", params.TOUCH_TARGET_ONE_HAND_MM
            if severity:
                out.append(Observation(
                    "PT-02", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                    [element["id"]], element_key(element),
                    {"name": "target_mm", "value": [round(w_mm, 2), round(h_mm, 2)], "unit": "mm", "threshold": threshold, "comparator": ">="},
                    False, severity,
                    f"'{label}' 물리 크기 {w_mm:.1f}×{h_mm:.1f}mm (기준 {threshold}mm 이상).",
                ))
    return out


def _box_mm_rect(ctx: Context, box: dict[str, float]) -> dict[str, float]:
    x, y = _point_mm(ctx, box["x"], box["y"])
    w, h = _box_mm(ctx, box)
    return {"x": x, "y": y, "w": w, "h": h}


def check_touch_accuracy(ctx: Context) -> list[Observation]:
    if not ctx.is_touch:
        return []
    out: list[Observation] = []
    k = float(ctx.attrs.get("motor", {}).get("touch_sigma_multiplier") or 1.0)
    targets = _interactive(ctx)
    destructive = [t for t in targets if "destructive" in _roles(t)]
    for element in targets:
        roles = _roles(element)
        if not _critical(ctx, element) or "destructive" in roles and element.get("id") not in ctx.path_element_ids:
            continue
        rect = _box_mm_rect(ctx, element["box"])
        p_miss = 1.0 - pointing.dual_gaussian_hit_probability(rect["w"], rect["h"], k)
        severity = None
        for limit, sev in params.MISS_PROBABILITY_SEVERITY:
            if p_miss >= limit:
                severity = sev
                break
        out.append(Observation(
            "PT-04", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
            [element["id"]], element_key(element),
            {"name": "miss_probability", "value": round(p_miss, 4), "unit": "probability", "threshold": params.MISS_PROBABILITY_SEVERITY[-1][0], "comparator": "<", "sigma_multiplier": k,
             "target_mm": [round(rect["w"], 2), round(rect["h"], 2)]},
            severity is None, severity,
            f"'{element.get('name') or element.get('text')}' 예측 오터치 확률 {p_miss*100:.1f}% (이중 가우시안, σ배수 {k:.2f}, {rect['w']:.1f}×{rect['h']:.1f}mm).",
            "bi-zhai-2016-dual-gaussian",
        ))
        for bad in destructive:
            if bad is element:
                continue
            bad_rect = _box_mm_rect(ctx, bad["box"])
            p_bad = pointing.dual_gaussian_neighbour_probability(rect, bad_rect, k)
            gap_mm = _point_mm(ctx, pointing.box_gap(element["box"], bad["box"]), 0)[0]
            if gap_mm > 20 and p_bad < 1e-4:
                continue
            severity = None
            if p_bad >= params.DESTRUCTIVE_NEIGHBOUR_PROB and "irreversible" in _roles(bad):
                severity = "P0"
            elif p_bad >= params.DESTRUCTIVE_NEIGHBOUR_PROB_HIGH:
                severity = "P1"
            elif p_bad >= params.DESTRUCTIVE_NEIGHBOUR_PROB:
                severity = "P2"
            elif gap_mm < params.DESTRUCTIVE_MIN_GAP_MM:
                severity = "P3"
            out.append(Observation(
                "PT-03", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                [element["id"], bad["id"]], element_key(bad),
                {"name": "destructive_misfire", "value": {"p_misfire": round(p_bad, 5), "gap_mm": round(gap_mm, 2)}, "unit": "probability/mm",
                 "threshold": {"p": params.DESTRUCTIVE_NEIGHBOUR_PROB, "gap_mm": params.DESTRUCTIVE_MIN_GAP_MM}, "comparator": "<", "sigma_multiplier": k},
                severity is None, severity,
                f"'{element.get('name') or element.get('text')}'을(를) 누르려다 '{bad.get('name') or bad.get('text')}'을(를) 누를 확률 {p_bad*100:.2f}%, 간격 {gap_mm:.1f}mm.",
                "bi-zhai-2016-dual-gaussian",
            ))
    return out


def check_fitts_sequence(ctx: Context) -> list[Observation]:
    step = ctx.step
    prev = ctx.previous
    if not step or not prev or ctx.is_touch:
        return []
    if step.get("action", {}).get("action") not in ("click", "tap", "double_tap"):
        return []
    point = step.get("point")
    prev_point = prev.get("focus_point")
    target = next((e for e in ctx.elements if e.get("id") == step.get("target_element_id")), None)
    if not point or not prev_point or not target:
        return []
    distance = math.hypot(point["x"] - prev_point["x"], point["y"] - prev_point["y"])
    width = max(1.0, min(target["box"]["w"], target["box"]["h"]))
    index = pointing.fitts_id(distance, width)
    failed = index > params.FITTS_ID_HIGH_BITS
    return [Observation(
        "PT-05", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
        [target["id"]], element_key(target),
        {"name": "fitts_id_bits", "value": round(index, 2), "unit": "bits", "threshold": params.FITTS_ID_HIGH_BITS, "comparator": "<=",
         "predicted_mt_ms": round(pointing.fitts_mt_ms(distance, width, params.FITTS_MOUSE_A_MS, params.FITTS_MOUSE_B_MS), 0)},
        not failed, "P3" if failed else None,
        f"직전 조작 위치에서 '{target.get('name') or target.get('text')}'까지 Fitts ID {index:.1f}bit.",
        "fitts-shannon-v1",
    )]


# ---------------------------------------------------------------- gaze

_FIXATION_CACHE: dict[tuple, dict[str, list[float]]] = {}


def _gaze_kind(ctx: Context) -> str:
    return gaze.prior_kind(getattr(ctx.device, "form_factor", "phone"), ctx.surface_kind)


def _priorities(ctx: Context) -> dict[str, float]:
    enriched = []
    for e in ctx.elements:
        item = dict(e)
        fg, bg = perception.parse_color(e.get("color_fg")), perception.parse_color(e.get("color_bg"))
        if fg and bg:
            item["_contrast"] = perception.contrast_ratio(fg, bg)
        fill, container = perception.parse_color(e.get("color_bg")), perception.parse_color(e.get("container_bg") or "#ffffff")
        if fill and container and e.get("interactive"):
            item["_fill_contrast"] = (perception.contrast_ratio(fill, container) - 1.0) / 4.0
        enriched.append(item)
    return gaze.element_priorities(enriched, ctx.viewport, _gaze_kind(ctx), ctx.conspicuity)


def _viewing_distance(ctx: Context) -> float:
    vision = ctx.attrs.get("vision", {})
    return float(vision.get("viewing_distance_mm") or getattr(ctx.device, "viewing_distance_mm", 300) or 300)


def _notice_scale(ctx: Context) -> float:
    vision = ctx.attrs.get("vision", {})
    older = ctx.attrs.get("age_band") == "70s+"
    low_vision = vision.get("acuity") in ("reduced", "low")
    loaded = ctx.attrs.get("cognition", {}).get("time_pressure") == "high"
    return params.NOTICE_PERSONA_SCALE if (older or low_vision or loaded) else 1.0


def _salient_change(ctx: Context, element: dict[str, Any], new: bool) -> tuple[bool, dict[str, Any]]:
    """GZ-02 salience: a new object that is >= 1 deg and >= 3:1 against its surroundings."""
    from .devices import mm_per_css_px

    size_px = max(element["box"]["w"], element["box"]["h"])
    size_deg = math.degrees(math.atan2(size_px * mm_per_css_px(ctx.device, "x"), _viewing_distance(ctx)))
    fg = perception.parse_color(element.get("color_fg"))
    bg = perception.parse_color(element.get("color_bg"))
    container = perception.parse_color(element.get("container_bg") or "#ffffff")
    contrast = 1.0
    if bg and container and bg != container:
        contrast = perception.contrast_ratio(bg, container)
    elif fg and bg:
        contrast = perception.contrast_ratio(fg, bg)
    salient = new and size_deg >= params.SALIENT_CHANGE_MIN_DEG and contrast >= params.SALIENT_CHANGE_MIN_CONTRAST
    return salient, {"size_deg": round(size_deg, 2), "contrast": round(contrast, 2), "new_object": new}


def check_gaze(ctx: Context) -> list[Observation]:
    from .devices import mm_per_css_px

    out: list[Observation] = []
    priorities = _priorities(ctx)
    if not priorities:
        return out
    kind = _gaze_kind(ctx)
    base = (ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"))
    focus = ctx.snapshot.get("focus_point")
    vw, vh = ctx.viewport
    if focus:
        start = (float(focus["x"]), float(focus["y"]))
    else:
        px, py = gaze.prior_peak(kind)
        start = (px * vw, py * vh)
    mm_px = mm_per_css_px(ctx.device, "x")
    viewing = _viewing_distance(ctx)
    centres = {e["id"]: pointing.centre(e["box"]) for e in ctx.elements if e["id"] in priorities}
    visible_primary = [e for e in ctx.elements if "primary" in _roles(e) and _visible(e) and e["id"] in priorities]
    if visible_primary:
        cache_key = (ctx.snapshot.get("snapshot_id"), ctx.run.get("run_id"), round(viewing), round(start[0], 1), round(start[1], 1), round(mm_px, 5))
        probs = _FIXATION_CACHE.get(cache_key)
        if probs is None:
            probs = gaze.fixation_probabilities(centres, priorities, start, mm_px, viewing, seed=zlib.crc32(str(ctx.snapshot.get("snapshot_id")).encode()) & 0xFFFF)
            _FIXATION_CACHE[cache_key] = probs
        k = params.GAZE_EARLY_FIXATIONS
        for element in visible_primary:
            p_seen = probs.get(element["id"], [0.0] * k)[k - 1]
            severity = None
            if p_seen < params.GAZE_PRIMARY_P2:
                severity = "P2"
            elif p_seen < params.GAZE_PRIMARY_PASS:
                severity = "P3"
            out.append(Observation(
                "GZ-01", *base, [element["id"]], element_key(element),
                {"name": "p_fixated_within_k", "value": round(p_seen, 3), "unit": "probability", "threshold": params.GAZE_PRIMARY_PASS,
                 "comparator": ">=", "k": k, "priority": round(priorities[element["id"]], 3)},
                severity is None, severity,
                f"주요 동작 '{element.get('name') or element.get('text')}'을(를) 처음 {k}번 시선 안에 볼 확률(모델) {p_seen:.2f}.",
                gaze.MODEL_ID,
            ))
            stronger = [key for key, v in priorities.items() if v > priorities[element["id"]] and key != element["id"]]
            interactive_ids = {e["id"] for e in _interactive(ctx)}
            competing = [key for key in stronger if key in interactive_ids]
            failed = len(competing) >= params.GAZE_COMPETITORS_MAX
            out.append(Observation(
                "GZ-04", *base, [element["id"], *competing[:5]], element_key(element),
                {"name": "competing_interactive_elements", "value": len(competing), "unit": "count", "threshold": params.GAZE_COMPETITORS_MAX, "comparator": "<"},
                not failed, "P3" if failed else None,
                f"주요 동작보다 시각적 우선순위가 높은 조작 요소 {len(competing)}개.",
                gaze.MODEL_ID,
            ))
    # GZ-02: feedback noticing after an action (change blindness + thumb occlusion).
    if ctx.previous is not None and focus:
        before = {e.get("selector") or e.get("id"): e for e in ctx.previous.get("elements", []) if _visible(e)}
        scale = _notice_scale(ctx)
        grip = ctx.attrs.get("grip", "")
        geom = reach.geometry_for_device(ctx.device) if ctx.is_touch else None
        thumb = float(ctx.attrs.get("thumb_length_mm") or params.THUMB_LENGTH_MM["all"][0])
        for element in ctx.elements:
            roles = _roles(element)
            is_feedback = roles & {"error_message", "critical_message", "status"} or element.get("role") in ("alert", "status")
            if not is_feedback or not _visible(element):
                continue
            key = element.get("selector") or element.get("id")
            prior = before.get(key)
            changed_text = prior is not None and (prior.get("text") or "") != (element.get("text") or "")
            if prior is not None and not changed_text:
                continue
            centre_css = pointing.centre(element["box"])
            theta = gaze.eccentricity_deg_css((focus["x"], focus["y"]), centre_css, mm_px, viewing)
            salient, sal = _salient_change(ctx, element, new=prior is None)
            band = gaze.notice_band(theta, salient, scale)
            occluded = False
            if geom is not None and grip.startswith("one_hand"):
                occluded = reach.occluded_by_thumb(_point_mm(ctx, focus["x"], focus["y"]), _point_mm(ctx, *centre_css), geom, grip, thumb, params.OCCLUSION_WEDGE_DEG)
            critical = bool(roles & {"error_message", "critical_message"}) or element.get("role") == "alert"
            severity = None
            if band == "likely_missed" or occluded:
                severity = "P2" if critical else "P3"
            elif band == "uncertain" and critical:
                severity = "P3"
            out.append(Observation(
                "GZ-02", *base, [element["id"]], element_key(element),
                {"name": "feedback_eccentricity_deg", "value": round(theta, 1), "unit": "deg", "threshold": params.NOTICE_BANDS_DEG["salient" if salient else "non_salient"],
                 "comparator": "band", "band": band, "salient": salient, "occluded_by_thumb": occluded, "persona_scale": scale, **sal},
                severity is None, severity,
                f"조작 지점에서 {theta:.0f}° 떨어진 곳에 {'새' if prior is None else '바뀐'} 메시지 '{(element.get('text') or element.get('name') or '')[:30]}'"
                + f" ({'돌출' if salient else '비돌출'} 변화, 인지 가능성: {band})" + (", 한 손 파지 엄지에 가려질 위치" if occluded else "") + ".",
                gaze.MODEL_ID,
            ))
    # GZ-03: banner-blindness proxy on desktop/web.
    if getattr(ctx.device, "form_factor", "phone") in ("desktop", "laptop"):
        for element in ctx.elements:
            roles = _roles(element)
            if not (roles & {"critical_message", "error_message", "status"}) or not _visible(element):
                continue
            box = element["box"]
            right_rail = box["x"] >= vw * params.AD_RAIL_X_FRAC
            banner = box["y"] <= vh * params.AD_BANNER_Y_FRAC and box["w"] >= vw * 0.6 and box["h"] <= params.AD_BANNER_MAX_H
            ad_like = "ad_like" in roles
            failed = right_rail or ad_like
            if not failed and not banner:
                continue
            out.append(Observation(
                "GZ-03", *base, [element["id"]], element_key(element),
                {"name": "ad_like_zone", "value": {"right_rail": right_rail, "top_banner": banner, "declared_ad_like": ad_like}, "unit": "flags", "threshold": "none", "comparator": "=="},
                not failed, "P3" if failed else None,
                f"중요 정보 '{(element.get('text') or '')[:30]}'이(가) 광고 영역처럼 보이는 위치에 있습니다(배너 블라인드니스 위험, 판단 확인 필요).",
                "ad-zone-proxy-v1",
            ))
    return out


# ---------------------------------------------------------------- perception

def check_contrast(ctx: Context) -> list[Observation]:
    out: list[Observation] = []
    lighting = ctx.attrs.get("context", {}).get("lighting")
    for element in ctx.elements:
        text = (element.get("text") or "").strip()
        if not text or not _visible(element) or element.get("enabled", True) is False:
            continue
        fg, bg = perception.parse_color(element.get("color_fg")), perception.parse_color(element.get("color_bg"))
        if not fg or not bg:
            continue
        ratio = perception.contrast_ratio(fg, bg)
        need = perception.required_text_contrast(element.get("font_size_px"), element.get("font_weight"))
        if ratio < need:
            severity = "P2"
            if ratio < params.CONTRAST_SEVERE:
                severity = "P1"
            if _roles(element) & {"primary", "critical_message", "error_message"}:
                severity = "P1"
            out.append(Observation(
                "PC-01", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                [element["id"]], element_key(element),
                {"name": "contrast_ratio", "value": round(ratio, 2), "unit": "ratio", "threshold": need, "comparator": ">=",
                 "fg": element.get("color_fg"), "bg": element.get("color_bg"), "font_size_px": element.get("font_size_px")},
                False, severity,
                f"'{text[:30]}' 대비 {ratio:.2f}:1 (기준 {need}:1).",
            ))
        elif lighting == "bright_sun" and ratio < params.CONTRAST_BRIGHT_LIGHT:
            if not (_roles(element) & {"primary", "critical_message", "error_message", "status"} or element.get("interactive")):
                continue
            out.append(Observation(
                "PC-05", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                [element["id"]], element_key(element),
                {"name": "contrast_ratio", "value": round(ratio, 2), "unit": "ratio", "threshold": params.CONTRAST_BRIGHT_LIGHT, "comparator": ">="},
                False, "P3",
                f"햇빛 환경에서 '{text[:30]}' 대비 {ratio:.2f}:1은 여유가 부족할 수 있습니다.",
                "situational-contrast-v1",
            ))
    for element in _interactive(ctx):
        border = perception.parse_color(element.get("border_color"))
        bg = perception.parse_color(element.get("container_bg") or element.get("color_bg"))
        fill = perception.parse_color(element.get("color_bg"))
        container = perception.parse_color(element.get("container_bg"))
        candidates = []
        if border and bg:
            candidates.append(("border", perception.contrast_ratio(border, bg)))
        if fill and container and fill != container:
            candidates.append(("fill", perception.contrast_ratio(fill, container)))
        if not candidates:
            continue
        best_kind, best = max(candidates, key=lambda c: c[1])
        if best < params.NON_TEXT_CONTRAST_MIN and element.get("tag") in ("input", "select", "textarea", "button") and element.get("enabled", True):
            out.append(Observation(
                "PC-02", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                [element["id"]], element_key(element),
                {"name": "non_text_contrast", "value": round(best, 2), "unit": "ratio", "threshold": params.NON_TEXT_CONTRAST_MIN, "comparator": ">=", "kind": best_kind},
                False, _escalate("P2", element) if element.get("tag") != "button" else "P3",
                f"'{element.get('name') or element.get('selector')}' 경계 대비 {best:.2f}:1 (기준 3:1).",
            ))
    return out


def _colour_groups(ctx: Context) -> list[list[dict[str, Any]]]:
    groups: dict[tuple, list[dict[str, Any]]] = {}
    for element in ctx.elements:
        if not _visible(element):
            continue
        colour = element.get("color_bg") if element.get("color_bg") and not (element.get("text") or "").strip() else element.get("color_fg")
        if not perception.parse_color(colour):
            continue
        box = element["box"]
        key = (element.get("tag"), element.get("role"), round(box["w"] / 4), round(box["h"] / 4), tuple(sorted(_roles(element) - {"primary"})))
        groups.setdefault(key, []).append(element)
    return [g for g in groups.values() if len(g) >= 2]


def check_colour_only(ctx: Context) -> list[Observation]:
    kind = ctx.attrs.get("vision", {}).get("cvd", "none")
    if kind in (None, "none"):
        return []
    severity_level = float(ctx.attrs.get("vision", {}).get("cvd_severity") or 1.0)
    out: list[Observation] = []
    seen: set[tuple[str, str]] = set()
    for group in _colour_groups(ctx):
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                text_a = (a.get("text") or a.get("name") or "").strip()
                text_b = (b.get("text") or b.get("name") or "").strip()
                if text_a != text_b and text_a and text_b:
                    continue  # a textual cue distinguishes them
                use_bg = not text_a
                ca = perception.parse_color(a.get("color_bg") if use_bg else a.get("color_fg"))
                cb = perception.parse_color(b.get("color_bg") if use_bg else b.get("color_fg"))
                if not ca or not cb:
                    continue
                normal = perception.color_difference(ca, cb)
                if normal < params.CVD_DISTINCT_NORMAL_DE:
                    continue  # not meant to be different colours
                simulated = perception.cvd_difference(ca, cb, kind, severity_level)
                pair = tuple(sorted((a["id"], b["id"])))
                if pair in seen:
                    continue
                seen.add(pair)
                state_contrast = perception.contrast_ratio(ca, cb)
                if simulated >= params.CVD_MARGINAL_DE or state_contrast >= params.CVD_STATE_CONTRAST_EXEMPT:
                    continue  # distinct after simulation, or a >= 3:1 luminance cue separates the states (G183)
                marginal = simulated >= params.CVD_CONFUSABLE_DE
                out.append(Observation(
                    "PC-03", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                    [a["id"], b["id"]], element_key(a),
                    {"name": "cvd_delta_e2000", "value": round(simulated, 1), "unit": "dE00", "threshold": params.CVD_MARGINAL_DE, "comparator": ">=",
                     "normal_delta_e2000": round(normal, 1), "cvd": kind, "state_contrast": round(state_contrast, 2),
                     "confidence": "low" if kind == "tritan" else "model"},
                    False, "P3" if marginal else "P2",
                    f"'{text_a or a.get('selector')}'와 '{text_b or b.get('selector')}'은(는) 색으로만 구분되며 {kind} 시뮬레이션에서 ΔE00 {simulated:.1f}로 거의 같아 보입니다.",
                    "machado2009-ciede2000-v1",
                ))
    return out


def check_text_size(ctx: Context) -> list[Observation]:
    """Font-size visual angle: floor (ISO ~16') and Hangul critical print size (P3)."""
    out: list[Observation] = []
    vision = ctx.attrs.get("vision", {})
    presbyopic = bool(vision.get("presbyopia")) or vision.get("acuity") in ("reduced", "low")
    viewing = _viewing_distance(ctx)
    if presbyopic and ctx.is_touch:
        viewing = max(viewing, float(params.PRESBYOPIA_VIEWING_DISTANCE_MM))
    comfortable = params.TEXT_MIN_ARCMIN_PRESBYOPIA if presbyopic or ctx.attrs.get("age_band") in ("60s", "70s+") else params.TEXT_MIN_ARCMIN
    is_game_surface = ctx.surface_kind == "game"
    for element in ctx.elements:
        text = (element.get("text") or "").strip()
        size = element.get("font_size_px")
        if not text or not size or not _visible(element):
            continue
        size_mm = _point_mm(ctx, float(size), 0)[0]
        angle = perception.visual_angle_arcmin(size_mm, viewing)
        hud = "hud" in _roles(element) or is_game_surface
        critical = bool(_roles(element) & {"error_message", "critical_message", "primary"}) or len(text) >= params.BODY_TEXT_MIN_CHARS
        form = getattr(ctx.device, "form_factor", "phone")
        floor_1080 = params.HUD_PLATFORM_MIN_PX_1080.get(form)
        if hud and floor_1080:
            display_px_h = (getattr(ctx.device, "display_px", (0, 0)) or (0, 0))[1] or 1080
            dpr = float(getattr(ctx.device, "dpr", 1.0) or 1.0)
            floor_css = floor_1080 * (display_px_h / 1080.0) / dpr
            if float(size) < floor_css:
                out.append(Observation(
                    "GM-01", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
                    [element["id"]], element_key(element),
                    {"name": "hud_text_css_px", "value": size, "unit": "css_px", "threshold": round(floor_css, 1), "comparator": ">=", "standard": "XAG 101"},
                    False, "P2",
                    f"HUD 글자 '{text[:20]}' {size}px < 플랫폼 최소 {floor_css:.0f}px(XAG 101, 1080p 기준 {floor_1080:.0f}px).",
                    "xag-101-floor",
                ))
        check_id = "GM-01" if hud else "PC-04"
        if angle < params.TEXT_FLOOR_ARCMIN:
            severity, threshold, tier = ("P1" if critical and _roles(element) & {"error_message", "critical_message"} else "P2"), params.TEXT_FLOOR_ARCMIN, "floor"
        elif angle < comfortable and not hud:
            severity, threshold, tier = "P3", comfortable, "critical_print_size"
        else:
            continue
        out.append(Observation(
            check_id, ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
            [element["id"]], element_key(element),
            {"name": "font_visual_angle_arcmin", "value": round(angle, 1), "unit": "arcmin", "threshold": threshold, "comparator": ">=",
             "tier": tier, "font_size_px": size, "viewing_distance_mm": viewing},
            False, severity,
            f"'{text[:30]}' 글자({size}px≈{size_mm:.1f}mm)가 {viewing/10:.0f}cm 거리에서 {angle:.0f}′"
            + (" — 가독 하한(16′) 미만." if tier == "floor" else f" — 한글 임계 글자 크기({threshold:.0f}′) 미만으로 읽기 속도가 떨어질 수 있음."),
            "visual-angle-v2",
        ))
    return out


# ---------------------------------------------------------------- cognition

def check_choice_overload(ctx: Context) -> list[Observation]:
    out: list[Observation] = []
    groups: dict[tuple, list[dict[str, Any]]] = {}
    for element in _interactive(ctx):
        box = element["box"]
        key = (element.get("tag"), element.get("role"), round(box["w"] / 8), round(box["h"] / 8), element.get("font_weight"))
        groups.setdefault(key, []).append(element)
    for members in groups.values():
        if len(members) <= params.CHOICE_OVERLOAD_MAX:
            continue
        decision_ms = cognition.hick_hyman_ms(len(members))
        out.append(Observation(
            "CG-01", ctx.run["run_id"], ctx.profile["profile_id"], ctx.snapshot.get("snapshot_id"), ctx.snapshot.get("step_index"),
            [m["id"] for m in members[:12]], element_key(members[0]),
            {"name": "equal_choices", "value": len(members), "unit": "count", "threshold": params.CHOICE_OVERLOAD_MAX, "comparator": "<=",
             "hick_decision_ms": round(decision_ms)},
            False, "P3",
            f"동일한 모양의 선택지 {len(members)}개(힉-하이먼 예측 결정 시간 약 {decision_ms/1000:.1f}초).",
            "hick-hyman-v1",
        ))
    return out


def check_run_timing(run: dict[str, Any], profile: dict[str, Any], device: Any, snapshots: dict[str, dict[str, Any]], scenario: dict[str, Any] | None) -> list[Observation]:
    """Checks that need the whole run: feedback latency, transient text, QTE windows, flashes."""
    out: list[Observation] = []
    attrs = profile.get("attributes", {})
    run_id, pid = run["run_id"], profile["profile_id"]
    for step in run.get("steps", []):
        action = (step.get("action") or {}).get("action")
        if action not in ("tap", "click", "double_tap", "press") or step.get("result") != "ok":
            continue
        latency = step.get("feedback_latency_ms")
        band = cognition.latency_band(latency)
        target_id = step.get("target_element_id") or ""
        after = snapshots.get(step.get("after") or "", {})
        target = next((e for e in after.get("elements", []) if e.get("id") == target_id), None)
        key = element_key(target) if target else f"{target_id}|{(step.get('action') or {}).get('target', '')}"
        severity = None
        if band == "needs_progress_indicator":
            severity = "P2"
        elif band == "attention_lost":
            severity = "P1"
        elif band == "no_feedback" and action in ("tap", "click"):
            severity = "P2"
        elif band == "noticeable" and latency is not None and latency > params.LATENCY_DOHERTY_MS:
            severity = "P3"
        out.append(Observation(
            "CG-03", run_id, pid, step.get("after"), step.get("step_index"),
            [target_id] if target_id else [], key,
            {"name": "feedback_latency_ms", "value": latency, "unit": "ms", "threshold": params.LATENCY_FLOW_MS, "comparator": "<=", "band": band},
            severity is None, severity,
            f"{step.get('step_index')}단계 조작 후 첫 화면 변화까지 {latency if latency is not None else '없음'}ms ({band}).",
        ))
    age = attrs.get("age_band", "30s")
    reading_rate = float(params.READING_SLOW_SYLLABLES_PER_MIN.get(age, 330))
    windows = {w.get("id"): w for w in (scenario or {}).get("timing_windows", [])}
    for measured in run.get("timing_windows", []):
        declared = windows.get(measured.get("id"), {})
        durations = measured.get("intervals_ms") or measured.get("visible_ms")
        if isinstance(durations, (int, float)):
            durations = [durations]
        durations = [d for d in (durations or []) if isinstance(d, (int, float))]
        if not durations:
            continue
        shortest = min(durations)
        kind = declared.get("kind") or measured.get("kind") or "transient_text"
        key = f"{declared.get('selector') or measured.get('selector') or measured.get('id')}|{measured.get('id')}"
        if kind == "qte":
            rt = float(attrs.get("reaction_time_ms") or params.choice_reaction_ms_for_age("30s"))
            rt95 = game.reaction_time_quantile_ms(rt, rt * params.RT_CV, 0.95)
            margin = game.timing_window_margin_ms(shortest, rt95, params.INPUT_LATENCY_MS.get(getattr(device, "input", "touch"), 80))
            failed = margin < 0
            out.append(Observation(
                "GM-03", run_id, pid, None, None, [], key,
                {"name": "timing_margin_ms", "value": round(margin), "unit": "ms", "threshold": 0, "comparator": ">=",
                 "window_ms": shortest, "reaction_p95_ms": round(rt95)},
                not failed, "P1" if failed else None,
                f"입력 제한 시간 {shortest:.0f}ms < 이 프로필의 반응 95백분위 {rt95:.0f}ms + 동작/지연.",
                "reaction-window-v1",
            ))
        else:
            text = declared.get("text") or measured.get("text") or ""
            has_action = bool(declared.get("has_action") or measured.get("has_action"))
            need = cognition.min_display_ms(text, reading_rate) if text else params.TOAST_FLOOR_MS
            failed = shortest < need or has_action
            severity = ("P1" if has_action else "P2") if failed else None
            out.append(Observation(
                "CG-02", run_id, pid, None, None, [], key,
                {"name": "visible_ms", "value": shortest, "unit": "ms", "threshold": round(need), "comparator": ">=", "chars": len(text),
                 "reading_rate_syll_per_min": reading_rate, "has_action": has_action},
                not failed, severity,
                f"'{text[:30]}' 메시지가 {shortest:.0f}ms만 표시됨(느린 독자 기준 읽기 필요 시간 약 {need:.0f}ms)"
                + (" — 동작이 포함된 메시지가 자동으로 사라짐(WCAG 2.2.1)." if has_action else "."),
                "reading-time-v2",
            ))
    samples = run.get("flash_samples") or []
    if samples:
        stats = game.count_general_flashes(samples)
        display = getattr(device, "display_mm", None) or (0, 0)
        viewing = float(attrs.get("vision", {}).get("viewing_distance_mm") or getattr(device, "viewing_distance_mm", 300))
        big = game.flash_area_exceeds(stats["max_area_fraction"], display[0], display[1], viewing) if display[0] else stats["max_area_fraction"] > 0.25
        failed = stats["max_flashes_per_window"] > 3 and big
        extended = not failed and stats["extended"] and big
        out.append(Observation(
            "GM-04", run_id, pid, None, None, [], "viewport|flash",
            {"name": "flashes_per_second", "value": stats["max_flashes_per_window"], "unit": "flashes/s", "threshold": 3, "comparator": "<=",
             "area_fraction": round(stats["max_area_fraction"], 3), "area_exceeds": big,
             "flashes_per_5s": stats["max_flashes_per_5s"], "extended_failure": extended},
            not (failed or extended), "P0" if failed else ("P1" if extended else None),
            f"1초 창에서 최대 {stats['max_flashes_per_window']:.1f}회 섬광(5초 창 {stats['max_flashes_per_5s']:.1f}회), 변화 면적 {stats['max_area_fraction']*100:.0f}%."
            + (" 인증 도구(EA IRIS/Harding)로 재검사가 필요합니다." if failed or extended else ""),
            "general-flash-screen-v1",
        ))
    for note in run.get("persona_notes", []):
        if not note.get("confusion"):
            continue
        failure_class = note.get("failure_class", "unknown")
        if failure_class in ("agent_limitation", "environment"):
            continue  # a run limitation, not a UX finding (recorded in the report as a limitation)
        # Judgment-only findings: P3 by default; P2 at most, and only when the same
        # mismatch was replicated by another agent model or input channel.
        severity = "P2" if note.get("corroborated") else "P3"
        out.append(Observation(
            "PJ-01", run_id, pid, None, note.get("step_index"), [], f"step-{note.get('step_index')}|persona-note",
            {"name": "persona_confusion", "value": True, "unit": "flag", "threshold": False, "comparator": "==",
             "failure_class": failure_class, "corroborated": bool(note.get("corroborated"))},
            False, severity,
            f"페르소나 기록(시뮬레이션·실제 사용자 발화 아님): 의도 '{note.get('intent', '')}' / 기대 '{note.get('expected', '')}' / 화면 '{note.get('observed', '')}'",
            "llm-persona-note",
            {"agent": run.get("agent", {})},
        ))
    return out


SNAPSHOT_CHECKS: tuple[Callable[[Context], list[Observation]], ...] = (
    check_reach,
    check_target_size,
    check_touch_accuracy,
    check_fitts_sequence,
    check_gaze,
    check_contrast,
    check_colour_only,
    check_text_size,
    check_choice_overload,
)


def run_snapshot_checks(ctx: Context) -> list[Observation]:
    out: list[Observation] = []
    for check in SNAPSHOT_CHECKS:
        out.extend(check(ctx))
    return out


def iter_catalog() -> Iterable[CheckSpec]:
    return CATALOG.values()
