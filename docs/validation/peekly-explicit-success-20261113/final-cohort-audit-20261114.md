# Final cohort audit — 2026-11-14

## Result: 32-persona aggregate is not yet supportable

This addendum records the evidence actually present in the approved execution worktree. It does not convert queued or uncertain sends into completed sessions, and it does not replay any uncertain send. The original persona files, queue databases, observations and screenshots remain untouched.

### Three-column comparison

| Measure | First run `696dbe3` | Verdict revision `cb0188d` | Latest independently verifiable evidence |
| --- | ---: | ---: | ---: |
| Cohort target | 32 | 32 | 32 |
| Session pass | 0 | 4 | 1 in the r4 slice; r5 re-observation of persona 031 is inconclusive |
| Session fail | 2 | 0 | 4 in the r4 slice |
| Session inconclusive | 30 | 7 | 7 in the r4 slice; r5 persona 031 inconclusive |
| N/A / unassessed | 0 | 21 | Not safely aggregatable across the incomplete queues |
| Success criteria passed | Not retained | 22 | r4 completed receipts: 20; r5 persona 031: 2 (overlapping persona; do not add) |
| Success criteria failed | Not retained | 0 | r4 completed receipts: 4; r5: 0 |
| Success criteria not run | Not retained | 6 | r4 completed receipts: 19; r5: 2 |
| Success criteria N/A | Not retained | 0 | r4 completed receipts: 9; r5: 0 |

The r4 counts above are calculated only from its 12 completed receipts, not its entire 16-job plan. The r5 receipt is a second observation of `PER-PEEKLY-V2-031`, already present in r4, so its criterion counts are shown separately and are not added to the r4 totals.

### Queue-state reconciliation

| Queue | Jobs in durable SQLite state | Interpretation |
| --- | --- | --- |
| `peekly-host-protocol-followup16-20261114` | 14 queued, 2 uncertain | No completed jobs are recorded in this queue. This contradicts the earlier handoff statement that 14 were complete. |
| `peekly-host-protocol-followup16-r4-20261114` | 12 complete, 1 queued, 3 uncertain | 12 valid completed receipts; 4 jobs must not be represented as completed. |
| `peekly-host-protocol-followup16-r5-20261114` | 1 complete | `PER-PEEKLY-V2-031` re-observed; session outcome remains inconclusive. |

All five uncertain entries described in the handoff remain quarantined and were not resent. The initial queue's 14 queued entries are not evidence of execution. The r4 queue is a separate 16-job plan and overlaps the r5 persona 031 re-observation. The available files do not establish a non-overlapping, evidence-complete set of 32 final persona outcomes. Therefore no 32-persona pass/fail/inconclusive/N/A total is published here.

### Verified r4 and r5 observations

- r4 completed receipts: 12 distinct jobs; 1 session pass, 4 session failures, 7 inconclusive.
- r4 criterion units from completed receipts only: 20 passed, 4 failed, 19 not run, 9 not applicable.
- r5: `PER-PEEKLY-V2-031`, one completed operational session, one inconclusive UX outcome. It verified the sample relationship list's copy/save controls and a safe recovery from a rejected click. Only 2 of 11 required distinct snapshots were imported; remaining retention and full Pro/paywall gating were not executed within the fixed turn budget.
- r5 execution used 24 TOKENMAXX model calls and 22 browser tool calls; no paid fallback was attempted. Provider-reported billing fields were absent and no provider invoice was independently verified. Do not interpret the reviewed free-route estimate as an invoice.
- No live real-user evidence or product-readiness conclusion is established.

### Defect separation

**Product UX finding carried forward (P3):** the relationship-list explanatory copy omits the former-mutual inclusion rule. Existing source anchor: `src/components/ResultsTab.tsx:272`; the earlier evidence anchor is persona 020 `obs-2` / `browser-00019.png` as documented in the main report. This finding was not newly browser-retested in r4/r5.

**Execution/runner defects:** the prior `host_protocol` receipt problem and the concurrency-slot retention for uncertain sends are runner/protocol issues, not Peekly product defects. The two local runner fixes in commits `5651c8e` and `8e9e065` address denied browser storage access and return of concurrency slots for quarantined sends. The r5 report records no `host_protocol` issue for its completed receipt.

**Verdict/criterion limitations:** r5's retention and paywall criteria are `not_run`, not failures. The incomplete 11-snapshot import is a bounded execution limitation and does not prove a product retention defect. No model-inferred failure is promoted to a product defect without its own criterion evidence.

### Evidence paths

- Initial queue: `.ux-loop/peekly-host-protocol-followup16-20261114/stage-33/queue.sqlite`
- r4 queue and report: `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/queue.sqlite` and `report.json`
- r4 stage summary: `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/stage-summary.json`
- r5 queue and report: `.ux-loop/peekly-host-protocol-followup16-r5-20261114/stage-33/queue.sqlite` and `report.json`
- r5 stage summary: `.ux-loop/peekly-host-protocol-followup16-r5-20261114/stage-33/stage-summary.json`

The SQLite queues were opened read-only for this audit. Raw queue databases, model ledgers, persona files, observations and screenshots are not copied into this report or modified.

## Publication decision

The two runner-fix commits are locally present and the remote branch was verified at `0ed84ec98e0a241034e998ac7ace7185b9c24385` before publication. This audit deliberately records the missing 32-persona evidence rather than manufacturing a complete aggregate. The report's three-column comparison is complete for the two historical baselines and the currently verifiable r4/r5 slices; a final 32-persona verdict remains unassessed until the missing queue evidence is recovered or the outstanding jobs are explicitly authorized for execution.
