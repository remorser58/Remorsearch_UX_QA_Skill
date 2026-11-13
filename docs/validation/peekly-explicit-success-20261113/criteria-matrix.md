# Peekly acceptance criteria — current PRD v3

정본: Peekly `rem/peekly-import-ux-20261113` commit `51110f4c569673faa8d242d5b85c4b47afb54cbb`, `docs/PRD.md` SHA-256 `a014a85b7523928f693cd4422793929631f033176715f31409412e95e1d7432b`. 이전 페르소나 라이브러리의 PRD SHA는 `5c18b75a9e4c5d31a1b8b45df60818a2391ea464d4010d976b94a0e908a6bb2d`로 달랐다. 기존 32개 persona ID와 행동 정체성은 보존하고 별도 v3 라이브러리에 새 revision으로 재도출한다. 상세 persona별 요구사항 ID와 구문 변경은 `persona-prd-diff-v3.json`을 정본으로 한다.

## 판정 계약

- 각 persona의 `requirement_ids` 순서대로 criteria index를 매긴다. 각 기준은 이 표의 화면·정확한 텍스트·수치·선행조건·행동·제한시간을 사용한다.
- 브라우저는 현재 DOM 텍스트, visible controls, file inputs, network policy, PNG를 매 행동마다 기록한다. 업로드는 fixture manifest hash 확인 및 `DOM.setFileInputFiles` 성공 후에만 ledger에 추가한다.
- 실행하지 않은 과제는 `not_run`이다. 실제 실행기/브라우저 자체가 시작·응답하지 못한 경우에만 `blocked`/`uncertain`으로 분리한다. 앱의 미실행·모델이 건너뛴 흐름을 판단 불가로 숨기지 않는다.
- 제품 결함은 관찰된 기준 불일치만 `failed`로 판정한다. PRD에 없는 기대 동작(예: 정렬 규칙을 임의로 바꾸기)은 기준에서 제외한다.
- Native iOS만 가능한 동작은 desktop run에서 N/A다. N/A를 pass로 합산하지 않는다.

## 기준표

| PRD ID | 현재 정본의 성공 기준 | 판정·증거 | 선행조건 / 행동 / 제한시간 |
|---|---|---|---|
| `PRD-START-SAMPLE` | 첫 화면에 `인스타그램으로 로그인`, `샘플로 먼저 둘러보기`; 파일 형식을 요구하지 않음 | visible text + sample CTA control + PNG | fresh isolated profile 첫 화면 관찰 / 8초 |
| `PRD-START-IMPORT` | More 첫 화면에서 `이미 받은 자료로 확인하기`를 통해 저장 자료 가져오기 흐름으로 바로 진입 | 클릭 전후 DOM route/text, file-selection screen, PNG; 이전 1/3 단계 문구를 요구하지 않음 | More 열기 → 해당 경로 선택 / 30초 |
| `PRD-START-SKIP` | 요청 단계 `이미 파일을 받았어요` 링크가 파일 선택 단계로 이동 | exact link + 클릭 후 `파일 고르기`와 `input[type=file]` | 요청 단계에서 링크 클릭 / 20초 |
| `PRD-IMPORT-FORMATS` | 공식 HTML·JSON 백업 모두 같은 관계 결과를 읽음 | HTML fixture와 JSON fixture를 별도 가져오기; 세 분류별 기대 count와 fixture username을 비교 | direct file selection / 각 업로드 최대 120초 |
| `PRD-IMPORT-MULTI` | loose JSON·HTML 최대 512개 함께 선택 가능; ZIP은 loose files와 혼합 불가 | `input[type=file][multiple]`; mixed loose selection success; 512 boundary accept, 513 reject; ZIP+loose reject | file-selection step; frozen group fixture로 실제 선택 / 300초 |
| `PRD-IMPORT-HTML` | HTML follower/following에서 ID 해석 실패가 있으면 파일명을 포함한 오류로 중단, 잘못된 결과 미생성 | malformed HTML fixture 업로드 후 `[role=alert]`의 파일명·오류; 기존 결과 불변 | direct file selection / 60초 |
| `PRD-IMPORT-PROGRESS` | worker의 읽기와 분석 단계를 구분 표시하고 창 닫기/중단 시 즉시 취소 | `[role=status][aria-live=polite]`의 `파일을 읽고 있어요` → `팔로우 목록을 확인하고 있어요`; footer `읽기 멈추기`; 취소 후 결과 미저장 | 64MiB valid synthetic archive 업로드 후 100ms DOM polling, 중단 클릭 / 30초 |
| `PRD-IMPORT-ACCOUNT` | 기존 기록과 다른 계정의 파일은 차단 | mismatch fixture 후 계정 불일치 안내, 기존 snapshot hash/DOM 불변 | existing synthetic account result → mismatch upload / 60초 |
| `PRD-IMPORT-MISSING` | followers 또는 following 중 하나라도 없으면 결과 생성 중단, 두 목록 모두 필요하다는 안내 | 두 누락 fixture 각각 업로드; `[role=alert]` 문구와 기존 결과 불변 | direct file selection / 각 60초 |
| `PRD-IMPORT-SIZE` | ZIP 128MiB, loose file 32MiB, loose aggregate 64MiB 한도 적용 | 세 경계 초과 fixture 각각 업로드; 정확한 오류 문구, 기존 결과 불변 | existing synthetic result; 각 boundary upload / 합계 180초 |
| `PRD-RESULT-RECIPROCITY` | 내가 팔로우하지만 나를 팔로우하지 않는 계정 분류·수치·목록 정확 | `나를 맞팔 안 한 사람` count와 fixture username set 대조 | valid synthetic snapshot / 30초 |
| `PRD-RESULT-REVERSE` | 나를 팔로우하지만 내가 팔로우하지 않는 계정 분류·수치·목록 정확 | `내가 맞팔 안 한 사람` count와 fixture username set 대조 | valid synthetic snapshot / 30초 |
| `PRD-RESULT-MUTUAL` | 서로 팔로우하는 계정 분류·수치·목록 정확 | `맞팔 중인 사람` count와 fixture username set 대조 | valid synthetic snapshot / 30초 |
| `PRD-RESULT-SNAPSHOT` | 같은 계정의 서로 다른 두 완전한 기록 비교는 무료이며 최신 비교 count와 이름 제공 | previous→current snapshot; `팔로워에서 빠진 사람` count와 list 대조; 원인 단정 문구 없음 | two complete snapshots / 120초 |
| `PRD-RESULT-SEARCH` | 관계 목록은 username 순이며 8명 초과 시 검색 칸 표시 | exact placeholder `이름 또는 아이디 찾기`; visible row usernames order; exact handle 검색 후 row count/target 확인 | 9+ row fixture / 45초 |
| `PRD-SAMPLE-EXPORT` | 샘플에서 목록 공유/복사/저장 비활성화 | `matrix-export-btn` controls disabled + sample-specific title; click 불가 | sample relationship list / 30초 |
| `PRD-PRIVACY-LOCAL` | 관계 데이터는 기기 안에서 처리; 사용자가 공유할 때 선택한 외부 목적지로 전달될 수 있음 | 앱의 실제 고지문 + browser network policy 차단; share preview/target은 별도 관찰 | import guide/result / 30초; native share sheet N/A |
| `PRD-PRIVACY-DELETE` | 전체 초기화는 로컬 v7/v6/legacy, onboarding, folder, refresh keys 제거; 예약 알림 취소; iOS WebView data/cookies 삭제; 결제 권한 유지 | isolated browser localStorage keys before/after; native iOS cookies/notifications are N/A, not pass | synthetic-only context에서 확인·실행 / 60초 |
| `PRD-IDENTITY-LIMIT` | 백업에는 permanent ID가 없으며 username 변경이 변화로 보일 수 있음을 고지 | current comparison help/copy contains username-change limitation; no confirmed cause claim | open latest comparison explanation / 30초 |
| `PRD-IMPORT-SNAPSHOT-UNKNOWN` | 실제로 비었는지 알 수 없는 과거 백업은 비교 제외 | empty-previous→current; no fabricated unfollow delta, explicit unavailable/excluded state | two snapshots / 120초 |
| `PRD-IMPORT-ALLTIME` | Instagram export guide에서 기간 `전체 기간` 선택 가능 | guide scene text + selected row/step evidence | request guide scenes / 45초 |
| `PRD-IMPORT-SAVE-FAIL` | 저장 쓰기 실패 시 안내와 `다시 저장`; 기존 데이터 보존 후 retry success | deterministic one-shot localStorage write-failure adapter; before/after state digest, alert, retry action | synthetic-only test harness / 60초; browser observation과 분리 표기 |
| `PRD-IMPORT-REOPEN` | 앱 재실행 시 저장된 단계 이어하기 | localStorage onboarding key before close, same isolated profile reopen, resumed screen | persist request/wait/import step then reopen / 45초 |
| `PRD-SNAPSHOT-RETENTION` | 무료·유료 모두 최근 최대 10개 보관 | 11 unique synthetic snapshots; history IDs newest 10; oldest removed/retention behavior | isolated library / 300초 |
| `PRD-PAYWALL-BOUNDARY` | 현재 관계·이름·최신 두 기록 비교는 무료; Pro는 여러 기록 timeline, two-date compare, per-person history | free result names and latest compare visible; Pro history entry points locked; no purchase; no old “masked name” assumption | free entitlement + 2+ synthetic snapshots / 60초 |

## 이전 판정 기준과의 차이

1. 시작 경로가 구 PRD의 `1 / 3단계` 직접 가져오기 전제로 고정돼 있었으나 현재 PRD는 More의 `이미 받은 자료로 확인하기`에서 저장 자료를 바로 여는 경로를 명시한다.
2. 파일 선택 기준을 단순 `multiple=true`에서 512 loose files, JSON+HTML 혼합, ZIP+loose 혼합 금지, 파일당 32MiB, 합계 64MiB까지 확대했다.
3. 진행 상태의 중단 control 실제 라벨은 `읽기 멈추기`다. native close/abort 경로도 검증 대상으로 명시했다.
4. 최신 두 기록 비교는 무료이며 계정 이름을 가리지 않는다. Pro 경계는 여러 기록 timeline, 날짜 선택 비교, 사람별 이력이다.
5. 결과 검색의 실제 placeholder는 `이름 또는 아이디 찾기`; 목록은 username 순이다. 별도의 새 정렬 UX는 추가하지 않는다.
6. 전체 초기화는 desktop에서 localStorage 일부만 검증 가능하다. iOS WebView/cookie·알림 취소는 N/A로 분리한다.
7. 공유는 사용자가 고른 앱/위치로 목록을 전달할 수 있으며 샘플 공유는 비활성화한다. 단순히 “모든 외부 요청이 차단됨”을 제품의 전체 데이터 흐름 성공 기준으로 쓰지 않는다.

## Cohort와 provenance

`peekly-persona-library-v2` 원본은 변경하지 않는다. `peekly-persona-library-v3`는 32개 기존 persona ID를 동일하게 유지하고 revision을 하나씩 올린 별도 라이브러리다. 각 profile의 behavioral identity는 보존하되 current PRD 기준 지시를 추가했다. 페르소나별 old/new requirement mapping 및 PRD excerpt 변경은 `persona-prd-diff-v3.json`에서 확인한다. 이 synthetic cohort는 실제 사용자 대표성·선호·실제 계정 동작을 증명하지 않는다.
