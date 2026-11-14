# Semantic review checklist — remaining 23 baseline criteria

Prepared 2026-11-15 (Asia/Seoul), before the fresh cohort's semantic review. This is an offline audit checklist, not new UX evidence or a forecast of outcomes.

## Sources and matching rule

- Frozen baseline: commit `65f52f78918d097c39ac8eb5ec49ed6daea537bc`, `docs/validation/peekly-coverage-20261114/reviewed-summary.json`, SHA-256 `f803cd44fcad79d203c826d36ee2f8e1409538e6f67ae06a240e8c634c21b4dc`. The current file was byte-compared with `git show` at that commit.
- Baseline selector: `candidate.criteria[] | select(.status == "not_run")`. It contains exactly **23 rows across 14 personas: 22 success and 1 recovery**. Each row retains its old job ID, reason and evidence references.
- New saved profiles: `.ux-loop/peekly-persona-library-v4-pinned-20261115/library.json`, file SHA-256 `02c728a1b750d86164e035d88c096ffa7feca42f363cb68ed697a3beec7fa616`. All 22 success indices below match the new requirements in **context requirement order**, the order used to construct tasks.
- Actual task/checklist construction: `skills/remorsearch-ux-qa/uxpersonas/scale_entry.py`, especially `criterion_checklist` and `prepare_scale_goal`; reviewed file SHA-256 `24547d6a3660d2f5c76ad01642e822d9a11c510e26da93a5bec6c11065b81752`.
- Native evidence rules: `skills/remorsearch-ux-qa/uxpersonas/peekly_criteria.py`; reviewed file SHA-256 `2c56c951e419a0e82b217a63f0f0fc65fa5ed309f90d356db1904f2d592f4593`.
- Product authority: archived `.ux-loop/peekly-pinned-product-51110f4-20261115/source/docs/PRD.md`, SHA-256 `a014a85b7523928f693cd4422793929631f033176715f31409412e95e1d7432b`, product commit `51110f4c569673faa8d242d5b85c4b47afb54cbb`. Bind the fresh run to its own freeze and the new build manifest/served bytes; do not substitute the externally changed original worktree or port 4174.

Join old and new results by **persona ID + requirement ID + criterion kind**, verifying the actual new plan's index. Job IDs, library revisions and result directories legitimately change. Only a queue-complete, operationally completed, receipted and current-valid new session is eligible. A file on disk or a tool response that never entered the receipt is not admitted criterion evidence.

## Exact baseline rows

Indices are zero-based; `017` means `PER-PEEKLY-V2-017`.

| Persona | Kind[index] | Requirement |
| --- | --- | --- |
| 013 | recovery[0] | CONDITIONAL-RECOVERY |
| 017 | success[0] | PRD-RESULT-RECIPROCITY |
| 017 | success[1] | PRD-RESULT-REVERSE |
| 017 | success[2] | PRD-RESULT-MUTUAL |
| 018 | success[0] | PRD-RESULT-RECIPROCITY |
| 018 | success[1] | PRD-RESULT-REVERSE |
| 018 | success[2] | PRD-RESULT-MUTUAL |
| 019 | success[0] | PRD-RESULT-RECIPROCITY |
| 019 | success[1] | PRD-RESULT-REVERSE |
| 019 | success[2] | PRD-RESULT-MUTUAL |
| 020 | success[0] | PRD-RESULT-RECIPROCITY |
| 020 | success[1] | PRD-RESULT-REVERSE |
| 020 | success[2] | PRD-RESULT-MUTUAL |
| 021 | success[2] | PRD-IMPORT-SNAPSHOT-UNKNOWN |
| 022 | success[1] | PRD-IDENTITY-LIMIT |
| 022 | success[2] | PRD-IMPORT-SNAPSHOT-UNKNOWN |
| 023 | success[2] | PRD-IMPORT-SNAPSHOT-UNKNOWN |
| 024 | success[2] | PRD-IMPORT-SNAPSHOT-UNKNOWN |
| 025 | success[0] | PRD-RESULT-SEARCH |
| 029 | success[2] | PRD-PAYWALL-BOUNDARY |
| 030 | success[2] | PRD-PAYWALL-BOUNDARY |
| 031 | success[2] | PRD-PAYWALL-BOUNDARY |
| 032 | success[2] | PRD-PAYWALL-BOUNDARY |

## Evidence checks by group

### Relationship lists — 12 rows, 017–020

Use `result_scope_evidence`. Require a completed, hash-bound ordinary upload of `peekly-sample-current.zip`, a new persisted result, and the subsequent hit-tested click and actual opened sheet for **each** category. Import attempt ID and storage digest must remain bound across those observations.

| Requirement | Actual sheet/count | Expected synthetic row keys |
| --- | --- | --- |
| PRD-RESULT-RECIPROCITY | 나를 맞팔 안 한 사람 / 5 | atelier.luna_, ina.archive, junho.jeong, minsu.kim_, taeo.kang_ |
| PRD-RESULT-REVERSE | 내가 맞팔 안 한 사람 / 2 | haneul.song, seongsu.coffee |
| PRD-RESULT-MUTUAL | 맞팔 중인 사람 / 5 | dohyun.fit, haerin.daily, minji_kim, seojun.park, yuna.choi |

**PASS:** clicked card count, opened heading count and complete actual row set match the fixture. **FAIL:** the valid scoped visit shows a wrong count or row set. **NR:** only sample lists, dashboard cards, another category, departed-account list, person details, stale storage, or no completed scoped visit. A sample visit before import earns none of these 12 credits.

### Legacy UNKNOWN — 4 rows, 021–024

Use `legacy_scope_evidence`. Require the actual admitted `seed_legacy_unknown` observation and immutable `legacy_seed` receipt: status validated; exact fixture/product/loader/validation hashes; nonempty attempt ID; source key v6 and target key v7; source snapshot ID `peekly_legacy_unknown_v6`; all fresh-owned-profile, initial-storage-match, absent-source-includedFiles, absent-source-listCompleteness, reload and migration validation flags true. Before/after storage must be available, changed and bound to the readback.

The seed must be the first mutating action in the new owned profile. The optional existing theme preference may be exactly `system`; full `storage_keys` and filtered snapshot `storage_snapshot.keys` are different inventories.

Seed readback must contain one non-sample snapshot with unknown completeness, inferred followers/following included files, and null active/comparison selections. **Do not require migrated included files to remain absent.** Then require exactly one completed current-fixture import, chained from seed storage, producing exactly the retained unknown plus one known current snapshot of the same synthetic account. Current completeness may be null or known.

**PASS:** while that two-snapshot state remains unchanged, persisted active/comparison IDs both point to current; the actual expanded Home notice says the retained incomplete record is not used for analysis and another new record is needed; no departed-account comparison is exposed. Preserve this observation before importing the normal previous/current pair for other requirements.

**FAIL:** that valid legacy/current setup actually exposes a departed-account comparison using the unknown prerequisite. **NR:** rejected/missing seed, only a known-empty ZIP, no actual migration/readback, no sole-current checkpoint, or no exclusion UI. Seed success alone is not criterion success; unrelated later comparison copy cannot turn the earlier legacy test into a failure.

### PAYWALL — 4 rows, 029–032

Use `paywall_scope_evidence`, then inspect the actual scoped UI. These personas also require sample export and retention; do not count those earlier screens as the free imported-data comparison. Retention's eleven distinct imports and history inspection precede the final previous/current pair; reuse that pair without more uploads during A/B/C.

- **A:** completed pinned same-account previous/current imports with a continuous storage chain; actual current free results and latest departed-account comparison with names, without a purchase.
- **B:** actual History / 기간 비교 screen. Both visible select controls, accessible names `비교 시작 기록` and `비교 종료 기록`, appear in one observation and are disabled for the free state. Accessible labels may be absent from body text.
- **C:** actual visible Peekly Pro sheet, with its close/confirm controls and all three feature explanations: chronological changes, choice of two dates, and per-person history. The pinned sheet labels include `변화를 시간순으로`, `원하는 두 시점 비교`, and `한 사람의 관계 이력`. A generic Pro mention or hidden background text is insufficient.

**PASS:** all A/B/C have admitted proof tied to the same saved pair. **FAIL:** a fully reached, valid scoped state contradicts the boundary, such as charging for the required latest names or enabling Pro-only date choices on a verified free account. **NR:** pair, actual names, same-screen selectors or Pro explanation remains unobserved. A missed navigation action, modal obstruction or exhausted turn budget is not a product boundary failure by itself. Never click disabled controls or purchase to complete coverage.

### SEARCH — 1 row, 025

Use `search_scope_evidence`. Require accepted `peekly-search-ready.zip`, the ordered 12-key `synthetic_search_outgoing_00` through `_11` list and its actual visible enabled `input[type=search]`. Then require a fresh admitted `type` action for `synthetic_search_outgoing_05`, same selector/attempt/storage, matching retained expected/actual query hashes, and exactly that one remaining row.

**PASS:** actual query and filtering match, including initial username order. **FAIL:** the valid query was dispatched but order/filter result is wrong. **NR:** visible input without typing, stale typed-input facts, another screen, or no query result. Do not recreate the old placeholder-only false failure: this list labels its field `이름 또는 아이디 찾기`, not the MatrixTab placeholder.

### IDENTITY — 1 row, 022

After the legacy exclusion checkpoint, require the normal complete same-account previous/current pair and actual opened `팔로워에서 빠진 사람` account list. The explanation must disclose `아이디 변경이나 계정 삭제 때문일 수도 있어요`, rather than claim a confirmed unfollow cause.

**PASS:** disclosure is visible on that actual comparison. **FAIL:** the scoped comparison/list was reached but its required explanation is missing or contradicted. **NR:** first-record preview, loading state, generic warning elsewhere, or unopened comparison. The warning itself is not a clickable control.

### General RECOVERY — 1 row, 013

The task's recovery criterion applies only after a recoverable failure actually occurs. For the SAVE-FAIL fallback, require a definitely completed `upload_save_failure` response, consumed and restored one-shot fault, visible save error, and unchanged valid saved baseline. Only then may observed normal file re-selection/input be used for one ordinary upload of the failed fixture. Require the admitted normal import completion and actual changed saved state; a selected filename or cleared error is insufficient.

**PASS:** that safe recovery is actually performed and persisted. **FAIL:** an attempted, fully evidenced recovery contradicts the criterion. **NR:** a real trigger occurred but recovery was not attempted or could not be verified. **N/A:** no triggering recoverable failure occurred; this earns no execution credit.

**Keep direct-save-retry separate:** `PRD-IMPORT-SAVE-FAIL` is success[2] for 013–016 and is not the remaining recovery row. A valid write-failure screen with unchanged storage and only normal file re-selection, but no required `다시 저장` action, proves that product failure. Successful normal reimport cannot convert it to a direct-retry PASS or erase the failure. Do not reinject or resend an uncertain operation to obtain recovery evidence.

## Denominators and review output

1. Baseline assessed population is **29 completed/current-valid sessions**, with success **62 passed / 8 failed / 22 NR / 0 N/A** (92 rows) and recovery **9 / 0 / 1 / 19** (29 rows): **121 total**. Prior uncertain 009/010/012 were unassessed, not extra NR.
2. The new saved 32-person plan has **104 success + 32 recovery = 136 possible rows** if all sessions become eligible. The additional three personas contribute 12 success and 3 recovery obligations; they cannot earn credit toward the old 23. Recompute actual eligible counts from terminal results.
3. Publish an explicit status for **each of the 23 old rows**, including unassessed if its new session is uncertain/interrupted/invalid. Report old-23 passed, failed, NR, N/A and unassessed separately, even if the whole-cohort NR count is zero. Only passed or failed is executed coverage; N/A and unassessed earn no credit.
4. Report the fresh whole cohort and matched old-23 view separately. Do not mix the original 46 weighted mappings or 32 unique mappings with this 23-row set. Smoke sessions and repeated persona observations are not additional people in the fresh 32-person cohort.
5. Session complete is operational eligibility, not a criterion pass. Preserve criterion failures and separate product defects, runner/precondition limits, and judgment errors. Record host_protocol/uncertainty separately; no uncertain resends.
6. For every reviewed row retain: current job ID; actual plan kind/index/requirement; setup/action/result observation IDs and receipt artifact paths/SHA256; raw status; reviewed status; short reason and classification. Rehash cited JSON/PNG and confirm they are admitted to the current-valid receipt. Preserve raw receipts and explain any judgment delta instead of rewriting original evidence.

