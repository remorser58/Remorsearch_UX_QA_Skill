"""Score swarm findings against a blind benchmark answer key (spec section 12).

Matching is by scenario, category, element selector and profile condition; check
IDs are deliberately not part of the key. Findings on clean controls or decoys
are false-positive candidates. Unmatched findings in defect variants are
"unlabeled" and need manual adjudication (they may be real, unseeded issues).
"""

from __future__ import annotations

import math
from typing import Any, Iterable

from .profiles import flatten_condition, matches_condition

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


PAGE_LEVEL_SELECTORS = ("viewport", "body", "html", ":root")


def _selector_matches(finding: dict[str, Any], selector: str, exact_viewport: bool = False) -> bool:
    selector = (selector or "").strip()
    if not selector:
        return False
    candidates = list(finding.get("selectors") or [])
    candidates.append(finding.get("element_key", "").split("|", 1)[0])
    if finding.get("element_key", "").startswith("viewport|"):
        # A page-level finding (frame-sampled flash) has no element. Legacy scoring let it
        # match any selector; exact scoring matches it only to page-level keys (UEM-10).
        return selector in PAGE_LEVEL_SELECTORS if exact_viewport else True
    if selector in (finding.get("context_selectors") or []):
        return True  # the key names the container (toolbar, chip row) of the flagged element
    if selector.endswith("-") and selector.startswith("#"):
        # Answer-key convention: an id prefix ("#opt-") names a family of elements.
        return any(c.startswith(selector) for c in candidates if c)
    for candidate in candidates:
        if not candidate:
            continue
        if candidate == selector or candidate.endswith(selector) or selector.endswith(candidate) and candidate.startswith("#"):
            return True
        if selector in candidate.split() or selector in candidate.split(">"):
            return True
    return False


def _profile_ok(finding: dict[str, Any], condition: dict[str, Any], profiles_by_id: dict[str, dict[str, Any]]) -> bool:
    if not condition:
        return True
    return any(matches_condition(profiles_by_id[p], condition) for p in finding["triggered_profiles"] if p in profiles_by_id)


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if n == 0:
        return [0.0, 0.0]
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)]


def score(answer_key: dict[str, Any], findings: Iterable[dict[str, Any]], profiles: Iterable[dict[str, Any]],
          exact_viewport: bool = False, include_hypotheses: bool = False) -> dict[str, Any]:
    findings = list(findings)
    hypotheses = [f for f in findings if f.get("tier") == "hypothesis"]
    if not include_hypotheses:
        # Hypotheses are listed for review, not reported as defects: they neither count as
        # detections nor as false alarms.
        findings = [f for f in findings if f.get("tier") != "hypothesis"]
    profiles_by_id = {p["profile_id"]: p for p in profiles}
    defects = answer_key.get("defects", [])
    decoys = answer_key.get("decoys", [])
    clean_ids = {c["scenario_id"] for c in answer_key.get("clean_controls", [])}
    defect_scenarios = {d["scenario_id"] for d in defects}
    matched_finding_ids: set[str] = set()
    per_defect = []
    for d in defects:
        in_scenario = [f for f in findings if f["scenario_id"] == d["scenario_id"] and _selector_matches(f, d.get("element_selector", ""), exact_viewport)]
        strict = [f for f in in_scenario if f["category"] == d["category"] and _profile_ok(f, d.get("profile_condition") or {}, profiles_by_id)]
        lenient = [f for f in in_scenario if _profile_ok(f, d.get("profile_condition") or {}, profiles_by_id)]
        best = min(strict, key=lambda f: SEVERITY_ORDER.get(f["severity"], 3)) if strict else None
        severity_ok = bool(best) and SEVERITY_ORDER.get(best["severity"], 3) <= SEVERITY_ORDER.get(d.get("severity_min", "P3"), 3)
        specific_ok = None
        if best and d.get("profile_condition"):
            specific_ok = all(best["profile_specific"].get(k) == v for k, v in flatten_condition(d["profile_condition"]).items())
        for f in strict or lenient:
            matched_finding_ids.add(f["id"])
        per_defect.append({
            "id": d["id"],
            "scenario_id": d["scenario_id"],
            "category": d["category"],
            "selector": d.get("element_selector"),
            "profile_condition": d.get("profile_condition") or {},
            "detected_strict": bool(strict),
            "detected_lenient": bool(lenient),
            "severity_expected_min": d.get("severity_min"),
            "severity_found": best["severity"] if best else None,
            "severity_ok": severity_ok,
            "differential_matches_condition": specific_ok,
            "matched_findings": [f["id"] for f in (strict or lenient)],
            "matched_checks": sorted({f["check_id"] for f in (strict or lenient)}),
        })
    decoy_hits = []
    for n in decoys:
        hits = [f for f in findings if f["scenario_id"] == n["scenario_id"] and f["category"] == n.get("category") and _selector_matches(f, n.get("element_selector", ""), exact_viewport) and not f["element_key"].startswith("viewport|")]
        decoy_hits.append({"id": n["id"], "hit": bool(hits), "findings": [f["id"] for f in hits], "checks": sorted({f["check_id"] for f in hits})})
    clean_findings = [f for f in findings if f["scenario_id"] in clean_ids]
    unlabeled = [f for f in findings if f["scenario_id"] in defect_scenarios and f["id"] not in matched_finding_ids]
    n = len(defects) or 1
    tp_findings = len(matched_finding_ids)
    fp_findings = sum(len(h["findings"]) for h in decoy_hits) + len(clean_findings)
    # Unit-level validity (Hartson et al. 2001): count problem units, not element findings.
    from .swarm import units as make_units

    unit_list = make_units(findings)
    unit_of = {fid: u["id"] for u in unit_list for fid in u["instances"]}
    strict_ids = {fid for d in per_defect if d["detected_strict"] for fid in d["matched_findings"]}
    matched_units = {unit_of[f] for f in strict_ids if f in unit_of}
    clean_units = {u["id"] for u in unit_list if u["scenario_id"] in clean_ids}
    decoy_units = {unit_of[f] for h in decoy_hits for f in h["findings"] if f in unit_of} - matched_units
    defect_units = {u["id"] for u in unit_list if u["scenario_id"] in defect_scenarios}
    unlabeled_units = defect_units - matched_units - decoy_units
    detected = sum(d["detected_strict"] for d in per_defect)
    validity_lb = round(len(matched_units) / (len(matched_units) + len(clean_units) + len(decoy_units)), 3) if (matched_units or clean_units or decoy_units) else None
    clean_scenarios = len(clean_ids) or 1
    return {
        "suite": answer_key.get("suite"),
        "defects": len(defects),
        "recall_strict": round(sum(d["detected_strict"] for d in per_defect) / n, 3),
        "recall_lenient": round(sum(d["detected_lenient"] for d in per_defect) / n, 3),
        "severity_agreement": round(sum(d["severity_ok"] for d in per_defect) / n, 3),
        "decoys": len(decoys),
        "decoys_flagged": sum(h["hit"] for h in decoy_hits),
        "clean_control_findings": len(clean_findings),
        "clean_control_by_severity": {s: sum(1 for f in clean_findings if f["severity"] == s) for s in ("P0", "P1", "P2", "P3")},
        "precision_labeled": round(tp_findings / (tp_findings + fp_findings), 3) if (tp_findings + fp_findings) else None,
        "unlabeled_findings_in_defect_variants": len(unlabeled),
        "thoroughness_strict": round(detected / n, 3),
        "thoroughness_ci95": wilson(detected, len(defects)),
        "units": len(unit_list),
        "matched_units": len(matched_units),
        "clean_control_units": len(clean_units),
        "clean_control_units_by_severity": {s: sum(1 for u in unit_list if u["id"] in clean_units and u["severity"] == s) for s in ("P0", "P1", "P2", "P3")},
        "decoy_units": len(decoy_units),
        "unlabeled_units": len(unlabeled_units),
        "validity_lb_units": validity_lb,
        "effectiveness_lb": round(detected / n * validity_lb, 3) if validity_lb is not None else None,
        "false_alarm_units_per_clean_scenario": round(len(clean_units) / clean_scenarios, 2),
        "exact_viewport_matching": exact_viewport,
        "hypotheses_excluded": 0 if include_hypotheses else len(hypotheses),
        "per_defect": per_defect,
        "decoy_hits": decoy_hits,
        "clean_findings": [{"id": f["id"], "scenario_id": f["scenario_id"], "check_id": f["check_id"], "severity": f["severity"], "element_key": f["element_key"]} for f in clean_findings],
        "unlabeled": [{"id": f["id"], "scenario_id": f["scenario_id"], "check_id": f["check_id"], "severity": f["severity"], "element_key": f["element_key"]} for f in unlabeled],
    }
