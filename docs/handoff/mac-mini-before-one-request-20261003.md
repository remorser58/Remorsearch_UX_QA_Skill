# Mac mini 개발 핸드오프

기준일: 2026-10-03. 맥미니에서 Remorsearch UX QA를 이어서 개발할 때 이 문서부터 읽습니다.
현재 구현과 검증 공백을 함께 확인하려면 아래 읽기 순서를 따르세요.

## 현재 상태

- 스킬 저장소: [remorser58/Remorsearch_UX_QA_Skill](https://github.com/remorser58/Remorsearch_UX_QA_Skill), 비공개.
- [스킬 PR #1](https://github.com/remorser58/Remorsearch_UX_QA_Skill/pull/1)은 병합됐습니다.
  마지막 스킬 구현 검증 기준은 `1671b8d4d6c3c6fa3fa0aac3dd98bab9212b813d`입니다.
  이 구현 기준과 검증한 PR head `967fa53e10fd015083328ce6d7bd234d6db2b71d`의 소스 트리가 같습니다.
  현재 문서 포함 커밋은 저장소에서 `git rev-parse HEAD`로 확인합니다.
- [병합 후 CI](https://github.com/remorser58/Remorsearch_UX_QA_Skill/actions/runs/37030025506)는 5개 작업이 모두 통과했습니다.
  공개 전환과 공개 릴리스는 아직 하지 않았습니다.
- 설치 단위는 `skills/remorsearch-ux-qa/` 한 폴더입니다. insane-search는 그 안의
  `references/insane-search/`에 포함되어 리서치 수집 단계에서 사용됩니다.
- UniClub은 [PR #1](https://github.com/remorser58/UniClub/pull/1)을 올려 두는 범위로 마칩니다.
  최신 사용자 지시가 PR까지만 처리하는 것이므로 병합·배포하지 않습니다.

## 읽을 순서

1. [PRD](PRD.md): 사용자가 설명한 목적, 의도 보존, 조사 출처와 완료 기준.
2. [현재 SKILL](skills/remorsearch-ux-qa/SKILL.md)과
   [제품 개선 지침](skills/remorsearch-ux-qa/references/loop/product-improvement.md): 실제 시작 방법과 반복 범위.
3. [제품 의도 구현 검증](docs/validation/product-intent-2026-10-02.md)과
   [UniClub 실제 실행 기록](docs/validation/uniclub-live-20261002.json): 통과한 항목과 현재 한계.
4. [README](README.md), [설치·배포 검사](docs/release.md),
   [native 실행 계약](skills/remorsearch-ux-qa/references/loop/provider-contract.md#native-application-identity): 설치와 근거 형식.
5. 인체공학을 수정할 때 [heldout-2 결과](docs/validation/experiments/heldout-2-results.md)와
   [실험 결정 기록](docs/validation/experiments/decisions.md).

[이전 클라우드 핸드오프](docs/handoff/cloud-handoff-through-20261001.md)와
[관련 보관 자료](docs/handoff/README.md)는 당시 결정의 근거가 필요할 때 참고합니다.
옛 할 일, 모델 추천, 브랜치, 삭제·공개 지시는 현재 작업 지시로 사용하지 않습니다.
README의 설치 예제는 아직 RC 브랜치를 가리킵니다. 다음 개발은 아래 준비된 작업 폴더의 현재 `main` 기준으로 시작합니다.

## 스킬이 해야 하는 일

어느 정도 완성된 제품의 URL이나 저장소를 받으면 제품과 개발자의 의도를 읽고,
초기 QA에서 질문과 문제를 발견합니다. 사용자가 질문·페르소나·문제 목록을 미리 작성할 필요는 없습니다.
관련 Claude·Codex 세션과 메모리, 결정 기록, 커밋과 Figma를 대조해 의도적으로 유지한 결정을 보존합니다.

제품 과업에서 조사 질문과 출처를 정하고, 포함된 insane-search 자료로 허용된 수집을 진행합니다.
당근·디시인사이드·유튜브 댓글·X·인스타그램·Threads는 출처 후보입니다.
모든 사이트 수집이나 플랫폼만으로 이용자의 나이·성별·성향을 추정하는 작업은 요구하지 않습니다.
원문·댓글·검색 요약과 미열람 공백을 구분하고, 접근 중단과 개인정보 규칙을 유지합니다.

조사 근거를 QA 시나리오로 바꾸고, 실제로 재현한 원인을 되돌릴 수 있는 범위에서 수정합니다.
화면·UX 변경은 Figma에서 먼저 만들고 실제 파일 URL·노드·버전·읽어 확인한 결과를 남깁니다.
수정 후 같은 과업과 인접 과업을 다시 실행해 의도 보존까지 확인합니다.
세로 강조선과 측면 탭 카드는 사용하지 않습니다.

CLI는 가져온 근거의 형식·해시·연결을 검사하고 허용된 로컬 텍스트 패치를 적용합니다.
브라우저·리서치·Figma·빌드 작업은 호스트 도구가 수행합니다.
실행 기록을 받아들였다는 사실만으로 제품 개선 완료를 선언할 수 없습니다.

## Mac mini 작업 위치

SSH 별칭은 `m4mini-work`, 호스트 이름은 `REVOLAR_MINI`입니다.
맥미니 작업 dot은 [REM](https://chatgpt.com/local/01a0fcdd-ec2c-7026-97c6-e83397037039?hostId=local)입니다.

| 용도 | Mac mini 경로와 상태 |
| --- | --- |
| 다음 스킬 개발 | `/Users/m4mini/Work/projects/rq-wt/mac-mini-development-20261003`, 브랜치 `codex/mac-mini-development-20261003`. `main`의 `1671b8d`에서 만든 깨끗한 worktree이며 핸드오프 반영 후 현재 HEAD를 확인합니다. |
| 검증 당시 스킬 | `/Users/m4mini/Documents/Codex/2026-10-02/task-2/remorsearch`, 검증 기준 `967fa53` |
| 기존 스킬 작업 | `/Users/m4mini/Work/projects/Remorsearch_UX_QA_Skill`, `42579a6` 기준의 수정·미추적 파일이 남아 있습니다. 현재 개발 시작점으로 사용하지 말고 보존합니다. |
| UniClub PR 작업 | `/Users/m4mini/Documents/Codex/2026-10-02/task-2/uniclub`, REM이 변경을 담당한 체크아웃 |

실험·앱 실행·테스트는 맥미니에서 수행합니다. 노트북은 문서 읽기와 작업 조율에 사용합니다.
기존의 수정된 작업 폴더에 `reset`, `clean`, 덮어쓰는 복사나 `pull`을 실행하지 않습니다.
이미 준비된 다음 개발 폴더에서 시작하고, 이전 근거와 다른 작업자의 수정을 보존합니다.

## 확인된 검증과 남은 일

| 범위 | 확인된 결과 | 남은 검증 |
| --- | --- | --- |
| 스킬 Python | native 수정 후 993개 실행: 992개 통과, 1개 skip | 이 수치는 위 검증 소스 기준이며 후속 수정에는 관련 검사가 필요합니다. |
| native 계약 | 11개 회귀 검사 통과. native raw URI 식별과 Swift `+` 파일 경로 문제 수정 | 내장 native 실행기와 의미 정보 수집 어댑터가 없습니다. |
| 실제 UniClub 기록 입력 | 수정 전 거부되던 실제 근거가 유효한 bundle로 처리됨 | `improve`는 `unknown`, `product_complete: false`, `intent_verified: false`. 필요한 근거가 부족합니다. |
| 제품 의도 | 구체적 의도 결정, 변경 없는 범위, 시나리오별 재실행과 검토 연결 검사 | 실제 제품의 현재 의도·디자인·회귀 근거를 끝까지 연결하는 검증이 필요합니다. |
| 접근성·Figma | 일부 실제 XCUITest 로그와 화면이 보관됨 | 전체 VoiceOver, 하드웨어 키보드, 정확한 viewport·버전에 연결된 Figma 비교가 없습니다. |
| 인체공학 | 실험적 선별 기능과 고정된 평가 기록 보유 | heldout-2의 오류 보고량은 1.75로 기준 0.35를 초과했습니다. 실제 사람에 대한 정확도는 입증되지 않았습니다. |

합성 자료의 통과는 실제 제품 개선을 입증하지 않습니다.
실제 기록을 가져온 검사는 기록 간 일관성을 확인하며, 기록 자체의 독립적 진위 확인까지 수행하지 않습니다.
이미 답을 본 heldout 자료로 임계값을 맞춘 뒤 새 성능으로 보고하지 않습니다.

## UniClub PR 인계 상태

[UniClub PR #1](https://github.com/remorser58/UniClub/pull/1)은 열린 Draft입니다.
head는 `codex/remorsearch-uniclub-qa-20261002`의 `32c2757b45789757d3bd2a9909e37e1691985b87`,
base는 `codex/uniclub-ios-release`입니다. 기획용 `main`을 별도로 유지합니다.

알림 3개 사례와 소유권 이전 후 역할 복구가 통과했고, 앞선 저장소 검사 870개가 통과했습니다.
최종 후속 수정은 위 커밋으로 푸시했고, 해당 head의
[PR 저장소 CI](https://github.com/remorser58/UniClub/actions/runs/37039926126)와
[push 저장소 CI](https://github.com/remorser58/UniClub/actions/runs/37039920685)가 모두 통과했습니다.
아래 실제 UI 검사 실패는 별도로 남아 있습니다.

마지막 customization 검사는 빌드에 성공했지만 UI 검사 1개가 실패했습니다.
`ReleaseSurfaceUITests.swift:130`에서 첫 라벨 입력 뒤 `eventSingular` 필드를 조작할 수 없었습니다.
전체 높이 편집 화면과 첫 입력은 확인됐고, 키보드는 `Return`을 표시하는데 보조 함수는 `완료`를 찾았습니다.
키보드 처리가 원인이라는 판단은 추정이며, 수정 후 재실행으로 확인하지 못했습니다.
preview·저장 유지·이력까지 통과했다고 보고하지 않습니다.

이번 작업은 검토한 변경과 실패 근거를 PR에 남기는 것으로 마쳤습니다.
후속 앱 수정은 새 개발 범위에서 다루고, 이 핸드오프만으로 PR을 병합하거나 배포하지 않습니다.

## 근거 위치

다음 경로는 맥미니의 원본 근거입니다. 저장소 문서의 요약과 함께 확인합니다.

- 실제 스킬·UniClub 실행: `/Users/m4mini/Work/artifacts/remorsearch/uniclub-live-20261002/rem-evidence`
- 제품 의도와 설치 위치 변경 검사: `/Users/m4mini/Documents/Codex/2026-10-02/task/rem-validation`
- 최종 UniClub 근거 목록: `/Users/m4mini/Work/artifacts/remorsearch/uniclub-pr-completion-20261003/rem-evidence/validation-index.json`
- PR 검사 로그·결과 묶음: `/Users/m4mini/Documents/Codex/2026-10-02/task-2/pr-evidence`

앞선 실패·중간 결과·원본 결과 묶음을 지우지 않습니다. 새 실행은 별도 근거 폴더에 기록합니다.
로컬 경로는 비공개 핸드오프 문맥이며, 자격 증명이나 무관한 사용자 기록은 넣지 않습니다.

## 다음 개발 순서와 수용 기준

1. 준비된 스킬 worktree와 설치본의 버전을 확인하고 UniClub 실제 근거를 최신 스킬로 처리합니다.
   실제 baseline·replay·인접 회귀·의도 검토·Figma 연결의 누락 항목을 구체적으로 기록합니다.
   누락이 남으면 현재 `unknown`과 완료 보류가 유지되어야 합니다.
2. 원본 XCUITest 결과·실제 앱 식별·기기·viewport·입력·빌드·capture hash를 기존 계약에 연결합니다.
   수동 기록 연결로 해결되지 않는 누락이 있으면 native 실행·의미 정보 수집 어댑터의 필요 범위를 검토하고 개발합니다.
   VoiceOver·키보드 미실행, 잘못된 식별, 오래된 replay가 통과하지 않는 기존 검사를 유지합니다.
3. 실제 제품에서 질문 발견부터 조사·Figma 수정·같은 과업 및 인접 과업 재실행까지 진행합니다.
   범위 안의 중대한 문제와 필수 근거 공백이 없고 `intent_verified`가 참이어야 완료를 선언합니다.
4. 인체공학은 보지 않은 새 평가 자료와 수용 기준을 미리 고정한 뒤 평가합니다.
   재현율·정상 화면의 오류 보고량·조건 식별을 함께 보고하고, 기존 heldout은 과거 비교용으로 보존합니다.

## 설치와 검사 명령

준비된 맥미니 스킬 저장소 루트에서 사용합니다. Python 3.10+와 web driver용 Node.js 22가 필요합니다.
설치는 아래처럼 Git 체크아웃의 스킬 폴더를 직접 복사합니다.
기존 설치본에 로컬 변경이 있으면 별도 위치에 보존한 뒤 복사하세요. ZIP 전달은 필요하지 않습니다.

```sh
mkdir -p ~/.codex/skills
cp -R skills/remorsearch-ux-qa ~/.codex/skills/
```

아래 명령은 현재 README·release 문서와 기존 실행 기록에 대조했습니다.
이번 핸드오프 문서 작업에서는 앱이나 전체 검사를 다시 실행하지 않았습니다.
full package 검사는 준비된 driver 의존성이 필요하며 `--output`에 아직 없는 디렉터리를 사용합니다.
내부에서 만드는 ZIP은 설치 위치·무결성 검사용 산출물입니다.

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 skills/remorsearch-ux-qa/scripts/smoke_loop.py
python3 scripts/check_release.py --output dist/release-check
```

Node 의존성 준비와 세부 검사 선택은 [현재 release 문서](docs/release.md)를 따릅니다.

## 다음 세션에 붙여 넣을 요청

```text
맥미니의 /Users/m4mini/Work/projects/rq-wt/mac-mini-development-20261003에서 Remorsearch UX QA 개발을 이어서 해.
HANDOFF.md → PRD.md → skills/remorsearch-ux-qa/SKILL.md → skills/remorsearch-ux-qa/references/loop/product-improvement.md와 연결된 검증 기록을 읽어.
현재 HEAD와 설치된 스킬 버전을 확인하고 기존 수정 파일과 원본 근거를 보존해. 실험·앱·테스트는 맥미니에서 돌려.
사용자가 질문을 미리 쓰지 않아도 제품 QA에서 문제를 발견하고 조사·수정·재검증하는 목적을 유지해.
개발자의 의도와 관련 세션 메모리, Figma를 확인하고 insane-search는 Remorsearch 내부 리서치에서 사용해.
최신 스킬에 실제 UniClub 근거를 연결해 남은 공백부터 확인해. 수동 연결로 해결되지 않으면 필요한 native 수집 어댑터를 검토·개발해.
미실행 접근성이나 Figma·의도 근거 누락을 통과로 바꾸지 말고 새 인체공학 평가는 보지 않은 자료로 해.
UniClub은 기존 PR까지만 처리한 상태야. 이번 요청으로 앱 PR을 병합하거나 배포하지 마.
```
