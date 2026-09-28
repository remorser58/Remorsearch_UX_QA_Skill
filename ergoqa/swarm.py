"""Aggregate per-profile observations into swarm findings.

The swarm borrows MiroFish's structure (many persona agents -> shared record ->
report) but not its claims: counts are coverage over *simulated* profiles, never
a prevalence estimate, and the "differential condition" (which profile
attributes separate triggered from untriggered profiles) is computed, not
narrated by an LLM.
"""

from __future__ import annotations

from typing import Any, Iterable

from . import checks
from .profiles import _get_path

DIFFERENTIAL_ATTRIBUTES = (
    "handedness", "grip", "age_band", "device_id", "orientation",
    "vision.cvd", "vision.presbyopia", "motor.tremor", "context.mobility",
    "context.lighting", "cognition.familiarity", "hand_percentile",
)


def _differential(triggered: list[dict[str, Any]], untriggered: list[dict[str, Any]]) -> dict[str, Any]:
    """Attribute values shared by every triggered profile and by no untriggered one."""
    if not triggered or not untriggered:
        return {}
    out: dict[str, Any] = {}
    for attr in DIFFERENTIAL_ATTRIBUTES:
        values = {repr(_get_path(p["attributes"], attr)) for p in triggered}
        if len(values) != 1:
            continue
        value = _get_path(triggered[0]["attributes"], attr)
        if all(_get_path(p["attributes"], attr) != value for p in untriggered):
            out[attr] = value
    return out


def _segments(profile_ids: list[str], profiles_by_id: dict[str, dict[str, Any]]) -> list[str]:
    """Audience segments (ergo-audience.v1) whose composed profiles triggered the finding."""
    found = {((profiles_by_id.get(pid) or {}).get("audience_ref") or {}).get("segment_id") for pid in profile_ids}
    return sorted(s for s in found if s)


def _device_of(profile: dict[str, Any]) -> Any:
    from .devices import get_device, rotate

    attrs = profile.get("attributes", {})
    device = get_device(attrs.get("device_id"))
    if attrs.get("orientation") == "landscape" and device.orientation != "landscape":
        device = rotate(device, "landscape")
    return device


def aggregate(analyses: Iterable[dict[str, Any]], profiles: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    profiles_by_id = {p["profile_id"]: p for p in profiles}
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    evaluated_by_run: dict[str, list[str]] = {}
    devices: dict[str, Any] = {}
    for analysis in analyses:
        scenario_id = analysis.get("scenario_id") or "?"
        run_id = analysis.get("run_id")
        if run_id and analysis.get("profiles_evaluated"):
            evaluated_by_run.setdefault(run_id, [])
            evaluated_by_run[run_id] += [p for p in analysis["profiles_evaluated"] if p not in evaluated_by_run[run_id]]
        for obs in analysis["observations"]:
            # Group by the element's selector, not its current text: a countdown or score
            # whose text changes every snapshot is one element (cross-review 2026-09-28).
            key = (scenario_id, obs["check_id"], obs["element_key"].split("|", 1)[0])
            group = groups.setdefault(key, {"tested": set(), "triggered": set(), "failed": [], "runs": set()})
            group["tested"].add(obs["profile_id"])
            group["runs"].add(obs["run_id"])
            if not obs["passed"]:
                group["triggered"].add(obs["profile_id"])
                group["failed"].append(obs)
    findings: list[dict[str, Any]] = []
    for (scenario_id, check_id, _selector), group in sorted(groups.items()):
        if not group["failed"]:
            continue
        element_key = group["failed"][0]["element_key"]
        spec = checks.CATALOG[check_id]
        if check_id != "PJ-01":
            # Denominator: every evaluated profile the check applies to, not only the ones
            # that happened to emit an observation.
            for run_id in group["runs"]:
                for pid in evaluated_by_run.get(run_id, []):
                    profile = profiles_by_id.get(pid)
                    if profile is None:
                        continue
                    if pid not in devices:
                        devices[pid] = _device_of(profile)
                    if checks.applicable(check_id, profile, devices[pid]):
                        group["tested"].add(pid)
        worst = min(group["failed"], key=lambda o: checks.SEVERITY_ORDER.get(o["severity"] or "P3", 3))
        tested = sorted(group["tested"])
        triggered = sorted(group["triggered"])
        untriggered = [profiles_by_id[p] for p in tested if p not in group["triggered"] and p in profiles_by_id]
        differential = _differential([profiles_by_id[p] for p in triggered if p in profiles_by_id], untriggered)
        findings.append({
            "check_id": check_id,
            "tier": checks.tier(check_id, worst.get("measurement")),
            "category": spec.category,
            "scenario_id": scenario_id,
            "element_key": element_key,
            "severity": worst["severity"],
            "basis": spec.basis,
            "epistemic_status": "observed" if spec.basis == "measured" else "inferred",
            "model": worst.get("model"),
            "triggered_profiles": triggered,
            "tested_profiles": tested,
            "coverage_label": ("profile-independent (measured on the screen; coverage, not prevalence)" if check_id in checks.PROFILE_INVARIANT_CHECKS
                               else f"{len(triggered)}/{len(tested)} simulated profiles (coverage, not prevalence)"),
            "profile_specific": differential,
            "segments_affected": _segments(triggered, profiles_by_id),
            "observation_ids": [o["id"] for o in group["failed"]],
            "run_ids": sorted(group["runs"]),
            "selectors": sorted({sel for o in group["failed"] for sel in o.get("selectors", [])}),
            "context_selectors": sorted({sel for o in group["failed"] for sel in o.get("context_selectors", [])}),
            "measurement": worst["measurement"],
            "title_ko": spec.title_ko,
            "summary_ko": worst["message_ko"],
            "fix_layer": spec.fix_layer,
            "recommendation_ko": spec.recommendation_ko,
            "refs": list(spec.refs),
        })
    findings.sort(key=lambda f: (checks.SEVERITY_ORDER.get(f["severity"] or "P3", 3), f["category"], f["scenario_id"], f["element_key"]))
    for index, finding in enumerate(findings, 1):
        finding["id"] = f"EF-{index:03d}"
    return findings


def severity_counts(findings: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    for finding in findings:
        if finding.get("severity") in counts:
            counts[finding["severity"]] += 1
    return counts


def _differential_key(finding: dict[str, Any]) -> str:
    diff = finding.get("profile_specific") or {}
    return ";".join(f"{k}={diff[k]}" for k in sorted(diff)) or "all tested profiles"


def units(findings: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group findings into problem units: one (scenario, check, differential condition).

    A systemic problem (small body text across a page for presbyopic profiles, five
    targets under 24 px) is one unit with its elements as instances, as accessibility
    scanners report one rule with many nodes. Counting units instead of findings is
    the standard merge step before counting problems (UEM-02).
    """
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for f in findings:
        groups.setdefault((f["scenario_id"], f["check_id"], _differential_key(f)), []).append(f)
    out = []
    for (scenario_id, check_id, diff), members in groups.items():
        worst = min(members, key=lambda f: checks.SEVERITY_ORDER.get(f["severity"] or "P3", 3))
        triggered = sorted({p for f in members for p in f["triggered_profiles"]})
        tested = sorted({p for f in members for p in f["tested_profiles"]})
        out.append({
            "scenario_id": scenario_id,
            "check_id": check_id,
            "tier": worst.get("tier", checks.tier(check_id)),
            "category": worst["category"],
            "basis": worst["basis"],
            "severity": worst["severity"],
            "condition": diff,
            "profile_specific": worst.get("profile_specific") or {},
            "instances": [f["id"] for f in members],
            "elements": [f["element_key"] for f in members],
            "triggered_profiles": triggered,
            "tested_profiles": tested,
            "segments_affected": sorted({s for f in members for s in f.get("segments_affected", [])}),
            "title_ko": worst["title_ko"],
        })
    out.sort(key=lambda u: (checks.SEVERITY_ORDER.get(u["severity"] or "P3", 3), u["category"], u["scenario_id"], u["check_id"]))
    for i, u in enumerate(out, 1):
        u["id"] = f"EU-{i:03d}"
    return out
