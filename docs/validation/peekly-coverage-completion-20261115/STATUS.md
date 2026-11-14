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

## Current phase — integration complete; fresh actual smoke next

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
| RECOVERY013 direct retry unavailable | 1 | Preserve observed product blocker; no forced pass or N/A credit |

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
- Exactly 28 tasks use 64 and 4 use 80. Actual launcher goals: all 32 privacy-clean and <= 8000 characters; maximum 7053.
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

1. Finish source commit and comprehensive integration check; record revision, commands, failures and skips.
2. Fresh actual two-person smoke; inspect seed and PAYWALL evidence before expansion.
3. Only after passed smoke, launch fresh 32 once in background and monitor with short read-only checks.
4. Terminal raw aggregation, full byte/seal/source/ledger audit, independent semantic review. Compare pinned remaining 23 and original 46 without N/A or unassessed credit.
5. Update historical comparison, STATUS and findings, commit/push, verify exact remote SHA and clean worktree.

Historical r1 had five uncertain resends and remains disclosed. The preceding final 32 had zero. New runs must independently verify zero; no lifetime-zero claim.
