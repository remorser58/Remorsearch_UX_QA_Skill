# Persona QA instruction improvement: preregistered bounded comparison

Frozen before operator execution on 2026-10-14. Baseline skill: `ba090fe832799beeee1ea76167ac70954b9f7c2c`. Treatment is frozen separately before its operator starts. This tests actual use of persona composition and profile-conditioned QA; the earlier `skill-ab-20261014` experiment did not.

## Scope and conditions

Reuse the existing `benchmarks/dev-2` delivery product, both variants, without changing its pages, defect keys or success contract. Supply the same product brief and a standalone, brief-derived audience to all operators. Fixture assertions remain synthetic product facts, not independently verified population research. This is a development regression sample, not an unseen test set.

Three fresh, independent operators use the same native `qa-reviewer` role and configured model/effort, with no inherited history: no skill, baseline skill, candidate skill. All can use the same existing browser driver and deterministic analysis CLI; only access to skill instructions differs. They must not inspect fixture source, defect keys, other operators or previous results. The implementation worker cannot read the evaluation pages, scenarios or keys.

Each operator composes a small persona plan from the supplied audience, chooses two relevant contrasting profiles on Galaxy S24, and performs the same ordering task on each page under each profile. Different chosen facets are reported as an experimental limitation. Record profiles, per-run binding and unsupported simulated capabilities. No requirement to invent user speech, preference, discomfort or physical impairment.

The common task includes mandatory menu choices, quantity, an allergy request, an invalid coupon followed by correction, checkout and final-value verification. All data and submissions belong to the local synthetic fixture. No external research, live accounts, real payments or new design work.

## Limits fixed before outcomes

- Four planned runs per operator, at most 35 browser actions per run, 25 minutes total including instruction reading and analysis, then report-only closeout. Explicitly report any unfinished run; do not silently remove it from denominators.
- Same Node.js 22, pinned Playwright and Chromium, common driver version, screenshot plus accessibility input. All operators see images before choosing touch actions. General-purpose browsing remains Aside; this controlled fixture task uses the existing project driver.
- Page order is reversed between the two profiles. All arms use the same order. No concurrent reuse of a browser context or output directory. No cross-arm coaching after execution starts, except identical transport recovery and time-bound reminders.
- Candidate instructions and the scorer are frozen before candidate execution. Failures stay in the record. Further implementation changes require a separately labelled rerun; no choosing the best attempt retrospectively.

## Evaluation

Primary: supported seeded findings with reproducible state/trace evidence, next to unsupported findings and warnings on the clean twin. No credit for a mere hypothetical concern or unexecuted model command. Count defect identities once per arm, report condition attribution separately, and adjudicate evidence against the existing key using blinded arm labels after operators finish.

Also report: task completion and final-value integrity; actual profiles composed, facets selected and profile-to-run binding; actual versus shared-recording coverage; deterministic measurements separated from model hypotheses and agent judgment; extra verified issues; elapsed time including setup/reporting; available provider token counters and their cache limitations. A successful fixture selector alone does not establish integrity of entered values.

Success for this bounded improvement requires a completed persona path and more supported issue coverage than the old-skill arm without a higher unsupported-finding count. If that condition is not met, report the failure and diagnose before claiming performance improved. One operator per arm cannot support statistical, population, dollar-cost or broad superiority claims. A no-skill comparison supplies context rather than replacing the old/new comparison.

Do not change benchmark answers, relax severity/evidence thresholds, count repeated profile occurrences as new defects, or describe deterministic selftests as skill-performance evidence. Preserve the original instructions, source hashes, generated profiles, run records, citations and adjudication. Publish only task-owned synthetic evidence; omit credentials, unrelated records, host prompts and hidden reasoning.

## Candidate 2 amendment, before its execution

Full CI rejected candidate 1 (`5f3c04e`) for exceeding the unchanged instruction reading budgets: entrypoint 8,226 versus 8,192 bytes, combined first-read closure 45,402 versus 42,000 bytes. Candidate 2 removes duplicated recipes and limits standalone QA to its relevant component. Its closure is 41,708 bytes (original baseline: 41,983), preserving composition, bound execution, evidence, permissions and analysis. No runtime, test, threshold, fixture or key changed.

Candidate 1 remains in the record; it is not silently replaced by a better run. A fresh candidate-2 operator receives the same audience, task, common tools, four planned runs and 25-minute observation limit as the original arms. Its prompt changes only assigned output/port and instruction-version paths. Candidate 2 is the final version to assess; the unsuccessful reading-budget candidate is diagnostic. This amendment is based on CI and instruction review, before inspecting operator findings. Staggered starts and one operator per version remain limitations.
