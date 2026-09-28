# UX Research QA Skills

Two Codex skills for evidence-driven UX research, design proposal, and browser-based UX QA.

## Skills

### `/aside-community-ux-research`

Aside-first research across public communities, comments, reviews, official sources, and comparable products. It separates firsthand evidence from inference, traces root causes and outcomes, and turns findings into Figma-ready flows and validation plans.

File: [`skills/aside-community-ux-research/SKILL.md`](skills/aside-community-ux-research/SKILL.md)

### `/persona-driven-ux-qa`

UX QA that combines Korean synthetic persona scenarios, Aside community signals, real browser reproduction, Figma comparison, causal analysis, and prioritized remediation with P0–P3 severity.

File: [`skills/persona-driven-ux-qa/SKILL.md`](skills/persona-driven-ux-qa/SKILL.md)

### `/ergonomic-persona-swarm-qa`

Stage 0 researches who uses the product. It writes an `ergo-audience.v1` file:
segments with evidence, device and age mix, conditions, contexts, and key tasks
with concrete data. A persona set is composed deterministically from that file.
Real runs of the product are recorded: web, mobile web and browser games through
a Playwright driver, Android via uiautomator, and iOS, desktop and native games
via annotated screenshots. Each run is then scored under every persona with
deterministic human-factors models:

- thumb reach by grip and handedness (left and right mirrored; side grips on
  tablets);
- dual-Gaussian touch accuracy and destructive misfire;
- feedback noticing;
- WCAG contrast;
- colour vision deficiency (Machado + CIEDE2000);
- text visual angle for presbyopia;
- Korean reading time for toasts;
- reaction windows, flashing, and game input demands.

Findings are grouped into problem units. Each carries the differential condition
(for example `grip=one_hand_left`) and the audience segments it affects, and is
reported as coverage over simulated profiles, never as prevalence. The structure
borrows from MiroFish; the claims do not. Optional LLM persona agents can drive
exploratory runs. They look at screenshots and act, and never role-play
ergonomics. That agent layer is not yet validated. See
[`validation-and-limits.md`](skills/ergonomic-persona-swarm-qa/references/validation-and-limits.md)
for what the benchmarks do and do not show.

File: [`skills/ergonomic-persona-swarm-qa/SKILL.md`](skills/ergonomic-persona-swarm-qa/SKILL.md) ·
research: [`docs/human-factors/`](docs/human-factors/) · contracts:
[`docs/ergonomic-swarm-spec.md`](docs/ergonomic-swarm-spec.md) · validation:
[`docs/validation/`](docs/validation/)

```sh
python3 scripts/ergo_qa.py profiles --count 16 --seed 7 --devices galaxy-s24,iphone-15 --out work/profiles.json
node drivers/web/ergo_drive.mjs run --scenario scenario.json --profile work/ep-01.json --out runs/ --base http://127.0.0.1:8765
python3 scripts/ergo_qa.py swarm --runs runs/ --profiles work/profiles.json --scenario scenarios/ --cross-profile --bundle --out report/
python3 scripts/ergo_bench.py --suite benchmarks/heldout-mixed --out .ergo-bench/heldout   # blind benchmark scoring
```

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

## One-entry improvement loop

The optional `ux-improvement-loop` skill and `scripts/ux_loop.py` compose the two
skills without merging their ownership. The CLI is a foreground, receipt-driven
state machine: it validates research intake, plans P0–P3 findings, gates browser
and visual evidence, applies explicitly authorized **local text patches**,
requires same-scenario regression replay, and persists an evidence-backed stop
report. It does not launch agents, browsers, Figma, Aside, builds or deployments.
Missing live receipts stop as `blocked`; they are never replaced by fixture proof.

Use Python 3.10+ on Linux or macOS from the repository root. No third-party Python
packages, Node packages, database, Git executable at runtime, or network are
required for offline validation. This implementation was tested on Python 3.13.5
on Linux; macOS and other Python versions have not been executed here. Keep the
repository-level `uxloop/`, `schemas/`, and `scripts/` together for the CLI; this is
not a published pip package. Each original skill still installs independently.

### One command with an actual, isolated example patch

```sh
python3 scripts/ux_loop.py demo --output .ux-loop/demo \
  --grant code_write --actor local-supervisor \
  --reason 'Approve the reviewed patch to this disposable fixture site only'
```

The command creates `.ux-loop/demo/site/index.html`, applies the provided label
patch, and runs all offline gates. The bundled screenshots, Figma readback,
research, browser telemetry and comparisons are **authored synthetic test
fixtures**, not live observations. Expected result: `status: complete`,
`decision: fixture_only_pass_not_product_verification`, `product_complete: false`.
The initial sample copy is local demo setup; no accounts or product data are
created. Existing sample source is never reset on resume.

Without `--grant code_write`, the same command stops with exit 3 at the permission
gate and leaves the original sample label unchanged. Provider-supplied v1
`permissions.granted` fields are historical evidence, not permission to operate.
Only the supervisor's explicit CLI grants authorize new actions for this goal.

### Persist, interrupt, and resume

Use a new output directory to see the interruption rather than reopen a completed
demo:

```sh
python3 scripts/ux_loop.py demo --output .ux-loop/resume-demo \
  --grant code_write --actor local-supervisor \
  --reason 'Approve only the isolated fixture patch' --pause-after browser
# Expected exit 6: checkpoint exists; the patch has not been applied.
python3 scripts/ux_loop.py resume \
  --checkpoint .ux-loop/resume-demo/checkpoint.json \
  --report .ux-loop/resume-demo/report.json
# Expected exit 0: same goal/run IDs and operational grant; no re-grant needed.
```

`--pause-after fix` demonstrates a patch that is applied but **not accepted**.
`--max-steps 1` yields a durable interruption after one gate. `--revoke code_write
--actor NAME --reason TEXT` removes future write permission, without pretending
that a previous authorized change never happened. All permission changes are
recorded. Checkpoints and the scoped product workspace are locked separately;
concurrent cooperating writers are blocked.

### Product evidence intake

First prepare a `ux-loop.v1` JSON packet following
[`docs/provider-contract.md`](docs/provider-contract.md). A live packet must
contain actual, versioned provider receipts; do not relabel the demo as live.
The complete annotated example is [`examples/loop/packet.json`](examples/loop/packet.json).

```sh
python3 scripts/ux_loop.py validate /path/to/packet.json \
  --evidence-root /path/to/evidence
python3 scripts/ux_loop.py run /path/to/packet.json \
  --workspace /path/to/product-checkout --evidence-root /path/to/evidence \
  --checkpoint /path/to/product-checkout/.ux-loop/goal.json
# Default read-only. To approve reviewed, scoped patches explicitly:
python3 scripts/ux_loop.py resume \
  --checkpoint /path/to/product-checkout/.ux-loop/goal.json \
  --grant code_write --actor APPROVING_OPERATOR --reason 'Approved goal and patch scope'
```

A provider can later append a replay to a blocked checkpoint with `resume --input
/path/to/extended-packet.json`. Old arrays must remain identical prefixes, and the
goal, scenario matrix, mode, privacy policy and historical permission record are
immutable. A failed/unknown attempt is not automatically retried: append a new
numbered round and new evidence/run/artifact IDs, then explicitly use `--retry`.
Maximum iterations are 1–10, chosen in the original goal. Old failed receipts
remain visible. A changed goal, scenario, Figma baseline or required evidence
identity requires a new goal/checkpoint rather than overwriting history.

Exit codes: **0** completed (read `mode` and `product_complete`); **1** invalid
packet in `validate`; **2** malformed input/CLI/integrity error; **3** blocked;
**4** unknown; **5** failed; **6** interrupted; **7** iteration limit. `validate`
checks the input graph and optionally artifact hashes; it explicitly does **not**
assess goal completion. A valid failed/blocked receipt is still valid input.

### Validation and design trade-offs

```sh
python3 scripts/validate_bundle.py tests/fixtures/valid-bundle.json
python3 scripts/ux_loop.py validate examples/loop/packet.json --evidence-root examples/loop
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/smoke_loop.py
```

The original v1 schema and both skill directories are retained. The v1 validator
now also rejects malformed categorical/reference field types, duplicate IDs
across record groups, and purported verified findings from uncompleted runs. The
new strict envelope is additive, not a v1 migration requirement. Standalone v1
supports bounded excerpts under its original rules; composition intake is
stricter and requires removing raw/excerpt content and retaining summaries.

The implementation intentionally imports browser/Figma/comparison receipts rather
than adding a privileged autonomous runner. Actual Aside, browser execution,
Figma reads/writes, test-data setup/cleanup, pixel comparison, accessibility
scanners, builds, deployment and signed provider authentication are **not
implemented or exercised** here. External operators/providers must perform and
attest those actions. Explicit grants do not turn an absent integration into a
success. `design_write` and `test_data_write` fix requests therefore remain blocked
even after authorization; authorized test-data scenario receipts can be imported.

Content hashes bind the declared `code_paths`, not every file in the product or a
remote deployed build. Include every relevant source/configuration path and
use an external provider that binds its running build to that exact scope. There
is no broad shell-command runner, automatic deployment, UX aggregate score, raw
community archive, or implicit claim of WCAG conformance. Figma-first and the ban
on side accent bars/side-tab cards remain hard gates. Community signals and
synthetic personas cannot establish population prevalence or user preference.

See [architecture](docs/architecture.md), [provider contract](docs/provider-contract.md),
[OMO inspection and provenance](docs/omo-reference-review.md), and
[implementation/verification report](IMPLEMENTATION_REPORT.md) for exact boundaries.
