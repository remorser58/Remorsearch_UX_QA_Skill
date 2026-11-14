# R6 independent completion review

## Decision and scope

**R6 meets the criteria execution gate for expansion:** two completed, sealed sessions; all six assigned success criteria actually exercised and reviewed as passed; no success `not_run`, no success `not_applicable`, and no uncertain operation. The launcher finished `smoke_passed` at **2026-11-14T20:46:51.072684+00:00**. This assessment does not establish product readiness or real-user evidence.

The one verdict correction is **024 recovery index 0: raw N/A → reviewed P (`judge_missed_execution`)**. The expected missing-list imports were actual product rejections, followed by a safely verified valid import. Raw receipts, queue rows, model replies, and artifacts remain immutable.

[The companion JSON](smoke-r6-independent-review.json) contains exact criterion text, requirement bindings, raw receipt/result seals, the independent review, live completion-guard proof, all **152 actual artifact hashes**, six supplemental hashes, and the full integrity findings.

| Item | Verified value |
| --- | --- |
| Run | `.ux-loop/peekly-completion-smoke-r6-20261115` |
| Frozen runtime | `f50d082a197e683b5961d17919fe219dc48c4d55` |
| HEAD during integrity audit | `f36c530084d28c1b264c2b7f199c534e99ea83a1`; all 17 runtime sources still match the frozen revision |
| Independent integrity audit | 2026-11-14T20:49:36.268600+00:00 |
| Queue | complete 2; uncertain/running/queued/blocked/cancelled 0 |
| Raw criteria | success P6/F0/NR0/N/A0; recovery P0/F0/NR0/N/A2 |
| Reviewed criteria | success P6/F0/NR0/N/A0; recovery P1/F0/NR0/N/A1 |
| Product revision | `51110f4c569673faa8d242d5b85c4b47afb54cbb` |
| Calls and route | 81 actual model attempts/replies, solely `TOKENMAXX/deepseek-v4.1-flash-free` |
| Audit effects | Read-only queue/evidence inspection; no model/browser calls, queue writes, runtime changes, cleanup, or uncertain resends |

The preserved queue control metadata says `running`; it is not evidence of a live job. The terminal launcher state, two complete jobs, zero pending operations, normal owned closures, and process inventory establish the completed state.

## Criterion review

| Persona | Index / requirement | Raw → reviewed | Actual execution and scope |
| --- | --- | --- | --- |
| 024 | success 0 / IMPORT-MISSING | P → P | Both separately uploaded missing-list fixtures rejected at obs-9/10 with the specified notice; persisted state unchanged. |
| 024 | success 1 / IDENTITY-LIMIT | P → scoped P | Actual two-known-snapshot comparison at obs-15 shows the limitation and one noncausal `이유 모름` row. The prescribed current-fixture direction was not exercised. |
| 024 | success 2 / IMPORT-SNAPSHOT-UNKNOWN | P → P | Validated seed is first mutation, followed by only one current import; retained unknown record excluded before the second known import (obs-2/5/6). |
| 032 | success 0 / SAMPLE-EXPORT | P → P | Sample relationship list inspected before imports; both copy/save controls disabled with sample-specific title explanations (obs-4). |
| 032 | success 1 / SNAPSHOT-RETENTION | P → P | Eleven distinct fixture names and hashes imported individually; actual saved history shows ten records at obs-41, before the normal pair. No storage-pressure branch triggered. |
| 032 | success 2 / PAYWALL-BOUNDARY | P → P | Pinned previous/current saves at obs-46/49; actual free names at 51; both disabled date selectors visible together at 57/58; actual Pro sheet and feature descriptions at 62, all on the same saved state. |
| 024 | recovery 0 | N/A → P | Rejections at 9/10 preserve state, close/reopen at 11/12, valid reselection/import at 13 changes persisted state, usable results follow at 14/15. |
| 032 | recovery 0 | N/A → N/A | All 13 imports complete new saves; no actual recoverable browser/import failure occurs. |

### Exact 024 binding, criterion text, and order

Persona **PER-PEEKLY-V2-024**, revision **1**, profile SHA-256 `1513b20a0904c715df26a27cdf13bb26ac492c5fdb3dee1edc91c9ac0169ab6c`, job `S-mfopimglobkoejplhjkbgpkj`.

The requirement bindings are IMPORT-MISSING → success index 0 / O-PRD-1, IDENTITY-LIMIT → success index 1 / O-PRD-2, and IMPORT-SNAPSHOT-UNKNOWN → success index 2 / O-PRD-3. The saved required-step checklist orders them **UNKNOWN → MISSING → IDENTITY**, while the criterion-index order is MISSING → IDENTITY → UNKNOWN.

Exact success index 0:

> 팔로워와 팔로잉이 모두 있어야 결과를 만들고, 하나라도 없으면 [팔로워 및 팔로잉]을 골랐는지 확인하라고 안내한다. [PRD-IMPORT-MISSING] both missing-followers and missing-following fixtures are rejected

Exact success index 1:

> 안정적 ID가 없는 백업 비교에는 이름 변경도 포함될 수 있다는 안내를 붙인다. [PRD-IDENTITY-LIMIT] comparison explains username change/account deletion as possible explanations and does not assert a confirmed unfollow cause

Exact success index 2:

> 목록이 실제로 비어 있었는지 알 수 없는 과거 백업은 비교 대상에서 제외한다. [PRD-IMPORT-SNAPSHOT-UNKNOWN] a legacy snapshot with unknown included-file provenance is excluded; a recognized empty import is known-empty

The actual 024 sequence is:

1. Observe (1), then validated legacy seed as the first mutation (2).
2. Import current once (5), expand the retained legacy notice and inspect exclusion (6).
3. Separately import missing-followers (9) and missing-following (10).
4. Close the import sheet (11), reopen the import entry (12), and import previous (13).
5. Scroll results (14), open the actual departed-follower comparison (15), then finish (model turn 16).

The saved IDENTITY checklist says: “Import both complete previous/current snapshots, then reveal and open the visible 팔로워에서 빠진 사람 control on current results.” The UNKNOWN checklist additionally calls for the normal previous/current pair after the exclusion checkpoint. This job did **not** upload current a second time after previous. Therefore its ordinary pinned current-direction workflow remains untested.

The observed comparison still exercises the assigned business criterion: two known snapshots are compared; its actual warning states that username change or account deletion may explain disappearance; the single admitted `evt_yuna.choi` row says `이유 모름`. The entire warning and row are visible in obs-15’s PNG. The upload-order deviation does not by itself make that actually exercised criterion NR. Conversely, the raw reason’s claim of all checklist steps/current-results order is too broad. This scoped pass neither transfers an old verdict nor establishes that the old causal-badge defect was fixed or retested in 024.

### Recovery correction is based on the assigned trigger

Both personas have this exact recovery criterion:

> If a recoverable browser/import failure actually occurs, perform the safe recovery and verify it. If no triggering failure occurs, report not_applicable; do not manufacture a failure.

The criterion does not say that the failure must be unexpected. A successful negative test or a done browser-tool operation is not a successful import: obs-9 and obs-10 actually reject the product input and show the required missing-list notice.

| Sequence | Persistence evidence |
| --- | --- |
| Missing-followers rejection, obs-9 | Before and after: `1e9648f9d78dd0059af37f93cc6462109065525b6722cdafc2f24d45de65b6db`; `persistence_unchanged=true` |
| Missing-following rejection, obs-10 | Same before/after hash; `persistence_unchanged=true` |
| Close / reopen, obs-11/12 | Safe UI navigation before selecting a valid input |
| Valid previous import, obs-13 | Before equals the preserved hash; after `b3e9cb57bad6213d670d16c26a02403deab30f587cd5939b9aac39100c79b718`; `persistence_unchanged=false`; “결과를 불러왔어요.” |
| Results / comparison, obs-14/15 | Usable resulting state and an actual comparison |

This is sufficient for recovery P. The raw N/A explanation says “every import completed,” which conflicts with the two admitted rejections and overlooks the observed recovery. The correction is bound to result SHA-256 `cb2db3a40efe55793a8ca9b7a7aaddedafef15f1da7a06071a902edc9b339991` and receipt canonical SHA-256 `c7444eded9a6129634121903b70ea67984ece328ed1fcc6249eb4c532600a9ba`. It changes no success verdict and no raw artifact.

032’s 13 admitted imports all reach loaded results and change persisted state. Its recovery remains N/A. The premature model final described below is a completion-control event and is not an import/browser failure under this criterion.

## 032 PAYWALL evidence is one connected execution

Retention precedes the pair. The 11 numbered uploads occur at obs-8/11/14/17/20/23/26/29/32/35/38; history count ten is actually inspected at obs-41.

| Step | Actual evidence |
| --- | --- |
| Previous | Obs-46, `upload-486`, fixture SHA `b06f0fd115ab74703087e11f0c025df3791a09664cd03922a9fe182760fdc823` |
| Current | Obs-49, `upload-522`, fixture SHA `938514f0010f47ace5c2a2fdae17d2c237fd82838cedd78829e0915d367ca186` |
| Pair persistence chain | Previous after = current before = `e64948a14d9090d97831bb29f99632aa76879139ff4eda051fd1f47f65d025be` |
| A: free actual names | Obs-51 returns six actual departed-comparison rows. Card counts alone are not used as proof. |
| B: locked date controls | Obs-57 and obs-58 each contain both `비교 시작 기록` and `비교 종료 기록`, with `disabled=true` and `visible=true` together. |
| C: actual Pro sheet | Obs-62 follows a click on the visible `Pro 기능 보기` entry; the sheet includes Close/Confirm and all three feature title/description pairs. |
| Unchanged A/B/C anchor | `upload-522` and storage SHA `3a3ced9feb2a55c31bdd1478aa235934fef5591c1cd175bc1f2deb9b9e05d5bd` across all A/B/C observations |

The actual Pro sheet DOM contains:

- **변화를 시간순으로** — 여러 번 확인한 관계 변화를 한곳에서 봐요
- **원하는 두 시점 비교** — 저장한 날짜를 골라 달라진 사람을 확인해요
- **한 사람의 관계 이력** — 보관된 기록에서 그 사람과의 관계를 따라봐요

It also says current relationships/recent changes are free and Pro follows accumulated history. No purchase action occurs.

### Fresh live completion-guard exercise

This is now observed in the committed R6 runtime and completed evidence, rather than being inferred from model/observation counts.

| Model turn / operation slot | Received decision or admitted effect |
| --- | --- |
| Turn 60 / model slot 59 | `op-10e412256f3570e8901d8914045626ce9dc94f9c` returns **final**, with PAYWALL success index 2 = NR because the Pro explanation had not been opened. |
| Saved completion attempt | `action=continue`, obs-59, effective limit 80, 20 turns and 2870.693 task seconds remain; next step is a grounded modal scroll toward the existing offscreen Pro entry. |
| Turn 61 / model slot 60 | New scroll action; admitted obs-61 moves modal scrollTop **344 → 411** by 67 pixels, background unchanged; Pro entry becomes `visible=true`. |
| Turn 62 / model slot 61 | Clicks that visible Pro entry; admitted obs-62 opens the actual sheet and completes C. |
| Turn 63 / model slot 62 | Received final with all success P; guard records `accept_final`, obs-62, effective limit 80, 17 turns and 2831.614 seconds remain. |

The original turn-60 judgment’s computed canonical digest is `3e9e1474566e48db00b14f7fe3886a44251250cae537bb3bf3272c6c7af145da`, exactly matching the saved completion attempt. Operation request/reply hashes and the later admitted observation hashes are in the companion JSON.

There is no obs-60 because that model turn returned a final decision, not a browser action. The job has 63 model turns and 61 admitted browser observations. This is not a lost reply or an uncertain resend. The guard converted premature completion into a grounded continuation, and the continuation actually reached the required UI.

## Visibility and product-finding limits

The recorded viewport is **756 × 413**. DOM evidence and screenshot evidence are kept distinct:

- 024 obs-6: exclusion notice is visible; the next-record explanation is present in returned DOM below the capture.
- 024 obs-9/10: returned DOM contains the exact validation error; both PNGs show the upper modal/chooser and do not show the below-viewport error text.
- 024 obs-15: the limitation and complete single noncausal row are visible.
- 032 obs-4: disabled export controls are visible with upper edges clipped; DOM supplies disabled state and sample-specific titles.
- 032 obs-41: actual ten-record count is visible.
- 032 obs-51: PNG captures the explanation and first row; the returned DOM contains all six names.
- 032 obs-57: both selectors are visible together; the DOM independently records both as visible and disabled. The native same-observation B condition remains strict.
- 032 obs-62: PNG shows the actual Pro sheet, heading, Close, and Confirm. The three feature explanations are present in returned DOM, outside the captured portion of the short sheet.

Modal scroll receipts show real movement without background movement. The small viewport therefore does not establish unreachable controls.

A separate fresh **032 DOM causal-label contradiction candidate** remains: the current-direction obs-51 rows for `ina.archive` and `junho.jeong` contain `언팔로우` alongside the username-change/account-deletion caveat. Those badges are below the captured PNG viewport, so this report does not call them screenshot-confirmed. The finding belongs to this fresh 032 observation; it neither overrides 024’s scoped IDENTITY assessment nor changes 032’s PAYWALL criterion. The frozen product source has the corresponding label path, but source code alone is not substituted for execution.

## Integrity, delivery, and owned closure

| Check | Independent result |
| --- | --- |
| Completed receipt binding | Both task/profile/revision/build bindings match the sealed plan/input provenance. |
| Checkpoint/result/first-judgment seals | All six match their decoded canonical contents. |
| Operations | 79 model + 2 review + 76 tool + 2 close = **159**, all done; no intent or uncertainty. |
| Request/reply seals | All **159 requests and 159 replies** have matching digest and context/operation binding. |
| Plan and event chain | Plan digest/meta match; **325 events** form a valid chain ending `108a50ad53c5d7f58751794c5aa43047fc0786e28d3989c03c39d72c13a54f02`. |
| Route ledger | **81 calls, 81 attempts, 81 received replies**, exactly one attempt each; only free TOKENMAXX route; final/live ledgers equal. |
| Retry/repair/fallback | Zero known quality repair, known reply retry, unsettled guard, uncertain resend, or paid fallback. |
| Usage | 3,451,764 input tokens; 33,767 output tokens. No provider invoice was independently verified. |
| Runtime freeze | All **17** source files match captured hashes and the frozen f50d082 commit. |
| Prior queues | All **37** saved queues unchanged under read-only/query-only snapshots; aggregate `3c0a8f2755ee648a506afff029718e559e095c2625ed1ac114a32a01d69c1c1a`. No Queue constructor used. |
| Inputs | All **544** fixture files, fixture manifest, persona library, and build manifest match. |
| Frozen product | All **319** source rows (bytes/SHA/git-blob/mode), source tree/manifest and build provenance match; all **13** dist files match. |
| Saved HTTP receipts | All **6** before/after assets match each other and frozen dist at 2026-11-14T20:29:57.519029+00:00 / 2026-11-14T20:46:51.070976+00:00. No new browser or HTTP observation was created by the audit. |
| Registered artifacts | **152 files / 4,177,050 bytes**, zero hash mismatches: 024 has 15 logs +15 PNGs; 032 has 61 logs +61 PNGs. |
| Supplemental files | Six lifecycle/legacy-seed files hashed separately; they do not add criterion credit. |
| Owned shutdown | Both contexts closed normally; driver shutdown and owned-group exit confirmed, no forced cleanup, channel poisoning, shutdown error, or unclosed context. |
| Process inventory | No exact owned profile/PID/PGID match for the two R6 contexts. No auditor cleanup performed. |
| Saved status pins | Input provenance, report, stage summary, and final ledger hashes all match run-status pins. |

Node PID/PGID **6960** belongs to 024; **7011** belongs to 032. The independent process inventory was taken during the integrity audit recorded above. Only these exact owned identities were checked; no unrelated process action was taken.

## Key evidence hashes

Paths resolve under `stage-2/sessions/<job-id>/evidence/<job-id>/1/` within the run root. Artifact IDs and filenames, including every PNG and log, are fully mapped in the companion JSON.

| Persona | Artifact ID | Actual SHA-256 |
| --- | --- | --- |
| 024 | log-9 | `89fc7682e2373a7a13014b593590892ad67bc8a9f36db701d538d8f4c87d885d` |
| 024 | log-10 | `19eddf3cd3306ac57b032bbcc8170699d32a0f92f6540da70808fa15977928d5` |
| 024 | log-13 | `ad6b207a420f08861d25992e9bb301255c660dec1cae209193e1249db4a96f6c` |
| 024 | log-15 | `47484898c5547f725ecf3b88894bedcd07b03553ec46fef6f01a88d70c56795f` |
| 024 | png-15-0 | `15696f64de449be3d37015b6ad8f6d7f6233c88a862eb4ca0f4afea23ed0432b` |
| 032 | log-4 | `15056ab5f6aab7dca4dcab3966fc0fce15d7557bb5f10aaed8e9084ebf7ad0ef` |
| 032 | log-41 | `81079fca57a54615d44eda7b8c85b329c8513271ada19f84f5f2806bf2376106` |
| 032 | log-46 | `3c0a6d7a083e05d4b72a0604fa5379d1b9c4e33749cf66cfe2a38b9270b470d3` |
| 032 | log-49 | `680ea99143ab79e6ad4714f8329c5d0d025b9711bc100a83a3cdb712802cb7d2` |
| 032 | log-51 | `d9cdacf4ddf1df009e1392493969cea95d5a09128925129f1dae57b419befbaa` |
| 032 | log-58 | `81eb6e5e1206660d8af36d2296840e42841ec52f4e0c00db2e68e16362226db3` |
| 032 | log-62 | `d2801b03c4a9573d7e3275a66e46934021badeef379cb1e856b6febf2c1a93da` |
| 032 | png-62-0 | `633c86301f6dc1cf5b9300de57c73847f0244459cc17314dd0ee852bdf8fe989` |

Raw result seals:

- 024: `cb2db3a40efe55793a8ca9b7a7aaddedafef15f1da7a06071a902edc9b339991`; receipt canonical seal `c7444eded9a6129634121903b70ea67984ece328ed1fcc6249eb4c532600a9ba`.
- 032: `599fecf252ac936a7da9f7d9734e963fca238126b49d9a99a2b0a65d769133ff`; receipt canonical seal `977a8620ba23013ce946050d01b4960b07d65d6fc1a1905b3b1613dc34af6c10`.

This review authorizes no new dispatch itself. It supplies the completed evidence and independent gate assessment for the parent’s already authorized cohort preflight and checkpoint.
