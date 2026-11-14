# Cohort semantic review — personas 001–012

This fragment covers every assigned success and recovery criterion for **11 operationally complete, receipted candidates** in the fresh pinned stage. Persona 011 is uncertain; all five of its assigned criteria remain **unassessed and excluded**.

There are **47 decisions: 36 success and 11 recovery**. The reviewed distribution is **36 passed, 4 not_run, 7 not_applicable, 0 failed**, compared with raw 39 passed and 8 not_applicable. Five decisions change: privacy visibility for 001–004 changes from passed to not_run; 009 recovery changes from not_applicable to passed. These are scoped semantic corrections, not full-cohort completion or product-readiness claims.

## Bindings and admission

- Stage: `.ux-loop/peekly-completion32-pinned-20261115/stage-32`
- Frozen runtime: `f50d082a197e683b5961d17919fe219dc48c4d55`
- Plan envelope's inner plan hash: `59f2c770425f85dd834542349f1915f084ca8fc6129c421cc907b4127d0212d8`
- Actual plan.json file hash: `660406bc74f05921184be02549ad9ee39a456c33e820283ead5b5476a2d76213`
- Global raw-summary and artifact-audit hashes remain **pending terminal finalization**. Their fields are deliberately null in the JSON. Parent must bind final raw outputs and current-valid eligibility before applying the combined review.
- Full criterion decisions and exact registered evidence are in [cohort-review-001-012.json](cohort-review-001-012.json).

SQLite was opened with `mode=ro`. All **178 registered artifacts across 89 observations** were rehashed. Receipt registration, approved session paths, execution-log schema, plan binding, context ID, checkpoint observation projection, and stored result/checkpoint hashes matched. Each decision has at least one registered execution log with `purpose=result`. Every evidence row records the exact artifact_id, receipt-relative path, sha256, observation_id, and purpose.

Cited PNG pixels were directly inspected or proved byte-identical to an inspected registered PNG after independently rehashing this session's file. Visual claims remain scoped to the specific session and admitted view. Twelve relevant tool-operation replies were matched to checkpoint facts, text, checks, and capture bytes to bind the four causal browser-recovery sequences.

No new model/browser call, queue write, raw-receipt edit, resend/resume, or runtime change was made. This review writes only its two documentation fragments.

## Decision matrix

Success statuses are in the exact assigned order.

| Persona | Queue state | Success decisions | Recovery decision |
|---|---|---|---|
| 001 | complete | passed; passed; passed -> not_run | not_applicable |
| 002 | complete | passed; passed; passed -> not_run | not_applicable |
| 003 | complete | passed; passed; passed -> not_run | not_applicable |
| 004 | complete | passed; passed; passed -> not_run | not_applicable |
| 005 | complete | passed; passed; passed | passed |
| 006 | complete | passed; passed; passed | not_applicable |
| 007 | complete | passed; passed; passed | not_applicable |
| 008 | complete | passed; passed; passed | not_applicable |
| 009 | complete | passed; passed; passed; passed | not_applicable -> passed |
| 010 | complete | passed; passed; passed; passed | passed |
| 011 | uncertain | Four success criteria unassessed/excluded | Recovery unassessed/excluded |
| 012 | complete | passed; passed; passed; passed | passed |

## Material findings

### 001–004: privacy visibility was not executed

Each session has exactly three admitted observations: first screen, More, then the current received-file import guide. Product local-processing/no-send copy appears in the guide DOM, but the final guide PNG exposes only the upper instructions and picker. No admitted scroll or later view exposes the notice.

The exact assigned criterion says the notice **is visible**. DOM membership alone does not meet that execution requirement. All four privacy passes therefore become **not_run**, classified as `judge_false_pass`, `judge_unfounded_execution`, and `runner_limitation`. This is a missing executed view, not a finding that product copy is absent or that product privacy failed. Host-enforced network blocking is not product evidence.

For persona 001, the registered first and final evidence is:

- log-1, obs-1: `evidence/S-ljlmeakahgnhmnnffbajmljk/1/agent-observation-1.json`, SHA-256 `e022292823a647ef470853300fe8b082764d8c1693975ae215bb116e38d6eb32`.
- png-1-0, obs-1: `evidence/S-ljlmeakahgnhmnnffbajmljk/1/browser-00014.png`, SHA-256 `bdd0b8b7514ec9249498d858a4ffab440aacb2fbe5f3e7d32e87a181212115df`.
- log-3, obs-3: `evidence/S-ljlmeakahgnhmnnffbajmljk/1/agent-observation-3.json`, SHA-256 `97a0a5cfecf20be60fcdedc4d337411630af2be4ea5663ca7d03dfa801a7f97a`.
- png-3-0, obs-3: `evidence/S-ljlmeakahgnhmnnffbajmljk/1/browser-00034.png`, SHA-256 `75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1`.

Each privacy JSON decision separately binds all three logs and all three PNGs from that same session.

The sample-entry pass is scoped to the assigned sample-without-picker clause: the admitted control is marked visible, the first PNG partially exposes the sample card, and no file input exists. **The sample and login labels are not both readable in those captured pixels.** No full first-viewport text-visibility claim is made.

The existing-files route is actually executed: More exposes its current row and the hit-tested dispatched click opens the guide, enabled file input, and visible picker. These route passes remain. No triggering browser/import failure occurs, so recovery remains not_applicable.

### 005–008: current route and complete positive fixtures

The assigned START-SKIP clause explicitly does not require a separate legacy “이미 파일을 받았어요” shortcut. Each session executes the current More -> existing-files -> import-guide route. Both route criteria remain passed without inventing a legacy-shortcut defect.

HTML and JSON are ordinary valid uploads. The HTML archive contains complete followers.html and following.html documents and is archive-valid. Its SHA-256 is `14cd426c95c123b76cabc344dda1b48892618c4c46ce352b4e8d613172e6512b`; the JSON fixture hash is `ca5d25b7cf474622f829a32db0d9d43cb0eb9b1947db336e15f677a248691a6a`.

Each import produces all three named result headings and counts 1, 1, 0 in returned DOM, the loaded-result message, and a changed available persisted storage snapshot. In every session HTML-after equals JSON-before. The PNGs show the result page and first count; lower cards extend beyond the captured viewport. The assigned criterion requires producing the counts, so no additional all-cards-in-one-viewport requirement is invented.

005 has a real browser recovery: obs-3 rejects a click without dispatch or automatic retry; obs-4 corrects the short label to the full row label on the same selector and opens the guide; obs-5 completes the valid persisted HTML result. The recovery pass remains. The full sequences for 006–008 contain no triggering failure, so their recovery decisions remain not_applicable.

**No cancel or large-file criterion is assigned to 001–012.** This scope does not establish that the earlier 51–104 ms cancellation gap was retested.

### 009, 010, 012: negative imports and conditional recovery

All three completed sessions execute valid HTML and JSON imports before the assigned malformed, account-mismatch, missing-followers, and missing-following cases. Each named negative fixture is actually uploaded.

Malformed HTML produces a product error naming [followers.html]. Account mismatch produces the same-account retry message. Each missing-list case produces guidance requiring both lists and checking [팔로워 및 팔로잉]. Every negative attempt stays in the retry flow and preserves the preceding valid JSON storage hash, with available before/after snapshots and `persistence_unchanged=true`; no new result is published.

The deliberately malformed negative HTML fixture is distinguished from an incomplete positive-format fixture. Rejection is supported by each admitted DOM/storage result. Negative PNGs show the retry picker; **the detailed error wording is below the captured region**. The retained passes do not claim those alerts were visually readable.

Expected negative-input errors are actual recoverable failures under the literal conditional criterion. No “unexpected failures only” restriction is added. The criterion is existential and has no every-failure requirement. Each session has an earlier, directly causal browser recovery:

| Persona | Failure and correction | Verified recovery result | Decision |
|---|---|---|---|
| 009 | obs-3 sample click rejects the requested label “샘플로 먼저 둘러보기”; obs-4 uses the same selector with the fresh actual label “샘플로 둘러보기” | Hit test and dispatch succeed at obs-4, though its immediate PNG still shows landing. Before any import, obs-5 reaches expanded sample More menus with a changed persisted state. | N/A -> passed, judge_missed_execution |
| 010 | obs-4 existing-files click is rejected; obs-5 uses the same selector with the full fresh row label | Guide opens at obs-5; obs-6 loads and persists valid HTML through the recovered route. | passed retained |
| 012 | Three rejected clicks occur at obs-3, obs-5, obs-6; obs-4 upward scroll is at_boundary, with no dispatch or movement; obs-7 uses the full fresh row label | Guide opens at obs-7; obs-8 loads and persists valid HTML through that route. | passed retained; raw prose's two rejected attempts corrected to three |

For 009, the pre-import state changes from `7b3f3a770f0ac89471a660ccfe9a54f5de96b387ebb22d307e06fadb84f77355` to `e8fc9399636d81e28c5eb0954498e57377d0b17aa491ede553b70f8c92bf1891`. Later HTML/JSON success is not substituted for the recovered sample-entry result.

**Later negative-import recovery is unattempted** in 009, 010, and 012: no valid retry follows those errors. Those attempts prove assigned rejection behavior. The earlier verified browser sequences satisfy the existential recovery criterion without asserting every later failure was recovered.

### 011: excluded before seed dispatch; cleanup pending finalization

The exact original request is `seed_legacy_unknown({"file":"peekly-legacy-unknown-state.json"})`. The checkpoint decision calls this an UNKNOWN persona, but assigned IDs are FORMATS, HTML, ACCOUNT, and MISSING, with no PRD-IMPORT-SNAPSHOT-UNKNOWN.

- Operation: `op-fcc559b12e7d408c0dc7405eb73d5d309172b743`.
- Request SHA-256: `6bd1f723068bb648e945bec8b7085b361a36f74cbfd71ff6815ef845b68de8e1`.
- Checkpoint SHA-256: `60c903e17657d252f7f03e18314e2c345bacc062652b0bb448b21ec1ffb185b0`.
- Queue problem: `host_execution_failed:legacy_seed_task_not_authorized`.
- Original operation remains uncertain with reply null; result and receipt are absent.

Frozen ScaleBrowserHost invokes `_authorize_legacy_seed` before any `_exchange`. Without the UNKNOWN requirement it produces this exact rejection before seed dispatch. This is a **model/tool-selection error reaching a runner authorization guard**, not a product defect. None of 011's unfinished criteria is converted to not_run or not_applicable; all remain unassessed and excluded.

Cleanup is separate. At this review snapshot, host lifecycle is spawned; the driver's last record is prior click command 6 reply_written at `2026-11-14T21:04:25.183Z`. The live stage owner calls host.shutdown after the cohort executor exits, so the correct description is **closure pending stage finalization**, not a leak conclusion. No external cleanup or resend was attempted. Parent will bind terminal shutdown and independent process-inventory proof.

## Result and receipt hashes

Receipt hashes use canonical UTF-8 JSON with sorted keys, compact separators, and ensure_ascii=false. Actual stored result hashes and full plan/context bindings are also recorded in the JSON.

| Persona | Job | Result SHA-256 | Canonical receipt SHA-256 |
|---|---|---|---|
| 001 | S-ljlmeakahgnhmnnffbajmljk | `f64e43772606974fa898ec26885c4ab6738f3f04c82586da7cb897a7af90099c` | `905191593ef26d658c93c3a7c98b8c86ced4f71faabae9bdcf5a8e671dc38a60` |
| 002 | S-ljffmnkkgdhopplfbhhegkma | `8ed0f9b6a989ca0a26202a8bfa398703c44f28a5f900074a01a5c77d34913de4` | `be583994151832ec67159c74213a3c9d0e9f35a4995f4a7dd4965f4c8c27bed4` |
| 003 | S-gimbpjkdealchomaigbnfkap | `6f9f22da65d8dacb6c2468028bfb8a73d369e4a859747a4b2dac831f182a9397` | `a743ac7281b0074ae3227675695a703cfe2fd9e7b0366ede726b138da942740a` |
| 004 | S-gppbnocdodpcpfackcopdgal | `d757666a4a56bd0a7d1470afc89a60f882d8c78a70146b5e20cd76522699a563` | `73a1c1ffafd5261897f710359fba768546a984b05995862259b9af40559b6828` |
| 005 | S-ahigmmpldbffjlajeimgmmhg | `440cff05513438b3d97c44d80abea13885a21a1dd801987d888cda61986e6178` | `59e665d3a90e23fa66fcec52f8c0906727a7f1f373cf159c2e404c1412c82898` |
| 006 | S-eaimebeeijnlneijkfognapa | `e9861f5e2024de88aa0c1174c9b801351a88568c8df0178fa5d6c8266d12ee69` | `4bac6798453fcbee58a8e71137ed73474682d618c5042d2192b7d8c16993643b` |
| 007 | S-dhklecmcppmmgkgiknilflkl | `21ba5c5db0132684aed6fe92add0e7b6bc80101d8276b56fb1fe810587dbcc81` | `12de88e136beb1b01c1f94a9ce85535b17f35b8400d12da242eecc0576fb76bc` |
| 008 | S-bjhjihfccjkbmdiedidhoncf | `ed234648e280228f50160325a10f3c2b306f1d2c42befcdd7542c3db7f29c13a` | `4bb29b6d0dde964e1251ba393ea0a14b20df2ff639052b3f1e09fc92dc2085f5` |
| 009 | S-pblkjnfjnefpmkcnmhghnikb | `f6e58ec63e724e54d66357f296cdf6d634e6bfd4757baa36771e295b8bb5bf63` | `b24d99cc75e455135227007dadca53641bfccaabd57441d91a18c6d0e3030e3a` |
| 010 | S-cijopeodbceldieicjneaaji | `778efeea04a12b711aa170048adc3216281b497189626fc2125c4df077d136cf` | `e98f6036b1cdf0d9991909e3a1dc8af6b0841e3bfc33cd4518ef136bebb0393c` |
| 012 | S-galdkhommdhbgkalkcfmmefk | `b19e9aa546e32fd90f85c520f5122864f23529af418081de50ff9e056df15101` | `a738df39de59981d87eb8c8f49527a4d508985d163b144441dae730969f686a3` |

## Exact assigned criteria

The following text comes from the pinned plan; each JSON row also contains its own exact assigned criterion.

### PRD-START-SAMPLE

> 첫 화면에는 인스타그램으로 로그인 버튼과 샘플로 먼저 둘러보기 링크가 있다. [PRD-START-SAMPLE] sample entry is visible without a file picker

### PRD-START-IMPORT

> 이미 Instagram 자료를 받은 사용자는 더보기 첫 화면의 **이미 받은 자료로 확인하기**에서 직접 가져오기 흐름을 바로 연다. [PRD-START-IMPORT] the current More entry for users who already have Instagram files is visible and opens the saved-file import flow

### PRD-PRIVACY-LOCAL

> 직접 연결·파일에서 받은 관계 목록과 기록 비교는 기기 안에서 처리한다. [PRD-PRIVACY-LOCAL] the product's own local-processing and no-send notice is visible; a host-enforced network block is not product privacy evidence

### CONDITIONAL-RECOVERY

> If a recoverable browser/import failure actually occurs, perform the safe recovery and verify it. If no triggering failure occurs, report not_applicable; do not manufacture a failure.

### PRD-START-SKIP

> 1단계에는 **이미 파일을 받았어요** 링크가 있어 3단계로 바로 갈 수 있다. [PRD-START-SKIP] the current PRD requires the More entry to open the existing-file import flow; a separate request-guide shortcut labelled '이미 파일을 받았어요' is not required

### PRD-IMPORT-FORMATS

> Instagram이 HTML 형식으로 만든 백업과 JSON 형식으로 만든 백업을 똑같이 읽는다. [PRD-IMPORT-FORMATS] each valid complete Instagram HTML and JSON fixture produces counts 1, 1, 0; an incomplete HTML test fixture is not product evidence

### PRD-IMPORT-HTML

> 팔로워·팔로잉 HTML 목록에서 아이디를 읽지 못한 항목이 하나라도 있으면, 그 사람이 떠난 것처럼 보이지 않도록 파일 이름을 담은 오류로 멈춘다. [PRD-IMPORT-HTML] named malformed file is rejected and no result is published

### PRD-IMPORT-ACCOUNT

> 이미 기록된 계정과 다른 계정의 파일은 막는다. [PRD-IMPORT-ACCOUNT] account mismatch is blocked before a result is saved

### PRD-IMPORT-MISSING

> 팔로워와 팔로잉이 모두 있어야 결과를 만들고, 하나라도 없으면 [팔로워 및 팔로잉]을 골랐는지 확인하라고 안내한다. [PRD-IMPORT-MISSING] both missing-followers and missing-following fixtures are rejected

## Remaining terminal reconciliation

Parent must bind final raw summary/artifact-audit hashes, verify final current-valid eligibility and cleanup, and apply the combined review over the assigned scopes. This fragment contains no decisions about personas outside 001–012, does not reuse old-run overrides, and modifies no raw output.
