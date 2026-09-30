# 인수인계: Remorsearch UX QA (클라우드 세션 → 로컬)

작성: 2026-09-30, 클라우드 세션(패키징 담당). 공개 배포 전에 이 파일, `docs/handoff/`,
`COORDINATION.md`를 모두 지웁니다.

## 1. 한눈에 보기

- **레포와 브랜치**
  - 레포: `remorser58/Remorsearch_UX_QA_Skill` (비공개)
  - 작업 브랜치: `claude/admiring-goldberg-llu3f5`
  - PR: [#1](https://github.com/remorser58/Remorsearch_UX_QA_Skill/pull/1) (초안, `main`으로)
- **지금까지 한 것**
  - 스킬 4개를 `skills/remorsearch-ux-qa/` 하나로 통합했습니다.
  - 공개 페이지 리더와 서브에이전트 모델 실험을 마쳤습니다.
  - 한국형 리서치 팩(K1)과 읽기 규칙(K2)을 넣었습니다.
  - 유튜브 댓글은 공식 Data API로 읽도록 했습니다.
  - 반박 검토 4건에서 지적 72건이 나왔고, 그중 코드 쪽 대부분을 고쳤습니다.
- **남은 것**: 문서 수정 대부분(특히 한국어 팩), 원문 재확인, 옆 세션 요청, 공개 전 정리. 순서는 5절에 있습니다.
- **검증 상태** (이 문서가 들어 있는 커밋 기준)
  - Python 테스트 638개 통과
  - `smoke_loop.py` 통과: 스킬 폴더만 따로 복사해도 통과
  - 웹 드라이버 셀프테스트 234개 통과
- **가장 먼저 할 일**: 5절의 P0 다섯 가지. 대부분 한국어 팩 문서의 안전 규칙 위반과 사실 오류입니다.

## 2. 로컬에서 시작하기

```sh
git clone https://github.com/remorser58/Remorsearch_UX_QA_Skill.git
cd Remorsearch_UX_QA_Skill
git switch claude/admiring-goldberg-llu3f5
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py
(cd skills/remorsearch-ux-qa/drivers/web && npm install && npx playwright install chromium && node selftest.mjs)
```

- **환경 요구사항**
  - Python 3.10 이상, 표준 라이브러리만 씁니다.
  - 리더와 루프가 `fcntl`을 쓰므로 macOS나 Linux가 필요합니다. Windows는 WSL을 쓰세요.
  - 드라이버는 Node.js 22와 Playwright가 필요합니다.
- **커밋 작성자**: remorser58 `<remorser58@naver.com>`입니다. 클라우드에서는 서명 때문에 커미터만 Claude로 두었을 뿐이니, 로컬에서는 평소처럼 본인 이름으로 커밋하면 됩니다.
- **테스트 규칙**
  - 테스트는 네트워크를 쓰지 않고, 127.0.0.1의 로컬 서버만 씁니다.
  - 새 테스트는 `tests/`에 두고, 파일 맨 앞에서 `import _paths`를 합니다.

## 3. 결정 사항

### 3.1 한국형 팩 구현 때의 결정 (`docs/handoff/design/owner-decisions.md`, 영어)

**결정 D1~D13**

- **D1 약관 제한(`terms_restricted`)**
  - `reported`: 사용자가 기록한 확인으로만 풀립니다.
  - `confirmed`: 풀리지 않습니다. 유튜브 페이지와 메타 플랫폼이 여기에 해당합니다.
  - 요청하기 전에 멈추고, 리디렉션의 매 단계에서도 멈춥니다.
- **D2 AI 에이전트용 robots.txt 그룹을 따릅니다.**
- **D3 연구자 메모 기능은 뺍니다.**
- **D4 네이버·카카오 검색 API는 꺼 둡니다.** 소유자가 약관을 읽기 전까지입니다.
- **D5 한국형 팩은 전부 한국어로 씁니다.**
- **D6 키는 `REMORSEARCH_*` 환경 변수로만 받습니다.**
- **D7 보상 리뷰(리뷰 이벤트 등)**
  - 만족도·선호에 쓰는 근거와 별점 평균: 최대 D등급입니다.
  - 불만·우회 방법에 쓰는 근거: 최대 한 단계만 낮춥니다.
- **D8 자체 브랜드 상품 리뷰는 다른 채널의 확인이 필요합니다.**
- **D9 모델이 보기 전에 개인정보를 지웁니다.**
- **D10 저작권법 제37조와 제94조② 적용은 변호사 판단입니다.**
- **D11 `ethics_review` 필드는 기록만 합니다.**
- **D12 유튜브 Data API 경로를 둡니다.**
- **D13 몇 가지는 뒤로 미룹니다.**

**안전 규칙 S1~S6**

- S1: 우회 금지.
- S2: 비공개·회원 전용 커뮤니티를 사용자 단서로 적지 않음.
- S3: 커뮤니티 성향을 개인에게 씌우지 않음.
- S4: 법률 자문 아님, 미확인 표시.
- S5: 남의 코드와 글 복사 금지.
- S6: 짧은 인용, 작성자 비식별.

### 3.2 검토 뒤에 추가된 결정 (코드에 반영됨)

1. **봇 차단과 브라우저 확인 화면은 멈춤입니다.**
   - 정직한 요청을 거절하는 `bot_filter`와 "브라우저 확인 중" 화면인 `js_check`는 R2·R3로 올라가지 않습니다.
   - 둘 다 등록 도메인 전체의 `opted_out` 멈춤입니다.
   - 확인 화면을 거친 캡처는 `ingest`가 거부합니다. 캡처에 확인 표지가 있거나, 대기 시간 `waited_ms`가 0보다 크면 확인 화면을 거친 것으로 봅니다.
   - robots.txt 자리에 확인 화면이 오면 그 사이트 전체를 거부로 봅니다.
2. **서면 허락이 필요한 약관은 허락 기록이 있어야 풀립니다.**
   - 대상: 디시인사이드, 네이버, 네이버 카페 공지, 쿠팡, X.
   - 해제하려면 약관 확인에 `permission {granted_by, granted_on, reference}`가 있어야 합니다.
   - 항목마다 `lift_requires`로 표시되어 있습니다.
3. **약관 확인은 항목마다 따로 합니다.**
   - 확인의 `terms_url`이 그 항목의 약관 문서여야 합니다.
   - 확인의 `host`는 그 항목의 호스트이거나 더 좁아야 합니다.
   - 한 URL에 걸린 항목은 모두 풀려야 그 URL을 읽습니다.
   - 항목의 효력일(`effective_from`) 이전 확인과 365일이 지난 확인은 무효입니다.
   - 네이버 카페 공지 항목은 약관 URL이 비어 있어서, 누가 공지 URL을 기록하기 전에는 풀리지 않습니다.
4. **해제된 항목은 한 실행에 문서 10개까지입니다.** 호스트마다가 아니라 항목 단위로 셉니다.
5. **남의 서버를 거친 사본은 읽지 않습니다.**
   - 대상: 아카이브, 번역·리더 프록시, AMP 캐시, 유튜브 대체 프런트엔드.
   - 제3자 사본(`third_party_copy`)으로 거부합니다. 공식 페이지의 웨이백 사본만 예외입니다.
6. **사이트 전체 멈춤은 등록 도메인 단위입니다.** 문구만으로 알아낸 속도 제한이나 사람 확인도 사이트 전체를 멈춥니다.
7. **`ingest`가 받는 캡처를 좁혔습니다.**
   - `--context anonymous`만 받습니다. 허가된 커뮤니티는 `signed_in`도 받습니다.
   - `unknown`은 거부합니다.
   - 리디렉션이 무한 반복되면 멈춤입니다.
8. **`start --routes`로 약관 항목 플랫폼의 경로를 추가하거나 바꿀 수 없습니다.**
9. **실행 폴더의 정책 해시를 명령마다 검증합니다.** 다만 해시까지 함께 고친 변조는 잡지 못합니다.
10. **유튜브 API는 켜 둡니다.**
    - 키 소유자가 YouTube API Services Terms, Developer Policies, 파생 지표·데이터 보관 부록을 따르는 조건입니다. 이 정책들은 검색 요약으로만 확인했습니다.
    - 항목마다 `retention_until`(30일)을 붙이고, 기한이 지나면 `validate_bundle.py`가 오류를 냅니다.
    - 자동 삭제 기능은 없습니다.
11. **테스트 전용 환경 변수를 없앴습니다.** 이제 사설 IP 차단을 끄는 경로가 없습니다.
12. **X를 약관 항목에 추가했습니다.** 단축 링크 `naver.me`, `me2.do`, `coupa.ng`, `t.co` 등도 요청 전에 멈춥니다.

## 4. 검토 결과와 처리 상태

검토 원문은 `docs/handoff/review/`의 `r1-legal.json`, `r2-code.json`, `r3-korean.json`, `r4-docs.json`에 있습니다. 코드 수정 결과는 `fix-code.json`에 있습니다.

| 검토 | 지적 | 고침 | 남음 |
| --- | --- | --- | --- |
| 코드 정확성 (C) | 17 | 17 | 0 |
| 법·안전 (L) | 23 | 19 | 부분 3개(L-13, L-14, L-21), 미착수 1개(L-18), L-08 문서 부분 |
| 문서·패키징 (D) | 16 | 6개(D-01, D-03, D-08, D-11, D-15, D-16) | 8개, D-13은 옆 세션 몫, D-14는 역사 기록이라 둠 |
| 한국어 내용 (K) | 16 | K-16 일부(README.ko.md) | 15개와 K-16 나머지 |

- **막아야 할 문제 2건: 수정 확인함**
  - C-01/L-01, `--routes`로 유튜브 멈춤 우회: 이제 `start`가 거부합니다(종료 코드 2).
  - C-02/L-02, 약관 확인 한 건이 맘카페 항목까지 풀던 문제: 이제 두 항목이 각각 따로 멈춥니다.
- **재현 스크립트 주의**: 검토자 재현 스크립트는 `docs/handoff/repro/`에 있습니다. 일부는 바뀐 동작(환경 변수 제거, 서면 허락 요구) 때문에 스크립트 자체가 중간에 멈춥니다. 이건 예상된 결과입니다.

## 5. 남은 일 (순서대로)

### P0: 공개 전 반드시

1. **한국어 팩의 안전 규칙 위반을 고칩니다.**
   - K-01: `platform-map.md` 3절·5절과 `korea-platforms.json`에서 비공개 채널(에브리타임, 밴드, 오픈채팅)의 "사용자 단서"를 지웁니다.
   - K-03: 네이버 블로그 "10~30대가 작성자의 약 70%"를 지웁니다.
   - K-13: `korea-statistics.json`에서 근거 없는 성비 메모를 지웁니다.
2. **법률 점검표의 사실 오류를 고칩니다.**
   - K-04: 2023도1086은 무죄가 아니라 파기환송입니다.
   - K-12: "Non-Authorized Data" 번역을 바로잡습니다.
   - L-08 나머지: `legal-checklist.md` L16·L17 행에 X 항목, `lift_requires`, `effective_from`, 유튜브 파생 지표 조건을 넣습니다.
3. **한국어 팩을 새 규칙(3.2절)에 맞춥니다.** K-16과 L-14 나머지입니다.
   - `platform-map.md` 3절의 채널별 규칙 줄은 `korea-platforms.json`과 같이 고쳐야 합니다. `tests/test_korean_pack.py`가 둘의 일치를 검사합니다.
   - `overview.md`, `legal-checklist.md`, `report-template.md`도 맞춥니다.
   - 반영할 내용: 봇 차단 멈춤, 항목별 해제, 서면 허락, X.
4. **L-18: 민감 속성은 작성자 키와 같은 기록에 두지 않습니다.** 건강, 장애, 나이 같은 속성이고, 출처 종류와 상관없이 적용합니다.
   - 대상 파일: `research-protocol.md`, `audience-pipeline.md`, 두 `evidence-bundle-contract.md`.
   - 두 번들 계약 파일은 바이트 단위로 같아야 합니다.
5. **L-13 나머지를 처리합니다.**
   - `routes.json`의 `x` 플랫폼 `terms_note`를 새 규칙에 맞게 고칩니다. 지금은 oEmbed가 쓸 수 있다고 되어 있습니다.
   - Reddit, Bluesky, Hacker News, 앱 스토어의 약관을 검토합니다.

### P1

6. **분량을 줄입니다** (K-02, D-02, K-15).
   - `platform-map.md`(102KB, 18%가 중복)는 요약표와 채널별 절로 다시 짭니다.
   - `overview.md`는 파일 전체가 아니라 필요한 절만 가리키게 합니다.
   - A0 단계에는 `legal-checklist.md` 6절 표만 필요합니다.
   - `public-page-access.md`에는 읽는 순서 안내를 붙입니다.
   - 빌더를 쓰려면 `docs/handoff/builders/`를 보되, 손으로 고친 부분이 있으니 먼저 출력과 현재 파일을 비교하세요.
7. **D-10: 약관 항목 표의 사본을 줄입니다.**
   - `public-page-access.md` 17.1절에만 표를 두고, README·`community-to-test.md`·`legal-checklist.md`는 그 절을 가리키게 합니다.
   - 17.1절 표와 `routes.json`이 일치하는지 검사하는 테스트를 추가합니다.
8. **작은 문서 수정**
   - D-04: macOS/Linux 필요, Windows는 WSL을 명시합니다.
   - D-05: `kwcag-2.2.md` 84행 문장을 고칩니다.
   - D-06: 문서에 남은 "소유자 결정 D#" 표기와 세션 이름을 뺍니다.
   - D-07: `SKILL.md`의 `cd` 뒤 경로가 틀린 명령을 고칩니다.
   - D-09: 설치된 폴더에서 레포 전용 경로를 가리키는 곳을 고칩니다.
   - D-12: 고지 파일의 인용 개수를 맞춥니다.
   - K-05~K-11, K-14: 디시 약관의 개정판 표기도 여기 포함됩니다(2026-07-14 개정, 07-21 시행, 검색 요약 기준).
9. **리더의 남은 한계를 판단합니다.**
   - L-21: 해시까지 고친 변조는 못 잡습니다. 실행 폴더 밖 기록이 필요한지 판단하세요.
   - 개인정보 지우기가 "iOS(17.2)" 같은 문자열을 IP로 잘못 지우는 문제를 조정합니다.

### P2: 공개 전 정리

10. **옆 세션 요청이 처리됐는지 확인합니다** (`COORDINATION.md` 마지막 두 절).
    - `read_page.mjs`: 확인 화면을 만나면 기다리지 않고 바로 멈추기
    - 드라이버 README 링크
    - `audience-research.md`의 멈춤 목록
    - PC-01 문구
    - `ux-design-discipline.md` 5.6절
    - 고령층 71.8%
11. **옆 세션 브랜치를 병합하고 전체 테스트를 돌립니다.**
12. **원문을 다시 확인합니다.** 클라우드 프록시가 막아서 `미확인(요약)`으로 남은 것들입니다.
    - 법령(law.go.kr), 공정위 추천·보증 심사지침, korea.kr 보도자료, KOSIS
    - 디시 제16조 최신판, 네이버 카페 공지 URL(`routes.json`에 기록해야 해제가 가능), 쿠팡, X, 당근 약관
    - YouTube API 정책과 파생 지표 부록
13. **반박 검토를 한 번 더 돌립니다.** 특히 한국어 팩과 법률 점검표를 봅니다.
14. **공개 배포합니다.**
    - `COORDINATION.md`, `HANDOFF.md`, `docs/handoff/`를 지웁니다.
    - PR 본문을 갱신하고 `main`에 병합합니다.
    - 레포 설명과 토픽을 설정하고(PR 본문 체크리스트 참고) Public으로 바꿉니다.

## 6. 옆 세션 (인체공학 스웜)

- **누구인가**: 클라우드 세션 "스킬 확인"입니다. 브랜치는 `claude/practical-edison-n5sisf`이고, 이쪽이 마지막으로 병합한 커밋은 `abb2a55`입니다.
- **그쪽 파일**
  - `references/ergonomics/`, `ergoqa/`, `drivers/`
  - `docs/ergonomic-swarm-spec.md`, `docs/human-factors/`, `docs/validation/experiments/`
  - `benchmarks/`, `tests/test_ergo_*`
- **협업 방식**
  - 연락은 두 브랜치의 `COORDINATION.md`로 합니다.
  - 그쪽은 자기 브랜치에만 푸시하고, 병합은 이쪽이 합니다.
  - 로컬로 옮긴다는 사실도 `COORDINATION.md`에 적어 두었습니다.

## 7. 참고

- 서브에이전트 모델 실험: `docs/validation/subagent-model-benchmark.md`. 결론은 Sonnet 5.5 max 추천, Haiku 제외입니다.
- 첫 실행 설정: `skills/remorsearch-ux-qa/references/agent-setup.md`.
- 한국형 팩 입구: `skills/remorsearch-ux-qa/references/research/korea/overview.md`.
- 읽기 규칙 전체: `skills/remorsearch-ux-qa/references/research/public-page-access.md`. 17절이 약관 규칙입니다.
- 이 클라우드 세션에서 정리한 것: PR #1 자동 점검 예약 취소, PR 활동 구독 해제. 이 세션은 더 이상 브랜치에 푸시하지 않습니다.
