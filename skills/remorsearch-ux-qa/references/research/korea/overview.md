# 한국 리서치 팩 개요

한국 사용자, 한국 채널, 한국 통계가 들어가는 리서치 실행에서 이 팩을 씁니다. 팩은 research 모드의 기본 흐름
(`references/research/workflow.md`, `references/research/audience-pipeline.md`)을 바꾸지 않고, 단계마다 한국
맥락에서 달라지는 점을 더합니다. 읽기 계약은 `references/research/public-page-access.md`를, 등급 규칙은
`references/research/source-grading.md`를 그대로 따릅니다. 이 팩과 두 문서가 다르면 더 엄격한 쪽을 따릅니다.

이 팩에는 중단을 넘는 방법이 없습니다. 멈춘 페이지는 수집 공백으로 보고서에 남깁니다. 이 팩은 법률 자문도
아닙니다. 법령 근거는 `references/research/korea/legal-checklist.md`에 모았습니다. 확인일은 2026-09-29이고, 확인
표시(관찰됨, 미확인, 추론)는 팩의 다른 문서와 같습니다.

## 1. 언제 쓰는가

다음 가운데 하나라도 맞으면 이 팩을 씁니다.

- 브리프의 `product.locale`이 `ko-KR`임.
- 브리프의 `languages.primary`가 `ko`임.
- 브리프의 `report_lang`이 `ko`임.
- 제품의 사용자나 조사할 채널이 한국 사용자·한국 채널임.

ergonomics Stage 0(`references/ergonomics/audience-research.md`)도 웹 근거를 research 실행에서 받으므로, 한국
사용자를 다룰 때는 같은 규칙을 따릅니다. persona-qa에서 한국 웹 접근성을 점검할 때는
`references/persona-qa/kwcag-2.2.md`를 함께 읽습니다.

## 2. 단계별로 달라지는 점

단계 이름은 `references/research/audience-pipeline.md`의 A0-A6을 따릅니다.

| 단계 | 한국 팩에서 달라지는 점 | 먼저 읽을 파일 |
| --- | --- | --- |
| A0 브리프 | 팀 자료, 약관 확인 기록, 윤리 심의, 유튜브 키, 승인 커뮤니티 | `references/research/korea/legal-checklist.md` |
| A1 계획 | 채널별 경로·중단·약관 상태, 통계 출처 카드, 덜 잡히는 집단 | `references/research/korea/platform-map.md`, `references/research/korea/statistics.md` |
| A2-A3 발견·읽기 | 한국어 검색어, 꺼 둔 검색 API, 검색 결과 페이지 거절, 약관 중단, AI 에이전트 robots 규칙, 식별 정보 지우기 | `references/research/korea/query-craft.md`, `references/research/public-page-access.md` |
| A4-A5 병합·등급 | 협찬·리뷰 보상·가상인물 표지, 자체 브랜드 리뷰, 비꼼·전해 들은 말·초성체, 익명 닉네임 | `references/research/korea/promotion.md`, `references/research/korea/query-craft.md` |
| A6 보고 | 한국어 보고서 틀과 문체, 접근 표, 유튜브 데이터 보관 기한, 법률가 판단 항목 | `references/research/korea/report-template.md` |
| persona-qa | KWCAG 2.2와 WCAG 2.2를 따로 적음 | `references/persona-qa/kwcag-2.2.md` |

### A0 브리프

- 팀 자체 VOC, 고객센터 기록, 스토어·판매자 콘솔 내보내기가 있는지 먼저 물음. 측정 자료이므로 가장 먼저 씀.
- 팀 자료는 전화번호, 이메일 주소, 주민등록번호, 카드·계좌 번호 같은 식별 정보를 지운 뒤 받음. 이런 자료를 정리하는
  명령은 아직 없음(계획).
- `access_policy.terms_checked`에는 사용자가 호스트의 현행 약관을 직접 읽은 뒤에만 항목을 적음. 항목마다 `host`,
  조항 앵커나 번호를 붙인 `terms_url`, `checked_on`, `result`가 필요하고 `note`는 선택임. `result`는
  `permits_this_reading`, `restricts_this_reading`, `unclear` 가운데 하나임. `permits_this_reading`인 항목만 그
  실행에서 `reported` 제한을 풀고, 풀린 호스트는 실행당 문서 10건까지 읽음. `confirmed` 제한은 풀리지 않음. 에이전트는
  이 항목을 쓰지 않고, 명령줄 스위치도 없음.
- 윤리 심의는 `ethics_review`에 적음(`status`는 `none`, `exempt`, `approved`, `pending` 가운데 하나, `body`와
  `reference`는 선택). 기록만 하고 강제하지 않음.
- 유튜브 댓글이 필요하면 사용자 본인의 키를 환경 변수 `REMORSEARCH_YOUTUBE_API_KEY`로 받음(예전 이름
  `YOUTUBE_API_KEY`도 받음). 키는 환경 변수로만 받고 파일에 두지 않음. 키가 없으면 수집 공백이자 사용자에게 묻는
  질문임.
- 사용자가 회원인 커뮤니티는 사용자가 직접 승인한 경우에만 `access_policy.signed_in_communities`에 적음. 카페처럼 한
  호스트에 여러 커뮤니티가 있으면 `path_prefix`를 함께 적음. 그 커뮤니티의 회원 전용 글도 요약으로만 남김.
- 브리프 형식은 `schemas/ux-research-brief.v1.schema.json`을 따름.

### A1 계획

- 채널마다 정당한 경로, 예상 중단, 약관 상태를 계획에 적음(`references/research/korea/platform-map.md`).
- 약관 제한 호스트는 계획 단계에서 수집 공백으로 미리 적음. `reported` 호스트는 사용자의 약관 확인이 있어야 읽고,
  `confirmed` 호스트(유튜브 페이지, 인스타그램, 스레드, 페이스북)는 풀리지 않음.
- 한국 제품이면 `kr-communities` 축을 `global-communities` 축보다 먼저 돌림(`references/research/audience-pipeline.md`의
  기본 축).
- 통계는 승인번호, 모집단, 기준 시점, 표본 수를 담은 출처 카드와 함께 고름(`references/research/korea/statistics.md`).
- 공개 웹에서 덜 잡히는 집단(50-60대, 학생, 닫힌 카페)은 설문, 인터뷰, 팀 자료로 계획함.

### A2-A3 발견·읽기

- 한국어 검색어와 사용자 언어 읽기 규칙을 따름. 씨앗 단어는 후보이며 이번 실행의 글에 나온 말만 런 폴더의
  `lexicon.json`에 남김(`references/research/korea/query-craft.md`).
- 네이버 검색 API, NAVER API HUB, 네이버 데이터랩, 카카오 다음 검색 API는 소유자가 현행 약관을 읽기 전까지 꺼 둠.
  reader는 이 엔드포인트를 부르지 않고, 직접 넘기면 exit 2로 거절함.
- 검색 결과 페이지는 `read`, `robots`, `ingest`가 exit 2로 거절함. 리디렉션 중에 만나면 범위 밖 중단으로 기록함. 발견은
  에이전트 자신의 검색 도구로 하고, 결과로 나온 페이지를 하나씩 읽음.
- `terms_restricted` 호스트는 요청 전에, 그리고 리디렉션 단계와 공식 경로·대체 주소마다 멈춤. 제한 호스트로 넘어가는
  짧은 주소도 멈춤. `robots`는 이런 호스트에서 exit 3을 내고, 브라우저 도구도 그 호스트를 열지 않음. `ingest`는 풀리지
  않은 제한 호스트의 캡처를 받지 않음.
- robots.txt는 `RemorsearchUXQA` 그룹이 있으면 그 그룹만으로 판정함. `*` 그룹으로 판정된 경우에만, 사용자 요청으로
  페이지를 여는 AI 에이전트 토큰 그룹의 금지도 우리 토큰의 금지로 따름(중단 `opted_out`, 이유
  `robots:ai_agent:<token>`). 학습·검색 크롤러 그룹의 금지는 신호(`ai_training_disallow`)로만 기록함. 토큰 목록은
  `uxresearch/data/agent-tokens.json`에 있음.
- 유튜브는 Data API로만 받음(공식 경로만 쓰는 방식). 영상 주소에서 영상 ID만 읽고 videos.list와
  commentThreads.list를 쓰며, 페이지 요청과 렌더 캡처는 하지 않음. 키가 없으면 `official_route_needs_key`로 수집
  공백이 되고, 키 거절이나 그 밖의 실패로 공식 경로가 끝나면 그 주소는 `terms_restricted`로 끝나며 페이지로 바꾸지
  않음. 작성자 이름은 솔트 키로 바꾸고 채널 ID는 저장하지 않음. API로 받은 항목마다 `retention_until`(받은 시각 +
  30일)을 둠. 채널·재생목록·검색 페이지는 경로가 없어 수집 공백임.
- `read`와 `ingest`가 에이전트에게 보여 주거나 파일로 남기는 글에서는 전화번호, 이메일 주소, 주민등록번호, 카드·계좌
  번호, IP 주소(일부만 보이는 IP 포함), @핸들, 작성자 프로필 URL을 먼저 지움. 계획된 `merge`의 원문 대조는 지운 뒤의
  글과 비교함. 지우는 규칙은 완전하지 않으므로 인용은 짧게 두고 검증자가 표본을 확인함.
- `author-key`는 기본 익명 닉네임(ㅇㅇ 등)과 IP 일부가 붙은 닉네임을 거절함. 이런 글은 `--thread-url`로 스레드 키를
  받음.

### A4-A5 병합·등급

- 표지는 `uxresearch/data/markers.json`에 있음. 협찬·광고 표시(`promotion`, `promotion_patterns`,
  `promotion_placed`, `promotion_labels`), 리뷰 보상(`incentive`: `seller_event`, `seller_notice`,
  `platform_points`, `reward_unspecified`), 가상인물(`virtual_person`), 회원·본인 확인 게이트(`membership`,
  `age_identity`), 기본 익명 닉네임(`anonymous_handles`)이 있음. 표지는 후보이며 검증자가 확인함
  (`references/research/korea/promotion.md`).
- 리뷰 보상 표시가 있으면 만족·선호·반대 근거 검색·별점 평균은 D까지만 인정함. 불만과 대처 방법은 한 단계만
  낮춤(최소 C). 판매자나 게시판의 보상 공지는 페이지 전체를 낮추지 않고 리뷰별 후보로 넘김. 플랫폼 전체의 리뷰 적립
  제도와 판매자가 여는 리뷰 이벤트는 구분함.
- 플랫폼 자체 브랜드 상품 리뷰는 다른 채널 계열의 근거가 있어야 셈.
- 비꼼, 전해 들은 말, 초성체는 `references/research/korea/query-craft.md`의 규칙으로 판단함. 익명 1인칭 사연은
  `narrative_unverified`로 다룸(`references/research/korea/platform-map.md` 4절).
- 커뮤니티의 성별·연령·정치 성향 추정치는 어떤 주장에도 쓰지 않음(`references/research/korea/platform-map.md` 4절).
- 등급과 상태 계산은 `gate`(계획)가 맡음. 나오기 전에는 `references/research/source-grading.md`를 손으로 적용하고
  "게이트가 아니라 손으로 확인함"이라고 적음.

### A6 보고

- 한국어 보고서 틀과 문체 규칙을 따름(`references/research/korea/report-template.md`). 본문은 합니다체, 표와 근거
  줄은 개조식임. 확인 표시는 관찰됨·추론·미확인이고, 주장 상태는 영문 코드에 한국어 풀이를 붙임.
- 지원되지 않은 주장은 "미확정 / 확인 필요 (부록)"에만 둠.
- 접근 표에 `terms_restricted` 중단을 다른 중단과 나눠 적고, 범위 밖 채널은 따로 셈. 공개 웹에서 덜 잡힌 집단도
  수집 공백으로 적음.
- 유튜브 API 항목은 `retention_until`이 지나면 지움.
- 작성자 이름 지우기는 출처 명시 규정(저작권법 제37조②)과 부딪칠 수 있음(검증되지 않은 분석, 법률가 판단). 회사
  안의 리서치가 영리 목적(저작권법 제94조②1호 단서)에 드는지도 법률가 판단임. 조문은 법률 제21336호(2026-08-11
  시행판)를 공개 저장소 사본으로 읽음 — 미확인(미러). 기본값은 풀어 쓰기와 짧은 인용임
  (`references/research/korea/legal-checklist.md` L06, L08, 법률 자문 아님).

## 3. 한국 실무에서 이 팩이 돕는 방식

- 팀 자료를 먼저 씁니다. VOC, 고객센터 기록, 앱스토어·구글 플레이 콘솔 내보내기는 측정 자료(measured)이므로 가장 먼저
  봅니다.
- 공개 게시판만 읽습니다. 공개 커뮤니티 글은 reader(`scripts/ux_research.py read`)로 읽고, 회원 전용 글은 사용자가
  승인한 커뮤니티에서 요약으로만 다룹니다.
- 통계는 승인번호, 모집단, 기준 시점이 붙은 출처 카드와 함께 씁니다. 게시글 수는 비율이 아닙니다.
- KWCAG와 WCAG는 따로 보고합니다.
- 네이버처럼 멈추는 채널이 많다는 점을 처음부터 계획에 넣습니다. 멈춘 채널은 수집 공백으로 적고 다른 채널 계열과
  팀 자료로 채웁니다.

## 4. 요청 강도 신호어

요청에 아래 말이 있으면 실행 방식을 바꿉니다. 어느 경우에도 중단 규칙, 등급 규칙, 확인 표시는 그대로입니다.

| 신호어 | 실행 방식 |
| --- | --- |
| 간단히 | 가장 중요한 축 한두 개만 돌림. 예산을 줄이고 확장 라운드는 돌리지 않음. 결과는 짧게 쓰고 빠진 축을 부록에 적음 |
| 깊게, 철저히 | 기본 축을 모두 돌림. 제품이 바뀌었으면 시간 구간을 둘 이상 두고, 확장은 최대 2라운드까지 돌림. 반대 근거 검색이 필요한 주장은 모두 검색함 |
| 근거 붙여서, 출처 검증 | 모든 주장에 출처 ID를 붙이고 통계에는 출처 카드를 붙임. 검증자가 원문과 대조하는 발췌 표본을 늘림 |
| 공식 자료 위주 | 공식 통계, 운영사 문서, 팀 자료를 먼저 씀. 커뮤니티 글은 존재 주장에만 씀 |

"간단히"가 다른 신호어와 함께 나오면 "간단히"를 따릅니다. 다른 신호어가 요구한 일 가운데 하지 못한 것은 보고서의
"미확정 / 확인 필요 (부록)"에 다음에 할 일로 적습니다.

## 5. 하지 않는 일

- 로그인·회원 전용·유료·캡차·본인인증 뒤의 글을 읽지 않음.
- 사람 확인(캡차)을 풀거나 남에게 풀게 하지 않음. robots.txt, 약관 제한, 속도 제한, 봇 차단을 피해 가지 않음.
- 멈춘 페이지를 다른 호스트, 미러, 캐시, 아카이브, 앱, 요령으로 가져오지 않음. 그런 방법을 찾거나 문서에 적지도
  않음. 중단은 그 자체로 답이며 수집 공백으로 적음.
- 검색 결과 페이지를 긁지 않음.
- 페이지 뒤의 JSON이나 GraphQL 같은 문서화되지 않은 내부 엔드포인트를 부르지 않음.
- 소유자가 현행 약관을 읽기 전까지 네이버·카카오 검색 API를 쓰지 않고, 그 결과를 모델에 넣지 않음.
- 캐시·아카이브로 삭제된 글을 되살리지 않음.
- 회원 전용이거나 닫힌 커뮤니티를 사용자 단서로 이름 대지 않음. 승인하지 않은 커뮤니티의 회원 전용 글은 읽지도
  요약하지도 않음.
- 커뮤니티의 성별·연령·정치 성향 추정치를 게시자, 주장, 페르소나에 붙이지 않음.
- 커뮤니티 성비·연령 추정치를 세그먼트 비율로 쓰지 않음.
- 게시글·리뷰·좋아요 수로 비율을 말하지 않음.
- 말투나 호칭으로 나이·성별을 추정하지 않음.
- 협찬 표시가 없다고 순수 후기로 보지 않음.
- 특정인의 글 이력을 모으거나 신원을 추정하지 않음.
- 유튜브 댓글 작성자를 나이, 인종, 종교, 정치 성향, 성적 지향, 건강 같은 보호 속성으로 분류하거나 추정하지 않음.
- 작성자 이름·닉네임을 쓰지 않음. 인용은 300자 이하로 하고 풀어 쓰기를 먼저 씀.
- 법률 자문을 하지 않음. 법령은 조항과 판(공포일이나 시행일)을 함께 적고, law.go.kr나 원문에서 확인하지 못한 것은
  미확인으로 적음. 적용이 다투어지는 부분은 "법률가 판단"으로 적음.
- 다른 스킬 모음의 글·코드·표·목록을 옮기지 않음. 생각만 참고하고 그 출처는 `THIRD_PARTY_NOTICES.md`에 밝힘.

## 6. 완료 기준(Done when)

- 실행에 쓴 채널을 정당한 경로, 중단 유형과 함께 적음.
- 모든 호스트에 약관 상태가 있음(`references/research/korea/platform-map.md` 기준).
- 통계마다 출처 카드가 있음.
- 모든 출처가 협찬·리뷰 보상 표지 확인을 거침.
- 런 폴더에 이번 실행의 용어집 `lexicon.json`이 있음(형식은 `references/research/korea/query-craft.md` 4절).
- 한국어 보고서 틀에서 `report-check`(계획)가 통과함. 나오기 전에는 같은 규칙을 손으로 적용하고 그렇게 적음.
- 유튜브 API 항목에 `retention_until`이 있고, 30일이 지난 항목은 지움.
- 접근 표에 `terms_restricted` 중단과 공개 웹에서 덜 잡힌 집단을 적음.

## 7. 실패 유형(Failure modes)

- 네이버 채널이 멈춤: 약관 제한 때문에 예상된 결과임. 보고서에 수집 공백으로 적고 팀 자료와 다른 채널 계열로
  보완함. 우회하지 않음.
- 전역 검색 도구가 네이버 글을 잘 찾지 못할 수 있음(미확인): 결과가 없다고 논의가 없다는 뜻이 아님.
- 약관 상태가 `unchecked`인 호스트를 허용된 곳으로 읽음: `unchecked`는 확인하지 못했다는 뜻이지 제한이 없다는 뜻이
  아님. reader의 일반 중단 규칙은 그대로 적용됨.
- 커뮤니티 구성 수치가 서로 어긋남: 단서로만 쓰고 사람에게 붙이지 않음.
- 리뷰 폭주 기간을 사용성 문제로 읽음(예: 2025-09-23 카카오톡 개편 직후 보도, 미확인(요약)): 날짜 구간을 나눠 읽음
  (`references/research/korea/platform-map.md` 7절).
- 오래된 플랫폼 정보를 믿음: 확인일이 90일을 넘으면 다시 확인함.
- 운영사가 바뀐 뒤 약관이 바뀜: 디시인사이드(2026-02 매각 본계약 보도, 종결 미확인)와 다음(2025-12 운영사 변경,
  2026-05 인수, 2026-07 사명 변경, 2026-09 외부 AI 크롤링 정책 개정 보도, 모두 미확인(요약))은 실행 전에 약관과
  robots를 다시 확인함(`references/research/korea/platform-map.md` 7절).
- 키가 없음: 수집 공백이자 사용자에게 묻는 질문임. 다른 경로로 바꾸지 않음.
- 신호어를 잘못 읽음: "간단히"가 있으면 짧은 실행이 이김. 빠진 일은 부록에 적음.

## 8. 이 폴더의 파일

| 파일 | 내용 |
| --- | --- |
| `references/research/korea/overview.md` | 이 문서. 언제 쓰는가, 단계별 차이, 신호어, 하지 않는 일 |
| `references/research/korea/platform-map.md` | 한국 채널 27곳의 공개 범위, 정당한 경로, 예상 중단, 약관 상태, 콘텐츠 규범 |
| `references/research/korea/query-craft.md` | 한국어 검색어 짜기와 사용자 언어 읽기(초성체, 비꼼, 말투, 용어집) |
| `references/research/korea/promotion.md` | 협찬·광고 표시, 리뷰 보상, 가상인물, 자체 브랜드 상품 리뷰의 등급 규칙 |
| `references/research/korea/statistics.md` | 한국 통계 출처 카드, 모집단 틀, 기관 이름 변경 |
| `references/research/korea/legal-checklist.md` | 스킬 규칙과 법령 근거 대조표(법률 자문 아님) |
| `references/research/korea/report-template.md` | 한국어 보고서 틀과 문체 규칙 |
| `references/persona-qa/kwcag-2.2.md` | KWCAG 2.2와 WCAG 2.2 대조(persona-qa) |
| `uxresearch/data/korea-platforms.json` | 플랫폼 지도 데이터(platform-map.md의 원본) |
| `uxresearch/data/korea-statistics.json` | 통계 출처 데이터(statistics.md의 원본) |

영문 기본 문서는 `references/research/workflow.md`(흐름), `references/research/audience-pipeline.md`(A0-A6),
`references/research/public-page-access.md`(읽기 계약), `references/research/source-grading.md`(등급),
`references/research/research-protocol.md`(기록 양식), `references/research/evidence-classification.md`(근거 유형),
`references/research/output-template.md`(영문 보고서 틀)입니다.
