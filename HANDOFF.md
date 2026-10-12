# 원클릭 Remorsearch UX QA 인계

**2026-10-12 후속 검증:** [호스트 복구·인체공학 집계 기록](docs/validation/mac-mini-continuation-20261012.md)에 실제 Codex 세션 중단·재개, 동시 소스 변경 감지, 중복 수정 방지와 설치 위치 변경 결과를 기록했다. 판단 불가 프로필을 정상 비교 근거에서 제외하도록 수정했고 Python 1,060개가 skip 없이 통과했다. 과거 heldout-2의 noise·H5 실패는 유지한다. UniClub의 접근성 후속 작업은 [기존 Draft PR #1](https://github.com/remorser58/UniClub/pull/1)에서 관리하며, 실기기 인증은 사용자 요청으로 보류한다.

**2026-10-12 앞선 검증:** [맥미니 검증 기록](docs/validation/mac-mini-20261012.md)에 Python 1,059·웹 selftest 570 통과, 실제 XCTest 캡처 가져오기, CG-01 행별 버튼 오탐 수정, 고정 Figma 버전 대조와 UniClub 입력란·미리보기 개선을 기록했다. 기존 game-desktop 결함 16/16 탐지를 유지했고 clean 경고는 17→16이다. UniClub 최종 XCTest의 접근성 감사 10건 실패와 heldout-2 실패 판정은 보존했다. 두 PR은 Draft/open이며 실기기 인증은 사용자 요청으로 보류했다. 호스트 채택·복구 성숙도 검증은 남아 있다.

아래 문단은 2026-10-03 시점의 과거 기록이다.

기준일: 2026-10-03. 최신 사용자 요청은 **하던 작업을 인계하고 PR을 올린 뒤 종료**하는 것입니다.
이 브랜치는 미완료 검증을 남긴 Draft PR로 전달합니다. 원래 wish의 전체 완료나 병합 승인이 아닙니다.

## 전달 대상과 변경 내용

- 저장소: [remorser58/Remorsearch_UX_QA_Skill](https://github.com/remorser58/Remorsearch_UX_QA_Skill), 비공개 유지.
- 브랜치: `wish/one-request-ux-qa-20261003`, PR base: `main`.
- 마지막 구현 검증 커밋: `611ca999130a993736b97862d155fc7fe9ea93a1`.
  이후 인계 문서 커밋은 런타임 코드와 설치 payload를 변경하지 않습니다.
- 이번 전달에서 PR 병합, 공개 전환, 릴리스, UniClub 변경·병합·배포는 하지 않습니다.

| 커밋 | 구현한 동작 |
| --- | --- |
| `53120a0` | 설치된 지원 Python과 선택적 Node 22를 탐색하고, 오래된 Python에서 실행 가능한 안내를 출력 |
| `fc3bee0` | `ux_loop.py fill`로 명시적인 `@auto` bookkeeping만 계산 |
| `f07d77a` | 제품·의도 발견 → 초기 QA → 필요한 조사 → 타당한 수정 → 재검증 흐름, 기본 세션 모델 상속 |
| `611ca99` | 복사된 설치본의 runtime discovery와 실제 fill/validate/patch/replay를 배포 검사에 연결 |

사용자가 브리프, 페르소나, 근거 패킷이나 모델을 먼저 정할 필요 없이 호스트가 시작합니다.
`fill`은 관측 결과, 시각, 권한, 인텐트 결정이나 완료 판정을 만들지 않습니다.
기존 엄격한 evidence/intent 계약과 engine은 유지했습니다.

## 읽을 순서

1. 이 문서와 [PRD](PRD.md).
2. [SKILL.md](skills/remorsearch-ux-qa/SKILL.md)와
   [제품 개선 지침](skills/remorsearch-ux-qa/references/loop/product-improvement.md).
3. [런타임 탐색](skills/remorsearch-ux-qa/scripts/find_runtime.py),
   [fill 구현](skills/remorsearch-ux-qa/uxloop/fill.py),
   [loop CLI](skills/remorsearch-ux-qa/references/loop/cli.md).
4. [설치·배포 검사](docs/release.md)와
   [native 근거 계약](skills/remorsearch-ux-qa/references/loop/provider-contract.md#native-application-identity).

[직전 Mac mini 핸드오프](docs/handoff/mac-mini-before-one-request-20261003.md)는 바이트 단위로 보존했습니다.
그 안의 오래된 worktree, 테스트 수, UniClub 실패와 다음 세션 요청을 현재 상태로 사용하지 마세요.
더 오래된 자료는 [보관 목록](docs/handoff/README.md)에 있습니다.

## 확인한 결과와 한계

아래 결과는 구현 커밋 `611ca99`에 대한 실제 실행 기록입니다.
이번 인계 문서 작성 때문에 전체 런타임 검사를 반복하지 않았습니다.

| 범위 | 관측 결과 |
| --- | --- |
| 전체 Python | 1,024개 실행, `OK (skipped=1)`. 기존 실제 캡처 의존 검사를 후속 실행으로 보완 |
| 캡처 의존 검사 | 실제 브라우저 캡처 그룹 20개 통과 후 Python painted-state 9개 통과. 기존 skip 항목을 포함하며 중복 8개를 새 검사로 세지 않음 |
| 웹 driver | 559개 통과, 실패 0 |
| 설치본 smoke | 18개 명령 통과. 실제 fill → validate → 격리된 patch/replay 포함 |
| 배포 검사 | 16개 항목 통과, `ready=true`, `published=false`; 복사된 runtime 탐색·무결성·현재 소스 일치 확인 |
| 대상 회귀 | runtime 13개, portability 3개, loop 139개, reading-budget 13개, packaging 32개 통과 |
| 실패 재현 | 출력 경로 사전 거부, 잘못된 소유 revision, shell quoting, 불투명 캡처의 `@` 바이트, `.ux-loop` scratch 경계의 RED → GREEN 보존 |
| smoke 유효성 | 별도 복사본의 no-op fill을 옛 15명령 smoke는 놓쳤고 새 smoke는 실제 종료 코드 1로 발견. 원본 코드를 변조하지 않았으며 복사본 정리 완료 |
| 부정 시나리오 C002 | 설치본으로 데스크톱 키보드·모바일 크기의 마우스 과업을 실행. 404 실패를 그대로 보고하고 필수 Figma 공백, 불신 지시, 출처 없는 설문 주장을 통과로 바꾸지 않음 |

C002에서 합성 과업의 완료는 0/2였고 `task_success=false`, `product_complete=false`를 유지했습니다.
캡처만 본 별도 검토자는 네 PNG 해시와 과업 실패/P1 판단을 확인했습니다.
전체 QA 범위의 누락은 `inconclusive`로 남았습니다. 이는 스킬의 부정 시나리오 처리 근거이며,
실제 UniClub 실행이나 실사용자 효익의 근거가 아닙니다.

정적 분석을 깨끗하다고 보고하지 않습니다. 새 helper/test 파일은 오류 0개지만 경고 320개와 종료 코드 1이 남습니다.
기존 CLI에는 baseline generic annotation 오류 1개가 있고,
배포 스크립트 분석은 baseline과 같은 오류 2개, 경고 136개에서 148개로 관측됐습니다.
모든 현재 경고를 기존 문제로 분류하지 않았고 suppression을 추가하지 않았습니다.
네이티브 LSP preflight는 사용할 수 없어 작업 전용 basedpyright 1.40.1 CLI로 비교했습니다.

## 미완료 조건

1. **C001 실제 UniClub 과업:** 화면 기록 권한이 `denied`여서 조작·스크린샷을 수행하지 못했습니다.
   입력과 AX 권한은 허용됐지만 캡처와 display count는 사용할 수 없었습니다.
   다른 캡처 방식으로 거부를 우회하거나 예전 앱 기록을 새 실행으로 재사용하지 않습니다.
2. **최종 품질 게이트:** 목적 범위의 계획 게이트는 `OKAY`였지만 최종 ultrabrain 검토는 아직 실행하지 않았습니다.
   이 Draft PR을 최종 승인이나 병합 가능 상태로 간주하지 않습니다.
3. **후속 CI·병합·정리:** PR의 최신 CI를 확인하고 필요한 실제 QA와 최종 검토를 마친 뒤 별도 후속 범위에서 처리합니다.
   이번 사용자 요청은 인계와 PR 게시까지입니다.

원래 실행의 실제 완료 항목은 18개이며, 차단·종속 항목 5개는 `dropped`로 닫았습니다.
체크리스트의 `23/23 done` 표시는 닫힌 항목 수이지 원래 목표의 완료 증거가 아닙니다.
기존 loop goal은 `G001-one-goal-only-deliver-the-approved-o`, checkpoint는 `blocked`, revision 29입니다.
다음 세션은 필요한 항목을 다시 열고 기존 목표·근거를 이어받습니다.

## 실제 앱 QA를 이어갈 때

Mac mini의 OmO 실행 앱에 화면 기록 권한을 허용하고 완전히 재시작한 뒤
`computer.capabilities()`로 현재 capture/input/AX 권한을 확인합니다.
사용할 수 없으면 필요한 접근만 요청하고 거부를 우회하지 않습니다.

설치본에 전달할 원래 요청:

```text
우리 앱에서 동아리 꾸미기 과업의 UX를 점검해줘. 저장소: /Users/m4mini/Documents/Codex/2026-10-02/task-2/uniclub
```

범위는 소유한 로컬 fixture의 초안 편집이며, 게시하지 않습니다.
현재 앱 소스와 기획을 먼저 확인하고 새 실행의 build/fixture/device identity를 기록합니다.
마지막 확인된 UniClub checkout은 `d6c42411a149d9e87ffcb44fabb48ef829815c69`이며 이번 인계에서 수정하지 않았습니다.

1. 새 작업 전용 simulator/fixture를 준비하고 정리 항목을 먼저 등록합니다.
2. 실제 화면에서 `내 정보` → `운영 화면` → `동아리 꾸미기`를 관측해 진입합니다.
3. 현재 상태에 맞는 초안을 만들고 member label을 `동아리원`, event label을 `모임`으로 바꿉니다.
4. `저장하고 미리보기`에서 두 값이 반영된 화면을 확인합니다.
5. 닫고 나갔다가 `초안 이어 편집`으로 돌아와 두 값의 유지와 `버전 기록 보기`를 확인합니다.
6. 실제 조작 로그·동시각 캡처·영수증을 남기고 입력·오류·복구·포커스·한국어 잘림과 미검사 범위를 구분합니다.
7. 작업 전용 앱·fixture·simulator를 정리하고 영수증을 기록합니다.

실패한 과업은 유용한 발견일 수 있지만 통과나 수리 완료로 보고하지 않습니다.
UX 구현에는 기존 Figma·의도·권한 계약을 그대로 적용합니다.
실제 참가자의 만족도, 시간 절약, 전환율은 별도 측정 없이는 주장하지 않습니다.

## 작업 위치와 원본 근거

| 용도 | 로컬 위치 |
| --- | --- |
| 현재 브랜치 worktree | `/Users/m4mini/Work/projects/rq-wt/wish-one-request-20261003` |
| 검증한 설치본 | 위 worktree의 `dist/wish-release-check/extracted/remorsearch-ux-qa` |
| 작업 전용 도구 | `/Users/m4mini/Work/artifacts/remorsearch/wish-one-click-20261003/tooling` |
| 전체 노트패드 | `/Users/m4mini/Work/artifacts/remorsearch/wish-one-click-20261003/notepad.md` |
| 정확한 native 시나리오 | 같은 폴더의 `native-qa-scenario.md` |

원본 근거와 loop state는 아래 CloudStorage 체크아웃 안에 있습니다.
이 로컬 자료는 GitHub PR의 첨부물이 아니며 설치 payload에도 포함되지 않습니다.

```text
/Users/m4mini/Library/CloudStorage/GoogleDrive-12tjdwnaos17@gmail.com/My Drive/_PROJECT/Remorsearch_UX_QA_Skill
  .omo/evidence/ulw/01a0fe13-0d11-7e03-9c1a-1e949e04ed38/
  .omo/ulw-loop/01a0fe13-0d11-7e03-9c1a-1e949e04ed38/
  .omo/plans/wish-one-request-ux-qa.md
```

근거 폴더에서 먼저 읽을 파일:

- `release-proof.md`, `release-validation/validation.json`, `release-validation/logs/`:
  원본 validation과 로그 15개를 원본과 같은 바이트 수·SHA-256으로 별도 보존했습니다.
- `qa-web/assessment.md`, `case-record.json`, `second-pass.json`, `cleanup.json`:
  실제 부정 시나리오의 관측과 정리. 네 `*.capture.json`에 원본 PNG와 캡처 시각·해시가 있습니다.
- `blocked-audit.json`, `resume-2026-10-03T00-39-49-392Z.json`: native 접근 차단과 최근 체크포인트.
- `follow-ups.md`: 지원하지 않는 Python의 기여자 검사 안내, 정적 분석 부채, 호스트 브라우저 adapter의 관측된 한계.

QA 서버·브라우저·프로필·fixture는 정리됐습니다.
미병합 worktree, 브랜치, 작업 전용 도구와 증거는 인계를 위해 보존합니다.
다른 작업자의 수정, 기존 worktree, 원본 실패 기록을 `reset`, `clean`, 덮어쓰기로 없애지 않습니다.

## 검사 재실행

기록한 환경은 Python 3.12.14, Node 22.23.3, Playwright 1.56.1과 Chromium 1194입니다.
시스템 Python 3.9로 전체 검사를 실행하지 마세요.
`python3 skills/remorsearch-ux-qa/scripts/find_runtime.py`로 지원 런타임을 확인하고 그 경로를 사용합니다.
아래 명령의 `python3`과 `node`는 지원 버전이어야 합니다.

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py
python3 scripts/check_release.py --output dist/one-request-followup-check
```

배포 검사 출력은 아직 없는 새 디렉터리를 사용합니다.
기존 작업 전용 브라우저를 재사용한다면 `PLAYWRIGHT_BROWSERS_PATH`를 위 tooling의 `browsers`로 지정합니다.
전체 실행 환경과 명령은 원본 로그에서 확인하고, 바뀐 대상만 다시 검증하며 같은 근거를 다른 버전으로 재표시하지 않습니다.

## 다음 세션에 전달할 요청

```text
wish/one-request-ux-qa-20261003의 HANDOFF.md와 로컬 loop/notepad를 읽고 기존 근거부터 확인해.
원래 wish는 미완료이며 이 인계 요청은 Draft PR 게시까지였어.
현재 native capture 권한과 코드 버전을 확인하고, 후속 범위가 승인되면 C001 실제 앱 과업과 최종 검토부터 이어가.
과거 테스트와 synthetic 결과를 실제 사용자 효익이나 native 과업 완료로 바꾸지 마.
기존 worktree와 원본 근거를 보존하고, 이번 인계 지시만으로 스킬 PR을 병합하거나 UniClub을 변경·병합·배포하지 마.
```
