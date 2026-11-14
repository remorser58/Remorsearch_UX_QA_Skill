# First completion smoke — preserved setup and evidence-limit failures

Run root: `.ux-loop/peekly-completion-smoke-20261115`.
Started `2026-11-14T15:41:05.164088+00:00`; stopped `2026-11-14T16:04:40.926388+00:00`.
Frozen runtime source was 125b732, launched at documentation revision 02bdd95.
**This run did not produce two valid completed sessions and does not authorize the 32-person cohort.**

## Preserved state

| Persona | Stored queue state | Last durable phase | Interpretation |
| --- | --- | --- | --- |
| 021 | uncertain | turn 2, tool | Seed freshness precondition rejected before storage writes; never resent. |
| 029 | running in the preserved DB | turn 65, tool; 64 admitted observations | Launcher terminated on artifact-list validation. The retained DB row is an interrupted attempt, not a currently running or assessed session. No resume or queue rewrite was performed. |

The launcher is gone and no matching owned main Chrome process remained at the read-only process check. The normal final `report.json` and `stage-summary.json` were not generated, so there is no durable normal browser-shutdown completion receipt to claim. The existing `finally` shutdown path ran during the exception unwind; its source does not persist a summary on this failure path.

Read-only operation counts: 67 completed model operations, 66 completed tool operations, 1 uncertain tool operation, no intent operations. The live router ledger contains 67 actual attempts, all 67 delivery guards `reply_received`; its audit is valid, uncertain resends 0, unsettled model guards 0. The uncertain seed tool remains separate from model delivery counts.

All 32 prior queue snapshots were unchanged. Before/after snapshot map SHA:
`519f7537af1ff08a992c47d8ed70c8828f0b942baf56f9acff2aa3bd375fa15c`.
The full runtime/fixture/library freeze was independently recomputed after stopping and matched. All later fixes are prepared in isolated worktrees.

## 1. Default theme incorrectly rejected by seed freshness check

The actual fresh profile contained the empty default v7 state and `peekly_theme_preference=system`, which the product automatically writes on first mount. The original fresh check required exactly the v7 key and rejected that legitimate default.

The rejection receipt has `initial_storage_match=true`, `status=rejected`, `reload_observed=false`, `migration_validated=false`, and identical snapshot before/after SHA `7b3f3a770f0ac89471a660ccfe9a54f5de96b387ebb22d307e06fadb84f77355`. Seed writes did not occur.

Evidence:
`stage-2/sessions/S-cadepflpaecgloopgfjkohof/evidence/S-cadepflpaecgloopgfjkohof/1/legacy-seed-17-rejected.json`, SHA `598e553de6ae353ec9135088c01611dc310a4c100ccaf4d3c902baa0d682fe4e`.

Full `facts.storage_keys` contains two keys; `storage_snapshot.keys` filters only snapshot keys and contains v7 alone. These inventories have different purposes.

Isolated fix 3b71251 permits only the optional exact default theme, preserves it, and retains the owned-profile, empty-v7, full initial digest, no-prior-mutation and one-shot requirements. Nondefault themes, other keys and concurrent mutation remain rejected. Regression reproduced three failures before the fix; 14 legacy cases and 44 combined Node guardrail cases passed afterward.

## 2. Avoidable History navigation

029 reached actual previous/current imports and the free names list. At obs-51, the Results page already exposed a visible History button. The task forced More navigation; obs-52 had the History entry above the viewport, and obs-53's downward scroll moved page Y 286 → 616.

Isolated fix e85b242 uses the already visible Results entry. Grounded control ordering determines the direction only for the known Results/More layout; unknown layouts and modal backgrounds do not receive guessed scroll directions. The judge requirements remain unchanged.

## 3. 80-turn execution exceeded the old 128-artifact receipt cap

The durable checkpoint had 64 observations and 128 registered JSON/PNG artifacts. The next successful browser tool produced obs-65, but adding its evidence exceeded `swarm._artifacts`' 128-entry limit. The exception propagated before final receipt/report generation.

This is an executor limit, not a product failure or a completed evaluation. The fix must be verified through actual registration of 80 observation logs plus screenshots, final receipt creation, queue finalization and readback. Existing file-size, PNG, path, hash, privacy and per-criterion reference limits must remain enforced.

## 4. Pro feature copy was not recognized by the judge

The unadmitted raw obs-65 shows the actual Pro sheet after the visible Pro explanation button was clicked. The product says “변화를 시간순으로”, “원하는 두 시점 비교” and “한 사람의 관계 이력”. The earlier helper's timeline aliases omit the first label; raw text also contains nonbreaking spaces.

Even normalizing whitespace leaves the old helper at `not_run`. A narrow actual-copy regression and coherent Pro sheet proof are being added. This diagnostic does not retroactively admit obs-65 or score the failed session.

Raw obs-65: `stage-2/sessions/S-jopolnkkaipimlidlnlnjcoh/evidence/S-jopolnkkaipimlidlnlnjcoh/1/agent-observation-65.json`, SHA `ac5f5b57b66c2c041ae5921bce99a42014af7694ff2803dc83227caae593e342`.

## Source hashes and next gate

- `run-status.json`: `d4167f880ae23b3f29c3044c5cb5e173f0ed6c63f8c1c648dd46556280729100`.
- `stage-2/model-router-ledger.live.json`: `47413eba69574d06d20240e6ab89ba9fdb7bf010a869b46b526c3bddb2349654`.

After integrating the isolated fixes and affected regressions, use the fresh root `.ux-loop/peekly-completion-smoke-r2-20261115`. Never resume this root or resend its uncertain operation. Both target flows and all six success criteria must be actually exercised before the cohort expands.
