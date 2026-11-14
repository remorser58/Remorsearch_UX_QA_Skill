# Browser lifecycle repair validation before R4

The failed R3 root and its two uncertain tool operations remain unchanged. This change addresses runner startup/teardown, not Peekly product behavior or a reclassification of missing UX evidence.

## Implementation and independent review

The Python host now owns a new POSIX process group per fresh context. Once dispatch might have occurred, timeout, cancellation or an invalid reply identity poisons the channel; no new command consumes its late response. Cleanup uses only the recorded owned group, waits for Node exit and group disappearance, and retains ownership on failure. A closed context cannot be restarted. Durable records cover ownership, failures and closure; ordinary dispatch/reply progress stays in memory rather than adding two fsyncs per tool.

The Node driver retains complete validation of all 544 frozen fixtures, now with asynchronous reads and cancellation checks. Its total startup budget is 60 seconds; Python allows 70 seconds. CDP discovery/body and WebSocket opening are bounded. Shutdown waits for actual child exit after TERM/KILL, understands signal exits, closes only owned proxy connections, and preserves diagnostics. Python close is bounded at 12 seconds before owned-group cleanup.

The live stage writer preserves an actual returned report and the router ledger even if teardown fails, records execution error and shutdown error separately, and gives the original error priority over diagnostic disk failures. It never fabricates a completed report if execution did not return one, nor a successful stage summary after failed teardown.

Independent read-only review found no further blocking lifecycle defect. The driver's JSONL is bounded best-effort diagnostic output; if its first exclusive file creation times out after creation, later appends may be unavailable. Host ownership and confirmed group exit remain authoritative. This limitation does not change an uncertain delivery into a success.

## Regression

Final combined Python command:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests /Users/m4mini/.local/bin/python3.11 -m unittest \
  test_scale_browser_lifecycle test_live_browser_recovery test_peekly_legacy_seed \
  test_scale_browser_guardrails test_peekly_completion_target test_peekly_completion_launcher \
  test_peekly_completion_finalizer test_peekly_coverage_launcher test_peekly_history_navigation
```

Result: **88 tests, zero failures/skips, 3.142 seconds**. Log: `.ux-loop/peekly-completion-r4-regression-20261115.log`, SHA-256 `9800b1bfbe3c7952e5697add90e3506c23931572345e70b5a0af468d6336644a`.

The Python guardrail case invokes the Node suite. Its separate direct run with the prepared Node 26 runtime passed **61 cases: 17 new lifecycle plus 44 prior guardrail/scroll/legacy cases, zero failures/skips, 3.929 seconds**. These counts describe the two runners and must not be added as disjoint tests.

Coverage includes late responses, cancellation and stdin backpressure, response identity mismatch, absent ownership, failed cleanup retention, a real owned Python child/descendant process group, diagnostic disk failure, cancelled shutdown, late fixture reads, CDP header/body stalls, WebSocket timeout/pre-open close, signal exits, delayed KILL exit, and proxy connections/listen state. No model was called by regression.

## Actual owned-browser lifecycle probe

A separate zero-model probe at `.ux-loop/peekly-browser-lifecycle-probe-20261115` started a fresh owned context, admitted one real observation, and confirmed teardown in **4.816 seconds**. It counted **zero persona sessions and zero model calls**; it is not the two-person UX smoke.

The driver reported shutdown; the host also used its owned-group fallback (`forced_cleanup=true`) and independently observed the group gone. Final lifecycle phase is `closed`, channel not poisoned, `owned_group_exit_confirmed=true`. Before/after all six served target bytes matched, and the source/fixture/library freeze remained identical.

Probe summary SHA-256: `56508047d3566945172ddcf7622953619dcaf5703b2865a9ea16943161e15ba5`.

## R4 admission

Offline R4 preflight passed with 35 old queues, 333 excluded prior job IDs and 43 preserved historical uncertain rows. Personas 024/032 are predeclared in `smoke-r4-plan.md`. No old operation is resumed.

This validates the runner changes and actual lifecycle only. Reduction of the matched two-not-run smoke baseline and the full old-23 set still requires fresh completed persona evidence. The prior packaged Node 22 release check limitation remains; these results do not establish packaged release readiness.

