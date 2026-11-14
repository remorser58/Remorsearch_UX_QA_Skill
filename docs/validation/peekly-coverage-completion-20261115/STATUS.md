# Peekly coverage completion — durable status

Updated: 2026-11-15 (Asia/Seoul).

## Authorized goal

From verified `65f52f78918d097c39ac8eb5ec49ed6daea537bc`, implement a validated legacy-state seed, prove actual coverage with a fresh two-person smoke, then run all 32 saved personas in a new background cohort. Use only `TOKENMAXX/deepseek-v4.1-flash-free`, concurrency 2, zero paid fallback, and never resend an uncertain operation.

The user authorizes implementation, regression, owned isolated test contexts, smoke/cohort, reports, commit and push. Product `51110f4` remains the fixed target. Preserve all old queues, receipts, fixtures, and uncertainty.

## Workspace and baseline

- Approved root: `/remorsearch-ux-qa`.
- Worktree: `.worktrees/peekly-ux-findings-20261113/.worktrees/peekly-verdict-quality-20261113`.
- New branch: `rem/peekly-coverage-completion-20261115`.
- Base local/remote SHA and clean tree verified: `65f52f78918d097c39ac8eb5ec49ed6daea537bc`.
- Prior reviewed report: `docs/validation/peekly-coverage-20261114/reviewed-summary.json`, SHA `f803cd44fcad79d203c826d36ee2f8e1409538e6f67ae06a240e8c634c21b4dc`.
- Prior 32: 29 complete / 3 uncertain; sessions 9 passed / 8 failed / 12 inconclusive.
- Prior criteria: success 62 / 8 / 22 / 0; recovery 9 / 0 / 1 / 19; all 71 / 8 / 23 / 19 (passed / failed / not_run / N/A).
- The old uncertain 009/010/012 remain preserved. The new requested cohort uses new jobs and call IDs.
- Original 46 weighted mapping at 65f: 20 passed / 8 failed / 18 not_run; 32 unique mappings: 13 / 6 / 13.

## Current phase — isolated R2 ready for fresh actual smoke

- Host/tool recovery confirmed on 2026-11-15. Git and ordinary file access respond normally. The pending nine-file change set is intact on `a360b85`; no R2/cohort directory or active completion launcher was present. The earlier smoke-start wrapper failed at its first import before spawning a child; it created no model/browser operation.
- Recovery verification: 61/61 regression tests passed again (0.545 seconds, no skip/failure); normal CLI preflight passed with 33 preserved queues / 329 old job IDs / 40 old uncertain rows. Actual archive/library freeze and six-file HTTP verification passed again. Proceed with the already authorized fresh smoke, then cohort only after the gate; do not resend any old uncertain request.
- Source/library isolation is complete. The 61-case target/launcher/finalizer regression passed; independent review reran 36 of those cases and found no blocker. Actual HTTP index plus five entry assets match the new pins. See `pinned-target-validation.md` and `pinned-inputs.json`. No R2 or new 32-person run has launched at this checkpoint.
- Use new roots `.ux-loop/peekly-completion-smoke-pinned-20261115` (R2) and `.ux-loop/peekly-completion32-pinned-20261115`. These replace the earlier planned `smoke-r2`/`completion32` names; no old result is overwritten.

- R1 ended `2026-11-14T16:04:40.926388+00:00` with `stopped_preserved`: 029 reached tool turn 65 and exceeded the old 128-artifact receipt cap. Its DB row remains interrupted/running with 64 admitted observations; it is not a valid completed session. No resume or queue rewrite.
- Normal report/stage-summary files are absent. Launcher PID 24410 and matching owned main Chrome processes are gone; no normal browser-shutdown completion receipt is claimed.
- Live ledger: 67 actual requests, audit valid, all reply_received, 0 uncertain resends, 0 unsettled model guards. Separate tool uncertainty: the pre-write seed rejection. Prior queues and runtime/fixture/library hashes remained unchanged.
- Detailed evidence, hashes, actual Pro copy mismatch and navigation cause: `smoke-r1-diagnostics.md`.
- Ready isolated commits: theme `3b7125119d884cc6070912e23247b775fb13e72b`; conditional safe SAVE-FAIL recovery `d9493da718959f0d87bd8fefba9c20d641923e78`; grounded History navigation `e85b242c80199b454d48d2f466fad27e4d683aa4`.
- Main integrated theme `a0f20bd`, safe recovery `f1641da`, History navigation `90ed8ea`, shared 256-artifact budget `7554298`, and actual Pro-copy/visible-sheet judgment `2e41a0b`. No R2 or 32-person run has launched.
- Artifact regression now completes 80 real tool observations with 240 registered JSON/PNG artifacts through receipt preview, Queue finalization and current-report revalidation; 39 affected tests passed, 256/257 boundary and all existing byte/hash/path/privacy/reference caps enforced.
- The merged source `2e41a0b` passed all 245 affected regression tests, with no skips or failures (72.098 seconds). Log: `.ux-loop/peekly-completion-r2-regression-20261115.log`, SHA `6043c3058727ecf396a106653c3d99e5986b90965d64dc4d305bbe8613d31b5a`. The rebuilt 282-file bundle verifies with zero problems, payload SHA `44185f5a989a39b054278a9da407c194e89bd6535da9c173e9dd31405b70688e`; the earlier Node 22 release limitation is still unresolved.
- R2 preflight then correctly refused all 32 saved personas with `stale_prd`. Another task changed the original product worktree after R1 stopped: `src/App.tsx` at 01:12:13, `docs/PRD.md` at 01:17:39, and `dist/index.html` at 01:19:35 (2026-11-15 Asia/Seoul). R1 stopped at 01:04:40. The old 4174 preview now serves index SHA `b5911db7d651e3c68dca42233427cf0e2baef11971f92280d266ea427b14bce3`; its unchanged old build manifest still claims `848b334a6affa5c6a578911819aaf127da34bc2e6ae2f04899022872b7d0f6f5`.
- Preserved that other task's product files and server. Created a separate archive of product commit `51110f4c569673faa8d242d5b85c4b47afb54cbb` under `.ux-loop/peekly-pinned-product-51110f4-20261115`, built from a private copy of prepared local dependencies, and served it on owned port 4175 (PID 78876). The new public-API-imported library `.ux-loop/peekly-persona-library-v4-pinned-20261115` has 32/32 reusable revision-1 personas, unchanged profile contents/criteria/citations, and only the PRD path rebound. The old library and its stale-binding gate remain unchanged.
- Archive verification has matched all 319 tracked source file Git blob hashes. The archived PRD SHA is `a014a85b7523928f693cd4422793929631f033176715f31409412e95e1d7432b`. New launcher gates must bind archive provenance and actual served index/assets rather than infer a product Git HEAD from the nested archive directory.
- NEW R2 root: `.ux-loop/peekly-completion-smoke-pinned-20261115`. After its successful gate the 32 launch must use that same smoke root; it is now the launcher's default. Freeze all runtime, fixtures, library, source and dist bytes through both stages.
- Durable post-run reporter/publisher is implemented in new `scripts/finalize_peekly_completion.py`; 14 offline tests pass, and the real prior 716-request ledger passes its free-route/no-resend validation. It has not been started. It preserves raw/unreviewed labels and only publishes the five owned generated documents after terminal integrity gates.

### R1 launch checkpoint (historical; superseded by stopped state above)

- Published pre-run HEAD: `02bdd95cd9817af396e11036c8386b37a805c6aa`; exact remote SHA verified.
- Actual smoke started `2026-11-14T15:41:05.164088+00:00`, launcher PID 24410. Root: `.ux-loop/peekly-completion-smoke-20261115`.
- 021 job `S-cadepflpaecgloopgfjkohof`: uncertain at turn 2, `host_execution_failed:browser_action_failed:legacy_seed_profile_not_fresh_owned`. No resend or resume.
- 029 job `S-jopolnkkaipimlidlnlnjcoh` was running at the earlier turn-15 checkpoint. It later stopped at the artifact limit described above.
- Exact seed failure: product startup stores the default `peekly_theme_preference=system`. The guard required only the empty v7 key and rejected this legitimate default preference. Initial storage matched; seed status rejected before storage write, before/after snapshot digest identical; reload/migration were not attempted.
- Full `facts.storage_keys` includes v7 plus the theme preference; filtered `storage_snapshot.keys` includes only snapshot keys. Do not confuse those two inventories.
- A separate worktree `.worktrees/peekly-seed-theme-fix-20261115` on `rem/peekly-seed-theme-fix-20261115` is preparing the minimal fix/tests. Main runtime remains byte-identical while 029 runs. Allow only optional theme preference exactly `system`, preserve it, keep empty-v7/full initial digest/owned-profile/no-prior-mutation/one-shot checks, deny other values and keys.
- After this stage is terminal: audit and preserve it; integrate the reviewed fix; use a NEW smoke result root. This failed two-person gate does not authorize cohort expansion.
- Isolated fix ready: `3b7125119d884cc6070912e23247b775fb13e72b`, driver + Node tests only. Exact failed storage reproduced 3 failures before the fix; 14 legacy Node cases and the 44-case combined guardrail/scroll/legacy suite passed afterward. Main runtime has not yet integrated it while 029 is running.

### Implementation baseline before R1

- Runtime source revision: `125b7325ed60cdafa52546fee39492cb0279a3ce`.
- Full discovery: 1,834 tests, 1,813 passed, 21 optional skips, zero failures. Prepared agent runtime separately passed 25/25 without skips.
- Release checker passed 18/20 entries; ready=false because default Node 24 fails the packaged Node 22 gate and its Playwright check was skipped. This does not establish release readiness. See `implementation-validation.md` for exact commands and hashes.
- Loop smoke 18 expected outcomes and research fixture passed with no network requests. Actual Peekly CDP behavior will be evaluated in the new smoke.

- New smoke: `.ux-loop/peekly-completion-smoke-20261115`.
- New 32: `.ux-loop/peekly-completion32-20261115`.
- Launcher: `scripts/run_peekly_completion.py`; offline report: `scripts/report_peekly_completion.py`.
- Smoke personas: 021 (UNKNOWN) and 029 (PAYWALL). Their matched baseline has 2 not_run among 6 success criteria.
- Gate requires two valid complete sessions, both target flows with actual evidence, all 6 success criteria executed, no success N/A, no uncertain delivery, free route only, confirmed browser closure and unchanged prior queues.
- Source/fixture/library freeze is checked before and after both stages and must match between smoke and 32. Failed smoke roots are immutable; fixes require a fresh root.
- Offline launcher preflight passed: 32 prior queues, 327 forbidden old job IDs, 39 preserved historical uncertain job rows.
- Served local preview SHA: `848b334a6affa5c6a578911819aaf127da34bc2e6ae2f04899022872b7d0f6f5`, matching the pinned build.
- Applicable AGENTS.md read; PRD/HANDOFF/release docs were previously read and verified unchanged from 43e3b14 to 65f52f7.

## Remaining 23 and changes

| Cause | Criteria | Change |
| --- | ---: | --- |
| Imported relationship lists not visited, 017–020 | 12 | Imported-data checklist plus bounded final-response continuation |
| No valid legacy UNKNOWN setup, 021–024 | 4 | Validated v6 seed, real product migration and readback, actual exclusion proof |
| PAYWALL downstream stages not attempted, 029–032 | 4 | Same-pair import/comparison/locked selectors/Pro sequence; ARIA labels; 80-turn ceiling |
| SEARCH025 actual query absent | 1 | Explicit actual search action, pinned search fixture, continuation |
| IDENTITY022 comparison explanation unreached | 1 | Actual departed-list control and comparison pair reused |
| RECOVERY013 direct retry unavailable | 1 | Preserve direct-retry product failure; after a confirmed consumed/restored fault only, exercise ordinary reselect/reimport recovery once; no uncertain resend or N/A credit |

The reference to 3 legacy UNKNOWN prerequisites was the repeated original-46 mapping; the prior whole-cohort remaining-23 set has 4 UNKNOWN criteria. Both mappings will be retained.

## Validated seed and fixture freeze

- New immutable catalog: `.ux-loop/peekly-coverage-fixtures-v8-20261115`, 544 files.
- Manifest SHA: `9654fa6b07da5d443fbc97df16ab8885e170084ceda23399a36fbbd721997941`.
- All 543 v7 fixture bytes/hashes remain identical. One legacy-state JSON was added.
- Seed SHA: `f4ea8b627d7b305552cf326205096aa244cf40a873fcbf275807947feec1a6f5`.
- Actual-product validation SHA: `8812e073064029937aaecb1908d0301eff96c2bee8794e3ee8ec6a6ddc46871c`.
- The real path is `peekly_state_v6` → pinned `loadPersistedState/normalizeSnapshot` → v7. It derives UNKNOWN and infers includedFiles; current-schema v7 cannot be seeded by inserting malformed legacy fields.
- `seed_legacy_unknown` accepts only the pinned allowlisted fixture, only an UNKNOWN task, only a fresh host-owned synthetic context, and only once. Existing state, nonfresh contexts, changed hashes and second applications fail closed.
- Driver saves before/after storage digests, reload and migration proof. First observe now truthfully supplies `last_action=observe`.
- UNKNOWN order: seed first → one current import → visible comparison exclusion → ordinary previous/current pair for other criteria.
- Seed alone cannot pass UNKNOWN. The actual later import, exact legacy/current state and visible exclusion are required.
- Current imported rows may legitimately have null optional listCompleteness while includedFiles proves known data; legacy remains explicitly UNKNOWN.

## Execution and judgment controls

- All ordinary Peekly tasks: at most 64 model turns. RETENTION + PAYWALL tasks 029–032: at most 80. Lower approved ceilings remain effective.
- Exactly 28 tasks use 64 and 4 use 80. After the R1 task corrections, all 32 launcher goals were privacy-clean and <= 8000 characters; maximum 7359. The new pinned-source/library preflight must recheck the final configured goals.
- A known completed final response may be continued only when native normalization leaves a targeted criterion unattempted and a currently observed safe next action exists.
- The original final stays in the operation ledger. Continuation uses a new normal turn/call ID, at most 2 per criterion and at most once per unchanged page.
- Actual failures, disabled controls, repeated no-movement scrolling, rejected actions, time limits and uncertainty are preserved. Conditional recovery is never forced.
- PAYWALL proof requires actual same previous/current pair, real names/comparison, both locked date selectors and a coherent Pro feature sheet. ARIA labels are admitted; loose text-only claims remain not_run.

## Regression completed before integration

- New seed Python suites: 24 pass (6 seed, 3 host guardrail, 15 fixture builder); guardrail includes the new 9-case Node seed suite and prior guardrails.
- New criterion scope: 19 pass; saved evidence scope: 67 pass; verdict: 25 pass; scale execution: 12 pass.
- Completion guard: 9 pass, including actual SQLite ledger preservation, fresh call IDs and uncertain continuation no-resend.
- Launcher/checkpoint boundary: 9 pass; prior launcher: 18 pass.
- Prepared optional agent environment: 25 / 25 pass with `REMORSEARCH_REQUIRE_AGENT_RUNTIME=1 .ux-loop/peekly-agent-venv/bin/python`.
- Offline actual-product load/save oracle plus driver-readback → host → agent admission → native guard integration passed. This is synthetic/offline validation, not actual UX improvement.
- Comprehensive check completed on source 125b732; full results and explicit Node 22 limitation are recorded in `implementation-validation.md`.

## Completion still required

1. Commit/push the verified pinned-source launch checkpoint; source/library/build preparation and served-asset pre/post gates are complete.
2. Fresh actual two-person smoke; inspect seed and PAYWALL evidence before expansion.
3. Only after passed smoke, launch fresh 32 once in background and monitor with short read-only checks.
4. Terminal raw aggregation, full byte/seal/source/ledger audit, independent semantic review. Compare pinned remaining 23 and original 46 without N/A or unassessed credit.
5. Update historical comparison, STATUS and findings, commit/push, verify exact remote SHA and clean worktree.

Historical r1 had five uncertain resends and remains disclosed. The preceding final 32 had zero. New runs must independently verify zero; no lifetime-zero claim.
