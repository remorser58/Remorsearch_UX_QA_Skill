# Collaboration notes (sessions working on this repository)

Channel: this file on each session's branch. Cloud sessions cannot always message
each other, so write decisions, questions and hand-offs here and push.

## Session "스킬 확인" — branch `claude/practical-edison-n5sisf`

### Goal (as clarified by the user)

1. Research **who would use the product under test** (target users, contexts,
   devices, abilities, key tasks), with evidence.
2. Compose **diverse personas from that research** — not random sampling.
3. Simulate those personas operating the **real screen** and QA it with
   human-factors models (reach/handedness, touch accuracy, gaze, contrast, CVD,
   text size, reading time, timing windows, flashing, game input demands).
4. Results must be very good: high recall of real issues, low noise, findings
   explained per user segment and condition.

### State (pushed)

- Skill: `skills/ergonomic-persona-swarm-qa/` (SKILL.md + references)
- Contracts: `docs/ergonomic-swarm-spec.md`
- Research briefs: `docs/human-factors/*.md`; MiroFish review: `docs/mirofish-reference-review.md`
- Code: `ergoqa/` (stdlib Python), `scripts/ergo_qa.py`, `scripts/ergo_bench.py`
- Web driver: `drivers/web/` (`node drivers/web/selftest.mjs`)
- Benchmarks: `benchmarks/{mobile-commerce,game-desktop,heldout-mixed}` (answer keys: do not read them if you evaluate detection)
- Validation: `docs/validation/*.json` — held-out suite scored once with the detector frozen at 8c1de02: swarm recall 0.80 (strict), single default persona 0.35, measured-only 0.15; noise (clean-control findings) still high.

### In progress here

- Audience → persona pipeline: `ergo-audience.v1` schema (spec section "Audience"),
  `scripts/ergo_qa.py personas --audience audience.json`, segment-aware aggregation and report.
- Fixes from six Opus-max cross-reviews, precision adjudication and the live persona-agent trial.

### Proposed split (please confirm or overwrite in your branch's copy of this file)

- Other session: Stage-0 "target user research" method and content —
  `skills/ergonomic-persona-swarm-qa/references/audience-research.md` (how an agent
  researches who uses a product: `aside-community-ux-research`, app-store reviews,
  official docs/analytics, competitor audiences; evidence tagging; output
  `audience.json`), `examples/audience/` samples, and an end-to-end dogfood on a
  real open-source web app served locally (`docs/dogfood-*.md`).
- This session: code and contracts under `ergoqa/`, `drivers/`, `scripts/`,
  `docs/ergonomic-swarm-spec.md`, and the skill's SKILL.md integration.
- Work in disjoint files; base on this branch; push to your branch; this session
  fetches and merges.

### Interface promise

`ergo-audience.v1` will be documented in `docs/ergonomic-swarm-spec.md` before any
code depends on it; changes after that are additive only.
