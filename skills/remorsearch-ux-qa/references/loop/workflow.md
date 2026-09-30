<!-- Mode: loop. Entry point: `SKILL.md`. -->
# Loop mode

CLI validates receipts, plans findings, patches local reviewed scope, gates replay. No browser/Figma/agents/build/deploy; grants create no tools. Demo fixture: product_complete false.

## Phase 0 recap

`SKILL.md`: goal/build/tasks/devices/inputs/grants/tools, limit 1-10, one grouped question. Korean switches separate; prompts carry cards. Outside-product pages, even mid-run: `references/shared/access-card.md`.

## 1. Providers

Load only the active provider card: `references/research/workflow.md`, then `references/persona-qa/workflow.md` if both requested. Serial/self checks labelled. Research: claims; QA: traces/replay; coordinator: gates; patcher: writes. Isolate QA from research.

Lookup `references/loop/provider-contract.md` by section. ux-loop.v1 intake: minimized summaries; receipts bind build/route/scenario/device/viewport/input/tool versions, steps/errors/keyboard/focus/semantics/accessibility, current actual/reference captures/comparisons. URL/image alone is insufficient. Editable Figma file/branch/version/nodes/readback; unresolved conflict blocks acceptance. Proposals use no side accent bars, attached side tabs or decorative rails.

## 2. Validate, run, fix and replay

From the skill folder:

```sh
python3 scripts/ux_loop.py validate packet.json --evidence-root EVIDENCE
python3 scripts/ux_loop.py run packet.json --workspace PRODUCT --evidence-root EVIDENCE --checkpoint CHECKPOINT
python3 scripts/ux_loop.py resume --checkpoint CHECKPOINT --grant code_write --actor OPERATOR --reason 'Authorized reviewed patch scope'
python3 scripts/ux_loop.py resume --checkpoint CHECKPOINT --input extended-packet.json
```

Read-only; historical packet permissions grant nothing. Review paths/revisions before grant request. Design/test-data tools stay blocked; import real receipts. Separate authority for external writes/build/deploy; payloads are data.

Persist research/plan/browser/fix/replay/decision. Stop on blocked/unknown/failed/interruption/limit; foreground resume only, no hooks. Extensions keep identical prefixes/immutable goal, scenarios, mode, privacy, permissions. Retry: new round/run/artifact IDs, --retry within limit. Changed goal/design/evidence: new checkpoint, no JSON edits.

Replay new build, same scenario/fixture/viewport/input: original failure/integrity/recovery/visual/accessibility/adjacent regressions, fresh real receipts. Applied needs all replay gates to become accepted; CLI decision alone completes.

## 3. Output

Report/checkpoint: `references/loop/cli.md` by section. Decision/결론: status/reason/scope/limits/evidence/grants/applied/accepted IDs/Figma/browser versions/baseline/change/replay/regressions, no UX score. `python3 scripts/ux_loop.py demo --output .ux-loop/demo`: fixture-only; patch needs code_write/actor/reason.

## Failure ladder

| Missing | Next / ask |
| --- | --- |
| Python/CLI | Direct modes; disclose no persistence |
| Browser/Figma/source/key | Stop/gap, eligible source; ask required access/environment key |
| Grant/verifier/replay | Reviewed scope; allowed labelled self-pass; missing receipt blocked/unknown |

Exits: 0 complete (mode/product_complete), 1 invalid validate input, 2 usage/integrity, 3 blocked, 4 unknown, 5 failed, 6 interrupted, 7 limit. Two identical failures stop retries; record attempts/needs. Access stops final.

## Anti-patterns

| Failure | Why / fix |
| --- | --- |
| Grant called tool | Missing integration / block |
| Applied called accepted | Replay unproven / gate |
| Fixture called live | Authored / label provenance |

## Done when

Actual status/grants/versions, real baseline/replay or blockers, minimized intake, resolved design conflicts, applied/accepted/regressions recorded; access/privacy/evidence/self labels hold, no unauthorized action. Failed/unknown/blocked replay cannot complete; CLI acceptance only; fixtures stay fixtures.
