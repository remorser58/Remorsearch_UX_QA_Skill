# Validation and Limits

How this skill is validated, what the numbers mean, and where it is known to be
weak. Raw results: `docs/validation/`. Benchmark format: `docs/ergonomic-swarm-spec.md`
section 12.

## Method

1. **Blind seeded-defect suites.** A separate agent writes fixture pages with
   seeded defects, decoys (things that look wrong but pass the cited standard)
   and clean controls (the same page without the defects). The answer key
   names scenario, category, element selector, profile condition and minimum
   severity. It never names check IDs. Tool authors must not read answer keys.
2. **Real surface.** `scripts/ergo_bench.py` serves the suite locally, records
   one scripted run per scenario and device in Chromium (real touch/mouse
   events via CDP), analyses each run under every profile on that device, and
   scores three configurations:
   - `measured_only`: measured checks, one default persona. This is roughly what
     a standard automated accessibility scan reports.
   - `single_profile`: all checks, one default persona (30s, right hand, one-hand
     grip, normal vision, seated).
   - `swarm`: all checks, 14 stratified profiles per touch device (7 per pointer
     device).
3. **Metrics.**
   - Strict recall: the same element, category and profile condition as the key.
   - Lenient recall: the same element and condition, any category.
   - Severity agreement: detected at or above `severity_min`.
   - Decoys flagged.
   - Clean-control findings: findings on pages with no seeded defect. They are
     false-positive *candidates*, because a clean page can still have real
     unseeded problems.
   - Unlabeled findings: extra findings on defect pages. These need
     adjudication.
4. **Held-out rule.** A suite is scored once with the detector frozen at a
   recorded commit. After that it becomes a development suite.
5. **Adjudication.** A stratified sample of unlabeled and clean-control findings
   is judged by independent LLM judges that see the screenshot, the element and
   the rule. They do not see the answer key. The result estimates real
   precision.

## Results so far

| Suite (role) | Detector | measured-only | single persona | swarm | Clean-control findings (swarm) |
| --- | --- | --- | --- | --- | --- |
| mobile-commerce v1 (dev, 17 defects) | before tuning | 0.29 | 0.65 | 0.82 | 232 |
| mobile-commerce v2 (dev) | `8c1de02` | 0.35 | 0.71 | **0.94** | 84 |
| game-desktop v1 (dev, 16 defects) | before tuning | 0.06 | 0.25 | 0.31 | 92 |
| game-desktop v3 (dev) | `3cad062` | 0.44 | 0.88 | **1.00** | 31 |
| heldout-mixed (held-out, 20 defects) | frozen `8c1de02` | 0.15 | 0.35 | **0.80** (lenient 0.90) | 98 |

Recall is strict recall. On the held-out suite the swarm found 9 defects that
the single default persona missed. Severity agreement was 0.70, 2 of 6 decoys
were flagged, and labelled precision (a lower bound) was 0.34.

Read these numbers with the disclosures below. The development-suite gains are
post-hoc: the checks were tuned after seeing those suites' scores. Only the
held-out row is an out-of-sample estimate, and it is one small suite of
synthetic pages.

## Disclosures

- **Post-hoc tuning.** Noise fixes were made after v1 scoring on the
  development suites. Each was a principled rule change (for example PC-02 limited
  to boundary-identified components, profile multipliers only below 9.2 mm).
  They were still chosen while looking at the scores.
- **Blindness breaches.** The benchmark authors' completion summaries described
  some seeded defects to the tool author, for all suites. The held-out suite's
  timing-window metadata was also printed once before scoring. The held-out
  result was still produced by a frozen detector with no change after scoring.
- **Synthetic pages.** Fixture pages written by an agent are cleaner and more
  regular than production apps. Recall on real products is unknown.
- **Seeded categories match the checks.** Suites were written from the same
  human-factors literature as the checks. Defect types the tool has no check
  for are under-represented, so recall overstates coverage of all UX problems.

## Known limits

- **Noise is the main weakness.** Clean-control findings (84–98 per suite) mean
  that a raw findings list is too long to hand to a team unfiltered. Report P0–P2
  first, group P3 by condition, and use adjudication before claiming precision.
- **Models are uncalibrated for Korean users.** Thumb reach (Parhi landmark
  scaled by hand length), touch-SD multipliers for walking, tremor and age,
  gaze priors (free viewing in Western labs) and notice bands are assumptions or
  foreign data. They can reorder findings; they never justify P0 alone.
- **Gaze is free-viewing.** `gaze-priority-v2` does not model goal-directed
  search, so GZ findings are prompts to check hierarchy, capped at P3 (GZ-01).
- **Timing needs measurement.** QTE and flash results depend on frame-accurate
  capture; software input injection under-reports latency.
- **LLM persona agents are not users.** They find task-flow confusion, dead
  ends and missing feedback. They cannot evidence bodily difficulty, and they
  follow ambiguous goals differently from people. Scenario goals must include
  concrete data (amounts, dates, names), or the agent never reaches the branch
  under test (seen in the persona trial: a transfer-limit path was never hit).
- **Coverage, not prevalence.** "k/n simulated profiles" says which conditions
  were tried. It says nothing about how many real users are affected.

## Calibration protocol (proposed, not yet run)

- **Reach and touch.** About 20 Korean adults per grip, a target-acquisition
  task on two phone sizes; fit the polar reach zones and the per-condition
  σ multipliers.
- **Gaze.** About 20 people × 30 Korean app screens with an eye tracker or
  webcam gaze. Check the P(primary fixated within 4 fixations) ranking against
  real first-fixation data.
- **Reading.** Korean older-adult reading rates for short UI messages (toasts)
  on phones.
- **Real products.** Run the swarm on open-source apps with known accessibility
  bug reports. Compare against issue-tracker ground truth and have human experts
  adjudicate findings.

## Experiments

Removal and addition experiments (leave-one-out per check and per profile
condition, model toggles, swarm-size discovery curves, audience-based versus
random composition) are recorded under `docs/validation/experiments/` with the
decision each one led to.
