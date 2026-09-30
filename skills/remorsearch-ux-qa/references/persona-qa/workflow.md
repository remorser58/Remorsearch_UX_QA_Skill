<!-- Mode: persona-qa. Entry point: `SKILL.md`. -->
# Persona QA mode

Test whether each priority task completes with its entered data intact. Synthetic scenarios test conditions; product traces establish failures. Community research requires a user request.

## Phase 0 recap

Use `SKILL.md` Phase 0. Record URL/app/build/tasks, device/viewport/input, criteria/constraints, Figma version, grants and test identities. Choose smoke/persona/heuristic/visual/regression/deep; community is separately requested. Sufficient brief: no question; missing material input: one grouped question. No dataset/audience blocker: brief conditions are first-class.

Before scenarios, disclose Chromium viewport/DPR/input emulation limits: no real device/grip/keyboard occlusion/safe area/screen reader; repeat in report. Korean product: `references/persona-qa/kwcag-card.md`, no platform map; report language: wording/headings only. Outside-product pages, even mid-run: `references/shared/access-card.md` in persona/verifier prompts. Host browser first, preserve tabs/context; authorized-product rules govern local QA.

## 1. Build the priority-task matrix

For every priority task, require all these rows on each device in scope:

| Path | Required checks |
| --- | --- |
| Happy path | Enter all choices/values; compare with final state/payload |
| Required omissions | Leave each required choice or field out separately |
| Validation | Exercise each validation error with safe test data |
| Recovery | Back, return, rerender and each coupon/address/error transition |
| Keyboard only | Whole primary task, including intermediate choices and recovery |
| Reading order | Each intermediate screen's meaningful sequence and focus order |

After **every step**, verify all prior values/choices persist correctly. Failed submit: focus at first invalid field, field marked invalid, error associated. Success means task integrity: every option/quantity/amount/note reaches final state, not a success string alone. Each row: pass/partial/fail/untested with reason; inaccessible/gated rows are gaps.

Scenario: ID/task/goal/safe data, basis/brief condition, context/constraints/device/input/start, expected decision/integrity/risk, claim IDs and omissions. Audience rows cite audience_id/segment_id/task_id/facet and gate-supported motivations. Without an audience, choose task-changing strata: new/returning, touch/keyboard, interruption, delay, empty/stale/edge data. Do not add demographic decoration or stereotype behavior.

Optional dataset: exact source/revision/schema, bounded/streaming sample; record adapter/schema fingerprint/seed/config/shard/read-byte-time bounds/IDs/strata/stop. Separate original attributes/assumptions. Scenario detail: `references/persona-qa/persona-scenario-design.md` by section.

## 2. Exercise and capture

Exercise actual product/input/start state; capture decisions/recovery, console/network/runtime errors, keyboard/focus/semantics and feedback. Screenshots support the trace; available interactions require flow evidence.

Bundled fallback (Node.js 22; detect installed dependencies first):

```sh
node drivers/web/ergo_drive.mjs devices
node drivers/web/ergo_drive.mjs init --url URL --device DEVICE --task TASK --out sc.json
node drivers/web/ergo_drive.mjs serve --scenario sc.json --device DEVICE --agent-json agent.json --out runs/ --port 9477
node drivers/web/drive_client.mjs --port 9477 observe
node drivers/web/drive_client.mjs --port 9477 act '{"action":"tap","target":"#control"}'
node drivers/web/drive_client.mjs --port 9477 note '{"intent":"Complete the task","expected":"Entered values survive","observed":"Describe the screen","confusion":false}'
node drivers/web/drive_client.mjs --port 9477 finish '{"success":false}'
```

Use real targets/outcome; agent.json records actual operator/model/input_channel. **Blind touch:** screenshot-only decisions before DOM/source/run data. Then separate a11y or screenshot+a11y technical auditor reproduces transitions with provenance. After each step/failed submit:

```sh
node drivers/web/drive_client.mjs --port 9477 inspect
```

Inspect returns values/choices/invalid/error association/focus/reading order; link receipt to screen/step. Screenshot channel refuses inspect; no DOM knowledge in blind pass. Programmatic evidence cannot stand for assistive-tech speech. Scripted replay: `node drivers/web/ergo_drive.mjs run --scenario sc.json --device DEVICE --out replay/`, recorded steps/integrity criteria. Driver success cannot override data loss.

Budget a bounded task matrix, no population download; driver run/idle default 900 s. Stop missing access/unsafe action. Separate authorization for posting/purchase/signup/account/data changes. Production identity/SMS/CAPTCHA/security-keypad/certificate/payment gates stop; only approved staging mocks/test payment can complete. No real government/contact/payment/account inputs. Team-approved origins govern widgets; unavailable iframe/popup/app-switch evidence is untested. Lookup `drivers/web/README.md` options/sandbox by section; no installation to pass blocks.

Write a receipt beside **each capture during the run**:

```text
{artifact_path, sha256, captured_at, surface_url, build_id, device, quoted_ui_text}
```

Build ID is commit/version/deploy ID or page hash. Check file/type/viewport, redact private data and quote exact visible UI text. Every P0/P1 receipt must be newer than run start; stale/missing receipts leave it unverified.

## 3. Conditional evidence and intended experience

Only requested community research enters `references/research/workflow.md` with access/evidence cards. Use `references/persona-qa/community-to-test.md` by section for conversion; supported_high/medium may motivate P0/P1, single_voice/lead_only are exploratory. Missing gate means manual unverified assessment. This affects community motivation only; product failures keep impact-based severity. No raw community text reaches personas.

Inspect Figma/spec entry/journey/hierarchy/content/units/variants/tokens/critical states/responsive/input. Record file/branch/baseline/readback/nodes/time/artifact. Differences need task/comprehension/trust/accessibility/maintainability impact. Separate implementation_defect/design_defect/spec_conflict/approved_deviation; unresolved conflict blocks code acceptance, missing source limits comparison. Proposals: no side accent bars, attached side tabs or decorative rails; existing product bars require task harm.

## 4. Grade, trace and second-pass

Severity: `references/persona-qa/evidence-and-severity.md` by section, impact-based. Reproduced input loss/inaccessible required control can be P0/P1 for blocked/corrupted task. Synthetic confusion stays P2/P3 under caps; preference stays hypothesis. No audience/gate downgrade of observed harm.

Finding: ID/severity/rationale; build/screen/device/viewport/input; persona or scenario/task; steps from start URL; expected and observed with visible UI quotes; capture receipt; user/product impact; verified/inferred cause; fix layer/change/trade-off; standards for accessibility only; second pass; confidence. Consult `references/shared/causal-chain.md` for every P0/P1; unknown organizational constraints remain unknown. Never use as any, @ts-ignore or @ts-expect-error in remediation.

Every P0/P1 requires a second pass over only its capture and text dump, without the draft (at most three priority scenarios):

```text
{finding_id, reviewer: subagent|self, task_completed, control_name,
 omitted, severity: agree|disagree, inconclusive}
```

Without subagents, run a labelled self-pass; it is not independent review. Resolve every disagreement in writing before finalization. Unreadable artifacts require recapture or inconclusive status. Korean accessibility findings have separate KWCAG 2.2 and WCAG 2.2 item/status/coverage; lookup mappings in `references/persona-qa/kwcag-2.2.md` by ID.

## 5. Remediate, replay and report

Propose the smallest useful change in copy, interaction/state, IA, hierarchy/tokens, accessibility, service policy/trust or persistence/system behavior. Each states expected behavior, trade-off and validation; benefit claims need measurements. Writes need their separate existing grants. After any fix replay the same scenario/data/build scope/device/input, original failure, primary task, recovery, adjacent states, Figma alignment and accessibility/content. Record baseline/change/replay artifacts; applied is not accepted until replay passes.

Use `references/persona-qa/qa-report-template.md` by section. First heading after title is Decision/결론: verdict/reason naming build; up to three actions, each at most 25 words with behavior, finding IDs and confirming state; one line untested. Verdict rules:

- hold: verified current P0, primary task completed by no scenario, or primary P1 without workaround.
- ship after fixes: no P0; primary task completes; P1s have concrete fixes.
- ship: primary and recovery exercised on every scoped device/current build, no P0/P1 left.
- inconclusive: unavailable surface, production gate, coverage minimum missing or stale evidence. No findings alone never means ship.

Then matrix/basis, ranked cards, P0/P1 causes, recommendations, Figma/artifacts/replay/unverified/next evidence. Community/access annex only if run; omit zero stops. Emulation/AT/identity/payment limits explicit; language adds no research administration. Reusable artifacts: `references/research/evidence-bundle-contract.md` by section (persona copy exists); verified findings link observed observations/completed runs/scenarios. Record separate read/write/blocked reasons.

```sh
python3 scripts/validate_bundle.py bundle.json
```

## Failure ladder

| Missing/failing | Next step; ask boundary |
| --- | --- |
| Browser/build | Highest available fallback; if denied/unavailable, named blocker and inconclusive. Ask only for access needed to exercise the task. |
| Dataset/audience | Brief-derived synthetic conditions; continue QA, no invented participants. |
| Community source/key | Only when requested: obey final stops; use other families. Ask for environment key only if needed and not already declined. |
| Figma/verifier | Conditional comparison; labelled self-pass. Ask for missing required design decision or independent/human verification. |
| Coverage/time | Finish bounded rows, list untested ones; minimum unmet means inconclusive. |

## Anti-patterns

| What goes wrong | Why | Fix |
| --- | --- | --- |
| Success banner passes | Input may be corrupted | Compare entered values to final state |
| One generic recovery row | Misses distinct omissions/errors | Required matrix, checks after every step |
| Touch looks accessible | Keyboard/order/error association differ | Whole keyboard task and auditor pass |
| Persona says “confused”, graded P0 | Judgment cannot prove harm | Separate reproduced behavior and capped judgment |
| Korean QA loads channel atlas | Unrequested research | KWCAG card only |

## Done when

Surface exercised or exact blocker stated; matrix meets coverage or verdict is inconclusive; synthetic/real evidence and blind/auditor provenance are separate; every priority finding has fresh reproduction evidence, impact rationale and labelled cause; every P0/P1 has second-pass record and resolved disagreement. Community motivation is gate-supported or exploratory, tools/context authorized; critical states/accessibility considered; Korean standards/status/coverage and untested gates separate. Reusable bundle validates; report names build, limits, untested scope and replay outcome. No unauthorized side effect occurred.
