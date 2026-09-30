<!-- Mode: ergonomics, experimental. Entry point: `SKILL.md`. -->
# Ergonomics mode

Default to a stratified detector run on the real surface: one recorded flow per device/orientation, analyzed across profiles. It needs no subagents. Persona agents, interviews and simulated experience boards are opt-in. Reports can be English or Korean.

## Phase 0 recap

Use `SKILL.md` Phase 0: scope/build/tasks, devices/orientations, input, supplied data, grants and tools. Choose detector coverage or requested persona-agent behavior. Missing audience research takes the stratified path; explain it. Korean product QA reads `references/persona-qa/kwcag-card.md`; Korean research users/channels open `references/research/korea/overview.md` only when research runs. Before an external page, including a later lead, carry `references/shared/access-card.md` and use research's evidence card. Ask at most one grouped question for necessary missing inputs.

Keep basis visible: **measured** is surface observation against a fixed standard; **model** applies a published model to measured inputs and is inferred; **judgment** is human/LLM inference. Only measured observations from completed runs can be verified. Counts are k/n **simulated-profile coverage**; never real prevalence, preference, discomfort or forecast. Do not role-play pain or seeing difficulty as measurements. The uncalibrated thumb model alone is capped at P2. Model prediction alone cannot reach P0; P0 needs measured safety failure or a declared irreversible action with a computed misfire path. Every P0/P1 needs measured basis or corroborating task trace.

## 1. Frame the scenario

Record actual URL/app/build, task/data, platform/device/orientation and data-mutation risk. Declare roles: primary, destructive, irreversible (only after sandbox confirmation of no confirm/undo), critical_message, error_message, status, hud, game_control, timed, ad_like. Declare transient_text and qte windows. Use the shipped driver init/schema; consult `references/ergonomics/platform-drivers.md` by section for a non-web transport. Repository specification `docs/ergonomic-swarm-spec.md` is not installed with the skill.

```sh
node drivers/web/ergo_drive.mjs devices
node drivers/web/ergo_drive.mjs init --url URL --device DEVICE --task TASK --out sc.json
python3 scripts/ergo_qa.py catalog
```

Set safe recorded steps and success criteria that compare all entered values with the final state. Read-only defaults and separate write grants apply. Stop on production verification/payment, human checks or unavailable evidence; no real accounts/data are changed without scope-specific authority. Emulation is Chromium viewport/DPR/input, not a real device, grip, keyboard occlusion, safe area or screen reader; disclose before scenarios and in the report.

## 2. Compose profiles

Default stratified coverage:

```sh
python3 scripts/ergo_qa.py profiles --count 16 --seed 7 --devices galaxy-s24,iphone-15 --out work/profiles.json
```

Cover per device right/left one-hand, two-thumb and cradled grips; pointer devices use mouse right/left and keyboard-only. Include condition strata: deutan, presbyopia 60s, mild tremor, walking, low vision, 70s+, small hand; alternate hands. Pointer devices skip walking/small-hand/tremor because only the touch model reads them. Base rates fill remaining slots, never measure this product's audience. Record assumptions, seed, sampled and unfilled facets.

If a completed evidence-backed ergo-audience.v1 was supplied/requested, consult `references/ergonomics/audience-research.md` by section, validate it, then:

```sh
python3 scripts/ergo_qa.py audience-check audience.json
python3 scripts/ergo_qa.py personas --audience audience.json --budget 12 --plan work/persona-plan.md --out work/profiles.json
python3 scripts/ergo_qa.py scenario-stubs --audience audience.json --out scenarios/
```

Research-origin audiences also require the supported gate/bundle/run checks described in `references/research/workflow.md`. Drafts cannot compose; unknown shares stay unknown. Audience composition chooses typical members, weighted one-facet variants and inclusive floors; the plan explains every profile and uncovered facet. Extra conditions follow the audience. A linked narrative dataset needs exact revision/schema/bounded sampling; it has no measured ergonomic attributes. Synthetic/LLM output never supplies audience evidence.

## 3. Record real runs

Use the host browser first or Node.js 22 fallback with installed dependencies:

```sh
node drivers/web/ergo_drive.mjs run --scenario sc.json --device DEVICE --out runs/
python3 scripts/ergo_qa.py analyze --runs runs/ --profiles work/profiles.json --scenario sc.json --cross-profile --out analysis.json
```

One real scripted trace per device/orientation can serve all profiles there. Keep screenshots, geometry/colors/timing before/after each step, actual outcomes and collector versions. Bundled run/idle default limit is 900 seconds. Android uses adb capture plus `android-snapshot`; iOS/desktop/engine-rendered games use platform captures and annotations (vision geometry is inferred); look up `references/ergonomics/platform-drivers.md` for exact options. A blocked transport stays untested.

Opt-in persona agents use serve and `references/ergonomics/persona-agent-protocol.md`, plus `references/agent-setup.md` if spawning is authorized. Each agent receives applicable cards and sees screenshots before touch decisions. Separate runs per agent when behavior matters; later technical/a11y inspection records its provenance. Notes/expectation/confusion remain judgment. Optional `references/ergonomics/swarm-and-social-layer.md` boards/interviews cite run/step/observation IDs; ungrounded answers are speculative and simulated discourse only generates research hypotheses.

## 4. Analyze, judge and aggregate

```sh
python3 scripts/ergo_qa.py swarm --runs runs/ --profiles work/profiles.json --scenario sc.json --cross-profile --bundle --out report/
python3 scripts/validate_bundle.py report/bundle.json
```

Add `--audience audience.json` only for a completed audience. Use the emitted bundle path if this version names it differently. Outputs: findings.json, analyses.json, report.md and an evidence bundle. Segment groups/segments_affected describe triggered profiles, never user shares. Record model IDs and differential conditions (shared by triggered profiles and no untriggered profile). Use `python3 scripts/ergo_qa.py heatmap --help` for reach/gaze review options.

Lookup fired check IDs in `references/ergonomics/human-factors-checks.md`: reach, pointing/Fitts/misfire, gaze, contrast/CVD/visual angle/bright light, choice/reading/latency, game reaction/flash, names/labels/errors/focus/clipping/reflow. Formulas and validity limits are in `ergoqa/params.py`; repository briefs `docs/human-factors/` are not installed. A detector alone cannot decide WCAG size exceptions, irreversible actions, destructive-primary styling, ad-like information, game intent, left-handed options or heuristic fit: record screenshot/step-backed judgment and its limit. ACT examples gate covered checks; a screening result never certifies standards compliance.

## 5. Report, fix and replay

Use `references/ergonomics/report-template.md` by section. Decision first, findings ordered by severity/confidence, measured/model/judgment separated, differential conditions and k/n coverage, assumptions and untested platform/device/grip/condition list. Cite source/model limits; benefit claims require measurement. Propose the smallest fix at the deepest confirmed cause (`references/shared/causal-chain.md`). Figma is the design source of truth when present; record version/readback. Skill-authored proposals use no side accent bars, attached side tabs or decorative rails; existing product QA requires task harm.

Writes need design/test-data/code grants separately. Replay identical scenario/device/profiles after a fix; compare baseline/change/replay and adjacent states. For P0/P1 use persona-qa's fresh capture receipt and second-pass rules. Generated report wording can be English or Korean without changing measured outputs.

## Failure ladder

| Missing/failing | Next step; ask boundary |
| --- | --- |
| Audience | Stratified default with reason/untested facets; do not block screening |
| Browser/platform | Available host transport, then driver; deny/unavailable means real-surface blocker. Ask only for needed access. |
| Source/key | Only requested audience research: card stop, other source family; key set in environment if necessary |
| Verifier | Serial labelled self-pass; unresolved exceptions/flags stay inconclusive. Ask for required human verification. |
| Model input | No guess of geometry/timing; measured or explicitly inferred input, otherwise untested |

## Anti-patterns

| What goes wrong | Why | Fix |
| --- | --- | --- |
| Spawn 16 agents by default | Screening only needs traces/profiles | Detector default; agents opt-in |
| “My thumb hurts” | Synthetic role-play | Computed model, validity cap |
| k/n becomes market percent | Profiles are sampling coverage | State denominator and omissions |
| Thumb model rated P0 | Uncalibrated reach cannot prove harm | P2 cap, measured/task corroboration |
| Vision boxes called measured | Geometry is inferred | Record annotation provenance |

## Done when

Evidence-backed audience or explicit stratified reason; real-surface runs or exact blockers; assumptions/sampling/untested facets recorded; measured/model/judgment separated with model IDs; P0/P1 has measured basis or trace corroboration and fresh receipt/second pass; severity caps hold; counts are simulated coverage; bundle validates when produced; report language, limitations and replay outcome explicit; no unauthorized side effect.
