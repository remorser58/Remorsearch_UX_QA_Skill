# Remorsearch UX QA

[English](README.md) | 한국어 | [PRD · 제품 요구사항](PRD.md)

Remorsearch(리모서치, *ree-mor-search*) UX QA는 어느 정도 완성된 제품의 UX를 개선하는 Claude Code·Codex 스킬입니다. 제품 URL이나 저장소와 함께 개선을 요청하면, 에이전트가 제품과 개발자의 결정을 확인하고 초기 QA에서 조사 질문을 찾습니다. 관련 사용자 경험을 조사해 필요한 부분을 수정한 뒤 같은 과업을 다시 실행합니다. 문제 목록, 페르소나, 조사 질문은 미리 준비하지 않아도 됩니다.

## 하는 일

네 구성 요소를 요청에 맞게 함께 사용합니다. 사용자가 모드를 고르거나 단계마다 자료를 다시 전달할 필요는 없습니다. 조사나 리뷰만 요청한 경우에는 그 범위에서 마칩니다.

| 구성 요소 | 하는 일 | 필요한 것 |
| --- | --- | --- |
| **research** | 커뮤니티·댓글·리뷰·공식 자료에서 과업과 관련된 경험, 우회 행동과 반대 사례를 찾고 원문 맥락과 조사 공백을 기록합니다. | 허용된 출처 접근 경로. 유튜브 댓글은 본인의 YouTube Data API 키(`REMORSEARCH_YOUTUBE_API_KEY`)를 사용합니다. |
| **persona-qa** | 실제 제품에서 과업 완료, 입력 보존, 오류·복구, 키보드와 접근성을 확인합니다. 합성 페르소나는 서로 다른 테스트 조건을 만듭니다. | 접근 가능한 제품과 안전한 테스트 자료. 기본 웹 드라이버에는 Node.js 22와 Playwright가 필요합니다. |
| **ergonomics**(실험적) | 시뮬레이션한 프로필로 도달, 터치, 지각, 시간과 배치를 선별 점검합니다. | 관련 시나리오. 모델 결과와 실제 기기·사람의 검증을 구분합니다. |
| **loop** | 한도 안에서 수정, 현재 빌드 재실행, 회귀와 의도 보존 결과를 기록합니다. | 호스트의 브라우저·Figma 도구와 실제 실행 기록. 개선 요청에 포함된 권한을 로컬 수정 범위에 맞게 기록합니다. |

제품 이해부터 수정·재검증까지 이어지는 호스트 에이전트 지침을 구현했습니다. CLI는 전달받은 근거를 검증하고 범위가 정해진 로컬 텍스트 패치를 적용합니다. 브라우저 조작, Figma 작업과 빌드 실행은 호스트가 수행합니다. 실제 제품에서 요청부터 개선 완료까지 이어지는 전체 실행은 별도 검증이 필요합니다. 기존 픽스처와 구성 요소 검사만으로 전체 실행을 검증했다고 주장하지 않습니다.

## 설치

명령 하나로 스킬 전체를 설치합니다. research, persona-qa, ergonomics, loop 네 구성 요소와
참조 문서·스키마, 번들로 포함된 insane-search 원문, 명령 실행기, 고정된 웹 드라이버와
Chromium이 모두 담깁니다. 기능을 골라 설치하는 방식은 없고, 참조 문서는 작업마다 필요할 때
불러 읽습니다. 사용자는 테스트 패킷이 아니라 URL이나 저장소를 넘겨 주면 되고, 번들 예제는
스킬 자체 점검용 유지보수 자료일 뿐입니다. Python 도구는 macOS, Linux, Windows의 WSL에서
Python 3.10 이상과 표준 라이브러리, POSIX 파일 잠금을 사용합니다. 기본 `python3`가 더 낮으면(macOS 기본 Python은 3.9입니다) 호스트가 스킬 폴더에서 `python3 scripts/find_runtime.py`를 실행합니다. 지원되는 가장 높은 Python, Node.js 22 경로와 공백을 JSON으로 출력하며 아무것도 설치하지 않습니다.

```sh
git clone https://github.com/remorser58/Remorsearch_UX_QA_Skill.git
cd Remorsearch_UX_QA_Skill
python3 scripts/install.py --target codex
```

`--target claude`는 `~/.claude/skills/remorsearch-ux-qa`에, 기본값 `codex`는
`~/.codex/skills/remorsearch-ux-qa`에 설치합니다. 격리해서 시험해 보려면
`--destination /path/to/folder`로 경로를 직접 정하세요. 유지보수용 패키징과 무결성 검사는
[빌드와 배포 전 검사](docs/release.md)에 정리했습니다.

Python 3.10 이상, Node.js 22(>=22 <23), npm을 먼저 확인한 뒤에야 파일을 씁니다. 설치 스크립트는
임시 복사본의 `drivers/web`에서 `npm ci`를 실행하고, Playwright가 쓰는 브라우저 캐시(macOS
기본 `~/Library/Caches/ms-playwright`, `PLAYWRIGHT_BROWSERS_PATH`를 먼저 정하면 위치를 바꿀 수
있습니다)로 Chromium을 내려받고, 마지막에 실제 Chromium 실행을 확인한 뒤 설치를 마칩니다.
전역 런타임이나 계정은 건드리지 않습니다. Node.js 22를 쓰십시오. 고정된 Playwright 1.56.1에서는
Node.js 24.16 이상과 Node.js 26에서 `npx playwright install`이 다운로드 뒤 멈춥니다
([microsoft/playwright#40724](https://github.com/microsoft/playwright/issues/40724), Playwright 1.60에서는 됩니다).

심볼릭 링크 경로, 원본 저장소, 관련 없는 기존 폴더, 파일 시스템 루트, 홈 디렉터리는 설치
대상으로 거절합니다. 드라이버 준비는 임시 복사본에서 먼저 끝내고, 의존성을 설치한 뒤에는
다시 검사합니다. npm이나 Chromium 내려받기가 실패해도 기존 설치는 그대로입니다.
Node.js, npm, 네트워크를 고친 뒤 같은 명령을 다시 실행하면 됩니다. 이미 설치된 스킬을
갱신할 때는 실행 기록과 심볼릭 링크까지 통째로 `remorsearch-ux-qa.backup-<timestamp>.tar.gz`로
보관한 뒤 새 설치를 넣습니다. 계정은 사용자가 준비합니다. 유튜브 댓글은 본인의 YouTube Data
API 키(`REMORSEARCH_YOUTUBE_API_KEY`)가 필요하고, Figma 비교에는 Figma 접근 권한이 필요합니다.

## 사용법

처음이어도 괜찮습니다. 평소 말투로 요청하거나, 스킬 이름을 불러서 시작하시면 됩니다.

```text
/remorsearch-ux-qa 우리 앱 UX 개선해줘. URL: https://app.example.test 또는 저장소: /path/to/product
/remorsearch-ux-qa 우리 앱 결제 화면에서 사람들이 왜 이탈하는지 리뷰와 커뮤니티 글에서 찾아 줘.
/remorsearch-ux-qa 결제 화면을 처음 쓰는 사용자 페르소나로 QA해 줘. Figma 파일은 이거야.
/remorsearch-ux-qa 갤럭시 S24에서 가입 흐름을 한 손으로 쓰거나 색약이어도 문제없는지 점검해 줘.
/remorsearch-ux-qa 간단히: 배달앱 재주문이 불편한 이유를 앱 리뷰에서 찾아 줘.
/remorsearch-ux-qa 깊게: 간편결제 실패 경험을 여러 채널에서 조사해 줘.
/remorsearch-ux-qa 근거 붙여서: 고령 사용자가 키오스크에서 겪는 어려움을 정리해 줘.
```

요청에 "간단히"가 있으면 가장 중요한 축만 돌립니다. "깊게"가 있으면 기본 축을 모두 돌립니다. "근거 붙여서"가 있으면 모든 주장에 출처 ID를 붙입니다. "간단히"가 다른 말과 함께 나오면 "간단히"를 따릅니다. 어느 경우에도 중단 규칙, 등급 규칙, 확인 표시는 그대로입니다([`overview.md`](skills/remorsearch-ux-qa/references/research/korea/overview.md) 4절).

에이전트는 제품에서 주요 과업과 질문을 찾고, 관련 프로젝트 문서와 접근 가능한 의도 기록을 확인합니다. 확인한 결정은 수정 후에도 항목별로 점검합니다. 필수 접근 정보가 없거나 중요한 결정이 충돌하는 부분만 질문하고, 가능한 작업은 계속합니다. 하위 에이전트는 필요할 때 사용하며 현재 세션의 모델을 그대로 씁니다. 모델을 직접 고르고 싶다고 말할 때만 묻습니다.

요청은 URL이나 저장소 하나로 충분합니다. 에이전트는 먼저 실제로 도달한 과업의 범위를 정한 기준 평가를 작성합니다. 이 평가만으로도 쓸모가 있습니다. 그다음 평가에서 나온 질문만 조사하고, 수정이 정당할 때만 고쳐서 다시 실행합니다. 선택 출처나 도구가 없으면 해당 결과만 제한됩니다. loop 패킷을 만들 때는 호스트가 관찰한 사실을 쓰고 기계적인 필드를 `@auto`로 표시합니다. `python3 scripts/ux_loop.py fill DRAFT.json --evidence-root EVIDENCE [--workspace PRODUCT] --out packet.json`는 해시, 다이제스트, 실행 연결과 수정 리비전만 계산합니다. 맥락, 의도, 권한, 결과, 심각도는 채우지 않으며 거부되거나 유효하지 않은 결과는 승인이 아닙니다. 통과한 과업은 그 과업만 보여 주며 제품 전체 준비 상태나 실제 사용자 이점의 측정이 아닙니다.

기본 조사 후보는 당근, 디시인사이드, 유튜브 댓글, X, 인스타그램, Threads(쓰레드)입니다. 관찰한 과업에 맞는 곳을 선택하며 매번 모두 수집하지는 않습니다. 현재 접근 가능성이나 수집 성공도 보장하지 않습니다. 후보 URL을 찾은 뒤 포함된 insane-search 방법을 사용하되 기존 접근·근거 규칙을 따릅니다. [실행 안내](skills/remorsearch-ux-qa/references/loop/product-improvement.md)에 제품 탐색부터 재검증까지의 절차와 plan·bundle·loop 명령을 정리했습니다.

## 근거 규칙

제품 UI QA는 실제 화면과 Figma 이미지를 열어 정렬·여백·타이포그래피·잘림·가림·디자인 일치 여부를 영역별로 기록합니다. 기존 loop 검사기는 관찰 근거가 없거나 통과 판정과 모순되면 거부하며, `pixel_diff`는 번들 PNG 디코더로 이미지 차이를 직접 계산합니다. 화면의 의미와 품질은 호스트의 이미지 판독 도구를 사용하는 검토자가 판단합니다. 기록 검증만으로 그 판단의 정확성까지 보장하지는 않습니다.

- 모든 진술에 `observed`(관찰됨), `inferred`(추론), `unknown`(미확인) 가운데 하나를 붙입니다. 같은 말이 반복된다고 추론이 사실이 되지는 않습니다.
- 합성 페르소나와 시뮬레이션한 프로필은 테스트 상황을 만듭니다. 실제 사용자의 선호, 비율, 불편을 보여 주지 않습니다.
- 커뮤니티 신호는 실제 제품에서 그 행동을 확인하기 전까지 가설입니다.
- 조사·리뷰 요청은 읽기 전용입니다. 개선 요청에는 지정 범위의 통상적이고 되돌릴 수 있는 수정 권한이 포함됩니다. 에이전트는 이 권한을 CLI에 기록하며 같은 승인을 다시 묻지 않습니다. 배포, 외부 게시, 실제 계정 변경에는 별도 권한이 필요합니다.
- 화면 구성과 UX 변경은 Figma에서 먼저 만들고 실제 파일, 노드, 버전과 읽어 확인한 내용을 기록합니다. 접근할 수 없으면 해당 변경을 보류하고 가능한 조사와 QA를 계속합니다.
- 개선 완료에는 현재 빌드의 재실행, 인접 과업의 회귀 검사와 의도 보존 확인이 필요합니다. 정한 QA에서 재현 가능한 문제가 없으면 변경 없이 점검을 마칠 수 있습니다. 필수 근거가 없으면 미완료로 남깁니다.

UI QA는 과업 완료 여부와 별도로 컴포넌트 계약과 화면 구성을 확인합니다. 해부·토큰 역할·상태 변형·동작 위계·긴 문구·반응형 변화·아이콘 전용 조작의 발견 가능성을 컴포넌트·화면 매트릭스로 기록합니다. [UI 품질 카드](skills/remorsearch-ux-qa/references/persona-qa/ui-quality.md)는 REA로 참고 기능의 상태 전이·컴포넌트 경계·설계 이유를 역추적한 뒤 사용자의 Figma와 컴포넌트에 맞춰 구현하고 다시 실행하는 흐름을 제공합니다. REA는 선택형이며 설치본에 포함하지 않습니다. 결함 판정은 현지 Figma·의도·실제 화면 근거로 합니다.

조사와 QA 실행은 기계가 읽을 수 있는 **증거 번들**(evidence bundle, `schemas/ux-evidence-bundle.v1.schema.json`)을 주고받을 수 있습니다. 오프라인 검증기가 ID, 상호 참조, 권한 기록, 합성 페르소나 오용, 근거 없는 "검증됨" 발견, 지난 보관 기한을 확인합니다. 스킬에 작은 유효 번들 예시가 들어 있어 검증기를 바로 시험해 볼 수 있습니다.

```sh
python3 ~/.claude/skills/remorsearch-ux-qa/scripts/validate_bundle.py bundle.json
python3 ~/.claude/skills/remorsearch-ux-qa/scripts/validate_bundle.py ~/.claude/skills/remorsearch-ux-qa/examples/bundle/minimal.json
```

## 공개 페이지 읽기

research와 persona-qa는 계정 없이 누구나 읽을 수 있는 것만 읽습니다.

- **도구.** 스킬은 에이전트 호스트에 있는 가장 좋은 브라우저 도구를 씁니다. 먼저 사용자 본인의 브라우저를 움직이는 에이전트 도구(Aside, Claude in Chrome, Claude 앱 내장 브라우저)를 찾고, 다음으로 자동화 브라우저(Playwright MCP, Chrome DevTools MCP, 함께 들어 있는 페이지 reader `read_page.mjs`)를, 그다음 스킬 자체 reader를, 마지막으로 일반 웹 검색과 가져오기를 씁니다. 마지막 도구의 결과는 단서일 뿐입니다. 함께 들어 있는 실시간 웹 드라이버는 제품을 테스트하는 도구이며 커뮤니티 페이지를 읽지 않습니다. 스킬은 출처마다 어떤 도구로 읽었는지 기록합니다.
- **reader**(`scripts/ux_research.py`)는 거부 신호가 없을 때 공식 피드나 API, 정직하게 밝힌 요청 한 번, 사이트가 내놓은 모바일·피드 판, 실제 브라우저 렌더 순서로 읽습니다. 거절 뒤에는 다음 경로로 넘어가지 않습니다.
- **중단.** 로그인, 유료 벽, 회원 전용 그룹, 나이 확인, 캡차 같은 사람 확인, 봇 차단과 "브라우저 확인 중" 화면, robots.txt와 AI·TDM 거부 표시, 속도 제한, 삭제된 글 앞에서 멈추고 수집 공백으로 보고합니다. 봇 차단(`bot_filter`)과 브라우저 확인 화면(`js_check`)은 `opted_out`이며 등록 도메인 전체를 이번 실행에서 멈춥니다. 확인 화면이 풀리기를 기다리거나 거절 뒤에 렌더하지 않습니다. robots.txt 자리에 확인 화면이 와도 같습니다. 확인 화면 표지가 있거나 `waited_ms`가 0보다 큰 캡처는 `ingest`가 받지 않습니다. 사람 확인과 속도 제한으로 사이트가 멈출 때도 등록 도메인 단위로 닫힙니다. 약관이나 공식 공지가 자동 수집·AI 이용을 제한한 곳(`terms_restricted`)에서도 멈추고, 사용자 요청으로 페이지를 여는 AI 에이전트 robots.txt 규칙도 따릅니다. 검색 결과 페이지는 읽지 않습니다. 호스트마다 한 번에 한 페이지를 기본 8초 이상 간격으로, 예산 안에서 읽습니다.
- **제3자 사본.** 아카이브, 번역·리더 프록시, AMP 캐시, 대체 프런트엔드는 `third_party_copy`로 거절합니다. 브리프가 허용한 제품 공식 페이지의 과거 웨이백 사본만 예외입니다.
- **개인정보.** 인용은 짧게 하고, 작성자는 솔트 키로 바꾸며, 임시 페이지 텍스트는 프로젝트 밖에 두었다가 실행을 닫을 때 지웁니다. 전화번호, 이메일 주소, 주민등록번호, 카드·계좌 번호, IP 주소는 에이전트가 보기 전에 지웁니다. 로그인해서 읽는 일은 실행마다 사용자가 승인한 커뮤니티에서만 하고 요약만 남깁니다.

자세한 내용은 [`public-page-access.md`](skills/remorsearch-ux-qa/references/research/public-page-access.md)(영문)에 있습니다.

## 한국어 리서치

한국 제품, 한국어를 쓰는 사용자, 한국어 보고서를 다룰 때 research 모드는 한국 리서치 팩도 함께 따릅니다. 시작 문서는 [`overview.md`](skills/remorsearch-ux-qa/references/research/korea/overview.md)입니다. persona-qa는 접근성 점검에 [`kwcag-2.2.md`](skills/remorsearch-ux-qa/references/persona-qa/kwcag-2.2.md)를 더합니다. 팩은 한국어로 쓰여 있고 다음을 더합니다.

- 한국 채널 27곳의 지도: 공개 범위, 정당한 읽기 경로, 예상되는 중단, 약관 상태
- 한국어 검색어 짜기와 사용자 언어 읽기(초성체, 비꼼, 말투)
- 협찬·광고 표시와 리뷰 보상 표지, 그에 따른 등급 규칙
- 한국 통계의 출처 카드와 모집단 틀
- 법령 점검표(법률 자문 아님)와 한국어 보고서 틀
- KWCAG 2.2와 WCAG 2.2를 따로 적는 접근성 결과

**약관 중단.** 자동 수집 제한이 있는 호스트와 짧은 주소는 요청 전에 멈춥니다. `reported`와 `confirmed`는 근거의 확인 수준을 나타냅니다. 해제 여부는 `lift_requires`로 정합니다. `never`는 풀 수 없고, `written_permission`은 사용자의 현행 약관 확인과 해당 읽기에 적용되는 사전 서면 허락이 필요합니다. `terms_check`는 사용자의 현행 약관 확인이 필요합니다. 에이전트는 사용자의 확인 기록을 쓰지 않습니다.

유튜브·인스타그램·스레드·페이스북·TikTok·클리앙·App Store·Hacker News 페이지는 `lift_requires: never`입니다. 디시인사이드·네이버·네이버 카페 공지·쿠팡·X·당근·Reddit은 `written_permission`에 따라 항목별 사용자 확인과 사전 서면 허락을 기록해야 풀립니다. 네이버 카페 공지의 원문 주소는 기록되어 있으며 이용약관과 공지를 각각 확인해야 합니다. URL에 걸린 제한은 각각 별도 확인으로 모두 풀어야 하며, 풀린 항목도 모든 호스트를 합쳐 실행당 문서 10건까지 읽습니다.

확인의 `host`는 항목의 호스트이거나 더 좁고 읽을 URL을 포함해야 합니다. `terms_url`은 항목에 등록된 약관 문서여야 합니다. `checked_on`은 `effective_from`이 있으면 그날부터 허용되며 오늘 기준 365일 이내여야 합니다. 미래 날짜는 허용하지 않습니다. 열린 실행의 명령마다 두 날짜 조건을 다시 확인하고, 만료되면 새 실행을 요구합니다. 이전 정책으로 만든 실행은 재개를 거부하며 저장된 파일을 고쳐 옮기지 않습니다.

유튜브는 공식 API만 씁니다. Hacker News 페이지는 멈추며 공식 API도 어댑터가 생기기 전까지 `official_route_unavailable`로 남습니다. X oEmbed 경로는 2026-09-30 무인증 요청에 HTML을 반환한 뒤 제거했습니다. 공식 폐지 공지는 확인하지 못했습니다. 팀 자기 앱의 리뷰는 App Store Connect에서 내보낸 자료를 `team_provided`로 받습니다. [항목과 확인 조건](skills/remorsearch-ux-qa/references/research/public-page-access.md#171-entries)을 따릅니다.

**유튜브 댓글**은 YouTube Data API로만 받습니다. 본인의 키를 환경 변수 `REMORSEARCH_YOUTUBE_API_KEY`에 두면 됩니다(`YOUTUBE_API_KEY`도 받습니다). 키는 환경 변수로만 읽고 파일에 두지 않습니다. 키가 없으면 수집 공백으로 적고 사용자에게 묻습니다. 페이지를 대신 읽지 않습니다. 키 보유자로서 사용자가 YouTube API Services Terms of Service와 Developer Policies를 따릅니다. 승인 없이 API Data로 새 데이터·파생 데이터·지표를 만드는 제한과 시청자 감정 분석·콘텐츠 분류 예시는 `미확인(요약)`이며 적용은 법률가 판단입니다. 그동안 API 항목은 정성 근거(풀어 쓰기, 짧은 인용의 존재 근거)로만 쓰고 감정·분류·개수 지표를 계산하지 않습니다.

[YouTube 개발자 정책 III.E.4.d](https://developers.google.com/youtube/terms/developer-policies)는 저장한 Non-Authorized Data를 30일 뒤 삭제하거나 갱신하도록 정합니다(관찰됨 2026-09-30). reader는 각 항목에 받은 시각에서 30일 뒤인 `retention_until`을 적고, 실행을 닫을 때 자기 페이지 텍스트를 지웁니다. 번들이나 보고서에 남긴 각 항목은 사용자가 그 보관 기한까지 삭제하거나 다시 받아야 합니다(`validate_bundle.py`가 지난 기한을 오류로 알립니다). 번들 항목을 자동으로 지우는 기능은 아직 없습니다.

**한계.** 네이버 글은 대부분 에이전트가 읽을 수 없습니다. [네이버 이용약관](https://policy.naver.com/rules/service.html)과 [2026-08-25 카페 공지](https://notice.naver.com/notices/cafe/33743)의 자동 수집 제한을 2026-10-01 원문에서 읽었습니다. 2026-08-31은 공지 보도일입니다. `lift_requires: written_permission`에 따라 사용자가 이용약관과 공지를 각각 확인하고 해당 읽기의 사전 서면 허락을 기록해야 합니다. 네이버·카카오 검색 API는 소유자가 현행 약관을 읽기 전까지 꺼 둡니다. 수집 공백은 팀 자체 자료(VOC, 고객센터 기록, 스토어·판매자 콘솔 내보내기), 다른 채널 계열, 설문, 인터뷰로 채웁니다. 직접 읽은 사실은 `관찰됨`, 원문에 닿지 못한 사실은 `미확인(...)`으로 구분했고, 사람이 읽기 전까지 `verified_at`은 null입니다.

## 저장소 구성

```text
skills/remorsearch-ux-qa/    설치하는 스킬(scripts/install.py가 설치함)
  SKILL.md                   진입점: 모드, 공통 규칙, 도구
  references/                모드별 흐름과 참고 문서
    research/korea/          한국 리서치 팩(한국어): 플랫폼 지도, 검색어, 표지, 통계, 법령 점검표, 보고서 틀
    persona-qa/kwcag-2.2.md  KWCAG 2.2와 WCAG 2.2 노트(한국어)
  scripts/                   CLI: validate_bundle, ux_loop, ux_research, ergo_qa, 벤치마크
  uxloop/ uxresearch/        loop CLI와 공개 페이지 reader의 Python 패키지
  ergoqa/ schemas/           인체공학 패키지와 CLI가 쓰는 JSON 스키마
  drivers/web/               실시간 Playwright 드라이버(Node.js)
  examples/loop/             loop CLI용 합성 시연 예제
tests/                       단위 테스트와 픽스처
benchmarks/                  정답이 있는 블라인드 벤치마크
docs/                        설계 노트, 인체공학 연구, 검증 기록
README.md, README.ko.md      이 문서의 영어판과 한국어판
```

## 개발

저장소를 내려받은 상태에서 실행합니다.

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py
(cd skills/remorsearch-ux-qa/drivers/web && npm install && node selftest.mjs)
python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/heldout-mixed --out .ergo-bench/heldout
```

loop CLI의 전체 설명(재개, 종료 코드, 신뢰 한계 포함)은 [`references/loop/cli.md`](skills/remorsearch-ux-qa/references/loop/cli.md)(영문)에 있습니다.

테스트는 네트워크에 나가지 않습니다. reader 테스트는 127.0.0.1의 로컬 서버에서 페이지를 내려 줍니다.

Python 3.10 이상과 고정된 웹 드라이버 의존성을 준비한 뒤 배포 패키지 전체를 검사합니다.
보고서에 각 테스트 결과를 남기고 ZIP을 다른 위치에 풀어 실행합니다. [배포 전 검사](docs/release.md)를 참고하세요.

```sh
python3 scripts/check_release.py --output dist/release-check
```

## 한계

[포트폴리오 비주얼 QA 재검증](docs/validation/visual-qa-20261017/report.md)에서 수정된 스킬은 원본 이미지의 잘림 6곳을 찾았고, 정상 대조 제목 3곳은 잘림으로 지적하지 않았습니다. 기존 스킬도 이미지를 실제로 본 실행에서는 같은 6곳을 찾았으므로 탐지율 향상으로 주장하지 않습니다. 별도 검토에서는 현재 웹 캡처 30장과 실제 Figma 내보내기를 대조해 디자인 차이를 찾고, 잘림·승인 여부·미실행 상호작용을 구분했습니다. 한 제품의 알려진 실패 사례를 재검증한 결과입니다.

[QA 성능 기준](PRD.md#91-일반-omo-대비-qa-성능)은 같은 모델·도구·과업·예산에서 일반 OMO와 Remorsearch를 적용한 OMO를 비교하는 것입니다. 모바일·데스크톱의 정렬·잘림·컴포넌트 가림을 필수로 확인합니다. [실제 OMO 비교와 모바일 QA](docs/validation/design-qa-20261015/report.md)에서 같은 접근 권한의 Astra medium은 유효 결함 5건·6건, 근거 부족 지적 1건·0건을 기록했습니다. 보고서 저장까지는 5분 7초·10분 8초였습니다. 앞선 접근 차이 실험은 별도로 보존했습니다. InferHub GLM 5.3 high는 공급자 오류로 QA 점수를 매기지 않았습니다. 소규모 결과로 일반적인 우위를 단정하지 않습니다.

[스킬 사용·미사용 비교](docs/validation/skill-ab-20261014/report.md)는 Codex에서 같은 모델과 브라우저 도구로 기존 로컬 평가 화면을 조건별 두 번씩 점검한 결과입니다. 탐지, 근거가 부족한 지적, 과업 완료, 시간과 토큰을 설치·자체 검사와 구분해 기록했습니다. 이 소규모 결과로 일반적인 성능 우위를 단정하지 않습니다.

[QA 속도 평가](docs/validation/qa-speed-20261015/report.md)에서는 GPT-6.1 Sol high로 기존 스킬과 지침 개선안을 두 번씩 비교했습니다. 개선안은 보고서 저장 중앙값이 4.1%, 최종 응답 중앙값이 1.5% 더 느렸습니다. 두 번째 반복은 핵심 6개 영역을 증거화했지만, 누락 소스 피드백 결함을 별도 발견 카드로 분류하지 않고 복구 관찰에 남겼습니다. 속도 향상과 분류 명확성을 얻지 못해 개선안은 채택하지 않았습니다.

- 실시간 브라우저 조사(Aside 같은 에이전트 브라우저), Figma, loop 모드의 브라우저 수집은 사용자나 에이전트 호스트가 제공합니다. loop CLI는 그 기록을 가져올 뿐 직접 실행하지 않습니다.
- reader는 robots.txt와 AI·TDM 거부 표시를 따르고 봇 차단과 브라우저 확인 화면에서 멈추므로 일부 사이트는 수집 공백으로 끝납니다. 렌더는 클릭하지 않으므로 긴 댓글 목록과 "리뷰 더 보기"는 일부만 읽습니다.
- 한국 플랫폼 상당수가 자동 수집을 제한하므로, 디시인사이드, 네이버, 쿠팡, X는 서면 허락과 함께 항목별 약관 확인을 기록하지 않으면 수집 공백으로 끝납니다. 유튜브는 본인의 키를 쓰는 API로만 읽습니다. 한국 팩은 법률 자문이 아닙니다.
- ergonomics 모드의 엄지 도달 모델은 보정되지 않았고, 벤치마크 세트는 작으며 에이전트가 만들었습니다. 결과는 인증이 아니라 선별용으로 봅니다. `docs/validation/`을 보십시오.
  [기존 별도 평가](docs/validation/experiments/heldout-2-results.md)에서는 정상 시나리오당 P0–P2 문제 단위가 1.75건으로 사전 기준 0.35건을 넘었고, 조건 식별 목표도 충족하지 못했습니다. 이후 수정만으로 이 목표를 통과했다고 볼 수 없습니다. 발견 항목은 실제 수정 전에 검토해야 합니다.
- 번들 웹 드라이버는 Chromium 기기 에뮬레이션만 실행합니다. Mobile Safari는 문서에 적힌 호스트 경로(iOS 시뮬레이터와 safaridriver)로 확인하고, iOS 네이티브 앱은 가져온 XCUITest 결과로 확인합니다. 실제 기기는 다루지 않습니다.

## 라이선스

MIT 라이선스입니다. [`LICENSE`](LICENSE)를 보십시오. 서드파티 자료와 참고 자료는 [`THIRD_PARTY_NOTICES.md`](skills/remorsearch-ux-qa/THIRD_PARTY_NOTICES.md)에 있습니다.

출처 표시: 공개 페이지 reader와 리서치 게이트는 fivetaku의 [insane-search](https://github.com/fivetaku/insane-search)와 [insane-research](https://github.com/fivetaku/insane-research)(둘 다 MIT)를 살펴본 뒤 설계했습니다. insane-search 원문과 참조 자료는 스킬 안에 포함되어 리서치 수집 단계에서 사용합니다. 원문, 파일 해시, 출처와 upstream 라이선스를 보존했습니다. insane-research는 게이트 설계의 아이디어만 참고했습니다. 한국 팩과 이중 언어 README 구성은 [K-skill](https://github.com/NomaDamas/k-skill)(MIT), DaleSeo의 [korean-skills](https://github.com/DaleSeo/korean-skills)(MIT), [SoDam-Persona-Codex](https://github.com/sodam-ai/SoDam-Persona-Codex)(Apache-2.0), fivetaku의 [gptaku_plugins](https://github.com/fivetaku/gptaku_plugins)(MIT)에서도 생각을 얻었습니다. 이 역시 생각만 참고했습니다. 플랫폼 이름은 설명을 위해 썼으며 어느 곳과도 제휴 관계가 없습니다.
