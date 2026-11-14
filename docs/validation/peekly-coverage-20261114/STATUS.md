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

## Current state — FINAL32 cohort is running, never launch it again

- Frozen runtime source:43e3b143cdfee0a8ae23f68808ebf850e99008bb; launch HEAD78810f048b8069e4307f165c4cd128899768b3f9 differs only by handoff docs. Both commits were pushed and remote SHAs verified.
- Fresh cohort launched2026-11-14T06:14:39Z, PID97160; durable started_at06:14:43Z. Exactly saved personas001–032, no duplicates.
- Root:.ux-loop/peekly-coverage32-20261114; queue stage-32/queue.sqlite; launch log:.ux-loop/peekly-coverage32-launch-20261114.log; PID file same prefix.pid.
- Initial check:running2/queued30. At06:21Z:8 complete, all8 operational_completed=true/passed/problem=null; running2/queued22, uncertain0. Offline gates and passed r4 report/summary/router hashes were revalidated before execution.31 historical queues/295 old job IDs are protected;36 historical uncertain rows remain preserved.
- Latest observed06:57Z:complete16/running2/queued11/uncertain3. Raw complete outcomes11passed/4failed/1inconclusive. Ordinals8/9/11 (personas009/010/012) have model_delivery_uncertain and remain excluded, never resend/resume. The scheduler continues019/021. Both009/010 have one150-second timeout delivery record, uncertain guard/can_retry=false, one dispatch intent, and no later operation for the uncertain call. No completed-session denominator may include these uncertain rows.
- Smoke and cohort handoff docs were pushed as68c3ba4bb60f1ff79c2fdbc1156a75bcef2ac409, exact remote SHA verified. Runtime remains43e3b14.
- Do not edit runtime, fixture files or saved library during this cohort. No uncertain request may be resent or resumed. Regressions for the frozen runtime are complete; while the cohort runs, use only readonly monitoring/review and docs/report work. The newly discovered post-cohort scope repair is described below.
- Once terminal, run: PYTHONDONTWRITEBYTECODE=1 /Users/m4mini/.local/bin/python3.11 scripts/report_peekly_coverage.py .ux-loop/peekly-coverage32-20261114/stage-32 docs/validation/peekly-coverage-20261114 --requested 32. The summary.json/comparison.md outputs do not exist yet and the reporter refuses overwrite.
- Independently verify completed receipt artifact bytes, classify remaining gaps/failures, update the four-column comparison and original report pointer/table, commit/push and verify final remote SHA. Keep smoke cohorts separate from final32 counts.
- A statically reviewed independent auditor is ready in docs/validation/peekly-coverage-20261114/audit_final_artifacts.py; it has not run. After terminal state, invoke with stage-32 path and output docs/validation/peekly-coverage-20261114/artifact-audit.json, using PYTHONDONTWRITEBYTECODE=1 and the pinned Python. It checks all assessed receipt artifacts, all result/checkpoint seals, first seals, plan/DB/report bindings and terminal provenance with read-only SQLite. Empty first judgment with no seal is permitted only for uncompleted records; no evidence files/queue writes.
- implementation-notes.md records the46 cause counts, source/fixture changes,25 unchanged PRD definitions,1697pass/21skip regression, confirmed missing save retry and the initial5-resend smoke incident.
- Completed011(jobS-pdalpdmknheojnhkkichdfbm,18turn) has2successpassed/2not_run. Independent review found bothnot_run false: actual own-upload rejection and unchanged stored digest exist inobs10/14/15, but the evaluator expects different Korean phrases. See evidence-review.md. Original scores remain unchanged.
- Critical new scope finding017(jobS-jmpokhjegennajnihcaemagh): raw4successPASS, but first3RESULT criteria require valid import then each category list; task instructions also allow sample and evaluator has no native prerequisite branch. Actual sample lists areobs4/6/8; previous/current importsobs13/16 have real expected cards but no lists; only postimport listobs18 is departed. Thus3rawPASS are unsupported for full imported scope, and baseline NR-21/22(2rows/2keys) must not receive reduction credit. SNAPSHOT NR-04/23(2rows/1key) has real supporting evidence.
- Cards-scope issue affects task definitions for017–020.018/020 have now completed and classifier is reviewing their saved observations;019 still runs. Never generalize unsupportedPASS without individual evidence. All evidence review is readonly.
- After the entire cohort is terminal, apply the minimal task prerequisite/order and native RESULT guard fixes, with stored-evidence/unit regressions. No additional model/browser run is currently planned. Task/driver agents are preparing proposals only and must wait for parent's explicit edit release as an internal source-freeze coordination step. Runtime/fixtures/library remain frozen until terminal. Keep original32 receipts and raw four-column results; separately publish conservative reviewed outcomes/mapping so unsupported sample-onlyPASS does not inflate reduction.
- Driver review found native not_run currently cannot veto a modelPASS at both receipt boundaries. The post-cohort fix must enforce the prerequisite only for the3RESULT IDs, with current import generation and actual category/list evidence; never make all generic not_run authoritative. Sample and current fixture have identical counts AND names, so matching content alone is insufficient.
- 018/020 were independently checked: same sample-only3categorylists and real previous/current→departed path. Their raw9PASS across017/018/020 lack postimport list scope. Baseline exclusions now7weighted rows/5unique keys:017 NR-21/22;020 NR-06/07/28/29/30.018 contributes no category rows to old46; its NR-24 SNAPSHOT is supported. At07:00:33Z,019 also completedpassed and is under the same evidence review. Current queue complete17/running2/queued10/uncertain3; running021/022.
- Latest pushed docs commit32a29f1b5c391ce0ca403ba2b492b85bdc5cf3d8 was remote-SHA verified. It contains implementation-notes.md and the independent artifact auditor. evidence-review.md is currently newer/uncommitted.
- 019 review is now complete: samplelistsobs7/9/11, actualimports16/19, departed22, close23; no postimport3categorylists. All017–020 scope changes are12PASS→not_run and4passed sessions→inconclusive. Original46 reduction excludes9weightedrows/7unique keys(NR-06/07/21/22/25/26/28/29/30).
- criterion-review.json now records14 exact independent changes: those12, plus011 HTML/ACCOUNT2not_run→passed because actual rejection/unchanged storage meets fixed PRD. Parent cross-checked all5 resultSHA values with readonlyDB. It is an overlay only, no source receipts/queue changed.
- Classifier may write ONLY docs/validation/peekly-coverage-20261114/review_coverage_results.py while cohort runs; no execution yet. After terminal rawreport+artifact-audit, use it for reviewed-summary.json/comparison-reviewed.md. Four historical+new data columns should show reviewed finalcolumn with raw counterpart retained. Exact present overlay delta:success/all passed-10/not_run+10; sessionspassed-3/inconclusive+3; baselinepassed-9/not_run+9(7unique). Recompute totals, do not hand-edit summary counts.

## Passed r4 smoke — preserved pre-expansion evidence

- Frozen runtime commit:43e3b143cdfee0a8ae23f68808ebf850e99008bb. Pushed to origin/rem/peekly-coverage-20261114 and exact remote SHA verified.
- Detached launch2026-11-14T05:56:47Z, PID93473; durable run started_at05:56:51Z. Exact016/029.
- Root:.ux-loop/peekly-coverage-smoke-r4-20261114; queue stage-2/queue.sqlite; launch log:.ux-loop/peekly-coverage-smoke-r4-launch-20261114.log; PID file same prefix.pid.
- R4 ended2026-11-14T06:11:35Z, smoke_passed.2 valid complete; sessions0passed/1failed/1inconclusive. Success4passed/1failed/1not_run/0N/A; recovery1passed/1N/A. Same-person baseline not_run3→1. Remaining gap is029 PAYWALL; do not relabel it.
- Actual Peekly modal scroll atobs44 moved67px with background_moved=false. Retention11 imports/count10 passed.016 progress and all three size boundaries passed; missing direct save-retry is failed. Independent SIZE audit confirmed actual128/32/64MB messages, matching fixture byte/hash data and unchanged persisted digest; an intermediate model claim about missing128MB text was inaccurate.
- Final ledger audit valid:77 requests,1 known completed-response repair,0 uncertain resends/0 unsettled guards. Prior queues unchanged; browser shutdown confirmed. This passed gate authorized the current cohort.

## Preserved r3 result and r4 prelaunch verification

- R3 runtime commit:18a4c0af8cee17e6af73984eaebfa4a5595720e4. Pushed and remote SHA verified; docs-only de7692192636bf1083425d2a9db9c8eb33d22c54 was also pushed and verified.
- Fresh detached launch2026-11-14T05:19:15Z, PID84778; durable started_at05:19:18Z. Exact personas016/029.
- Run root:.ux-loop/peekly-coverage-smoke-r3-20261114; stage-2/queue.sqlite; launch log:.ux-loop/peekly-coverage-smoke-r3-launch-20261114.log.
- R3 ended2026-11-14T05:35:49Z:smoke_passed numerically,2 valid complete,0 queued/running/uncertain. Sessions0passed/1failed/1inconclusive; success3passed/1failed/2not_run/0N/A; recovery1passed/1N/A. Prior queues unchanged, browser shutdown confirmed.
- Final r3 ledger audit valid:49 requests/47 call IDs,2 known completed-response repairs,0 uncertain resends/0 unsettled guards. Only free TOKENMAXX route, fallback0. No persona run is currently active; runtime edits began only after r3 ended.
- R1/r2 are preserved. No32-person cohort has launched. R3 has exposed a new deterministic scroll-target defect; do NOT expand from r3 even if its numerical gate later passes. Repair and verify this known blocker before a new smoke/32 cohort.
- R3 persona016:valid operational_completed=true, failed session, success passed2/failed1/not_run0; direct missing-save-retry failure is now admitted.029 ended at31 turns with sample export passed and retention/paywall not_run.
- Newly confirmed r3 blocker:driver mouseWheel is hard-coded to(500,400), outside the saved history modal at viewport756x413/modal roughlyx118..638,y96..318. Four scrolls(+300,-400x3) left identical PNGsobs19–23, SHAe029fa773bb6ce590fe595e6733014d0c712307a391df72fc820e3d3c2169b08. Closing at24 worked. Scroll targeting is a runner defect; possible zero-height modal body is still being checked against product source.
- Product source resolves the apparent missing body:at756x413 desktop CSS leaves a221px sheet with approximately84px scrollable body; the tabs are below the visible overview. There is no established zero-height product defect. Pro explanation additionally requires an older comparable period beyond the latest pair.
- After r3 terminal confirmation, driver agent fixed actual modal scroll targeting/movement evidence and ran a local-only owned Chrome fixture regression; task agent fixed retention/paywall prerequisites, no-movement escape and r4 root. No model calls, product edits or old queue writes occurred in that repair. Production viewport is unchanged. R4 subsequently launched as recorded above.
- Both agents have now finished and frozen source edits. Task/fixture/launcher31 tests pass; driver/evidence/admission31 Python tests pass, including30 Node guardrail cases. All32 saved-persona goals pass privacy/8000-character bounds; longest6057 with conservative787-character base goal.
- Actual local Chrome fixture regression passed with one temporary profile, zero page network requests and profile removed. An84px body moved0→67 after requested400 was capped67, a below-fold control became visible/hit-testable, background did not move. Old fixed point did not move; zero-height/fitting/covered targets did not dispatch. Production viewport remains implicit/unmodified; isolated test measured756x432.
- Evidence:.ux-loop/peekly-scroll-regression-20261114-dE8wr9/result.json (SHA256c95c02368b957b045a481e1cc6092da9d5fe51e5e1d9729b5e87ecf1e3f0fee9), before.png, after.png, focused-tests.log. Verified driver SHA256dcddb4069f3103da5c66ed3da3a3927eee83c1d5759c648d5521de664de8b4a5.
- Parent full regression completed:1718 tests,1697 passed,21 optional dependency skips,0 failures,198.965s. Log .ux-loop/peekly-coverage-r4-regression-20261114.log SHA256909b3b9362a540f3baf4df48232cd0dbfa9f2e077613ef0164a3a15f0e799983. No repeat needed. Actual r4 offline preflight passed:30 prior queues,293 forbidden job IDs,36 historical uncertain rows. The then-fresh r4 root is now active as recorded above.

## Initial implementation before r1 (historical)

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

## Preserved r2 result and r3 prelaunch validation

- Frozen implementation: fb0c6666bde5e969a6b479ec94ccf875a5f3aac5. Pushed to origin/rem/peekly-coverage-20261114 and remote SHA verified equal.
- New smoke launched detached2026-11-14T04:48:43Z, PID78522, exact016/029.
- Current root: .ux-loop/peekly-coverage-smoke-r2-20261114; queue stage-2/queue.sqlite; launch log .ux-loop/peekly-coverage-smoke-r2-launch-20261114.log.
- r2 ended2026-11-14T05:13:52Z with state=smoke_failed. Queue complete2 but assessed1:016 operational_completed=false/problem=observation_invalid;029 valid inconclusive, success passed2/not_run1 and recovery N/A1. No jobs remain running, queued or uncertain; owned browser shutdown confirmed.
- Exact016 cause: upload_save_failure op-f30fb0491f9e1ca6d18d7babaa8454b28e305646 returned an honest failed native criterion with a bounded reason, but agent_run.py observation admission accepts reason only for not_run. The preceding64MiB rejection was an intentional size-boundary group, not the v7 progress fixture.
- Applied after r2 ended: allow only bounded failed/not_run diagnostic reasons through the existing privacy/length checks; clarify direct scroll-to-import after sample export. New default smoke root is .ux-loop/peekly-coverage-smoke-r3-20261114. Runtime edits are frozen and regression/offline preflight passed. R3 subsequently launched as recorded above. Preserve r1/r2; never resume either.
- R3 verification:30 focused tests passed (native reason5, checklist7, launcher18); existing agent/scale/verdict/evidence85 tests had65 passes/20 optional LangGraph skips/0 failures. Combined95 passes/20 skips. Focused log .ux-loop/peekly-r3-final-focused-20261114.log SHA25699fc74ab8fb6dd2abdf439f7c0362a9ec1664c4721567c6f3893f9c9cafc8e4f; existing suite log .ux-loop/peekly-reason-schema-regressions-20261114.log SHA25691162f2b2f3408c42d2140f0a17923e754aa24e3a721566dedb4748e6d217aa0.
- Actual r3 offline preflight passed:29 preserved queues,291 forbidden distinct job IDs,36 historical uncertain rows; existing543 fixture hashes and32 saved personas checked without model/browser calls.
- Final r2 ledger:77 actual request receipts/76 call IDs,1 known completed-response repair,0 uncertainty,0 uncertain resends,0 unsettled guards. Audit valid; prior_queues_unchanged=true. Ledger SHA25665334e4a9034a104a277e7f5d01826e82679842ed51653c041a5314904ced745. Only approved free TOKENMAXX route; fallback0.
- R2 actual cancel dispatched and preserved storage;029 imported all11 retention files and passed retention, reaching a1,517,312-byte final checkpoint without the old1MiB failure. Paywall remained not_run. See smoke-r2-diagnostics.md. No32 cohort has launched.

- First smoke ended with a checkpoint size error. Its evidence is preserved and is ineligible for expansion. See smoke-r1-diagnostics.md, including the disclosed five internal timeout resends across four call IDs.
- All r2 runtime source edits are complete/frozen. Final full regression:1708 tests,1687 passed,21 optional dependency skips, zero failures,197.137s. Log .ux-loop/peekly-coverage-r2-regression-final-20261114.log; SHA2563004b7f0fdc7e6c980a0a9255a0a344d1e9bebdde2b0b2bb454a610625819d7f. The previous1697-test run had one stale exception expectation, now corrected without removing diagnostic assertions.
- Router26 + recovery6 tests pass: uncertainty immediately stops dispatch/fallback; durable call_delivery guards fence uncertain IDs across restart. Uncertain resends0; only complete known replies may receive up to2 bounded repairs. Router timeout150s/provider180s.
- Checkpoint planning11 and queue28 tests pass. Two realistic sessions reached finalturn64 with63 full observations each, >1MiB durable history, all artifacts unchanged and model envelopes<=256KiB.
- Parent focused79 tests pass: verdict25, criterion23, driver3 (18 Node cases), fixture15 and reporter13.
- Launcher17 and reporter17 tests pass. Actual ledger audit and SHA bind expansion/reporting; even an apparent32-complete report is rejected when a later request follows uncertainty. Known response repairs are counted separately.
- Final offline preflight passed before launch:28 preserved queues,289 forbidden job IDs,36 prior uncertain job rows.
- Reporter code is ready: scripts/report_peekly_coverage.py STAGE OUTPUT --requested 32. It preserves46 weighted baseline rows and32 unique persona/requirement keys; incomplete/N/A outcomes cannot count as coverage improvements.

## Preserved first smoke — never resume

- Frozen implementation commit: bf5e651845af84e4c2b22555662441e2cd9338a3.
- Smoke launched detached at 2026-11-14T04:00:52Z, PID66763, exact personas016/029.
- Run root: .ux-loop/peekly-coverage-smoke-20261114; queue stage-2/queue.sqlite.
- Launch log: .ux-loop/peekly-coverage-smoke-launch-20261114.log. Full run output: run root/run.log.
- Ended itself at2026-11-14T04:18:20Z: stopped_preserved, Queue data must be bounded finite JSON. Process66763 no longer exists; owned smoke Chrome processes0.
- Preserved queue:016 complete at18 turns,029 running with42 stored observations/phase tool turn43. No operations remain unresolved; the next done tool result could not fit the old checkpoint. Do not interpret the running row as an active worker.
- prior_queues_unchanged=true. Original27 queues were preserved. Router delivery uncertainty is a separate incident and is documented explicitly.
- r2 has now ended as described above. No32 cohort has launched yet.

## Applied r2 fixes and new inputs

- v6 progress fixture is rejected by the product's recognized/unpacked JSON aggregate64MiB guard. Reading/analysis text was observed but no active cancellation dispatched. Persona016 obs-9 is not a product failure.
- Fixed builder now enforces recognized aggregate64MiB including account JSON; new immutable .ux-loop/peekly-coverage-fixtures-v7-20261114 is ready. Manifest SHA2564df650d58c2105bc67ca3eec27c826b1f8129f8f1a846b396a4eb9e53c48f44a; progressZIP57961041 bytes, recognized JSON57960093 bytes; 300000 follower/120000 following rows. Fixture15 tests passed, including exact64MiB+1 refusal before output creation. Existingv5/v6 unchanged.
- Persona016 obs-13 reached a consumed/restored peekly_state_v7 write fault and unchanged persisted state. UI says 저장 공간이 부족해서 저장하지 못했어요…다시 불러와 주세요 and offers 다른 파일 고르기, with no 다시 저장 control.
- Pinned product docs/PRD.md §3 requires a 다시 저장 button on write failure. App.tsx1111–1122 throws before applying imported state; ExportWizardModal.tsx469–475 offers re-selection only. This is an executed missing-retry product failure. The r2 judge now recognizes the actual error wording and requires consumed/restored fault, preserved state and complete settled controls before failing the missing retry. Originalv6 receipt unchanged; read-only replay of obs13 confirms the repaired classification.
- Removed awaited active-phase screenshot from cancellation's critical path; immediate phase reread, target/hit verification and one native dispatch remain. Pre-upload/final captures remain. Real short-window and missed-window regressions pass.
- Launcher defaults now v7 and .ux-loop/peekly-coverage-smoke-r2-20261114. Its old-job rejection includes original smoke jobs. Cohort stays .ux-loop/peekly-coverage32-20261114.
- Actual pinned product parser acceptedv7 offline: .ux-loop/peekly-parser-offline-v7-20261114/parser-result.json and raw-validation.json. Raw420000 rows ->16/16 deduplicated accounts; same owner ascurrent/empty; no browser timing guarantee.

## Next checkpoints

1. Inspect the ALREADY RUNNING32 cohort with short readonly SQLite/jq calls. Never launch a second copy or resume any old job. Runtime stays frozen.
2. Preserve all uncertain/incomplete attempts outside the assessed denominator; no resend. Final router audit must distinguish known complete-response repairs from uncertain retransmission.
3. After cohort terminal, run the existing reporter once with --requested 32. Keep46 weighted baseline rows and32 unique persona/requirement keys; N/A and unassessed receive no coverage credit.
4. Hash-check registered evidence files of assessed receipts, confirm result/queue/report consistency, classify product/runner/judge findings and remaining not_run causes.
5. Update four-column comparison and final report, commit/push, verify exact remote SHA and clean worktree.

If interrupted, read this file and durable queues before doing anything. R1/r2/r3/r4 smokes are stopped and preserved. The final32 cohort has already launched at06:14:39Z with PID97160; inspect its durable state, never start another copy. Existing uncertain operations are never replayed.
