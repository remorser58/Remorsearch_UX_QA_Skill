# R5 smoke — two uncertain tool operations, evidence preserved

Runtime: `6046c7af218178ad2384900405cb428cd211072e`. Root: `.ux-loop/peekly-completion-smoke-r5-20261115`. Terminal state, ownership, source freeze and evidence integrity were independently audited on 2026-11-14 at 20:12–20:18 UTC.

**R5 failed the strict completion gate.** It ended at **19:35:20.869439 UTC** with **0 complete, 2 uncertain, 0 queued and 0 running jobs**. No completed receipt exists. All **6 success criteria and 2 recovery criteria remain unassessed on a completed-session basis**; reduction credit against the old 23 is **zero**. The selected pair's historical success-`not_run` baseline is 3. Product readiness and 32-person expansion remain false.

| Persona | Job | Terminal phase / turn | Acknowledged observations | Preserved failure |
| --- | --- | --- | ---: | --- |
| 022 | `S-jempbmnekmnoidfgnohkeofd` | tool / 10 | 9 | `host_execution_failed:TimeoutError` during `peekly-missing-followers.zip` upload |
| 031 | `S-pcngliijgicolppnjdbkipjn` | tool / 60 | 59 | `host_execution_failed:browser_action_failed:cdp_timeout:Page.captureScreenshot` during modal scroll |

These failures are classified as **runner/host transport and capture failures**, and do not establish product failures. Neither uncertain operation was resumed or resent during this audit. The retained queue control metadata is `running`, but the launcher's terminal state is `smoke_failed`, both job counts are settled as uncertain, and the owned processes are closed. Metadata was preserved without changing queue control.

## Operations, model delivery and seals

There are 140 queue operations: **70 model done, 68 tool done and 2 tool uncertain**. No review or per-job close operation was dispatched; global shutdown is recorded separately. There are no active intents.

- All **140 request-payload seals**, **138 received reply seals**, both checkpoint seals and the plan seal match. The plan hash also matches the queue's stored plan hash.
- The complete **285-entry event chain** validates, ending at `5eb6818fb3ee0fdc3c44c467d32cf53becea06579481df77268cd141605f14cb`.
- 022's uncertain operation is `op-93cda0d21d08f8dc859fc6c4aa4cb9ff0b63722a`; its `outcome_unknown` event is 19:10:53.362126 UTC. 031's is `op-75c37b4db94691e5fd7efa8f47274f44a76c0bec`, at 19:35:09.408332 UTC. Both retain null reply seals.
- The router records **70 distinct logical calls / 70 actual attempts**, one received successful attempt per call. All requests used `TOKENMAXX/deepseek-v4.1-flash-free`; the reported served model is `deepseek-v4.1-flash`. Final and live ledgers are semantically identical.
- There are no quality repairs, model delivery uncertainty, uncertain resend violations, unsettled or in-flight model guards, or paid fallback attempts. Input/output usage is **2,831,134 / 20,126 tokens**. Policy cost is zero; an independently verified provider invoice is unavailable.

The companion JSON preserves both uncertain request hashes, both checkpoint hashes, plan identity, all four saved run-status pins, source-file hashes and artifact hashes.

## Owned shutdown and process inventory

Both owned process groups have confirmed exits, with no unclosed context, execution error, shutdown error or diagnostic write error.

| Persona | Host channel | Host shutdown receipt | Owned group exit |
| --- | --- | --- | --- |
| 022 | poisoned by `TimeoutError` | `forced_cleanup: true`, `SIGTERM`, `driver_shutdown_confirmed: false` | confirmed |
| 031 | healthy | `forced_cleanup: false`, `driver_shutdown_confirmed: true` | confirmed |

022's driver lifecycle file also reports browser/proxy closure, but that does not replace the missing host protocol confirmation. The host correctly retains the forced-cleanup distinction. An independent process inventory at **20:12:20.230254 UTC** found **zero exact R5 profile, owned node PID or process-group matches**. The auditor performed no cleanup.

## What the partial observations preserve

### 022: validated UNKNOWN path before the upload timeout

Observation 1 only observes. Observation 2 performs the first mutating action, `seed_legacy_unknown`, on a fresh owned profile. Its receipt confirms the validated v6 → v7 migration, one UNKNOWN snapshot and empty active/comparison selections. By observation 7, the named current fixture has been imported and the retained-record notice shows both the exclusion explanation and the next-record explanation. The checkpoint's UNKNOWN preview is `passed`; **this remains partial evidence and supplies no completed-session credit**.

Observation 9 is the last acknowledged observation. A later `browser-00114.png` exists, with SHA-256 `b80d84a1e858054f5a30e8a9b25832268247b47d40c3fe87c024407704ba7442`. It is not registered in the checkpoint. Its existence does not prove that upload operation 10 returned a reply, that its validation was assessed, or that the session completed.

### 031: sample restriction and retention evidence; PAYWALL remains unproved

Observation 5 records the sample's copy/save controls as **visible and disabled**. Observation 44 follows **11 distinct retention fixture uploads** and records the actual **10-record** history count. The pinned previous and current fixtures appear in observations 49 and 52 respectively.

Observation 54 records six free comparison list rows in the DOM. The prior visual review found only a partial list in its **756 × 413** screenshot; the JSON does not substitute for full screenshot visibility. Observation 57 confirms the modal body moved 67 pixels with no background movement. Observations 58 and 59 show both date selectors as `disabled: true` and `visible: false`; the Pro explanation control is also `visible: false`. **Same-screen date-selector visibility and the Pro explanation are not proved**, so PAYWALL-B/C and the whole PAYWALL boundary criterion receive no completion credit. The subsequent screenshot timeout leaves operation 60 uncertain.

## Integrity and the time of verification

All **68 acknowledged partial observations** have their registered files checked against actual bytes:

| Persona | Observation JSONs | Registered screenshots | Total files | Bytes | Hash mismatches |
| --- | ---: | ---: | ---: | ---: | ---: |
| 022 | 9 | 9 | 18 | 467,807 | 0 |
| 031 | 59 | 59 | 118 | 3,191,338 | 0 |
| **Total** | **68** | **68** | **136** | **3,659,145** | **0** |

The JSON contains the complete 136-file manifest, plus actual hashes for seven supplemental capture/seed/lifecycle files. These are preserved partial-session artifacts, not completed receipts.

At **20:13:11.815738 UTC**, while main HEAD was `9e6b30bd7d40d43ba7d656f85fa2e0dc82b73b28`, all **17 frozen runtime source files matched**. Those same 17 hashes also independently match commit `6046c7af218178ad2384900405cb428cd211072e`. Parent integration later moved HEAD to `d6a3f25a4313248e3afb34e9c4b9b46ff325b54e`; this audit preserves the earlier verified freeze and does not claim the later repair is R5's runtime.

At the same pre-integration checkpoint, all **36 prior queues** were opened with SQLite `mode=ro`, `PRAGMA query_only=ON` and consistent read transactions, without constructing `Queue`. Every metadata snapshot matched the saved pre-run snapshot. The aggregate before/after/independent hash is:

`54b7d7bba6605d32a05e8fd35454bfa82b2177bc08afe6c868d1de665c4758d7`

At **20:13:13.182944 UTC**, all **544 fixture files**, fixture manifest, pinned persona library and build manifest matched their frozen hashes. The **319 product source files** and **13 distribution files** also matched. Product source remains `51110f4c569673faa8d242d5b85c4b47afb54cbb`, with source-tree hash `fa8c54630cfdef4260230d7b41a6a8a54405a97079961f66d2d43b47bd70c99e`.

All **6 saved HTTP entry-file receipts** match before (**19:07:45.203806 UTC**) and after (**19:35:20.867300 UTC**) the run, and match the frozen distribution. This verifies the preserved HTTP receipts; the audit did not open a browser or create a new run. All four run-status pins match the actual provenance, report, summary and router-ledger files.

## Continuation constraint

Preserve R5 and both uncertain operation IDs. Any source repair must use its own revision, freeze, fresh root and new identities. Require two independently valid completed receipts and the unchanged full six-success-criteria gate before expansion. This audit changes only these diagnostic documents; it does not authorize a resend, resume, queue mutation or new browser/model execution.
