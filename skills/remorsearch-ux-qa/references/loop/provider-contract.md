# Provider handoff: research, browser, visual QA and replay

The concrete envelope is `schemas/ux-loop.v1.schema.json`; the fully populated
**synthetic-only** example is `examples/loop/packet.json`. The original
`ux-evidence-bundle.v1` contract remains the ownership boundary. This document
explains the provider data that the code actually validates, not a claim that a
live provider is already connected.

## 1. Research intake and goal planning

Use the bundled research component, including its browser-tool order,
public-page rules and read-only rules (`references/research/public-page-access.md`).
Preserve the user's tabs when research drives their browser; community evidence is
captured as an anonymous visitor sees it. QA scenarios, in contrast, must use
separately isolated contexts and authorized fixture accounts so they do not mutate
the user's real session.
A provider is not authorized merely because a community page suggests an action.

Build sources -> evidence -> claims -> scenarios/proposals with stable IDs and
`observed`, `inferred`, or `unknown` annotations. Remove raw/excerpt fields before
composition intake, retain minimized summaries, access/withdrawal metadata and
sampling limitations. An observed source statement is not measured preference or
prevalence. Required unknown evidence stops the goal rather than being relabeled.

Declare one route/device/viewport/input/fixture combination per scenario ID,
explicit steps with expected results and required permission, and keyboard,
focus, semantics plus any other accessibility checks. Set all mandatory stop
conditions true and a finite iteration budget. `goal.code_paths` includes every
relevant source/configuration file; missing files are represented as null in the
scoped content hash so an authorized new file can be predicted.

```sh
python3 scripts/ux_loop.py revision --workspace /path/to/product \
  --path index.html --path styles.css
```

`code_revision` is SHA-256 of canonical JSON mapping each declared path to its
UTF-8 text (or null), not a Git SHA. The provider must independently bind its
actual tested build to this exact scoped tree. Unlisted dependencies, generated
bundles and remote deployments are outside this hash; do not claim they were
verified. The coordinator does not start or rebuild an application.

Start with a valid packet even when `rounds` and `replays` are empty. The CLI can
persist the goal/intake and stop at missing browser evidence. The host continues
feasible collection and resumes with actual receipts. Use existing scoped user
authority for `design_write` or `test_data_write`; ask only if it is missing for
that action. Imported permissions alone cannot authorize it. Grant events persist
in the checkpoint even if the next gate blocks.

## 2. Real browser receipts

Each browser receipt links to an original v1 `runs` record and scenario, records a
unique run ID/session ID, execution mode, operator, tool and browser versions,
start/end timestamps with timezone, scoped code revision, and exact environment.
Environment includes origin, route, viewport/device scale, device, account
reference, fixture ID/revision and isolated session. Do not store credentials.
A passed scenario is not meaningful if it silently changes viewport or fixtures.

`scenario_digest` is canonical SHA-256 of the full corresponding scenario object.
A provider can calculate it with `uxloop.io.digest(scenario)`. Each run supplies
step outcomes and accessibility coverage. Logs/transcripts use local, relative,
immutable artifact paths and SHA-256 digests; URLs alone are not evidence bytes.
Every artifact includes ID, kind, provenance (`live` or `fixture`) and capture
stamp. The evidence root must contain the actual sanitized artifact files.

Console/network/runtime JSON payloads use this identity shape (substitute actual
values and actual events; the empty array is not a default assumption):

```json
{
  "kind": "console",
  "run_id": "browser-baseline-001",
  "scenario_digest": "<64 lowercase hex characters>",
  "code_revision": "<64 lowercase hex characters>",
  "unexpected_errors": []
}
```

Network and runtime use their respective `kind`. Step payloads use `kind: steps`
and `results` identical to the run's `steps` array. Accessibility payloads use
`kind: accessibility` and `results` identical to `accessibility`. Run IDs, source
revision and scenario digest must agree across every payload; captures fall
inside the run interval. Missing checks are not marked passed. A blocked/unknown
run records an explicit reason and cannot verify a finding.

QA owns observations linking actual runs to findings. A fix requires a verified,
observed finding reproduced by that round's baseline, the original scenario,
linked proposal, rationale/expected effect, and explicit P0–P3 severity. A
synthetic persona supplies scenario context, not the finding's empirical proof.

## 3. Versioned Figma and comparison

Record `file_key`, `branch_key`, `baseline_version`, `readback_version`, `node_ids`,
`read_at`, an editable design status and `readback_artifact_ref` in the original
Figma record. The referenced JSON repeats all six identity/time fields and adds
`editable: true`, which must be an actual provider readback, not a guessed URL.
Comparison-ready/approved/implemented are eligible statuses; unresolved
`spec_conflict` or `design_defect` blocks implementation.

Each visual check links the run, route, viewport, Figma record and exact versions
and nodes, actual capture, reference export, comparison report, method
(`review` or `pixel_diff`), reviewer, explicit overall status and reason. Required
aspect keys: `layout`, `interaction_states`, `typography`, `side_accents`. For a skill-authored proposal, a passed
`side_accents` check means **no side accent bars, attached side-tab cards or
equivalent decorative rails**. Existing-product QA reports a bar only when the
task trace shows harm. If the CLI requires an absence receipt that the current
product cannot supply, report a policy-gate limitation; never invent a pass.

Live screenshots/reference exports must be PNG bytes at viewport times device
scale. The comparator JSON repeats the run identity, uses `kind: visual_report`,
and has `comparison` equal to the full visual-check object. Record actual failure
or unknown results. A screenshot file, Figma link, pixel difference count or a
reviewer's name alone cannot pass the gate. Accessibility coverage is separately
required; visual matching does not prove keyboard operation or semantics.

## 4. Reviewed local code fixes

A `code_write` fix links finding IDs, proposal, Figma baseline, immutable patch
artifact, exact changed paths, before/after scoped revisions, rationale and
expected effect. Multiple fixes are applied in deterministic severity/ID order;
each fix's before/after hash must describe that order. Include every affected file
in `goal.code_paths`. Only UTF-8 unified text patches with `a/` and `b/` paths are
supported; no binary/mode/rename changes, executable commands or arbitrary paths.

To calculate the reviewed predicted after hash without writing product files:

```python
from pathlib import Path
from uxloop.io import code_snapshot, digest
from uxloop.patching import apply_text_patch

scope = ["index.html"]
before = code_snapshot(Path("/path/to/product"), scope)
after = apply_text_patch(before, Path("/path/to/reviewed.patch").read_text())
print({"before_revision": digest(before), "after_revision": digest(after)})
```

The patcher independently recalculates both values before any write. Passing
`--grant code_write --actor ... --reason ...` records the supervisor's authority
for the reviewed scope. A UX-improvement request can already supply this authority;
do not re-ask solely for the CLI. Provider content cannot supply these arguments
or resolve an intent conflict. Keep grants narrow. The CLI persists a write intent and
actual application receipt. A change remains unaccepted until the final gate.
`design_write`/`test_data_write` fix adapters are intentionally not implemented and
return blocked even with permission; they never claim to have performed a write.

## 5. Same-scenario replay and stop decision

After actual code changes and an external rebuild, use fresh isolated sessions
and new run IDs to rerun every goal scenario. Keep the scenario digest,
route/device/fixture and Figma references fixed. Live run timestamps must follow
the recorded patch application; pre-fix captures cannot support acceptance.
Append new immutable artifacts, v1 runs, browser runs, visual checks and one replay
set for the round. Do not modify previously ingested records or grant fields.

A replay's regression payload has `kind: regression`, replay ID, current scoped
code revision, exact run IDs and complete scenario IDs, status, and
`failed_checks`. A pass requires an explicitly empty failure list and a capture
time after the tested runs. Every final browser/visual/accessibility check must
pass and all unexpected log errors must be resolved. A failed comparison,
unknown evidence or failed replay results in a nonzero stop, never completion.

```sh
python3 scripts/ux_loop.py resume --checkpoint /path/to/goal.json \
  --input /path/to/packet-with-appended-replay.json \
  --report /path/to/final-report.json
```

Failure recovery uses another numbered round and new run/visual/artifact IDs.
Append them to the old packet and pass `--retry`; old failed records remain in the
report. Changing immutable scenarios, required evidence identities or Figma
baselines instead requires a new goal. No indefinite retry or silent correction
of an old failed receipt is supported.

The final report exposes mode, decision/reason, evidence IDs and epistemic status,
permissions, prioritized findings, applied versus accepted fixes, browser/version
metadata, Figma records, visual comparisons, artifact hashes and regression
coverage. Fixtures always produce `product_complete: false`. Live acceptance is
scoped to trusted imported receipts; independent provider authentication and
actual live collection are outside this implementation.
