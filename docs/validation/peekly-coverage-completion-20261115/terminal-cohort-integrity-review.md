# Terminal cohort integrity review

Read-only audit of `.ux-loop/peekly-completion32-pinned-20261115/stage-32`, after the run finished at **2026-11-14T22:14:57.374160+00:00**. Runtime remains the 17-file freeze at `f50d082a197e683b5961d17919fe219dc48c4d55`. This review made no model, browser or HTTP requests, instantiated no Queue, and ran no tests.

## Terminal population and exclusions

The SQLite queue has **28 complete / 4 uncertain / 0 running / 0 queued**. There are **27 eligible operational completions** and **115 assessed criterion rows**. Of 136 planned rows, 21 remain unassessed because five sessions are excluded.

| Persona | Preserved terminal state |
|---|---|
| 011 | Uncertain tool; `legacy_seed_task_not_authorized` |
| 014 | Uncertain tool; `cdp_timeout:DOM.getDocument` |
| 025, 029 | Uncertain review delivery; model timeout |
| 030 | Queue complete, but `operational_completed=false`, `host_protocol`, no sealed first judgment; local payload-bound diagnosis is recorded separately |

All four uncertain operations retain a null reply and have **no later queued operation for the same job**. Cleanup does not promote their criteria. The 030 fallback verdicts remain excluded.

Raw receipt totals are success **82 passed / 6 failed**, recovery **6 passed / 21 N/A**, and zero raw not_run: **88 P / 6 F / 0 NR / 21 N/A** overall. The raw old-23 mapping is 20 passed and 3 unassessed (025 SEARCH; 029/030 PAYWALL). These raw judgments await the separate semantic review. `automated-outcome.json` correctly retains `run_state=incomplete_preserved`, `semantic_review_status=pending_manual_review`, and `coverage_target_met=null`.

## Owned browser closure

The lifecycle summary contains exactly the 32 planned contexts. Every context has phase `closed`, `stopped=true`, and `owned_group_exit_confirmed=true`; unclosed contexts and shutdown/diagnostic errors are empty. Independent process inventory at **22:16:29.532696 UTC** found no remaining recorded Node PID, owned PGID, or browser-profile command line.

Closure was not uniformly graceful:

- **012** (Node PID 40574) and **018** (47707) required `forced_cleanup=true`; both also record `driver_shutdown_confirmed=true` and confirmed group exit.
- **014** (43492) records `driver_shutdown_confirmed=false` and `forced_cleanup=false`, while its owned group exit and stopped state are confirmed.
- Thus **32 owned groups closed, 31 driver acknowledgments, two forced cleanups** is the supported statement.

All 28 acknowledged queue close operations contain exactly `{"stopped":true}` in the reply envelope's `result` field. The four uncertain sessions were covered by overall host shutdown without adding a queue close or resending the uncertain action.

Lifecycle summary SHA-256: `7ee34d10e01b41ce2bd54af5999895219dad2775e71cc918ed863a708c164f26`.

## Free route and delivery accounting

Independent ledger recomputation finds **642 logical calls / 651 actual attempt events**, comprising **649 received-success events and two uncertain transport timeouts**. Nine separate quality diagnostic markers bring the ledger to 660 rows; each marker matches an already-received response. There are 633 one-attempt calls and nine two-attempt calls. Every additional attempt follows known received-content quality rejection. Both uncertain model call IDs occur only once, with no later resend; there are no in-flight guards.

The plan has one live local-router provider, zero configured prices and budget, and the ledger requests only `TOKENMAXX/deepseek-v4.1-flash-free`. Received responses name `deepseek-v4.1-flash`; configured fallback order contains only that approved route and fallback attempts are zero. No priced route or uncertain resend was observed. Provider cost fields are missing for all 651 attempt records and `provider_invoice_verified=false`; the configured free route is not independent invoice proof.

Final ledger SHA-256: `15ed29997181435272f3217ebbd19fb3969fa3bec0b7c1408500c6ce9cfca775`.

## Frozen inputs and historical queues

Recomputed hashes match all **17 runtime files**, **544 fixture files plus manifest**, the saved persona library, **319 archived product source files**, and **13 dist files**. The runtime files also have no diff against the frozen commit. Product build/source manifests, build provenance and PRD pins match. The product remains commit `51110f4c569673faa8d242d5b85c4b47afb54cbb`; this audit makes no claim about a newer product revision.

Saved HTTP receipts at **20:54:59.700186** and **22:14:57.359835 UTC** match the pinned index and five entry assets for owned port 4175. This audit checked those existing receipts and disk bytes; it issued no new HTTP request.

All **38 prior queues** were opened in SQLite read-only/query-only mode. Their recorded job/status/problem and pending-operation metadata snapshots are unchanged. This is a metadata-snapshot claim, not a claim that every historical database byte was re-audited. The before/after aggregate is `fa7f89c44ecfb74d8b9eb9c3d633bbf7a90311e5d375a6e03b7ebf427dfb20fa`. The 32 fresh job IDs have no overlap with the 339 forbidden prior IDs; the 45 prior uncertain jobs remain preserved.

## Raw publication and byte audit

All five finalizer-owned files were observed and byte-compared successfully with publication commit `3248e54fd3e0990a5004de18a2decc6a7f140da0`. Finalizer PID 33511 was absent after publication; it was not relaunched.

| File | Bytes | SHA-256 |
|---|---:|---|
| summary.json | 690599 | `95c043fdd25492bc73772b26fd1c15e0bc9770c24f8caa6c810469db0341c9ac` |
| comparison.md | 13990 | `0cc6a18cb8196cbd932dd1b7881174e5a126a30c4e76564e4a1dacf25b21b4cc` |
| not-run-23-baseline.json | 52007 | `66823c35e27e6af1c5017c2ed89678c5b1e128bbb09c5ca838eea5dd0fe6fa0a` |
| artifact-audit.json | 19339 | `7483eca3a48afac5341a7db63e6d0ac93a37a1ed2bdc962e9ffd23db4951640d` |
| automated-outcome.json | 9946 | `45f08ec1cd2d7e695a3806e78c071eb3eea5aa0d6c1f7f42e8cace70943b4139` |

Independent byte checks reproduced **844 registered files / 22,414,369 bytes: 419 execution logs and 425 PNGs, from the 27 eligible sessions only**. Excluded sessions' partial artifacts are preserved separately and are outside this denominator. All 32 checkpoint seals, 28 stored result seals, and 27 eligible first-judgment seals match; there are zero mismatches.

The 12 raw-summary source references, nine artifact-audit source references, and four generated-file pins in automated-outcome also match. The plan seal agrees across envelope, queue and report. Its envelope file hash is `660406bc74f05921184be02549ad9ee39a456c33e820283ead5b5476a2d76213`; input provenance is `c530faba1c2d91190b068308cc71adaa37edafa10e77726a71c7f1dabffb4468`. Byte integrity establishes preservation and eligibility inputs; the assigned-criterion semantic conclusions remain with the independent review.
