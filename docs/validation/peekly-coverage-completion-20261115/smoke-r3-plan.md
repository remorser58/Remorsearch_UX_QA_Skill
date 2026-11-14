# Independent R3 smoke selection

Declared before live R3 execution on 2026-11-15 (Asia/Seoul).

R2 finished with one completed session (021) and one uncertain session (029). Its HTTP-502 call `op-f52816c286aa230cea3c061f5e4eee78205f3be0` was sent once, has `can_retry=false`, and remains quarantined. R2 failed its gate. Its raw queue, observations, receipt and ledger are preserved; see `smoke-r2-summary.json` and the artifact audit. Provider cost fields were absent, so zero configured policy cost is not an independently verified invoice.

The user's authorized sequence remains a complete two-person smoke followed by a new 32-person cohort using only the approved free TOKENMAXX route. R3 uses two different saved personas with the same ordered obligations, in a new root `.ux-loop/peekly-completion-smoke-r3-20261115`.

| Persona | Ordered success criteria | Prior 65f status | Library revision | Profile binding SHA256 |
| --- | --- | --- | ---: | --- |
| PER-PEEKLY-V2-023 | IMPORT-MISSING; IDENTITY-LIMIT; IMPORT-SNAPSHOT-UNKNOWN | passed / passed / not_run | 1 | 5543454d547152174327499077dfce490a216d14edc58fd8feadb183a3bc3590 |
| PER-PEEKLY-V2-030 | SAMPLE-EXPORT; SNAPSHOT-RETENTION; PAYWALL-BOUNDARY | passed / passed / not_run | 1 | 6efec52667589fcf70ab72beb55a57de93894abe7b891c0e51130df8ab126260 |

These ordered requirement records and PRD contexts are identical to 021 and 029 respectively. Both personas are active in the verified v4 library. Neither was selected in completion smoke R1/R2; this is not a claim that they have never appeared in historical cohorts. The matched baseline is still **two not_run among six success criteria**.

The two R3 sessions each start from their own fresh owned context with new job and operation IDs. All 331 prior jobs remain excluded from submission, and all 34 prior queues remain read-only. The preserved R2 029 request is never resumed or resent. R2's completed 021 is not combined with a later session to manufacture a passing two-person batch.

The gate remains unchanged: two valid complete sessions, all six success criteria actually executed, no success N/A, no uncertain model/tool operation, confirmed browser shutdown, unchanged prior queues, and matching frozen inputs plus actual served bytes before and after execution. A real product failure is executed coverage. The IDENTITY contradiction must be independently evidenced in R3's own job rather than copied from R2's case-specific review.

Only the smoke selection and default result root changed. The runner behavior, judgment functions, fixed product 51110f4, fixtures, library, route and budgets are unchanged. R3 freezes this new launcher configuration, and the future 32-person cohort must match that exact freeze and use R3's passed gate.

Validation: the same focused target/launcher/finalizer/old-launcher/history suite now has **62 passing tests**, including a regression rejecting the prior pair as a substitute. Runtime 0.577 seconds; no skips/failures. Normal CLI preflight passed with 34 prior queues, 331 forbidden job IDs and 41 preserved historical uncertain rows. No live model or browser was called for selection verification or preflight. R3 must still supply its own actual result.
