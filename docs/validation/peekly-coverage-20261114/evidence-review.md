# 신규 코호트의 저장 증거 검토

최종 32명 코호트의 공식 영수증은 동결된 실행기 `43e3b14`가 만든 값을 보존한다. 이 문서는 **실제 제품 실패, 실행 미완료, 판정기 오판을 분리하는 독립 검토**다. 아래 사실을 근거로 원본 큐나 영수증을 바꾸지 않았다. 코호트 전체 집계와 파일 무결성 감사는 종료 후 별도 산출한다.

공통 stage: `.ux-loop/peekly-coverage32-20261114/stage-32`.

## P2 제품 결함 — 저장 실패 후 직접 재시도 부재

실제 one-shot 저장 오류가 발생하고 이전 기록은 보존됐으나 **다시 저장** 버튼이 없고 **다른 파일 고르기**만 나타났다. 고정 PRD `51110f4` §3은 쓰기 실패 안내와 다시 저장 버튼을 요구한다. 제품 코드의 가져오기 저장 실패 경로는 오류를 표시하지만 그 재시도 조작을 제공하지 않는다.

| 페르소나 | job | 관측 | upload attempt | 기존 저장 보존 |
| --- | --- | --- | --- | --- |
|013|`S-pggllnfpmomgbiaefciinnlo`|`obs-15`|`upload-243`|true|
|014|`S-oheandojgflaijgkoigockdl`|`obs-13`|`upload-229`|true|

정확한 관측 경로:

- `stage-32/sessions/S-pggllnfpmomgbiaefciinnlo/evidence/S-pggllnfpmomgbiaefciinnlo/1/agent-observation-15.json`.
- `stage-32/sessions/S-oheandojgflaijgkoigockdl/evidence/S-oheandojgflaijgkoigockdl/1/agent-observation-13.json`.

위 경로의 `stage-32`는 공통 run root `.ux-loop/peekly-coverage32-20261114` 아래다. 스모크 016에서도 같은 결함을 관측했다. 실패 횟수는 동일 결함의 반복 관측이며 서로 다른 제품 결함 수가 아니다.

013의 조건부 복구는 버튼 부재로 실제 재시도하지 못해 `not_run`이고, 014는 별도의 예기치 않은 실행 장애가 없었다며 N/A로 남겼다. 이 원본 판정을 보존한다. 성공 기준의 저장 실패 판정과 조건부 복구의 실행 여부를 서로 대체하지 않는다.

## P2 판정기 오판 — 011의 거절 결과를 미실행으로 처리

011, job `S-pdalpdmknheojnhkkichdfbm`은 18턴에 완료했다. HTML/JSON 결과 일치와 두 missing-list 거절은 통과했고, 아래 두 항목은 공식 영수증에서 `not_run`이다. 하지만 저장 관측에는 각각의 업로드와 거절 결과가 이미 있다.

| 기준 | 실제 증거 | 판정기가 놓친 이유 |
| --- | --- | --- |
|`PRD-IMPORT-HTML`|`obs-10/14`에서 지정 malformed HTML ZIP을 업로드했고, `[followers.html] 파일에서 팔로워·팔로잉 목록을 읽지 못해 불러오지 않았어요`라는 오류를 표시했다.|`읽지 못했어요` 계열 문구만 허용한 문자열 조건에 실제 `읽지 못해 불러오지 않았어요`가 맞지 않았다.|
|`PRD-IMPORT-ACCOUNT`|`obs-15`에서 지정 account-mismatch ZIP을 업로드했고, 현재 기록과 다른 계정이므로 같은 계정 파일을 고르라는 오류를 표시했다.|`여러 계정의 정보가 섞여 있어요` 또는 `파일 이름과 내용의 계정이 달라요`만 허용한 문자열 조건에 실제 현재 계정 불일치 안내가 맞지 않았다.|

두 오류 모두 해당 업로드 관측 자체에 기록되어 있으므로 과제 미도달이나 후속 관측 누락으로 분류하지 않는다. HTML `upload-162`, account mismatch `upload-192`의 before/after 저장 digest는 모두 `9af62a14fb957a6ac318b8583f89a4e07e13c0b2e9db946a6a9410d0fe99e61f`이며, `persistence_unchanged=true`다.

PRD §3은 잘못된 HTML을 **파일 이름이 있는 오류로 중단**하고, **이미 기록된 계정과 다른 계정 파일을 차단**할 것을 요구한다. 특정 한국어 문장이나 ZIP 외부 파일명 자체를 요구하지 않는다. 따라서 이 두 `not_run`은 제품의 차단 기능 미실행을 뜻하지 않는다.

증거 경로:

- `stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-10.json`.
- 같은 디렉터리의 `agent-observation-14.json`, `agent-observation-15.json`.

011은 기존 46행의 페르소나 집합에 포함되지 않는다. 이 두 건을 기존 46개 감소 성과에 추가하지 않는다. 원본 비교표에는 저장된 `not_run`을 유지한다. 별도의 증거 감사 비교표에서는 이 두 항목을 통과로 바로잡고 원본과의 차이를 명시한다.

## P1 검증 범위 오판 — 017의 샘플 목록을 import 후 검증으로 인정

고정된 RECIPROCITY·REVERSE·MUTUAL 기준은 정상 합성 fixture import 이후 그 데이터의 카드 수와 목록을 확인하도록 요구한다. 그러나 과제에는 sample mode를 허용하는 상충 문구가 있고, 판정기에 이 세 기준의 native 선행조건 검사가 없다. 이는 제품 결함이 아니라 과제·판정기의 범위 불일치다.

017의 완료 관측 18개 전체를 읽기 전용으로 대조했다.

| 관측 | 상태 | 세 관계 목록의 검증 여부 |
| --- | --- | --- |
|obs4·6·8|샘플, 업로드 이력 없음|5/2/5개 목록 행을 확인|
|obs13|previous 정상 import|실제 카드2/2/10, 목록 행0|
|obs16|current 정상 import|실제 카드5/2/5, 목록 행0|
|obs17|import 후 스크롤|관계 목록 없음|
|obs18|팔로워에서 빠진 사람 목록|departed6개이며 세 현재 관계 범주와 다름|

두 import의 fixture 해시와 카드 수는 v7 manifest 기대값에 맞는다. sample과 current의 숫자가 모두5/2/5라는 사실만으로 import 이후 목록 열기 단계를 대체할 수 없다. 따라서 원본 success0~2 PASS는 보존하되, 독립 동일 범위 검토에서는 **import 후 목록 미실행**으로 유보한다. success3 SNAPSHOT은 실제 pair와 departed 목록 증거가 있다. 원본 세션은 passed이고, 동일 범위를 적용한 별도 검토 세션은 inconclusive다.

기존46행 중 **NR-21(r6/017 RECIPROCITY), NR-22(r6/017 MUTUAL)**의2행·2고유 조합에는 감소 성과를 부여하지 않는다. 반면 SNAPSHOT의 **NR-04(r4/017), NR-23(r6/017)**은2행·1고유 조합으로 실제 실행 근거가 있다. REVERSE는 이 사람의 baseline46에 없어 감소 수에 직접 영향을 주지 않는다.

- job: `S-jmpokhjegennajnihcaemagh`.
- 원본 result SHA: `0ce48eb2ea993433f63c1951f50053aac12a7a11e0a4d953d434286dd2babd78`.
- 증거: `stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-{4,6,8,13,16,17,18}.json`.
- 세 RESULT ID에 해당하는 baseline 전체는9행·7고유 조합이며017·019·020에 분포한다. 다른 사람의 결과는 각자의 저장 관측으로 별도 검토한다.

현재 코호트가 끝날 때까지 원본 실행기는 동결한다. 종료 후 과제의 sample 대체 문구와 native 선행조건 누락을 최소 범위로 수정하고, 이 저장 관측을 반례로 회귀 검증한다. 수정 후 과제의 새로운 실제 수행은 이 저장 증거만으로 입증했다고 주장하지 않는다.

### 018·019·020의 개별 확인과 합계

018·020의 각18개 관측,019의23개 관측도 모두 필요한 필드로 대조했다.018·020은017과 같은 순서이며,018이 추가 인용한obs16도 목록 행은0인 카드 화면이다.019는 샘플 목록obs7/9/11, 실제previous/current importsobs16/19, departed목록obs22와 닫기obs23으로 끝난다. 마지막 행동 설명에 관계 카드를 다시 확인하겠다는 의도가 있지만 실제 추가 목록 열기는 없다.

| 페르소나 | 원본 PASS → 독립 검토 not_run | baseline 감소에서 제외할 행 | 가중 행 / 고유 조합 |
| --- | ---: | --- | ---: |
|017|3|NR-21, NR-22|2 / 2|
|018|3|해당 관계 기준 없음|0 / 0|
|019|3|NR-25, NR-26|2 / 2|
|020|3|NR-06, NR-07, NR-28, NR-29, NR-30|5 / 3|
|합계|**12**|**9개 기존 행**|**9 / 7**|

네 세션은 완료된 평가 대상이다. 전송 불확실과 혼동해 분모에서 빼지 않고, 같은 기준 범위의 별도 감사에서 **세션 passed4 → inconclusive4**로 표시한다. 기존46의 감소에서도 위9가중행·7고유 조합에 성과를 부여하지 않는다. 각 세션의 실제 SNAPSHOT 관측과 조건부 복구 판정은 유지한다.

- 018 job: `S-pmfcniapopnnebacajhibjbh`, result SHA `5b7abd2f6b8c2833dfc7a5d9850122a1acb296998371a82dfb73f1d17b135070`.
- 019 job: `S-jbeffobgjfbgkhkfmfepeohi`, result SHA `f2e5b232570cbcc7e384c5d6de66b799cc96931ba70f0dd4ec3e499d707443da`.
- 020 job: `S-efdkbjaecbikgofacjhaaena`, result SHA `759e018f1dcba530fd94ce68b056f046f559d1b893ad552fa849fb857a6b4882`.

최초 14건의 판정 차이(관계 범위 12건과 011의 잘못된 미실행 2건)는 [criterion-review.json](criterion-review.json)에 원본 result SHA, 기준 index, 근거 파일, 이전·검토 상태, baseline 대응을 저장했다.

## P1 fixture·판정기 오귀속 — 021의 known-empty를 unknown 과거 기록으로 취급

`peekly-empty-previous.zip`은 445bytes이며 manifest와 일치하는 SHA는 `8585fbfdf08af2287d7ca2ae4b51c883fc41b8b409e08aa5f7a49b881784e1ac`다. `personal_information.json`, `followers.json=[]`, `following.json=[]`를 포함한다. 고정 제품 parser는 두 빈 배열을 정상 목록으로 인식하며 두 파일 종류를 새 snapshot의 `includedFiles`에 기록한다. 이는 빈 것이 확인되는 정상 기록이다.

PRD가 제외하도록 요구하는 것은 목록이 실제로 비었는지 알 수 없는 과거 기록이다. 제품의 `src/storage/snapshotStore.ts`와 `src/types/instagram.ts`에서는 `includedFiles` 도입 이전의 저장 기록을 unknown으로 다룬다. 따라서 새 known-empty ZIP으로 legacy unknown 선행조건을 구성했다고 볼 수 없다.

021의 obs7은 empty import 후0/0의 첫 기록 안내이고, obs10은 current import 후7/10 및 정상 empty 기록 대비 departed0명이다. unknown 제외 안내가 없다는 이유로 제품 실패를 만들 근거가 없다.

더구나 이 기준의 native 실패가 처음 생긴 시점은 obs21이다. 그전에 obs15/18에서 **다른 정상 previous/current pair**를 가져왔고, obs21은 그 pair의 departed6명 목록이다. 누적 `all_text`의 `언팔`·`명`을 사용하던 판정기가 이 후속 문구를 앞선 unknown 시험의 실패로 잘못 귀속했다.

- job: `S-injjambjkacdigcmpjaogaap`, success index2.
- 원본 result SHA: `4783928f842e7028d56ea25587229eaae176a781a97cc189708b86760b15e0af`.
- 증거 디렉터리: `stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/`.
- 파일: `agent-observation-7.json`, `agent-observation-10.json`, `agent-observation-15.json`, `agent-observation-18.json`, `agent-observation-21.json`.

독립 판정은 **failed→not_run**이다. 실제 legacy unknown을 준비하지 못했으므로 PASS로도 바꾸지 않는다. baseline **NR-34**를 실행된 제품 실패라는 감소 성과에서 제외한다. 이15번째 판정 차이도 criterion-review.json에 추가했다.022·023·024의 같은 기준은 각각의 완료 증거를 확인해 따로 처리한다.

격리 수정에서는 현재 지원되지 않는 legacy 선행조건을 명시적으로 미실행 처리한다. known-empty를 대용으로 실행시키거나 후속 비교 문구로 실패를 생성하지 않는다. 실제 legacy seed 실행 능력을 검증했다는 주장은 하지 않는다.

## 022·023·024 UNKNOWN 개별 확인

각 완료 세션의 저장 관측과 등록 파일 해시를 별도로 확인했다. 모두 legacy unknown 선행조건이 없으며 정상 empty 또는 다른 정상 pair의 결과를 UNKNOWN 실패로 오귀속했다. success index2만 failed→not_run으로 검토하며 다른 기준은 유지한다.

| 페르소나 | job | 핵심 관측 | baseline 제외 |
| --- | --- | --- | --- |
|022|`S-mnemkabchmofljkacpjkooai`|obs6/9/18/21/44/45/46; obs44까지not_run, 다른 pair의 관계 상세obs45에서실패생성|없음|
|023|`S-lpcmlkbehhmjifejlcbplfll`|obs7/10/13/19/22/24; 정상empty대비0명목록obs13, 다른pair의departed6목록obs24에서실패|NR-11, NR-36|
|024|`S-bhipnijdghjoompcjcokbceh`|obs8/11/13/16/30/33/35; 정상0명목록obs13, 정상기록2개obs16, 다른pair의목록obs35에서실패|없음|

021–024 합계4개 기준을 미실행으로 분리한다. baseline에서는3가중행·2고유조합이 감소 성과에서 제외된다. 실제 legacy 상태를 주입하는 fixture/harness는 이번 실행에 없었고, 이를 지원한다고 주장하지 않는다.

## P1 검색 판정기 오판 — 025의 다른 화면 placeholder 요구

고정 PRD110은 목록8명초과에서 검색 입력과 아이디 정렬을 요구하며 특정 placeholder 문구를 요구하지 않는다. 실제 ResultsTab에는 `input[type=search]`, label/placeholder `이름 또는 아이디 찾기`가 있다. 판정기는 MatrixTab의 `아이디나 이름으로 찾기`를 요구해 실제 입력이 없다고 잘못 실패시켰다.

025의 obs6은 검색 fixture를 가져온 실제12행 목록이며 입력은 visible=true, disabled=false다. 다음obs7에서 목록을 닫았다. 저장 관측15개 전체에서 typed_input_checks가 비어 있으므로 검색어 입력과 결과 축소까지 수행한 증거는 없다. 따라서 **failed→not_run**이며PASS가 아니다.

- job:`S-lienlcpnibobddnaaekmmami`, success index0, PRD-RESULT-SEARCH.
- result SHA:`65a77074cd29788022599df8d446d67c879313d0dcc9f03e9dd61e4ada4aa81a`.
- 증거:`stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-6.json`, 같은 디렉터리의`agent-observation-7.json`, 등록 캡처`browser-00060.png`.
- baseline:`NR-37`은 실제 검색 실행 감소 성과에서 제외한다.

026–028에는 실제 입력·필터링 기록이 있으므로025와 별도로 감사한다. 검색 입력을 찾는 판정 조건은 격리 작업 트리에서 수정 중이며, 이번 원본 영수증은 보존한다.
