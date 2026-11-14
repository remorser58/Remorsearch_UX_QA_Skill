# 두 번째 스모크 진단 — 평가 완료와 큐 완료의 구분

구현 `fb0c6666bde5e969a6b479ec94ccf875a5f3aac5`, fixture v7에서 새 독립 세션016·029를 실행했다. 시작은2026-11-14T04:48:43Z, 실행 루트는 `.ux-loop/peekly-coverage-smoke-r2-20261114`다. 기존 큐를 재개하거나 불확실 요청을 재전송하지 않았다.

## 016: 관측 수용 오류, 전체 세션은 미평가

Job `S-mdheffekaehcmlbncccbjmdg`의 SQLite 상태는 `complete`지만 결과의 `operational_completed=false`, `problem=observation_invalid`다. 첫 판정과 최종 판정은 모두 빈 객체다. 저장된 성공 기준 통과1/미실행2 및 복구 미실행1은 중단 때 보존한 checkpoint preview이므로 평가 완료 집계에 포함하지 않는다. 원래46행 중016의 저장 실패 NR-03·NR-20은 이번 완료 분모에서 여전히 미평가다.

기준 순서는 PROGRESS / SIZE / SAVE-FAIL이다. preview의 통과1은 실제 진행 중 취소 증거에 대한 index0이며, 크기 경계 전체가 최종 통과했다는 뜻이 아니다.

### 정확한 오류

13턴 `upload_save_failure(peekly-sample-previous.zip)`의 operation `op-f30fb0491f9e1ca6d18d7babaa8454b28e305646`은 `done`으로 저장됐다. 응답은 소비·복원된1회 저장 실패, 이전 저장 상태 보존, 실제 오류 안내, 직접 재시도 버튼 부재를 기록한다.

응답의 native check는 success index2 `failed`이며 다음 제한된 진단 이유를 갖는다:

> The write-failure notice and unchanged persisted state were observed, but the PRD-required direct save-retry control was absent; only file re-selection was offered.

그러나 `agent_run.py:Execution.observation`은 `reason`을 `not_run`에만 허용한다. 이 정직한 실패 증거가 수용 단계에서 거부됐다. `scale_run.py:Evidence.observation`도 같은 메서드를 사용한다. 수정은 failed/not_run의320자 이하·비어 있지 않은 이유만 허용하고 기존 개인정보·형식 검증과 passed+reason 거부를 유지하는 것으로 제한한다.

거부된 응답은 `stage-2/queue.sqlite`의 위 operation에서 읽을 수 있다. 화면은 해당 job의 `sessions/S-mdheffekaehcmlbncccbjmdg/evidence/S-mdheffekaehcmlbncccbjmdg/1/browser-00235.png`와 `browser-00247.png`다. 두 응답 참조 SHA-256은 `34fed3ee3d8a6cb98cb0a05736c670fc1058ca6c31f800187acde30f3bef83d8`다.

직전 obs12의64MiB 초과 거부는 의도된 `@group:peekly-loose-total-over` 시험이다. v7 progress fixture 거부로 해석하면 안 된다.

### 실제 취소는 수행됨

obs9 및 operation `op-3c9958680a9c857a58d41b6e36dcf7e8e41267ec`은 `upload-89`에 묶인 v7 progress 파일을 사용했다. reading1ms·analysis24ms가 관측됐고, `cancel_active=true`, `cancel_dispatched=true`, 최종 `cancelled_without_new_result`를 기록했다. 후속1,066ms 관측에서 진행/완료 상태는 모두false이며 전후 저장 해시는 동일하다. 이는 실제 클릭과 저장 상태의 증거다. 세션 전체가 미평가라는 사실과 개별 취소 동작이 수행됐다는 사실을 구분한다.

## 029: 가시성 판정은 정확했고 스크롤 후 진입함

Job `S-gpnddknljnlgfgabohhngibn`의 obs15는 More 화면 아래쪽이어서 import 카드가 viewport 위쪽 밖에 있었다. 모달이 없었고 `visible:false`는 정확했다. obs16·17의 위쪽 스크롤 후 버튼이 보였으며, obs18은 hit-test 및 실제 클릭을 통과하고 obs19에서 보관 스냅샷01을 가져왔다.

obs10–15의 Results↔More 왕복은 과제 문구를 개선할 근거다. sample export 확인 뒤 별도 샘플 닫기를 요구하지 않고, 모달이 없고 import 진입점이 화면 밖이면 다른 탭을 왕복하기 전에 위로 스크롤하도록 명시한다. 최신 실행 결과는 같은 루트의 `run-status.json`을 기준으로 한다.

## 전달 감사와 확대 금지

실행 중 원장 SHA `a3e16733ea3b698ba07a8eb8034e6e29e40f1e4856855af527394b7109afa344`의 읽기 전용 감사는 실제 요청34, 고유 call ID33, 완료 응답 품질 수정1, 불확실 이벤트0·불확실 재전송0이었다. 이는 중간 스냅샷이며 최종 원장 감사를 대신하지 않는다.

016이 평가 완료 조건을 충족하지 않아 이 스모크로32명 확대를 승인할 수 없다. r2 종료 후 최소 수정과 회귀 검증을 하고, 새 r3 실행으로 감소를 입증한다. r1/r2의 기록은 그대로 보존하며 어느 것도 재개하지 않는다.

## 최종 상태와 검증

- 종료:2026-11-14T05:13:52Z, `smoke_failed`. Queue complete2, running/queued/uncertain 모두0.
- 평가 완료:029만1세션, 미결론1. 성공 기준 통과2/실패0/미실행1/N/A0, 조건부 복구 N/A1. 016은 미평가이며 두 사람 스모크의 감소 승인 조건을 충족하지 못했다.
- 029의 sample export 및 보관 제한은 통과했다. 보관 증거는 obs49·52다. 무료 비교·기록 조작·Pro 설명을 모두 관측하지 못해 paywall은 미실행이다. 마지막 checkpoint는1,517,312바이트로 이전1MiB 장애를 넘어서 정상 저장됐다.
- 최종 원장 감사:실제 요청77, call ID76, 완료 응답 품질 수정1, 불확실 이벤트0·불확실 재전송0·미확정 guard0. 원장 SHA-256 `65334e4a9034a104a277e7f5d01826e82679842ed51653c041a5314904ced745`.
- Report SHA-256 `ad2eab7355b243caf150299c122f07b1656fecb41ca4621c8c7eab93335cd5c5`; stage-summary SHA-256 `c2b1b5d2431e0eeb8997676961e2e11b48d6603f72ab4e4bbe74676e96a88843`.
- 이전 큐 무변경과 격리 브라우저 종료가 확인됐다. 사용 route는 `TOKENMAXX/deepseek-v4.1-flash-free` 한 개이며 fallback0이다.
- 016의 저장 결과 해시 및 증거27개의 실제 파일 해시를 독립 대조했고 불일치0이었다. 결과 SHA-256은 `7ddf2088be466650b49add6a6069b31fb2d5a9af7801f69412c3938b0c451158`다.
- 029의 등록 증거122개(JSON61/PNG61)도 독립 대조해 누락·해시 불일치0을 확인했다. 11개 파일 각각에서 manifest 해시 일치, 저장 digest 변경, 성공 안내와 서로 다른 결과(팔로워13→23/팔로잉12)가 관측됐다.
- obs52의 이력 시작13:55·최신 비교14:05→14:06(KST)은 저장 operation의 snapshot02 13:55:18,10 14:05:26,11 14:06:23과 일치한다. 첫01은13:53:43이었다. 고정 제품의 RelationshipHistorySheet가 시작 시각을 정렬된 첫 기록의 observedAt으로 표시하므로, 화면상 가장 오래된01이 빠지고 최신10개가 남았다는 추가 근거다. 전체 내부 snapshot ID 목록은 보존하지 않아 저장소의 물리적 삭제 자체를 직접 검증한 것은 아니다.
- obs49 SHA-256 `03d836dd315d18a10bd0ea3a81204c708f08094d81e2494895769ba0bd242629`; obs52 SHA-256 `afa04455e58881476e710d5d1bc04ed49edf1396dcc94de4f8bbefeddd6889cc`. 029의 공통 증거 위치는 `stage-2/sessions/S-gpnddknljnlgfgabohhngibn/evidence/S-gpnddknljnlgfgabohhngibn/1/`이다.

종료 후 수정은 failed/not_run의 제한된 진단 이유 수용, 샘플 종료 우회와 가시성에 따른 스크롤 안내, 새 r3 루트 지정뿐이다. 새 실패 증거 회귀5개·체크리스트7개·launcher18개가 모두 통과했다. 관련 기존85개 검증은65개 통과·선택 LangGraph 의존성20개 건너뜀·실패0개다. 실제 r3 사전 점검은29개 이전 큐와291개 job ID의 재사용 차단을 확인했다.
