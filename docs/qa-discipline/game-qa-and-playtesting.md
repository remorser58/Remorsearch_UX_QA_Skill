# 게임 QA, 게임 접근성, 플레이테스트 실무 (Game QA, game accessibility and playtesting practice)

작성: 2026-09-28. 후보 ID 접두사: `GQA-`. 사용자 지시에 따라 본문은 한국어로 쓰고, 표준 이름·가이드라인 번호·필드 이름·원문 인용은 영어 그대로 둡니다.

> 상태: 작성 중. 1절(일부), 2.1절 완료. 재시작되면 이 파일을 먼저 읽고 끊긴 절부터 이어 씁니다.

**증거 태그.** [standard] 규범 문서 원문 · [paper] 동료 심사 논문, 원문 또는 저자가 공개한 논문 본문에서 확인 · [industry] 업체·기업 문서, 공개 소스 코드, 엔지니어링 블로그 · [report] 조사·정부 통계 · [snippet] 검색 발췌로만 봄(원문 미확인) · [derived] 내 계산 · [opinion] 실무자 의견(따로 밝히지 않으면 내 의견).

**이 문서와 기존 문서의 관계.** 게임 인체공학의 기초 자료는 이미 `docs/human-factors/game-ux-ergonomics.md`(이하 "게임 브리프")에 있습니다. 이 문서는 그것을 되풀이하지 않고, (1) 게임 브리프가 [R]·[V2]로 남긴 값 중 이번에 원문·소스 코드로 확인하거나 반박한 것, (2) 게임 QA 실무(인증, 플레이테스트, 자동 에이전트)에서 스킬 설계로 옮길 것, (3) GM-02~GM-06의 유지·삭제·변경·추가 판단과 그 실험 설계만 다룹니다. 다른 `qa-discipline` 문서의 후보(STF-, UEM-, AP-, LAT-, AUT-, SIT-)에 기대는 곳은 ID로 적습니다.

---

## 1. Scope and sources searched (범위와 검색한 자료)

### 1.1 질문

1. 게임 접근성 가이드라인(GAG, XAG 101–120, AbleGamers APX, The Last of Us Part II 옵션, Accessible Games Initiative 태그, CVAA)은 스킬이 브라우저 드라이버로 잴 수 있는 무엇을 요구하는가?
2. 광과민성: WCAG 2.3.1, ITU-R BT.1702, Ofcom, Trace 제안, EA IRIS는 무엇이 같고 무엇이 다른가? 화면 캡처 도구는 무엇을 잴 수 있고 무엇을 못 재는가?
3. 타이밍과 입력: QTE 수용 창, 연타 대안, 연령별 반응 시간, 입력 지연 예산, 리듬 게임 판정 창은 실제로 몇 ms인가?
4. HUD·글자·자막·안전 영역·모바일 터치 조작의 수치 기준은 무엇인가?
5. 게임 QA 실무(플랫폼 인증, 기능·규격·사용성 QA, RITE, 생체 신호, 텔레메트리, 자동 테스트 에이전트)는 결함을 얼마나 찾는가?
6. GM-02~GM-06을 각각 유지·삭제·변경·추가할 근거는 무엇이고, GM-06 연타 속도 스윕과 GM-03 수용 창 측정을 브라우저 드라이버로 어떻게 돌리는가?

### 1.2 검색 조건 (태그를 믿기 전에 읽을 것)

- 웹 검색은 30회 이하로 제한했습니다. 이 세션의 네트워크 정책이 `learn.microsoft.com`, `accessiblegames.com`, `supp.apa.org`, `frontiersin.org`, `ar5iv.labs.arxiv.org`, `jpattonassociates.com`, `static.mtv.co.uk`(Ofcom 문서 사본)을 막았습니다. 그래서 XAG 본문, Ofcom 패턴 규칙, Der & Deary 2006의 표, RITE 사례 수치는 검색 발췌([snippet])로만 봤습니다.
- GitHub 원본(raw)은 읽을 수 있었습니다. 그래서 **EA IRIS의 기본 설정 파일과 C++ 소스**, **W3C WCAG 저장소의 2.3.1 정의와 Understanding 원본**, **Trace Center의 PSE 제안 지침**, **Playwright Clock 문서 원본**, **Chrome DevTools Protocol 정의(pdl)**, **osu! 공식 위키 원본**, **StepMania 계열(OutFox) 설정 문서**는 원문으로 확인했습니다.
- W3C 문서는 `w3c/wcag`의 main 브랜치(편집 중 초안)에서 읽었으므로 권고안과 한 글자씩 대조하지는 않았습니다.

### 1.3 원문·소스로 직접 확인한 자료

- W3C, WCAG 2.x 용어 정의 "general flash and red flash thresholds" 원본. https://github.com/w3c/wcag/blob/main/guidelines/terms/20/general-flash-and-red-flash-thresholds.html [standard]
- W3C, Understanding SC 2.3.1 원본. https://github.com/w3c/wcag/blob/main/understanding/20/three-flashes-or-below-threshold.html [standard]
- Electronic Arts, IRIS 기본 설정 `config/appsettings.json`과 `src/TransitionTracker.cpp`, `src/Flash.cpp`, `src/FlashDetection.cpp`, `src/PatternDetection.cpp`. https://github.com/electronicarts/IRIS [industry]
- Trace RERC, `pseGuidelines.md`, `guidelinesFromPaper.md`(Jordan & Vanderheiden 2024, ACM TACCESS 논문의 지침 본문). https://github.com/traceRERC/pseGuidelines [paper]
- Microsoft Playwright, Clock 문서 원본 `docs/src/clock.md`. https://github.com/microsoft/playwright/blob/main/docs/src/clock.md [industry]
- Chrome DevTools Protocol, `HeadlessExperimental.pdl`(`beginFrame`). https://github.com/ChromeDevTools/devtools-protocol/blob/master/pdl/domains/HeadlessExperimental.pdl [industry]
- osu! 공식 위키 "Overall difficulty" 원본. https://github.com/ppy/osu-wiki/blob/master/wiki/Beatmap/Overall_difficulty/en.md [industry]
- Project OutFox(StepMania 계열) 설정 문서 `preferences.md`. https://github.com/TeamRizu/outfox-wiki [industry]

### 1.4 검색 발췌로만 본 자료 ([snippet])

(작성 중. 2.2절 이후에 채움.)

### 1.5 읽은 저장소 맥락 (수정하지 않음)

`skills/remorsearch-ux-qa/references/ergonomics/`의 `workflow.md`, `human-factors-checks.md`, `persona-agent-protocol.md`, `validation-and-limits.md`; `docs/ergonomic-swarm-spec.md` §0–§7; `docs/validation/experiments/decisions.md`; `docs/human-factors/game-ux-ergonomics.md`; `docs/qa-discipline/`의 기존 브리프 6편(목차와 게임 관련 부분); 코드 `ergoqa/checks.py`(GM-02, GM-03, GM-04, GM-05, GM-06, `_mash_bursts`, `_frame_flash`), `ergoqa/params.py`(게임 상수), `ergoqa/hf/game.py`(반응 시간 분위수, 연장 섬광), `drivers/web/session.mjs`와 `page_scripts.mjs`(타이밍 창 폴링, 섬광 표본). `benchmarks/`, `.ergo-bench/`, `.claude/`는 열지 않았습니다.

---

## 2. Key knowledge (핵심 지식)

### 2.1 광과민성: 섬광과 패턴

#### 2.1.1 규범 정의 (WCAG 2.3.1)

- **일반 섬광과 적색 섬광 기준.** 다음 중 하나면 통과: 어느 1초 동안에도 일반 섬광과 적색 섬광이 각각 3회 이하, 또는 동시에 일어나는 섬광의 합친 면적이 전형적 시청 거리에서 어떤 10° 시야 안에서도 0.006 sr(10° 시야의 25%) 이하. 일반 섬광은 "최대 상대 휘도(1.0)의 10% 이상인 상반된 변화 한 쌍이고, 어두운 쪽 상대 휘도가 0.80 미만"인 것입니다. [standard]
- **예외.** 한 변이 0.1° 미만인 "미세하고 균형 잡힌 패턴"(백색 잡음, 교대 체커보드)의 깜빡임은 기준을 어기지 않습니다. [standard]
- **10° 시야의 픽셀 근사.** 1024 × 768로 볼 때 341 × 256 px 사각형이 15–17인치 화면을 22–26인치에서 보는 10° 시야를 근사한다고 정의 문서가 적습니다. [standard]
- **적색 섬광의 새 정의(WCAG 2.2).** 한쪽 상태의 R/(R+G+B) ≥ 0.8이고, 두 상태의 CIE 1976 UCS 색도 차 √((u′₁−u′₂)² + (v′₁−v′₂)²)가 0.2보다 큰 상반된 전이 한 쌍. Understanding은 sRGB → XYZ 행렬과 u′ = 4X/(X+15Y+3Z), v′ = 9Y/(X+15Y+3Z)를 그대로 적습니다. [standard]
- **HDR과 절대 휘도.** sRGB가 아닌 색 공간 콘텐츠는 가장 넓은 동적 범위 판으로 검사하고, 이때 일반 섬광은 "20 cd/m² 이상의 변화이며 어두운 쪽이 160 cd/m² 미만"(ITU-R BT.1702). 어두운 쪽이 160 cd/m² 이상이면 Michelson 대비 (L_high − L_low)/(L_high + L_low) ≥ 1/17. [standard]
- **분석 조건.** "사용자가 볼 수 있는 가장 큰 크기"로 분석합니다. 웹 페이지 안에서도, 전체 화면으로도 재생되는 동영상은 전체 화면에서 분석합니다. 반복 재생되는 짧은 클립(GIF)은 반복시키며 분석합니다. [standard]
- **CSS 픽셀 대체와 그 모호함.** Understanding 원본은 "원래의 픽셀 블록을 CSS 픽셀로 바꾸면 섬광의 합친 면적은 341 × 256 CSS px, 즉 87,296 CSS px²가 된다"고 적습니다. [standard] 그러나 정의는 "10° 시야의 25%"이므로 같은 사각형을 10° 시야로 보면 문턱은 25%인 21,824 CSS px²입니다. [derived] 두 해석은 4배 차이가 납니다. 스킬은 이 모호함을 피해 기기 픽셀 피치와 프로필 시청 거리로 0.006 sr을 직접 계산합니다(아래 2.1.5).
- **밝기와 시청 거리의 한계.** Understanding은 "명세는 사람이 실제로 고르는 시청 거리를 반영할 수 없다. 이상적인 거리보다 가까이 보는 사용자는 규범상 통과하는 섬광 면적에도 영향을 받는다. 확대·화면 돋보기 사용자도 같다"고 적습니다. [standard] 스킬의 프로필별 시청 거리 계산은 이 한계를 줄이는 방향입니다.

#### 2.1.2 방송 기준과 연구 제안 (ITU-R BT.1702, Ofcom, Harding 2005, Trace 2024)

- **Trace 제안 지침(Jordan & Vanderheiden 2024).** 어떤 1초 구간에도 기준을 넘는 휘도 전이 또는 적색 전이가 6회를 넘지 않아야 합니다(= 3회 섬광 초과 금지를 전이 수로 쓴 것). 전이는 66 ms 이내에 끝나야 하며, 66 ms보다 느린 변화는 섬광 전이가 아닙니다. 같은 방향 전이가 20 ms 이내면 같은 전이로 보고 면적을 더합니다(작업값). 앞선 가장자리가 15 ms 이하 간격인 65 Hz 이상의 섬광은 위험이 크게 줄어듭니다. [paper]
- **Trace의 면적 문턱 세 가지.** (a) 화면 크기와 시청 거리를 알 때: 10° 시야의 0.006 sr(25%). (b) 크기를 모르는 TV 전용 콘텐츠: 화면의 25%. (c) 종류·크기를 모르는 화면: 0.0213°짜리 CSS px 기준으로 어떤 416 × 416 px 부분 영역의 25%(= 43,264 CSS px²), 사용자 확대 없이 가장 큰 크기로 표시할 때. 기준 화면은 23인치 Full HD 모니터를 71.1 cm에서 보는 것입니다. Trace는 TV의 "화면 25%" 기준이 하위 호환 때문에 남았고, 현대 디스플레이와 선호 시청 거리에서는 위험이 더 크다고 적습니다. HDR은 200 cd/m²를 기준 백색으로 봅니다. [paper]
- **Ofcom과 Harding 2005(EFA 합의)의 패턴 규칙.** 뚜렷한 줄무늬가 어느 방향으로든 밝음–어둠 쌍 5개를 넘으면 잠재적으로 해로운 패턴입니다. 줄무늬 전체가 최소 예상 시청 거리에서 0.006 sr보다 큰 입체각을 차지하고, 가장 밝은 줄의 휘도가 50 cd/m²를 넘고, 0.5초 이상 보이면, 줄무늬가 방향을 바꾸거나 진동·섬광·대비 반전할 때 밝음–어둠 쌍은 5개 이하여야 합니다. Ofcom은 정지한 줄무늬가 화면의 40%를 넘거나, 방향 변화·진동·섬광·대비 반전하는 줄무늬가 화면의 25%를 차지하면 허용하지 않습니다. Ofcom은 또 개별 기준 아래여도 5초에 걸친 섬광 연쇄의 누적 효과를 경고합니다. [snippet]
- **ITU-R BT.1702의 절대 휘도형 정의**(20 cd/m², 어두운 쪽 160 cd/m² 미만)는 WCAG Understanding이 인용한 문장으로만 확인했습니다. [standard, WCAG를 통해 간접]

#### 2.1.3 EA IRIS가 실제로 하는 일 (기본 설정과 소스 코드) [industry]

게임 브리프는 IRIS를 README 수준으로만 요약했습니다. 소스를 읽으면 스킬의 "IRIS와 같다"는 표현 몇 곳이 맞지 않습니다.

| 항목 | IRIS 기본값·동작 (근거 파일) | 스킬(GM-04) 현재 동작 | 차이의 의미 |
| --- | --- | --- | --- |
| 휘도 전이 | 상대 휘도 변화 0.1, 어두운 쪽 0.8 미만 (`appsettings.json`: `RelativeLuminanceFlashThreshold` 0.1, `RelativeDarkLuminanceThreshold` 0.8) | 같은 값, 블록별 | 같음 |
| 적색 전이 | `RedSaturation.FlashThreshold` 20, `RedDarkThreshold` 321(적색에는 어두운 쪽 조건을 사실상 끔) | 선형 RGB에서 (R−G−B)×320 > 20인 블록 비율 10% 이동 | 정의 계열은 같음. WCAG 2.2의 u′v′ 0.2 정의와는 둘 다 다름 |
| 면적 | `FlashDetection.AreaProportion` 0.25 = **프레임 전체 픽셀의 25%**. `Flash::CheckSafeArea`가 "조금이라도 바뀐 픽셀" 수(`countNonZero`)를 세어 25%를 넘을 때만 프레임 평균 휘도 차를 봄 | 블록 격자, 10° 시야(0.006 sr) 안의 동시 섬광 면적 합 | IRIS 기본 설정은 방송식 "화면 25%" 규칙이고, 전체 프레임 평균을 쓰므로 국소 섬광과 역위상 섬광을 놓칩니다. 스킬 쪽이 더 엄격하고 민감합니다 |
| 전이 누적 | `Flash::CheckTransition`: 같은 부호 평균 변화를 최근 1초 안에서 누적해 절댓값이 0.1을 넘으면 전이 1회(단조 구간당 1회) | 블록별 상반 변화 | IRIS에는 Trace의 "66 ms 이내" 조건이 없습니다. 느린 페이드도 1초 안에서 누적되면 전이가 됩니다 |
| 실패 | 최근 1초 전이 수 > `MaxTransitions` 6 → `FlashFail` | 1초 창 전이 7회 이상 → P0 | 같음 |
| 연장 실패 | `TransitionTracker::EvaluateFrameMoment`: 최근 5초 창(`ExtendedFailWindow` 5) 안에서 "1초 전이 수가 4–6인 프레임" 수가 4초 분량(`ExtendedFailSeconds` 4 × fps) 이상이고, 현재 1초 전이 수가 4 이상 → `ExtendedFail` | 5초 창 안에서 전이 20회(섬광 10회) 이상, 면적 초과 → P1 | **다른 규칙입니다.** IRIS는 "5초 중 4초 이상 초당 2–3회"를 보고, 스킬은 "5초에 섬광 10회"를 봅니다. 초당 2회가 4초 이어지면(섬광 8회) IRIS는 연장 실패, 스킬은 통과. 초당 3회가 3.4초 이어지면 스킬은 실패, IRIS는 통과 |
| 경고 | 1초 전이 수 ≥ `WarningTransitions` 4(초당 섬광 2회) → `PassWithWarning` | 없음 | 경고 단계가 없음 |
| 패턴 | `PatternDetection`: 50% 축소 → FFT 파워 스펙트럼 피크 → 역변환 → 윤곽선. 면적 ≥ 프레임의 25%, 줄 수(`nComponents`) ≥ `MinStripes` 6, 밝은 쪽 평균 휘도 ≥ 0.25, `TimeThreshold` 0.5초(= fps × 0.5 프레임) 지속이면 실패. **기본 설정에서 `PatternDetectionEnabled`: false** | 없음 | 패턴 규칙은 스킬에 없고, IRIS도 기본으로는 꺼져 있습니다 |
| 면책 | README: "IRIS is not intended to guarantee, certify or otherwise validate visual content's compliance with legal, regulatory or other requirements." | 보고서 문구: "인증 도구(EA IRIS/Harding)로 재검사가 필요합니다" | IRIS는 인증 도구가 아닙니다. IRIS 기본 설정의 통과가 스킬의 10° 시야 실패를 뒤집는 근거가 될 수 없습니다 |

#### 2.1.4 화면 캡처 도구가 잴 수 있는 것과 없는 것

- **짧은 섬광을 놓칠 확률.** 한 프레임(16.7 ms)짜리 밝은 상태를 무작위 위상의 순간 캡처로 잡을 확률은 캡처 간격에 대한 비율입니다. 20 fps 0.33, 24 fps 0.40, 30 fps 0.50, 60 fps(모든 프레임) 1.0. [derived] 드라이버 주석은 CDP 캡처가 약 24 fps라고 적습니다. 그러면 초당 4회의 한 프레임 섬광은 평균 초당 1.6회로 관측되어 통과합니다. [derived] 지터(`FLASH_JITTER_MS` 15)는 위상 고정을 깨지만 이 누락 확률은 줄이지 못합니다.
- **나이퀴스트 한계.** 표본 주파수 f_s로는 f_s/2 미만의 깜빡임만 주파수를 보존합니다. 24 fps에서 12 Hz 이상은 낮은 주파수로 접혀 들어옵니다. 스킬은 평균 20 fps 미만을 `inconclusive`로 처리합니다(`FLASH_MIN_FPS`). 이 규칙은 한 프레임 섬광의 누락은 다루지 못합니다. [derived]
- **결정적 전 프레임 캡처가 가능합니다.** CDP `HeadlessExperimental.beginFrame`은 "BeginFrame을 보내고 프레임이 완성되면 돌아오며, 결과 프레임의 스크린샷을 선택적으로 찍는다". `frameTimeTicks`와 `interval`(기본 16.666 ms)을 지정할 수 있습니다. 조건은 대상이 BeginFrameControl로 만들어지고 `--run-all-compositor-stages-before-draw`와 함께 쓰는 것입니다(헤드리스 전용 실험 도메인). [industry] 이 방식이면 기계 속도와 무관하게 60 Hz의 모든 프레임을 캡처할 수 있습니다. 실제 Playwright 번들 Chromium에서 되는지는 확인하지 않았습니다.
- **캔버스 게임은 페이지 안에서 매 프레임 읽을 수 있습니다.** WebGL/2D 캔버스 게임은 `requestAnimationFrame` 콜백이 끝난 직후 같은 작업 안에서 캔버스를 작은 2D 캔버스로 복사하면 게임 자신의 프레임률로 모든 프레임의 블록 휘도를 계산할 수 있습니다. [opinion, 파일럿 필요] `preserveDrawingBuffer: false`인 WebGL은 합성 뒤에는 버퍼가 비므로 같은 작업 안에서 읽어야 합니다. [opinion]
- **잴 수 없는 것.** 실제 디스플레이 휘도(cd/m²), HDR 톤 매핑, 사용자의 밝기 설정, 실제 시청 거리, 개인 감수성, 게임 안에서 우연히 겹치는 효과(멀티플레이 폭발 30개)의 완전한 도달. 절대 휘도 규칙(20 cd/m², 50 cd/m² 패턴 조건)은 기준 백색 200 cd/m² 가정으로만 환산할 수 있습니다. [derived, Trace의 200 cd/m² 가정 사용]

#### 2.1.5 스킬의 면적 문턱은 얼마인가 (휴대폰 예) [derived]

`ergoqa/devices.py`의 galaxy-s24(0.1833 mm/CSS px, 뷰포트 360 × 780)로 계산하면:

| 기준 | 문턱(CSS px²) | 뷰포트 대비 |
| --- | --- | --- |
| 0.006 sr, 시청 거리 250 mm | 11,160 | 4.0% |
| 0.006 sr, 300 mm (기기 기본값) | 16,071 | 5.7% |
| 0.006 sr, 400 mm | 28,571 | 10.2% |
| WCAG CSS 대체, 25% × 341 × 256 | 21,824 | 7.8% |
| WCAG Understanding 문장 그대로, 341 × 256 | 87,296 | 31.1% |
| Trace, 25% × 416 × 416 | 43,264 | 15.4% |
| IRIS 기본, 프레임의 25% | 70,200 | 25% |

휴대폰에서는 스킬의 기하 계산이 가장 엄격합니다. IRIS 기본 설정보다 약 4.4배 작은 면적에서 실패합니다. 따라서 "IRIS로 재확인"은 휴대폰에서 스킬의 P0를 거의 항상 뒤집는 쪽으로만 작동할 수 있고, 그것은 규범적으로 옳지 않습니다(WCAG는 10° 시야 기준). GQA-03에서 문구와 절차를 바꿉니다.

