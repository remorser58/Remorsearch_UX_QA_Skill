# Evidence Bundle Contract

This contract is shared by the research and QA skills. It makes provenance explicit without turning a research bundle into a claim that the sample is representative.

## Permission record

```json
{
  "permissions": {
    "requested": ["read_only", "design_write"],
    "granted": ["read_only"],
    "blocked": [
      {"capability": "design_write", "reason": "No Figma write approval for this run"}
    ]
  }
}
```

Allowed capabilities are `read_only`, `design_write`, `test_data_write`, and `code_write`. A blocked capability stays blocked even when a proposal recommends that action.

## Record graph

The top-level `records` object contains arrays named `sources`, `evidence`, `claims`, `personas`, `scenarios`, `runs`, `observations`, `findings`, `proposals`, and `figma`. Every record has a unique `id`.

```text
source → evidence → claim
persona → scenario → run → observation → finding → proposal
figma → finding or proposal
```

Use `source_id`, `evidence_ids`, `persona_id`, `scenario_id`, `run_id`, `observation_ids`, `finding_ids`, and `figma_id` for the links. A missing link is a validation error.

## Epistemic status

Every evidence item, claim, observation, and finding uses `epistemic_status`:

- `observed`: directly captured from a source or the product surface;
- `inferred`: reasoned from observed material;
- `unknown`: not established by the available evidence.

Use `verification_status: "verified"` only when the required observed support exists. Inference can guide a hypothesis and a next test. It cannot be the only support for a verified claim or finding.

## Source policy

Every source records `channel`, `source_ref`, `access_basis`, `access_method`, `public_scope`, and `retention_status`. Keep `withdrawn`, `deleted`, and `redacted` states visible. A withdrawn or deleted source must not continue to support a verified claim.

## Synthetic persona boundary

Synthetic personas require an adapter revision, schema fingerprint, seed, shard or config, maximum rows or bytes, timeout, selected record IDs, filled and unfilled strata, stop reason, `original_attributes`, and `scenario_assumptions`. Keep original attributes separate from assumptions added for a test. Synthetic personas produce bounded scenarios; they do not support claims about real-user preference, prevalence, or discomfort.

## Figma comparison

When comparing implementation with Figma, record `file_key`, `branch_key`, `baseline_version`, `node_ids`, `read_at`, `readback_artifact_ref`, and `design_status`. Classify the difference as `implementation_defect`, `design_defect`, `spec_conflict`, or `approved_deviation`. A baseline and readback version conflict keeps comparison unverified until resolved.
