# 첫 스모크 진단 — 보존된 실패 실행

이 스모크는 최종 확대 승인 자료로 사용하지 않는다. 기존 원본 큐·영수증·라우터 기록은 수정하지 않았다. 구현 bf5e651, fixture v6, 페르소나016/029로 2026-11-14T04:00:52Z에 시작했고 04:18:20Z에 실행기 오류로 종료됐다.

## 저장된 상태

- 실행 루트: .ux-loop/peekly-coverage-smoke-20261114/
- 상태 파일: run-status.json — stopped_preserved, 기존27개 큐 불변 확인 true.
- 큐: stage-2/queue.sqlite — 016 complete, 029 running으로 남은 부분 실행. 후자는 활성 프로세스가 아니라 종료 시점의 보존 상태이며 재개하지 않는다.
- 모델61개·도구60개 operation이 done. 029의 다음 도구 결과는 수신됐지만 관측을 체크포인트에 추가하는 단계에서 용량 검사가 중단했다.
- 종료 후 해당 실행 프로필을 사용하는 Chrome 프로세스0개 확인.

## 실행기 결함: 전달 불확실 요청의 내부 재전송

기존 model_router.py는 transport_or_protocol_error를 재시도 대상으로 취급했다. 이 경로를 실행 전에 놓쳤고, 첫 스모크에서 사용자 조건인 불확실 재전송 금지를 위반했다. Queue의 uncertain 작업을 재개한 것은 아니지만, 라우터 내부에서 같은 call_id가 다시 전송됐다.

증거: stage-2/model-router-ledger.live.json. 다음4개 호출 ID에서 TimeoutError5회와 그 뒤 재전송5회를 확인했다.

| call_id | 타임아웃 | 저장된 이벤트 순서 |
| --- | ---: | --- |
| op-653bfcd63aeb13b1783b1820f69b04617ebfb6e1 | 1 | transport_or_protocol_error → success |
| op-795cd7997caa94d8f2d7474dd5c385757393d717 | 1 | success → quality_rejected → transport_or_protocol_error → success |
| op-a30b2f09238e07f1805310fcfed197b4f5269cf7 | 2 | transport_or_protocol_error → transport_or_protocol_error → success |
| op-e03c0960139954cd75bcbdaa86e9204fe71f7fe0 | 1 | transport_or_protocol_error → success |

수정은 전송 직전 intent의 영속 기록, 불확실 call_id의 재사용 차단, timeout·전달/응답 불확실 시 즉시 ProviderUncertain, fallback 금지다. 불확실 요청은 재전송0회다. 응답을 완전히 받은 형식 오류 등에는 원래 요청의 남은 시간 안에서 최대2회 보정을 허용하며, 요청 timeout은150초다. 기존 큐 상태 불변과 라우터 요청 불확실성은 별도로 검증한다.

## 실행기 결함: 긴 세션 체크포인트 한도

029의 저장된 체크포인트는1,046,298bytes로 기존1,048,576bytes 한도에 근접했다. 전체 관측42개가983,187bytes, receipt preview가62,538bytes였고, 이미 완료된 다음 도구 응답24,044bytes를 추가할 수 없었다. 오류는 Queue data must be bounded finite JSON이었다.

모델 입력 축약만으로 이 저장 한도는 해결되지 않았다. 수정은 체크포인트 저장에 한해 승인된 턴 수와 관측별 상한으로 계산한 제한을 적용하며, 모델 요청256KiB·개별 관측 내용64KiB·일반 결과 한도는 유지한다. 실제 크기와 비슷한543개 fixture/36개 controls를 포함한 두 세션이63개 전체 관측을 보존하고64번째 턴에 완료되는 회귀 검사를 통과했다.

## Fixture 결함: 인식된 JSON 합계 초과

016 obs-9의 upload_cancel은 읽기1ms/분석50ms 상태를 관측했지만, 이후 파일 합계64MB 제한 오류가 나타났다. 취소는 실제 전송되지 않았고 저장 상태는 같았다. 이는 취소 기능의 제품 실패가 아니다.

v6의110,401,587bytes ZIP은 실제 관계 JSON이 제품의 인식된 JSON 합계64MiB 제한을 넘었다. 새 v7은 ZIP57,961,041bytes, 인식된 JSON57,960,093bytes다. 같은 계정의42만 원본 행을 포함하며, 고정 제품51110f4의 실제 파서에서 정상 처리됐다.

검증 자료: .ux-loop/peekly-parser-offline-v7-20261114/parser-result.json 및 raw-validation.json. ZIP SHA256은0aa68b7cb60516f22372d4e2c030957a033787a0e4a06092a7d4f33608ea0d79, manifest SHA256은4df650d58c2105bc67ca3eec27c826b1f8129f8f1a846b396a4eb9e53c48f44a다. 오프라인332.755ms 처리 시간은 브라우저의 취소 가능 시간을 보장하지 않는다.

## 제품 결함과 판정기 오분류: 저장 실패 후 직접 재시도 누락

016 obs-13에서 peekly_state_v7 쓰기 실패가 실제 소비되고 해제됐으며 기존 저장값 해시가 유지됐다. 화면에는 저장 공간 부족 안내와 다른 파일 고르기만 있고 다시 저장 버튼은 없었다.

고정 제품 docs/PRD.md §3은 쓰기 실패 시 안내와 다시 저장 버튼을 요구한다. src/App.tsx의 가져오기 저장 경로는 실패 시 새 상태를 적용하기 전에 예외를 발생시키며, src/components/ExportWizardModal.tsx의 해당 오류 분기는 파일 재선택만 제공한다. 이는 **P2 제품 결함**이다. 재업로드 성공은 우회 방법이 될 수 있으나 누락된 직접 저장 재시도를 충족하지 않는다.

기존 판정기는 다른 오류 문구와 다시 저장 문자열을 동시에 요구해 이를 not_run으로 남겼다. 원본 영수증은 그대로 보존한다. 수정된 판정기의 별도 읽기 전용 진단은 같은 관측을 failed로 판정했다. 수정은 실제 오류 문구·동일 시도·소비/해제된 fault·보존된 저장 상태·완전한 안정 상태 controls를 요구하며, 전이 중이거나 잘린 controls로는 실패를 확정하지 않는다.

## 다음 실행

새 fixture와 위 수정·회귀 검증을 고정한 뒤 별도 smoke-r2 루트에서016/029를 새로 평가한다. 첫 스모크의 작업 ID는 금지 목록에 들어가며 재개하거나 재전송하지 않는다. r2의 완료 영수증2개와 미실행3개 미만을 확인한 뒤에만 고유32명 코호트를 실행한다.
