"""Pre-registered evaluation of a v2 benchmark suite (heldout-2 layout).

A v2 suite has one folder per concern and one answer key per product:

    <suite>/products/<slug>/brief.md      product brief (Stage 0 input)
    <suite>/site/<slug>/...               pages (defect and clean variants)
    <suite>/scenarios/*.json              ergo-scenario.v1
    <suite>/keys/<slug>.json              defects, decoys, clean controls (spec 12.1)
    <suite>/audience/<slug>.audience.json Stage-0 output (written blind to defects)

Configurations (docs/validation/experiments/heldout-2-preregistration.md):

- C1 measured-only: measured checks, default persona per device group;
- C2 single persona: all checks, default persona;
- C3 stratified: ``sample_profiles`` stratified coverage, 14 per touch device and
  7 per pointer device;
- C4 audience-composed: ``audience.compose`` per product at each budget;
- C5 random: ``sample_profiles(strategy="base_rate_sample")`` at the same budgets,
  20 seeds.

Every scenario is recorded once per device group that any configuration needs
(real Chromium input, the default persona as recorder), then analysed offline
under the union of all configurations' profiles, and each configuration is
scored on the same recordings.

    python3 skills/remorsearch-ux-qa/scripts/ergo_eval.py record  --suite benchmarks/heldout-2 --out .ergo-bench/h2
    python3 skills/remorsearch-ux-qa/scripts/ergo_eval.py analyse --suite benchmarks/heldout-2 --out .ergo-bench/h2
    python3 skills/remorsearch-ux-qa/scripts/ergo_eval.py score   --suite benchmarks/heldout-2 --out .ergo-bench/h2

Custody: ``score`` prints and writes aggregate metrics only (``aggregate.json``).
Per-defect results go to ``<out>/sealed/`` and are opened only after the
aggregate report is committed. ``--open`` also prints per-defect misses; use it
for development suites only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import random
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]  # skill folder
REPO = ROOT.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ergoqa import analyze, audience, bench, checks, swarm  # noqa: E402
from ergoqa.devices import get_device  # noqa: E402
from ergoqa.profiles import sample_profiles  # noqa: E402

from ergo_bench import default_profile, provenance, static_server  # noqa: E402

BUDGETS = (6, 10, 14)
C5_SEEDS = 20
C3_TOUCH, C3_POINTER = 14, 7
BOOTSTRAP = 2000
LEAN_PASSED = ("check_id", "element_key", "profile_id", "passed", "run_id")


# ---------------------------------------------------------------------------
# Suite


def load_suite(suite: Path) -> dict[str, Any]:
    scenarios, paths = {}, {}
    for f in sorted((suite / "scenarios").glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        scenarios[doc["scenario_id"]] = doc
        paths[doc["scenario_id"]] = f
    keys = {}
    for f in sorted((suite / "keys").glob("*.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        keys[doc.get("product") or f.stem] = doc
    product_of: dict[str, str] = {}
    for slug, key in keys.items():
        for item in key.get("defects", []) + key.get("decoys", []) + key.get("clean_controls", []):
            product_of[item["scenario_id"]] = slug
    for sid in scenarios:
        if sid not in product_of:
            m = re.match(r"SC-[a-z0-9]+-([a-z0-9]+)-", sid)
            product_of[sid] = m.group(1) if m else sid
    audiences = {}
    for f in sorted((suite / "audience").glob("*.audience.json")) if (suite / "audience").is_dir() else []:
        audiences[f.name.split(".")[0]] = json.loads(f.read_text(encoding="utf-8"))
    merged = {"suite": suite.name, "defects": [], "decoys": [], "clean_controls": []}
    for key in keys.values():
        for part in ("defects", "decoys", "clean_controls"):
            merged[part].extend(key.get(part, []))
    return {"suite": suite, "scenarios": scenarios, "paths": paths, "keys": keys, "key": merged, "product_of": product_of, "audiences": audiences}


def _group(profile: dict[str, Any]) -> str:
    a = profile["attributes"]
    return f"{a['device_id']}|{a['orientation']}"


def _scenario_groups(scenario: dict[str, Any]) -> list[str]:
    out = []
    for device_id in scenario["device_ids"]:
        out.append(f"{device_id}|{scenario.get('orientation') or get_device(device_id).orientation}")
    return out


def _canonical(profile: dict[str, Any]) -> str:
    """Profiles with identical attributes are one profile (C5 seeds often repeat draws)."""
    digest = hashlib.sha1(json.dumps(profile["attributes"], sort_keys=True).encode()).hexdigest()[:10]
    a = profile["attributes"]
    return f"EV-{digest}@{a['device_id']}-{a['orientation'][0]}"


def _base(gk: str) -> dict[str, Any]:
    device_id, orientation = gk.split("|")
    p = default_profile(device_id, orientation)
    p["profile_id"] = f"EP-BASE-{device_id}-{orientation[0]}"
    return p


def configurations(data: dict[str, Any]) -> tuple[dict[str, set[str]], dict[str, dict[str, Any]], dict[str, set[str]], list[str]]:
    """Profile sets per configuration, the profile registry, device groups per scenario, notes."""
    registry: dict[str, dict[str, Any]] = {}
    configs: dict[str, set[str]] = {}
    notes: list[str] = []

    def add(config: str, profile: dict[str, Any], canonical: bool = True) -> None:
        pid = _canonical(profile) if canonical else profile["profile_id"]
        if pid not in registry:
            keep = dict(profile)
            keep["profile_id"] = pid
            registry[pid] = keep
        configs.setdefault(config, set()).add(pid)

    groups_of: dict[str, set[str]] = {sid: set(_scenario_groups(sc)) for sid, sc in data["scenarios"].items()}
    products: dict[str, list[str]] = {}
    for sid, slug in data["product_of"].items():
        if sid in data["scenarios"]:
            products.setdefault(slug, []).append(sid)
    for slug, sids in sorted(products.items()):
        product_groups = sorted({g for sid in sids for g in groups_of[sid]})
        for gk in product_groups:
            base = _base(gk)
            add("C1", base, canonical=False)
            add("C2", base, canonical=False)
            device_id, orientation = gk.split("|")
            count = C3_TOUCH if get_device(device_id).input == "touch" else C3_POINTER
            for p in sample_profiles(count, 11, [device_id], orientation=orientation):
                add("C3", p)
        doc = data["audiences"].get(slug)
        if doc is None:
            notes.append(f"{slug}: no audience file, C4 not run")
        for budget in BUDGETS:
            if doc is not None:
                plan = audience.compose(doc, budget)
                for p in plan["profiles"]:
                    add(f"C4@{budget}", p)
                    for sid in sids:
                        groups_of[sid].add(_group(p))
            devices = sorted({g.split("|")[0] for g in product_groups})
            for seed in range(C5_SEEDS):
                for p in sample_profiles(budget, 1000 + seed, devices, strategy="base_rate_sample"):
                    add(f"C5@{budget}#{seed}", p)
                    for sid in sids:
                        groups_of[sid].add(_group(p))
    return configs, registry, groups_of, notes


# ---------------------------------------------------------------------------
# Record and analyse


def record(data: dict[str, Any], out: Path) -> None:
    _, _, groups_of, notes = configurations(data)
    for n in notes:
        print(f"note: {n}", flush=True)
    runs_dir = out / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    (out / "profiles").mkdir(exist_ok=True)
    log = []
    with static_server(data["suite"].parent) as base_url:
        for sid, sc in sorted(data["scenarios"].items()):
            for gk in sorted(groups_of[sid]):
                device_id, orientation = gk.split("|")
                recorder = _base(gk)
                run_id = f"R-{sid}-{device_id}-{orientation[0]}"
                if (runs_dir / run_id / "run.json").is_file():
                    continue
                ppath = out / "profiles" / f"{recorder['profile_id']}.json"
                ppath.write_text(json.dumps(recorder, ensure_ascii=False), encoding="utf-8")
                cmd = ["node", str(ROOT / "drivers/web/ergo_drive.mjs"), "run", "--scenario", str(data["paths"][sid]), "--profile", str(ppath),
                       "--out", str(runs_dir), "--run-id", run_id, "--base", base_url, "--continue-on-error"]
                if sc.get("surface", {}).get("kind") == "game":
                    cmd += ["--flash-sample-ms", "1500"]
                started = time.time()
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
                entry = {"run_id": run_id, "scenario_id": sid, "group": gk, "exit": proc.returncode, "seconds": round(time.time() - started, 1)}
                log.append(entry)
                print(f"recorded {run_id}: exit {proc.returncode} in {entry['seconds']}s", flush=True)
    previous = json.loads((out / "record-log.json").read_text(encoding="utf-8")) if (out / "record-log.json").is_file() else []
    (out / "record-log.json").write_text(json.dumps(previous + log, indent=1), encoding="utf-8")


def _lean(obs: dict[str, Any]) -> dict[str, Any]:
    if obs["passed"]:
        return {k: obs[k] for k in LEAN_PASSED}
    keep = dict(obs)
    keep.pop("refs", None)
    keep.pop("message_en", None)
    return keep


def analyse_all(data: dict[str, Any], out: Path) -> dict[str, Any]:
    configs, registry, _, _ = configurations(data)
    by_group: dict[str, list[dict[str, Any]]] = {}
    for p in registry.values():
        by_group.setdefault(_group(p), []).append(p)
    analyses, health = [], []
    started = time.time()
    for run_dir in sorted(p for p in (out / "runs").iterdir() if (p / "run.json").is_file()):
        run_doc = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        dev = run_doc.get("device") or {}
        gk = f"{dev.get('id')}|{dev.get('orientation')}"
        # The recorder is the default persona; groups that only C4/C5 need are not in
        # C1/C2, so the recorder is evaluated but belongs to no configuration there.
        own = registry.get(run_doc["profile_id"]) or {**_base(gk), "profile_id": run_doc["profile_id"]}
        evaluated = [own] + [p for p in by_group.get(gk, []) if p["profile_id"] != own["profile_id"]]
        result = analyze.analyze_run(run_dir, evaluated, data["scenarios"].get(run_doc["scenario_id"]), cross_profile=True)
        health.append({"run_id": result.get("run_id"), "status": result.get("health")})
        result["observations"] = [_lean(o) for o in result["observations"]]
        result.pop("coverage", None)
        analyses.append(result)
        print(f"  {run_dir.name}: {len(result['profiles_evaluated'])} profiles, {len(result['observations'])} obs, {time.time() - started:.0f}s", flush=True)
    cache = {"analyses": analyses, "registry": registry, "configs": {k: sorted(v) for k, v in configs.items()}, "health": health,
             "provenance": provenance()}
    with (out / "analysis-cache.pickle").open("wb") as fh:
        pickle.dump(cache, fh)
    return cache


# ---------------------------------------------------------------------------
# Scoring


def _findings(cache: dict[str, Any], profile_ids: set[str], basis: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    analyses = []
    for a in cache["analyses"]:
        obs = [o for o in a["observations"] if o["profile_id"] in profile_ids]
        if basis is not None:
            obs = [o for o in obs if checks.CATALOG[o["check_id"]].basis == basis]
        evaluated = [pid for pid in a.get("profiles_evaluated", []) if pid in profile_ids]
        if evaluated:
            analyses.append({"scenario_id": a["scenario_id"], "run_id": a.get("run_id"), "profiles_evaluated": evaluated, "observations": obs})
    used = [cache["registry"][pid] for pid in sorted(profile_ids)]
    return swarm.aggregate(analyses, used), used


def score_config(cache: dict[str, Any], key: dict[str, Any], config: str) -> dict[str, Any]:
    ids = set(cache["configs"][config])
    findings, used = _findings(cache, ids, basis="measured" if config == "C1" else None)
    return bench.score(key, findings, used, exact_viewport=True, include_hypotheses=False)


def _rate(k: int, n: int) -> dict[str, Any]:
    lo, hi = bench.wilson(k, n) if n else (None, None)
    return {"k": k, "n": n, "rate": round(k / n, 3) if n else None, "ci95": [lo, hi]}


def breakdown(per_defect: list[dict[str, Any]], defects: list[dict[str, Any]]) -> dict[str, Any]:
    meta = {d["id"]: d for d in defects}
    out: dict[str, Any] = {}
    for field in ("category", "detectable_by", "audience_relevance"):
        groups: dict[str, list[bool]] = {}
        for d in per_defect:
            value = meta[d["id"]].get(field)
            for v in value if isinstance(value, list) else [value]:
                groups.setdefault(str(v), []).append(d["detected_strict"])
        out[field] = {g: _rate(sum(v), len(v)) for g, v in sorted(groups.items())}
    return out


def aggregate(sc: dict[str, Any], key: dict[str, Any]) -> dict[str, Any]:
    clean_n = len({c["scenario_id"] for c in key.get("clean_controls", [])}) or 1
    by_sev = sc["clean_control_units_by_severity"]
    detected = sum(d["detected_strict"] for d in sc["per_defect"])
    return {
        "recall_strict": _rate(detected, len(sc["per_defect"])),
        "recall_strict_by_operating_point": sc["recall_strict_by_operating_point"],
        "recall_strict_unconditioned": sc["recall_strict_unconditioned"],
        "condition_identified": sc["condition_identified"],
        "recall_condition_attributed": sc["recall_condition_attributed"],
        "conditioned_defects": sc["conditioned_defects"],
        "recall_lenient": sc["recall_lenient"],
        "severity_agreement": sc["severity_agreement"],
        "by": breakdown(sc["per_defect"], key["defects"]),
        "units": sc["units"],
        "matched_units": sc["matched_units"],
        "validity_lb_units": sc["validity_lb_units"],
        "precision_labelled_subset_units": sc["precision_labelled_subset_units"],
        "clean_control_units": sc["clean_control_units"],
        "clean_control_units_by_severity": by_sev,
        "clean_units_per_clean_scenario": {
            "p0_p1": round((by_sev["P0"] + by_sev["P1"]) / clean_n, 2),
            "p0_p2": round((by_sev["P0"] + by_sev["P1"] + by_sev["P2"]) / clean_n, 2),
            "all": round(sc["clean_control_units"] / clean_n, 2),
        },
        "decoy_units": sc["decoy_units"],
        "decoys_flagged": sc["decoys_flagged"],
        "unlabeled_units": sc["unlabeled_units"],
        "hypotheses_excluded": sc["hypotheses_excluded"],
    }


def _paired_diff(a: dict[str, float], b: dict[str, float], ids: list[str], seed: int = 7) -> dict[str, Any]:
    """Mean of a[d] - b[d] over defects with a paired bootstrap 95 % interval (resampling defects)."""
    if not ids:
        return {"diff": None, "ci95": [None, None], "n": 0}
    diffs = [a[i] - b[i] for i in ids]
    rng = random.Random(seed)
    boots = sorted(statistics.fmean(rng.choice(diffs) for _ in diffs) for _ in range(BOOTSTRAP))
    return {"diff": round(statistics.fmean(diffs), 3), "ci95": [round(boots[int(0.025 * BOOTSTRAP)], 3), round(boots[int(0.975 * BOOTSTRAP) - 1], 3)], "n": len(ids)}


def _verdict(point: float | None, ci: list[float | None], threshold: float) -> str:
    """Pre-registered rule: inconclusive when the interval overlaps the threshold."""
    if point is None or ci[0] is None:
        return "not_run"
    if ci[0] >= threshold:
        return "pass"
    if ci[1] < threshold:
        return "fail"
    return "inconclusive"


def hypotheses(scores: dict[str, dict[str, Any]], key: dict[str, Any]) -> dict[str, Any]:
    defects = key["defects"]
    ids = [d["id"] for d in defects]
    primary = [d["id"] for d in defects if d.get("audience_relevance") == "primary"]
    unconditioned = [d["id"] for d in defects if not d.get("profile_condition")]
    hit = {c: {d["id"]: float(d["detected_strict"]) for d in s["per_defect"]} for c, s in scores.items()}
    out: dict[str, Any] = {}

    semantic = [d["id"] for d in defects if d.get("category") in ("semantics", "layout")]
    out["H1"] = {c: _rate(int(sum(hit[c][i] for i in semantic)), len(semantic)) for c in ("C3", "C4@14") if c in hit}
    out["H1"]["verdict"] = "reported"

    if "C4@10" in hit:
        c5 = [c for c in hit if c.startswith("C5@10#")]
        c5_mean = {i: statistics.fmean(hit[c][i] for c in c5) for i in ids}
        prim = _paired_diff(hit["C4@10"], c5_mean, primary)
        overall = _paired_diff(hit["C4@10"], c5_mean, ids)
        v1 = _verdict(prim["diff"], prim["ci95"], 0.10)
        v2 = _verdict(overall["diff"], overall["ci95"], 0.0)
        verdict = "pass" if v1 == v2 == "pass" else ("fail" if "fail" in (v1, v2) else "inconclusive")
        out["H2"] = {"primary_minus_c5_mean": prim, "overall_minus_c5_mean": overall, "parts": [v1, v2], "verdict": verdict}
    else:
        out["H2"] = {"verdict": "not_run"}

    if "C4@14" in hit:
        d = _paired_diff(hit["C4@14"], hit["C3"], ids)
        out["H3"] = {"c4_14_minus_c3": d, "verdict": _verdict(d["diff"], d["ci95"], -0.05)}
        by_sev = scores["C4@14"]["clean_control_units_by_severity"]
        clean_n = len({c["scenario_id"] for c in key.get("clean_controls", [])}) or 1
        p01 = (by_sev["P0"] + by_sev["P1"]) / clean_n
        p02 = (by_sev["P0"] + by_sev["P1"] + by_sev["P2"]) / clean_n
        out["H4"] = {"p0_p1_per_clean_scenario": round(p01, 2), "p0_p2_per_clean_scenario": round(p02, 2),
                     "verdict": "pass" if p01 <= 1 and p02 <= 5 else "fail"}
    else:
        out["H3"] = out["H4"] = {"verdict": "not_run"}

    h5 = {}
    for c in ("C3", "C4@14"):
        if c not in scores:
            continue
        cond = [d for d in scores[c]["per_defect"] if d["profile_condition"]]
        k = sum(1 for d in cond if d["differential_matches_condition"])
        r = _rate(k, len(cond))
        r["verdict"] = _verdict(r["rate"], r["ci95"], 0.5)
        h5[c] = r
    out["H5"] = h5
    out["H5"]["verdict"] = ("pass" if all(v["verdict"] == "pass" for v in h5.values()) else
                           "fail" if any(v["verdict"] == "fail" for v in h5.values()) else "inconclusive") if h5 else "not_run"

    d7 = _paired_diff(hit["C3"], hit["C2"], unconditioned)
    out["H7"] = {"c3_minus_c2_unconditioned": d7, "verdict": _verdict(d7["diff"], d7["ci95"], 0.0)}
    out["H6"] = {"verdict": "scored separately (persona agents, C6)"}
    return out


def score_all(data: dict[str, Any], out: Path, show_open: bool) -> dict[str, Any]:
    with (out / "analysis-cache.pickle").open("rb") as fh:
        cache = pickle.load(fh)
    key = data["key"]
    scores = {c: score_config(cache, key, c) for c in sorted(cache["configs"])}
    agg: dict[str, Any] = {"suite": data["suite"].name, "defects": len(key["defects"]), "decoys": len(key["decoys"]),
                           "clean_scenarios": len({c["scenario_id"] for c in key.get("clean_controls", [])}),
                           "products": sorted(data["keys"]), "provenance_analysis": cache["provenance"], "provenance_score": provenance(),
                           "run_health": {s: sum(1 for h in cache["health"] if h["status"] == s) for s in {h["status"] for h in cache["health"]}},
                           "configs": {}}
    for c, sc in scores.items():
        if c.startswith("C5@"):
            continue
        agg["configs"][c] = aggregate(sc, key)
    for budget in BUDGETS:
        seeds = [scores[c] for c in scores if c.startswith(f"C5@{budget}#")]
        if not seeds:
            continue
        rec = [s["recall_strict"] for s in seeds]
        clean = [s["clean_control_units"] for s in seeds]
        agg["configs"][f"C5@{budget}"] = {"seeds": len(seeds), "recall_strict_mean": round(statistics.fmean(rec), 3),
                                          "recall_strict_range95": [round(sorted(rec)[0], 3), round(sorted(rec)[-1], 3)],
                                          "clean_control_units_mean": round(statistics.fmean(clean), 2)}
    agg["hypotheses"] = hypotheses(scores, key)
    (out / "aggregate.json").write_text(json.dumps(agg, ensure_ascii=False, indent=1), encoding="utf-8")
    sealed = out / "sealed"
    sealed.mkdir(exist_ok=True)
    for c, sc in scores.items():
        (sealed / f"score-{c.replace('#', '-s').replace('@', '-b')}.json").write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding="utf-8")
    if show_open:
        for c in ("C3", "C4@14"):
            if c in scores:
                missed = [d["id"] for d in scores[c]["per_defect"] if not d["detected_strict"]]
                agg.setdefault("open_missed", {})[c] = missed
    return agg


def _listify(value: Any) -> list[Any]:
    return value if isinstance(value, list) else [value]


def score_agents(data: dict[str, Any], agent_dir: Path) -> dict[str, Any]:
    """C6: persona-agent runs (serve mode) scored on ``agent_judgment`` defects.

    ``agent_dir`` holds ``runs/<run_id>/run.json`` and ``profiles.json`` (the composed
    operator profiles). Each run is analysed under its own profile only. PJ-01 units
    are hypotheses unless runs on another model family or input channel noted the
    same anchor (computed in swarm.aggregate). A judgment note has no category, so
    matching is lenient (scenario, selector, condition); strict matching is reported
    too. Aggregates only.
    """
    profiles = json.loads((agent_dir / "profiles.json").read_text(encoding="utf-8"))["profiles"]
    by_id = {p["profile_id"]: p for p in profiles}
    analyses, runs = [], []
    for run_dir in sorted(p for p in (agent_dir / "runs").iterdir() if (p / "run.json").is_file()):
        run_doc = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        own = by_id.get(run_doc["profile_id"])
        if own is None:
            continue
        result = analyze.analyze_run(run_dir, [own], data["scenarios"].get(run_doc["scenario_id"]), cross_profile=False)
        result["observations"] = [_lean(o) for o in result["observations"]]
        analyses.append(result)
        notes = run_doc.get("persona_notes") or []
        runs.append({"success": run_doc.get("success"), "steps": len(run_doc.get("steps") or []), "health": result.get("health"),
                     "channel": (run_doc.get("agent") or {}).get("input_channel"),
                     "notes": len(notes), "confusion": sum(1 for n in notes if n.get("confusion")),
                     "failure_class": {c: sum(1 for n in notes if n.get("confusion") and n.get("failure_class") == c)
                                       for c in ("ux_issue", "agent_limitation", "environment", "unknown")}})
    findings = swarm.aggregate(analyses, profiles)
    key = data["key"]
    judgment = [d for d in key["defects"] if "agent_judgment" in _listify(d.get("detectable_by"))]
    subkey = {**key, "defects": judgment}
    pj = [f for f in findings if f["check_id"] == "PJ-01"]
    out: dict[str, Any] = {"runs": len(runs), "agent_judgment_defects": len(judgment),
                           "task_success_rate": round(sum(1 for r in runs if r["success"]) / len(runs), 3) if runs else None,
                           "steps_mean": round(statistics.fmean(r["steps"] for r in runs), 1) if runs else None,
                           "confusion_notes": sum(r["confusion"] for r in runs),
                           "confusion_by_class": {c: sum(r["failure_class"][c] for r in runs) for c in ("ux_issue", "agent_limitation", "environment", "unknown")},
                           "run_health": {s: sum(1 for r in runs if r["health"] == s) for s in {r["health"] for r in runs}}}
    for name, fs, include in (("pj_corroborated", pj, False), ("pj_including_hypotheses", pj, True), ("all_checks_on_agent_runs", findings, False)):
        sc = bench.score(subkey, fs, profiles, exact_viewport=True, include_hypotheses=include)
        lenient = sum(d["detected_lenient"] for d in sc["per_defect"])
        strict = sum(d["detected_strict"] for d in sc["per_defect"])
        clean_n = len({c["scenario_id"] for c in key.get("clean_controls", [])}) or 1
        out[name] = {"recall_lenient": _rate(lenient, len(judgment)), "recall_strict": _rate(strict, len(judgment)),
                     "units": sc["units"], "clean_control_units": sc["clean_control_units"],
                     "clean_units_per_clean_scenario": round(sc["clean_control_units"] / clean_n, 2), "unlabeled_units": sc["unlabeled_units"]}
    hyp = out["pj_corroborated"]["recall_lenient"]
    out["H6"] = {"threshold": 0.30, "verdict": _verdict(hyp["rate"], hyp["ci95"], 0.30),
                 "note": "the clean-scenario part (<= 1 invalid corroborated PJ-01 unit per clean scenario) needs round-2 adjudication"}
    sealed = agent_dir / "sealed"
    sealed.mkdir(exist_ok=True)
    (sealed / "c6-findings.json").write_text(json.dumps({"findings": findings}, ensure_ascii=False, indent=1), encoding="utf-8")
    (agent_dir / "aggregate-c6.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def main() -> int:
    global C5_SEEDS
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("record", "analyse", "score", "plan", "score-agents"):
        p = sub.add_parser(name)
        p.add_argument("--suite", required=True, type=Path)
        p.add_argument("--out", required=True, type=Path, help="work folder (score-agents: the agent-run folder with runs/ and profiles.json)")
        p.add_argument("--c5-seeds", type=int, default=C5_SEEDS, help="pre-registered: 20; fewer only for pipeline tests")
        if name == "score":
            p.add_argument("--open", action="store_true", help="also list per-defect misses (development suites only)")
    args = parser.parse_args()
    C5_SEEDS = args.c5_seeds
    data = load_suite(args.suite.resolve())
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.cmd == "plan":
        configs, registry, groups_of, notes = configurations(data)
        print(json.dumps({"configs": {c: len(v) for c, v in configs.items() if not c.startswith("C5@") or c.endswith("#0")},
                          "distinct_profiles": len(registry), "recordings": sum(len(g) for g in groups_of.values()), "notes": notes}, indent=1))
    elif args.cmd == "record":
        record(data, out)
    elif args.cmd == "analyse":
        analyse_all(data, out)
    elif args.cmd == "score-agents":
        print(json.dumps(score_agents(data, out), ensure_ascii=False, indent=1))
    else:
        agg = score_all(data, out, args.open)
        print(json.dumps({k: v for k, v in agg.items() if k not in ("provenance_analysis", "provenance_score")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
