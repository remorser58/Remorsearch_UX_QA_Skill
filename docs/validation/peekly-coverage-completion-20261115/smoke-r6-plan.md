# R6 independent smoke — bounded action and response handling

This plan is declared before R6 execution. R5 remains preserved: 022 has an uncertain upload response and is never resumed or resent. At this plan's preparation, 031 is still running; its later result cannot be combined with a different smoke to authorize the cohort.

The action correction is prepared and tested in a separate worktree while R5's runtime remains frozen. It assigns a bounded 80-second Node action window and a shared 90-second host action window inside the existing 180-second Queue call. A possible 70-second context startup plus the action window remains inside that ceiling. Known nondispatched click rejection and its fresh observation share one action window. Post-deadline responses remain uncertain. Full fixture size/path/symlink/SHA validation and exclusive private capture writes are retained; asynchronous I/O and phase diagnostics do not authorize retrying an uncertain operation.

## Predeclared pair and matched baseline

Before R6 launch, R5 terminated with both sessions uncertain and no completed receipt. The source is additionally being strengthened so only `Page.captureScreenshot` receives a 30-second CDP response window; other CDP methods retain 10 seconds and the entire action remains bounded at 80 seconds. Actual pending-response, monotonic-deadline, abort and no-resend behavior must pass regression and independent review. R5's two requests remain quarantined; a longer limit does not retroactively acknowledge either response or establish the underlying stall cause.

New root: `.ux-loop/peekly-completion-smoke-r6-20261115`. Use **024 + 032** in new independent jobs, contexts, and call IDs. Their earlier R4 evaluation was deliberately paused after all in-flight responses settled, with zero uncertain operations and confirmed context closure. R4 stays paused and immutable. This is a new evaluation of the corrected runtime, not a continuation of R4. Every prior job ID is excluded.

| Persona | Current profile SHA-256 | Old 65f job | Old success results |
| --- | --- | --- | --- |
| PER-PEEKLY-V2-024 | 1513b20a0904c715df26a27cdf13bb26ac492c5fdb3dee1edc91c9ac0169ab6c | S-bhipnijdghjoompcjcokbceh | passed / passed / not_run |
| PER-PEEKLY-V2-032 | 09506ecac317692bd1c0eba798a2a24e6b5b262ec670680f8642ac9684ace5f9 | S-cceilcdlaojmdnjfhjfhcpal | passed / passed / not_run |

The matched baseline is **two not_run among six success criteria**, independently documented in the R4 plan/audit. R5's three-not-run baseline must not be reused for this pair.

## Unchanged strict gate

- Two current-valid completed receipts; all six success criteria executed as passed or failed, with zero not_run and zero success N/A.
- Actual validated legacy seed, then one known current import and UNKNOWN exclusion evidence before the ordinary comparison pair.
- Actual retention journey followed by the prescribed same previous/current pair and all PAYWALL A/B/C evidence, independently checked against admitted observations.
- Zero uncertain delivery and zero uncertain resends; confirmed closure of both owned browser contexts/groups.
- All old queues unchanged; identical 17-file runtime freeze, pinned product/library/fixtures, and six served-file before/after checks.

Only `TOKENMAXX/deepseek-v4.1-flash-free`, concurrency 2, and zero paid fallback are authorized. A failed or partial smoke cannot authorize expansion, and evidence from separate failed roots is never pooled into this gate. A product failure is still an executed criterion when supported by actual admitted evidence.

After R5 is terminal, integrate the independently reviewed correction, validate the R6 launcher selection, commit/push the source, verify the exact remote SHA and preflight, then launch R6 once. Only a passing and independently reviewed R6 authorizes `.ux-loop/peekly-completion32-pinned-20261115` with the identical frozen runtime and inputs. Old-23 improvement is counted only for matched passed/failed outcomes; not_run, N/A, and unassessed earn no execution credit.
