# Peekly 실제 정적 빌드의 소유 headless UX 과업 검증

기준일: 2026-11-12. [기계 판독 결과 JSON](peekly-headless-results-20261112.json), [사전 고정 프로토콜](../../benchmarks/peekly-headless-pilot/protocol.json), [준비·실행 절차](../../benchmarks/peekly-headless-pilot/README.md)를 함께 읽습니다.

## 1. 결과와 근거 등급

실제 Peekly 소스의 복사본을 빌드하고 실제 UI·파일 입력·Worker를 실행했습니다. 샘플 탐색과 누락 입력 회복은 고정 기준을 통과했습니다. 팔로워·팔로잉 각각 150,000행의 ZIP 및 개별 JSON 가져오기는 실제 오류 문구를 표시해 두 과업의 목표가 실패했습니다. 각 실패 뒤 이전 카운트 표시와 작은 정상 입력으로의 회복은 확인했습니다.

| 구분 | 관측 또는 범위 |
| --- | --- |
| 실제 제품 코드·실브라우저 | 실행함. 제품 화면을 대신 만든 합성 HTML은 사용하지 않음 |
| 입력·페르소나 | 합성 파일, 기존 PRD 가설 페르소나 4개 저장·3개 실행 |
| 과업·행동 | 4과업 각각 1회 직렬 실행, 37개 행동 모두 완료 |
| 측정 기준 | 37개 체크: 33개 통과·4개 실패·미관측 0개 |
| 과업 판정 | 2개 통과·2개 실패. `task_scope_passed: false`, 명령 종료 코드 1 |
| 실행 감사 | 4개 receipt와 영속 로그 일치. 실행 불확실·격리 0건, 소유 브라우저 종료 확인 |
| 실제 사람·새 공개 조사 | 실제 참여자 0명, 새 공개 출처 수집 0건 |
| 효과·제품 준비 | `real_user_evidence: false`, `product_ready: false`, 페르소나 효과 미검증 |

실제 화면 관측과 합성 조건의 실행은 동시에 성립합니다. 이 결과는 일반인의 행동을 자율적으로 재현했다는 증거, 실제 사용자 수요 검증 또는 Remorsearch의 비교 우위가 아닙니다. 기존 프로토콜의 `P-*` 가설은 Library·receipt의 `PER-*` ID에 대응합니다(예: `P-EXPLORE` → `PER-EXPLORE`). 아래 표는 실제 실행 ID를 사용합니다. `PER-KEEP`는 저장·재사용 검증만 했으며 해당 페르소나의 제품 과업은 실행하지 않았습니다.

## 2. 이번에 완성한 실행 연결

앞선 브라우저 연결은 검토한 정적 합성 UI를 실행했지만 실제 Peekly의 파일 입력과 module Worker를 그대로 작동시킬 수 없었습니다. 이번에는 기존 Library·swarm 배정·`WebSession`·task check·PNG·receipt·감사 구조를 재사용하면서 다음 경계를 추가했습니다. 자세한 계약은 [browser-run.md](../../skills/remorsearch-ux-qa/references/persona-qa/browser-run.md)에 있습니다.

- 호스트가 고정한 업로드 registry의 ID·이름·MIME·바이트·SHA-256만 허용합니다. 실제 화면의 버튼을 누르기 전에 owned filechooser를 준비하고, 확인한 실제 input에 `setFiles(Buffer)`를 전달합니다. OS 파일 선택창, 사용자 선택 파일, 가짜 `FileList`는 사용하지 않습니다.
- 정확한 검토 Worker 경로만 허용하고 원래 Worker 코드는 바꾸지 않습니다. 정적 파일은 `https://remorsearch.invalid/index.html`의 고정 origin에서 검토한 바이트로 응답합니다. HTTP/WebSocket 전달 fallback, 기존 localhost 서버·브라우저·프로필·CDP 연결을 사용하지 않습니다.
- Worker 계획은 macOS의 고정 정책 `(version 1)(allow default)(deny network*)`를 거친 실행과 실행 전 네트워크 거부 검증을 요구합니다. 페이지 RTC/WebTransport guard만으로 Worker realm까지 보호된다고 가정하지 않습니다. 이 정책은 일반 파일시스템 샌드박스나 전체 OS 보안의 독립 인증이 아닙니다.
- 파일 선택 receipt와 실제 제품 처리 결과를 분리합니다. 측정 admission은 현재 과업·시도·빌드·페르소나·단계·snapshot·PNG에 연결하고, 실제 UI 실패를 filechooser 성공이나 마지막 회복 성공으로 덮지 않습니다.

registry는 최대 32개·총 32 MiB, 파일 하나는 16 MiB, 한 행동은 최대 16개 파일입니다. 이번 registry는 17개·24,573,378바이트이며 선택 행동은 9회, 선택한 파일 인스턴스는 20개였습니다. 고정한 Worker가 실제로 9회 시작됐습니다. 5,000행 control ZIP은 생성·등록했지만 UI에 넣지 않았습니다. 따라서 그 control의 UI 성공을 주장하지 않습니다.

## 3. 제품 복사·빌드와 실행 전 고정

지정 worktree는 `/Users/r3m0r5e/CodeProjects/remorsearch-ux-qa-resume/.ux-loop/web-pro-peekly-headless-20261112/worktree`이며 시작 기준은 `7359fb6c8c770601598d431b92d350bda20096d9`입니다. 프로토콜·fixture generator·pilot runner·README의 benchmark 4파일을 실제 제품 실행 전에 `28160d29f9f5b07b8b97c86c66034d67588fbe26`으로 커밋했습니다. Production driver는 실행 전 소스 SHA-256과 독립 검토로 고정했으며 그 커밋에 모든 production 변경이 포함됐다는 뜻은 아닙니다.

제품 원본은 `/Users/r3m0r5e/CodeProjects/insta_tracker`, HEAD는 `58214441a1f87bd7b766a72c97de2a79b27438dd`입니다. 기존 dirty 50개 항목을 보존했습니다. 기존 최소 복사 recipe의 64개 실제 소스·설정·문서·테스트 파일을 해시·mode·mtime으로 고정하고 `.ux-loop/peekly-headless-20261112/product-build`에 한 번 복사했습니다. 원본 dist·iOS·Git·환경 파일·수집 자료는 복사하지 않았습니다.

의존성은 같은 APFS에서 `cp -cRP`로 한 번 복사했습니다. 복사본은 원본과 다른 inode를 사용하고 내부 상대 symlink와 바이트가 일치함을 확인했습니다. 설치 없이 복사된 실제 `tsc -b`와 Vite 설정을 Node 22.16.0으로 실행했습니다. 빌드 프로세스에는 네트워크 거부 및 제품 원본 읽기·쓰기 거부 정책, 제한한 환경, 소유 HOME/TMPDIR/cache를 적용했습니다. 두 빌드 명령 모두 종료 코드 0이며 결과는 6개 파일·542,314바이트입니다.

제품 소스 수정은 0건입니다. 빌드 전후 원본 64개 선택 파일·의존성 트리·기존 dist의 바이트와 메타데이터, Git HEAD·index·상태와 선택 경로의 diff 지문을 대조했습니다. 원본 전체의 무관한 파일 내용이나 개인 자료를 검사했다는 뜻은 아닙니다. 보존 범위와 개별 dist 해시는 archive의 provenance receipt에 있습니다.

제품 실험 뒤 최종 패키지 검사 전의 [보존 재검사 v2](peekly-headless-evidence-20261112/preservation-before-final-check-v2.json)는 12개 항목을 모두 충족했습니다. dirty 50개·64개 소스 바이트/메타데이터·Git 상태/index·tracked diff 지문이 같고 Remorsearch 지정 루트·이전 worktree가 깨끗하며 남은 소유 브라우저 PID는 0개였습니다. [첫 재검사](peekly-headless-evidence-20261112/preservation-before-final-check.json)는 줄바꿈 직렬화 상태를 기존 NUL 기준과 비교해 전체 상태 항목만 불일치했습니다. 그 결과를 보존하고 v2에서 원래 빌드 receipt의 `git status --porcelain=v1 -z --untracked-files=all` 명령으로 바로잡아 일치를 확인했습니다. 제품 파일을 고쳐 맞춘 것이 아닙니다.

| 고정 대상 | SHA-256 |
| --- | --- |
| 제품 선택 소스 manifest | `dd057f188c7f222d879956506dc314bfbff373d7bd4331d628d2dbebee62c838` |
| 제품 build receipt | `9ee962c26ab9e24ded9e073f13bf7c32f7d7c0771433632df058729029e39008` |
| dist 내용 manifest의 집계 | `905611c4994352e7d43fcea6626461a168a86b792e2f12ef37a2e7cbbe7b7a7d` |
| `assets/importWorker-hLjzVhak.js` | `1d124bb6590f4eccc420baa24c60ab8a7d4c68cdd16928fc26010fbd070237d5` |
| 고정 프로토콜 | `304f013b15d096d40958bcd42bb00b2fb3e39aed5501820ff268d7de3b79be77` |
| `run_pilot.py` | `39421ea70477ffa60b0cb9e7b37523a9a9df49ef6426b84f19d0fc9d5baa3186` |
| fixture manifest | `2d713311b2bb742c886cbad450fd587862fd0b4d71143257d08bf45998234a2d` |
| 실행한 `reviewed-plan-v2.json` | `f0306b1071af79235e0e774884cbddc650a8e6e152b48004df46cbf7821567a2` |

Node 22.16.0·Playwright 1.56.1·일치하는 Chromium headless shell의 위치와 바이트를 고정했습니다. 기기는 `desktop-1920`, viewport는 1920×1080입니다. 클릭 뒤 500 ms, 업로드 뒤 1,000 ms의 고정 정착 시간을 두고 대용량 입력은 1,000 ms를 추가로 기다렸습니다. 이는 처리 시간이나 사람의 반응 속도 측정이 아닙니다. 각 과업의 30초 한도·행동·체크·회복 분기는 실행 전에 정했습니다.

## 4. 과업별 실제 관측

| 과업 / 페르소나 | 행동 | 체크 | 관측 |
| --- | ---: | ---: | --- |
| `T-SAMPLE` / `PER-EXPLORE` | 6 | 10 통과 | 팔로워 7·팔로잉 10, 맞팔하지 않은 계정 수 5와 목록 제목, 빠진 계정 수 6과 제목·비교 한계, 샘플 종료 후 환영 화면과 진입 버튼 |
| `T-RECOVER` / `PER-RETURN` | 11 | 11 통과 | 이전 ZIP의 12/12와 다음 기록 안내, following 누락 오류, 닫은 뒤 12/12, 정상 현재 ZIP의 7/10 및 빠진 계정 6명 제목·비교 한계 |
| `T-LARGE-ZIP` / `PER-ARCHIVE` | 10 | 6 통과·2 실패 | 이전 12/12, 대용량 ZIP 뒤 오류, 닫은 뒤 12/12, 작은 정상 현재 ZIP 뒤 7/10 |
| `T-LARGE-JSON` / `PER-ARCHIVE` | 10 | 6 통과·2 실패 | 이전 12/12, 개별 JSON 묶음 뒤 같은 오류, 닫은 뒤 12/12, 작은 정상 현재 ZIP 뒤 7/10 |

보고서가 recovery 기준으로 분류한 22개 체크에는 두 대용량 과업의 사전 baseline 4개가 포함됩니다. 따라서 이를 서로 다른 오류에서 회복한 22건으로 세지 않습니다. baseline·오류 뒤 표시·정상 입력 회복은 원래 단계와 criterion mapping으로 구분합니다.

누락 입력은 step 6에서 `팔로워와 팔로잉 목록이 모두 들어 있는 파일이 필요해요. 인스타그램에서 내보낼 때 [팔로워 및 팔로잉]을 골랐는지 확인해 주세요.`로 안내했습니다. 이후 올바른 파일을 넣은 step 9와 비교 화면 step 10을 별도로 측정했습니다. 마지막 회복을 누락 입력 자체의 성공으로 계산하지 않았습니다.

두 대용량 과업의 step 7에서 실제로 표시된 문구는 다음과 같습니다.

> [followers_1.json] 파일에서 팔로워·팔로잉 목록을 읽지 못해 불러오지 않았어요. 인스타그램에서 파일을 다시 받아 주세요.

사전 기대값은 각각 `팔로워 150000명`과 `팔로잉 150000명`이었습니다. 고정 CSS는 열린 오류 모달의 보이는 안내 또는 모달이 없는 결과의 해당 카운트 중 실제 표시된 하나를 측정합니다. 모달 뒤 기존 수치를 성공으로 읽지 않으며, 결과 뒤 기대값이나 selector를 바꾸지 않았습니다. 두 기대값 모두 오류 문구와 달라 총 4개 goal check가 실패했습니다.

텍스트의 `normalize_whitespace: true`는 KoreanLineBreak의 NBSP·줄바꿈을 공백으로 접는 사전 설정입니다. 단어·숫자를 느슨하게 맞추지 않으며 원래 snapshot·PNG를 보존합니다. 자동 기준은 카운트·목록 제목·한계 문구입니다. 개별 계정 이름과 전체 행의 동일성을 자동 통과 기준으로 주장하지 않습니다.

## 5. 대용량 실패의 재현 조건

합성 파일은 복사된 제품의 `sampleData.ts`와 기존 `buildSampleExportZip`을 재사용해 한 번 생성했습니다. 고정 시점은 `2026-11-12T00:00:00+09:00`이며 실제 계정이나 개인 내보내기 파일을 사용하지 않았습니다. 프로필·댓글 등 보조 파일도 제품이 만든 합성 자료입니다.

| 입력 | 크기 | 비교한 제품 한도 |
| --- | ---: | --- |
| `large-150000.zip` | 816,720 B | ZIP 128 MiB 이내 |
| `followers_1.json` | 11,850,001 B | 파일당 JSON 32 MiB 이내 |
| `following.json` | 11,850,029 B | 파일당 JSON 32 MiB 이내 |
| 개별 JSON 12개 합계 | 23,712,900 B | 총 JSON 64 MiB·JSON 파일 512개 이내 |

제품의 archive entry 상한 20,000은 파일 항목 수에 대한 한도이며 사용자 행 수를 뜻하지 않습니다. 이 입력은 확인한 파일 수·바이트 한도 안에 있습니다. 드라이버의 파일당 16 MiB·선택 합계 32 MiB·최대 16파일 한도도 충족했습니다. 이 사실만으로 모든 규모에서 제품이 성공해야 한다는 일반 보증을 만들지는 않습니다.

ZIP SHA-256은 `02e5d68b0da3d12c63e97ffa820652b3acfc2b71d905de9cdbc7e2b16e148164`입니다. 두 큰 JSON의 SHA-256은 각각 `234bbb45d81bb50e7c3f596f498700b1c96db081603db9727b635cec7eca2618`, `a7b0d7bb34dfc59a7c1d7a4e4071af0f27a461da002238739aeb357b3be4c3ee`입니다. 선택 receipt가 실제 전달한 바이트와 연결됩니다.

재현한 고정 순서는 다음과 같습니다. 새로 실행하라는 지시가 아니라 보존한 실행을 설명하는 순서입니다.

1. 새 소유 context에서 고정 origin의 실제 빌드를 엽니다. 파일 시작과 준비된 파일 진입 버튼을 누릅니다.
2. step 3에서 `ZIP-PREVIOUS`를 선택하고 팔로워·팔로잉 각각 12명임을 측정합니다.
3. 새 파일 흐름을 열고 step 6에서 `ZIP-LARGE-150000` 또는 고정 JSON 12개를 선택합니다. step 7에서 추가 1,000 ms를 기다린 뒤 두 150,000 카운트를 측정합니다.
4. 실제 오류 안내가 관측되면 미리 정한 step 8의 닫기 행동 뒤 12/12 카운트를 다시 측정합니다.
5. 파일 흐름을 다시 열고 step 10에서 `ZIP-CURRENT`를 넣어 7/10으로 회복하는지 측정합니다.

두 과업 모두 이 순서를 각 1회만 실행했습니다. 성공 시에만 존재하는 다른 분기로 바꾸거나 반복하지 않았습니다. 예상과 달리 큰 입력이 성공했다면 고정된 오류 닫기 분기의 후속 결과는 미방문으로 남도록 정한 프로토콜입니다.

## 6. 원인 후보와 선행 코어 실험의 관계

복사된 `src/core/zipParser.ts`의 `aggregateParsedFiles`는 `followers.push(...parsed.users)`와 `following.push(...parsed.users)`를 포함한 집계 구간을 `try` 안에서 실행합니다. 그 구간의 catch는 원래 예외를 받지 않고 알려진 파일 이름이면 `InstagramExportFormatError`를 새로 만듭니다. 원래 예외의 종류·stack·cause는 버립니다.

`src/workers/importWorker.ts`는 변환된 name·message·fileName을 보내고 `src/core/importWorkerClient.ts`가 이를 오류로 복원합니다. `src/components/ExportWizardModal.tsx`와 `src/core/importValidation.ts`가 위 안내를 표시합니다. 따라서 지금의 UI는 파일 가져오기 목표 실패와 사용자에게 보인 이유를 증명하지만 원래 `RangeError` 또는 특정 spread 호출의 실패를 증명하지는 않습니다.

[선행 코어 검증](peekly-journey-results-20261112.md)에서는 150,000행 단일 JSON 파싱은 성공하고 ZIP·JSON 집계 경로는 format error로 실패했습니다. 이 차이와 소스는 집계 구간을 강한 원인 후보로 지지합니다. 선행 결과는 `ui_observed: false`였고 이번 결과는 실제 UI·Worker 관측입니다. 새로운 ZIP은 별도로 해시를 고정했으므로 이전 ZIP과 바이트 동일한 재실행이라고 하지 않습니다. 제품 수정·예외 계측·수정 후 재실행은 수행하지 않았습니다.

## 7. 원본 증거와 다시 읽기

[전체 native evidence ZIP](peekly-headless-evidence-20261112/native-evidence.zip)은 5,343,416바이트, SHA-256 `93d1407c3c20304ed7f6b8d066207759ec3b894478455586b6485b187b7b23f6`입니다. [archive manifest](peekly-headless-evidence-20261112/archive-manifest.json)는 각 member의 크기·해시를 기록하며 SHA-256은 `bbc6a73f1dca9fd34cda6830a16deda28b63133ce39bf6ad052beb8f579f3509`입니다.

ZIP의 157개 member에는 원본 native 증거 131개와 준비·실행·provenance 자료가 들어 있습니다. native 증거는 JSON 49개와 PNG 82개입니다. 과업별 최초 상태와 37개 행동을 합한 41개 capture마다 원본 PNG와 CSS PNG가 하나씩 있습니다. 제품 소스·의존성·합성 입력 파일 원본은 ZIP에 포함하지 않았으며 실제 계정·개인 파일도 없습니다. 파일럿의 원래 소유 근거 폴더는 지우지 않았습니다.

아래 12개 PNG는 가공하지 않은 원본과 바이트 동일한 복사본입니다. 나머지 모든 capture와 snapshot도 ZIP에 보존했습니다.

| 과업 | 대표 원본 PNG |
| --- | --- |
| 샘플 | [step 1 결과](peekly-headless-evidence-20261112/T-SAMPLE-step-001.png), [step 2 맞팔 목록](peekly-headless-evidence-20261112/T-SAMPLE-step-002.png), [step 4 비교 한계](peekly-headless-evidence-20261112/T-SAMPLE-step-004.png), [step 6 종료](peekly-headless-evidence-20261112/T-SAMPLE-step-006.png) |
| 누락 입력 회복 | [step 6 오류](peekly-headless-evidence-20261112/T-RECOVER-step-006.png), [step 9 정상 입력](peekly-headless-evidence-20261112/T-RECOVER-step-009.png), [step 10 비교](peekly-headless-evidence-20261112/T-RECOVER-step-010.png) |
| 대용량 ZIP | [step 3 baseline](peekly-headless-evidence-20261112/T-LARGE-ZIP-step-003.png), [step 7 오류](peekly-headless-evidence-20261112/T-LARGE-ZIP-step-007.png), [step 8 닫은 뒤](peekly-headless-evidence-20261112/T-LARGE-ZIP-step-008.png), [step 10 회복](peekly-headless-evidence-20261112/T-LARGE-ZIP-step-010.png) |
| 대용량 JSON | [step 7 오류](peekly-headless-evidence-20261112/T-LARGE-JSON-step-007.png) |

완료 뒤 `readback`은 제품을 dispatch하지 않고 상태를 다시 읽었습니다. 첫 결과와 같았으며 `ui-pilot`의 214개 파일 해시가 전후 동일했습니다. 상태 조회 종료 코드 0은 대용량 과업을 통과로 바꾸지 않습니다. 최초 보고서의 기존 일반 안내문도 원래 바이트로 보존합니다. 실행 후 `local_run.py`의 안내 두 문장을 실제 정적 UI와 Worker 정책의 범위에 맞게 정정했으며 제품 코드·원래 관측은 바꾸지 않았습니다. 실제 Worker 정책은 각 `owned_execution`과 launcher·정책 해시를 기준으로 읽고, 이 안내문 정정을 새 제품 실행 증거로 취급하지 않습니다.

## 8. 실패 보존·red → green·패키지 검사

[독립 검토·테스트 receipt](peekly-headless-evidence-20261112/review-and-tests.json)는 red/green 결과, 원본 로그 8개의 해시·보관 경로, 검토한 production 소스, 실행 후 안내 두 문장의 변경 전후 해시를 연결합니다. 독립 검토자는 별도 모델 에이전트이며 실제 참여자가 아닙니다. 실제 37개 기준·native 근거·업로드 바인딩과 archive를 대조했으며 제품 과업을 추가 실행하지 않았습니다.

| 검사 | 실제 결과와 해석 |
| --- | --- |
| Python owned-input red | 구현 전 새 검사 4개에서 failure 2·error 2. 업로드·Worker의 freeze/검증 연결 부재를 기록 |
| Node bridge red | 8개 중 7개 통과·1개 실패. 미지원 연결을 먼저 재현 |
| Python 전체 green | 1,428개 실행, 실패 0·skip 1. `python-suite.log` 보존 |
| Web driver green | 559개 통과·실패 0 |
| Bridge contract green | 33개 통과·실패 0 |
| Smoke·연구 fixture | 통과. 연구 fixture는 네트워크 요청 0의 발명된 자료이며 새 공개 조사 아님 |
| 최초 release 검사 | 21개 중 20개 통과, `ready: false`. 검사 도중 benchmark의 README·protocol·runner가 바뀌어 `validation-inputs-stable` 게이트가 실패 |
| 최종 release 재검사 | 이 문서 작성 시점에는 대기. 모든 문서·입력을 고정한 뒤 후속 별도 receipt `peekly-headless-evidence-20261112/final-release.json`에 결과를 기록할 예정이며 최초 실패를 덮어쓰지 않음 |

최초 준비는 기본 Python 3.9에서 CLI의 Python 3.10+ 요구를 충족하지 못해 Library·실행 attempt 생성 전에 종료 코드 2로 멈췄습니다. 실패 `operations/001-import.json`과 처음 만든 adapter·plan·criterion map을 보존했습니다. 실행 전 독립 검토로 큰 입력 이전의 12/12 baseline 체크 두 개를 보완하고 별도 v2 파일로 작성했습니다. 정확한 부분 준비 파일·해시·미실행 상태를 검증한 `resume_prepare`를 Python 3.14로 한 번 진행했으며 삭제·덮어쓰기·시도 초기화는 하지 않았습니다.

별도 capability probe에서는 full macOS Chromium 앱이 같은 엄격한 네트워크 거부 정책 아래 필요한 ProcessSingleton socket을 만들 수 없어 시작에 실패했습니다. 정책을 완화하지 않고 동일 Playwright에 맞는 이미 설치된 Chromium headless shell로 작은 합성 Worker probe를 실행해 거부 검증·Worker 처리·종료 ACK를 확인했습니다. 이는 실제 Peekly 과업의 선행 환경 검사이며 제품 과업 성공으로 집계하지 않습니다. 이후 고정한 실제 제품 과업 4개는 모두 한 번씩만 실행했습니다.

최초 release의 입력 안정성 실패는 실제 제품 결과 관측 전 benchmark 작성 단계의 변경을 감지한 것입니다. 기능 검사 통과만으로 그 release를 준비 완료로 올리지 않았습니다. 최종 package 판정과 실제 Peekly의 두 과업 목표 실패는 서로 독립적으로 보존해야 합니다.

## 9. 남은 한계와 다음 검증의 조건

- 자동 체크는 화면의 카운트·제목·문구에 한정됩니다. 전체 목록의 동일성·완전성, 모든 행의 접근 가능성, localStorage 바이트 보존을 증명하지 않았습니다.
- 실제 사람의 이해·행동·불편, 실사용자 효과, 공개 연구의 진위·대표성, 페르소나 방법 간 비교 우위, 병렬 다중 스웜 효과는 측정하지 않았습니다. 이번 실행은 3개 PRD 가설의 고정 여정을 직렬 실행한 것입니다.
- OS 파일 선택창, 사용자 Chrome·기존 탭/프로필, 실제 로그인·계정·개인 내보내기, backend·일반 원격 URL, iOS·실기기·보조기기를 실행하지 않았습니다. 합성 계정명이나 URL은 방문·전송하지 않았습니다.
- 네트워크 거부 실행은 검토한 소유 코드 범위의 제한입니다. 모든 파일시스템 접근이나 악성 코드의 모든 동작을 막는 일반 샌드박스를 입증하지 않았습니다.
- 제품 소스 수정과 원래 예외 stack 계측을 하지 않았습니다. 별도 승인된 제품 수정 또는 원인 계측이 필요하면 이번 원본 증거·페르소나 버전·입력·기준을 보존하고 새 빌드·새 실행으로 비교해야 합니다. 완료한 이번 시도나 기대값을 변경해 재실행하지 않습니다.
