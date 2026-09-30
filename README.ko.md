# Remorsearch UX QA

[English](README.md) | 한국어

**Research before release. No remorse after.** 출시 전에 조사하고, 출시 뒤에 후회하지 않습니다.

Remorsearch(리모서치, *ree-mor-search*) UX QA는 Claude Code와 Codex에서 쓰는 근거 중심 에이전트 스킬입니다. 실제 사용자가 하는 말을 조사하고, 페르소나로 실제 화면을 테스트하고, 인체공학과 접근성을 점검하고, 수정한 뒤에는 같은 시나리오를 다시 돌립니다. 관찰된 사실, 추론, 합성 페르소나를 끝까지 나누어 적으므로, 보고서가 시뮬레이션을 사용자 조사처럼 내세우는 일이 없습니다.

## 하는 일

스킬 하나에 모드가 넷 있습니다. 스킬이 요청을 보고 모드를 고릅니다.

| 모드 | 하는 일 | 필요한 것 |
| --- | --- | --- |
| **research** | 커뮤니티, 댓글, 앱 리뷰, 공식 자료에서 실제 사용자 경험을 모음. 직접 겪은 근거와 추론을 나누고, 근본 원인을 추적하고, Figma로 넘길 수 있는 흐름을 제안함. 사용자가 누구인지도 조사해 페르소나의 바탕이 되는 사용자 집단을 만듦 | 공개 페이지는 계정이 필요 없음. 유튜브 댓글은 본인의 YouTube Data API 키(`REMORSEARCH_YOUTUBE_API_KEY`)가 필요함 |
| **persona-qa** | 페르소나 시나리오를 만들어 브라우저에서 실제 제품으로 실행하고, Figma와 견주고, P0-P3 발견을 재현 절차와 근본 원인과 함께 보고함 | 실제 웹 화면은 Node.js 22와 Playwright가 필요함. Figma 파일은 선택임 |
| **ergonomics**(실험적) | 신체·감각 프로필(한 손·왼손 잡기, 엄지 도달, 손떨림, 걷는 중, 색각 이상, 노안)을 적용한 페르소나 에이전트가 실제 화면을 조작함. 같은 입력에 같은 값을 내는 인체공학 모델이 도달, 터치 정확도, 시선, 대비, 읽는 시간, 게임 타이밍, 번쩍임을 점수화함. 결과는 시뮬레이션한 프로필의 커버리지이며 유병률이 아님 | 실제 웹 화면은 Node.js 22와 Playwright가 필요함. 선별용으로만 씀 |
| **loop** | 조사와 QA를 한도가 있고 다시 이을 수 있는 목표로 묶음. 명시적으로 허락받은 수정, 같은 시나리오 재실행, 근거를 갖춘 종료 보고서 순서로 진행함 | 수정에 쓰기 권한을 따로 허락해야 함. 브라우저와 Figma 기록은 에이전트 호스트가 제공함 |

## 설치

폴더 하나를 스킬 폴더에 복사하면 됩니다.

```sh
git clone https://github.com/remorser58/Remorsearch_UX_QA_Skill.git
# Claude Code(개인용). 팀과 나누려면 프로젝트 안의 .claude/skills/에 복사합니다
cp -R Remorsearch_UX_QA_Skill/skills/remorsearch-ux-qa ~/.claude/skills/
# Codex
cp -R Remorsearch_UX_QA_Skill/skills/remorsearch-ux-qa ~/.codex/skills/
```

폴더에 스킬이 실행하는 모든 것이 들어 있습니다. Python 도구(3.10 이상, 표준 라이브러리만), JSON 스키마, 시연용 예제, 실시간 웹 드라이버입니다.

실제 웹 페이지에서 persona-qa와 ergonomics를 돌리는 실시간 웹 드라이버에는 Node.js 22와 Playwright도 필요합니다.

```sh
cd ~/.claude/skills/remorsearch-ux-qa/drivers/web
npm install && npx playwright install chromium
```

## 사용법

처음이어도 괜찮습니다. 평소 말투로 요청하거나, 스킬 이름을 불러서 시작하시면 됩니다.

```text
/remorsearch-ux-qa 우리 앱 결제 화면에서 사람들이 왜 이탈하는지 리뷰와 커뮤니티 글에서 찾아 줘.
/remorsearch-ux-qa 결제 화면을 처음 쓰는 사용자 페르소나로 QA해 줘. Figma 파일은 이거야.
/remorsearch-ux-qa 갤럭시 S24에서 가입 흐름을 한 손으로 쓰거나 색약이어도 문제없는지 점검해 줘.
/remorsearch-ux-qa 간단히: 배달앱 재주문이 불편한 이유를 앱 리뷰에서 찾아 줘.
/remorsearch-ux-qa 깊게: 간편결제 실패 경험을 여러 채널에서 조사해 줘.
/remorsearch-ux-qa 근거 붙여서: 고령 사용자가 키오스크에서 겪는 어려움을 정리해 줘.
```

요청에 "간단히"가 있으면 가장 중요한 축만 돌립니다. "깊게"가 있으면 기본 축을 모두 돌립니다. "근거 붙여서"가 있으면 모든 주장에 출처 ID를 붙입니다. "간단히"가 다른 말과 함께 나오면 "간단히"를 따릅니다. 어느 경우에도 중단 규칙, 등급 규칙, 확인 표시는 그대로입니다([`overview.md`](skills/remorsearch-ux-qa/references/research/korea/overview.md) 4절).

**처음 실행할 때.** 실행에 하위 에이전트(페르소나 에이전트, 병렬 조사, 심사 에이전트)가 필요하면, 스킬은 먼저 하네스에 이미 있는 하위 에이전트 모델 설정(`CLAUDE_CODE_SUBAGENT_MODEL`, 에이전트 정의, 플러그인 에이전트)을 찾아 묻지 않고 그대로 따릅니다. 설정이 없을 때만 호스트의 선택 창으로 모델과 추론 강도를 한 번 묻고, 답을 `~/.config/remorsearch-ux-qa/config.json`에 저장합니다. "에이전트 모델 바꿔줘"라고 말하면 다시 묻습니다. 권장 기본값인 Sonnet 최대 강도는 화면 11개로 한 블라인드 벤치마크에서 나왔습니다([`docs/validation/subagent-model-benchmark.md`](docs/validation/subagent-model-benchmark.md), 영문). Claude Code는 하위 에이전트의 추론 강도를 에이전트 정의로만 적용하므로, 스킬은 `~/.claude/agents/`에 작은 정의 두 개를 만들겠다고 제안합니다.

## 근거 규칙

- 모든 진술에 `observed`(관찰됨), `inferred`(추론), `unknown`(미확인) 가운데 하나를 붙입니다. 같은 말이 반복된다고 추론이 사실이 되지는 않습니다.
- 합성 페르소나와 시뮬레이션한 프로필은 테스트 상황을 만듭니다. 실제 사용자의 선호, 비율, 불편을 보여 주지 않습니다.
- 커뮤니티 신호는 실제 제품에서 그 행동을 확인하기 전까지 가설입니다.
- 기본은 읽기 전용입니다. 디자인, 테스트 데이터, 코드를 쓰려면 각각 명시적 허락이 필요합니다.
- Figma가 있으면 Figma가 디자인의 기준입니다.

조사와 QA 실행은 기계가 읽을 수 있는 **증거 번들**(evidence bundle, `schemas/ux-evidence-bundle.v1.schema.json`)을 주고받을 수 있습니다. 오프라인 검증기가 ID, 상호 참조, 권한 기록, 합성 페르소나 오용, 근거 없는 "검증됨" 발견을 확인합니다.

```sh
python3 ~/.claude/skills/remorsearch-ux-qa/scripts/validate_bundle.py bundle.json
```

## 공개 페이지 읽기

research와 persona-qa는 계정 없이 누구나 읽을 수 있는 것만 읽습니다.

- **도구.** 스킬은 에이전트 호스트에 있는 가장 좋은 브라우저 도구를 씁니다. 먼저 사용자 본인의 브라우저를 움직이는 에이전트 도구(Aside, Claude in Chrome, Claude 앱 내장 브라우저)를 찾고, 다음으로 자동화 브라우저(Playwright MCP, Chrome DevTools MCP, 함께 들어 있는 페이지 reader `read_page.mjs`)를, 그다음 스킬 자체 reader를, 마지막으로 일반 웹 검색과 가져오기를 씁니다. 마지막 도구의 결과는 단서일 뿐입니다. 함께 들어 있는 실시간 웹 드라이버는 제품을 테스트하는 도구이며 커뮤니티 페이지를 읽지 않습니다. 스킬은 출처마다 어떤 도구로 읽었는지 기록합니다.
- **reader**(`scripts/ux_research.py`)는 짧은 사다리를 필요한 만큼만 오릅니다. 공식 피드나 API, 정직하게 밝힌 요청 한 번, 사이트가 내놓은 모바일·피드 판, 실제 브라우저 렌더 순서입니다.
- **중단.** 로그인, 유료 벽, 회원 전용 그룹, 나이 확인, 캡차 같은 사람 확인, robots.txt와 AI·TDM 거부 표시, 속도 제한, 삭제된 글 앞에서 멈추고 각각 수집 공백으로 보고합니다. 플랫폼의 약관이나 공식 공지가 자동 수집이나 AI 이용을 제한한 곳(`terms_restricted`)에서도 멈추고, 사용자 요청으로 페이지를 여는 AI 에이전트를 향한 robots.txt 규칙도 따릅니다. 검색 결과 페이지는 읽지 않습니다. 정체를 숨기지 않으며, 호스트마다 한 번에 한 페이지를 기본 8초 이상 간격으로, 예산 안에서 읽습니다.
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

**약관 중단.** 플랫폼 약관이 자동 수집을 제한한 호스트에서는 reader가 요청을 보내기 전에 멈춥니다. 유튜브 페이지, 인스타그램, 스레드, 페이스북은 제한 조항을 찾은 항목(`confirmed`)이라 풀리지 않습니다. 디시인사이드, 네이버(카페 포함), 쿠팡은 보도와 인용으로 알려진 항목(`reported`)입니다. 사용자가 그 호스트의 현행 약관을 직접 읽고 결과를 브리프의 `access_policy.terms_checked`에 적은 실행에서만 풀립니다. 풀린 호스트도 실행당 문서 10건까지만 읽습니다. 에이전트는 이 항목을 쓰지 않습니다.

**유튜브 댓글**은 YouTube Data API로만 받습니다. 본인의 키를 환경 변수 `REMORSEARCH_YOUTUBE_API_KEY`에 두면 됩니다(`YOUTUBE_API_KEY`도 받습니다). 키는 환경 변수로만 읽고 파일에 두지 않습니다. 키가 없으면 수집 공백으로 적고 사용자에게 묻습니다. 페이지를 대신 읽지 않습니다. API로 받은 항목의 보관 기한(`retention_until`)은 받은 시각에서 30일 뒤이며, 기한이 지나면 지웁니다.

**한계.** 네이버 글은 대부분 에이전트가 읽을 수 없습니다. 보도와 인용에 따르면 네이버 약관과 2026-08-31 카페 공지가 자동 수집을 제한하고, 팩은 사용자가 약관 확인을 직접 기록하기 전까지 이를 중단으로 다룹니다. 네이버·카카오 검색 API는 소유자가 현행 약관을 읽기 전까지 꺼 둡니다. 수집 공백은 팀의 자체 자료(VOC, 고객센터 기록, 스토어·판매자 콘솔 내보내기), 다른 채널 계열, 설문, 인터뷰로 채웁니다. 팩의 플랫폼 사실은 대부분 검색 결과 요약으로 읽은 것이라 `미확인`으로 표시했습니다.

## 저장소 구성

```text
skills/remorsearch-ux-qa/    설치하는 스킬(이 폴더를 복사함)
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

## 한계

- 실시간 브라우저 조사(Aside 같은 에이전트 브라우저), Figma, loop 모드의 브라우저 수집은 사용자나 에이전트 호스트가 제공합니다. loop CLI는 그 기록을 가져올 뿐 직접 실행하지 않습니다.
- reader는 robots.txt와 AI·TDM 거부 표시를 따르므로 일부 호스트는 수집 공백으로 끝납니다. 렌더는 클릭하지 않으므로 긴 댓글 목록과 "리뷰 더 보기"는 일부만 읽습니다.
- 한국 플랫폼 상당수가 자동 수집을 제한하므로, 디시인사이드, 네이버, 쿠팡은 약관 확인을 기록하지 않으면 수집 공백으로 끝납니다. 유튜브는 본인의 키를 쓰는 API로만 읽습니다. 한국 팩은 법률 자문이 아닙니다.
- ergonomics 모드의 엄지 도달 모델은 보정되지 않았고, 벤치마크 세트는 작으며 에이전트가 만들었습니다. 결과는 인증이 아니라 선별용으로 봅니다. `docs/validation/`을 보십시오.
- 웹 드라이버가 다루는 것은 Chromium 기기 에뮬레이션뿐입니다. 실제 iOS Safari, 네이티브 앱, 실제 기기는 다루지 않습니다.

## 라이선스

MIT 라이선스입니다. [`LICENSE`](LICENSE)를 보십시오. 서드파티 자료와 참고 자료는 [`THIRD_PARTY_NOTICES.md`](skills/remorsearch-ux-qa/THIRD_PARTY_NOTICES.md)에 있습니다.

출처 표시: 공개 페이지 reader와 리서치 게이트는 fivetaku의 [insane-search](https://github.com/fivetaku/insane-search)와 [insane-research](https://github.com/fivetaku/insane-research)(둘 다 MIT)를 살펴본 뒤 설계했습니다. 생각만 참고했고 코드와 글은 옮기지 않았으며, 스킬은 두 프로젝트 어느 쪽에도 의존하거나 호출하지 않습니다. 한국 팩과 이중 언어 README 구성은 [K-skill](https://github.com/NomaDamas/k-skill)(MIT), DaleSeo의 [korean-skills](https://github.com/DaleSeo/korean-skills)(MIT), [SoDam-Persona-Codex](https://github.com/sodam-ai/SoDam-Persona-Codex)(Apache-2.0), fivetaku의 [gptaku_plugins](https://github.com/fivetaku/gptaku_plugins)(MIT)에서도 생각을 얻었습니다. 이 역시 생각만 참고했습니다. 플랫폼 이름은 설명을 위해 썼으며 어느 곳과도 제휴 관계가 없습니다.
