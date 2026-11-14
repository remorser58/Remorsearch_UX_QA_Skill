# R4 smoke — paused and preserved, normal shutdown confirmed

Runtime: `4a0f3bbbf610132798d8edb8ad343637f7e4d82d`. Root: `.ux-loop/peekly-completion-smoke-r4-20261115`. Terminal state verified on 2026-11-15 03:59 Asia/Seoul; integrity follow-up completed at 04:03.

**R4 failed the completion gate after an intentional pause.** It ended at 03:58:20 with two queued jobs, no running or uncertain jobs, and no completed receipts. The queue stays paused and will not be resumed.

| Persona | Phase at pause | Turns | Observations | Completed receipt |
| --- | --- | ---: | ---: | --- |
| 024 | close | 14 | 13 | none |
| 032 | model | 22 | 22 | none |

The parent found a host close-result contract mismatch by code inspection and paused the run before a per-job close operation was dispatched. **No `worker_stop_unconfirmed` failure occurred in R4.** The parent's subsequent offline regression of that mismatch is a separate result, not a live R4 failure.

## Actual delivery and shutdown

- All 72 queue operations settled: 36 model, 1 review and 35 tool, all done. No per-job close operation was dispatched.
- All 72 request-payload seals and 72 reply seals match; both final checkpoint seals match.
- The router recorded **37 logical calls and 38 actual attempts**, including one repair after a known received response was rejected for quality. The repair call is `op-ccf98f2aed688b9b1fb1449b973fa9e2160b8082`, with success → quality_rejected → success events. This was not an uncertain resend, and not every call had one attempt.
- All requests used `TOKENMAXX/deepseek-v4.1-flash-free`. The delivery audit is valid, with zero uncertain resend violations, uncertainty, unsettled guards, in-flight guards or paid fallback. Input/output tokens: 953,611 / 16,783. Provider invoice zero is not independently established.
- Final stage summary and lifecycle receipts confirm normal shutdown of both owned contexts, actual owned-group exits, no forced cleanup, no unclosed context and no shutdown error. An independent process listing at 03:59:55 found zero exact R4 profile processes.

## Coverage and preserved evidence

Success criteria 6 and recovery criteria 2 remain **unassessed on a completed-session basis**. The 35 partial observations and 024's queued close phase do not provide completed-session coverage or reduction credit for the old 23.

024 observation 2 did independently prove the first-mutation validated legacy seed, actual v6 → v7 reload, one UNKNOWN snapshot and empty active/comparison selections. Its JSON SHA is `76a87ce9e0773b338394e5978f9fa36d7660c99dd8667c22ef1ca3a419e437af`. Seed evidence alone is not success for the full UNKNOWN requirement.

Initial R4 runtime verification matched all 17 frozen source files. A fresh independent read-only snapshot matched all 35 prior queues, aggregate `93722e15dd90d764f392933cb64420238d00f6f69624f51ae95e6bd678b239ca`, exactly as the saved launcher before/after receipts record. All **70 partial-session artifact files / 1,878,191 bytes** match their registered hashes: 024 has 26 files / 721,994 bytes, and 032 has 44 files / 1,156,197 bytes. Seven report/provenance/lifecycle source files were hashed, with the saved run-status pins matching. These integrity checks do not turn partial sessions into completed receipts. Source repair after terminal R4 requires a new freeze and smoke.

## Next pair: 022 + 031, baseline **three** not_run

Neither persona appears in completion smoke R1–R4. Their active revision-1 profiles have the same PRD context and requirement IDs as the original UNKNOWN and PAYWALL groups.

| Persona | Previous success outcomes | Previous not_run requirements |
| --- | --- | --- |
| 022 | passed / not_run / not_run | IDENTITY, UNKNOWN |
| 031 | passed / passed / not_run | PAYWALL |

The next smoke keeps six success criteria but must explicitly use **baseline not_run = 3**, not 2. Current binding hashes and baseline job IDs are in the companion JSON. Independent revalidation confirmed both current active revision-1 bindings, absence from completion R1–R4, exact PRD context and profile requirement IDs, and identical ordered old success/recovery/requirement_coverage records versus 021/029.

The parent owns the close-contract fix, regression, new root and predeclared run. Preserve R4, require two independently valid complete sessions and the full gate before 32-person expansion, and never resend uncertainty.
