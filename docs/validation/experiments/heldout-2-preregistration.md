# heldout-2 pre-registration

This document was written before `benchmarks/heldout-2` is scored. Everything
below is fixed first: the scorer, the configurations, the metrics, the hypotheses
and the pass rules. Changes after scoring must be listed in a dated amendment at
the end, with the reason, and the original analysis must still be reported.

## Custody

- The suite was written by four blind Opus agents from product briefs and public
  taxonomies, using the format in spec §12.1. Their completion messages were
  restricted to counts and file lists.
- The tool author (this session) does not open `benchmarks/heldout-2/keys/`,
  `site/` or `scenarios/` content. Scripts read them for recording and scoring.
- Scoring output shown to the author is limited to aggregate metrics. Per-defect
  results are written to a file and opened only after the aggregate report is
  committed.
- **Known limitation:** authors, detector author and adjudicators are all Claude
  models (the user asked for Claude-only subagents). The briefs use public
  taxonomies, but the answer-key schema still uses this tool's categories and
  profile attributes.

## Freeze

- The detector (`ergoqa/`, `drivers/web/`) and the scorer (`ergoqa/bench.py`)
  are frozen at the commit recorded in the scoring summary (`provenance.commit`,
  `dirty: false`) before the first recording of heldout-2.
- No change to checks, thresholds, floors or the composition algorithm is
  allowed between freeze and scoring.

## Configurations (all on the same recorded runs)

| ID | Profiles per device group |
| --- | --- |
| C1 measured-only | This tool's measured checks, default persona (30s, right one-hand / right mouse, no conditions) |
| C2 single persona | All checks, default persona |
| C3 stratified | `sample_profiles` stratified coverage: 14 per touch device, 7 per pointer device (current default fallback) |
| C4 audience-composed | `audience.compose` from the Stage-0 `audience.json` of each product, default floors. Budgets 6, 10 and 14 per product |
| C5 random | `sample_profiles(strategy="base_rate_sample")`, same budgets as C4, 20 seeds, mean and 95 % range |
| C6 persona agents | Opus persona agents in serve mode, composed from the audience (budget 4 per product), `--agent` recorded. Scored on `agent_judgment` defects only |

Stage 0 is run blind to defects. For each product, one Opus agent reads only
`products/<slug>/brief.md` and public sources, following
`references/audience-research.md`, and writes `audience.json`. That file is
committed before any recording.

## Scorer settings

- `bench.score(..., exact_viewport=True, include_hypotheses=False)`.
- Strict matching: scenario, category, selector and condition satisfied by a
  triggered profile.

## Metrics

- `recall_strict` with a Wilson 95 % CI (headline). Reported alongside:
  - `recall_strict_by_operating_point` (P0–P1, P0–P2, all);
  - `recall_strict_unconditioned`;
  - `condition_identified`;
  - `recall_lenient`.
- Recall per category, per `detectable_by` class and per `audience_relevance`
  class.
- Noise:
  - `validity_lb_units` (all units in the denominator);
  - `precision_labelled_subset_units`;
  - `clean_control_units` and per clean scenario, by severity;
  - decoy units;
  - unlabelled units.
- Severity: agreement with `severity_min` (one-sided).

## Hypotheses and pass rules

**H1: Coverage outside the check families is low, and is reported.**
Recall on `semantics` and `layout` defects is expected to be near 0, because
there are no checks for them yet. This is reported and not tuned.

**H2: Audience composition finds the defects that matter to the product's users.**
At a budget of 10 per product:

- C4 recall on `audience_relevance = primary` defects ≥ C5 mean + 0.10;
- C4 overall recall ≥ C5 mean.

Both must hold for "audience composition beats random" to be claimed.

**H3: Audience composition is not worse than stratified coverage at equal or
lower budget.** C4 at budget 14 has overall recall ≥ C3 − 0.05. If it fails, the
report says stratified coverage remains the better default for detection, and
audience composition is kept for prioritisation and agent selection.

**H4: Noise is acceptable for triage.**
C4 at budget 14 has:

- P0–P1 clean-control units per clean scenario ≤ 1;
- P0–P2 clean-control units per clean scenario ≤ 5.

**H5: Condition identification.**
`condition_identified` ≥ 0.5 for C3 and C4 at budget 14.

**H6: The persona-agent layer finds task-flow problems.**
C6 detects ≥ 30 % of `agent_judgment` defects. Uncorroborated PJ-01 notes are
hypotheses and do not count. Round-2 adjudication must find
≤ 1 invalid corroborated PJ-01 finding per clean scenario.

**H7: Unconditioned recall.**
C3 `recall_strict_unconditioned` ≥ C2 `recall_strict_unconditioned`. This is a
sanity check that more profiles do not hide profile-independent defects.

Each hypothesis is reported as pass, fail or inconclusive (CI overlapping the
threshold), with the numbers. There is no tuning between hypotheses.

## Round-2 adjudication

A stratified sample of at least 60 units from C4 budget 14 (unlabelled and
clean-control units, all check families present) is judged. Each unit gets 2
independent Opus judges who see the screenshot, element and rule text but not
the key. The report gives agreement and κ, and valid / invalid / split per check
family and per basis.

## Amendments

None yet.
