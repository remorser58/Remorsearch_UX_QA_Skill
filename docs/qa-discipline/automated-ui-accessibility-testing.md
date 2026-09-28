# 자동 UI·접근성 테스트: 규칙 엔진, 커버리지, 오탐 (Automated UI and accessibility testing)

작성: 2026-09-28. 후보 ID 접두사: `AUT-`. 사용자 지시에 따라 본문은 한국어로 쓰고, 표준 이름·규칙 ID·필드 이름·원문 인용은 영어 그대로 둡니다.

> 상태: 작성 중 (skeleton). 재시작되면 이 파일을 먼저 읽고 끝난 절은 다시 하지 않습니다.

## 1. Scope and sources searched (범위와 검색한 자료)

### 1.1 질문

1. 규칙 엔진(axe-core, Lighthouse, Android ATF, XCTest 감사, W3C ACT Rules)은 무엇을 어떤 알고리즘으로 검사하고, 공개된 탐지율과 오탐률은 얼마인가?
2. Playwright 드라이버에서 결정적으로(deterministic) 검사할 수 있는 WCAG 성공 기준은 무엇이고, 정확한 알고리즘은 무엇인가? (4.1.2, 2.4.3, 2.4.7, 2.4.11/2.4.12, 1.4.10, 1.4.4, 1.4.12, 2.5.8, 1.3.1, 3.3.1/3.3.3, 글자 잘림)
3. 어느 검사가 프로필과 무관하고(한 번만 보고), 어느 검사가 프로필에 따라 달라지는가(저시력 확대, 노안 글자 크기)?
4. 이미 구현된 SM-01~SM-06, LY-01 가운데 무엇을 유지·축소·삭제하고, 무엇을 axe-core에 맡기며, 무엇을 새로 더해야 하는가? axe-core를 페이지 안에서 호출할 때 MPL-2.0은 무엇을 요구하는가?

### 1.2 검색 조건 (태그를 믿기 전에 읽을 것)

- 웹 검색 17회, 원문 가져오기 약 30회. 이 세션의 네트워크 정책이 `w3.org`, `deque.com`, `webaim.org`, `dl.acm.org`, `arxiv.org`, `semanticscholar.org`, `zenodo.org`, `*.github.io`, 대학 저장소(`eprints.whiterose.ac.uk`, `ro.ecu.edu.au`), `philmcminn.com`, `businesswire.com`을 막았습니다.
- 그래서 W3C 규범 문서는 W3C가 GitHub에 둔 **원본 소스**(`w3c/wcag`, `w3c/accname`, `w3c/wcag-act`, `act-rules/act-rules.github.io`)로 읽었습니다. 이 원본에서 읽은 문장은 [standard]로 태그합니다. 편집 중인 main 브랜치일 수 있으므로 인용문은 권고안(Recommendation)과 한 글자씩 대조하지는 않았습니다.
- 논문 대부분(Vigo 2013, Chiou 2021/2024, Althomali 2019, Groundhog 2022)은 초록이나 검색 발췌만 봤습니다. 이런 수치는 [snippet]입니다.
- 이 저장소의 `benchmarks/`, `.ergo-bench/`, `.claude/`는 읽지 않았습니다. 드라이버와 검사 코드(`drivers/web/*.mjs`, `ergoqa/checks.py`)는 읽기만 했습니다.

### 1.3 원문을 직접 읽은 자료

| 자료 | URL | 확인한 내용 |
| --- | --- | --- |
| axe-core README | https://github.com/dequelabs/axe-core | "on average 57% of WCAG issues automatically", "zero false positives (bugs notwithstanding)", `incomplete`, MPL-2.0 |
| axe-core 4.13 규칙 목록 | https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md | 규칙 105개(비권장 5개 포함), 절별 개수, Issue Type, ACT 대응 |
| axe-core LICENSE와 `axe.min.js` 4.13.0 머리말 | https://github.com/dequelabs/axe-core/blob/develop/LICENSE , https://registry.npmjs.org/axe-core/-/axe-core-4.13.0.tgz | MPL-2.0 §1.7, §3.1–3.4; 파일 크기 |
| npm 메타데이터 | https://registry.npmjs.org/ | axe-core 4.13.0 MPL-2.0, @axe-core/playwright 4.13.0 MPL-2.0, accessibility-checker 4.0.34 Apache-2.0, @siteimprove/alfa-rules 0.119.0 MIT, html_codesniffer 2.5.1 BSD-3-Clause |
| axe-core 이슈 검색 ("false positive" in title) | https://github.com/dequelabs/axe-core/issues?q=is%3Aissue+%22false+positive%22+in%3Atitle | 오탐 보고가 몰리는 규칙 |
| Lighthouse 설정과 점수 문서 | https://github.com/GoogleChrome/lighthouse/blob/main/core/config/default-config.js , https://github.com/GoogleChrome/lighthouse/blob/main/docs/scoring.md | 접근성 감사 가중치, 수동 감사 10개 |
| GOV.UK 접근성 도구 감사 | https://github.com/alphagov/accessibility-tool-audit (README, `tests.json`, gh-pages `index.html`) | 장벽 142개 × 도구 13개, 도구별 탐지율, 2018-04-13 갱신 |
| WCAG 2.2 성공 기준 원문과 Understanding | https://github.com/w3c/wcag (`guidelines/sc/**`, `understanding/**`) | 1.3.1, 1.4.4, 1.4.10, 1.4.12, 2.4.3, 2.4.7, 2.4.11–2.4.13, 2.5.3, 2.5.8, 3.3.1–3.3.3, 4.1.2 |
| ACT 규칙 원본 | https://github.com/act-rules/act-rules.github.io/tree/develop/_rules | 59br37, oj04fd, b4f0c3, 2ee8b8, 36b590, e086e5, 97a4e1, 24afc2 |
| ACT 구현 판정 규칙 | https://github.com/act-rules/act-rules.github.io/blob/develop/pages/implementations/mapping.md | 예제 유형별 허용 결과, correct/partial 구현 정의 |
| ACT 1.0 CR 구현 보고 (2019) | https://github.com/w3c/wcag-act/blob/main/act-implementations.html | 초기 규칙 11개와 구현 도구 |
| accname 1.2 편집자 초안 | https://github.com/w3c/accname (gh-pages `index.html`) | 계산 단계(Hidden Not Referenced ~ Tooltip), CSS 생성 콘텐츠, shadow DOM |
| Chrome DevTools Protocol `Accessibility` | https://github.com/ChromeDevTools/devtools-protocol/blob/master/pdl/domains/Accessibility.pdl | `getFullAXTree`, `queryAXTree`, 이름 출처 유형, 속성 이름, 무시 사유 |
| Playwright 문서 | https://github.com/microsoft/playwright/blob/main/docs/src/accessibility-testing-js.md , `aria-snapshots.md` | `@axe-core/playwright` 권장, 면책 문구, ARIA snapshot |
| Android ATF 소스 | https://github.com/google/Accessibility-Test-Framework-for-Android (`framework/checks/*.java`) | 검사 14개, 48 dp와 가장자리 32 dp, 대비 허용오차 0.01, TextSizeCheck 오탐 경고 |
| Apple `XCUIAccessibilityAuditType` | https://developer.apple.com/documentation/xcuiautomation/xcuiaccessibilityaudittype (JSON) | 감사 유형 10개, iOS 17 / macOS 14부터 |
| WWDC23 세션 10035 | https://developer.apple.com/videos/play/wwdc2023/10035/ | 이슈 핸들러로 오탐 무시, "audits shouldn't substitute real testing" |
| KWCAG 2.2 (KS X OT0003:2022) | https://github.com/a11ykr/kwcag22 | 33개 검사항목, 6.1.2, 6.1.3(대각선 6.0 mm 권장), 6.5.3, 7.3.1, 7.3.2 |
| VISER README | https://github.com/redecheck/viser | 반응형 레이아웃 실패를 "보이는 것/보이지 않는 것"으로 분류 |

### 1.4 검색 발췌로만 본 자료 ([snippet])

- Deque, "Automated testing identifies 57 percent of digital accessibility issues" (2021): https://www.deque.com/blog/automated-testing-study-identifies-57-percent-of-digital-accessibility-issues/ , 보도자료 https://www.businesswire.com/news/home/20210310005156/en
- Vigo, Brown & Conway, "Benchmarking web accessibility evaluation tools: measuring the harm of sole reliance on automated tests", W4A 2013: https://dl.acm.org/doi/10.1145/2461121.2461124
- WebAIM Million 2026: https://webaim.org/projects/million/
- W3C ACT 구현 보고서(axe-core, Alfa, QualWeb, Equal Access): https://www.w3.org/WAI/standards-guidelines/act/implementations/
- Chiou, Winn, Alotaibi & Halfond, "Automatically Detecting Reflow Accessibility Issues in Responsive Web Pages", ICSE 2024: https://doi.org/10.1145/3597503.3639229
- Chiou, Alotaibi & Halfond, "Detecting and localizing keyboard accessibility failures in web applications" (KAFE), ESEC/FSE 2021: https://dx.doi.org/10.1145/3468264.3468581 ; 대화상자 키보드 실패, ICSE 2023: https://dl.acm.org/doi/abs/10.1109/ICSE48619.2023.00120
- Flow-A11y (2026): https://arxiv.org/abs/2607.03100 ; A11yLTLNav (2026): https://arxiv.org/pdf/2609.17959
- Althomali, Kapfhammer & McMinn, "Automatic visual verification of layout failures in responsively designed web pages", ICST 2019: https://www.gregorykapfhammer.com/research/papers/althomali2019/
- Salehnamadi, Mehralian & Malek, Groundhog, ASE 2022: https://dl.acm.org/doi/10.1145/3551349.3556905 ; TaskAudit (Groundhog 재평가): https://arxiv.org/html/2510.12972v1
- Adrian Roselli, "Honoring Mobile OS Text Size" (2026-02): http://adrianroselli.com/2026/02/honoring-mobile-os-text-size.html

### 1.5 읽은 저장소 맥락 (수정하지 않음)

`references/ergonomics/workflow.md`, `human-factors-checks.md`(SM-01~SM-06, LY-01 표), `persona-agent-protocol.md`, `validation-and-limits.md`, `docs/ergonomic-swarm-spec.md` §3·§5·§7·§12.1, `docs/validation/experiments/decisions.md`, `heldout-2-preregistration.md`(수정 1 포함), 기존 브리프 4개(UEM-, STF-, AP-, LAT- 후보), `drivers/web/page_scripts.mjs`(`accNameSrc`, `clippedOf`), `drivers/web/session.mjs`(`focusInfo`, `focusWalk`), `ergoqa/checks.py`(`check_semantics`, `check_focus_walks`).

**중요한 현황 차이.** 작업 지시문은 "semantics/layout 검사가 없다"고 적었지만, 저장소에는 이미 SM-01~SM-04와 LY-01(heldout-2 사전등록 수정 1), SM-05·SM-06(그 뒤 커밋 `962374f`, `50e05f7`)이 있습니다. 이 브리프는 새 검사를 제안하는 것과 함께 **이미 들어간 검사를 원문 기준으로 다시 검증**합니다. heldout-2는 아직 동결 전이고 기록되지 않았으므로, 동결 전에 바꿀 것과 동결 뒤 dev-2에서만 실험할 것을 3절에서 나눕니다.

## 2. Key knowledge (핵심 지식)

### 2.1 규칙 엔진과 규칙 집합

**axe-core (Deque, MPL-2.0).**

- README 원문: "With axe-core, you can find on average 57% of WCAG issues automatically. Additionally, axe-core will return elements as 'incomplete' where axe-core could not be certain, and manual review is needed." [industry]
- 설계 원칙(manifesto): "It returns zero false positives (bugs notwithstanding)." [industry] 즉 `violations`는 정밀도를 우선하고, 확신이 없는 경우는 `incomplete`(needs review)로 넘깁니다.
- 4.13 규칙 목록: 모두 105개입니다. WCAG 2.0 A/AA 60개, WCAG 2.1 A/AA 2개(`autocomplete-valid`, `avoid-inline-spacing`), WCAG 2.2 A/AA 1개(`target-size`), best practice 27개, AAA 3개, experimental 7개, deprecated 5개입니다. 56개가 ACT 규칙에 대응합니다. Issue Type은 failure만 42개, failure + needs review 52개, needs review만 11개입니다. [derived: `rule-descriptions.md` 표를 셈]
- 이 스킬과 겹치거나 인접한 규칙:
  - `button-name`(Critical), `link-name`(Serious), `label`(Critical), `select-name`, `input-button-name`, `aria-command-name`, `aria-input-field-name`, `aria-toggle-field-name`: 모두 4.1.2
  - `label-content-name-mismatch`: 2.5.3, **experimental**이라 기본으로 꺼져 있음
  - `meta-viewport`: 1.4.4, Moderate, ACT b4f0c3
  - `avoid-inline-spacing`: 1.4.12, ACT 24afc2·9e45ec·78fd32
  - `target-size`: 2.5.8, "failure, needs review"
  - `scrollable-region-focusable`: 2.1.1·2.1.3
  - `aria-hidden-focus`, `nested-interactive`: 4.1.2
  - `tabindex`(양수 tabindex, best practice), `focus-order-semantics`(experimental)
  - `image-alt`, `role-img-alt`, `svg-img-alt`, `input-image-alt`, `area-alt`: 1.1.1
  - `document-title`, `html-has-lang`, `html-lang-valid`, `list`, `listitem`, `td-headers-attr`, `th-has-data-cells`, `duplicate-id-aria`, `aria-valid-attr-value`, `aria-required-attr` 등
  [industry]
- **axe-core에 없는 것:** 4.13 목록의 어떤 규칙도 ACT 59br37(200 % 확대 시 잘린 글자), oj04fd(보이는 초점), 36b590(오류 메시지가 잘못된 값을 설명)에 대응하지 않습니다. 2.4.11(초점 가림)과 1.4.10(리플로) 규칙도 없습니다. [derived: 규칙 표에서 ACT ID 검색] 이 스킬이 드라이버로 직접 측정해야 하는 영역이 바로 이것입니다.

**Lighthouse (Google).**

- 접근성 점수는 감사 항목의 가중 평균입니다 (`docs/scoring.md`). [industry]
- `default-config.js`(main)의 접근성 범주에는 가중치가 있는 감사 66개(가중치 10이 18개, 7이 31개, 3이 5개, 1이 4개, 0이 8개)와 가중치 0인 **수동** 감사 10개가 있습니다. [derived]
- 수동 감사 10개: `focusable-controls`, `interactive-element-affordance`, `logical-tab-order`, `visual-order-follows-dom`, `focus-traps`, `managed-focus`, `use-landmarks`, `offscreen-content-hidden`, `custom-controls-labels`, `custom-controls-roles`. 초점 순서, 초점 관리, 키보드 함정은 Lighthouse가 자동으로 판정하지 않는다는 뜻입니다.
- 주요 가중치: `button-name`·`image-alt`·`label`·`meta-viewport` 10, `link-name`·`color-contrast`·`target-size`·`tabindex`·`document-title` 7, `heading-order` 3, `label-content-name-mismatch` 0(숨김). [derived]
- 범주 설명 원문: "Automatic detection can only detect a subset of issues and does not guarantee the accessibility of your web app, so manual testing is also encouraged." [industry]

**Android Accessibility Test Framework (ATF, Google).**

- 검사 클래스 14개: `ClassNameCheck`, `ClickableSpanCheck`, `DuplicateClickableBoundsCheck`, `DuplicateSpeakableTextCheck`, `EditableContentDescCheck`, `ImageContrastCheck`, `LinkPurposeUnclearCheck`, `RedundantDescriptionCheck`, `SpeakableTextPresentCheck`, `TextContrastCheck`, `TextSizeCheck`, `TouchTargetSizeCheck`, `TraversalOrderCheck`, `UnexposedTextCheck`. [industry: 소스 디렉터리]
- `TouchTargetSizeCheck`: 기본 48 × 48 dp, 화면 가장자리나 IME 안에서는 32 × 32 dp. `TouchDelegate`, 클릭 가능한 조상, 스크롤 가장자리(이 경우 `NOT_RUN`), 조상에 의한 잘림을 고려합니다. [industry: 소스 상수와 주석]
- `TextContrastCheck`: `CONTRAST_TOLERANCE = 0.01`. 계산 대비가 기준보다 0.01까지 낮아도 통과시키는 보호 대역입니다. STF-15의 guard band와 같은 발상입니다. [industry]
- `TextSizeCheck`는 정적 휴리스틱입니다. sp가 아닌 단위, 그리고 고정 크기 뷰나 컨테이너 안의 sp 글자를 찾습니다. 소스 주석 원문: "This check is not perfect and can produce false positive (FP) results." [industry] 글자를 실제로 키워 보는 동적 검사가 정밀도에서 유리하다는 근거입니다 (2.3의 1.4.4).
- `SpeakableTextPresentCheck`: "Does not check if the text makes sense." `DuplicateClickableBoundsCheck`: 자식과 경계가 같은 클릭 가능 컨테이너. `TraversalOrderCheck`: 개발자가 지정한 탐색 순서(traversalBefore/After)의 오류. `UnexposedTextCheck`: OCR로 찾은 글자가 접근성 서비스에 노출되지 않음 (개발 중). [industry]

**Apple XCTest `performAccessibilityAudit`.**

- `XCUIAccessibilityAuditType`: `action`, `all`, `contrast`, `dynamicType`, `elementDetection`, `hitRegion`, `parentChild`, `sufficientElementDescription`, `textClipped`, `trait`. 문서 메타데이터 기준 iOS 17.0, macOS 14.0부터입니다. 유형별 설명문은 공식 문서에 비어 있습니다. [industry]
- WWDC23 세션 10035 원문:
  - 감사 결과를 걸러 내는 클로저에 대해 "Perhaps the issue is a false positive or expected behavior. Accessibility audits makes it easy to ignore these kinds of issues."
  - "audits shouldn't substitute real testing with assistive technologies."
  - 데모에서 나온 이슈는 "Element has no description"과 "The label is not human-readable"(레이블이 `QUOTE_TEXTVIEW`)이었습니다.
  [industry]
- 스킬에 주는 시사점: 벤더도 오탐을 무시하는 경로를 API로 둡니다. 그리고 "사람이 읽을 수 없는 이름"(개발자 식별자)은 결정적으로 잡을 수 있는 이름 품질 결함입니다 (AUT-14).

**W3C ACT Rules.**

- 규칙은 적용 대상(Applicability), 기대(Expectation), 가정(Assumptions), 보조기술 지원(Accessibility Support), 그리고 사람이 쓴 예제(passed / failed / inapplicable)로 이루어집니다. [standard: ACT 규칙 원본]
- 구현이 맞는지는 예제로 판정합니다 (ACT CG "Mapping To Rule"):

  | 예제 유형 | 허용되는 결과 |
  | --- | --- |
  | Passed | `passed`, `cantTell`, `inapplicable` |
  | Failed | `failed`, `cantTell` |
  | Inapplicable | `inapplicable`, `cantTell`, `passed` |

  모든 예제에서 허용 결과를 내면 *correct implementation*입니다. passed·inapplicable은 모두 맞고 failed 일부만 잡으면 *partial implementation*입니다. [standard: W3C 커뮤니티 그룹 문서이며 W3C 권고안은 아님] 곧 **통과 예제를 하나라도 실패로 판정하면 일관된 구현이 아닙니다.** ACT의 판정 기준은 사실상 "예제에서 오탐 0"이라는 정밀도 계약입니다.
- 구현 보고서 수치 [snippet]:

  | 도구 (버전) | consistent WCAG 2 규칙 | consistent proposed 규칙 | partially consistent |
  | --- | --- | --- | --- |
  | axe-core 4.10.2 | 26 | 3 | WCAG 2 1개, proposed 11개 |
  | Alfa 0.108.2 | 29 | 4 | – |
  | QualWeb 3.0.0 | 29 | 7 | – |
  | Equal Access 3.1.42-rc.0 | 21 | 3 | – |

**WCAG-EM (평가 방법론).**

- 2.0 초안은 1.0을 바탕으로 합니다. [standard, draft]
- Step 3.2: 무작위 표본은 "**10% of the structured sample set**"입니다.
- Step 3.3: 완결된 프로세스(complete processes)를 포함합니다.
- Step 4.3: 무작위 표본에서 구조적 표본에 없던 *유형*의 콘텐츠나 결과가 나오면 안 됩니다. 나오면 구조적 표본이 대표성이 없다는 뜻입니다.
- Step 3의 고려 사항: "smaller sample sets may be required when evaluators have access to prior evaluation findings, including test results from manual and automated accessibility testing."
- 스킬에 대응시키면: 시나리오 실행은 "완결된 프로세스"이고, 페르소나 에이전트가 도달한 추가 화면은 "무작위 표본"의 역할을 할 수 있습니다 (AUT-17).

**KWCAG 2.2 (KS X OT0003:2022, 한국형 웹 콘텐츠 접근성 지침).**

- 검사항목은 33개입니다. 이 주제와 관련된 항목은 다음과 같습니다. [standard: a11ykr 공개본]
  - 5.4.3 텍스트 콘텐츠의 명도 대비: 4.5:1. 18pt 이상이나 14pt 굵은 글꼴은 3:1. "화면 확대가 가능한 콘텐츠"도 3:1까지 허용하는데, 이는 WCAG에 없는 예외입니다.
  - 6.1.2 초점 이동과 표시: "키보드에 의한 초점은 논리적으로 이동해야 하며, 시각적으로 구별할 수 있어야 한다." WCAG 2.4.3과 2.4.7을 한 항목에 묶었습니다.
  - 6.1.3 조작 가능: 대각선 길이 6.0 mm 이상을 권장("바람직하다")하고, 테두리 안쪽 1픽셀 여백을 권장합니다.
  - 6.5.3 레이블과 네임: WCAG 2.5.3에 해당합니다.
  - 7.3.1 오류 정정, 7.3.2 레이블 제공
- **KWCAG 2.2에는 WCAG 1.4.4(글자 크기 조절), 1.4.10(리플로), 1.4.12(글자 간격), 2.4.11(초점 가림)에 해당하는 검사항목이 없습니다.** [derived: 33개 항목 목록 대조] 따라서 한국 제품에서 이 검사들은 "품질인증 항목"이 아니라 "WCAG 2.2 AA 및 저시력 사용자 영향"으로 보고해야 합니다 (AUT-16).

### 2.2 커버리지, 오탐, 미탐에 관해 공개된 수치

**"자동 검사는 얼마나 찾는가"는 무엇을 세느냐에 따라 13 %에서 57 %까지 갈립니다.**

| 출처 | 분모 | 수치 | 태그 |
| --- | --- | --- | --- |
| Deque (2021) | 첫 감사 2,000건 이상, 13,000쪽 이상, 이슈 약 300,000건의 **이슈 건수** | axe로 57 %. 업계 통념은 20–30 %. Deque는 성공 기준 개수가 아니라 이슈 건수로 커버리지를 정의했습니다. | [snippet] |
| GOV.UK 도구 감사 (2018-04-13 갱신) | 일부러 넣은 **장벽 142개**, 도구 13개 | 온전히 탐지한 비율: 최고 40 %(SortSite), 최저 13 %(Nu Html Checker), aXe 29 %, Google ADT 17 %. 사람 확인 요청까지 넣으면 최고 50 %(FAE) | [industry] |
| 같은 감사 `tests.json` 재집계 | 장벽 142개 | 한 도구라도 오류·경고로 잡은 장벽 102개(72 %), 수동 확인 요청까지 124개(87 %), 어떤 도구도 표시하지 않은 장벽 18개 | [derived] |
| 같은 자료, 키보드·초점·확대·레이아웃·CSS 장벽 24개 | 24개 | 한 도구라도 8개. axe 1, Google ADT 1, WAVE 2, SortSite 2, Tenon 2, HTML_CodeSniffer 0 | [derived] |
| Vigo, Brown & Conway (W4A 2013) | 도구 6개, WCAG 2.0 | 성공 기준 커버리지 최대 50 %, 완전성(completeness) 14–38 %, 정확성(correctness)은 대체로 93 % 초과. 다만 완전성이 높은 도구는 66–71 %로 낮았습니다 (더 많이 잡으려다 오탐이 늘어남). | [snippet] |
| WebAIM Million 2026 | 홈페이지 100만 개, WAVE | 95.9 %가 자동 검출 가능한 WCAG 실패를 가짐(2025년 94.8 %). 쪽당 오류 56.1개(2025년 51개). 오류의 96 %가 여섯 범주: 낮은 대비 83.9 %, 대체 텍스트 없음 53.1 %, 입력 레이블 없음 51 %, 빈 링크 46.3 %, 빈 버튼 30.6 %, 문서 언어 없음 13.5 %. 낮은 대비는 쪽당 평균 34건 | [snippet] |

**GOV.UK 감사에서 13개 도구 중 어느 것도 잡지 못한 장벽.** 이 가운데 상당수가 이 스킬의 드라이버가 측정할 수 있는 것입니다. [derived: `tests.json`]

- "Focus not visible"
- "Focus order in wrong order"
- "Keyboard trap"
- "Wide page forces users to scroll horizontally"
- "Page zoom - boxes that don't expand with the text"
- "Inadequate line height used"
- "Error messages - no suggestion for corrections given"
- "Alert shows for a short time"
- 라이트박스 초점 문제 3개: 초점 이동 없음, 초점 유지 안 됨, ESC로 닫히지 않음

"Errors are not identified"는 1/13, "Keyboard focus is not indicated visually"는 3/13(axe는 못 잡음)이었습니다.

**정적 규칙 엔진의 오탐은 0이 아닙니다.**

- axe-core 이슈 가운데 제목에 "false positive"가 들어간 이슈가 적어도 11건입니다. [industry: GitHub 검색]
  - `scrollable-region-focusable` 여러 건
  - `aria-required-parent`
  - `label-content-name-mismatch`: "CJK / full-width punctuation is not removed". 한국어 UI에 직접 걸리는 문제입니다.
  - `p-as-heading`
  - `target-size`: 덮여 있는 input을 건너뛰지 않음
  - `link-in-text-block`
  - `color-contrast`: OKLCH 색
  - shadow DOM 목록
- 오탐은 휴리스틱 규칙(스크롤 영역, 구조, 실험 규칙)에 몰리고, 이름 규칙에는 드뭅니다. 2.4절 파일럿에서도 이름 규칙 오탐은 0이었습니다.

**모바일 스캐너와 상호작용 기반 도구** [snippet]:

- Groundhog(ASE 2022)는 보조기술로 앱을 조작하며 이슈를 찾습니다. Google Accessibility Scanner(ATF)와는 "no intersection between the type of issues each … detects"입니다.
- TaskAudit(2025)의 재평가에서 Groundhog는 기능 오류를 recall 25.6 %, precision 14.2 %로 찾았습니다. Locatability 표시의 73 %, Actionability 표시의 96 %가 오탐이었습니다.
- ScreenAudit(CHI 2025, LLM 기반)은 14개 화면에서 스크린리더 오류 커버리지 69.2 %를 보였고, 널리 쓰이는 검사기는 31.3 %였습니다 (전문가 6명 평가).
- 결론: 상호작용·판단 기반 탐지는 더 많이 찾지만 정밀도가 크게 떨어질 수 있습니다. 이 스킬이 에이전트 판단을 가설 등급에 두는 규칙(LAT-16, UEM-11)과 같은 방향입니다.

**레이아웃 실패 탐지의 오탐.**

- VISER README: 반응형 레이아웃 실패(요소 겹침, 컨테이너 넘침, 뷰포트 넘침)를 "visually observable / non-observable"로 분류하는 도구입니다. DOM 기하만으로 찾은 실패에는 **보이지 않는 실패**가 섞인다는 전제에서 출발합니다. [industry]
- 초록 발췌: ReDeCheck가 20쪽에서 보고한 117건을 VISER가 모두 자동 분류했고, 28건을 수동 분석과 다르게 분류했으며, 그중 3건은 오탐으로 올바르게 재분류했습니다. [snippet]
- 결론: 기하 기반 겹침·넘침 검사에는 **픽셀 확인 단계**가 필요합니다 (AUT-06, AUT-07).

**드라이버 기반 탐지 연구** [snippet, 수치는 확보하지 못함]:

- 키보드 접근성 실패 탐지 KAFE(FSE 2021): "high precision and recall"
- 대화상자 관련 키보드 탐색 실패(ICSE 2023)
- 반응형 리플로 접근성 이슈 자동 탐지(ICSE 2024): "among the most prevalent modern web accessibility issues"
- Flow-A11y(2026): 페이지 단위 스캐너는 대화상자 열림 시 초점 이동, 초점 가두기, 닫힘 시 초점 복귀를 검증할 수 없습니다. 시나리오를 실제 브라우저에서 실행하고 기준별 증거 묶음을 만듭니다.
- 이 스킬은 이미 실제 흐름을 실행하므로 같은 증거를 공짜에 가깝게 얻을 수 있습니다 (AUT-11).

### 2.3 Playwright 드라이버에서 결정적으로 검사할 수 있는 성공 기준과 알고리즘

아래 "필요한 데이터"는 드라이버가 이미 읽는 것(DOM, 계산된 스타일, 경계 상자, 스크린샷, 타이밍)과 새로 읽어야 하는 것(CDP 접근성 트리)을 구분합니다.

**(a) 4.1.2 Name, Role, Value: 접근 가능한 이름 계산.**

- 규범: "the name and role can be programmatically determined; states, properties, and values that can be set by the user can be programmatically set; and notification of changes to these items is available to user agents". [standard]
- accname 1.2의 계산 순서:
  1. Hidden Not Referenced: 숨은 노드라도 `aria-labelledby`로 직접 참조되면 포함
  2. LabelledBy
  3. Embedded Control: 레이블 안의 입력 칸은 그 값을 이름에 넣음
  4. AriaLabel
  5. Host Language Label: `label`, `alt`, SVG `title`. presentational이면 제외
  6. Name From Content: 이름을 내용에서 얻는 역할이나 참조된 노드일 때. CSS `::before`, `::after`, `::marker` 생성 글자와 shadow root·slot 자식을 포함
  7. Text Node
  8. Tooltip (`title`): "used only if nothing else, including subtree content, has provided results"
  [standard]
- 이 스킬의 `accNameSrc`는 이 순서를 단순화했습니다 (2.7). 구현 선택지는 넷입니다.
  1. **브라우저가 계산한 트리:** CDP `Accessibility.getFullAXTree`(experimental 도메인)
     - 노드마다 `role`, `name`, 이름 출처 `sources`를 줍니다. 출처 유형은 attribute, implicit, style, contents, placeholder, relatedElement이고, native 출처는 label, labelfor, labelwrapped, legend, figcaption, title, tablecaption 등입니다.
     - `ignored`와 그 사유(ariaHiddenElement, inertElement, notRendered, presentationalRole 등)를 줍니다.
     - 속성(focusable, focused, invalid, required, describedby, errormessage, labelledby, checked, expanded, pressed, modal 등)을 줍니다.
     - DOM 노드와는 `backendDOMNodeId`로 연결합니다.
     [industry: 프로토콜 정의]
  2. Playwright `locator.ariaSnapshot()`: 역할과 이름을 YAML로 줍니다. 편하지만 요소별 기하와 잇기 어렵습니다. [industry]
  3. axe-core 규칙 안의 이름 계산.
  4. 자체 JS(현재 방식).
- ACT 적용 범위: 이름 규칙(97a4e1 버튼, e086e5 입력 칸, c487ae 링크)은 **접근성 트리에 포함된** 요소에 적용하며, 화면에 보이는지를 따지지 않습니다. e086e5는 비활성 입력 칸에도 적용합니다 ("Several assistive technologies have a functionality to list all form fields on a page, including the `disabled` ones"). [standard: ACT CG]
- 정밀한 판정: 무시되지 않은(ignored가 아닌) AX 노드 가운데, 위젯 역할이거나 focusable인 노드의 이름이 공백을 제거하고 비어 있으면 실패입니다. 위젯 역할은 button, link, menuitem, tab, checkbox, radio, switch, textbox, searchbox, combobox, listbox, slider, spinbutton, treeitem입니다. 필요한 데이터: CDP AX 트리 + 기존 요소 상자.

**(b) 2.5.3 Label in Name.**

- 적용 대상: 이름을 내용에서 얻는 위젯 역할(button, checkbox, gridcell, link, menuitem, menuitemcheckbox, menuitemradio, option, radio, switch, tab, treeitem 등) 가운데 보이는 글자가 있고 `aria-label`/`aria-labelledby`를 가진 요소입니다. 약어나 철자 차이가 있으면 제외합니다. [standard: ACT 2ee8b8]
- 레이블 포함 판정 알고리즘:
  1. 괄호와 그 안의 글자를 지웁니다.
  2. 대소문자를 접고(case folding) NFKD로 정규화합니다.
  3. 글자(L)와 숫자(N)가 아닌 문자를 공백으로 바꿉니다.
  4. 그 언어의 단어 분리 규칙으로 나눕니다.
  5. 보이는 레이블의 토큰 목록이 이름 토큰 목록의 **연속 부분열**인지 봅니다.
  "보이는 내부 글자(visible inner text)"는 `innerText`와 다릅니다. 시각적으로 숨긴 글자는 빠집니다. [standard: ACT 용어 정의]
- 가정: 괄호 안은 무시해도 된다. 원문: "This assumption is almost always true in English… known to be often false in languages other than English". [standard]
- **한국어 위험** [derived]: 한국어는 조사가 붙은 어절 단위로 띄어 씁니다. 보이는 글자 "장바구니 담기"와 이름 "상품을 장바구니에 담기"는 토큰 "장바구니" ≠ "장바구니에"라서 ACT 알고리즘으로는 "포함되지 않음"입니다. 음성 제어가 실제로 실패하는지는 확인하지 못했습니다 (4절).

**(c) 1.3.1·3.3.2 레이블.**

- HTML의 이름 계산에서 입력 칸은 `label`이 없으면 `title`, `placeholder`를 마지막 출처로 씁니다. Chromium도 이름 출처로 `placeholder`를 보고합니다 (CDP `AXValueSourceType.placeholder`). [industry]
- 따라서 placeholder만 있는 칸은 ACT e086e5를 **통과**합니다 ("non-empty accessible name"). 이는 레이블 품질 문제(axe `label-title-only` best practice)이지 WCAG 이름 실패가 아닙니다. [derived]
- 현재 SM-03은 placeholder·title만 있는 칸을 경로 위에서 P2로 올리므로, WCAG 실패로 읽히지 않게 이름을 붙여야 합니다 (AUT-03).

**(d) 3.3.1·3.3.3 오류 식별과 제안.**

- ACT 36b590의 세 기대 [standard: ACT CG]:
  1. 오류 표시(텍스트, 비텍스트, 표현)가 어느 칸의 오류인지 식별하게 해 준다.
  2. 원인이나 고치는 법을 **보이는** 텍스트로 설명한다.
  3. 그 텍스트가 접근성 트리에 있거나 그 칸의 이름·설명에 들어 있다.
- 드라이버가 읽을 수 있는 신호: `aria-invalid="true"`, `aria-errormessage`(`aria-invalid`가 참일 때만 유효), `aria-describedby`, `:user-invalid`, `role=alert`·라이브 영역. SM-04가 이미 `invalid`, `user_invalid`, `described_by`, `error_message`를 기록합니다.
- 3.3.3(제안)을 결정적으로 판정할 방법은 좁습니다. GOV.UK 감사의 "no suggestion for corrections" 장벽은 13개 도구 모두 못 잡았습니다 [derived]. 에이전트 판단(`error_unclear`)에 맡깁니다.

**(e) 2.4.3 초점 순서.**

- Understanding 원문: "Since there may be several possible logical reading orders for the content, the focus order may match any of them." [standard] 시각 순서와 DOM 순서의 불일치만으로는 실패를 판정할 수 없습니다. Lighthouse도 `logical-tab-order`, `visual-order-follows-dom`을 수동 감사로 둡니다. [derived]
- 드라이버가 정밀하게 잡을 수 있는 하위 실패:
  - 양수 `tabindex` (axe `tabindex`)
  - `aria-hidden` 안의 초점 가능 요소 (axe `aria-hidden-focus`)
  - 동작 뒤 초점이 `body`로 사라짐
  - 모달이 열렸는데 초점이 안으로 들어가지 않음
  - Tab이 모달 밖으로 빠져나감
  - 모달이 닫힌 뒤 초점이 트리거로 돌아오지 않음
  - 크기 0이거나 투명하거나 화면 밖에 있는 요소에 초점이 멈춤
  GOV.UK 감사의 라이트박스 초점 장벽 세 개는 13개 도구 중 0–1개만 잡았습니다. [derived] 필요한 데이터: 단계마다 `document.activeElement`, `dialog[open]`·`[aria-modal=true]`, 초점 걷기 결과(이미 있음).

**(f) 2.4.7 보이는 초점과 2.4.13 초점 모양.**

- ACT oj04fd의 기대: "there is at least one device pixel inside the scrolling area of the viewport whose HSL color value is different when the element is focused from when it is not." [standard: ACT CG]
- 같은 규칙의 배경 설명: 2.4.7에는 크기나 거리 요구가 없으므로 "barely perceptible changes at the other end of the page"도 통과합니다. [standard]
- 2.4.13(AAA) 원문: 초점 표시 영역이 "at least as large as the area of a 2 CSS pixel thick perimeter of the unfocused component"이고, "a contrast ratio of at least 3:1 between the same pixels in the focused and unfocused states"여야 합니다. [standard]
- 결론: **2.4.7 실패로 셀 수 있는 것은 "뷰포트 어디에도 변화가 없다"뿐입니다.** 요소 주변의 작은 변화는 2.4.13 성격의 약한 표시로 따로 다뤄야 합니다. 현재 SM-05는 요소 상자 + 4 px 안에서 24/255 이상 바뀐 픽셀이 4개 미만이면 실패로 봅니다. 표시가 요소 옆에 따로 그려지면 오탐이 납니다 (2.4절 파일럿).

**(g) 2.4.11·2.4.12 초점이 가려지지 않음.**

- 2.4.11 원문: "the component is not entirely hidden due to author-created content".
- 주석 두 개:
  - "Content opened by the user may obscure the component receiving focus."
  - "If the user can reveal the focused component without advancing the keyboard focus, the component with focus is not considered visually hidden."
- Understanding: 초점을 완전히 가리는 쿠키 배너는 실패입니다. 배너를 모달로 만들거나 `scroll-padding`을 쓰면 통과합니다. 사용자 조치가 필요 없는 알림은 초점을 잃을 때 닫히면 됩니다.
[standard]
- 현재 SM-06은 fixed·sticky 층이 9개 표본점을 모두 덮으면 P2, 일부만 덮으면 P3(2.4.12, AAA)로 봅니다. 사용자가 연 층과, 초점을 옮기지 않고 닫을 수 있는 층(Esc)을 빼지 않습니다 (AUT-13).

**(h) 1.4.10 리플로.**

- 규범: 세로 스크롤 콘텐츠는 폭 320 CSS px, 가로 스크롤 콘텐츠는 높이 256 CSS px에서 두 방향 스크롤 없이 정보와 기능을 잃지 않아야 합니다. 두 방향 배치가 필요한 부분(지도, 도표, 비디오, 게임, 프레젠테이션, 데이터 표, 조작 중 계속 보여야 하는 도구 모음)은 예외입니다. "320 CSS pixels is equivalent to a starting viewport width of 1280 CSS pixels wide at 400% zoom." [standard]
- Understanding [standard]:
  - "Neither adjusting or relocating content is considered a loss of information or functionality, so long as users are still able to access the content."
  - 줄여 보여 주더라도 전체를 볼 방법이 있으면 괜찮습니다.
  - 확대하면 고정·sticky 콘텐츠가 초점을 가리기 쉽습니다.
- 알고리즘 (AUT-06):
  - 폭 320 CSS px, 높이 256 CSS px, DPR 4로 에뮬레이트합니다 (데스크톱 1280 × 1024의 400 %).
  - RF-01: `document.scrollingElement.scrollWidth > clientWidth + 1`이면 오른쪽 끝이 뷰포트를 넘는 요소를 찾습니다. 예외 요소(`table`, `canvas`, `video`, `iframe`, `svg`, `pre`, 지도 역할), 그리고 자체 `overflow-x:auto|scroll` 컨테이너 안에 있는 요소는 제외합니다.
  - RF-02: 글자 잘림은 (l)의 ACT 방식으로 판정합니다.
  - RF-03: 인터랙티브 요소가 문서 스크롤 영역 밖에 있거나, fixed·sticky 층에 완전히 덮여 도달할 수 없음.
  - 겹침 후보는 VISER처럼 픽셀로 확인합니다. 겹친 상자 영역이 두 상태(겹침 해소 전후)에서 실제로 다르게 그려질 때만 셉니다.
  - 필요한 데이터: 추가 스냅숏 1장, 계산된 스타일, 경계 상자, 스크린샷.

**(i) 1.4.4 글자 크기 조절.**

- 규범: 캡션과 글자 이미지를 빼고 "text can be resized without assistive technology up to 200 percent without loss of content or functionality". [standard]
- Understanding: "Content satisfies the success criterion if it can be scaled up to 200% using at least one text scaling mechanism supported by user agents." [standard] 한 가지 메커니즘만 되면 됩니다.
- ACT 59br37 [standard: ACT CG]:
  - 640 × 512 뷰포트(1280 × 1024의 200 %)에서, `overflow: hidden|clip` 조상이 있는 보이는 텍스트 노드가 가로·세로로 잘리면 실패입니다.
  - 예외: 가로는 조상이 `white-space: nowrap`이고 `text-overflow`가 `clip`이 아니면(말줄임) 통과합니다. 세로는 조상의 line-height가 상자 높이 이상이면(한 줄 고정) 통과합니다.
  - 가정: 다른 크기 조절 수단이 있으면 실패가 SC 실패는 아닙니다.
- ACT b4f0c3(메타 뷰포트): `user-scalable=no`나 `maximum-scale` < 2는 실패입니다. 그러나 보조기술 지원 절 원문: "Desktop browsers ignore the viewport `meta` element, and most modern mobile browsers either ignore it by default or have an accessibility option which will allow zooming … Only users with older mobile browsers can experience issues tested by this rule." [standard: ACT CG] 확실하게 잡히지만 실제 영향은 제한적이므로 심각도는 낮게 둡니다 (AUT-08).
- 모바일 OS 글자 크기 (Roselli 2026) [industry·opinion]:
  - Android Firefox는 OS 글자 크기에 맞춰 웹 글자를 키웁니다.
  - Android Chrome은 OS 설정을 자동으로 따르지 않고 브라우저 안 설정을 써야 합니다.
  - Safari는 작성자가 `-apple-system-body` 같은 CSS를 쓰지 않으면 키우지 않습니다.
  - 앱 안 WebView는 "text inflation"으로 글자만 키우고 여백과 간격은 그대로 둡니다.
  따라서 모바일 프로필의 글자 확대는 "요소별 글자 크기 × s, 간격은 그대로"로 에뮬레이트하는 것이 WebView 동작에 가깝습니다. [derived]
- 정적 휴리스틱(ATF `TextSizeCheck`)은 오탐을 스스로 경고합니다. XCTest `dynamicType`은 실행 중에 검사합니다. [industry] 동적 방식이 낫습니다.

**(j) 1.4.12 글자 간격.**

- 규범 값 [standard]:
  - 줄 높이 ≥ 글자 크기의 1.5배
  - 문단 뒤 간격 ≥ 2배
  - 자간 ≥ 0.12배
  - 단어 간격 ≥ 0.16배
  이 속성을 쓰지 않는 언어·문자는 해당 속성만 빼고 적용합니다. Understanding에 따르면 일본어는 문단 뒤 간격을 쓰지 않습니다. 한국어는 띄어쓰기와 자간을 쓰므로 네 값이 모두 적용된다고 봅니다. [derived]
- Understanding: 글자가 겹치면 실패입니다. 말줄임표가 생겨도 전체 글자에 접근할 방법이 있으면 통과입니다. [standard]
- 정적 ACT 규칙(24afc2·78fd32·9e45ec)은 `style` 속성에 `!important`로 박힌 값이 기준보다 작은지만 봅니다. 사용자 스타일시트가 이길 수 없기 때문입니다. axe `avoid-inline-spacing`이 이를 구현합니다. [standard/industry]
- 동적 시험은 네 값을 주입한 뒤 잘림·겹침을 비교하는 방식입니다 (AUT-19). GOV.UK 감사의 "Inadequate line height used"는 13개 도구 모두 못 잡았습니다. [derived]

**(k) 2.5.8 대상 크기(최소).**

- 규범 [standard]: 24 × 24 CSS px 이상이어야 합니다. 예외는 다섯 가지입니다.
  - Spacing: "a 24 CSS pixel diameter circle is centered on the bounding box of each, the circles do not intersect another target or the circle for another undersized target"
  - Equivalent
  - Inline
  - User Agent Control
  - Essential
- 이 스킬의 PT-01이 이미 레이블까지 넓힌 대상과 원 예외를 구현합니다. axe `target-size`는 "failure, needs review"이고, "덮인 input을 건너뛰지 않는" 오탐 이슈가 있습니다. [industry] 새로 구현하지 않습니다 (AUT-18).

**(l) 글자 잘림과 말줄임.**

- ACT 59br37 정의: 텍스트 노드의 flat-tree 조상 가운데 `overflow-x|y`가 `hidden|clip`인 것들을 모두 `visible`로 바꾸면 더 많이 보이게 되는 경우를 "clipped by overflow"라고 합니다. [standard]
- 현재 LY-01은 **자기 상자**의 `scrollWidth > clientWidth + 1`만 봅니다. 조상에 잘리는 경우를 놓치고, ACT가 통과시키는 말줄임과 한 줄 고정을 잡습니다 (2.4절).
- XCTest에는 `textClipped` 감사 유형이 있습니다. [industry]
- "전체 내용에 접근할 수 있는지"(1.4.10·1.4.12의 Understanding)는 결정적으로 일부만 확인할 수 있습니다. 같은 글자가 `title`, `aria-label`, 연결된 상세 링크, 펼치기 버튼에 있는지 봅니다. 없으면 `truncated_without_alternative`로 기록합니다 (AUT-05).

## 3. Implications for the skill (스킬에 주는 시사점)

(작성 중)

## 4. Risks, open questions and what could not be verified (위험, 열린 질문, 확인하지 못한 것)

(작성 중)
