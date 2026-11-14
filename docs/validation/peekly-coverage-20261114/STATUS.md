# Peekly coverage follow-up — durable status

Updated: 2026-11-14 (Asia/Seoul).

## Goal and scope

Reduce the 46 success-criterion not_run records in the ee4b145 r4/r6 completed-session baseline. Preserve raw evidence, uncertain operations and saved persona identities. Fix runner/task/fixture causes, run meaningful regression, then a two-person smoke. Expand to a fresh unique-32-persona background cohort only after smoke demonstrates less not_run coverage. TOKENMAXX free route only, concurrency 2, no paid fallback. Never resend an uncertain operation.

## Workspace

- Approved root: /remorsearch-ux-qa
- Worktree: .worktrees/peekly-ux-findings-20261113/.worktrees/peekly-verdict-quality-20261113
- Current branch: rem/peekly-coverage-20261114
- Base and original remote verified: ee4b14571930af428d5a52e0e133deebedba485d
- Product/PRD: existing owned Peekly build 51110f4; do not change product UX in this runner-focused task.

## Completed

- Baseline/remote/clean state verified; new branch created.
- Baseline: 24 complete sessions / 15 unique personas; UX 1 passed, 6 failed, 17 inconclusive; success criteria 28 passed, 6 failed, 46 not_run; recovery 7 passed, 17 N/A.
- Exact 46-row cause audit is saved in not-run-baseline.json/md: task/precondition/screen not reached 27; loading follow-up absent 1; storage fault harness absent 4; retention catalog absent 5; search fixture absent 4; account mismatch 2; NBSP rejection matching false negatives 3.
- Progress/cancel and occluded-click failures are outside the 46 not_run denominator; keep that distinction in comparisons.
- Runner implements occlusion/visibility checks, actual bounded active-import cancellation and isolated one-shot snapshot save failure with storage digests. Criterion checks bind actual action, fixture and attempt; stale success text or later unrelated actions cannot prove success.
- Task plans include per-criterion mandatory steps, correct sample/import/delete ordering, 64 bounded turns, compact historical prompt observations and completed-receipt-only totals.
- New immutable fixture directory: .ux-loop/peekly-coverage-fixtures-v6-20261114. Manifest SHA256: 2465e11c1b6f66553a8caa5851b42bef2b328a46b1aa6e5a24ff01ac8d1dd8d2. 543 registered files; 11 distinct retention snapshots; search category12/filtered1; compatible empty/current and previous/current account pairs.
- Progress archive is 110401587 bytes of recognized relationship JSON (600000 follower rows/200000 following rows), not inert padding. SHA256: 9e8d5cc5ee96635d281704937f5d2cc3d7b0e3652763a11c6a076157b092d52b. No processing-time guarantee.
- Full unittest discovery completed: 1651 tests, 1630 passed, 21 optional dependency skips, zero failures, 148.913s. Log .ux-loop/peekly-coverage-regression-20261114.log; SHA256 e0f2f7a876cbd8ad3202873c2f44f51b0f74acdb3604324046dd0a33171e9114.
- Final focused integration completed: 46 passed (verdict25, criterion evidence18, driver3 including16 Node behavioral checks); log .ux-loop/peekly-coverage-integration-20261114.log. Launcher12 offline tests also passed.
- Actual launcher offline preflight passed: 27 existing queues, 287 forbidden distinct job IDs, 36 historical uncertain job rows; all543 fixture byte/hash pairs and all32 reusable saved persona IDs verified. No model/browser calls occurred during this preflight.
- Owned preview HTTP200 and served/local index SHA256 both match pinned artifact: 848b334a6affa5c6a578911819aaf127da34bc2e6ae2f04899022872b7d0f6f5.

## Work in progress

- Root: implementation commit/freeze and run orchestration.
- Driver reviewer: launcher complete/frozen; scripts/run_peekly_coverage.py smoke or cohort, optional offline --check-only, fresh folders only.
- Task reviewer: implementation complete; no further edits.
- Cause reviewer: offline report aggregation and comparable baseline mapping.

## No execution launched yet

No smoke or cohort is running from this change. Before any run, finish changes/regression, freeze exact engine/tool/fixture hashes, create a fresh output folder and reviewed budget/route plan. Do not resume or edit old r4/r5/r6 queues.

## Next checkpoints

1. Finish launcher and full regression; record exact commands/results and implementation commit.
2. Freeze engine/driver/fixture hashes and prove past uncertain operations remain unchanged.
3. Launch smoke personas016/029 as a detached background process; latest r6 same-person baseline has3 success not_run. Expansion requires2 valid complete receipts, no host_protocol, zero success N/A and fewer than3 success not_run.
4. If completed receipts demonstrate not_run reduction, launch fresh32 once, preserve every uncertain send; periodically inspect.
5. Update four-column comparison, report commit/push, verify remote SHA and clean worktree.

If interrupted, read this file and the durable queues before doing anything. Existing uncertain operations are never replayed; completed outputs are read back. No authorized live model execution has started as of this checkpoint.
