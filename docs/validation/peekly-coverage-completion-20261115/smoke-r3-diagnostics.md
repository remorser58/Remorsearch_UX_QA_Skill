# R3 smoke — preserved uncertainty and owned-process cleanup

Audited 2026-11-15 03:41 Asia/Seoul. Runtime revision: `054342d099648104fd23aae29953f9a6399f3e73`. Root: `.ux-loop/peekly-completion-smoke-r3-20261115`.

**R3 did not pass the smoke gate. No 32-person cohort was started from this run.** Both personas stopped at the first host tool, with no admitted observation and no completed receipt. The two model responses were received; the two tool operations remain uncertain.

## Actual terminal state

| Persona | Job | Model delivery | Tool state | Observations |
| --- | --- | --- | --- | ---: |
| 023 | `S-obfofmpdpeibgbipcfgdlcoa` | reply_received | uncertain / TimeoutError | 0 |
| 030 | `S-nebbkpjgckcjdeeachjcglag` | reply_received | uncertain / TimeoutError | 0 |

The launcher records `stopped_preserved`, reason `browser_shutdown_unconfirmed`, from 03:25:03 to 03:26:04 Asia/Seoul. Normal final report, stage summary and final router ledger are absent; the live router ledger survives. Exact model and tool call IDs, hashes and query results are retained in `smoke-r3-diagnostics.json`.

**Six success criteria and two recovery criteria are unassessed.** They are not six new not_run, eight failures, or evidence that Peekly regressed. This run contributes no reduction credit to the prior 23 unexecuted criteria.

## Delivery, integrity and cost

- Exactly two actual model attempts, two distinct call IDs, two received responses and no model-delivery uncertainty. Both requested `TOKENMAXX/deepseek-v4.1-flash-free`; the route returned the accepted `deepseek-v4.1-flash` alias. No paid fallback or uncertainty resend was observed.
- Both first tool operations remain uncertain, without reply or retransmission. No raw queue, receipt or ledger was edited by this audit.
- Both checkpoint seals, the plan seal, all four request **payload** seals and both received reply seals match. Queue request_sha seals the payload, not the entire request envelope.
- The provenance file hash matches run-status. A fresh read-only snapshot of all 34 prior queues at 03:41:46 reproduces `73d8a2ac24755069abc4110bca52357d87b91ba64b2e6c831b87ac3eb3b29f8d` exactly.
- Saved launcher before/after target checks cover six served files on port 4175. This audit does not re-certify newly edited runtime bytes against R3's old freeze.
- Input/output tokens: 17,044 / 87. Both responses omit provider cost; policy budget zero and free routing do not establish a verified provider invoice.

## Browser cleanup is a separate postmortem action

After connector recovery, a read-only process listing found orphan main Chrome PID **33010**, PPID **1**, with the exact private R3 persona-030 profile. Helpers 33035, 33038, 33041, 33044, 33054 and 33205 shared that profile. This is concrete evidence of an execution cleanup failure.

The parent rechecked that exact process/profile and sent SIGTERM only. Its receipt is `.ux-loop/peekly-r3-postmortem-20261115/owned-chrome-cleanup.json`, SHA `232a0e2f2f04761465d2615f81d0c38f83e2a23d42af88356caa00f1f2edcfe4`. It reports the main PID absent, no SIGKILL, and no historical receipt change. This auditor independently confirmed **zero exact R3 profile process matches at 03:41:03**.

That postmortem cleanup does **not** turn the original shutdown into a confirmed normal shutdown, does not change either uncertain operation, and does not make the failed smoke usable for cohort expansion. The saved data does not identify whether startup or the first action consumed the 25-second host timeout; phase diagnostics were missing. Disk/tunnel latency is not established as the root cause.

## Fresh smoke selection, declared before any new run

After the lifecycle repair and regressions, use a fresh run for **024 + 032**. Neither was used in completion smoke R1/R2/R3. Current library entries are active revision 1; their PRD contexts and profile requirement IDs match 021/029, and the old cohort's ordered success/recovery/requirement records match that original pair exactly.

| Persona | Matched success requirements | Prior outcomes | Prior not_run |
| --- | --- | --- | ---: |
| 024 | MISSING, IDENTITY, UNKNOWN | passed / passed / not_run | 1 |
| 032 | SAMPLE-EXPORT, RETENTION, PAYWALL | passed / passed / not_run | 1 |

The denominator remains six success criteria and baseline not_run remains two. The alternative 022 + 031 has three baseline not_run because 022 also did not exercise IDENTITY; that alternative must not silently inherit the two-not-run denominator.

Use new job, context and call identities and a new directory. Preserve the full gate: two valid complete sessions, six executed success criteria, no success N/A or uncertainty, confirmed owned-browser shutdown, unchanged prior queues, free route only and identical input freeze. Do not combine the completed R2 session with another run's result to manufacture a passing pair.
