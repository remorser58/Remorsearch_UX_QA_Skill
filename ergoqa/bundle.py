"""Export swarm results as a ux-evidence-bundle.v1 (spec section 8).

The bundle is accepted by scripts/validate_bundle.py. Findings are ``verified``
only when every linked observation is a measured (observed) value from a
completed run of the same scenario/profile pair; model and judgment findings
stay ``unverified`` with epistemic status ``inferred``.
"""

from __future__ import annotations

from typing import Any, Iterable

from .profiles import COVERAGE_STRATA, profile_fingerprint


def _persona_record(profile: dict[str, Any], strategy: str, seed: int | None) -> dict[str, Any]:
    ref = profile.get("persona_ref") or {}
    attrs = profile["attributes"]
    assumptions = {field: attrs.get(field) for field in profile.get("assumption_fields", []) if field in attrs}
    filled = [profile["coverage_stratum"]] if profile.get("coverage_stratum") else []
    return {
        "id": profile["profile_id"],
        "basis": "synthetic",
        "label_ko": profile.get("label_ko", ""),
        "adapter_revision": "ergoqa-profiles/1",
        "schema_fingerprint": profile_fingerprint(profile),
        "seed": seed if seed is not None else 0,
        "shard_or_config": strategy,
        "max_scanned_rows": 0,
        "max_bytes_read": 0,
        "timeout_ms": 0,
        "selected_record_ids": [ref["record_id"]] if ref.get("record_id") else [],
        "filled_strata": filled,
        "unfilled_strata": [],
        "stop_reason": "count_reached",
        "original_attributes": {k: v for k, v in ref.items()},
        "scenario_assumptions": assumptions,
    }


def to_evidence_bundle(
    bundle_id: str,
    analyses: Iterable[dict[str, Any]],
    findings: Iterable[dict[str, Any]],
    profiles: Iterable[dict[str, Any]],
    strategy: str = "stratified_coverage",
    seed: int | None = None,
) -> dict[str, Any]:
    analyses = list(analyses)
    findings = list(findings)
    profiles = list(profiles)
    personas = [_persona_record(p, strategy, seed) for p in profiles]
    pairs: dict[str, dict[str, Any]] = {}
    runs: dict[str, dict[str, Any]] = {}
    observations: dict[str, dict[str, Any]] = {}
    obs_pair: dict[str, str] = {}
    obs_run_status: dict[str, str] = {}
    for analysis in analyses:
        scenario_id = analysis.get("scenario_id") or "unknown"
        for obs in analysis["observations"]:
            if obs["passed"]:
                continue
            pair_id = f"{scenario_id}@{obs['profile_id']}"
            pairs.setdefault(pair_id, {"id": pair_id, "persona_id": obs["profile_id"], "scenario_ref": scenario_id})
            run_record_id = f"{analysis['run_id']}@{obs['profile_id']}"
            runs.setdefault(run_record_id, {
                "id": run_record_id,
                "scenario_id": pair_id,
                "status": "completed" if analysis.get("run_status") == "completed" else str(analysis.get("run_status") or "unknown"),
                "recorded_run_id": analysis["run_id"],
                "cross_profile_evaluation": obs["profile_id"] not in analysis["profiles_evaluated"][:1],
            })
            observations[obs["id"]] = {
                "id": obs["id"],
                "run_id": run_record_id,
                "epistemic_status": obs["epistemic_status"],
                "basis": obs["basis"],
                "check_id": obs["check_id"],
                "element_key": obs["element_key"],
                "measurement": obs["measurement"],
                "severity": obs["severity"],
                "summary": obs["message_ko"],
            }
            obs_pair[obs["id"]] = pair_id
            obs_run_status[obs["id"]] = runs[run_record_id]["status"]
    bundle_findings: list[dict[str, Any]] = []
    proposals: list[dict[str, Any]] = []
    for finding in findings:
        per_pair: dict[str, list[str]] = {}
        for obs_id in finding["observation_ids"]:
            if obs_id in obs_pair:
                per_pair.setdefault(obs_pair[obs_id], []).append(obs_id)
        ids = []
        for pair_id, obs_ids in sorted(per_pair.items()):
            verified = all(
                observations[o]["epistemic_status"] == "observed" and obs_run_status[o] == "completed" and observations[o]["basis"] == "measured"
                for o in obs_ids
            )
            record_id = f"{finding['id']}@{pairs[pair_id]['persona_id']}"
            ids.append(record_id)
            bundle_findings.append({
                "id": record_id,
                "swarm_finding_id": finding["id"],
                "scenario_id": pair_id,
                "observation_ids": obs_ids,
                "severity": finding["severity"],
                "epistemic_status": "observed" if verified else "inferred",
                "verification_status": "verified" if verified else "unverified",
                "check_id": finding["check_id"],
                "summary": finding["summary_ko"],
            })
        if ids and finding.get("recommendation_ko"):
            proposals.append({
                "id": f"PR-{finding['id']}",
                "finding_ids": ids,
                "fix_layer": finding["fix_layer"],
                "summary": finding["recommendation_ko"],
            })
    return {
        "schema_version": "ux-evidence-bundle.v1",
        "bundle_id": bundle_id,
        "permissions": {"requested": ["read_only"], "granted": ["read_only"], "blocked": []},
        "records": {
            "sources": [], "evidence": [], "claims": [],
            "personas": personas,
            "scenarios": list(pairs.values()),
            "runs": list(runs.values()),
            "observations": list(observations.values()),
            "findings": bundle_findings,
            "proposals": proposals,
            "figma": [],
        },
        "notes": {
            "coverage_strata": [name for name, _ in COVERAGE_STRATA],
            "prevalence": "Synthetic ergonomic profiles give coverage, not prevalence.",
        },
    }
