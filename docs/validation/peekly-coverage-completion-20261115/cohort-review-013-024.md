# Fresh cohort review — personas 013–024

Draft from the actual fresh plan, sealed completed results/checkpoints and admitted saved artifacts. Final eligibility and shared raw-summary/artifact-audit hashes remain pending. No raw receipt, queue, runtime, finalizer-owned output or historical verdict was changed.

- Stage: `.ux-loop/peekly-completion32-pinned-20261115/stage-32`.
- Plan SHA-256: `59f2c770425f85dd834542349f1915f084ca8fc6129c421cc907b4127d0212d8`.
- Assignment: 40 success + 12 recovery = 52 criteria; includes 18 historical remaining rows.
- Reviewed personas: 013, 015, 016, 017, 018, 019, 020, 021, 022, 023, 024.
- Decisions: 48. Uncertain 014 contributes no assessed criteria.

## Decisions

| Persona | Criterion | Raw | Reviewed | Classification |
| --- | --- | --- | --- | --- |
| 013 | success[0] / PRD-IMPORT-PROGRESS | passed | passed | confirmed_raw_verdict |
| 013 | success[1] / PRD-IMPORT-SIZE | passed | passed | confirmed_raw_verdict |
| 013 | success[2] / PRD-IMPORT-SAVE-FAIL | failed | failed | product_defect, confirmed_raw_verdict |
| 013 | recovery[0] / CONDITIONAL-RECOVERY | passed | passed | confirmed_raw_verdict |
| 015 | success[0] / PRD-IMPORT-PROGRESS | passed | passed | confirmed_raw_verdict |
| 015 | success[1] / PRD-IMPORT-SIZE | passed | passed | confirmed_raw_verdict |
| 015 | success[2] / PRD-IMPORT-SAVE-FAIL | failed | failed | product_defect, confirmed_raw_verdict |
| 015 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | not_run | judge_unfounded_execution |
| 016 | success[0] / PRD-IMPORT-PROGRESS | passed | passed | confirmed_raw_verdict |
| 016 | success[1] / PRD-IMPORT-SIZE | passed | passed | confirmed_raw_verdict |
| 016 | success[2] / PRD-IMPORT-SAVE-FAIL | failed | failed | product_defect, confirmed_raw_verdict |
| 016 | recovery[0] / CONDITIONAL-RECOVERY | passed | passed | confirmed_raw_verdict |
| 017 | success[0] / PRD-RESULT-RECIPROCITY | passed | passed | confirmed_raw_verdict |
| 017 | success[1] / PRD-RESULT-REVERSE | passed | passed | confirmed_raw_verdict |
| 017 | success[2] / PRD-RESULT-MUTUAL | passed | passed | confirmed_raw_verdict |
| 017 | success[3] / PRD-RESULT-SNAPSHOT | passed | failed | product_defect, judge_false_pass |
| 017 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | not_applicable | conditional_not_applicable, confirmed_raw_verdict |
| 018 | success[0] / PRD-RESULT-RECIPROCITY | passed | passed | confirmed_raw_verdict |
| 018 | success[1] / PRD-RESULT-REVERSE | passed | passed | confirmed_raw_verdict |
| 018 | success[2] / PRD-RESULT-MUTUAL | passed | passed | confirmed_raw_verdict |
| 018 | success[3] / PRD-RESULT-SNAPSHOT | passed | failed | product_defect, judge_false_pass |
| 018 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | not_applicable | conditional_not_applicable, confirmed_raw_verdict |
| 019 | success[0] / PRD-RESULT-RECIPROCITY | passed | passed | confirmed_raw_verdict |
| 019 | success[1] / PRD-RESULT-REVERSE | passed | passed | confirmed_raw_verdict |
| 019 | success[2] / PRD-RESULT-MUTUAL | passed | passed | confirmed_raw_verdict |
| 019 | success[3] / PRD-RESULT-SNAPSHOT | passed | failed | product_defect, judge_false_pass |
| 019 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | not_applicable | conditional_not_applicable, confirmed_raw_verdict |
| 020 | success[0] / PRD-RESULT-RECIPROCITY | passed | passed | confirmed_raw_verdict |
| 020 | success[1] / PRD-RESULT-REVERSE | passed | passed | confirmed_raw_verdict |
| 020 | success[2] / PRD-RESULT-MUTUAL | passed | passed | confirmed_raw_verdict |
| 020 | success[3] / PRD-RESULT-SNAPSHOT | passed | failed | product_defect, judge_false_pass |
| 020 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | not_applicable | conditional_not_applicable, confirmed_raw_verdict |
| 021 | success[0] / PRD-IMPORT-MISSING | passed | passed | confirmed_raw_verdict |
| 021 | success[1] / PRD-IDENTITY-LIMIT | passed | passed | confirmed_raw_verdict |
| 021 | success[2] / PRD-IMPORT-SNAPSHOT-UNKNOWN | passed | passed | confirmed_raw_verdict |
| 021 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | passed | judge_missed_execution |
| 022 | success[0] / PRD-IMPORT-MISSING | passed | passed | confirmed_raw_verdict |
| 022 | success[1] / PRD-IDENTITY-LIMIT | passed | passed | confirmed_raw_verdict |
| 022 | success[2] / PRD-IMPORT-SNAPSHOT-UNKNOWN | passed | passed | confirmed_raw_verdict |
| 022 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | passed | judge_missed_execution |
| 023 | success[0] / PRD-IMPORT-MISSING | passed | passed | confirmed_raw_verdict |
| 023 | success[1] / PRD-IDENTITY-LIMIT | passed | passed | confirmed_raw_verdict |
| 023 | success[2] / PRD-IMPORT-SNAPSHOT-UNKNOWN | passed | passed | confirmed_raw_verdict |
| 023 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | passed | judge_missed_execution |
| 024 | success[0] / PRD-IMPORT-MISSING | passed | passed | confirmed_raw_verdict |
| 024 | success[1] / PRD-IDENTITY-LIMIT | passed | passed | confirmed_raw_verdict |
| 024 | success[2] / PRD-IMPORT-SNAPSHOT-UNKNOWN | passed | passed | confirmed_raw_verdict |
| 024 | recovery[0] / CONDITIONAL-RECOVERY | not_applicable | passed | judge_missed_execution |

## Persona 013

Result SHA-256: `2d92908c7b17f4d1dbfed676265d444d58295c9dd9f7f2f7fe60c8946b7d9a0f`; checkpoint SHA-256: `5096dcc677905127e85b4eb76d37ce0d0e71384211db2b2d296635a6f8d13976`. Verified 28 registered artifacts (775070 bytes) across 13 observations.

### success[0] — PRD-IMPORT-PROGRESS

obs-5 established a new persisted current-fixture baseline. The scoped progress attempt in obs-8 sampled reading at 6 ms and analysis at 51 ms, recorded cancel_active=true and cancel_dispatched=true, ended cancelled_without_new_result after a 1,115 ms observation window, and preserved the same 401ca05d4e2b93517fe5eb77ebeba21b66891c2695091ce34708a808a561dbb3 storage digest. The PNGs show pre-upload/post-cancel selection states; active cancellation is supported by the admitted guarded-dispatch facts, not a claimed active-cancel screenshot or an exact dispatch timestamp.

Evidence: `obs-5 / log-5` (setup); `obs-8 / log-8` (result); `obs-8 / png-8-0` (context); `obs-8 / png-8-1` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-IMPORT-SIZE

The actual 128 MiB+1 ZIP, 32 MiB+1 loose-file group and over-64 MiB loose aggregate were each uploaded separately in obs-9/10/11. Each corresponding DOM observation contains its specific size rejection, and before/after/current storage stays at the saved 401ca05d4e2b93517fe5eb77ebeba21b66891c2695091ce34708a808a561dbb3 baseline. The captured modal viewport does not expose the rejection paragraphs; the rejection wording is supported by admitted DOM logs rather than claimed visible PNG text.

Evidence: `obs-5 / log-5` (setup); `obs-9 / log-9` (result); `obs-10 / log-10` (result); `obs-11 / log-11` (result); `obs-9 / png-9-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-IMPORT-SAVE-FAIL

obs-12 actually consumed and restored the one-shot peekly_state_v7 write fault during the distinct previous-fixture import. The admitted save-error DOM and unchanged 401ca05d4e2b93517fe5eb77ebeba21b66891c2695091ce34708a808a561dbb3 baseline establish the failed write with prior-state preservation. Its complete 19-control inventory contains no 다시 저장 action; the viewed frame offers only 다른 파일 고르기. The error paragraph itself is outside the captured viewport. Successful ordinary re-selection afterward does not satisfy or erase the missing direct-save-retry requirement.

Evidence: `obs-5 / log-5` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-1` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

After the acknowledged consumed/restored save failure in obs-12, obs-13 performs exactly one ordinary upload of the same failed peekly-sample-previous.zip through the observed file input. Its before digest equals the preserved failed-attempt baseline, its completion sample appears at 28 ms, and its after/current digest changes to f11c5fbd771cd44df0de8603fa850a5fdee3c4671e9f31552232dae0b94347a5. The saved result and success toast are visible. This confirms safe persisted recovery while the separate direct-retry product failure remains failed.

Evidence: `obs-12 / log-12` (setup); `obs-13 / log-13` (result); `obs-13 / png-13-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: The save-error and size-error paragraphs are in admitted DOM text but outside the captured 756x413 modal viewport; no active-cancel frame is captured.

## Persona 015

Result SHA-256: `b2c78a26376232e7d1e26c3c325ad2ae961204b69d3b05074579fd0daed9feed`; checkpoint SHA-256: `bd80b0ec1ccbc32ad526560f3fa96221236d5d635e708950db970b921f9af4c6`. Verified 30 registered artifacts (814766 bytes) across 14 observations.

### success[0] — PRD-IMPORT-PROGRESS

obs-7 established a new persisted current-fixture baseline. obs-10 sampled reading at 3 ms and analysis at 61 ms, recorded cancel_active=true and cancel_dispatched=true, ended cancelled_without_new_result after a 1,105 ms observation window, and preserved 0cb983c39b7af7bcd743d34a6b2054dc40a46a68277dfb58adda5de4db148f4b. The PNGs are pre-upload/post-cancel selection states; active cancellation is supported by admitted guarded-dispatch facts, not a visible active-cancel frame or exact dispatch timestamp.

Evidence: `obs-7 / log-7` (setup); `obs-10 / log-10` (result); `obs-10 / png-10-0` (context); `obs-10 / png-10-1` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-IMPORT-SIZE

obs-11/12/13 separately uploaded the pinned 128 MiB+1 ZIP, 32 MiB+1 loose-file group and over-64 MiB loose aggregate. Each admitted DOM contains the corresponding 128MB, 32MB or 64MB rejection, and each before/after/current storage digest equals the actual saved 0cb983c39b7af7bcd743d34a6b2054dc40a46a68277dfb58adda5de4db148f4b baseline. Rejection paragraphs are outside the captured modal viewport; wording is supported by the DOM logs rather than claimed visible PNG text.

Evidence: `obs-7 / log-7` (setup); `obs-11 / log-11` (result); `obs-12 / log-12` (result); `obs-13 / log-13` (result); `obs-11 / png-11-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-IMPORT-SAVE-FAIL

obs-14 consumed and restored the one-shot peekly_state_v7 fault during the distinct previous-fixture import and retained the saved 0cb983c39b7af7bcd743d34a6b2054dc40a46a68277dfb58adda5de4db148f4b baseline. The admitted save-error DOM and complete 19-control inventory show no 다시 저장 action. The viewed final frame offers 다른 파일 고르기; the error paragraph is outside its captured viewport. This proves the missing direct-save-retry product requirement, independently of general recovery.

Evidence: `obs-7 / log-7` (setup); `obs-14 / log-14` (result); `obs-14 / png-14-1` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

The literal recovery criterion is triggered by an actual recoverable import/save failure and does not exempt expected fixture failures. obs-14 is a definitely completed failed save with consumed=true, restored=true, unchanged valid baseline, admitted error DOM and observed normal file selection. The session finalizes at obs-14 without any subsequent ordinary reimport or persisted recovery. Raw N/A incorrectly excludes this real trigger; recovery is not_run because it was unattempted, not a product recovery failure. This is a new remaining NR outside the historical 23-row baseline.

Evidence: `obs-7 / log-7` (setup); `obs-11 / log-11` (context); `obs-12 / log-12` (context); `obs-13 / log-13` (context); `obs-14 / log-14` (result); `obs-14 / png-14-1` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: Size/save error paragraphs are admitted DOM text outside the captured viewport. No active-cancel frame or exact dispatch timestamp is recorded.

## Persona 016

Result SHA-256: `22a301ce66fbb807c25688ee6c7427a624ceb8ceb94b636c226b67a227beb39b`; checkpoint SHA-256: `e0062d181c302429159d006c51ce8c7eff53d125e8eddc877c965914b263dea8`. Verified 28 registered artifacts (777540 bytes) across 13 observations.

### success[0] — PRD-IMPORT-PROGRESS

obs-5 established a new persisted current-fixture baseline. obs-8 sampled reading at 0 ms and analysis at 26 ms, recorded cancel_active=true and cancel_dispatched=true, ended cancelled_without_new_result after a 1,085 ms observation window, and preserved 117b07616a1f2aa17fc3df37fa24f904575d3d930bafd9c2d8b58bf01f0cf51b. The PNGs are pre-upload/post-cancel selection states; active cancellation is supported by admitted guarded-dispatch facts, not a visible active-cancel frame or exact dispatch timestamp.

Evidence: `obs-5 / log-5` (setup); `obs-8 / log-8` (result); `obs-8 / png-8-0` (context); `obs-8 / png-8-1` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-IMPORT-SIZE

obs-9/10/11 separately uploaded the pinned 128 MiB+1 ZIP, 32 MiB+1 loose-file group and over-64 MiB loose aggregate. Each admitted DOM contains the corresponding 128MB, 32MB or 64MB rejection, and each before/after/current storage digest equals the actual saved 117b07616a1f2aa17fc3df37fa24f904575d3d930bafd9c2d8b58bf01f0cf51b baseline. Rejection paragraphs are outside the captured modal viewport; wording is supported by the DOM logs rather than claimed visible PNG text.

Evidence: `obs-5 / log-5` (setup); `obs-9 / log-9` (result); `obs-10 / log-10` (result); `obs-11 / log-11` (result); `obs-9 / png-9-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-IMPORT-SAVE-FAIL

obs-12 consumed and restored the one-shot peekly_state_v7 fault during the distinct previous-fixture import and retained the saved 117b07616a1f2aa17fc3df37fa24f904575d3d930bafd9c2d8b58bf01f0cf51b baseline. The admitted save-error DOM and complete 19-control inventory show no 다시 저장 action. The viewed final frame offers 다른 파일 고르기; the error paragraph is outside its captured viewport. This proves the missing direct-save-retry product requirement, independently of general recovery.

Evidence: `obs-5 / log-5` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-1` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

After the acknowledged consumed/restored failed save in obs-12, obs-13 performs one ordinary upload of the same failed peekly-sample-previous.zip. Its before digest equals the preserved baseline; its completion sample appears at 9 ms and its after/current digest changes to d1a4371f7cfb1317cb490ad905643694565ee658a8c226cce1ed2b64d9bdfd63. The viewed saved-result frame and success toast support actual persisted recovery. The separate missing direct retry remains failed.

Evidence: `obs-12 / log-12` (setup); `obs-13 / log-13` (result); `obs-13 / png-13-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: Size/save error paragraphs are admitted DOM text outside the captured viewport. No active-cancel frame or exact dispatch timestamp is recorded.

## Persona 017

Result SHA-256: `355660544f87364b6c3f96d57c0ac8150a6ab0692b6d1d7d6dbf23ea3dc2cc8b`; checkpoint SHA-256: `3beac525b02142bf9902b0188d9a7621896fd69b9644d22ea50bb4eb83af66ee`. Verified 34 registered artifacts (866990 bytes) across 17 observations.

### success[0] — PRD-RESULT-RECIPROCITY

The ordinary previous import in obs-5 and current import in obs-8 form one persisted storage chain. With the current import retained at b27288687710063289433db955270fddbf2c9dc1ae930a9495140ad02581d4b4, obs-13 actually hit-tests and opens the required category sheet: count 5, complete admitted row set atelier.luna_, ina.archive, junho.jeong, minsu.kim_, taeo.kang_. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-5 / log-5` (setup); `obs-8 / log-8` (setup); `obs-13 / log-13` (result); `obs-13 / png-13-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-RESULT-REVERSE

The ordinary previous import in obs-5 and current import in obs-8 form one persisted storage chain. With the current import retained at b27288687710063289433db955270fddbf2c9dc1ae930a9495140ad02581d4b4, obs-15 actually hit-tests and opens the required category sheet: count 2, complete admitted row set haneul.song, seongsu.coffee. The screenshot confirms the sheet label/count and both rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-5 / log-5` (setup); `obs-8 / log-8` (setup); `obs-15 / log-15` (result); `obs-15 / png-15-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-RESULT-MUTUAL

The ordinary previous import in obs-5 and current import in obs-8 form one persisted storage chain. With the current import retained at b27288687710063289433db955270fddbf2c9dc1ae930a9495140ad02581d4b4, obs-17 actually hit-tests and opens the required category sheet: count 5, complete admitted row set dohyun.fit, haerin.daily, minji_kim, seojun.park, yuna.choi. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-5 / log-5` (setup); `obs-8 / log-8` (setup); `obs-17 / log-17` (result); `obs-17 / png-17-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[3] — PRD-RESULT-SNAPSHOT

The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-5/8 persist the expected pair; obs-10 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels.

Evidence: `obs-5 / log-5` (setup); `obs-8 / log-8` (setup); `obs-10 / log-10` (result); `obs-10 / png-10-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

All 17 admitted observations were reviewed. The two ordinary valid imports completed and persisted, followed by normal navigation through the comparison and all three relationship sheets. No recoverable browser/import rejection or failed save is observed in this session. The product's inferred-cause defect is not an import/browser failure requiring the conditional recovery action. Raw N/A is retained and earns no execution credit.

Evidence: `obs-1 / log-1` (context); `obs-2 / log-2` (context); `obs-3 / log-3` (context); `obs-4 / log-4` (context); `obs-5 / log-5` (context); `obs-6 / log-6` (context); `obs-7 / log-7` (context); `obs-8 / log-8` (context); `obs-9 / log-9` (context); `obs-10 / log-10` (context); `obs-11 / log-11` (context); `obs-12 / log-12` (context); `obs-13 / log-13` (context); `obs-14 / log-14` (context); `obs-15 / log-15` (context); `obs-16 / log-16` (context); `obs-17 / log-17` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: Category screenshots show labels/counts and upper rows; full row sets are admitted DOM evidence. The comparison caveat is visible, but causal badges occur below the captured crop and are supported by that same observation's DOM.

## Persona 018

Result SHA-256: `f9674665f4fdbb0b3e1f76a196aba820ba906eae580a42eb58a459dec23558e6`; checkpoint SHA-256: `b9ab869b84bbefb167cd78f0ce10dfd85b83a1c2e60b5f3e5d19c2fb43ef9211`. Verified 32 registered artifacts (823233 bytes) across 16 observations.

### success[0] — PRD-RESULT-RECIPROCITY

The ordinary previous import in obs-4 and current import in obs-7 form one persisted storage chain. With the current import retained at 3c0e4d3a5b0bb3037b397cab5a7b22cb187502401e5ef80a69a4e70744771126, obs-12 actually hit-tests and opens the required category sheet: count 5, complete admitted row set atelier.luna_, ina.archive, junho.jeong, minsu.kim_, taeo.kang_. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-RESULT-REVERSE

The ordinary previous import in obs-4 and current import in obs-7 form one persisted storage chain. With the current import retained at 3c0e4d3a5b0bb3037b397cab5a7b22cb187502401e5ef80a69a4e70744771126, obs-14 actually hit-tests and opens the required category sheet: count 2, complete admitted row set haneul.song, seongsu.coffee. The screenshot confirms the sheet label/count and both rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-14 / log-14` (result); `obs-14 / png-14-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-RESULT-MUTUAL

The ordinary previous import in obs-4 and current import in obs-7 form one persisted storage chain. With the current import retained at 3c0e4d3a5b0bb3037b397cab5a7b22cb187502401e5ef80a69a4e70744771126, obs-16 actually hit-tests and opens the required category sheet: count 5, complete admitted row set dohyun.fit, haerin.daily, minji_kim, seojun.park, yuna.choi. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-16 / log-16` (result); `obs-16 / png-16-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[3] — PRD-RESULT-SNAPSHOT

The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-4/7 persist the expected pair; obs-9 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-9 / log-9` (result); `obs-9 / png-9-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

All 16 admitted observations were reviewed. The two ordinary valid imports completed and persisted, followed by normal navigation through the comparison and all three relationship sheets. No recoverable browser/import rejection or failed save is observed in this session. The product's inferred-cause defect is not an import/browser failure requiring the conditional recovery action. Raw N/A is retained and earns no execution credit.

Evidence: `obs-1 / log-1` (context); `obs-2 / log-2` (context); `obs-3 / log-3` (context); `obs-4 / log-4` (context); `obs-5 / log-5` (context); `obs-6 / log-6` (context); `obs-7 / log-7` (context); `obs-8 / log-8` (context); `obs-9 / log-9` (context); `obs-10 / log-10` (context); `obs-11 / log-11` (context); `obs-12 / log-12` (context); `obs-13 / log-13` (context); `obs-14 / log-14` (context); `obs-15 / log-15` (context); `obs-16 / log-16` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: Category screenshots show labels/counts and upper rows; full row sets are admitted DOM evidence. The comparison caveat is visible, but causal badges occur below the captured crop and are supported by that same observation's DOM.

## Persona 019

Result SHA-256: `48c41d21ab0b7599aece798a7a928a3557633d55db8369495cf57e2ebf06509e`; checkpoint SHA-256: `e43c0f9783986282d59ba49eb59d7ae9341a3e279d1d2d368d4d0c8c926e0617`. Verified 32 registered artifacts (804073 bytes) across 16 observations.

### success[0] — PRD-RESULT-RECIPROCITY

The ordinary previous import in obs-6 and current import in obs-9 form one persisted storage chain. With the current import retained at 66d933cfd77338b6562e49a06319445828c010008ca46f91f543d1ffaee683c3, obs-10 actually hit-tests and opens the required category sheet: count 5, complete admitted row set atelier.luna_, ina.archive, junho.jeong, minsu.kim_, taeo.kang_. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-6 / log-6` (setup); `obs-9 / log-9` (setup); `obs-10 / log-10` (result); `obs-10 / png-10-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-RESULT-REVERSE

The ordinary previous import in obs-6 and current import in obs-9 form one persisted storage chain. With the current import retained at 66d933cfd77338b6562e49a06319445828c010008ca46f91f543d1ffaee683c3, obs-12 actually hit-tests and opens the required category sheet: count 2, complete admitted row set haneul.song, seongsu.coffee. The screenshot confirms the sheet label/count and both rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-6 / log-6` (setup); `obs-9 / log-9` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-RESULT-MUTUAL

The ordinary previous import in obs-6 and current import in obs-9 form one persisted storage chain. With the current import retained at 66d933cfd77338b6562e49a06319445828c010008ca46f91f543d1ffaee683c3, obs-14 actually hit-tests and opens the required category sheet: count 5, complete admitted row set dohyun.fit, haerin.daily, minji_kim, seojun.park, yuna.choi. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-6 / log-6` (setup); `obs-9 / log-9` (setup); `obs-14 / log-14` (result); `obs-14 / png-14-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[3] — PRD-RESULT-SNAPSHOT

The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-6/7 persist the expected pair; obs-16 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels.

Evidence: `obs-6 / log-6` (setup); `obs-9 / log-9` (setup); `obs-16 / log-16` (result); `obs-16 / png-16-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

All 16 admitted observations were reviewed. The two ordinary valid imports completed and persisted, followed by normal navigation through the comparison and all three relationship sheets. No recoverable browser/import rejection or failed save is observed in this session. The product's inferred-cause defect is not an import/browser failure requiring the conditional recovery action. Raw N/A is retained and earns no execution credit.

Evidence: `obs-1 / log-1` (context); `obs-2 / log-2` (context); `obs-3 / log-3` (context); `obs-4 / log-4` (context); `obs-5 / log-5` (context); `obs-6 / log-6` (context); `obs-7 / log-7` (context); `obs-8 / log-8` (context); `obs-9 / log-9` (context); `obs-10 / log-10` (context); `obs-11 / log-11` (context); `obs-12 / log-12` (context); `obs-13 / log-13` (context); `obs-14 / log-14` (context); `obs-15 / log-15` (context); `obs-16 / log-16` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: The category labels/counts and upper rows are visible; complete sets are admitted DOM evidence. Comparison caveat is visible; contradictory causal badges are same-observation DOM below the captured crop.

## Persona 020

Result SHA-256: `3bd6ab6f5a3d798838a65a79e8a8a8d9d092d04f3714f3caca7a50fa54bf52d4`; checkpoint SHA-256: `dc5b72c738b7ae33d678e32171294c46700ff04dc61763dd53dfed5a171a3430`. Verified 32 registered artifacts (821895 bytes) across 16 observations.

### success[0] — PRD-RESULT-RECIPROCITY

The ordinary previous import in obs-4 and current import in obs-7 form one persisted storage chain. With the current import retained at 70da2011655df18dfc36624837eddc6aaed9c3325d524f56cecb9672ec016031, obs-12 actually hit-tests and opens the required category sheet: count 5, complete admitted row set atelier.luna_, ina.archive, junho.jeong, minsu.kim_, taeo.kang_. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-RESULT-REVERSE

The ordinary previous import in obs-4 and current import in obs-7 form one persisted storage chain. With the current import retained at 70da2011655df18dfc36624837eddc6aaed9c3325d524f56cecb9672ec016031, obs-14 actually hit-tests and opens the required category sheet: count 2, complete admitted row set haneul.song, seongsu.coffee. The screenshot confirms the sheet label/count and both rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-14 / log-14` (result); `obs-14 / png-14-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-RESULT-MUTUAL

The ordinary previous import in obs-4 and current import in obs-7 form one persisted storage chain. With the current import retained at 70da2011655df18dfc36624837eddc6aaed9c3325d524f56cecb9672ec016031, obs-16 actually hit-tests and opens the required category sheet: count 5, complete admitted row set dohyun.fit, haerin.daily, minji_kim, seojun.park, yuna.choi. The screenshot confirms the sheet label/count and its upper rows; the full set is supported by the registered DOM list rows. No sample-mode or dashboard-only evidence is used.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-16 / log-16` (result); `obs-16 / png-16-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[3] — PRD-RESULT-SNAPSHOT

The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-4/7 persist the expected pair; obs-9 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels.

Evidence: `obs-4 / log-4` (setup); `obs-7 / log-7` (setup); `obs-9 / log-9` (result); `obs-9 / png-9-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

All 16 admitted observations were reviewed. The two ordinary valid imports completed and persisted, followed by normal navigation through the comparison and all three relationship sheets. No recoverable browser/import rejection or failed save is observed in this session. The product's inferred-cause defect is not an import/browser failure requiring the conditional recovery action. Raw N/A is retained and earns no execution credit.

Evidence: `obs-1 / log-1` (context); `obs-2 / log-2` (context); `obs-3 / log-3` (context); `obs-4 / log-4` (context); `obs-5 / log-5` (context); `obs-6 / log-6` (context); `obs-7 / log-7` (context); `obs-8 / log-8` (context); `obs-9 / log-9` (context); `obs-10 / log-10` (context); `obs-11 / log-11` (context); `obs-12 / log-12` (context); `obs-13 / log-13` (context); `obs-14 / log-14` (context); `obs-15 / log-15` (context); `obs-16 / log-16` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: The category labels/counts and upper rows are visible; complete sets are admitted DOM evidence. Comparison caveat is visible; contradictory causal badges are same-observation DOM below the captured crop.

## Persona 021

Result SHA-256: `0a4b3e6bb5d849c0aca9056463a6c4c5c9028411f07c52268466b8ababd464ae`; checkpoint SHA-256: `c0c3ab4d1746f12880f82db3334c1617146d2f3f2ce2671ba391a13811c6c851`. Verified 28 registered artifacts (766225 bytes) across 14 observations.

### success[0] — PRD-IMPORT-MISSING

obs-10 and obs-11 separately submit the pinned missing-followers and missing-following ZIPs. Each completed attempt retains the actual current/legacy storage digest a4ce104c8558ee68d4ff3adc2f60e29d83c706fdf5dbc9a4a5d6aba987b8455e; each admitted DOM requires both lists and asks whether [팔로워 및 팔로잉] was selected. The screenshot shows normal file re-selection, while the rejection paragraph is below its captured crop. These are actual rejected imports, not merely catalogued negative fixtures.

Evidence: `obs-6 / log-6` (setup); `obs-10 / log-10` (result); `obs-11 / log-11` (result); `obs-10 / png-10-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-IDENTITY-LIMIT

The actual same-session known pair is current in obs-6 followed by previous in obs-12, a documented deviation from the prescribed previous→current order. Its active previous snapshot compares with the retained current snapshot, excluding the legacy unknown snapshot. obs-14 hit-tests and opens the exact reverse-direction difference: one yuna.choi row. The viewed PNG and admitted DOM both show the username-change/account-deletion caveat and 이유 모름; no confirmed-unfollow badge appears anywhere in this comparison. This supports this session's IDENTITY requirement without transferring contradictory badges from other sessions or claiming a forward six-person comparison.

Evidence: `obs-6 / log-6` (setup); `obs-12 / log-12` (setup); `obs-14 / log-14` (result); `obs-14 / png-14-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-IMPORT-SNAPSHOT-UNKNOWN

obs-2 is the first mutation after observation and validates the pinned v6 seed through the actual v7 product loader: fresh_owned_profile, initial_storage_match, migration_validated and reload_observed are true. It retains exactly one non-sample unknown snapshot with null active/comparison IDs. Before any previous import, obs-6 adds only current; obs-7 retains exactly unknown plus current for the same account, with active and comparison both pointing to current at a4ce104c8558ee68d4ff3adc2f60e29d83c706fdf5dbc9a4a5d6aba987b8455e. Its genuinely opened Home notice visibly excludes incomplete old records from analysis; the admitted Home DOM asks for a subsequent record and has no departed-follower comparison. Inferred migrated included_files does not erase list_completeness=unknown. This verifies the assigned migration/exclusion path; no separate known-empty fixture import was attempted. The known-empty phrase is treated as the predeclared fixture-classification guard, supported by frozen peekly_criteria.py:135–140 and 998–1063, scale_entry.py:65 and 96–100, test_peekly_result_scope.py:473–477, and the seed/current/exclusion-only positive contract in test_peekly_completion_scope.py:60–92 and 156–162. Separate empty-input behavior is unexecuted and uncredited.

Evidence: `obs-1 / log-1` (setup); `obs-2 / log-2` (setup); `obs-6 / log-6` (result); `obs-7 / log-7` (result); `obs-7 / png-7-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

The literal conditional criterion has no unexpected-failure-only exception. The actual missing-list rejections in obs-10/11 trigger it; obs-12 then performs one permitted ordinary valid previous-fixture upload through the observed file input. It preserves the rejected-attempt baseline as its before digest and persists a new result at cda27becf7d3dbb117e81822b13ef55e0d3a9899331dd34c39e5f482c8689875; the completion sample is 35 ms and the saved-result/success-toast PNG is visible. Raw N/A missed this executed, persisted recovery and becomes PASS. No uncertain operation is repeated.

Evidence: `obs-10 / log-10` (setup); `obs-11 / log-11` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: The expanded legacy Home exclusion notice, recovered saved result/toast, comparison caveat and sole reason-unknown row are visible. Missing-list rejection paragraphs and the subsequent-record prompt are supported by admitted DOM below the captured crop.

## Persona 022

Result SHA-256: `9852c5a4d4d56d1162efd121f3e61fc35c3501162c73b9ba4f47b6af6815d4b7`; checkpoint SHA-256: `2e5860762bbb7224c6e940509310061686f730b67d52fba343a3aebb171c31bd`. Verified 28 registered artifacts (765852 bytes) across 14 observations.

### success[0] — PRD-IMPORT-MISSING

obs-10 and obs-11 separately submit the pinned missing-followers and missing-following ZIPs. Each completed attempt retains the actual current/legacy storage digest e002e6e16c74f4c689bde5f93a4413632a41b7d01603ce976d747f280d074f04; each admitted DOM requires both lists and asks whether [팔로워 및 팔로잉] was selected. The screenshot shows normal file re-selection, while the rejection paragraph is below its captured crop. These are actual rejected imports, not merely catalogued negative fixtures.

Evidence: `obs-6 / log-6` (setup); `obs-10 / log-10` (result); `obs-11 / log-11` (result); `obs-10 / png-10-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-IDENTITY-LIMIT

The actual same-session known pair is current in obs-6 followed by previous in obs-12, a documented deviation from the prescribed previous→current order. Its active previous snapshot compares with the retained current snapshot, excluding the legacy unknown snapshot. obs-14 hit-tests and opens the exact reverse-direction difference: one yuna.choi row. The viewed PNG and admitted DOM both show the username-change/account-deletion caveat and 이유 모름; no confirmed-unfollow badge appears anywhere in this comparison. This supports this session's IDENTITY requirement without transferring contradictory badges from other sessions or claiming a forward six-person comparison.

Evidence: `obs-6 / log-6` (setup); `obs-12 / log-12` (setup); `obs-14 / log-14` (result); `obs-14 / png-14-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-IMPORT-SNAPSHOT-UNKNOWN

obs-2 is the first mutation after observation and validates the pinned v6 seed through the actual v7 product loader: fresh_owned_profile, initial_storage_match, migration_validated and reload_observed are true. It retains exactly one non-sample unknown snapshot with null active/comparison IDs. Before any previous import, obs-6 adds only current; obs-7 retains exactly unknown plus current for the same account, with active and comparison both pointing to current at e002e6e16c74f4c689bde5f93a4413632a41b7d01603ce976d747f280d074f04. Its genuinely opened Home notice visibly excludes incomplete old records from analysis; the admitted Home DOM asks for a subsequent record and has no departed-follower comparison. Inferred migrated included_files does not erase list_completeness=unknown. This verifies the assigned migration/exclusion path; no separate known-empty fixture import was attempted. The known-empty phrase is treated as the predeclared fixture-classification guard, supported by frozen peekly_criteria.py:135–140 and 998–1063, scale_entry.py:65 and 96–100, test_peekly_result_scope.py:473–477, and the seed/current/exclusion-only positive contract in test_peekly_completion_scope.py:60–92 and 156–162. Separate empty-input behavior is unexecuted and uncredited.

Evidence: `obs-1 / log-1` (setup); `obs-2 / log-2` (setup); `obs-6 / log-6` (result); `obs-7 / log-7` (result); `obs-7 / png-7-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

The literal conditional criterion has no unexpected-failure-only exception. The actual missing-list rejections in obs-10/11 trigger it; obs-12 then performs one permitted ordinary valid previous-fixture upload through the observed file input. It preserves the rejected-attempt baseline as its before digest and persists a new result at e2fef179a1885fea8261602d220dc7344b3eebe18fbe5bcf771caab199988ab9; the completion sample is 4 ms and the saved-result/success-toast PNG is visible. Raw N/A missed this executed, persisted recovery and becomes PASS. No uncertain operation is repeated.

Evidence: `obs-10 / log-10` (setup); `obs-11 / log-11` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: The expanded legacy Home exclusion notice, recovered saved result/toast, comparison caveat and sole reason-unknown row are visible. Missing-list rejection paragraphs and the subsequent-record prompt are supported by admitted DOM below the captured crop.

## Persona 023

Result SHA-256: `b2a28e014af1cc091a7027e3cfece7e9e5bbd348ba30f0d774ecfa9f68f82161`; checkpoint SHA-256: `4a50978fe7bdb78871ef1ecb94ea07c5c295e33ec1a3f632c0e8e9e6ea5c1007`. Verified 28 registered artifacts (767044 bytes) across 14 observations.

### success[0] — PRD-IMPORT-MISSING

obs-10 and obs-11 separately submit the pinned missing-followers and missing-following ZIPs. Each completed attempt retains the actual current/legacy storage digest 10611cc54a16080de9ec2b41f9e28c98bfda7cac65cb5450be5ba92e368c083a; each admitted DOM requires both lists and asks whether [팔로워 및 팔로잉] was selected. The screenshot shows normal file re-selection, while the rejection paragraph is below its captured crop. These are actual rejected imports, not merely catalogued negative fixtures.

Evidence: `obs-6 / log-6` (setup); `obs-10 / log-10` (result); `obs-11 / log-11` (result); `obs-10 / png-10-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-IDENTITY-LIMIT

The actual same-session known pair is current in obs-6 followed by previous in obs-12, a documented deviation from the prescribed previous→current order. Its active previous snapshot compares with the retained current snapshot, excluding the legacy unknown snapshot. obs-14 hit-tests and opens the exact reverse-direction difference: one yuna.choi row. The viewed PNG and admitted DOM both show the username-change/account-deletion caveat and 이유 모름; no confirmed-unfollow badge appears anywhere in this comparison. This supports this session's IDENTITY requirement without transferring contradictory badges from other sessions or claiming a forward six-person comparison.

Evidence: `obs-6 / log-6` (setup); `obs-12 / log-12` (setup); `obs-14 / log-14` (result); `obs-14 / png-14-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-IMPORT-SNAPSHOT-UNKNOWN

obs-2 is the first mutation after observation and validates the pinned v6 seed through the actual v7 product loader: fresh_owned_profile, initial_storage_match, migration_validated and reload_observed are true. It retains exactly one non-sample unknown snapshot with null active/comparison IDs. Before any previous import, obs-6 adds only current; obs-7 retains exactly unknown plus current for the same account, with active and comparison both pointing to current at 10611cc54a16080de9ec2b41f9e28c98bfda7cac65cb5450be5ba92e368c083a. Its genuinely opened Home notice visibly excludes incomplete old records from analysis; the admitted Home DOM asks for a subsequent record and has no departed-follower comparison. Inferred migrated included_files does not erase list_completeness=unknown. This verifies the assigned migration/exclusion path; no separate known-empty fixture import was attempted. The known-empty phrase is treated as the predeclared fixture-classification guard, supported by frozen peekly_criteria.py:135–140 and 998–1063, scale_entry.py:65 and 96–100, test_peekly_result_scope.py:473–477, and the seed/current/exclusion-only positive contract in test_peekly_completion_scope.py:60–92 and 156–162. Separate empty-input behavior is unexecuted and uncredited.

Evidence: `obs-1 / log-1` (setup); `obs-2 / log-2` (setup); `obs-6 / log-6` (result); `obs-7 / log-7` (result); `obs-7 / png-7-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

The literal conditional criterion has no unexpected-failure-only exception. The actual missing-list rejections in obs-10/11 trigger it; obs-12 then performs one permitted ordinary valid previous-fixture upload through the observed file input. It preserves the rejected-attempt baseline as its before digest and persists a new result at 274a3a4c9ce858615bfefaae377b3c563f55fe3be1017431fe635b3b21843d3a; the completion sample is 27 ms and the saved-result/success-toast PNG is visible. Raw N/A missed this executed, persisted recovery and becomes PASS. No uncertain operation is repeated.

Evidence: `obs-10 / log-10` (setup); `obs-11 / log-11` (setup); `obs-12 / log-12` (result); `obs-12 / png-12-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: The expanded Home exclusion notice, saved recovery result/toast and sole comparison row with caveat/reason-unknown are visible in the verified PNGs. Missing-list rejection and next-record prompt are admitted DOM text below the captured crop. Byte-identical PNGs are explicitly identified where their pixels were already viewed.

## Persona 024

Result SHA-256: `b3360d3f353f8bac9f53bade1de8902fa77e21ec358ff67e298acec2f7e40348`; checkpoint SHA-256: `306691972b5d0be47a7bbb3184ae80dfc44d37271ead384e7be68b5917e818e8`. Verified 30 registered artifacts (827145 bytes) across 15 observations.

### success[0] — PRD-IMPORT-MISSING

obs-9 and obs-10 separately submit the pinned missing-followers and missing-following ZIPs. Each completed attempt retains the actual current/legacy storage digest 3a15edf2b2554e7af318a4417687304e5f3136faf916f7bf4e4177bf9f2ecf9f; each admitted DOM requires both lists and asks whether [팔로워 및 팔로잉] was selected. The screenshot shows normal file re-selection, while the rejection paragraph is below its captured crop. These are actual rejected imports, not merely catalogued negative fixtures.

Evidence: `obs-5 / log-5` (setup); `obs-9 / log-9` (result); `obs-10 / log-10` (result); `obs-9 / png-9-0` (context). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[1] — PRD-IDENTITY-LIMIT

The actual same-session known pair is current in obs-5 followed by previous in obs-11, a documented deviation from the prescribed previous→current order. Its active previous snapshot compares with the retained current snapshot, excluding the legacy unknown snapshot. obs-15 hit-tests and opens the exact reverse-direction difference: one yuna.choi row. The viewed PNG and admitted DOM both show the username-change/account-deletion caveat and 이유 모름; no confirmed-unfollow badge appears anywhere in this comparison. This supports this session's IDENTITY requirement without transferring contradictory badges from other sessions or claiming a forward six-person comparison.

Evidence: `obs-5 / log-5` (setup); `obs-11 / log-11` (setup); `obs-15 / log-15` (result); `obs-15 / png-15-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### success[2] — PRD-IMPORT-SNAPSHOT-UNKNOWN

obs-2 is the first mutation after observation and validates the pinned v6 seed through the actual v7 product loader: fresh_owned_profile, initial_storage_match, migration_validated and reload_observed are true. It retains exactly one non-sample unknown snapshot with null active/comparison IDs. Before any previous import, obs-5 adds only current; obs-6 retains exactly unknown plus current for the same account, with active and comparison both pointing to current at 3a15edf2b2554e7af318a4417687304e5f3136faf916f7bf4e4177bf9f2ecf9f. Its genuinely opened Home notice visibly excludes incomplete old records from analysis; the admitted Home DOM asks for a subsequent record and has no departed-follower comparison. Inferred migrated included_files does not erase list_completeness=unknown. This verifies the assigned migration/exclusion path; no separate known-empty fixture import was attempted. The known-empty phrase is treated as the predeclared fixture-classification guard, supported by frozen peekly_criteria.py:135–140 and 998–1063, scale_entry.py:65 and 96–100, test_peekly_result_scope.py:473–477, and the seed/current/exclusion-only positive contract in test_peekly_completion_scope.py:60–92 and 156–162. Separate empty-input behavior is unexecuted and uncredited.

Evidence: `obs-1 / log-1` (setup); `obs-2 / log-2` (setup); `obs-5 / log-5` (result); `obs-6 / log-6` (result); `obs-6 / png-6-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

### recovery[0] — CONDITIONAL-RECOVERY

The literal conditional criterion has no unexpected-failure-only exception. The actual missing-list rejections in obs-9/10 trigger it; obs-11 then performs one permitted ordinary valid previous-fixture upload through the observed file input. It preserves the rejected-attempt baseline as its before digest and persists a new result at 37783829d6930fa47d96083d6bc0354cf702468188f769c5f2145a7a83a3241e; the completion sample is 30 ms and the saved-result/success-toast PNG is visible. Raw N/A missed this executed, persisted recovery and becomes PASS. No uncertain operation is repeated.

Evidence: `obs-9 / log-9` (setup); `obs-10 / log-10` (setup); `obs-11 / log-11` (result); `obs-11 / png-11-0` (result). Exact receipt-relative paths and SHA-256 values are in the JSON fragment.

Visual qualification: The expanded Home exclusion notice, saved recovery result/toast and sole comparison row with caveat/reason-unknown are visible in the verified PNGs. Missing-list rejection and next-record prompt are admitted DOM text below the captured crop. Byte-identical PNGs are explicitly identified where their pixels were already viewed.

## Excluded uncertain session 014

No final result exists. All three success criteria and recovery are excluded, not counted as NR or product failure. Nine admitted partial observations and 19 artifacts (502,328 bytes) were rehashed and binding-checked. Original operation `op-ae10298c78b325afb8a9847dc16a57af3ecc8b69` (request SHA `86b1039d9fcc29eee8bf031bf24263b535dd3cb39e7b22a26525235f3da59f40`) attempted the oversized ZIP upload. Node command 11 failed in upload_target_resolution after 54,176 ms with cdp_timeout:DOM.getDocument; upload_dispatch was not reached. Python host elapsed time was 60.397 s and retained transport_uncertain. These delays do not establish an underlying Chrome, event-loop or I/O cause.

The Node lifecycle separately records closed at 21:11:36.654Z with stopped/browser_stopped/proxy_stopped true. Final cohort host teardown remains pending; this is not a substitute for it. No resend, replay or external cleanup occurred.

## Remaining work

Semantic review of the full assigned partition is complete: 48 assessed decisions and four excluded uncertain criteria. Reconcile against final eligibility and sealed global raw outputs before applying. Root owns the combined review and its one application. New 015 recovery NR is outside the historical 23-row baseline.

## UNKNOWN scope interpretation

The recognized-empty phrase is a predeclared fixture-classification guard against treating a known-empty ZIP as unknown legacy provenance. It is not an additional required empty-import journey in this task. Credit is limited to the assigned validated seed → sole-current import → actual Home exclusion path; separate known-empty import behavior remains unexecuted and uncredited.

The following frozen source contracts were read, not executed as tests. Their bytes were checked unchanged from runtime `f50d082a197e683b5961d17919fe219dc48c4d55`.

- `skills/remorsearch-ux-qa/uxpersonas/peekly_criteria.py` (135–140, 998–1063): Definition retains known-empty wording while prescribing legacy seed/current/Home exclusion; production admission grants pass for that chain.

- `skills/remorsearch-ux-qa/uxpersonas/scale_entry.py` (65, 96–100): Exactly legacy JSON and current ZIP are required; the checkpoint precedes other imports and known-empty cannot substitute.

- `tests/test_peekly_result_scope.py` (473–477): Authored definition test explicitly retains known-empty value and excludes empty-ZIP upload from the action.

- `tests/test_peekly_completion_scope.py` (60–92, 156–162): Authored three-observation seed/current/exclusion case is explicitly expected to pass.

- `tests/test_coverage_planning.py` (350–366): Authored planning test requires precisely those two fixtures and rejects the old empty-ZIP journey.

Independent corroboration: `docs/validation/peekly-coverage-completion-20261115/unknown-criterion-scope-review.md`. Separate known-empty behavior receives no new cohort credit. Exact source SHA-256 values and the actual bound task action are preserved in the JSON fragment.
