"""Evaluate a recorded run (ergo-run.v1 directory) under one or more profiles.

A run is recorded once on a real surface by a driver. Ergonomic models are then
evaluated for the run's own profile and, with ``cross_profile=True``, for every
other profile that uses the same device and orientation: the screen geometry is
identical, only the human model differs. Actions chosen by an LLM persona are
not re-simulated for other profiles; judgment notes stay with their own run.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from . import checks, png
from .devices import device_for_snapshot, get_device, rotate
from .hf import gaze
from .snapshot import load_run_dir

SEVERITY_RANK = checks.SEVERITY_ORDER


_CONSPICUITY_CACHE: dict[tuple[str, int], list[list[float]] | None] = {}


def conspicuity_for_snapshot(snapshot: dict[str, Any], cell_css_px: int = 8) -> list[list[float]] | None:
    """Bottom-up conspicuity grid for a snapshot screenshot (None if unavailable).

    Prefers the driver's CSS-scale copy (``screenshot.css``); results are cached
    by screenshot hash so repeated analyses do not decode again.
    """
    shot = snapshot.get("screenshot", {})
    path = shot.get("resolved_path")
    if not path or not Path(path).is_file():
        return None
    css = shot.get("css") if isinstance(shot.get("css"), dict) else None
    if css and isinstance(css.get("path"), str):
        try:
            from .snapshot import resolve_within, sha256_file

            css_path = resolve_within(Path(path).parent, css["path"])
            if css_path.is_file() and (not css.get("sha256") or sha256_file(css_path) == css["sha256"]):
                path = str(css_path)
            else:
                css = None
        except Exception:  # noqa: BLE001 - fall back to the full screenshot
            css = None
    cache_key = (str(shot.get("sha256") or path) + ("|css" if css else ""), cell_css_px)
    if cache_key in _CONSPICUITY_CACHE:
        return _CONSPICUITY_CACHE[cache_key]
    try:
        image = png.to_rgb(png.read_png(path))
    except (png.PNGError, OSError):
        _CONSPICUITY_CACHE[cache_key] = None
        return None
    dpr = 1.0 if css else float(snapshot.get("device", {}).get("dpr") or 1.0)
    factor = max(1, int(round(cell_css_px * dpr)))
    small = png.downsample(image, factor)
    data = small.data
    rows = []
    for y in range(small.height):
        base = y * small.width * 3
        rows.append([(data[base + 3 * x], data[base + 3 * x + 1], data[base + 3 * x + 2]) for x in range(small.width)])
    grid = gaze.conspicuity_map(rows)
    _CONSPICUITY_CACHE[cache_key] = grid
    return grid


def _device_for(snapshot: dict[str, Any], profile: dict[str, Any]):
    device_block = snapshot.get("device", {})
    try:
        return device_for_snapshot(device_block)
    except Exception:  # noqa: BLE001 - fall back to the profile's device id
        device = get_device(profile["attributes"]["device_id"])
        if device_block.get("orientation") == "landscape":
            device = rotate(device, "landscape")
        return device


def _path_selectors(run: dict[str, Any], snapshots_by_id: dict[str, dict[str, Any]]) -> set[str]:
    selectors: set[str] = set()
    for step in run.get("steps", []):
        target_id = step.get("target_element_id")
        before = snapshots_by_id.get(step.get("before") or "")
        if before and target_id:
            element = next((e for e in before.get("elements", []) if e.get("id") == target_id), None)
            if element and element.get("selector"):
                selectors.add(element["selector"])
        target = (step.get("action") or {}).get("target")
        if isinstance(target, str):
            selectors.add(target)
    return selectors


def _dedupe(observations: list[checks.Observation]) -> list[checks.Observation]:
    """Keep one observation per (check, element, profile, run): the worst one."""
    best: dict[tuple, checks.Observation] = {}
    order: list[tuple] = []
    for obs in observations:
        key = (obs.check_id, obs.element_key, obs.profile_id, obs.run_id)
        current = best.get(key)
        if current is None:
            best[key] = obs
            order.append(key)
            continue
        if current.passed and not obs.passed:
            best[key] = obs
        elif not current.passed and not obs.passed and SEVERITY_RANK.get(obs.severity or "P3", 3) < SEVERITY_RANK.get(current.severity or "P3", 3):
            best[key] = obs
    return [best[k] for k in order]


def run_health(run: dict[str, Any], snapshots: list[dict[str, Any]], scenario: dict[str, Any] | None) -> tuple[str, list[str]]:
    """``ok``, ``degraded`` or ``failed`` plus human-readable reasons.

    A run that failed a step, lost off-origin resources, hit the element cap, or never
    saw a declared timing window cannot support a clean result; the report and the CI
    gate must say so (cross-review 2026-09-28).
    """
    rid = run.get("run_id")
    notes: list[str] = []
    health = "ok"
    if run.get("status") not in (None, "completed") or run.get("success") is False:
        health = "failed"
        bad = [s for s in run.get("steps", []) if s.get("result") not in (None, "ok")]
        where = f" (step {bad[0].get('step_index')}: {bad[0].get('result')})" if bad else ""
        notes.append(f"{rid}: 실행 상태 {run.get('status')}, 성공 {run.get('success')}{where} — 이후 화면은 검사되지 않았습니다.")
    driver = run.get("driver") or {}
    blocked = ((driver.get("network_policy") or {}).get("blocked_requests") or 0) if isinstance(driver, dict) else 0
    if blocked:
        health = "degraded" if health == "ok" else health
        notes.append(f"{rid}: 다른 출처 요청 {blocked}건을 차단했습니다(스타일/스크립트가 빠졌을 수 있음; 필요하면 --allow-origin).")
    capped = [n for snap in snapshots for n in (snap.get("notes") or []) if "capped" in str(n)]
    if capped:
        health = "degraded" if health == "ok" else health
        notes.append(f"{rid}: 요소 수 상한으로 일부 요소를 검사하지 못했습니다({capped[0]}).")
    declared = {w.get("id") for w in (scenario or {}).get("timing_windows", [])}
    for w in run.get("timing_windows", []):
        if w.get("id") in declared and not w.get("appearances") and not w.get("error"):
            notes.append(f"{rid}: 선언된 시간 창 '{w.get('id')}'이(가) 한 번도 나타나지 않았습니다(시나리오 경로 또는 선택자 확인).")
        if w.get("error"):
            health = "degraded" if health == "ok" else health
            notes.append(f"{rid}: 시간 창 '{w.get('id')}' 측정 오류: {w.get('error')}")
    game = (run.get("surface") or {}).get("kind") == "game" or any(w.get("kind") == "qte" for w in (scenario or {}).get("timing_windows", []))
    if game and not (run.get("flash_sampling") or {}).get("enabled"):
        notes.append(f"{rid}: 섬광(광과민성) 프레임 검사를 하지 않았습니다(--flash-sample-ms 없음). GM-04 결과가 없다는 것은 통과가 아닙니다.")
    return health, notes


def analyze_run(
    run_dir: str | Path,
    profiles: Iterable[dict[str, Any]],
    scenario: dict[str, Any] | None = None,
    cross_profile: bool = False,
    verify_screenshots: bool = True,
    gaze_enabled: bool = True,
) -> dict[str, Any]:
    run, snapshots = load_run_dir(run_dir, verify_screenshots=verify_screenshots)
    profile_list = list(profiles)
    by_id = {p["profile_id"]: p for p in profile_list}
    own = by_id.get(run.get("profile_id"))
    if own is None:
        raise ValueError(f"profile {run.get('profile_id')!r} of run {run['run_id']} not supplied")
    if not snapshots:
        raise ValueError(f"run {run['run_id']} has no snapshots")
    device_id = own["attributes"]["device_id"]
    orientation = snapshots[0].get("device", {}).get("orientation", own["attributes"].get("orientation", "portrait"))
    evaluated = [own]
    if cross_profile:
        evaluated += [
            p for p in profile_list
            if p is not own and p["attributes"]["device_id"] == device_id and p["attributes"].get("orientation", "portrait") == orientation
        ]
    snapshots_by_id = {s["snapshot_id"]: s for s in snapshots}
    step_by_after = {s.get("after"): s for s in run.get("steps", []) if s.get("after")}
    selectors = _path_selectors(run, snapshots_by_id)
    conspicuity: dict[str, Any] = {}
    if gaze_enabled:
        for snap in snapshots:
            conspicuity[snap["snapshot_id"]] = conspicuity_for_snapshot(snap)
    observations: list[checks.Observation] = []
    for profile in evaluated:
        previous = None
        for snap in snapshots:
            device = _device_for(snap, profile)
            path_ids = {e["id"] for e in snap.get("elements", []) if e.get("selector") in selectors}
            ctx = checks.Context(
                run=run, snapshot=snap, previous=previous, step=step_by_after.get(snap["snapshot_id"]),
                profile=profile, device=device, scenario=scenario, conspicuity=conspicuity.get(snap["snapshot_id"]),
                path_element_ids=path_ids,
            )
            observations.extend(checks.run_snapshot_checks(ctx))
            previous = snap
        device = _device_for(snapshots[-1], profile)
        run_obs = checks.check_run_timing(run, profile, device, snapshots_by_id, scenario) + checks.check_focus_walks(run, profile)
        if profile is not own:
            run_obs = [o for o in run_obs if o.check_id != "PJ-01"]
        observations.extend(run_obs)
    observations = _dedupe(observations)
    selector_of = {
        (snap["snapshot_id"], e.get("id")): e.get("selector")
        for snap in snapshots for e in snap.get("elements", []) if e.get("selector")
    }
    context_of = {
        (snap["snapshot_id"], e.get("id")): [f"#{a}" for a in (e.get("ancestor_ids") or []) if isinstance(a, str) and a]
        for snap in snapshots for e in snap.get("elements", [])
    }
    estimated = {snap["snapshot_id"] for snap in snapshots if snap.get("geometry_basis") == "estimated"}
    vision_elements = {(snap["snapshot_id"], e.get("id")) for snap in snapshots for e in snap.get("elements", []) if e.get("source") == "vision"}
    dicts = []
    for index, obs in enumerate(observations):
        record = obs.to_dict(index)
        if obs.snapshot_id in estimated or any((obs.snapshot_id, eid) in vision_elements for eid in obs.element_ids):
            # Geometry or colours estimated from a screenshot (spec section 11): never observed.
            record["epistemic_status"] = "inferred"
            record["geometry_basis"] = "estimated"
        record["selectors"] = [s for s in (selector_of.get((obs.snapshot_id, eid)) for eid in obs.element_ids) if s] or list(obs.extra.get("anchor_selectors") or [])
        record["context_selectors"] = sorted({c for eid in obs.element_ids for c in context_of.get((obs.snapshot_id, eid), [])})
        record["scenario_id"] = run.get("scenario_id")
        dicts.append(record)
    coverage: dict[str, list[str]] = {}
    for obs in observations:
        coverage.setdefault(f"{obs.check_id}||{obs.element_key}", [])
        if obs.profile_id not in coverage[f"{obs.check_id}||{obs.element_key}"]:
            coverage[f"{obs.check_id}||{obs.element_key}"].append(obs.profile_id)
    limitations = [
        f"{run['run_id']} step {n.get('step_index')}: {n.get('failure_class')} — {n.get('observed', '')}"
        for n in run.get("persona_notes", []) if n.get("confusion") and n.get("failure_class") in ("agent_limitation", "environment")
    ]
    health, health_notes = run_health(run, snapshots, scenario)
    limitations += health_notes
    return {
        "health": health,
        "limitations": limitations,
        "agent": run.get("agent", {}),
        "run_id": run["run_id"],
        "scenario_id": run.get("scenario_id"),
        "run_status": run.get("status"),
        "run_success": run.get("success"),
        "device_id": device_id,
        "orientation": orientation,
        "profiles_evaluated": [p["profile_id"] for p in evaluated],
        "observations": dicts,
        "coverage": coverage,
    }
