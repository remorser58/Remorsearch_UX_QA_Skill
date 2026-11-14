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

## Current phase — R6 independently passed; fresh 32-person cohort running

- R6 finished at `2026-11-14T20:46:51.072684Z` (05:46 Asia/Seoul), `smoke_passed`: two current-valid completed sessions, six passed success criteria, zero success not_run/N/A and zero uncertainty. The matched two-not-run smoke baseline is now zero. The separate 32-person cohort started after the independent gate audit described below.
- Independent gate audit at `20:49:36Z` confirmed all 152 registered artifacts / 4,177,050 bytes, receipt/checkpoint/result/first-judgment seals, all 159 request/reply seals and the 325-event chain. All 17 runtime files match frozen provenance and `f50d082a197e683b5961d17919fe219dc48c4d55`; 37 prior queues, fixtures, library, product source/dist and six HTTP before/after receipts match. Both owned groups closed normally; the process inventory is empty. All 81 model attempts received replies on the approved free route, with zero repair/fallback/uncertain resend.
- UNKNOWN seed/current/exclusion and PAYWALL A/B/C were actually exercised. For 032, a committed final at model turn 60 left PAYWALL incomplete; the bounded completion guard directed a grounded scroll to the offscreen Pro control, followed by actual observations 61/62 and final acceptance at turn 63. This is new live evidence for the previously offline-only completion continuation, not a replay of an uncertain call.
- Raw R6 receipts remain unchanged. Independent review supports the six success passes and corrects 024 recovery from N/A to passed: both invalid-list imports were rejected with saved state intact, then a valid import persisted new state. The actual 024 reverse-direction comparison supports its scoped IDENTITY pass; the prescribed current-fixture direction was not retested there. DOM/capture visibility limits and the separate 032 causal-label finding are retained in the independent review.
- The fresh 32-person preflight passed with 38 preserved queues, 339 excluded prior job IDs and 45 preserved historical uncertain rows. Root `.ux-loop/peekly-completion32-pinned-20261115` launched once at `2026-11-14T20:54:53.554687Z` (05:54 Asia/Seoul), detached PID 31561; actual run started at `20:54:59.705296Z`. Runtime is the same frozen `f50d082a197e683b5961d17919fe219dc48c4d55`; launch HEAD `f36c530084d28c1b264c2b7f199c534e99ea83a1` advances documentation only. The exclusive launch intent records the known documentation changes outside the freeze. All 32 jobs and call IDs are new; no R6 or old job earns cohort credit.
- Read-only checkpoint at `21:20:26Z`: complete 14 / running 2 / queued 14 / uncertain 2. Personas 017/018 are running at turns 17/16. 011 (`S-blhfedhpoafgojkcabihgadl`) is uncertain at tool turn 6 / five observations after requesting legacy seed without an assigned UNKNOWN requirement; the host rejected it before driver exchange. 014 (`S-ndgicogijfhmlolgkninpofi`) is uncertain at tool turn 10 / nine observations, `cdp_timeout:DOM.getDocument`, during target resolution for the oversize-plus-one fixture, before file selection was dispatched. Its Node elapsed time was 54,176 ms and host elapsed time 60.397 seconds; the underlying stall cause is unproven. No resend or resume; all nine criteria assigned to these two sessions remain unassessed. Neither is an established product failure. Completion counts are operational progress, not yet independently reviewed final outcomes. Product/library/fixtures and all 17 runtime files remain frozen through terminal checks.
- Offline finalizer PID 33511 launched once at `20:56:46.871221Z`; the exclusive intent, PID, live process and waiting events were read back at `20:59:48Z`. It polls every 30 seconds, performs no model/browser calls or queue writes, and may publish only the five raw report files after terminal integrity gates. Its outputs remain pending manual review. Do not stage other documents during its publication step.
- Independent reviewers own disjoint completed-session sets 001–012, 013–024 and 025–032; see `cohort-review-coordination.md`. Bind every decision to the new plan/result/receipt and registered admitted evidence. Final statistics must exclude uncertain/incomplete sessions, retain them as unassessed, and distinguish whole-cohort counts, old-23 credit and original-46 weighted mappings.
- Interim semantic review found that 001–004 never expose the assigned privacy notice in an admitted viewport, despite its presence in returned product DOM text and raw passed judgments. Each has only three observations and no scroll. The draft correction is passed to not_run for actual visibility, not a claim that product privacy copy is absent; root independently checked 001's first and final registered captures. These are outside the old-23 target set. Final evidence-bound decisions remain pending the full raw publication and combined review.
- The first old-23 recovery target, 013, has actual safe ordinary reimport after a consumed/restored one-shot save fault: obs-12 preserves the baseline, obs-13 persists new usable state. Direct retry remains a separate SAVE-FAIL product failure. Its cancel trial actually dispatches while active and leaves storage unchanged; the 1,115 ms recorded observation window is not an invented precise cancel timestamp. In contrast, 015 ends after its save fault without ordinary recovery; raw N/A must become recovery not_run, a new remaining criterion outside the old-23 set. Draft evidence reviews are saved as they complete.
- Host shutdown for any retained uncertain context is owned by `live_scale_browser.py::_execute_with_shutdown` after the whole stage settles. 014's Node separately records stopped/browser_stopped/proxy_stopped, while final host closure and the complete process inventory remain pending. Do not externally interfere with the live owner or claim final teardown yet. Read-only tool-response bookkeeping issues have been recovered without relaunching the cohort or resending any uncertain operation; use explicit workdir values if ephemeral tool-session variables disappear.
- Later checkpoint `21:28:31Z`: complete 20 / running 2 (023/024) / queued 8 / uncertain 2 (011/014). The 001–012 review is persisted: eleven completed candidates, 47 decisions, reviewed 36 passed / 0 failed / 4 not_run / 7 N/A, with 011's five criteria unassessed. All 178 artifacts / 89 observations and result/checkpoint/receipt bindings verify; 210 exact evidence references cover every decision. Global raw-summary/artifact-audit pins intentionally remain pending. JSON SHA `51167e22332e94adc34cc1552e6e98bf745f214fb13402559f809a21f7416e5c`, Markdown SHA `71ac2cccf3797f1a2889e2193dd909596676743e7ef1eb961f0bbc9fb0a082df`.
- Independent review now supports all twelve old-23 relationship rows in 017–020, plus 013 recovery: thirteen old-23 rows have actual execution evidence so far. All four relationship sessions use ordinary previous-to-current imports and actual 5/2/5 sheets. Each separate snapshot criterion changes raw passed to failed because its own departed-list DOM contains two inferred-cause labels despite the limitation caveat; the saved image crops do not show those badge pixels. Product failures remain distinct from the completed relationship coverage. UNKNOWN, identity, SEARCH and PAYWALL target reviews are still pending.

### R6 launch checkpoints (historical)

- R6 launched at `2026-11-14T20:29:49.518011Z` (05:29 Asia/Seoul), detached PID 6800; actual run started at `20:29:57.521366Z`. Runtime source `f50d082a197e683b5961d17919fe219dc48c4d55` was committed/pushed with exact remote SHA and clean worktree verified before launch.
- Root `.ux-loop/peekly-completion-smoke-r6-20261115`; 024 job `S-mfopimglobkoejplhjkbgpkj`, 032 job `S-ecklphmclceoijfnndjiekic`. The exclusive launch intent, launcher log and PID file are saved beside that root. No old job or uncertain operation is resumed.
- At `20:30:58Z`, both jobs were running at turn 5 / five admitted observations, with no recorded problem. The independent read of 024 confirms observe first, then the validated legacy seed as its first mutation, actual reload/migration, one UNKNOWN snapshot and null active/comparison selections. This is partial precondition evidence, not completed-session coverage or a passed smoke.
- Keep the 17 runtime files, fixtures, library and product fixed through R6 and the subsequent cohort if its gate passes. Both current-valid complete receipts, all six executed success criteria, actual UNKNOWN/PAYWALL evidence, zero uncertainty, confirmed closure and before/after integrity checks remain required. No 32-person execution has started.

### R5 preservation and R6 prelaunch validation (historical)

- Mac mini execution/read access was verified again at `2026-11-14T20:10:59Z` (05:10 Asia/Seoul). Main HEAD is `9e6b30bd7d40d43ba7d656f85fa2e0dc82b73b28`; the only untracked entry is the owned isolated action-deadline worktree. R6 and the new 32-person root do not exist yet.
- R5 ended at `2026-11-14T19:35:20.869439Z` (04:35 Asia/Seoul), `smoke_failed`, complete 0 / uncertain 2 / queued 0 / running 0. Preserve both jobs and every original operation. Six success plus two recovery criteria are unassessed on the completed-session basis, with zero old-23 execution credit.
- 022 remains uncertain after upload tool 10 / nine observations and the original host action-response limit. 031 remains uncertain after tool 60 / 59 observations, with `browser_action_failed:cdp_timeout:Page.captureScreenshot` under the 10-second CDP response limit. These are runner/transport failures, not established product failures; their underlying stall causes remain unproven.
- R5 preservation audit is complete in `smoke-r5-diagnostics.json` / `.md`: both owned groups exited, 022 through recorded forced owned-group cleanup and 031 through normal close; no matching R5 process was found at 20:12:20Z. Before integration, the 17 runtime pins, 36 prior queues, 544 fixtures, library/build, 319 source files, 13 dist files and six saved HTTP before/after entries were independently verified unchanged. All 140 request and 138 received-reply seals, both checkpoints, the plan and 285-event chain verify. All 136 registered partial artifacts (3,659,145 bytes) match. Model ledger: 70 logical calls / 70 attempts, all received on the single approved free route, no repair/retry/fallback. No old operation is resumed or resent.
- Isolated `b7079c51a79f10a6ab3c0c4de1c03e745edeb408` was integrated as `d6a3f25a4313248e3afb34e9c4b9b46ff325b54e`; reviewed screenshot correction `03c69151ca52822373782a167e7e188b61052287` was integrated as `19668ef2976875c210777c999bca5518d59534cd`. Only screenshot CDP gets 30 seconds; other methods retain 10 seconds and overall Node/host actions remain 80/90 seconds. The production pending helper has nine new deadline/abort/no-resend tests. The isolated checkout was removed after verifying its clean commit and preserving all regression logs; its branch remains.
- The integrated runtime and R6 selection passed **98 tests, zero failures/skips**, in 9.764 seconds (process exit 0). Log `.ux-loop/peekly-completion-r6-regression-20261115.log`, SHA `2b3a539d8cb553cf58d16d7f90def5c89f9d84ec405087d3c6c74c08dd4064c6`. The result-query transport timed out once; the original completed session and exact log subsequently confirmed exit 0 without rerunning the suite. The separate earlier isolated 32/35 result and unchanged 3/3 targeted rerun remain documented in `action-deadline-validation.md`.
- The predeclared R6 pair is 024/032, with two matched baseline not_run among six success criteria. Run it once in new contexts after the reviewed source is integrated, validated, committed and remotely verified. Only its full strict gate and independent evidence review authorize the new 32-person run with identical runtime/input bytes.
- R6 offline preflight passed: 37 preserved prior queues, 337 excluded prior job IDs and 45 preserved uncertain rows; all 32 saved revision-1 personas remain reusable. Target is the owned pinned `51110f4` archive on port 4175. The current six served files matched again at 20:15:59Z; the actual launcher still requires its own immediate before/after checks. No R6 or 32-person execution has started at this checkpoint.

### R5 launch and preparation checkpoints (historical)

- R5 launched at `2026-11-14T19:07:40.327649+00:00` (04:07 Asia/Seoul), detached PID 61433; source `6046c7af218178ad2384900405cb428cd211072e` committed/pushed with exact remote SHA verified. Runtime and tests were committed; the only untracked files were two offline report-review helpers under this documentation directory, outside the 17-file runtime freeze.
- Root `.ux-loop/peekly-completion-smoke-r5-20261115`; 022 job `S-jempbmnekmnoidfgnohkeofd`, 031 job `S-pcngliijgicolppnjdbkipjn`. Initial checkpoint: two running jobs, two model intents, no recorded problem. R5 preflight verified 36 prior queues, 335 excluded prior job IDs and 43 preserved historical uncertain rows.
- Keep runtime, fixtures, library and product bytes fixed. This is not yet a passed smoke; no 32-person execution has started. The exact close contract now has real Queue/ScaleExecution regression coverage.
- R5 checkpoint at 04:18 Asia/Seoul: 022 is uncertain at tool turn 10 after 9 admitted observations; original upload of `peekly-missing-followers.zip`, operation `op-93cda0d21d08f8dc859fc6c4aa4cb9ff0b63722a`, hit the host's 25-second action-response limit inside the approved 180-second queue call. A capture file exists but no correlated response was admitted; do not claim action completion or replay it. The channel is poisoned and ownership retained. 031 continues at turn 34 / 33 observations with no recorded problem. R5 cannot authorize expansion in this state.
- Preparing an action-deadline/I/O correction in a separate `.worktrees/peekly-action-deadline-20261115` checkout while R5 remains byte-frozen. The exact underlying stalled step is not established by the capture timestamp. No new model/browser execution for that isolated correction. A subsequent strict smoke must use new contexts and preserve all uncertain calls.
- The offline independent-review application is implemented and independently reviewed: 26 tests passed, actual historical log/PNG admission checked read-only. See `review-application.md`. It preserves raw outputs and four historical columns, binds new evidence, and keeps N/A/unassessed separate in old-23/46 mapping. No final new-cohort output exists yet.
- Checkpoint 04:34 Asia/Seoul: 031 is still running at turn 58 / 58 admitted observations. Actual prescribed previous/current imports and free comparison are reached; the History modal can be scrolled despite its small viewport. Final PAYWALL B/C and completed-session assessment remain pending. 022 stays uncertain and is not resent.
- Isolated correction is committed as `b7079c51a79f10a6ab3c0c4de1c03e745edeb408` on `rem/peekly-action-deadline-20261115`, with 35 Python tests passing, zero failures/skips (55.958 seconds), including the Node regression and actual Queue close contract. Independent review's combined click/observe monotonic deadline and pre-observe expiry checks are included. Final log SHA `f8e52810d1666fc389c77d81cf1607398c281bd7ef34f90b780b25d1c8b68b36`. Main runtime is unchanged until R5 is terminal; this is not evidence that R5's underlying stall or actual coverage is fixed.
- `smoke-r6-plan.md` predeclares fresh independent 024/032 contexts and the correct two-not-run baseline. Their R4 operations had settled without uncertainty and remain paused. Integrate the reviewed correction only after R5 termination, then run the full unchanged strict R6 gate before the 32-person cohort.

### R4 preservation and R5 preparation (historical)

- R4 ended at `2026-11-14T18:58:20.151359+00:00` with `smoke_failed`, control paused, queued 2 / complete 0 / running 0 / uncertain 0. It was intentionally paused after discovering a close-result adapter contract mismatch, before either job dispatched close. All in-flight responses settled; 37 logical model/review calls, 38 attempts with one known received-reply quality repair, zero uncertain resends. Both browser contexts and groups closed. The 35 prior queues and all 70 partial artifacts remain intact; partial observations earn no completed-session coverage. See `smoke-r4-diagnostics.json` / `.md`.
- The root's lifecycle change incorrectly added details to the close wire result. Existing ScaleExecution and AgentExecution require exactly `{"stopped": true}`. The prior 88-case suite and zero-model browser lifecycle probe did not cover that caller boundary. An offline actual Queue/ScaleExecution reproduction yielded blocked 2 / complete 0 with `worker_stop_unconfirmed`; this code was not dispatched as a per-job close in R4.
- Fixed the wire result only; rich teardown evidence remains in lifecycle records. Added two actual Queue/host integration regressions: successful current-valid completion/readback without redispatch, and failed-group closure retaining ownership/blocking completion. Final combined regression passed 90/90, zero failures/skips, in 19.543 seconds. Log `.ux-loop/peekly-completion-r5-regression-20261115.log`, SHA `5116e476ff038054f254fa881fa534aeda302100aaffc751d084fda6aa8fad9c`; asyncio slow-callback and temporary-directory cleanup warnings were emitted, without test failure.
- NEW independent R5 pair is 022/031 at `.ux-loop/peekly-completion-smoke-r5-20261115`, not used in completion R1–R4. Exact requirement/context equivalence verified; matched baseline is THREE not_run among six success criteria (022 IDENTITY + UNKNOWN; 031 PAYWALL). All-six-executed strict gate remains. See `smoke-r5-plan.md`. No R5/32-person execution yet at this checkpoint. Preserve R4 paused; never resume it.

### R4 launch checkpoint (historical)

- Source `4a0f3bbbf610132798d8edb8ad343637f7e4d82d` committed/pushed, exact remote SHA and clean worktree verified before launch. R4 launched at `2026-11-14T18:51:27.742143+00:00` (03:51 Asia/Seoul), detached PID 49840. Root `.ux-loop/peekly-completion-smoke-r4-20261115`; 024 job `S-iikjgdifekagbjlmmogeoldg`, 032 job `S-imkegjkfkgiilkafipmeibkj`.
- Read-only checkpoint at 03:52: both jobs running, turn 3, three admitted observations each; six completed model and six completed tool operations, no recorded problem. New startup has produced real observations in both contexts. This is progress, not a passed smoke or completed-session coverage. No 32-person run has started.
- Keep runtime/fixtures/library/product bytes fixed through R4 and the subsequent cohort. Preserve every old queue and uncertainty. Only documentation may be updated while execution runs.

### R3 preservation and R4 prelaunch validation (historical)

- R3 launched `2026-11-14T18:24:30.812452+00:00` (03:24 Asia/Seoul), detached PID 32659, source `054342d099648104fd23aae29953f9a6399f3e73` committed/pushed with exact remote SHA and clean tree verified. Root `.ux-loop/peekly-completion-smoke-r3-20261115`; jobs `S-obfofmpdpeibgbipcfgdlcoa` (023) and `S-nebbkpjgckcjdeeachjcglag` (030).
- R3 ended at 03:26 Asia/Seoul with `stopped_preserved` / `browser_shutdown_unconfirmed`: both first tool operations timed out, both jobs uncertain, zero admitted observations and no completed receipt. The two model replies were received; model uncertainty and tool uncertainty are distinct. Six success plus two recovery criteria are unassessed, not not_run/product failures; no old-23 improvement credit.
- User restored the Mac tunnel at 18:38Z. Source and remote `054342d099648104fd23aae29953f9a6399f3e73` matched. Independent R3 audit verified both checkpoint seals, plan seal, four request-payload seals, two model-reply seals and all 34 prior queues unchanged. See `smoke-r3-diagnostics.json` / `.md`.
- A surviving R3-owned headless Chrome PID 33010 was reverified against its exact 030 profile and terminated with SIGTERM only. Post-cleanup independent process inventory found no matching R3 profile. This postmortem cleanup does not rewrite the historical failed-shutdown receipt or uncertain operations.
- Confirmed runner defects: fixed 25-second startup timeout, unbounded CDP discovery/WebSocket waits, reuse of a timed-out response channel, teardown without waiting for process exit, premature loss of ownership, incorrect signal-exit handling, and failure reports omitted after shutdown failure. Implementing bounded startup/teardown, complete asynchronous fixture validation, poisoned-channel quarantine, owned process-group cleanup with observed exit, and durable failure diagnostics. Product/fixture/library bytes remain pinned.
- NEW independent R4 smoke is predeclared as 024 + 032 in `.ux-loop/peekly-completion-smoke-r4-20261115`. Neither was used in completion smoke R1/R2/R3. Exact same ordered success/recovery requirements and PRD context as 021/029; each old result is P/P/NR, preserving the six-success/two-not-run baseline. No old uncertain request is resumed or resent.
- No R4 or 32-person cohort has started at this checkpoint. Finish regression and source commit, run the new strict two-session gate, then freeze identical inputs for the new 32 cohort. No failed smoke can authorize expansion.
- Lifecycle repair is now complete and independently reviewed: final Python regression 88/88 and Node suite 61/61 passed, zero failures/skips. A separate actual owned-browser probe made zero model calls, admitted one observation and confirmed the entire owned process group closed (fallback used), with unchanged input freeze and six served files. Offline R4 preflight passed with 35 old queues / 333 excluded jobs / 43 old uncertain rows. Details and hashes: `lifecycle-validation.md`.

### R2 terminal audit and predeclared R3 selection

- R2 ended `2026-11-14T18:14:22.256268+00:00`: 021 complete, 029 uncertain at model turn 52 after HTTP 502. The exact call `op-f52816c286aa230cea3c061f5e4eee78205f3be0` has one attempt, `can_retry=false`, and remains quarantined. 72 actual attempts: 71 replies and one uncertainty; zero resends, zero known-quality retries, only the authorized TOKENMAXX route. Provider cost fields were missing, so policy cost zero is not an independently verified invoice.
- The R2 gate failed and no cohort started. Both queues are terminal; browser shutdown, source/input freeze, six served-target after hashes and prior-queue integrity passed. Completed receipt's 34 artifact files have no mismatch; both checkpoint seals were checked. See `smoke-r2-summary.json` and `smoke-r2-artifact-audit.json`. The 029 partial observations earn no completed-session coverage.
- Predeclared NEW independent R3 pair: 023 and 030, root `.ux-loop/peekly-completion-smoke-r3-20261115`. They were not used in completion smoke R1/R2. Their ordered requirement records and PRD context exactly match 021 and 029 respectively; prior 65f statuses are P/P/NR for each, so the same six success criteria have two matched not_run. New job/context/call IDs and all-old-job exclusion remain mandatory. No R2 session is combined into the R3 gate.
- Keep the unchanged strict gate: two valid complete sessions, six executed success criteria, no success N/A, no uncertain delivery, unchanged old queues, verified browser closure and target/input freeze. Runtime behavior, fixture and product bytes are unchanged; only the next smoke's persona selection/default output root changes. R3 must establish its own passing gate and identical freeze before the new 32 cohort.
- R3 preflight passed: 34 prior queues, 331 forbidden prior job IDs, 41 preserved uncertain job rows. The 62-case targeted regression passed in 0.577 seconds with no skip/failure; the added case rejects substitution of the old smoke pair even when its other counts look successful. `git diff --check` passed. Selection rationale and fixed requirements are in `smoke-r3-plan.md`.

### R2 execution checkpoint (historical; superseded by terminal state above)

- 021 is now queue-complete: 18 model turns, 17 admitted observations, 34 artifacts / 952,649 bytes with all hashes and three seals verified. Actual UNKNOWN seed → current import → exclusion proof succeeds. Raw success is 3 passed / 0 failed / 0 not_run; independent review is 2 passed / 1 failed / 0 not_run, with recovery passed. The IDENTITY delta is an actual rendered comparison that labels two rows `언팔로우` despite the no-cause-assertion requirement; preserve raw results and classify product wording inconsistency plus judge false pass. See `smoke-r2-021-review.json` and `.md`, including the PNG viewport limitation. Do not transfer this case-specific judgment to future jobs without their evidence.
- 029 remains running (50 observations at the 03:13 Asia/Seoul checkpoint), with no recorded queue problem or uncertain status. Full smoke gate, browser shutdown, served-target after-check and final router audit remain pending; no cohort expansion yet.
- Actual R2 started `2026-11-14T17:55:51.441018+00:00` (2026-11-15 02:55 Asia/Seoul), detached launcher PID 11609, on committed and remotely verified source `1939f32ccef5bf2eae2edb2e0c51d6fba10dd0d5`. Worktree was clean at launch.
- Root `.ux-loop/peekly-completion-smoke-pinned-20261115`, stage `stage-2`; jobs `S-beegcnopeblnnfadcbmfpcbk` and `S-ikjnkcfnpkaooaeedahemnmk` initially running. Initial read-only checkpoint: 4 completed model operations and 4 completed tool operations, 2 model intents. Input provenance SHA `c300d5d340c0d41566cc0d36a326a4a155b74e32417b8870778b2e4415e1971c`.
- Runtime, fixtures, library, source and dist are frozen. No 32-person run yet. Inspect actual smoke evidence and require its full gate before starting the new cohort. Initial counts are progress only, not completed-session coverage.

### Recovery and pre-launch checkpoint (historical)

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

1. Complete the fixed R5 smoke (022/031); verify two current-valid sessions, all six success criteria executed, and the matched three-not-run reduction with actual seed/IDENTITY/PAYWALL evidence.
2. Only after the strict gate and evidence review pass, launch fresh 32 once with the identical freeze. Start its durable raw report/audit publisher and monitor with short read-only checks.
3. Terminal raw aggregation, full byte/seal/source/ledger audit, independent semantic review. Compare pinned remaining 23 and original 46 with N/A and unassessed separate and earning no execution credit.
4. Update historical comparison, STATUS and findings, commit/push, verify exact remote SHA and clean worktree.

Historical r1 had five uncertain resends and remains disclosed. The preceding final 32 had zero. New runs must independently verify zero; no lifetime-zero claim.
