# 미실행 46개 기준 원인 분석 — 2026-11-14

기준 커밋은 `ee4b14571930af428d5a52e0e133deebedba485d`다. r4·r6에서 `status=complete`인 세션의 최종 receipt 중 `status=not_run`만 추출하고, 같은 plan job의 `requirement_ids[index]`와 연결했다. **r4 19개 + r6 27개 = 46개**, 모두 성공 기준이다. 기존 상태를 수정하거나 재판정하지 않았다.

## 집계 단위와 중복

46개는 **완료 실행 세션의 기준 단위**다. 24세션은 고유15명이며 016·017·018·019·020·023·026·029·030이 두 큐에서 반복된다. 불확실5건·대기1건과 r5의031 재관측은 이 분모에 포함하지 않았다.

## 중복 없는 주원인 분류

각 기준에 하나의 주원인만 부여했다. 합계는46이다.

| 주원인 | 기준 수 | 기계 분류 코드 |
| --- | ---: | --- |
| 결정적 저장 실패 주입 하네스 없음 | **4** | `runner_storage_fault_unavailable` |
| 필수 과제·선행조건·결과 화면 미도달 | **27** | `task_flow_incomplete` |
| NBSP 공백 때문에 누락 목록 거부 문구를 놓침 | **3** | `verdict_whitespace_false_not_run` |
| 상세 로딩 후 결과 관측 미완료 | **1** | `async_detail_not_observed` |
| 빈 이전 기록과 현재 fixture의 계정 불일치 | **2** | `fixture_pair_account_mismatch` |
| 9행 이상 검색 선행 fixture/목록 미준비 | **4** | `fixture_search_precondition_not_prepared` |
| 11개 보관 시험 fixture가 실행 도구에 등록되지 않음 | **5** | `fixture_retention_not_registered` |

상위 묶음으로는 과제 설계/관측 미완료28, 실행기 저장 실패 주입 능력 부재4, fixture 등록·선택·계정 문제11, 판정기 NBSP 오분류3이다. **실제로 하지 않은 과제와 실제로 했지만 판정기가 놓친 과제를 구분했다.**

### 직접 확인된 원인

- **저장 실패 주입4건:** r4 014·015·016 및 r6 016의 영수증은 허용 도구에 one-shot Storage.setItem 실패를 주입할 하네스가 없다고 명시한다. 사용하지 못한 하네스가 제품 실패를 뜻하지 않는다.
- **보관 fixture 미등록5건:** r4 029·030, r6 029·030·031의 첫 관측을 각각 확인했다. 모두 available_fixtures531개 중 `peekly-retention-snapshot-XX.zip`은0개다. 반면 `.ux-loop/peekly-retention-fixtures-v4-extension-20261114/fixture-manifest.json`에는01–11이 존재한다. 파일 생성만 하고 실제 실행 목록에 연결하지 않은 경로 차이다.
- **검색 선행조건4건:** r4 026·027, r6 025·026은 모두5행 목록만 관측했다. 과제는9행 이상을 요구하지만 그 상태를 준비할 구체적 fixture·카테고리를 지목하지 않는다. 이는 검색 기능 실패가 아니라 준비/선택 미완료다.
- **빈 이전 기록 쌍의 계정 불일치2건:** r4 023 obs13, r6 023 obs11에서 sample-current 업로드가 현재 저장된 계정과 다른 파일이라 거부됐다. empty-previous와 같은 계정의 current 쌍이 필요하다.
- **NBSP 판정 오류3건:** r4 023 obs6·7, r6 021 obs11·12, r6 023 obs6·7에서 두 누락 목록 fixture 각각의 거부 문구가 실제로 기록됐다. 여섯 관측 모두 raw substring 비교는false, NBSP를 보통 공백으로 정규화하면true다. 현재 `peekly_criteria.py`의 PRD-IMPORT-MISSING 분기는 정규화 없이 문자열을 찾는다.
- **과제/관측 미완료28건:** 필수 upload, import 후 목록 재열기, 두 기록 비교·이름 확인, 삭제 확인, Pro 경계 확인 등의 필수 경로가 수행되지 않았다. 그중1건은 상세 화면 로딩까지만 기록돼 별도 분류했다. 정확한 원문 이유는 아래 표와 JSON에 보존했다.

### 턴 상한은 별도 보조 요인

r4 plan의 `limits.turns`는24, r6는16이다. r6의 많은 완료 영수증은14~15개 행동 관측으로 끝나며,031 영수증은 턴 예산 안에서11개 중2개만 가져왔다고 명시한다. 그러나 **27개 과제 미도달 전부가 실제 턴 소진 때문이라고 입증된 것은 아니다.** 파일 미등록이나 잘못된 계정 쌍은 턴 수만 늘려도 해결되지 않는다.

JSON의 각 관련 행에는 fixed_turn_budget을 추정 보조 요인으로 표시했다. 이는 중복 합산하지 않는다.

## 요구사항별 미실행 수

| 요구사항 | 미실행 |
| --- | ---: |
| `PRD-IMPORT-SAVE-FAIL` | 4 |
| `PRD-RESULT-SNAPSHOT` | 7 |
| `PRD-RESULT-REVERSE` | 3 |
| `PRD-RESULT-MUTUAL` | 4 |
| `PRD-IMPORT-MISSING` | 3 |
| `PRD-IDENTITY-LIMIT` | 2 |
| `PRD-IMPORT-SNAPSHOT-UNKNOWN` | 3 |
| `PRD-RESULT-SEARCH` | 4 |
| `PRD-PRIVACY-DELETE` | 4 |
| `PRD-SNAPSHOT-RETENTION` | 5 |
| `PRD-PAYWALL-BOUNDARY` | 5 |
| `PRD-RESULT-RECIPROCITY` | 2 |

## 우선 수정과 확인 기준

1. **fixture와 실행 allowlist 연결:** 보관용11개를 실제 실행 manifest에 등록하고 시작 전 이름·해시·시점 차이·같은 계정을 확인한다. 검색은 실제9+행이 생기는 지정 fixture와 카테고리로 준비한다. empty/current 비교쌍은 계정을 일치시킨다.
2. **기준별 체크리스트:** sample 관측과 imported-data 검증을 분리하고, import 직후 세 관계 목록 재열기·모달 닫기·다음 기준 이동을 명시한다. 비교는 previous→current 후 비교 목록/이름을 열어야 완료다. 삭제는 진입→확인→동일 격리 프로필 상태 제거 확인까지다.
3. **과제 복잡도별 예산과 진행 기록:** 단순히16turns를 모두에게 적용하지 않는다. 11회 import 및 모달/화면 전환의 최소 단계 수에 맞게 예산을 정하고 미완료 단계가 남은 상태의 조기 종료를 줄인다. 로딩 직후에는 bounded wait/observe를 필수로 둔다.
4. **저장 실패 시험:** 소유된 합성 프로필 전용의 명시적1회 실패 주입과 이전 상태/재시도 성공 증거를 제공한다. 실제 브라우저 관측과 별도 하네스 검증을 혼동하지 않는다.
5. **판정기 수정:** NBSP를 정규화하되 두 missing-list fixture의 결과를 각각 귀속시켜 둘 다 거부됐는지 확인한다. 한 fixture의 메시지를 다른 fixture의 성공으로 가져오지 않는다.

### 46개 밖의 실행기 결함도 별도 검증

진행/취소51~104ms 완료4건, 모달 뒤 클릭1건, 비교 화면 오귀속1건은 기존 **failed6개**에 속하며46개 미실행 분모에 포함되지 않는다. 취소 중 행동을 실제 수행할 수 있는 fixture/비동기 관측 경로, 클릭 좌표의 hit-test와 현재 모달 상태 확인, 기준의 실제 대상 화면 확인을 고쳐야 하지만 이를 “미실행46개 감소” 숫자로 더해서는 안 된다.

## 권장2명 스모크

**016 + 029**를 권한다. r6 원문에서 성공 기준 미실행은016의1개와029의2개, 합계3개다.

- 016: 크기 경계 통과를 유지하면서 진행/중단과 저장 실패·재시도를 실제로 관측한다. 진행/중단 실패 해소는 미실행 감소와 별도 확인한다.
- 029: 샘플 export 경계 확인 후 실제로11개의 보관용 fixture를 import하고 기록 보관과 무료/Pro 경계 화면을 끝까지 확인한다.

동일 기준의 미실행이3개보다 줄어야 하며, 기준을 약화하거나 미실행을 N/A로 옮겨 감소시켜서는 안 된다. fixture·판정기 선행 검증이 통과했는데 스모크가 여전히 경로에 도달하지 못하면32명 확대 전에 원인을 해결한다.

## 기준별 장부

보고서 원문 reason을 그대로 인용했다. 모든 행의 원본 report 경로·job ID·criterion selector·세부 관측 경로는 [not-run-baseline.json](not-run-baseline.json)에 있다.

| ID | 큐/persona | 요구사항 | 주원인 | 저장된 원문 이유 |
| --- | --- | --- | --- | --- |
| NR-01 | r4/014 | `PRD-IMPORT-SAVE-FAIL` | 저장 실패 하네스 없음 | 저장 실패를 주입할 도구가 allowlist에 없고 격리 테스트 하네스에 접근할 수 없어 one-shot Storage.setItem 실패와 '다시 저장' 재시도 흐름을 실행하지 못했다. |
| NR-02 | r4/015 | `PRD-IMPORT-SAVE-FAIL` | 저장 실패 하네스 없음 | 결정적 one-shot Storage.setItem 실패 주입은 격리 테스트 하네스에서만 가능하며, 현재 허용 도구(observe/click/type/upload/scroll/wait)에는 저장 실패 주입 경로가 없어 브라우저 검증으로 실행할 수 없었다. |
| NR-03 | r4/016 | `PRD-IMPORT-SAVE-FAIL` | 저장 실패 하네스 없음 | 제품 코드에 Storage.setItem 주입 경로가 없고 이 브라우저 도구 목록에는 격리 테스트 하네스가 없어 결정적 1회 저장 실패와 다시 저장 흐름을 실제 실행할 수 없었음. 브라우저에서 검증된 것으로 보고하지 않음. |
| NR-04 | r4/017 | `PRD-RESULT-SNAPSHOT` | 과제 미도달 | The two required distinct snapshots were not both imported. |
| NR-05 | r4/019 | `PRD-RESULT-SNAPSHOT` | 과제 미도달 | The two required distinct snapshots were not both imported. |
| NR-06 | r4/020 | `PRD-RESULT-REVERSE` | 과제 미도달 | 가져오기 후 '내가 맞팔 안 한 사람' 목록을 다시 열지 않아 가져온 데이터의 목록 일치를 확인하지 못했다. |
| NR-07 | r4/020 | `PRD-RESULT-MUTUAL` | 과제 미도달 | 가져오기 후 '맞팔 중인 사람' 목록을 다시 열지 않아 가져온 데이터의 목록 일치를 확인하지 못했다. |
| NR-08 | r4/020 | `PRD-RESULT-SNAPSHOT` | 과제 미도달 | Two snapshots were imported, but the latest comparison and its names were not opened. |
| NR-09 | r4/023 | `PRD-IMPORT-MISSING` | NBSP 판정 오류 | Both missing-list uploads were observed but their result state was not captured. |
| NR-10 | r4/023 | `PRD-IDENTITY-LIMIT` | 로딩 결과 미관측 | Relationship detail was opened but remained on a loading message, so the username-change/account-deletion explanatory copy was never observed. |
| NR-11 | r4/023 | `PRD-IMPORT-SNAPSHOT-UNKNOWN` | fixture 계정 불일치 | Deterministic check not run because its precondition was not observed. |
| NR-12 | r4/026 | `PRD-RESULT-SEARCH` | 검색 fixture/목록 미준비 | obs-20 showed a relationship list with only 5 rows ('5명') and no search input; no 9+ row list or exact-handle filtering was observed. |
| NR-13 | r4/026 | `PRD-PRIVACY-DELETE` | 과제 미도달 | obs-22 showed 약관과 개인정보 still visible:false; no deletion dialog or confirmation was opened, and storage keys were not verified absent afterward. |
| NR-14 | r4/027 | `PRD-RESULT-SEARCH` | 검색 fixture/목록 미준비 | 관계 목록이 5행뿐이어서 9행 이상 선행조건이 충족되지 않았고, 검색 입력과 핸들 필터링을 실제로 수행하지 못했다. |
| NR-15 | r4/027 | `PRD-PRIVACY-DELETE` | 과제 미도달 | 더보기에 '기록 모두 지우기' 항목은 보였으나 삭제 확인 단계와 저장소 키 제거를 실행·검증하지 못했다. |
| NR-16 | r4/029 | `PRD-SNAPSHOT-RETENTION` | 보관 fixture 미등록 | Retention requires 11 distinct valid snapshot imports; observed 0. |
| NR-17 | r4/029 | `PRD-PAYWALL-BOUNDARY` | 과제 미도달 | The latest free comparison, history controls and Pro feature explanation were not all observed. |
| NR-18 | r4/030 | `PRD-SNAPSHOT-RETENTION` | 보관 fixture 미등록 | Retention requires 11 distinct valid snapshot imports; observed 0. |
| NR-19 | r4/030 | `PRD-PAYWALL-BOUNDARY` | 과제 미도달 | The latest free comparison, history controls and Pro feature explanation were not all observed. |
| NR-20 | r6/016 | `PRD-IMPORT-SAVE-FAIL` | 저장 실패 하네스 없음 | 결정적 one-shot Storage.setItem 실패를 주입할 격리 테스트 하네스가 제공되지 않아 저장 실패·다시 저장 흐름을 실행하지 못했다. |
| NR-21 | r6/017 | `PRD-RESULT-RECIPROCITY` | 과제 미도달 | Imported state showed 5명, but the category list was not reopened after import; the earlier sample list cannot prove fixture match. |
| NR-22 | r6/017 | `PRD-RESULT-MUTUAL` | 과제 미도달 | 맞팔 중인 사람 shows 5명 but was never opened; no member list was inspected. |
| NR-23 | r6/017 | `PRD-RESULT-SNAPSHOT` | 과제 미도달 | Two snapshots were imported, but the latest comparison and its names were not opened. |
| NR-24 | r6/018 | `PRD-RESULT-SNAPSHOT` | 과제 미도달 | The two required distinct snapshots were not both imported. |
| NR-25 | r6/019 | `PRD-RESULT-REVERSE` | 과제 미도달 | '내가 맞팔 안 한 사람 2명' 라벨과 숫자는 보였으나, 해당 카테고리를 직접 열어 목록을 확인하지 않았다. |
| NR-26 | r6/019 | `PRD-RESULT-MUTUAL` | 과제 미도달 | '맞팔 중인 사람 5명' 라벨과 숫자는 보였으나, 해당 카테고리를 직접 열어 목록을 확인하지 않았다. |
| NR-27 | r6/019 | `PRD-RESULT-SNAPSHOT` | 과제 미도달 | Two snapshots were imported, but the latest comparison and its names were not opened. |
| NR-28 | r6/020 | `PRD-RESULT-RECIPROCITY` | 과제 미도달 | 샘플 카드의 5명과 목록은 확인했으나 유효한 합성 가져오기 선행조건이 완료되지 않아 가져온 fixture 데이터와의 일치 여부를 판정하지 못했다. |
| NR-29 | r6/020 | `PRD-RESULT-REVERSE` | 과제 미도달 | 샘플 카드의 2명과 목록은 확인했으나 유효한 합성 가져오기 선행조건이 완료되지 않아 가져온 fixture 데이터와의 일치 여부를 판정하지 못했다. |
| NR-30 | r6/020 | `PRD-RESULT-MUTUAL` | 과제 미도달 | 샘플 카드의 5명과 목록은 확인했으나 유효한 합성 가져오기 선행조건이 완료되지 않아 가져온 fixture 데이터와의 일치 여부를 판정하지 못했다. |
| NR-31 | r6/020 | `PRD-RESULT-SNAPSHOT` | 과제 미도달 | The two required distinct snapshots were not both imported. |
| NR-32 | r6/021 | `PRD-IMPORT-MISSING` | NBSP 판정 오류 | Both missing-list uploads were observed but their result state was not captured. |
| NR-33 | r6/021 | `PRD-IDENTITY-LIMIT` | 과제 미도달 | 아이디 변경/계정 삭제 가능성 설명 화면을 열거나 관찰하지 않았다. |
| NR-34 | r6/021 | `PRD-IMPORT-SNAPSHOT-UNKNOWN` | 과제 미도달 | peekly-empty-previous.zip만 업로드되어 0명 결과만 확인했고 peekly-sample-current.zip 비교 흐름은 실행되지 않았다. |
| NR-35 | r6/023 | `PRD-IMPORT-MISSING` | NBSP 판정 오류 | Both missing-list uploads were observed but their result state was not captured. |
| NR-36 | r6/023 | `PRD-IMPORT-SNAPSHOT-UNKNOWN` | fixture 계정 불일치 | Deterministic check not run because its precondition was not observed. |
| NR-37 | r6/025 | `PRD-RESULT-SEARCH` | 검색 fixture/목록 미준비 | 관계 목록이 5행만 노출되어 9행 선행조건과 '아이디나 이름으로 찾기' input을 확인하지 못했다. |
| NR-38 | r6/025 | `PRD-PRIVACY-DELETE` | 과제 미도달 | '데이터 삭제' 탭 노출까지만 확인했고, 삭제 확인 단계 실행과 localStorage 키 제거 검증은 완료하지 못했다. |
| NR-39 | r6/026 | `PRD-RESULT-SEARCH` | 검색 fixture/목록 미준비 | 5행 목록만 열려 9행 이상 선행조건과 검색 입력·합성 아이디 필터링을 검증하지 못했다. |
| NR-40 | r6/026 | `PRD-PRIVACY-DELETE` | 과제 미도달 | 데이터 삭제 진입·확인·격리 프로필 저장 키 제거 확인을 수행하지 않았다. |
| NR-41 | r6/029 | `PRD-SNAPSHOT-RETENTION` | 보관 fixture 미등록 | Retention requires 11 distinct valid snapshot imports; observed 0. |
| NR-42 | r6/029 | `PRD-PAYWALL-BOUNDARY` | 과제 미도달 | The paywall boundary requires two valid snapshots for the same synthetic account. |
| NR-43 | r6/030 | `PRD-SNAPSHOT-RETENTION` | 보관 fixture 미등록 | Retention requires 11 distinct valid snapshot imports; observed 0. |
| NR-44 | r6/030 | `PRD-PAYWALL-BOUNDARY` | 과제 미도달 | The latest free comparison, history controls and Pro feature explanation were not all observed. |
| NR-45 | r6/031 | `PRD-SNAPSHOT-RETENTION` | 보관 fixture 미등록 | Retention requires 11 distinct valid snapshot imports; observed 0. |
| NR-46 | r6/031 | `PRD-PAYWALL-BOUNDARY` | 과제 미도달 | The latest free comparison, history controls and Pro feature explanation were not all observed. |

## 범위

이 분석은 기존 JSON·plan·저장 관측·기준 코드를 읽고 원인을 분류한 것이다. 모델/브라우저 호출, 새 여정, 코드 변경, 회귀 테스트 또는 커밋/푸시는 이 하위 작업에서 수행하지 않았다. 파일 작성은 이 폴더의 `not-run-baseline.json`과 `not-run-baseline.md` 두 개로 제한했다.
