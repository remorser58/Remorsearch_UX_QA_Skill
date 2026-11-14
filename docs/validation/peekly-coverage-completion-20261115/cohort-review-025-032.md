# Cohort review — personas025–032

## Draft checkpoint

This fragment reviews saved evidence from fresh `stage-32`, canonical plan `59f2c770425f85dd834542349f1915f084ca8fc6129c421cc907b4127d0212d8`. Global raw-summary and artifact-audit hashes are **pending**. Reconcile the draft against the terminal eligible report before application. Raw receipts and queues are unchanged; new model/browser calls and queue writes: **0**.

| Persona | SEARCH / SAMPLE | PRIVACY-LOCAL / RETENTION | DELETE / PAYWALL | Recovery | Eligibility |
| --- | --- | --- | --- | --- | --- |
| 025 | Unassessed | Unassessed | Unassessed | Unassessed | Review delivery uncertain; no completed-session credit |
| 026 | P → P | P → NR | F → F | N/A → N/A | Completed sealed receipt |
| 027 | P → P | P → NR | F → F | N/A → N/A | Completed sealed receipt |
| 028 | P → P | P → NR | F → F | P → P | Completed sealed receipt |
| 029 | Unassessed | Unassessed | Unassessed | Unassessed | Review delivery uncertain; no completed-session credit |
| 030–032 | Pending | Pending | Pending | Pending | Await eligible completed receipts |

Current reviewed subset: **12 decisions** — success P3/F3/NR3/N/A0; recovery P1/F0/NR0/N/A2.025 and029 each have four unassessed criteria outside that assessed subtotal. No old23 SEARCH credit is assigned to025 and no old23 PAYWALL credit to029. Partial execution does not create a completed receipt.

## Case-specific evidence for026–028

| Persona | Import / actual list / typed result | Privacy candidate screens | Delete confirmation / result | Recovery |
| --- | --- | --- | --- | --- |
| 026 | obs4 /5 /6; `upload-38` | guide3; policy12 |15 /16 | No triggering failure |
| 027 | obs4 /5 /6; `upload-38` | guide3; policy11 |14 /15 | No triggering failure |
| 028 | obs5 /7 /8; `upload-43` | guide4; policy13 |16 /17 | Known failed clicks3 /6, corrected at4 /7 |

### SEARCH: three fresh passes

Each job independently imports pinned `peekly-search-ready.zip`, completes a changed persisted state, opens the ordered twelve-key list `synthetic_search_outgoing_00` through `_11`, and exposes a visible enabled search input. An actual admitted type action retains `synthetic_search_outgoing_05`, with expected/actual query SHA-256 `cf12574baf4b6af9bc8ac4133367ad0e89ab059a2f32775053d92e6624c30dd5`, on the same selector/import/storage anchor. Exactly the `_05` row remains. Registered PNGs corroborate the entered query and single result. Each evidence reference belongs to its own fresh receipt.

### PRIVACY-LOCAL: three P → NR corrections

The exact criterion requires the product’s own local-processing and no-send notice to be **visible**. For every case, the complete admitted action sequence and all candidate notice screens were checked. The open import guide’s DOM contains the relevant copy, but its short screenshot exposes the heading, progress tabs and chooser; both notice facts are below the capture. The later privacy-policy capture shows its heading and initial login/credential paragraph. The relevant relationship-data local-processing and no-send sections remain below the captured area. Later actions switch to deletion without scrolling that privacy content.

**Neither relevant relationship/file notice fact is exposed in any admitted view for these cases.** Coherent separate visible views would have sufficed; no same-frame requirement is imposed. Generic login/credential copy, returned DOM membership, and the host-enforced network block are not substituted for the required facts. This is `judge_unfounded_execution` with `runner_limitation`, not a claim that the product lacks the text.

### DELETE: three scoped product failures

Each actual final confirmation is visible and followed by a hit-tested, dispatched `모두 지우기` click and completion toast. The required `peekly_state_v7` key remains or is recreated. This fails the assigned removal-of-keys criterion.

The filtered storage digest after deletion is `7b3f3a770f0ac89471a660ccfe9a54f5de96b387ebb22d307e06fadb84f77355`, equal to each fresh initial empty-profile digest. **Key presence does not prove retained personal or imported relationship data.** Native iOS WebView/cookie and notification cleanup is outside this desktop scope.

### Recovery:026/027 N/A,028 P

026 and027 each have one successful import and no triggering recoverable browser/import failure. Their later deletion assertion failure alone is not such a trigger.

028 has two actual, definitely rejected browser actions. Obs3 and6 explicitly state that the click was **not dispatched** because the target was not allowed or visible. Their returned current observations expose the correct visible enabled controls and preserve state. Corrected clicks at4 and7 succeed. The import at5 changes persisted state; the list/query at8 is usable and correct. This supports the literal recovery criterion and preserves raw P. No uncertain operation was resent.

## 025 — preserved transport uncertainty, all criteria unassessed

Job `S-ocglonedchibimababmanahg` is uncertain at review phase, turn19, with18 admitted partial observations and **no result**. Its checkpoint seal matches. This case has no helper decisions.

- Uncertain review operation: `op-420e1a6c72f19969085fcab1f74c90ed1d667fb1`, slot0.
- Original request SHA-256: `74855f10d4e71d04738725cf57ba9a4b1ce0431b498ddf4523a967271f4789be`; payload and context/operation envelope bindings match.
- One free TOKENMAXX attempt; `transport_or_protocol_error`, `TimeoutError`, reason `timed out`, elapsed150.0059s.
- Delivery state `uncertain`; `can_retry=false`; no reply exists and no resend was made.
- Transport evidence was independently captured at2026-11-14T21:40:33.056093+00:00; the live ledger snapshot hash is recorded in JSON. It is an as-of snapshot, not the eventual terminal ledger pin.
- Owned closure remains pending the stage’s terminal audit.

## 029 — preserved review uncertainty and partial artifacts

Job `S-cmkbfkbjcjonakfbhgkpeaod` is uncertain at review phase, turn64, with **62 admitted partial observations and no result**. All four assigned criteria are **unassessed** on the completed-session basis. There are no helper decisions and no old23 PAYWALL execution credit for this case.

- Independent read-only audit: 2026-11-14T21:54:49.988539+00:00.
- Original uncertain review operation: `op-3dec06a91069c876ebef12568133b8814b406db3`, slot0.
- Request SHA-256: `26f901de72b152e8b5265a0f1837927a701b29d9ab4a5928573f5e1321ed6edf`; payload and operation/context envelope bindings match.
- Started 2026-11-14T21:51:24.783Z; saved deadline 2026-11-14T21:54:24.783Z; no reply or ended timestamp exists.
- Exactly one free TOKENMAXX ledger attempt: `transport_or_protocol_error`, `TimeoutError`, reason `timed out`, elapsed **150.6345 seconds**. Delivery `uncertain`, `can_retry=false`.
- Checkpoint SHA-256 `bdcd08570b606ebbbdae1e6fd1929b3f7172c95f795a8486ebc5194161692e1f` matches its canonical contents.
- Preserved partial evidence: **124 registered-preview artifacts / 3,392,653 bytes** — 62 execution logs and62 PNGs. Every actual hash matches its sealed checkpoint registration, and all observation-log/body/context bindings match. The JSON fragment retains every actual artifact hash in `partial_artifact_preservation`.
- Two supplemental lifecycle files are separately hashed. They and the partial evidence confer no completed criterion credit.
- No close operation has completed for this job at this checkpoint; owned closure remains pending the stage’s terminal audit. No cleanup or resend was performed.

The live ledger snapshot hash `d918232eaf029142e36eedf55e65d84e14db8f8152ac27c86974de9f726bc479` is preserved as an audit-time receipt; it is not substituted for the eventual terminal ledger pin.

## Bindings and validation

| Persona | Result SHA-256 | Registered files / bytes |
| --- | --- | --- |
| 026 | `f0d8543cf576116d4229478b04d8e964591cc3b28d0cc56b18482efdca103392` | 32 / 846154 |
| 027 | `8c37f2dbc59ee7157d2ebc46e2295671b9890813bf0daef08339f975d7a250fb` | 30 / 797267 |
| 028 | `78cfaa5eb794778c35600c84aa69ca630faec4346b4e0f5effb4459763de8584` | 34 / 889271 |

All registered artifacts in these completed cases were rehashed with no mismatch. Result/checkpoint/first-judgment seals and receipt identity bindings match. Saved observation logs match their admitted checkpoint bodies and fresh bindings. Exact receipt-relative paths, hashes, observation IDs, requirement IDs and setup/action/result/context purposes are in `cohort-review-025-032.json`; every decision cites a registered result-purpose execution log. Terminal eligibility and shared raw/audit pin reconciliation remain pending.
