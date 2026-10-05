# Remorsearch 스킬 완성도 감사와 개선

기준일: 2026-10-05. **평가 대상은 Remorsearch UX QA**이며 OmO Native와 OMO Wish는 비교 표본이다. 연동, 기능 복제, 호스트 교체를 제안하거나 구현하지 않는다. 기존 접근·개인정보·Figma·의도 보존 규칙을 유지한다. 이번 전달 경계는 검토 가능한 PR이며 병합·배포·실사용 완료 인증이 아니다.

## 1. 결론

Remorsearch는 단순한 프롬프트 모음이 아니다. 단일 요청 진입, 설치 가능한 패키지, 출처·권한·의도 계약, 실제 근거 검증기, 수정·재검증 CLI, 합성·held-out 실험이 이미 있다. 특히 합성 페르소나를 실제 사용자로 오인하지 않고 접근 차단과 미검증을 결과에 남기는 부분은 유지할 강점이다. 다만 **패키지 테스트가 통과했다는 사실만으로 한 번의 요청이 검증된 제품 개선까지 이어지는 스킬이라고 확정할 수 없다**.[R1][R2][R3]

현재 증거로는 OMO와의 동등한 성능도, 열등한 성능도 수치로 판정할 수 없다. 목적과 호스트가 다르고 동일 과업·조건의 대조 실험을 하지 않았다. 비교 가능한 것은 진입·완료·검증·복구·효율의 계약과 그 계약을 뒷받침하는 증거 수준이다. Native/Wish의 문서 역시 실행 성공률을 대신하지 않는다.[N1][W1][W2]

이번 변경은 확인된 두 검증 결함을 수정하고 회귀 시험을 추가한다. 더 큰 공백인 실제 설치 호스트의 end-to-end 실행, 탐지 정확도, 사용자 개입량, 불필요한 재실행 비용은 아래의 별도 수용 기준으로 남긴다. 이 패치를 그 공백까지 해결한 것으로 표시하지 않는다.

## 2. 평가 스냅샷과 근거 수준

| 대상 | 고정 기준 | 실제 확인 범위 |
| --- | --- | --- |
| Remorsearch main | `232b7f51c489cd9ccfab81a004f0bec81284c30a` | 저장소 기본선 식별 |
| Remorsearch PR #3 | `6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b` | SKILL, 제품 개선 절차, 인계, 검증·JSON 코드, 기존 관련 시험, 배포 스크립트, CI 구성, 과거 held-out 보고서 |
| OmO Native | `b9463e692f93aa49bb10d306c0c6f1ade54f7840` | `ultrawork/SKILL.md` 1–200행의 목표·계층·실제 표면 QA·시나리오·발견 절차. 전체 Native 런타임 감사 아님 |
| OMO Wish | `1a4cff69915781274d794669e3746376b8016fb5` | Wish 진입 계약과 verification reference. 비교 목적이며 실제 Wish를 실행하지 않음 |

PR #3의 이전 구현 검증 보고서는 Python 1,024개 실행(1개 skip 후 별도 캡처 검증), 웹 드라이버 559개, 설치본 smoke 18개를 기록한다. 이번 검토에서 그 전체 실행을 로컬로 반복한 것은 아니다. 해당 head의 GitHub Actions `37156736179`는 조회 시 성공이었다. 이 수치를 합쳐 독립적인 사용자 과업 성공 횟수로 계산하지 않는다.[R3][R4]

실제 UniClub C001은 화면 기록 권한 문제로 미실행이다. C002의 실제 브라우저 입력은 합성 부정 시나리오이고 두 과업의 실패를 제대로 남긴 근거이지 제품 개선 성공의 근거가 아니다. 기존 기록의 `23/23 done`에는 차단·종속 항목 5개의 `dropped`가 포함돼 있다. 닫힌 항목 수와 달성한 성공 기준 수는 다르다.[R3]

## 3. 기능 수 대신 완성도로 비교

| 평가 축 | Native / Wish에서 확인한 기준 | Remorsearch의 현재 근거와 판단 |
| --- | --- | --- |
| 진입 부담 | Native는 조사 후 작업 규모와 미결정을 분류한다. Wish는 명시적 호출 후 정해진 단계로 진행한다. | URL/저장소만으로 호스트가 시작하며 브리프·페르소나·모델 선택을 사용자에게 떠넘기지 않는다. 좋은 계약이나 새 세션에서의 자동 채택 성공률은 별도 검증 필요. |
| 목표와 의도 | 원래 목적, 이상적 종료 상태, 관찰 가능한 성공 기준을 먼저 고정한다. | 실제 결정·기억·Figma를 읽고 의도 보존을 요구한다. 코드만 보고 의도를 만들지 않는 점은 강점. 목표별 실제 재현 결과가 필요하다. |
| 행동 검증 | Native는 실제 표면의 명령·입력·이진 관찰 기준을 요구한다. Wish는 통합 QA와 테스트를 구분한다. | build/scenario/시각/아티팩트 결합은 구체적이다. 그러나 스크린샷의 PNG 겉구조만 확인하는 결함이 있어 이번에 수정한다. |
| 완료 판단 | 응답·초록 테스트·작업 종료를 사용자 결과와 구별한다. | task success, product readiness, measured benefit를 구분하는 명세는 있다. 실사용 성공 경로의 반복 증거가 부족하므로 완성품 주장은 보류해야 한다. |
| 범위와 권한 | Wish는 본래 목적의 실패·새 회귀·무효 근거와 별도 개선 과제를 구분한다. | 한정된 수정 권한, 출처 제한, 선택적 공백 처리, 의도 충돌 기준이 있다. OMO의 자동 병합 권한이나 전용 도구 요구를 가져올 필요가 없다. |
| 수정 효율 | Wish는 대상의 파일·의존성·환경이 바뀌지 않았다는 근거가 있을 때만 이전 증거를 재사용한다. | 현재 범위의 새 build replay는 유지해야 한다. 안전한 재사용을 제품화하려면 의존 입력과 환경 fingerprint를 먼저 기록해야 하며, revision 문자열만으로 재사용해서는 안 된다. |
| 리뷰 | Wish는 새 수정에 새로운 reviewer의 delta 검토를 요구한다. | P0/P1 second pass와 근거 규칙은 있으나 PR #3 최종 검토는 미실행 기록이다. reviewer 이름만 다른 것을 독립 검토로 세지 말아야 한다. |
| 설치·호스트 | Native/Wish는 특정 호스트 런타임·기본 스킬을 전제로 한다. | Remorsearch는 Python 표준 라이브러리와 선택적 드라이버로 분리되어 있다. 이식성에 유리한 구조지만 Claude/Codex 각 호스트의 실제 과업 수행 증거가 필요하다. |
| 탐지 실효성 | 읽은 Native/Wish 계약에서 Remorsearch와 동등한 UX 결함 데이터셋 결과는 확보하지 않았다. | 자체 held-out 결과는 존재한다. 그 결과의 실패·불확실성을 감추지 않고 다음 개선의 기준으로 삼아야 한다. |

표는 [R1][R2][R3][R5][N1][W1][W2]의 정적 대조다. 점수 합산, 승률, 비용 절감률 또는 기능 동등성을 산출한 실험이 아니다.

## 4. 이번에 재현하고 수정한 결함

### F1 · P1: 픽셀 스트림이 손상된 PNG를 근거 형식 검사에서 수용

위치: `skills/remorsearch-ux-qa/uxloop/evidence.py::Evidence.screenshot`.

원래 검사는 PNG 서명, IHDR 크기, 청크 CRC, IDAT 존재, 마지막 IEND를 확인했다. 그러나 IDAT 내부 압축 스트림을 읽지 않았다. `IDAT = b"not compressed pixels"`에 올바른 청크 CRC를 붙이면 통과했고, 픽셀은 출력되지만 zlib trailer가 잘린 스트림도 통과했다. 원본 파일은 Git blob `b00fe6af861534b5f4be4b873cf5f188e9a2ac30`과 일치시킨 뒤 해당 메서드를 격리 실행해 재현했다.[R5]

영향은 **잘못된 이미지 바이트에 대한 형식 게이트의 false acceptance**다. 이 실험만으로 전체 완료 게이트가 우회되거나 실제 캡처가 인증된다고 주장하지 않는다. 다른 출처·시간·시나리오·시각 검토 조건은 별도로 존재한다.

수정: 별도 표준 라이브러리 모듈 `uxloop/png_capture.py`에서 정적 PNG의 청크 구조, 합법적인 색상·샘플 필드, 팔레트·투명도 순서, 연속 IDAT, 정확히 종료한 zlib 스트림, scanline 길이와 filter byte를 확인한다. 16-bit와 Adam7을 단순히 거부하지 않는다. 파일 32 MiB, 5천만 픽셀, 확장 scanline 256 MiB의 고정 상한을 적용하며 초과하면 픽셀 압축을 풀기 전에 거부한다. APNG는 정적 캡처 근거로 받지 않는다.[P1]

이 모듈은 모든 ancillary metadata와 색 관리, 팔레트 인덱스의 픽셀별 유효성까지 해석하는 PNG 인증기가 아니다. 유효한 합성 이미지도 제작할 수 있으므로 포맷 통과가 진짜 브라우저 실행을 증명하지 않는다. 기존 SVG fixture 허용과 live SVG 거부, 아티팩트 해시, 시간, Figma와 replay 조건은 유지한다.

### F2 · P2: JSON 지수 overflow가 비유한 수 거부를 빠져나감

위치: `skills/remorsearch-ux-qa/uxloop/io.py::parse_json`.

`parse_constant`는 `NaN`/`Infinity` 토큰을 막지만 `1e999`가 Python float의 `inf`가 되는 경우는 처리하지 않았다. 원본 Git blob `d72aa458b001cbb3226055d8e0dbf9551ea8f3b5`에서 `parse_json('{"value":1e999}')`가 무한대를 반환하는 것을 재현했다. 이후의 일부 canonicalization이 실패할 수 있으므로 입력 경계에서 일관되게 거부하는 편이 맞다. 모든 숫자 스키마가 우회된다는 주장은 아니다.[R6][P2]

수정: `parse_float` callback에서 변환값에 `math.isfinite`를 적용한다. 양·음 overflow와 중첩 입력을 거부하고 정상적인 유한 수, JSON 정수, 음의 0, 기존 float underflow 동작은 유지한다. 중복 키·잘못된 문법·비표준 상수의 기존 거부도 유지한다.

## 5. 실제 시험과 아직 하지 않은 시험

추가한 `tests/test_verification_boundaries.py`는 33개 test method다. subtest 수를 별도 독립 시험 수로 부풀리지 않는다.

- PNG stream 경계 25개와 JSON 경계 3개: 부분 체크아웃에서 실제 실행, **28/28 통과**.
- 실제 `Evidence` import·artifact 읽기까지 연결하는 5개: 전체 체크아웃 CI 대상. 부분 체크아웃 전체 discover에서는 `uxloop.contracts` 미확보로 5개 import error가 발생했다. 이 실패를 skip이나 통과로 바꾸지 않았다.
- 원본/수정본 screenshot 메서드의 격리 대조: 위의 손상 IDAT 두 종류는 원본에서 수용, 수정본에서 `unknown` 거부; 정상 PNG는 양쪽 수용. 이것은 전체 의존성 통합 검사를 대신하지 않는다.
- 모든 추가·수정 Python 파일의 구문 분석 통과. 전체 제품 실행, 실제 디바이스, 실제 사용자 편익, OMO/Wish 비교 실행은 이번 로컬 시험의 범위가 아니다.

로컬 집중 실행:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python -m unittest -v \
  test_verification_boundaries.PNGStreamTests \
  test_verification_boundaries.JSONBoundaryTests
```

전체 체크아웃 재현:

```sh
python -m unittest discover -s tests -p 'test_verification_boundaries.py' -v
python -m unittest discover -s tests -p 'test_*.py'
python skills/remorsearch-ux-qa/scripts/smoke_loop.py
python skills/remorsearch-ux-qa/examples/research/run_fixture.py
python scripts/release_files.py
# 준비된 Node 22 / Playwright 환경에서:
(cd skills/remorsearch-ux-qa/drivers/web && node selftest.mjs)
```

원격 CI 결과는 이 PR의 정확한 head와 check run에 귀속시킨다. 이전 head의 성공을 새 head에 복사하지 않는다. 현재 GitHub workflow는 새 시험을 자동 수집하며 Linux/macOS, Python 3.10/3.12 및 별도의 Node 22 web-driver job을 실행한다.[R7]

## 6. 실효성에 관해 이미 드러난 공백

`heldout-2-results.md`는 이전 detector `0a4fd68`에 고정된 4개 합성 제품·48개 결함·16개 decoy·4개 정상 시나리오 실험이다. stratified C3는 27/48(0.562), measured-only C1은 11/48(0.229)의 strict recall을 기록했다. 그러나 확증 절차의 잡음 기준은 정상 시나리오당 P0–P2 항목 ≤0.35인데 실제 1.75로 실패해 이후 확증 순서가 중단됐다. 조건을 식별하는 H5도 실패했고, audience 구성이 중요한 결함에서 random보다 낫다는 가설은 입증되지 않았다.[R8]

이것은 숨길 결과도, 현재 전체 스킬의 정확도라고 일반화할 결과도 아니다. 이전 component 실험이다. 같은 데이터에 맞춰 임계값을 바꾸고 다시 held-out 성공이라고 부르면 검증력이 사라진다. 다음 detector 개선은 정상 control의 오탐과 조건별 원인 식별을 함께 줄이고, 공개되지 않은 새 과업으로 다시 평가해야 한다. 이번 PNG/JSON 수정이 UX 탐지 recall을 높였다는 주장은 하지 않는다.

## 7. 다음 개발 우선순위와 종료 조건

| 우선순위 | 개발 단위 | 통과에 필요한 증거 |
| --- | --- | --- |
| P0 · 완성품 주장 전 | 설치 호스트에서 한 요청 → baseline → 정당한 수정 → 현재 build replay를 완주 | 버전이 고정된 설치본, 실제 호스트 tool trace, 전후 build와 fixture, 수정 diff, 원래 과업·인접 회귀·의도 보존 결과. JSON 선언이나 `--help` 성공만으로 통과 금지. |
| P1 | false-positive / false-negative를 함께 관리하는 탐지 개선 | 미리 고정한 신규 held-out 과업, clean controls, defect recall·precision·조건별 성능, 실패 실행 포함 분모, 패턴별 실패 분석. 기존 실험 기준을 결과에 맞춰 완화하지 않음. |
| P1 | 필요한 공백만 막는 실패 복구 | Figma·optional source·host permission 각각의 실패를 주입. 영향 없는 QA는 진행하고 영향받는 수정은 중지. 반복 승인·기존 작업 중복 수행·오래된 증거 재사용이 없는 기록. |
| P1 | 실제 host 간 이식성 | Claude Code와 Codex의 새 세션에서 같은 자연어 입력을 각각 실행. 스킬 버전, 채택 경로, 설치 경로 독립성, 필요한 도구와 실제 산출물을 기록. 없는 도구를 있다고 가정하지 않음. |
| P2 | 근거를 훼손하지 않는 효율 개선 | 과업별 의존 파일/설정/환경 fingerprint. 무관한 문서 변경은 불필요한 replay를 만들지 않고 영향 변경/관계 불명은 다시 실행. 원래 provenance와 최종 현재-build 검사는 유지. |
| P2 | 배포 증거 재현성 | 원격 CI 로그·패키지 manifest·설치 smoke가 같은 소스에 묶인 재현 절차. private raw logs나 개인 로컬 경로가 없으면 아무도 재검증할 수 없는 형태는 개선. |

P0의 실제 UniClub 실행은 필요한 화면 기록 권한이 복구되어야 한다. 권한 거부를 다른 캡처 경로로 우회하지 않는다. 다른 소유한 웹 제품에서의 성공은 별도 제품·플랫폼 사례로 기록할 수 있지만 C001 통과로 바꿀 수 없다.

### 최소 수용 시나리오

| ID | 입력과 조건 | 확인할 행동과 판정 | 상태 |
| --- | --- | --- | --- |
| M01 | 새 세션, 소유한 제품 URL/저장소와 `우리 앱 UX 개선해줘`만 제공 | 호스트가 실제 제품/의도를 먼저 읽고 과업을 스스로 구성. 사용자에게 브리프/모델/근거 JSON 제작을 요구하지 않음. | 미실행 |
| M02 | 저장·뒤로 가기에서 입력이 사라지는 알려진 결함과 안전한 fixture | 원래 실패 재현 → 허용된 수정 → 같은 시작 상태에서 값 유지 및 인접 과업 통과. 코드 diff만으로 통과 금지. | 미실행 |
| M03 | 결함 없는 control 과업 | 검사 범위와 근거를 제시하고 무리한 수정 없이 종료. 그럴듯한 새 문제가 꼭 있어야 한다고 만들지 않음. | 미실행 |
| M04 | optional source가 차단되지만 제품 QA는 가능 | 원문 접근 차단을 지키고 gap을 보고. 이미 재현한 결함의 QA를 계속함. 차단을 우회하거나 원문을 읽었다고 하지 않음. | 미실행 |
| M05 | required Figma readback 부재 | 영향을 받는 UI 변경은 하지 않되 baseline QA 결과는 전달. access missing을 no-defect/pass로 바꾸지 않음. | 미실행 |
| M06 | timestamp·revision·해시·PNG·숫자 오염 근거 | 각각 올바른 blocked/unknown/invalid 처리를 확인. 이번 패치는 PNG/JSON 하위 경계만 검증함. | 일부 component 시험만 완료 |
| M07 | 수정 후 세션 중단/재개와 concurrent source edit | 실제 체크포인트·현재 입력을 대조하고 이미 반영한 수정을 중복 적용하지 않음. 구 revision의 pass를 최신 결과로 재사용하지 않음. | 미실행 |
| M08 | 실제 호스트별 설치·업데이트 후 동일 과업 | 구 설치본·새 설치본을 구별하고 현재 버전의 실제 요청 채택·실행 결과를 확인. | 미실행 |

이 표는 새로운 수용 시험 제안이며 이전 C001/C002 기록을 지우거나 대체하지 않는다. `미실행`은 이번 감사에서의 상태이고, 같은 성격의 기존 component 시험이 없다는 뜻이 아니다.

## 8. OMO와 효과를 비교하는 방법

목적이 같은 UX 개선 과업에서만 대조한다. 같은 제품/커밋/fixture, 같은 자료, 가능한 한 같은 모델·추론 설정·도구·권한·예산으로 `기본 호스트만`, `Remorsearch`, `Native`, `Wish`를 비교한다. 호스트나 모델을 맞출 수 없다면 그 변수는 별도로 표기하고 스킬 효과만 분리해 입증했다고 하지 않는다. OMO가 요구하는 도구를 제공하지 않은 채 실패율을 비교하는 것도 공정하지 않다.

과업은 알려진 결함, 정상 control, 의도적 confirmation 보존, 접근 차단, 근거 오염, 복구로 나누고 개발용과 비공개 평가용을 분리한다. 수행 순서를 섞고 반복 횟수·중단·실패 집계 규칙을 결과 보기 전에 고정한다. 평가자는 가능한 범위에서 어떤 스킬이 만든 결과인지 모르게 실제 산출물과 실행 근거를 판정한다.

주요 결과는 **원래 과업의 검증된 개선 완료율**이다. 함께 기록할 것은 결함 recall/precision, 새 회귀, 권한 위반, 잘못된 완료 선언, 사용자 개입 횟수, 재실행 횟수, 경과 시간, 관측 가능한 토큰/비용이다. 도구 사용 불가나 모델 과금 미관측은 0으로 채우지 않는다. 여러 번 반복한 같은 과업을 독립적인 제품 수로 세지 않는다. 표본이 적으면 사례 결과와 불확실성만 보고하며 근거 없는 종합 점수나 'OMO급' 인증을 붙이지 않는다.

## 9. 이번 변경의 경계

변경은 PNG 근거 형식 검사, JSON 숫자 경계, 관련 회귀 시험, 이 감사 문서다. 연구 접근 정책, Figma/의도 계약, 호스트 기본 모델, 작업 권한, 원본 실패 기록, 기존 PR #3는 보존한다. OMO 패키지·코드·실행 권한을 추가하지 않는다. 전체 저장소의 모든 모듈을 보안 감사하거나 실사용 성능을 인증한 보고서가 아니다.

## 직접 읽은 근거

Remorsearch: [진입 계약][R1] · [제품 개선 절차][R2] · [기존 검증과 인계][R3] · [기준 CI][R4] · [스크린샷 게이트][R5] · [JSON 경계][R6] · [CI 구성][R7] · [과거 held-out 결과][R8].

비교 대상: [Native ultrawork][N1] · [Wish 진입 계약][W1] · [Wish 검증 절차][W2]. 형식 문서: [PNG 표준][P1] · [Python JSON][P2].

[R1]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/blob/6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b/skills/remorsearch-ux-qa/SKILL.md
[R2]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/blob/6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b/skills/remorsearch-ux-qa/references/loop/product-improvement.md
[R3]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/blob/6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b/HANDOFF.md
[R4]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/actions/runs/37156736179
[R5]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/blob/6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b/skills/remorsearch-ux-qa/uxloop/evidence.py
[R6]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/blob/6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b/skills/remorsearch-ux-qa/uxloop/io.py
[R7]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/blob/6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b/.github/workflows/test.yml
[R8]: https://github.com/remorser58/Remorsearch_UX_QA_Skill/blob/6ef61335b23f3dcd1758a7abaddb9d8aa528fa5b/docs/validation/experiments/heldout-2-results.md
[N1]: https://github.com/code-yeongyu/oh-my-openagent/blob/b9463e692f93aa49bb10d306c0c6f1ade54f7840/packages/omo-senpi/skills/ultrawork/SKILL.md#L1-L200
[W1]: https://github.com/DevNewbie1826/omo-wish/blob/1a4cff69915781274d794669e3746376b8016fb5/skills/wish/SKILL.md
[W2]: https://github.com/DevNewbie1826/omo-wish/blob/1a4cff69915781274d794669e3746376b8016fb5/skills/wish/references/verification.md
[P1]: https://www.w3.org/TR/2025/REC-png-3-20250624/
[P2]: https://docs.python.org/3/library/json.html
