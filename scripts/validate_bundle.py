#!/usr/bin/env python3
"""Validate the UX evidence bundle contract without external dependencies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


CAPABILITIES = {"read_only", "design_write", "test_data_write", "code_write"}
EPISTEMIC_STATUSES = {"observed", "inferred", "unknown"}
VERIFIED_STATUSES = {"verified", "unverified", "proposed"}
WITHDRAWN_SOURCE_STATES = {"withdrawn", "deleted"}
RECORD_NAMES = (
    "sources",
    "evidence",
    "claims",
    "personas",
    "scenarios",
    "runs",
    "observations",
    "findings",
    "proposals",
    "figma",
)


def _records(bundle: dict[str, Any], name: str) -> list[dict[str, Any]]:
    records = bundle.get("records")
    if not isinstance(records, dict):
        return []
    values = records.get(name, [])
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, dict)]


def _index(bundle: dict[str, Any], name: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    raw_records = bundle.get("records")
    values = raw_records.get(name) if isinstance(raw_records, dict) else None
    if not isinstance(values, list):
        errors.append(f"records.{name} must be an array")
        return indexed
    for position, record in enumerate(values):
        if not isinstance(record, dict):
            errors.append(f"records.{name}[{position}] must be an object")
            continue
        record_id = record.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"records.{name}[{position}].id is required")
            continue
        if record_id in indexed:
            errors.append(f"records.{name} contains duplicate id {record_id}")
            continue
        indexed[record_id] = record
    return indexed


def _require_ref(
    value: Any,
    target: dict[str, dict[str, Any]],
    location: str,
    errors: list[str],
) -> None:
    if not isinstance(value, str) or value not in target:
        errors.append(f"{location} references an unknown record")


def _require_ref_list(
    value: Any,
    target: dict[str, dict[str, Any]],
    location: str,
    errors: list[str],
) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{location} must contain at least one record id")
        return
    for index, item in enumerate(value):
        _require_ref(item, target, f"{location}[{index}]", errors)


def _validate_permissions(bundle: dict[str, Any], errors: list[str]) -> None:
    permissions = bundle.get("permissions")
    if not isinstance(permissions, dict):
        errors.append("permissions must be an object")
        return
    requested = permissions.get("requested")
    granted = permissions.get("granted")
    blocked = permissions.get("blocked")
    if not isinstance(requested, list) or not requested:
        errors.append("permissions.requested must be a non-empty array")
        requested = []
    if not isinstance(granted, list):
        errors.append("permissions.granted must be an array")
        granted = []
    if not isinstance(blocked, list):
        errors.append("permissions.blocked must be an array")
        blocked = []
    for capability in [*requested, *granted]:
        if capability not in CAPABILITIES:
            errors.append(f"unknown permission capability {capability!r}")
    if len(set(requested)) != len(requested):
        errors.append("permissions.requested must not contain duplicates")
    if len(set(granted)) != len(granted):
        errors.append("permissions.granted must not contain duplicates")
    for capability in granted:
        if capability not in requested:
            errors.append(f"granted permission {capability!r} was not requested")
    blocked_capabilities: set[str] = set()
    for index, entry in enumerate(blocked):
        if not isinstance(entry, dict):
            errors.append(f"permissions.blocked[{index}] must be an object")
            continue
        capability = entry.get("capability")
        reason = entry.get("reason")
        if capability not in CAPABILITIES:
            errors.append(f"permissions.blocked[{index}].capability is invalid")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"permissions.blocked[{index}].reason is required")
        if isinstance(capability, str):
            blocked_capabilities.add(capability)
            if capability not in requested:
                errors.append(f"blocked permission {capability!r} was not requested")
            if capability in granted:
                errors.append(f"permission {capability!r} cannot be granted and blocked")
    for capability in requested:
        if capability not in granted and capability not in blocked_capabilities:
            errors.append(f"unresolved permission {capability!r} must be granted or blocked")


def _validate_sources(sources: dict[str, dict[str, Any]], errors: list[str]) -> None:
    required = ("channel", "source_ref", "access_basis", "access_method", "public_scope", "retention_status")
    for source_id, source in sources.items():
        for field in required:
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"records.sources[{source_id}].{field} is required")


def _validate_personas(personas: dict[str, dict[str, Any]], errors: list[str]) -> None:
    required = (
        "adapter_revision",
        "schema_fingerprint",
        "seed",
        "shard_or_config",
        "max_scanned_rows",
        "max_bytes_read",
        "timeout_ms",
        "selected_record_ids",
        "filled_strata",
        "unfilled_strata",
        "stop_reason",
        "original_attributes",
        "scenario_assumptions",
    )
    for persona_id, persona in personas.items():
        if persona.get("basis") != "synthetic":
            continue
        for field in required:
            if field not in persona:
                errors.append(f"records.personas[{persona_id}].{field} is required for synthetic personas")
        for field in ("max_scanned_rows", "max_bytes_read", "timeout_ms"):
            value = persona.get(field)
            if not isinstance(value, int) or value < 0:
                errors.append(f"records.personas[{persona_id}].{field} must be a non-negative integer")
        if not isinstance(persona.get("selected_record_ids"), list):
            errors.append(f"records.personas[{persona_id}].selected_record_ids must be an array")
        if not isinstance(persona.get("filled_strata"), list):
            errors.append(f"records.personas[{persona_id}].filled_strata must be an array")
        if not isinstance(persona.get("unfilled_strata"), list):
            errors.append(f"records.personas[{persona_id}].unfilled_strata must be an array")
        if not isinstance(persona.get("original_attributes"), dict):
            errors.append(f"records.personas[{persona_id}].original_attributes must be an object")
        if not isinstance(persona.get("scenario_assumptions"), dict):
            errors.append(f"records.personas[{persona_id}].scenario_assumptions must be an object")


def _validate_links(
    sources: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
    claims: dict[str, dict[str, Any]],
    personas: dict[str, dict[str, Any]],
    scenarios: dict[str, dict[str, Any]],
    runs: dict[str, dict[str, Any]],
    observations: dict[str, dict[str, Any]],
    findings: dict[str, dict[str, Any]],
    proposals: dict[str, dict[str, Any]],
    figma: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    for evidence_id, item in evidence.items():
        _require_ref(item.get("source_id"), sources, f"records.evidence[{evidence_id}].source_id", errors)
    for claim_id, item in claims.items():
        _require_ref_list(item.get("evidence_ids"), evidence, f"records.claims[{claim_id}].evidence_ids", errors)
        if "persona_ids" in item:
            _require_ref_list(item.get("persona_ids"), personas, f"records.claims[{claim_id}].persona_ids", errors)
    for scenario_id, item in scenarios.items():
        _require_ref(item.get("persona_id"), personas, f"records.scenarios[{scenario_id}].persona_id", errors)
    for run_id, item in runs.items():
        _require_ref(item.get("scenario_id"), scenarios, f"records.runs[{run_id}].scenario_id", errors)
    for observation_id, item in observations.items():
        _require_ref(item.get("run_id"), runs, f"records.observations[{observation_id}].run_id", errors)
    for finding_id, item in findings.items():
        _require_ref(item.get("scenario_id"), scenarios, f"records.findings[{finding_id}].scenario_id", errors)
        _require_ref_list(item.get("observation_ids"), observations, f"records.findings[{finding_id}].observation_ids", errors)
        if "claim_ids" in item:
            _require_ref_list(item.get("claim_ids"), claims, f"records.findings[{finding_id}].claim_ids", errors)
        if "figma_id" in item:
            _require_ref(item.get("figma_id"), figma, f"records.findings[{finding_id}].figma_id", errors)
    for proposal_id, item in proposals.items():
        _require_ref_list(item.get("finding_ids"), findings, f"records.proposals[{proposal_id}].finding_ids", errors)
        if "figma_id" in item:
            _require_ref(item.get("figma_id"), figma, f"records.proposals[{proposal_id}].figma_id", errors)


def _validate_semantics(
    evidence: dict[str, dict[str, Any]],
    claims: dict[str, dict[str, Any]],
    personas: dict[str, dict[str, Any]],
    observations: dict[str, dict[str, Any]],
    findings: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
    figma: dict[str, dict[str, Any]],
    errors: list[str],
) -> None:
    for record_type, records in (("evidence", evidence), ("claims", claims), ("observations", observations), ("findings", findings)):
        for record_id, item in records.items():
            status = item.get("epistemic_status")
            if status not in EPISTEMIC_STATUSES:
                errors.append(f"records.{record_type}[{record_id}].epistemic_status is invalid")

    for claim_id, claim in claims.items():
        verification_status = claim.get("verification_status", "unverified")
        if verification_status not in VERIFIED_STATUSES:
            errors.append(f"records.claims[{claim_id}].verification_status is invalid")
        evidence_ids = claim.get("evidence_ids") if isinstance(claim.get("evidence_ids"), list) else []
        supporting = [evidence[evidence_id] for evidence_id in evidence_ids if evidence_id in evidence]
        synthetic_persona_ids = {
            persona_id for persona_id in claim.get("persona_ids", [])
            if persona_id in personas and personas[persona_id].get("basis") == "synthetic"
        }
        preference_kind = claim.get("claim_kind") in {"user_preference", "real_user_preference", "prevalence", "discomfort"}
        if preference_kind and synthetic_persona_ids:
            errors.append(f"records.claims[{claim_id}] uses a synthetic persona as direct real-user support")
        if preference_kind and claim.get("support_basis") == "synthetic_persona":
            errors.append(f"records.claims[{claim_id}] cannot use synthetic_persona support for a real-user claim")
        if verification_status == "verified":
            if claim.get("epistemic_status") != "observed":
                errors.append(f"records.claims[{claim_id}] cannot be verified from non-observed epistemic status")
            if not supporting or any(item.get("epistemic_status") != "observed" for item in supporting):
                errors.append(f"records.claims[{claim_id}] requires observed evidence for verification")
            if any(sources.get(item.get("source_id"), {}).get("retention_status") in WITHDRAWN_SOURCE_STATES for item in supporting):
                errors.append(f"records.claims[{claim_id}] uses withdrawn or deleted source material")

    for finding_id, finding in findings.items():
        if finding.get("verification_status") == "verified":
            observation_ids = finding.get("observation_ids")
            linked = [observations[observation_id] for observation_id in observation_ids if observation_id in observations] if isinstance(observation_ids, list) else []
            if not linked:
                errors.append(f"records.findings[{finding_id}] cannot be verified without an observation")
            elif any(item.get("epistemic_status") != "observed" for item in linked):
                errors.append(f"records.findings[{finding_id}] requires observed product observations for verification")

    for figma_id, item in figma.items():
        required = ("file_key", "branch_key", "baseline_version", "node_ids", "read_at", "design_status")
        for field in required:
            if field not in item or item[field] in (None, "", []):
                errors.append(f"records.figma[{figma_id}].{field} is required")
        if not isinstance(item.get("node_ids"), list) or not item.get("node_ids"):
            errors.append(f"records.figma[{figma_id}].node_ids must be a non-empty array")
        design_status = item.get("design_status")
        if design_status in {"comparison_ready", "approved", "implemented"} and not item.get("readback_artifact_ref"):
            errors.append(f"records.figma[{figma_id}].readback_artifact_ref is required for {design_status}")
        readback_version = item.get("readback_version")
        if readback_version and readback_version != item.get("baseline_version") and design_status in {"comparison_ready", "approved", "implemented"}:
            errors.append(f"records.figma[{figma_id}] has a baseline/readback version conflict")
        defect_class = item.get("defect_class")
        if defect_class and defect_class not in {"implementation_defect", "design_defect", "spec_conflict", "approved_deviation"}:
            errors.append(f"records.figma[{figma_id}].defect_class is invalid")


def validate_bundle(bundle: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(bundle, dict):
        return ["bundle must be a JSON object"]
    if bundle.get("schema_version") != "ux-evidence-bundle.v1":
        errors.append("schema_version must be ux-evidence-bundle.v1")
    if not isinstance(bundle.get("bundle_id"), str) or not bundle.get("bundle_id", "").strip():
        errors.append("bundle_id is required")
    records = bundle.get("records")
    if not isinstance(records, dict):
        errors.append("records must be an object")
        return errors
    _validate_permissions(bundle, errors)
    indexed = {name: _index(bundle, name, errors) for name in RECORD_NAMES}
    _validate_sources(indexed["sources"], errors)
    _validate_personas(indexed["personas"], errors)
    _validate_links(*(indexed[name] for name in RECORD_NAMES), errors)
    _validate_semantics(
        indexed["evidence"],
        indexed["claims"],
        indexed["personas"],
        indexed["observations"],
        indexed["findings"],
        indexed["sources"],
        indexed["figma"],
        errors,
    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: bundle not found: {args.bundle}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as error:
        print(f"ERROR: invalid JSON: {error}", file=sys.stderr)
        return 2
    errors = validate_bundle(bundle)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"VALID: {bundle['bundle_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
