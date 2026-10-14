# Preregistered skill-on / skill-off comparison

Frozen before operator dispatch on 2026-10-14. This is a small paired pilot, not a new evaluation runner or a product-readiness claim.

## Question and scope

Does loading Remorsearch's instructions change an agent's defect detection, false alarms, completion, elapsed time and reported token use when model, browser transport, task and evidence access are held constant?

Use existing `benchmarks/mobile-commerce` checkout and booking pages and their existing clean controls, unchanged from commit `bda38f67f8ff4b5f56588d487430c282d1483be1`. No new demo product. This covers local UI/task QA and relevant ergonomic judgment. Live community acquisition, Figma authoring, code remediation and physical-device accuracy are not measured by this comparison. Installation and component readiness are checked separately.

## Frozen conditions

- Skill bundle SHA-256: `6d5bd9755b5fb48b4ca7f617dae07d0d7fe8f0344c43003d2025270499f7e3d2`.
- Requested operator: native `qa-reviewer`, `inferhub/combo-deepseek-4-1-flash`, effort `ultra`, fresh context without parent conversation. Record actual reported model/provider and any failure; do not silently change one arm's model.
- Two repetitions per condition, four page tasks per operator. Same order within each pair, reverse order in the second pair. Four independent operators; new browser context for each page. No shared findings or feedback during execution.
- Galaxy S24 browser profile, Chromium 141.0.7390.37, Playwright 1.56.1, Node 22.23.3; screenshots plus accessibility/state inspection. This is viewport/input emulation, not a physical phone.
- Both conditions use the identical existing Remorsearch browser transport, supplied neutrally, to isolate instruction use. The baseline does NOT load Remorsearch's SKILL or references. The treatment loads the frozen complete skill and relevant references. This is an instruction ablation with common instrumentation, not a claim that a baseline has no testing tools.
- At most 25 browser actions per page, 25 minutes per operator including instruction reading; stop a page after three consecutive tool/grounding failures. No additional attempts selected after seeing scores. Infrastructure failures are reported separately; a failed admission may be repaired and both sides rerun under identical settings before scoring.
- Read-only product QA. All form/payment actions are inside owned, offline synthetic fixtures. No live accounts, real payments, external posting or production writes.

## Blinding and matching

Pages use opaque route names. Operators may not read page source, scenario JSON, answer keys, other operators' output or repository validation reports. They may use screenshots and the existing driver inspect response. Both sides get the same task text, transport command syntax, input data and output fields. Treatment gets only the additional instruction to use the frozen skill. Baseline instructions are intentionally not supplemented with the skill's checklist.

The existing answer key is held separately from served files. No prompt, threshold or fixture is tuned after results. Preserve operator prompts, findings and nonempty browser traces. Review tool traces for forbidden reads before scoring.

Primary descriptive measures: unique seeded issues matched / eligible seeded issues, unsupported findings, false alarms on clean controls, task completion from driver checks, and evidence-backed reporting. Match requires the same element/state and causal behavior; generic advice does not match. Repeated descriptions count once. Existing seeded ergonomic/cognitive hypotheses are reported as such, separately from directly observable behavior; they are not human-discomfort measurements. Valid unseeded findings require independent review and are not automatically false positives.

Score anonymized outputs against the key and relevant captures with an independent reviewer, then supervisor verification. Disagreements remain visible. Report counts and paired differences, without significance or population claims from this small sample.

## Time and tokens

Record operator start/end time, browser-run duration, tool errors and provider-reported token counters when available. Include skill-reading overhead. Record cached input separately if supplied. Missing token fields remain null; never estimate them from text length or claim a dollar cost without an applicable verified price. Concurrent execution and tool latency affect elapsed time; it is workflow latency on this host, not model throughput.

Artifacts are owned by `/private/tmp/remorsearch-comparison-20261014/`. A sanitized result and trace summary will be checked into this directory after scoring; no credentials, hidden model reasoning or personal session history will be published.
