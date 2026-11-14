# R5 independent smoke — exact close contract

R4 was paused after a code inspection found that the new host close response included diagnostic fields while the existing ScaleExecution/AgentExecution callers require exactly `{"stopped": true}`. All in-flight R4 responses settled before exit. Both contexts closed, no close operation had been dispatched by a job, and no uncertainty occurred. R4 remains paused and immutable; it is not resumed.

The mismatch was reproduced offline through actual Queue and ScaleExecution: both fixture sessions became blocked with `worker_stop_unconfirmed`, despite confirmed process exit. The fix preserves the exact wire result and keeps rich diagnostics in the separate lifecycle record. New integration regression verifies actual current-valid receipt finalization and the failure/ownership-retention path.

## Predeclared fresh pair

New root: `.ux-loop/peekly-completion-smoke-r5-20261115`. Personas **022 + 031** were not used in completion R1–R4. They have the same ordered success/recovery/requirement records and PRD context as 021/029, independently checked against current revision-1 profiles and the old plan.

| Persona | Current profile SHA-256 | Old 65f job | Old success results |
| --- | --- | --- | --- |
| PER-PEEKLY-V2-022 | dc997a81822d6d77c705795ede852ede13a103e8d214b40e8b7b65c4d220df26 | S-mnemkabchmofljkacpjkooai | passed / not_run / not_run |
| PER-PEEKLY-V2-031 | f380157b348b760778bd9fd0c2c8f5c842b230bd05922841a07d0f5509e447f7 | S-jcbmmflngenhiaonjnpggfdi | passed / passed / not_run |

The matched baseline is **three not_run among six success criteria**, because 022 also had IDENTITY unexecuted. Do not reuse the earlier pairs' baseline of two. The gate still requires all six criteria actually executed (passed or failed), no success N/A, both targeted UNKNOWN/PAYWALL flows, two valid completed sessions, zero uncertainty/resends, confirmed closure, old queues unchanged, identical source/input freeze and six served-file before/after checks. No gate requirement is relaxed.

Only `TOKENMAXX/deepseek-v4.1-flash-free`, concurrency 2, no paid fallback. Every job/context/call identity is new; no old uncertain request is retried. No failed smoke's completed/partial evidence is combined into this gate.

After this gate and independent evidence review, use the same frozen runtime/product/fixture/library bytes for `.ux-loop/peekly-completion32-pinned-20261115`. Raw smoke, raw cohort and independent review remain separate. Old-23 improvement counts only matched passed/failed outcomes, excluding not_run, N/A and unassessed.

