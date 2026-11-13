# Peekly explicit browser acceptance matrix

Target: the isolated Peekly worktree at `51110f4c569673faa8d242d5b85c4b47afb54cbb` (`rem/peekly-import-ux-20261113`). The product source is not modified by this QA run. The criteria below are derived from the saved Peekly PRD requirement excerpts and anchors in `peekly-persona-library-v2`; they are not new product requirements.

## Adjudication contract

- Each persona task expands its saved `requirement_ids` into the criteria below, in the same order as `success_criteria`.
- The owned headless Chrome host captures the current DOM text, visible controls, file inputs, network-policy facts and a PNG after every action. It records fixture names only after the file-input action completes.
- Native checks are emitted only after their trigger and all required fixture actions are observed. A native `failed` check is immutable; a later model judgment or recovery cannot erase it. Model judgments for remaining criteria must cite their own `obs-N` and screenshot evidence.
- A criterion that was not attempted remains `not_run`; it is not a pass. Conditional recovery is `not_applicable` only when no triggering failure occurred. Missing/unsupported native OS behavior is reported separately as N/A, never as a pass.
- Each timeout is measured from satisfying the stated precondition. The overall persona cap remains 1,800 seconds and the model decision cap is 24 turns.

## Criterion table

| PRD task | Observable success criterion | Machine adjudication | Precondition and required action | Limit | Evidence |
|---|---|---|---|---:|---|
| `PRD-START-SAMPLE` | First screen shows the Instagram connection CTA and sample entry; no file-format knowledge is required. | Visible button selector `button[aria-label='샘플로 둘러보기']` and exact sample text. | Fresh isolated profile; observe first screen. | 8s | DOM controls/text + PNG |
| `PRD-START-IMPORT` | Alternative path opens the existing direct-import guide at step 1/3. | Text `이미 받은 자료로 확인하기` and `1 / 3단계`. | Open sample/welcome, expand connection alternatives, choose existing-file path. | 30s | DOM text/control + PNG |
| `PRD-START-SKIP` | The step-1 shortcut reaches step 3/3 and exposes a file input. | Text `3 / 3단계` plus `input[type=file]`. | Step 1/3 visible; click the received-file shortcut. | 20s | DOM + file-input facts + PNG |
| `PRD-IMPORT-FORMATS` | HTML and JSON fixture imports produce matching 1 / 1 / 0 category counts. | Both fixture names must be recorded; visible category labels and expected count values are checked after result. | Upload `peekly-format-html.zip`, then `peekly-format-json.zip`. | 120s | Upload ledger + result DOM + PNG |
| `PRD-IMPORT-MULTI` | Multiple file selection is supported. | `input[type=file][multiple]` exists and combined selection completes without an error. | Direct import step 3; select reviewed HTML and JSON together. | 120s | DOM property + upload evidence + PNG |
| `PRD-IMPORT-HTML` | Malformed HTML stops import and names the file; it does not publish a false result. | `[role=alert]` contains the malformed-file error after the named fixture upload. | Upload `peekly-malformed-html.zip`. | 60s | Upload ledger + alert DOM + PNG |
| `PRD-IMPORT-PROGRESS` | Reading and analysis phases are distinguishable; a stop action is available during processing. | Poll `[role=status][aria-live=polite]` every 100ms; observe both phase strings and stop control. | Generate and hash-bind a sufficiently large valid synthetic fixture; upload it. | 15s | DOM polling trace + PNGs |
| `PRD-IMPORT-ACCOUNT` | A mismatched-account fixture is blocked before results are saved. | `[role=alert]` contains the account-mismatch error after the fixture upload. | Upload `peekly-account-mismatch.zip`. | 60s | Upload ledger + alert DOM + PNG |
| `PRD-IMPORT-MISSING` | Missing-followers and missing-following fixtures are both rejected with the required-list guidance. | Both fixture names must be recorded; alert contains `팔로워와 팔로잉 목록이 모두 들어 있는 파일이 필요해요`. | Upload both missing-list fixtures separately. | 120s | Upload ledger + alert DOM + PNG |
| `PRD-IMPORT-SIZE` | A file larger than 128 MiB is rejected without replacing the prior result. | `[role=alert]` contains the size error; before/after result snapshot remains equal. | Seed an isolated synthetic result; upload `peekly-oversize-plus-one.zip` (128 MiB + 1 byte). | 60s | File byte count/hash + before/after DOM + PNG |
| `PRD-RESULT-RECIPROCITY` | Reciprocity category label, count and list match fixture contents. | Visible category control and exact expected count/list entries. | Complete a valid synthetic import; open the category. | 30s | DOM count/list + PNG |
| `PRD-RESULT-REVERSE` | Reverse-follow category label, count and list match fixture contents. | Visible category control and exact expected count/list entries. | Complete a valid synthetic import; open the category. | 30s | DOM count/list + PNG |
| `PRD-RESULT-MUTUAL` | Mutual-follow category label, count and list match fixture contents. | Visible category control and exact expected count/list entries. | Complete a valid synthetic import; open the category. | 30s | DOM count/list + PNG |
| `PRD-RESULT-SNAPSHOT` | Two different snapshots show an unfollow count and the corresponding account list. | Both snapshot fixture names recorded; count and list visible in comparison. | Import previous then current sample fixture; open comparison. | 120s | Upload ledger + comparison DOM + PNG |
| `PRD-RESULT-SEARCH` | A list with more than eight entries exposes search; a synthetic handle narrows the list. | Exact search input placeholder; filtered row count and target handle match. | Open a relationship list with at least nine entries; type a fixture handle. | 45s | Input value + row DOM + PNG |
| `PRD-SAMPLE-EXPORT` | Sample list copy and save actions are disabled and explain why. | `button.matrix-export-btn` controls both have `disabled=true` and sample-restriction title. | Open sample relationship list. | 30s | Control properties + PNG |
| `PRD-PRIVACY-LOCAL` | Import guide states local-only processing; browser blocks external requests. | `.guide-privacy-note` text plus `network_policy.external_requests_blocked=true`. | Open import guide and observe. | 20s | DOM + network-policy facts + PNG |
| `PRD-PRIVACY-DELETE` | Full-reset confirmation explains local deletion and is scoped to the isolated profile. | Visible reset action and confirmation text; do not confirm destructive action. | Synthetic data only in a fresh isolated profile; open privacy settings. | 45s | DOM + PNG |
| `PRD-IDENTITY-LIMIT` | UI does not imply a permanent account identifier where the source has none. | Inspect identity explanation for permanent-ID limitation language; absence is not inferred from unrelated text. | Open an identity-related explanation. | 30s | DOM text + PNG |
| `PRD-IMPORT-SNAPSHOT-UNKNOWN` | Empty/unknown previous snapshot is excluded from comparison. | Both fixture names recorded; comparison exclusion text visible and no unfollow delta fabricated. | Import `peekly-empty-previous.zip`, then `peekly-sample-current.zip`. | 120s | Upload ledger + comparison DOM + PNG |
| `PRD-IMPORT-ALLTIME` | Export guide presents the all-time period choice. | Visible guide text contains `전체 기간`. | Open export request guide and advance guide scenes. | 45s | DOM text + PNG |
| `PRD-IMPORT-SAVE-FAIL` | Write failure shows retry-save guidance and preserves the prior result. | Deterministic storage-failure test adapter; assert alert/retry action and unchanged prior snapshot. | Isolated test harness injects a storage write failure; not a browser-only capability. | 30s | Unit-test trace + before/after snapshot |
| `PRD-IMPORT-REOPEN` | Reopening resumes the persisted guide step. | Persisted step before close equals resumed step after reopening same owned profile. | Save a guide step; close and reopen owned context/profile. | 45s | Local storage state + DOM + PNG |
| `PRD-SNAPSHOT-RETENTION` | Latest ten snapshots remain; the eleventh save prunes the oldest. | Compare ordered snapshot timestamps/IDs before and after eleventh import. | Eleven distinct valid synthetic snapshots. | 300s | Snapshot-store state + history DOM + PNG |
| `PRD-PAYWALL-BOUNDARY` | Core relationship analysis/comparison remains visible; only paid-detail names are locked. | Core counts visible alongside Pro lock affordance; no purchase action. | Valid import with free entitlement; inspect result and locked detail. | 45s | DOM labels/counts + PNG |

## Platform boundary and known non-coverage

The desktop headless browser cannot display the native iOS share sheet/Quick Look preview. The report must mark that specific preview N/A (desktop-only boundary), while still checking the web-visible local-processing copy and network block. Native iOS deletion of WebView cookies, notification cancellation, real iOS file-provider access, real Instagram authentication, and real-account data are not proven by this browser run. The `test-harness` criteria (`PRD-IMPORT-SAVE-FAIL`) must cite the separate automated test; it must not be presented as a browser observation. A criteria row whose fixture is not yet generated or whose precondition was not achieved remains not_run, and blocks a full-pass claim.

## Frozen cohort

The run uses only the existing reusable `PER-PEEKLY-V2-001` through `PER-PEEKLY-V2-032` records from `peekly-persona-library-v2`. It does not clone, edit, or regenerate personas. The per-persona plan records the exact requirement IDs and criterion indexes so the result can be compared to the earlier 32-persona runs.
