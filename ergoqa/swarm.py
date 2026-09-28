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


def aggregate(analyses: Iterable[dict[str, Any]], profiles: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    profiles_by_id = {p["profile_id"]: p for p in profiles}
    groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for analysis in analyses:
        scenario_id = analysis.get("scenario_id") or "?"
        for obs in analysis["observations"]:
            key = (scenario_id, obs["check_id"], obs["element_key"])
            group = groups.setdefault(key, {"tested": set(), "triggered": set(), "failed": [], "runs": set()})
            group["tested"].add(obs["profile_id"])
            group["runs"].add(obs["run_id"])
            if not obs["passed"]:
                group["triggered"].add(obs["profile_id"])
                group["failed"].append(obs)
    findings: list[dict[str, Any]] = []
    for (scenario_id, check_id, element_key), group in sorted(groups.items()):
        if not group["failed"]:
            continue
        spec = checks.CATALOG[check_id]
        worst = min(group["failed"], key=lambda o: checks.SEVERITY_ORDER.get(o["severity"] or "P3", 3))
        tested = sorted(group["tested"])
        triggered = sorted(group["triggered"])
        untriggered = [profiles_by_id[p] for p in tested if p not in group["triggered"] and p in profiles_by_id]
        differential = _differential([profiles_by_id[p] for p in triggered if p in profiles_by_id], untriggered)
        findings.append({
            "check_id": check_id,
            "category": spec.category,
            "scenario_id": scenario_id,
            "element_key": element_key,
            "severity": worst["severity"],
            "basis": spec.basis,
            "epistemic_status": "observed" if spec.basis == "measured" else "inferred",
            "model": worst.get("model"),
            "triggered_profiles": triggered,
            "tested_profiles": tested,
            "coverage_label": f"{len(triggered)}/{len(tested)} simulated profiles (coverage, not prevalence)",
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
