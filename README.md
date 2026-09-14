# UX Research QA Skills

Two Codex skills for evidence-driven UX research, design proposal, and browser-based UX QA.

## Skills

### `/aside-community-ux-research`

Aside-first research across public communities, comments, reviews, official sources, and comparable products. It separates firsthand evidence from inference, traces root causes and outcomes, and turns findings into Figma-ready flows and validation plans.

File: [`skills/aside-community-ux-research/SKILL.md`](skills/aside-community-ux-research/SKILL.md)

### `/persona-driven-ux-qa`

UX QA that combines Korean synthetic persona scenarios, Aside community signals, real browser reproduction, Figma comparison, causal analysis, and prioritized remediation with P0–P3 severity.

File: [`skills/persona-driven-ux-qa/SKILL.md`](skills/persona-driven-ux-qa/SKILL.md)

## Design boundary

- Synthetic personas generate plausible test situations. They do not represent measured user prevalence.
- Community findings generate hypotheses. Product behavior is confirmed through the real surface or a reliable product artifact.
- Figma remains the source of truth for screen composition, interaction states, navigation, and design intent.
- Research and QA stay read-only unless a separate action is explicitly authorized.
- Side accent bars, attached side tabs, and decorative rails are excluded from the design language.

## Evidence bundle contract

Research and QA runs can exchange a machine-readable evidence bundle. The bundle keeps source, evidence, claim, persona, scenario, run, observation, finding, proposal, and Figma records separately linked by stable IDs.

- `permissions` records requested, granted, and blocked capabilities: `read_only`, `design_write`, `test_data_write`, and `code_write`.
- `epistemic_status` is one of `observed`, `inferred`, or `unknown`. Inference does not become verified by repetition.
- A synthetic persona can create a scenario. It cannot directly support a claim about real-user preference or prevalence.
- `figma` records keep `file_key`, `branch_key`, `baseline_version`, `node_ids`, `read_at`, and `readback_artifact_ref` when comparison is claimed.
- Channel sources keep access basis, access method, public scope, and retention or withdrawal status.

Validate a bundle from the repository root:

```sh
python3 scripts/validate_bundle.py tests/fixtures/valid-bundle.json
python3 -m unittest discover -s tests -p 'test_*.py'
```

The validator checks structural IDs, cross-references, permission boundaries, synthetic-persona misuse, unsupported verified findings, withdrawn sources, bounded persona provenance, and Figma version conflicts. It does not prove that an artifact is authentic or that a source sample is representative.

## Installation

Copy either skill directory into `~/.codex/skills/` or `~/.claude/skills/`.

The skill directories include their own evidence-bundle reference. The repository-level `schemas/`, `scripts/`, and `tests/` directories provide optional offline validation for teams that keep research and QA artifacts together.
