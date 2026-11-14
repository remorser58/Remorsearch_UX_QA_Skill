# Final cohort audit — 2026-11-14

## 결과와 감사 범위

**최종 결과는 24개 완료 세션, 고유 페르소나 15명이다.** 저장된 세션 판정은 **통과 1 / 실패 6 / 미결론 17**, 기준 전체는 **통과 35 / 실패 6 / 미실행 46 / N/A 17**, 완료 영수증의 `host_protocol`은 **0건**이다. 불확실 전송 **5건**과 대기 **1건**은 이 24세션 밖의 미평가 실행 기록으로 유지한다.

사용자가 지정한 r4/r6 `stage-33`의 **실제 완료 영수증**만 집계했다. r5 031은 보조 관측으로 유지하며 합산하지 않았다. 분석 시작 HEAD와 원격은 `e638375fca8e7c3b76990ac0131eec5f3972a954`, 브랜치는 `rem/peekly-explicit-success-20261113`이었다.

이 보고서는 `e638375` 시점의 불완전한 최신 열을 교체한다. 큐 기록과 과거 커밋은 보존한다. 새 실행·모델·브라우저 호출, 큐 상태 수정, 제품·실행기 코드 수정은 없었다.

## 3열 비교

| 지표 | 최초 `696dbe3` | 재판정 `cb0188d` | 최종 r4 + r6 완료 세션 |
| --- | ---: | ---: | ---: |
| 집계한 완료 세션 | 32 | 32 | **24** |
| 고유 페르소나 | 32 | 32 | **15** |
| 세션 통과 | 0 | 6 | **1** |
| 세션 실패 | 2 | 4 | **6** |
| 세션 미결론 | 30 | 22 | **17** |
| 기준 전체 통과 | 미기록 | 56 | **35** |
| 기준 전체 실패 | 미기록 | 4 | **6** |
| 기준 전체 미실행 | 미기록 | 42 | **46** |
| 기준 전체 N/A | 미기록 | 34 | **17** |
| 완료 영수증의 `host_protocol` | 별도 집계 없음 | 별도 집계 없음 | **0** |

- `696dbe3`: `run-summary-32.json`의 `ux_outcomes_final_32_stage`는 마지막 **16명**의 0/1/15다. 전체 32명의 0/2/30은 해당 커밋 README의 “Supplemental: final 32-persona cohort” 및 `cb0188d` 요약의 `before`로 대조했다. evidence index에는 완료 32, 역사적 대기 2, 불확실 2의 시도 기록이 있다. 전체 기준별 장부가 없으므로 기준 숫자는 미기록으로 둔다.
- `cb0188d`: `verdict-quality-summary.json.after`와 `evidence-index-32.json.personas` 32개에서 **6/4/22**가 일치한다. 초기 engine_conflict 21건은 이후 고정 엔진의 별도 큐에서 실행됐고 최종 cohort 잔여 engine_conflict는 0이다. `e638375`의 4/0/7/미평가 21 표기는 초기 일부 큐를 최종 baseline으로 옮긴 오류였다.
- `cb0188d` 기준: 원시 장부는 success 51 passed / 4 failed / 49 not_run, recovery 5 passed / 27 N/A. 기존 요약이 명시적으로 native 공유 미리보기 7을 scope N/A로 분리하므로 표는 **56 passed / 4 failed / 42 not_run / 34 N/A**를 사용한다.
- 최종 기준은 성공·복구를 합산한 **35/6/46/17**이다. 이전 r4 표의 “success criteria passed 20”은 복구 통과 3까지 섞인 값이었다. 정확한 r4 성공 통과는 17, 복구 통과는 3이다.
- 두 과거 기준은 제품 `58214441`, 최종 큐는 제품/PRD `51110f4`다. 모집단·기준·제품 버전이 달라 이 표에서 인과적인 UX 개선률을 계산하지 않는다.

## 큐와 중복 인원 대조

| 큐 | 완료 | 통과 / 실패 / 미결론 | 기준 전체 통과 / 실패 / 미실행 / N/A | 불확실 | 대기 |
| --- | ---: | ---: | ---: | ---: | ---: |
| r4 | 12 | 1 / 4 / 7 | 20 / 4 / 19 / 9 | 3 | 1 |
| r6 | 12 | 0 / 2 / 10 | 15 / 2 / 27 / 8 | 2 | 0 |
| 합계 | **24** | **1 / 6 / 17** | **35 / 6 / 46 / 17** | **5** | **1** |

두 완료 집합은 9명이 겹친다: **016, 017, 018, 019, 020, 023, 026, 029, 030**.

완료 증거가 있는 고유 15명: **014, 015, 016, 017, 018, 019, 020, 021, 023, 025, 026, 027, 029, 030, 031**.

선택한 r4/r6에 완료 증거가 없는 목표 cohort 17명: **001–013, 022, 024, 028, 032**. 이는 해당 두 큐의 범위이며, 그 사람들이 다른 과거 큐에서도 한 번도 실행되지 않았다는 뜻은 아니다.

r6은 초기 큐의 queued 14개 ID를 대상으로 했지만 r4 완료 집합과 겹친다. 따라서 인수인계의 “실행 기록 없던 14명”을 모든 큐에 대해 검증된 사실로 유지할 수 없다. **24세션은 맞고 24명의 독립 결과는 아니다.**

### 미평가 실행 기록

| 큐 | persona 번호 | job ID | 보존 상태 |
| --- | --- | --- | --- |
| r4 | 021 | `S-plicdikpohnnejkdcgaikgfh` | uncertain |
| r4 | 022 | `S-ggmhldipofnolcjlnleodflf` | uncertain |
| r4 | 025 | `S-eiaeedlhipjocfgjoappiija` | uncertain |
| r4 | 031 | `S-kgmolpibhpcagimpdlbaajin` | queued |
| r6 | 022 | `S-lgdbhgjohjcmhfpnnplhmnil` | uncertain |
| r6 | 027 | `S-kigjbodgmdkadcbgbbpdckal` | uncertain |

5 uncertain은 고유 4명에 걸친 전송 기록이다. 021·025는 r6 완료 기록도 있고 027은 r4 완료 기록도 있으나, 각 uncertain job은 그대로 미평가다. 022는 양쪽 큐 모두 uncertain이다. r4 queued 031은 r6에서 별도 job으로 완료됐어도 원래 queued 기록을 바꾸지 않는다.

r5의 `S-flojkpnlcanpiajnjempledi` / persona 031은 complete/inconclusive다. r6 031과 겹치므로 이번 요청의 r4+r6 합계 밖에 둔다. 이전 초기 큐의 불확실 기록들도 이 보고 범위에 끌어와 합치거나 수정하지 않는다.

### 원본 summary를 그대로 더하면 안 되는 이유

r4의 `evidence_validation.ux_outcomes`는 1/4/11, r6은 0/2/12다. 그 값에는 r4 미완료 4개와 r6 불확실 2개가 inconclusive로 포함된다. `current_valid_sessions`도 16/14로, 완료 영수증 없는 기록까지 포함한다. 따라서 이 audit은 해당 요약을 UX 완료 세션의 근거로 사용하지 않았다.

선택 조건은 다음 모두다: **SQLite `jobs.status == complete` + plan/report/DB job·persona 일치 + `operational_completed == true` + 최종 receipt 존재**. 결과적으로 미결론은 23이 아니라 **17**이다. 보고 집계 결함은 P1로 기록하며 구현 수정은 이 보고 전용 작업 범위 밖이다.

## 기준 단위 구분

| 범위 | 통과 | 실패 | 미실행 | N/A | 합계 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 성공 기준 | 28 | 6 | 46 | 0 | 80 |
| 조건부 복구 기준 | 7 | 0 | 0 | 17 | 24 |
| 전체 기준 | **35** | **6** | **46** | **17** | **104** |

r4 성공 17/4/19/0, 복구 3/0/0/9. r6 성공 11/2/27/0, 복구 4/0/0/8이다. N/A 17은 모두 “복구가 필요한 실패가 실제로 발생하지 않음”에 대한 조건부 복구 제외다. 미실행 46을 통과나 제품 실패로 바꾸지 않았다. 24세션의 기준 단위는 104이며 반복 페르소나의 재관측 단위도 포함한다.

## 대표 Peekly UX 항목과 실패 원인

### 제품 UX — P3 관계 의미 설명, 기존 항목 보존

`696dbe3`의 `UX-03-RELATION-MEANING` 독립 리뷰는 “나를 맞팔 안 한 사람” 설명에서 과거 맞팔이었던 계정의 포함 의미를 설명하지 않는다는 문구 개선 항목을 기록했다. r6 016 obs-9에도 `내가 팔로우하는데 나를 팔로우하지 않아요`라는 짧은 설명이 보인다. 계산 오류라고 주장하지 않는다.

다만 현재 v3 `persona-prd-diff-v3.json`의 `PRD-RESULT-RECIPROCITY` 발췌는 현재 관계의 집합 정의다. 과거 inclusion 문구를 필수 표시해야 한다는 요구를 이 발췌만으로 다시 확정할 수 없다. 따라서 **기존 제품 UX 리뷰 항목/개선 제안**으로 보존하며 새 current-PRD 기능 실패로 더하지 않는다. 기존 보고서가 “현재 PRD 위반으로 확정”이라고 쓴 범위는 이번 감사의 직접 확인 범위를 넘는다.

증거:

- 역사적 원본: `696dbe3:docs/validation/peekly-ux-findings-20261113/evidence-index-32.json`, `manual_reviewed_findings[UX-03-RELATION-MEANING]`, persona 020 obs-2 / `browser-00019.png`, PNG SHA-256 `af7e9524110ed26fceb8e6deff6023fe2595614fd6542e3ec6feef9939abcdd0`.
- 현재 큐에 저장된 동일 문구: `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/sessions/S-ckpllpaipicenconelndnpji/evidence/S-ckpllpaipicenconelndnpji/1/agent-observation-9.json`.
- 현재 기준 발췌: `docs/validation/peekly-explicit-success-20261113/persona-prd-diff-v3.json`, persona 020.

역사적 P2 “가져온 결과가 화면 밖”과 “수동 가져오기 진입 발견성”은 이전 보고의 관측이다. 이전 `e638375` 보고는 소스 scroll 수정과 More 진입 관측을 기록한다. 이번에는 해당 제품 소스나 브라우저를 다시 시험하지 않았으므로 새 회귀나 새 통과로 표시하지 않는다.

### 실행기·판정 한계 — P2 진행/취소 실패 4건

대상: **r4 014·015·016, r6 016**, 모두 `PRD-IMPORT-PROGRESS`.

저장 관측은 51~104ms 안의 파일 처리 완료를 기록한다. r6 016 obs-9는 0ms 읽기 → 52ms 결과 완료이고, 취소 클릭이 실행됐다는 증거는 없다. r4 014는 분석 단계 자체를 관측했으므로 “모든 실행에서 분석 단계가 없다”는 일반화도 틀리다.

현재 `scale_browser_cdp.mjs` upload 경로는 내부에서 최대 1200ms 동안 50ms 간격으로 상태를 읽고 나서 반환한다. 그 호출이 반환될 때 이미 처리가 끝난 사례에서 모델의 다음 click으로 진행 중 취소를 검증할 수 없다. 관측한 빠른 완료와 관측하지 못한 중간 상태는 취소 기능 부재를 입증하지 않는다. **4개 failed 영수증은 보존하지만 제품 기능 결함으로 확정하지 않는다.**

증거:

- `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/sessions/S-ckpllpaipicenconelndnpji/evidence/S-ckpllpaipicenconelndnpji/1/agent-observation-9.json`
- `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/sessions/S-ckpllpaipicenconelndnpji/evidence/S-ckpllpaipicenconelndnpji/1/agent-observation-12.json`
- `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/sessions/S-ckpllpaipicenconelndnpji/evidence/S-ckpllpaipicenconelndnpji/1/browser-00107.png`
- 정적 원인 검토: `skills/remorsearch-ux-qa/drivers/web/scale_browser_cdp.mjs`의 upload polling 부분.

### 실행기·판정 오귀속 — P2 모달 뒤 버튼 클릭 1건

대상: **r4 019**, `PRD-RESULT-MUTUAL`.

obs-13은 “내가 맞팔 안 한 사람” 목록 모달이 열린 상태다. 그 관측의 “맞팔 중인 사람” control은 **`visible:false`**, 닫기는 **`visible:true`**다. obs-14는 맞팔 버튼을 요청한 뒤 단일 계정 상세를 표시한다. 영수증은 이 결과를 맞팔 목록 오류로 판정했다.

현재 실행기의 observation 경로는 `elementFromPoint`로 가림 여부를 검사하지만 click 경로는 bounding box/라벨만 확인하고 좌표 mouse event를 보낸다. click 경로에는 동일한 hit-test가 없다. `last_action_label`도 요청 인자의 라벨이어서 실제 클릭을 받은 DOM 요소의 증명은 아니다. 따라서 **실행기의 가려진 대상 클릭 허용 및 판정의 대상 오귀속**으로 기록한다. 제품의 맞팔 수치/목록 계산 결함은 이 기록으로 확인되지 않는다.

증거:

- 클릭 전: `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/sessions/S-efceebljpmeelhejldcenakm/evidence/S-efceebljpmeelhejldcenakm/1/agent-observation-13.json`
- 클릭 후: `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/sessions/S-efceebljpmeelhejldcenakm/evidence/S-efceebljpmeelhejldcenakm/1/agent-observation-14.json`
- PNG: `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/sessions/S-efceebljpmeelhejldcenakm/evidence/S-efceebljpmeelhejldcenakm/1/browser-00126.png`
- 정적 원인 검토: `skills/remorsearch-ux-qa/drivers/web/scale_browser_cdp.mjs`, observe의 visible 검사와 click의 coordinate dispatch 비교.

### 판정기 오판 — P2 비교 화면 선행조건 누락 1건

대상: **r6 023**, `PRD-IDENTITY-LIMIT`.

obs-13에서 실제 요청한 control은 “자세히 보기”다. obs-14는 첫 기록의 요약으로 “다음에 새로 확인하면 달라진 관계를 비교해요”와 아직 열지 않은 “변화 기록 보기”를 표시한다. 업로드 ledger에는 empty-previous, missing-followers, missing-following, sample-current가 있고, 유효한 두 시점 비교가 열렸다는 증거가 없다.

기준은 안정적인 ID가 없는 **백업 비교**의 설명이다. 이 화면에서 정확한 문장 “아이디 변경이나 계정 삭제 때문일 수도 있어요”가 없다는 사실만으로 그 기준을 실패시킬 수 없다. **잘못된 화면/선행조건의 실패 판정**으로 분류하며 제품 고지 누락으로 확정하지 않는다.

증거:

- `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/sessions/S-pcmnpelhjaeccidlnociacoh/evidence/S-pcmnpelhjaeccidlnociacoh/1/agent-observation-13.json`
- `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/sessions/S-pcmnpelhjaeccidlnociacoh/evidence/S-pcmnpelhjaeccidlnociacoh/1/agent-observation-14.json`
- `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/sessions/S-pcmnpelhjaeccidlnociacoh/evidence/S-pcmnpelhjaeccidlnociacoh/1/browser-00143.png`
- `persona-prd-diff-v3.json` persona 023의 현재 PRD 발췌 및 `criteria-matrix.md`의 PRD-IDENTITY-LIMIT.

### 실패 수와 결함 수의 관계

저장된 failed 기준 6개 = 진행/취소 관찰 한계 4 + 가려진 클릭/대상 오귀속 1 + 비교 화면 선행조건 오류 1이다. 이 보고는 원래 세션 1/6/17을 **수정 없이 기록**하고 원인 검토를 따로 제공한다. 새 판정 overlay나 제품 결함 6개를 만들어 내지 않는다. 이 검토로 제품 통과나 준비 완료를 선언하지도 않는다.

## 실행기 이력과 host_protocol

- 완료 24건의 job problem / result problem / current_issue에 `host_protocol`은 0건이다.
- 과거 stage-25 overlay의 완료 23건 중 host_protocol 22건과 혼합하지 않는다.
- `5651c8e`의 storage access 처리와 `8e9e065`의 uncertain slot 반환은 이미 존재하는 커밋이다. 이번에는 코드를 바꾸거나 회귀를 재실행하지 않았다.
- r4/r6 plan에 기록된 10개 엔진 manifest 항목은 동일하다. 제품 build SHA도 둘 다 `d5755c8912660cf80c0c9f48d18cc8952a3e7b46fe04e82e673f1eaa96b10beb`다.
- 고정 manifest 일치와 host_protocol 0은 미실행 기준, 판정 오귀속, 실제 사용자 효과 검증을 대신하지 않는다.

## 완료 세션 장부

아래 기준 숫자는 **통과 / 실패 / 미실행 / N/A**이며 성공·복구를 포함한다. 같은 persona 번호가 다른 큐에 반복되는 행은 별개 실행 세션이다.

| 큐 | persona 번호 | job ID | 원본 세션 판정 | 기준 숫자 |
| --- | --- | --- | --- | --- |
| r4 | 014 | `S-cdfkaillgggnoifejjmahlnd` | failed | 1 / 1 / 1 / 1 |
| r4 | 015 | `S-kannanoaknpgcdfcpnjipcpp` | failed | 1 / 1 / 1 / 1 |
| r4 | 016 | `S-mejjecmbmlhcmokgfkhfmlki` | failed | 2 / 1 / 1 / 0 |
| r4 | 017 | `S-llicafnbijihpafhdnkgabki` | inconclusive | 4 / 0 / 1 / 0 |
| r4 | 018 | `S-gmjclhccfllepkecklhejcjk` | passed | 4 / 0 / 0 / 1 |
| r4 | 019 | `S-efceebljpmeelhejldcenakm` | failed | 2 / 1 / 1 / 1 |
| r4 | 020 | `S-igkhcbhpllgaaeefcnghhbdm` | inconclusive | 1 / 0 / 3 / 1 |
| r4 | 023 | `S-dnpghpjkkefmnpbbfahadiia` | inconclusive | 0 / 0 / 3 / 1 |
| r4 | 026 | `S-hbccokhbajdlhklgphonlfjo` | inconclusive | 1 / 0 / 2 / 1 |
| r4 | 027 | `S-bmomdjabkgmnmopbhjeiaecm` | inconclusive | 2 / 0 / 2 / 0 |
| r4 | 029 | `S-gobjinmilfaceenedbhopbnc` | inconclusive | 1 / 0 / 2 / 1 |
| r4 | 030 | `S-aamdholooghglmdiceajhfda` | inconclusive | 1 / 0 / 2 / 1 |
| r6 | 016 | `S-ckpllpaipicenconelndnpji` | failed | 1 / 1 / 1 / 1 |
| r6 | 017 | `S-fejkgbjagdokoghgelfmbcaj` | inconclusive | 1 / 0 / 3 / 1 |
| r6 | 018 | `S-mdmgdeapcgabkflegfcojikl` | inconclusive | 3 / 0 / 1 / 1 |
| r6 | 019 | `S-ikonfnebadpmafejfdbhlbfi` | inconclusive | 2 / 0 / 3 / 0 |
| r6 | 020 | `S-njlobmghmcclimglglabhnif` | inconclusive | 0 / 0 / 4 / 1 |
| r6 | 021 | `S-bhggnhhmcfoefpkldhlgmnmo` | inconclusive | 1 / 0 / 3 / 0 |
| r6 | 023 | `S-pcmnpelhjaeccidlnociacoh` | failed | 0 / 1 / 2 / 1 |
| r6 | 025 | `S-lbijbjanebieoogdafhnojoj` | inconclusive | 1 / 0 / 2 / 1 |
| r6 | 026 | `S-lahjbaojphfmlebjabngdodi` | inconclusive | 1 / 0 / 2 / 1 |
| r6 | 029 | `S-dlfbcbfdnididdofcbnkiiie` | inconclusive | 2 / 0 / 2 / 0 |
| r6 | 030 | `S-dgoedmkboghanafhpfnjhjao` | inconclusive | 1 / 0 / 2 / 1 |
| r6 | 031 | `S-ckljgonbkoljgjojfnhffoae` | inconclusive | 2 / 0 / 2 / 0 |

각 행의 result SHA-256, requirement별 criterion 상태, evidence root는 `final-session-ledger-20261114.json`에 기록했다.

## 검증 방법과 원본 지문

1. SQLite `mode=ro` 및 `PRAGMA query_only=ON`으로 상태를 읽었다.
2. queue / report / stage-summary의 complete·uncertain·queued 수가 일치한다.
3. plan / report / DB의 job 집합과 persona binding이 일치한다.
4. 완료 24건의 result SHA-256, receipt outcome과 criterion 레코드를 대조했다.
5. 완료 영수증에 포함된 증거 참조 **822건**의 파일 바이트 SHA-256이 모두 일치했다.
6. 아래 입력 파일과 완료 영수증을 읽기만 했다. raw 증거는 이 보고서에 복사하지 않았다.
7. JSON 파싱·합계·문서/요약 일치와 `git diff --check`로 보고서 변경만 확인했다. 과거 테스트 숫자를 이번 실행 실적으로 표기하지 않는다.

| 입력 파일 | SHA-256 |
| --- | --- |
| `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/queue.sqlite` | `dd2a9200ae10310d327d993fad88aeba0fe4688e4f24062ee95f6722d7774455` |
| `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/report.json` | `677ce09d7daa7d6b83b3e0000d88235995c6296ae1bc79f07cd91b3d6ac96705` |
| `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/stage-summary.json` | `5a4036182be128b0fd85fac7a7a1ceb24bed2d772c9f826f0723e87fdbcee41f` |
| `.ux-loop/peekly-host-protocol-followup16-r4-20261114/stage-33/plan.json` | `861c5fdce87a7a4c2d1fbc3abfb9e3028bf30660db3ab0c88edd63587db02ab9` |
| `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/queue.sqlite` | `f84f2fb244e020113f6d936065315b7a0f042b77f0423e8ca87e5e4f3850ab6d` |
| `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/report.json` | `64fac8d674b9b65a7e223be089559994760283325a09a5af67a7656a75af4c9e` |
| `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/stage-summary.json` | `8d3b1f3eadf738454ec0db9a46526bc3ce4c24c7e23c6e327608a8dad92b0313` |
| `.ux-loop/peekly-host-protocol-followup16-r6-20261114/stage-33/plan.json` | `5f20b3a36bea699f1a0a9a1c9cfe42dda480b2f4069bddbc8b8c9402f0fa78bf` |

검증된 SQLite WAL 파일은 둘 다 0바이트다. 출판 직전 10개 입력 파일의 지문, 완료 24건의 DB 결과 지문, 문서 일관성을 다시 확인했고 모두 일치했다. 변경 범위는 이 폴더의 보고서 4개뿐이다. 원격 확인 결과는 최종 커밋 SHA로 보고하며, 자신의 커밋 SHA를 문서 안에 적기 위한 추가 커밋은 만들지 않는다.

## 한계와 종료 조건

새 persona 실행·모델 호출·브라우저 호출은 0회다. 현재 제품 결함 수정이나 실행기 개선은 수행하지 않았다. 불확실 전송은 미평가로 보존하고 다시 보내지 않았다. 원본 증거·persona·queue·엔진 파일은 변경하지 않았다.

최종 산출물은 완료 24세션의 정직한 집계, 고유 15명/중복 9명의 정정, baseline 원문 대조, 실패 원인 구분 및 보고서 출판이다. 실제 Instagram 계정, iOS 실기기, 실제 사용자 조사, 접근성 인증 또는 제품 출시 준비 완료는 이 자료로 확인되지 않는다.
