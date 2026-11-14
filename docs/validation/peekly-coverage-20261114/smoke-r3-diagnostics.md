# 세 번째 스모크 — 수치 감소와 추가 실행기 결함

런타임 `18a4c0af8cee17e6af73984eaebfa4a5595720e4`, 기존 v7 fixture로016·029의 독립 세션을 실행했다. 루트는 `.ux-loop/peekly-coverage-smoke-r3-20261114`이며05:19:18Z 시작,05:35:49Z 종료다.

## 최종 결과

| 범위 | 통과 | 실패 | 미실행 | N/A |
| --- | ---: | ---: | ---: | ---: |
| 성공 기준 |3|1|2|0|
| 조건부 복구 |1|0|0|1|
| 전체 |4|1|2|1|

평가 완료2세션의 outcome은 실패1·미결론1이다. 같은 두 사람의 r6 성공 기준 미실행3개에서2개로 감소해 기계 gate는 `smoke_passed`다. 그러나 남은 경로에서 결정적인 실행기 결함을 확인했으므로 **이 버전으로32명 확대하지 않고 수정 후 새 스모크로 확인하기로 했다.**

- 016:14턴, 정상 완료. 진행 중 실제 취소·저장 보존과 크기 경계는 통과, 직접 저장 재시도 버튼 누락은 실패다. failed reason 관측 수용 오류는 해결됐다. 의도된 저장 실패 시험 외의 우발적 복구 상황이 없어서 recovery는 N/A다.
- 029:31턴, 정상 완료지만 sample export만 통과했다. 보관 fixture는0개 실행됐고 보관·paywall은 미실행이다. 화면 밖 대상 클릭을 dispatch하지 않고 새 관측 후 보이는 대상으로 복구한 obs4→5는 recovery 통과다.
- 완료 영수증 host_protocol0, 제외 시도0, queued/running/uncertain0. 이전 큐 무변경과 소유 브라우저 종료를 확인했다.
- 실제 요청49/call ID47, 완료 응답 품질 수정2, 불확실 재전송0·미확정 guard0. TOKENMAXX 무료 경로만 사용했고 fallback0이다.

## 실행기: wheel 좌표가 활성 모달 밖에 있음

동결 driver의 scroll은 항상 `Input.dispatchMouseEvent(mouseWheel,x=500,y=400)`이다. 실제756×413 viewport에서 history sheet는 대략x118…638,y96…318이다. 따라서 wheel을 모달 밖 하단/backdrop에 보냈다.

obs19 이후 `+300,-400,-400,-400`을 실행했지만 obs19–23 PNG가 모두 동일하다. 닫기 obs24는 정상 실행됐고, 이후 모달 재진입과 obs26·29·30의 scroll도 같은 PNG를 유지했다. 입력 대상 문제이며 브라우저 전체 정지는 아니다.

029 job은 `S-lihpcgliffanjnflfmgfpgad`다. 증거는 `stage-2/sessions/S-lihpcgliffanjnflfmgfpgad/evidence/S-lihpcgliffanjnflfmgfpgad/1/`의 `browser-00171.png`, `browser-00195.png`, `browser-00253.png` 등이다. 공통 SHA-256:

`e029fa773bb6ce590fe595e6733014d0c712307a391df72fc820e3d3c2169b08`

고정 제품51110f4의 `src/styles.css`는 폭600px 이상에서 sheet 위·아래96px를 비워 이 viewport에서 높이221px를 허용한다. 헤더/푸터를 제외한 약84px의 body는 `overflow-y:auto`이며, 보이는 관계 기록 개요 아래에 탭이 있다. `Sheet.tsx`는 배경 body를 잠근다. **정확한 내부 scroll 치수는 기존 관측에 없지만, 저장 화면과 소스로 확인한 것은 좁고 스크롤 가능한 body다. 초기의 zero-height 추정은 확정 제품 결함으로 보고하지 않는다.**

수정은 실제 노출된 modal scroll 영역 안으로 wheel을 보내고, 전후 위치와 실제 이동 여부를 관측하는 것이다. 테스트 viewport를 키워 문제를 숨기지 않는다. 두 번 같은 방향으로 이동이 없으면 같은 모달 재진입을 반복하지 않고 다른 실행 가능한 필수 과제를 먼저 수행하도록 설계한다.

## 과제/fixture: Pro 설명의 선행 기록이 부족함

`RelationshipHistorySheet.tsx`에서 탭은 기록2개부터 표시되고 날짜 선택기는 `기간 비교` 선택 후 표시된다. 무료 상태의 날짜 선택기는 의도적으로 비활성이다. `Pro 기능 보기`는 최신 비교 쌍 외에 오래된 비교 구간이 있을 때만 표시된다.

따라서 과제는 보관 시험이 함께 있으면11개 보관 입력을 먼저 끝내고 previous/current 쌍을 준비해야 한다. Paywall만 있는 과제는 기존 동일 계정 retention01을 오래된 기록으로 먼저 넣고 previous/current를 준비한다. 없는 Pro 안내를 두 기록 상태에서 계속 찾게 해서는 안 된다. fixture 등록과 실제 mandatory-step preflight에도 이 선행조건을 반영하며 판정 기준 자체는 약화하지 않는다.

## 원본 무결성 참조

- report SHA-256:`c06e2bc7968288a3bd3b6d8b8f9f95991021516eaefe7eea206d0ba0915a7c67`
- stage-summary SHA-256:`e830cf34e4c4eed51eee4896b72177bd00cc9b43317e067e2d59bd78ce4f72a3`
- router ledger SHA-256:`36cfbb37c05ffba938bb8d77b182e635cfdcca250ce81a72e6de01930b65ed1b`

이 스모크는 디버깅 증거로 보존하며 최종32명 집계에 더하지 않는다. R1의 불확실 내부 재전송 사고, R2의 실패 이유 수용 오류도 각각 별도 진단 문서에 보존했다.

## 종료 후 수정과 실제 브라우저 회귀

실행기는 활성 modal과 내부 스크롤 영역을 측정하고 hit test를 재확인한 뒤 native wheel을 한 번만 보낸다. 짧은 body에서는 실제 보이는 높이의80%로 이동량을 제한하며 요청량·적용량·실제 이동·배경 이동을 관측에 남긴다. 높이가 없거나 가려졌거나 경계에 도달했으면 전송하지 않는다.

로컬 `about:blank` fixture와 임시 소유 Chrome 프로필 하나에서 실제 검증했다. 모달 body84px에 요청400px를67px로 적용해 `scrollTop:0→67`, 아래쪽에 가려진 control의 가시성·hit test 통과를 확인했다. 배경은 움직이지 않았고 기존(500,400)은 모달을 움직이지 못했다. 높이0·내용이 모두 들어감·가림의 세 경우는 모두 wheel을 보내지 않았다. 페이지 네트워크 요청0, 프로필 제거 완료다. 실제 기본 viewport는756×432였으며 viewport override는 없었다.

검증한 driver SHA-256은 `dcddb4069f3103da5c66ed3da3a3927eee83c1d5759c648d5521de664de8b4a5`다. 디렉터리 `.ux-loop/peekly-scroll-regression-20261114-dE8wr9/`의 증거는 다음과 같다.

| 파일 | SHA-256 |
| --- | --- |
| result.json | c95c02368b957b045a481e1cc6092da9d5fe51e5e1d9729b5e87ecf1e3f0fee9 |
| before.png | e04bd32adee7dd1219ae9de9b31d9af1f6680708648f9649edbc0cdd7242a825 |
| after.png | e8fd07f104d882d95d033ff5fe0ccc8cf525a6aadd11eda4f351e7e0c8e94bc2 |
| focused-tests.log | 86dea45fc6a978d5e3e460c541a5413203b8a2e30fc3d62f0b68fee5ce2c4ba9 |

과제 수정은 보관→paywall의 의존 순서, paywall 단독의 오래된 세 번째 기록 preflight, 비교 쌍 재사용, 기간 비교 탭/Pro 설명의 명시적 단계, 이동 없는 반복의 제한이다. task/fixture/launcher31개 테스트와 driver/evidence/admission31개 Python 테스트가 통과했고 후자에30개 Node guardrail 사례가 포함된다. 판정 기준·제품 소스·테스트 viewport는 바꾸지 않았다.

변경 전체에 대한 최종 unittest discovery는1,718개 중1,697개 통과·선택 의존성21개 건너뜀·실패0개로 종료됐다(198.965초). 로그는 `.ux-loop/peekly-coverage-r4-regression-20261114.log`, SHA-256 `909b3b9362a540f3baf4df48232cd0dbfa9f2e077613ef0164a3a15f0e799983`다. 실제 다음 스모크의 오프라인 점검도30개 이전 큐·293개 이전 job ID를 보호하며 통과했다.
