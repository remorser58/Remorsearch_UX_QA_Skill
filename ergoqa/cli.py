"""Command line entry for the ergonomic persona-swarm QA (scripts/ergo_qa.py)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import analyze, audience, bench, bundle, checks, report, swarm
from .devices import get_device, list_devices
from .profiles import sample_profiles, validate_profile
from .snapshot import SnapshotError, load_json

EXIT_OK, EXIT_FINDINGS, EXIT_USAGE = 0, 1, 2


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _load_profiles(path: str) -> list[dict[str, Any]]:
    data = load_json(path)
    profiles = data.get("profiles") if isinstance(data, dict) else data
    if not isinstance(profiles, list):
        raise ValueError("profiles file must be a list or {\"profiles\": [...]}")
    for profile in profiles:
        errors = validate_profile(profile)
        if errors:
            raise ValueError(f"{profile.get('profile_id', '?')}: {'; '.join(errors)}")
    return profiles


def _load_scenarios(paths: list[str]) -> dict[str, dict[str, Any]]:
    scenarios: dict[str, dict[str, Any]] = {}
    for raw in paths:
        path = Path(raw)
        files = sorted(path.glob("*.json")) if path.is_dir() else [path]
        for file in files:
            doc = load_json(file)
            if isinstance(doc, dict) and doc.get("schema_version") == "ergo-scenario.v1":
                scenarios[doc["scenario_id"]] = doc
    return scenarios


def cmd_devices(args: argparse.Namespace) -> int:
    devices = list_devices()
    if args.json:
        print(json.dumps([d.to_dict() if hasattr(d, "to_dict") else d.__dict__ for d in devices], ensure_ascii=False, indent=2, default=list))
        return EXIT_OK
    for d in devices:
        print(f"{d.id:22s} {d.form_factor:16s} {d.viewport_css[0]:>5}x{d.viewport_css[1]:<5} dpr {d.dpr:<5} body {d.physical_mm[0]}x{d.physical_mm[1]}mm  {d.input}")
    return EXIT_OK


def cmd_profiles(args: argparse.Namespace) -> int:
    device_ids = [d.strip() for d in args.devices.split(",") if d.strip()]
    for device_id in device_ids:
        get_device(device_id)
    personas = load_json(args.personas) if args.personas else None
    if isinstance(personas, dict):
        personas = personas.get("records")
    profiles = sample_profiles(args.count, args.seed, device_ids, args.strategy, personas, args.orientation)
    _write_json(Path(args.out), {"strategy": args.strategy, "seed": args.seed, "profiles": profiles})
    for p in profiles:
        print(f"{p['profile_id']}  {p['label_ko']}  [{p['attributes']['device_id']}]")
    return EXIT_OK


def cmd_audience_check(args: argparse.Namespace) -> int:
    doc = load_json(args.audience)
    errors = audience.validate_audience(doc)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return EXIT_USAGE
    segs = doc["segments"]
    print(f"ok: {doc['audience_id']} — {len(segs)} segments, {len(doc['sources'])} sources, "
          f"{sum(len(s.get('tasks') or []) for s in segs)} tasks")
    return EXIT_OK


def cmd_personas(args: argparse.Namespace) -> int:
    doc = load_json(args.audience)
    floors = None if args.floors is None else [f for f in args.floors.split(",") if f]
    plan = audience.compose(doc, args.budget, floors)
    _write_json(Path(args.out), {"strategy": "audience_composed", "audience_id": doc["audience_id"], "plan": {k: v for k, v in plan.items() if k != "profiles"}, "profiles": plan["profiles"]})
    if args.plan:
        Path(args.plan).parent.mkdir(parents=True, exist_ok=True)
        Path(args.plan).write_text(audience.plan_markdown(plan, doc), encoding="utf-8")
    for p in plan["profiles"]:
        print(f"{p['profile_id']}  {p['label_ko']}  [{p['attributes']['device_id']}]  ({p['audience_ref']['facet']})")
    if plan["untested"]:
        print(f"untested within budget: {len(plan['untested'])} (see plan)")
    return EXIT_OK


def cmd_scenario_stubs(args: argparse.Namespace) -> int:
    doc = load_json(args.audience)
    out = Path(args.out)
    for stub in audience.scenario_stubs(doc):
        _write_json(out / f"{stub['scenario_id']}.json", stub)
        print(f"{stub['scenario_id']}: {stub['task_goal_ko']}  devices={','.join(stub['device_ids'])}")
    return EXIT_OK


def _analyses(args: argparse.Namespace, profiles: list[dict[str, Any]], scenarios: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    runs_root = Path(args.runs)
    run_dirs = [runs_root] if (runs_root / "run.json").is_file() else sorted(p for p in runs_root.iterdir() if (p / "run.json").is_file())
    if not run_dirs:
        raise ValueError(f"no run directories under {runs_root}")
    out = []
    for run_dir in run_dirs:
        run_doc = load_json(run_dir / "run.json")
        scenario = scenarios.get(run_doc.get("scenario_id"))
        out.append(analyze.analyze_run(run_dir, profiles, scenario, cross_profile=args.cross_profile, gaze_enabled=not args.no_gaze))
    return out


def cmd_analyze(args: argparse.Namespace) -> int:
    profiles = _load_profiles(args.profiles)
    scenarios = _load_scenarios(args.scenario or [])
    analyses = _analyses(args, profiles, scenarios)
    _write_json(Path(args.out), {"analyses": analyses})
    failed = sum(1 for a in analyses for o in a["observations"] if not o["passed"])
    print(f"{len(analyses)} run(s), {failed} failing observation(s) -> {args.out}")
    return EXIT_OK


def cmd_swarm(args: argparse.Namespace) -> int:
    profiles = _load_profiles(args.profiles)
    scenarios = _load_scenarios(args.scenario or [])
    analyses = _analyses(args, profiles, scenarios)
    findings = swarm.aggregate(analyses, profiles)
    out = Path(args.out)
    _write_json(out / "analyses.json", {"analyses": analyses})
    _write_json(out / "findings.json", {"findings": findings, "severity_counts": swarm.severity_counts(findings)})
    audience_doc = load_json(args.audience) if getattr(args, "audience", None) else None
    plan = None
    raw = load_json(args.profiles)
    if isinstance(raw, dict) and isinstance(raw.get("plan"), dict):
        plan = raw["plan"]
    (out / "report.md").write_text(report.render(findings, profiles, analyses, title=args.title, audience=audience_doc, plan=plan), encoding="utf-8")
    if args.bundle:
        bundle_doc = bundle.to_evidence_bundle(args.bundle_id or f"ergo-{out.name}", analyses, findings, profiles)
        _write_json(out / "bundle.json", bundle_doc)
    counts = swarm.severity_counts(findings)
    print(f"findings: {len(findings)} (P0 {counts['P0']}, P1 {counts['P1']}, P2 {counts['P2']}, P3 {counts['P3']}) -> {out}")
    if args.fail_on:
        limit = checks.SEVERITY_ORDER[args.fail_on]
        if any(checks.SEVERITY_ORDER.get(f["severity"], 3) <= limit for f in findings):
            return EXIT_FINDINGS
    return EXIT_OK


def cmd_heatmap(args: argparse.Namespace) -> int:
    from . import png
    from .devices import css_px_to_mm, device_for_snapshot
    from .hf import gaze, reach

    snapshot = load_json(args.snapshot)
    profiles = {p["profile_id"]: p for p in _load_profiles(args.profiles)}
    profile = profiles[args.profile]
    shot = Path(args.snapshot).parent / snapshot["screenshot"]["path"]
    image = png.to_rgb(png.read_png(shot))
    device = device_for_snapshot(snapshot["device"])
    vw, vh = snapshot["device"]["viewport_css"]
    cols, rows = max(1, int(vw // 8)), max(1, int(vh // 8))
    values: list[list[float | None]] = []
    if args.kind == "reach":
        geom = reach.geometry_for_device(device)
        grip = profile["attributes"]["grip"]
        thumb = float(profile["attributes"]["thumb_length_mm"])
        for r in range(rows):
            row = []
            for c in range(cols):
                x_mm = css_px_to_mm(device, (c + 0.5) * vw / cols, "x")
                y_mm = css_px_to_mm(device, (r + 0.5) * vh / rows, "y")
                row.append(reach.reach_score(x_mm, y_mm, geom, grip, thumb)["difficulty"] if grip in reach.SUPPORTED_GRIPS else None)
            values.append(row)
    else:
        snapshot["screenshot"]["resolved_path"] = str(shot)
        grid = analyze.conspicuity_for_snapshot(snapshot) or []
        form = getattr(device, "form_factor", "phone")
        gh = len(grid)
        gw = len(grid[0]) if gh else 0
        for r in range(rows):
            row = []
            for c in range(cols):
                xf, yf = (c + 0.5) / cols, (r + 0.5) / rows
                bottom_up = grid[min(gh - 1, int(yf * gh))][min(gw - 1, int(xf * gw))] if gh else 0.0
                row.append(0.5 * bottom_up + 0.5 * gaze.position_prior(xf, yf, "phone" if form in ("phone", "foldable") else form))
            values.append(row)
    overlay = png.heat_overlay(image, values, alpha=0.45)
    png.write_png(args.out, overlay)
    print(f"{args.kind} heatmap -> {args.out}")
    return EXIT_OK


def cmd_view(args: argparse.Namespace) -> int:
    from . import png
    from .view import profile_view

    snapshot = load_json(args.snapshot)
    profiles = {p["profile_id"]: p for p in _load_profiles(args.profiles)}
    shot = Path(args.snapshot).parent / snapshot["screenshot"]["path"]
    image, applied = profile_view(png.read_png(shot), profiles[args.profile], float(snapshot["device"].get("dpr") or 1.0))
    png.write_png(args.out, image)
    print(f"profile view -> {args.out} ({'; '.join(applied) or 'no transform'}) [illustrative, not a measurement]")
    return EXIT_OK


def cmd_bench(args: argparse.Namespace) -> int:
    key = load_json(args.key)
    findings_doc = load_json(args.findings)
    profiles = _load_profiles(args.profiles)
    result = bench.score(key, findings_doc["findings"], profiles)
    if args.out:
        _write_json(Path(args.out), result)
    print(json.dumps({k: v for k, v in result.items() if not isinstance(v, list)}, ensure_ascii=False, indent=2))
    return EXIT_OK


def cmd_catalog(args: argparse.Namespace) -> int:
    print(report.catalog_markdown())
    return EXIT_OK


def cmd_android_snapshot(args: argparse.Namespace) -> int:
    from .drivers import android

    xml = Path(args.xml).read_text(encoding="utf-8")
    snap = android.build_snapshot(xml, screenshot_path=args.png, device_id=args.device, density_dpi=args.density,
                                  run_id=args.run_id, step_index=args.step)
    _write_json(Path(args.out), snap)
    print(f"android snapshot ({len(snap['elements'])} elements) -> {args.out}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ergo_qa.py", description="Ergonomic persona-swarm UX QA (evidence-first, stdlib only).")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("devices", help="list the device catalog")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_devices)

    p = sub.add_parser("profiles", help="sample ergonomic persona profiles")
    p.add_argument("--count", type=int, required=True)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--devices", required=True, help="comma-separated device ids")
    p.add_argument("--strategy", default="stratified_coverage", choices=("stratified_coverage", "base_rate_sample"))
    p.add_argument("--orientation", choices=("portrait", "landscape"), help="default: each device's natural orientation")
    p.add_argument("--personas", help="optional JSON list of persona records (dataset, revision, record_id, age_band)")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_profiles)

    p = sub.add_parser("audience-check", help="validate an ergo-audience.v1 file (Stage 0 target-user research)")
    p.add_argument("audience")
    p.set_defaults(func=cmd_audience_check)

    p = sub.add_parser("personas", help="compose ergonomic profiles from an ergo-audience.v1 file")
    p.add_argument("--audience", required=True)
    p.add_argument("--budget", type=int, required=True, help="number of profiles to compose")
    p.add_argument("--floors", help=f"comma-separated inclusive floors (default: {','.join(audience.FLOOR_DEFAULTS)}; empty string for none)")
    p.add_argument("--plan", help="write a Korean Markdown table explaining why each persona exists")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_personas)

    p = sub.add_parser("scenario-stubs", help="write ergo-scenario.v1 skeletons for the audience's key tasks")
    p.add_argument("--audience", required=True)
    p.add_argument("--out", required=True, help="directory")
    p.set_defaults(func=cmd_scenario_stubs)

    for name, func, helptext in (("analyze", cmd_analyze, "analyze recorded runs"), ("swarm", cmd_swarm, "analyze runs and aggregate a swarm report")):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--runs", required=True, help="a run directory or a directory of run directories")
        p.add_argument("--profiles", required=True)
        p.add_argument("--scenario", action="append", help="scenario JSON file or directory (repeatable)")
        p.add_argument("--cross-profile", action="store_true", help="also evaluate each run under every profile with the same device")
        p.add_argument("--no-gaze", action="store_true", help="skip screenshot conspicuity (faster)")
        p.add_argument("--out", required=True)
        if name == "swarm":
            p.add_argument("--bundle", action="store_true", help="also write a ux-evidence-bundle.v1")
            p.add_argument("--bundle-id")
            p.add_argument("--title", default="인간공학 페르소나 스웜 QA 보고서")
            p.add_argument("--fail-on", choices=("P0", "P1", "P2", "P3"))
            p.add_argument("--audience", help="ergo-audience.v1 file the profiles were composed from (segment names in the report)")
        p.set_defaults(func=func)

    p = sub.add_parser("heatmap", help="render a reach or gaze-priority heatmap over a snapshot")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--profiles", required=True)
    p.add_argument("--profile", required=True)
    p.add_argument("--kind", choices=("reach", "gaze"), default="reach")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_heatmap)

    p = sub.add_parser("view", help="render an illustrative profile view (CVD, glare, blur) of a snapshot for persona agents")
    p.add_argument("--snapshot", required=True)
    p.add_argument("--profiles", required=True)
    p.add_argument("--profile", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_view)

    p = sub.add_parser("bench", help="score findings against a blind answer key")
    p.add_argument("--key", required=True)
    p.add_argument("--findings", required=True)
    p.add_argument("--profiles", required=True)
    p.add_argument("--out")
    p.set_defaults(func=cmd_bench)

    p = sub.add_parser("catalog", help="print the check catalog")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("android-snapshot", help="build a snapshot from a uiautomator dump and screenshot")
    p.add_argument("--xml", required=True)
    p.add_argument("--png", required=True)
    p.add_argument("--device", required=True)
    p.add_argument("--density", type=int, required=True)
    p.add_argument("--run-id", default="R-android")
    p.add_argument("--step", type=int, default=0)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_android_snapshot)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, KeyError, OSError, SnapshotError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
