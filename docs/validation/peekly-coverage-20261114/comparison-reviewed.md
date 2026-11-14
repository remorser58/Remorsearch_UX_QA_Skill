# Peekly coverage comparison — 독립 증거 감사

| 항목 | 696dbe3 | cb0188d | ee4b145 | 신규32명·증거감사 |
|---|---:|---:|---:|---:|
| 완료·평가 세션 / 고유 페르소나 | 32 / 32 | 32 / 32 | 24 / 15 | 29 / 29 |
| 세션 통과 / 실패 / 미결론 | 0 / 2 / 30 | 6 / 4 / 22 | 1 / 6 / 17 | 9 / 8 / 12 |
| 전체 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 56 / 4 / 42 / 34 | 35 / 6 / 46 / 17 | 71 / 8 / 23 / 19 |
| 성공 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 51 / 4 / 42 / 7 | 28 / 6 / 46 / 0 | 62 / 8 / 22 / 0 |
| 복구 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 5 / 0 / 0 / 27 | 7 / 0 / 0 / 17 | 9 / 0 / 1 / 19 |
| 완료·평가 세션의 host_protocol | 미보존 / 미확인 | 미보존 / 미확인 | 0 | 0 |

## 집계 범위

신규 요청 32명 중 완료·평가 29세션을 분모로 사용했습니다. 미평가 3건은 세션·기준 판정에서 제외했습니다.
ee4b145의 24세션은 고유 페르소나 15명입니다. 기존 46행은 동일 페르소나의 반복 세션을 포함합니다.
696dbe3의 전체32 결과는 cb0188d.before로 교차 확인했습니다. 696dbe3 run-summary의 마지막16 결과와 혼합하지 않았습니다.
cb0188d의 성공 기준 N/A 7개는 당시 데스크톱 범위 판단을 보존합니다. 신규 영수증의 N/A를 임의로 재분류하지 않았습니다.

## 기존 미실행 기준의 대응 결과

| 집계 | 기준 수 | 통과 | 실패 | 미실행 | 미평가 |
|---|---:|---:|---:|---:|---:|
| 기존 세션 가중치 유지 | 46 | 20 | 8 | 18 | 0 |
| 고유 페르소나·요구사항 | 32 | 13 | 6 | 13 | 0 |

실패로 바뀐 기준도 실행 범위에는 포함되지만 제품 개선을 뜻하지 않습니다. 신규 N/A는 실행 감소 성과로 세지 않습니다.

## 신규 미실행

| 요구사항 | 기준 수 | 페르소나 |
|---|---:|---|
| CONDITIONAL-RECOVERY | 1 | PER-PEEKLY-V2-013 |
| PRD-IDENTITY-LIMIT | 1 | PER-PEEKLY-V2-022 |
| PRD-IMPORT-SNAPSHOT-UNKNOWN | 4 | PER-PEEKLY-V2-021, PER-PEEKLY-V2-022, PER-PEEKLY-V2-023, PER-PEEKLY-V2-024 |
| PRD-PAYWALL-BOUNDARY | 4 | PER-PEEKLY-V2-029, PER-PEEKLY-V2-030, PER-PEEKLY-V2-031, PER-PEEKLY-V2-032 |
| PRD-RESULT-MUTUAL | 4 | PER-PEEKLY-V2-017, PER-PEEKLY-V2-018, PER-PEEKLY-V2-019, PER-PEEKLY-V2-020 |
| PRD-RESULT-RECIPROCITY | 4 | PER-PEEKLY-V2-017, PER-PEEKLY-V2-018, PER-PEEKLY-V2-019, PER-PEEKLY-V2-020 |
| PRD-RESULT-REVERSE | 4 | PER-PEEKLY-V2-017, PER-PEEKLY-V2-018, PER-PEEKLY-V2-019, PER-PEEKLY-V2-020 |
| PRD-RESULT-SEARCH | 1 | PER-PEEKLY-V2-025 |

정확한 저장 사유와 증거 참조는 reviewed-summary.json의 candidate.not_run_by_requirement에 보존했습니다.

## 저장된 실패 판정

- PER-PEEKLY-V2-013 / PRD-IMPORT-SAVE-FAIL: The one-shot write fault was consumed and prior state preserved, but only 다른 파일 고르기 was offered; no 다시 저장 retry action appeared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pggllnfpmomgbiaefciinnlo/evidence/S-pggllnfpmomgbiaefciinnlo/1/agent-observation-15.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pggllnfpmomgbiaefciinnlo/evidence/S-pggllnfpmomgbiaefciinnlo/1/browser-00245.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pggllnfpmomgbiaefciinnlo/evidence/S-pggllnfpmomgbiaefciinnlo/1/browser-00257.png
- PER-PEEKLY-V2-014 / PRD-IMPORT-SAVE-FAIL: obs-13 shows the one-shot fault consumed and prior result preserved, but the required 다시 저장 retry control was absent; only 다른 파일 고르기 appeared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-oheandojgflaijgkoigockdl/evidence/S-oheandojgflaijgkoigockdl/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-oheandojgflaijgkoigockdl/evidence/S-oheandojgflaijgkoigockdl/1/browser-00231.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-oheandojgflaijgkoigockdl/evidence/S-oheandojgflaijgkoigockdl/1/browser-00243.png
- PER-PEEKLY-V2-015 / PRD-IMPORT-SAVE-FAIL: obs-11 consumed the one-shot write fault and preserved the prior hash, but no 결과를 저장하지 못했어요 alert or visible 다시 저장 control appeared; only file re-selection was offered. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00216.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00228.png
- PER-PEEKLY-V2-016 / PRD-IMPORT-SAVE-FAIL: obs-11 shows a save-failure notice with prior state preserved, but no 다시 저장 retry control existed (only 다른 파일 고르기); the required retry text and path were therefore untestable and absent. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mjpfaichoklgmcfglleieclo/evidence/S-mjpfaichoklgmcfglleieclo/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mjpfaichoklgmcfglleieclo/evidence/S-mjpfaichoklgmcfglleieclo/1/browser-00215.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mjpfaichoklgmcfglleieclo/evidence/S-mjpfaichoklgmcfglleieclo/1/browser-00227.png
- PER-PEEKLY-V2-025 / PRD-PRIVACY-DELETE: The final confirmed deletion was actually dispatched and hit-tested. The saved digest returned from imported data to the initial empty-state digest, but final storage_keys and storage_snapshot.keys still contain peekly_state_v7. Prior relationship data was cleared; the failure is the pinned PRD's final key-absence contract, not retained personal data. This preserves the original failed session when combined with the independently corrected SEARCH not_run; baseline execution credit is unchanged. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-1.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-5.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-12.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-14.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-15.json
- PER-PEEKLY-V2-026 / PRD-PRIVACY-DELETE: Deletion was confirmed, but storage_keys still included peekly_state_v7; required local state key absence was not verified. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/browser-00152.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/browser-00162.png
- PER-PEEKLY-V2-027 / PRD-PRIVACY-DELETE: Deletion confirmation was inspected and 모두 지우기 clicked, but storage keys peekly_state_v7 and peekly_theme_preference remained, so app state was not cleared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-14.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/browser-00142.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-15.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/browser-00152.png
- PER-PEEKLY-V2-028 / PRD-PRIVACY-DELETE: obs-14/obs-16 showed 데이터 삭제 and 모두 지우기 confirmation; obs-17 completed deletion but peekly_state_v7 remained in storage keys, so absence was not verified. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-14.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/browser-00133.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/browser-00153.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/browser-00163.png

실패 목록은 저장된 판정이며 제품 결함·실행기 결함·판정기 오판의 최종 분류는 별도 검토가 필요합니다.

## 경로와 비용

- 설정 경로: ['TOKENMAXX/deepseek-v4.1-flash-free']
- 실제 시도 경로: {'TOKENMAXX/deepseek-v4.1-flash-free': 716}
- 대체 모델 시도: 0
- 정책 비용 USD: 0
- 비용 필드 누락 응답: 716
- 공급자 청구 확인: 미확인

A configured free route and policy cost of zero do not verify provider billing; missing cost values remain missing.

## 신규 코호트 전달 감사

- 저장된 전달 정책: {'durable_call_id_guard': True, 'known_reply_retries': 2, 'timeout_seconds': 150, 'uncertain_resends': 0}
- 정책 일치 / 원장 감사 유효: True / True
- 실제 요청 응답 기록: 716
- 완료 응답 재시도 / 품질 복구: 13 / 13
- 품질 거절 진단 기록: 13
- 불확실 재전송 위반: 0
- 불확실 재전송 0 검증: True
- 불확실 이벤트 call ID: ['op-18227db7f9a6613db748a47c07fc445e1a3be89e', 'op-292b477d2281398ef8342b62b43ebf0af839f467', 'op-dd6d53ae98aa580084e278abdcc357d405ad67ce']
- 불확실 / 미결 전달 guard call ID: ['op-18227db7f9a6613db748a47c07fc445e1a3be89e', 'op-292b477d2281398ef8342b62b43ebf0af839f467', 'op-dd6d53ae98aa580084e278abdcc357d405ad67ce'] / []
- 위반 call ID: []
- 감사 오류: []
- 원장 SHA-256: faabef17810a83ee8f654fe12efaad9e1a1f36e3151deb1b6edeea915f985250

Known completed-reply repairs are distinct from resending an uncertain delivery. Quality-rejected diagnostics are not additional provider attempts.
이 감사는 신규 코호트 원장에만 적용되며 이전 smoke의 재전송 사고 기록을 변경하지 않습니다.

## 숫자 출처

- .ux-loop/peekly-coverage32-20261114/stage-32/report.json — SHA-256 65fa786a45d3f23f78b9eebfc83d1ba85dcc593180171408fa4e780869d70992
- .ux-loop/peekly-coverage32-20261114/stage-32/stage-summary.json — SHA-256 60a92258f06625a976836aa60f198709261e4684904bdcda2f05c85b802d5a90
- .ux-loop/peekly-coverage32-20261114/stage-32/plan.json — SHA-256 b8f4384c0c2d5632cdebed691007a252b1a73c2858e1e870d687a4a66656292e
- docs/validation/peekly-coverage-20261114/not-run-baseline.json — SHA-256 e661c293420ccfef537c444bf7f114e72f8e07a7e062ad554abe539177799cee
- 696dbe34e92247ed1b139662577f799b8595baaa:docs/validation/peekly-ux-findings-20261113/run-summary-32.json — SHA-256 622d1d21e15d37f467443b95e80d486477769e0459faa9f21cfa0f70eedbde0d
- cb0188ddf420b3b019facbafef75bde619365a41:docs/validation/peekly-verdict-quality-20261113/verdict-quality-summary.json — SHA-256 c04d166c6fa313bc3fc5a7bbf6ee4f1ea9562984cccbaef49dbf98894a6ace20
- ee4b14571930af428d5a52e0e133deebedba485d:docs/validation/peekly-explicit-success-20261113/summary.json — SHA-256 3b923e06d5df773b2564216d013f997d3d9aa0fbdc2be71feb3639246c536f84
- ee4b14571930af428d5a52e0e133deebedba485d:docs/validation/peekly-explicit-success-20261113/final-session-ledger-20261114.json — SHA-256 c11febc7ae6d12d69067237397145e4c4240a689143df926417a1036e7cbaf5d
- .ux-loop/peekly-coverage32-20261114/stage-32/model-router-ledger.json — SHA-256 faabef17810a83ee8f654fe12efaad9e1a1f36e3151deb1b6edeea915f985250
- .ux-loop/peekly-coverage32-20261114/run-status.json — SHA-256 70df5faec4c5b40556e4ec504dddb186113d27e797eb858795886e1d58ea7692
- docs/validation/peekly-coverage-20261114/review_coverage_results.py — SHA-256 d53648efb76c8da1d6205420acc507b0d674828155e56584cf675e92fde0351e
- scripts/report_peekly_coverage.py — SHA-256 e41251fc8221c9c02caa92ad42d2dd835af3cee971936c51aa959c25abe87044
- scripts/run_peekly_coverage.py — SHA-256 ea94906905b7d83e91d91c24bbb5b51237c2051a5d988f222770738930a95d60
- skills/remorsearch-ux-qa/uxresearch/canonical.py — SHA-256 fb7d200081fb8f91c2fb190195e8528feee4f9f32e4868c9e3c77634775afd73
- docs/validation/peekly-coverage-20261114/summary.json — SHA-256 e958af0066496a4a6dc3196fd64aa29978ec8d3e8f7139e238cddd6ba1d754a8
- docs/validation/peekly-coverage-20261114/criterion-review.json — SHA-256 3ac5e263fde82463b70a9fe881d922996248c481f4076ce190937bb101108ab0
- docs/validation/peekly-coverage-20261114/artifact-audit.json — SHA-256 18f249b296c0bd6d6a11b56ff1e6723d0a4004d8f4cd57d848edd48def30bbe0
- docs/validation/peekly-coverage-20261114/comparison.md — SHA-256 2d1ea0f94b26e9a39d21340d358005ec9c7e348178532db1f255adabec954d21
- .ux-loop/peekly-coverage32-20261114/stage-32/queue.sqlite — SHA-256 6a86213d2a02b69c9d7db4ad0b9329adb36fdaa39f2d4d213c0c31039c767ff1
- .ux-loop/peekly-coverage32-20261114/input-provenance.json — SHA-256 ec34b86289574d46580c0d972c04024255db5fe46f728ef9fb701afa8af45609
- docs/validation/peekly-coverage-20261114/audit_final_artifacts.py — SHA-256 78a7bce46cd9b6b2587e8df1446e7054397a31c11395f52baed3cdd4c2d2e310
- .ux-loop/peekly-coverage32-20261114/stage-32/queue.sqlite-wal — SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- .ux-loop/peekly-coverage-fixtures-v7-20261114/fixture-manifest.json — SHA-256 4df650d58c2105bc67ca3eec27c826b1f8129f8f1a846b396a4eb9e53c48f44a
- .ux-loop/peekly-coverage-fixtures-v7-20261114/peekly-oversize-plus-one.zip — SHA-256 7ea6ce492b9f2e83db0190808df466a16da53a11f25ba786f46c26821243c687
- .ux-loop/peekly-coverage-fixtures-v7-20261114/loose-file-over-32mib.json — SHA-256 731c45e3c9c8745df747dd8681fcc66ee441a74a2c1b105e83ea7429b1a50f36
- .ux-loop/peekly-coverage-fixtures-v7-20261114/loose-total-a.json — SHA-256 3ff845206ecc527b793b7133d1cc70aaf0991f2c753c69f17a5498c0861336ac
- .ux-loop/peekly-coverage-fixtures-v7-20261114/loose-total-b.json — SHA-256 d653c362855eadd8c8ede2dc66856356c60dae1be25d4a8c64c384a187634ffb
- .ux-loop/peekly-coverage-fixtures-v7-20261114/loose-total-c.json — SHA-256 ccef47ec2ff27446d89887df6d44f1e434d256612ff98e6988166aef1503ba93
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-4.json — SHA-256 6c782df70582bbad1cfeafbb59bdb5fd5da42d0b741632b3500a88f2b1f165e7
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-13.json — SHA-256 7e6bb24481c0948f9a1f1ddb13a48c6b2b31b756b3a23bb3649c48a34b1d83a2
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-16.json — SHA-256 cbd8ac13a16de748d0a20c60a9fa1b0aaaff6bd35951b9cfd2f7108b7baaac79
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-17.json — SHA-256 9976a543a58a0409bfba6d33baaec5cf4018e8206ce05d4a0ef59adaa5d05406
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-18.json — SHA-256 7cd8b438c97088c5598a19891d0131d90a3699fe08458ac69ea0879abfc9802f
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-6.json — SHA-256 2c802a801f12f4c2405b8c60550e13e904abee497c6726fe98cbb73d90f5f654
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-8.json — SHA-256 5eed4b945330f033fcd7e2956028aa3372f132a0185e960917694619a3169497
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-4.json — SHA-256 5f9fbf164cbb4867a543f87a91b87a3363c90648e66029d29caa9e16fe4ddf12
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-13.json — SHA-256 a3b2990fe71dd269a04ec891fe7d20336a2500813ecc2eeb851b2ca130a834be
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-16.json — SHA-256 5bc96580d273f52f078daed381f7fc2154e8a801e85864208a1cf80e0347be0b
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-17.json — SHA-256 5a37f88ed0c56a81e5fd02e24bc971afe8499e5cac44ecb602066b0759a152b4
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-18.json — SHA-256 b585ccc7b27725fea35a7e48a9226b0d23a827cc783889e9baaab6464bdf9908
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-6.json — SHA-256 f00ad89ec0307c7ff2ca4a59c4fd97d26dbb9c0f79c611b83d2a08c10901d6b1
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-8.json — SHA-256 71f8085a66b4060b0a6cd2e2bc1dba9b6e297ea29c75f5c462e59af0bed83e15
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-7.json — SHA-256 605ceb24bb3fcdf666b9b4b770a03babbdae0717326e63da4aded7ad3f76487b
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-16.json — SHA-256 4a00c2a56b88e1315aeb2d39d2cc440a0e44b70e1f148f38b850fa433f000fa3
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-19.json — SHA-256 aab5228e07537cb830a42fd47e2b2d2144d4c4e77bb0f27da5458f450806874a
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-22.json — SHA-256 1ccab05db66f61cfd68ef16cfbcb02bffcf850f66ce577696ea723792e0345d6
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-23.json — SHA-256 7a6eef9594d3f703207739e276fbbad2c704161b6b98b0f0e21f6b73a44127b0
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-9.json — SHA-256 9f5c211f86263e519e793c8f6aa3a33e3b32753f9c3ff1ff00a3b5ad9b665278
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-11.json — SHA-256 8a7cd819801bc77fcd5b3649b2390b15f379051df5503022d7bbbc16e4d842ef
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-4.json — SHA-256 161844546b9d8ee4f369d912d0088ca0fa8cb8e042d5111f929b6c872bdae257
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-13.json — SHA-256 740d8ff38a4990087cf55e254adb168468d7a14295c195b4769c5a76b8d38e6b
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-16.json — SHA-256 ce769e05cb4124c800b108609379210ffd5b419bd66c1bc0a4be9bec6ac493e7
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-17.json — SHA-256 d2ac56f993c00c6e15c98ac9f7d0064af2b8a31a2f6c48c2c44e20562cee71d7
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-18.json — SHA-256 5bdc00ddf45708b552005c1c2df36bf854cf795c76b583746220e072c7fb4111
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-6.json — SHA-256 5e6556d4c340851014595a331995411366895ab2b3ed2335ac7dafcc4106c0b8
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-8.json — SHA-256 fdbeacade6372baf5ac0c3cc1f5b7b5e92ac8362c94e8c5d7b813ea6f00ee4ed
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-10.json — SHA-256 b7708b415b312b9422de6f4863e499b965f7487667074454839556215aaa0bd3
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-11.json — SHA-256 66689a860b040eec3624844cd7f3d1ec608bb650cf530b23fdaeb12bf4dd4b6c
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-14.json — SHA-256 64ef36b4db90eeda03f1979deab1eeb0e5313cc664e23307771588784decfa42
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-15.json — SHA-256 f1c22588d15ab38f8162f5e18839ea0cc16ea3de1c6ccfe5a29425fa9edf74b0
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-7.json — SHA-256 8a8e15b2dabc9b180355c8870d56c3d50d3bb5e30b46c952043931578958985c
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-10.json — SHA-256 573ad3f096d79d2595a52fa70abb26b4c5bfced3dfe051d1e1d2a423596d8c46
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-15.json — SHA-256 ad422371d4601acbcd8c0e57f75d43d596d9bd24c2c4fcb386269941ba99b22d
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-18.json — SHA-256 ea473f1fc0b6ebe23580b193a915e7b8e5e3e7e35a5c7270f06420f197e0f46a
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-21.json — SHA-256 b1a3d2f33d206d777d9857fc353747babfd18757ae4bf95eacadd885830be88f
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-7.json — SHA-256 57146e8398fc93ab549e6bfc6e6b422a86da07160e91fcade4092d7502632355
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-10.json — SHA-256 3dc288cbecff51e949b320909852d66bfd1fe661cb93dd2aca72355693fc52d4
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-13.json — SHA-256 f4c8ae602b3e697302bd975fce472da9850555df5fe26354816f4ce80cf75df2
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-19.json — SHA-256 607a4fcc56367c9fcd847802914c154d47adade4539f6931ad82ba353fc28a04
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-22.json — SHA-256 d250caf7452bc160baba7ae87fbd8e1db28664b57e99072c1e5dba5dc67bc535
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-24.json — SHA-256 71d5efd4b0f30e1022d402200427badd1d7c8a25cb2dda9a448abe511cd95a82
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-6.json — SHA-256 55dfdbde5b9b3b09f603a87a8d61312df829f1c6d18bd425e1d4417abc05f4e0
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-9.json — SHA-256 a8a5713a82e2da15966ed6383ecb97ca2ab0a62abcb9356343cf01753b160514
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-18.json — SHA-256 5d0fab7439aea0636cec8d39cb18d277dff79acb3ef462da993c1c960d4e415f
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-21.json — SHA-256 5254088ab76b1d02ea9bb81cbede3dcadd34f4fade87c31803811c99138f1ecd
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-44.json — SHA-256 2e66797118ba07730350149a387694007e02a8a84c04bbe6f3b41777e924056b
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-45.json — SHA-256 96196dbae426594d81e4f4eb376090ffd53f078778a1a43d1ec3be50b630e145
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-46.json — SHA-256 bbe6d85f800621838a573c76bd8d96bb531d54ec6f9c088d8987ca249600ed96
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-8.json — SHA-256 0557bd09f72ba829557c87c783ef2824837575ff7f93e2120bd8e1c88cf0c493
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-11.json — SHA-256 02b8ec662ab198737e207dfeec857eae4502b34b29c3899232141de648bea366
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-13.json — SHA-256 fdfce6b657ea9a6454e59c7611016d293e3e33a854b734ee8c4e27e7c6ed8ea8
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-16.json — SHA-256 ff12e8cd33d637da9ae38fa7a182d84e0846a710e9db1e8d111ead922bb355fe
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-30.json — SHA-256 2446aa86f4062abd5be0e0cfd6db659a7fc2c9e00601b1065185100df9e0d1b8
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-33.json — SHA-256 ff1b3120425b6f35d521f4ef3920a9421de4c4f7b7caf9078d35d1a63d380551
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-35.json — SHA-256 6ddd1a3f097e03522907a6f7498c30f51c8115b8dd1d2b496d8f76a23bbf2ca8
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-6.json — SHA-256 9956d75294321ca79a02ccb4fc5b61dae2c446a6254eaa62e06484cef9bda918
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-7.json — SHA-256 56ce59a49f6b8147eecca0f50ba4c92f3fb7cade582705f12c8742fe001690f6
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-5.json — SHA-256 a456dd421828f520f26dc40c8ee7e8b5b09d6c89a6e52a3725ecec2ff1d6d916
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-6.json — SHA-256 9b0991d3099a9f4693713175021a2fe28910b9badc6c115a79f9179b96aa91f5
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-7.json — SHA-256 bcf826cd1cd2a4b044ddd33c079050d4a2f968fba6e8a7c7c4b8883ed9a27c83
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-4.json — SHA-256 16db474d32fa8a52d3e89b3d7e5b31db16e28f16f1e747c17b35dc3f19741f84
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-5.json — SHA-256 a457ac842dd0414ccb2e878da0ea6640b1ab057c058c89cd3d1e656dec67459b
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-6.json — SHA-256 d4e6f437c492b6539c7dd89e6ea5d2dabf0ca7fef18414680f1ad374361ab016
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-6.json — SHA-256 06bb32ab885c560cfd049495d9d4562068bba08f7be21d33b7a7f36e9b0704bd
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-7.json — SHA-256 8e3a59024d898e1154c9830cfe1c29769b235c969db2ae9c11f6ecca1777892c
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-8.json — SHA-256 def0e0a6b4c9f277c0e2dc1eae1254cf73d82fd25d280260bfed2c7ed9a627d4
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-4.json — SHA-256 de8489aafa25076aabee5840d313c1a035cbd81815a0570c64d3a72fde494ac9
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-8.json — SHA-256 b368a85c54e307f2a72e16866c0bf94168424d88faa390fbb896a5e0a7905dd5
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-9.json — SHA-256 7dd60383d2cc6363038017f1c0e08b01044a0651ae36d5c1068df1c8dc7c9fca
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-10.json — SHA-256 e766c4a990bbe71a8ee893fbece079d6efb07f7a2ae41569c9f7d91a25d23a00
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-26.json — SHA-256 08b91aef18464a40ed30472c42fec14fb6ab69e6b3f4d78d1a84f59ae2207f91
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-1.json — SHA-256 db6056ba24042a41f89834ebf6bc6c980891b9f10d9b4e3ba149e8f499984b50
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-5.json — SHA-256 e7a4dd839707a55760eec63137de5f0627ebf4225e3766de2356d50058740a83
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-12.json — SHA-256 13a58570b6d0941b79947fc6a55337f6130dfc30a8cb064daed54eab78858ee8
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-13.json — SHA-256 41d1e52575ee1385feea1cb8d0466e9fc8bf805b5615f7b4cc5037c389fc8676
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-14.json — SHA-256 22bd27837ad52631c6ed75c5dd7281cf91bc49ee844fb88f66eb9934e6afe00a
- .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-15.json — SHA-256 9c24e8c6ef6141f2ffe8809d70aac4cb72364ef65d20ebf55a848b13762763ee

각 비교 열의 source_refs.selector가 사용한 JSON 필드를 명시합니다.
입력 report의 current_valid 기록을 사용했으며 새로운 모델·브라우저 호출이나 이전 영수증 변경은 없습니다.

## 원본 판정과 증거 감사의 차이

첫 세 비교 열은 원본과 같습니다. 네 번째 열 '신규32명·증거감사'는 같은 완료·평가 세션에만 명시된 판정 변경을 적용합니다.
raw summary.json, comparison.md, 원본 receipt·checkpoint는 보존했습니다. 새로운 관측·모델·브라우저 실행은 없습니다.
목록에 없는 판정, 원본 N/A, 불확실·미평가 시도는 변경하거나 실행 성과로 인정하지 않았습니다.

| 집계 | 통과 변화 | 실패 변화 | 미실행/미결론 변화 | N/A/미평가 변화 |
|---|---:|---:|---:|---:|
| 전체 기준 | -7 | -8 | +15 | +0 |
| 세션 | -3 | -4 | +7 | 0 |
| baseline 46행 | -7 | -6 | +13 | +0 |
| baseline 고유 조합 | -6 | -4 | +10 | +0 |

기존 14개 검토 항목은 그대로 보존했습니다. 관계 목록 범위 혼동 12건은 PASS→미실행, 실제 파일 거절 증거를 놓친 2건은 미실행→PASS입니다.
이 14개 항목만의 효과는 세션 PASS −3 / 미결론 +3, baseline 9행·고유 조합 7개 PASS→미실행입니다.
추가 UNKNOWN 선행조건 검토 4건은 PASS→미실행 0건, 실패→미실행 4건입니다. 알려진 빈 목록은 알 수 없는 과거 형식의 전제를 충족하지 않으므로 실행 감소 성과를 추가하지 않습니다.
검색 컨트롤 문구 오판으로 별도 확인된 1건은 실패→미실행입니다. 입력·필터 동작을 실행하지 않은 개별 사례만 적용하며 검색 PASS를 만들거나 다른 페르소나에 일괄 적용하지 않습니다.
실제 검색 실행이 별도로 검증된 3건은 실패→PASS입니다. 같은 가져오기·저장 상태에서 정렬된 12행, 활성 검색 입력, query SHA 일치와 유지, 정확한 1행 필터 결과가 고정 증거에 있습니다.
이 검색 PASS 보정은 원래도 실행된 실패의 판정 변경이므로 baseline 실행 성과 변화는 0입니다. 해당 세션 결과와 DELETE 기준도 유지했습니다.
별도로 확인한 SIZE 1건은 실패→PASS입니다. 정상 저장 기준과 실제 크기 초과 fixture, 128MB·32MB·64MB 거절 안내, 시도별 저장 digest 유지 증거를 결합했습니다.
SIZE 보정도 기존 실패의 재분류이며 미실행 감소를 추가하지 않습니다. SAVE-FAIL 실패와 세션 실패를 유지했고, 구조상 읽을 수 없는 ZIP의 용량 검사가 구조 검사보다 먼저 실행되는 범위를 명시했습니다.
삭제 키 부재 조건을 다시 확인한 1건은 PASS→실패입니다. 실제 최종 확인 뒤 빈 초기 상태의 v7 키가 남은 증거이며, 가져온 관계 데이터가 남았다는 주장이 아닙니다.
025의 SEARCH와 DELETE는 같은 세션이므로 원본→전체 보정 결과를 함께 계산했습니다. SEARCH만 반영한 중간 미결론에서 DELETE가 실패를 복원하는 상호작용을 별도 기록하며 그룹별 세션 변화를 단순 합산하지 않습니다.
전체 세션 전이: failed→failed 5건, failed→inconclusive 4건, inconclusive→passed 1건, passed→inconclusive 4건.
위 표의 전체 변화는 원본 집계와 SHA로 고정한 검토 항목에서 각각 계산해 대조했습니다. 반복 baseline 행의 가중치도 보존합니다.

## 독립 변경 원장

### PER-PEEKLY-V2-017 / PRD-RESULT-RECIPROCITY

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-4; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-jmpokhjegennajnihcaemagh].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: 0ce48eb2ea993433f63c1951f50053aac12a7a11e0a4d953d434286dd2babd78
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[0]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-4.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-18.json

### PER-PEEKLY-V2-017 / PRD-RESULT-REVERSE

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-6; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-jmpokhjegennajnihcaemagh].result.receipt.criteria[kind=success,index=1]
- 원본 result SHA-256: 0ce48eb2ea993433f63c1951f50053aac12a7a11e0a4d953d434286dd2babd78
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[1]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-18.json

### PER-PEEKLY-V2-017 / PRD-RESULT-MUTUAL

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-8; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-jmpokhjegennajnihcaemagh].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: 0ce48eb2ea993433f63c1951f50053aac12a7a11e0a4d953d434286dd2babd78
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[2]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jmpokhjegennajnihcaemagh/evidence/S-jmpokhjegennajnihcaemagh/1/agent-observation-18.json

### PER-PEEKLY-V2-018 / PRD-RESULT-RECIPROCITY

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-4; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-pmfcniapopnnebacajhibjbh].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: 5b7abd2f6b8c2833dfc7a5d9850122a1acb296998371a82dfb73f1d17b135070
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[3]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-4.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-18.json

### PER-PEEKLY-V2-018 / PRD-RESULT-REVERSE

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-6; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-pmfcniapopnnebacajhibjbh].result.receipt.criteria[kind=success,index=1]
- 원본 result SHA-256: 5b7abd2f6b8c2833dfc7a5d9850122a1acb296998371a82dfb73f1d17b135070
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[4]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-18.json

### PER-PEEKLY-V2-018 / PRD-RESULT-MUTUAL

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-8; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-pmfcniapopnnebacajhibjbh].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: 5b7abd2f6b8c2833dfc7a5d9850122a1acb296998371a82dfb73f1d17b135070
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[5]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pmfcniapopnnebacajhibjbh/evidence/S-pmfcniapopnnebacajhibjbh/1/agent-observation-18.json

### PER-PEEKLY-V2-019 / PRD-RESULT-RECIPROCITY

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 23 saved observations were inspected. The category list appears only in sample obs-7; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-jbeffobgjfbgkhkfmfepeohi].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: f2e5b232570cbcc7e384c5d6de66b799cc96931ba70f0dd4ec3e499d707443da
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[6]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-7.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-19.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-22.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-23.json

### PER-PEEKLY-V2-019 / PRD-RESULT-REVERSE

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 23 saved observations were inspected. The category list appears only in sample obs-9; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-jbeffobgjfbgkhkfmfepeohi].result.receipt.criteria[kind=success,index=1]
- 원본 result SHA-256: f2e5b232570cbcc7e384c5d6de66b799cc96931ba70f0dd4ec3e499d707443da
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[7]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-9.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-19.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-22.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-23.json

### PER-PEEKLY-V2-019 / PRD-RESULT-MUTUAL

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 23 saved observations were inspected. The category list appears only in sample obs-11; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-jbeffobgjfbgkhkfmfepeohi].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: f2e5b232570cbcc7e384c5d6de66b799cc96931ba70f0dd4ec3e499d707443da
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[8]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-19.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-22.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-jbeffobgjfbgkhkfmfepeohi/evidence/S-jbeffobgjfbgkhkfmfepeohi/1/agent-observation-23.json

### PER-PEEKLY-V2-020 / PRD-RESULT-RECIPROCITY

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-4; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-efdkbjaecbikgofacjhaaena].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: 759e018f1dcba530fd94ce68b056f046f559d1b893ad552fa849fb857a6b4882
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[9]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-4.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-18.json

### PER-PEEKLY-V2-020 / PRD-RESULT-REVERSE

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-6; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-efdkbjaecbikgofacjhaaena].result.receipt.criteria[kind=success,index=1]
- 원본 result SHA-256: 759e018f1dcba530fd94ce68b056f046f559d1b893ad552fa849fb857a6b4882
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[10]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-18.json

### PER-PEEKLY-V2-020 / PRD-RESULT-MUTUAL

- 판정: passed → not_run; 분류: task_and_judge_scope; 심각도: P1
- 검토 사유: All 18 saved observations were inspected. The category list appears only in sample obs-8; subsequent valid imports have cards but no post-import list for this category. The departed list is a different category.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-efdkbjaecbikgofacjhaaena].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: 759e018f1dcba530fd94ce68b056f046f559d1b893ad552fa849fb857a6b4882
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[11]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-efdkbjaecbikgofacjhaaena/evidence/S-efdkbjaecbikgofacjhaaena/1/agent-observation-18.json

### PER-PEEKLY-V2-011 / PRD-IMPORT-HTML

- 판정: not_run → passed; 분류: judge_rejection_phrase_mismatch; 심각도: P2
- 검토 사유: The named malformed HTML upload was actually rejected with the internal filename and an unreadable-list error; the same-attempt saved digest stayed unchanged. The PRD does not require the evaluator's exact Korean phrase.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-pdalpdmknheojnhkkichdfbm].result.receipt.criteria[kind=success,index=1]
- 원본 result SHA-256: ceec6c68aac9d4e9ecedc5b9ad22b1c5aa7ab9057a8c3411c270d5163891cbf6
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[12]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-10.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-14.json

### PER-PEEKLY-V2-011 / PRD-IMPORT-ACCOUNT

- 판정: not_run → passed; 분류: judge_rejection_phrase_mismatch; 심각도: P2
- 검토 사유: The named account-mismatch upload was actually rejected because its owner differs from the saved account; the same-attempt saved digest stayed unchanged. The evaluator's accepted phrases omitted this observed PRD-compliant rejection.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-pdalpdmknheojnhkkichdfbm].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: ceec6c68aac9d4e9ecedc5b9ad22b1c5aa7ab9057a8c3411c270d5163891cbf6
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[13]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pdalpdmknheojnhkkichdfbm/evidence/S-pdalpdmknheojnhkkichdfbm/1/agent-observation-15.json

### PER-PEEKLY-V2-021 / PRD-IMPORT-SNAPSHOT-UNKNOWN

- 판정: failed → not_run; 분류: fixture_semantics_and_judge_cross_attempt_attribution; 심각도: P1
- 검토 사유: The ZIP contains recognized explicit empty lists, not unknown legacy history. Native failed first appears after a different previous/current pair because cumulative text matched an unrelated unfollow label. The required legacy prerequisite was never created.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-injjambjkacdigcmpjaogaap].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: 4783928f842e7028d56ea25587229eaae176a781a97cc189708b86760b15e0af
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[14]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-7.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-10.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-15.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-18.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-21.json

### PER-PEEKLY-V2-023 / PRD-IMPORT-SNAPSHOT-UNKNOWN

- 판정: failed → not_run; 분류: fixture_semantics_and_judge_cross_attempt_attribution; 심각도: P1
- 검토 사유: The recognized empty ZIP creates known-empty history. Its actual zero-departure list was opened at obs13. The unknown native check failed only at obs24 after a different normal pair's unfollow list; no legacy-unknown prerequisite was created.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-lpcmlkbehhmjifejlcbplfll].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: 303f3661604108f54126a43a8d67bdf1bc0238c8379d7446e768cc97be9954f3
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[15]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-7.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-10.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-19.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-22.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-24.json

### PER-PEEKLY-V2-022 / PRD-IMPORT-SNAPSHOT-UNKNOWN

- 판정: failed → not_run; 분류: fixture_semantics_and_judge_cross_attempt_attribution; 심각도: P1
- 검토 사유: No legacy state was created: the empty ZIP has recognized lists. Native UNKNOWN stayed not_run through obs44, then failed at obs45 when a different normal pair's relationship detail included an unfollow label. The original IDENTITY-LIMIT not_run is preserved.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-mnemkabchmofljkacpjkooai].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: f98582bbe60f8b46e4aa5845e085434809bfff512c692754c6767e530c41ca70
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[16]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-9.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-18.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-21.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-44.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-45.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-46.json

### PER-PEEKLY-V2-024 / PRD-IMPORT-SNAPSHOT-UNKNOWN

- 판정: failed → not_run; 분류: fixture_semantics_and_judge_cross_attempt_attribution; 심각도: P1
- 검토 사유: The empty ZIP creates recognized known-empty history. The actual zero-departure list was opened at obs13 and history showed two normal records at obs16. Native UNKNOWN remained not_run through obs34, then failed at obs35 after a different normal pair's departed-six list. No legacy-unknown prerequisite was created.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-bhipnijdghjoompcjcokbceh].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: 29d0ecc451b3f3f12172fb32d5455f63b09790992c4cc323c0c44067d3892141
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[17]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-30.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-33.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-35.json

### PER-PEEKLY-V2-025 / PRD-RESULT-SEARCH

- 판정: failed → not_run; 분류: judge_search_control_mismatch; 심각도: P1
- 검토 사유: The actual imported 12-row result list has a visible enabled input[type=search] labeled 이름 또는 아이디 찾기. Native evaluation incorrectly demanded another screen's placeholder 아이디나 이름으로 찾기 and the list was then closed. All 15 saved observations have empty typed_input_checks, so the required query and narrowing were not exercised.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-lienlcpnibobddnaaekmmami].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: 65a77074cd29788022599df8d446d67c879313d0dcc9f03e9dd61e4ada4aa81a
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[18]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-7.json

### PER-PEEKLY-V2-026 / PRD-RESULT-SEARCH

- 판정: failed → passed; 분류: judge_search_control_mismatch_with_exercised_query; 심각도: P1
- 검토 사유: The imported search fixture produced exactly 12 correctly sorted outgoing rows with a visible enabled input[type=search]. A real type action retained the exact expected query (matching SHA), and the subsequent observation in the same import attempt and storage scope showed only synthetic_search_outgoing_05. The old native evaluator incorrectly demanded the MatrixTab placeholder. The separate DELETE failure remains; session outcome and executed-criterion credit are unchanged.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-ebhioimecepninpkpdilghkk].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: e95e5355eee53677ab1cd817cd0694b5e1b69381ec2d3f0af0d20770230f9beb
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[19]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-5.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-7.json

### PER-PEEKLY-V2-027 / PRD-RESULT-SEARCH

- 판정: failed → passed; 분류: judge_search_control_mismatch_with_exercised_query; 심각도: P1
- 검토 사유: The imported search fixture produced exactly 12 correctly sorted outgoing rows with a visible enabled input[type=search]. A real type action retained the exact expected query (matching SHA), and the subsequent observation in the same import attempt and storage scope showed only synthetic_search_outgoing_05. The old native evaluator incorrectly demanded the MatrixTab placeholder. The separate DELETE failure remains; session outcome and executed-criterion credit are unchanged.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-lpghnnmpbapicjbemjpnjmdk].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: f87021408221ab63db3e0ab1122ae2af5793231db0322e273e4bc2fa6305d391
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[20]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-4.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-5.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-6.json

### PER-PEEKLY-V2-028 / PRD-RESULT-SEARCH

- 판정: failed → passed; 분류: judge_search_control_mismatch_with_exercised_query; 심각도: P1
- 검토 사유: The imported search fixture produced exactly 12 correctly sorted outgoing rows with a visible enabled input[type=search]. A real type action retained the exact expected query (matching SHA), and the subsequent observation in the same import attempt and storage scope showed only synthetic_search_outgoing_05. The old native evaluator incorrectly demanded the MatrixTab placeholder. The separate DELETE failure remains; session outcome and executed-criterion credit are unchanged.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-kaknpddcajkpeekbgjeiahmd].result.receipt.criteria[kind=success,index=0]
- 원본 result SHA-256: be73f02056ee27e56e17a3bb1648f798adf1c307cb08b7552d617500b112c5db
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[21]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-7.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-8.json

### PER-PEEKLY-V2-015 / PRD-IMPORT-SIZE

- 판정: failed → passed; 분류: judge_size_alert_evidence_omission; 심각도: P1
- 검토 사유: The own upload attempts at obs8/9/10 explicitly show the 128MB ZIP, 32MB single-file and 64MB aggregate rejection messages and preserve the saved baseline from obs4; obs26 repeats the 32MB boundary. The five actual fixture files match the frozen manifest bytes/SHA. The raw model failure overlooked its own cited alerts, and the native branch omitted the sanitized group aliases. The multi-file group has no aggregate fixture SHA; its three member hashes were verified separately. SAVE-FAIL and the failed session are unchanged; baseline execution credit does not increase.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-eoddcjbgpjchiikdllkckjcf].result.receipt.criteria[kind=success,index=1]
- 원본 result SHA-256: 798bc8a0fec90b2f6a02ce180af3b660507b077da13eb3177042c70fb761ae49
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[22]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-4.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-9.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-10.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-26.json

### PER-PEEKLY-V2-025 / PRD-PRIVACY-DELETE

- 판정: passed → failed; 분류: judge_delete_key_absence_misread; 심각도: P1
- 검토 사유: The final confirmed deletion was actually dispatched and hit-tested. The saved digest returned from imported data to the initial empty-state digest, but final storage_keys and storage_snapshot.keys still contain peekly_state_v7. Prior relationship data was cleared; the failure is the pinned PRD's final key-absence contract, not retained personal data. This preserves the original failed session when combined with the independently corrected SEARCH not_run; baseline execution credit is unchanged.
- 원본 판정 위치: .ux-loop/peekly-coverage32-20261114/stage-32/report.json :: tasks[job_id=S-lienlcpnibobddnaaekmmami].result.receipt.criteria[kind=success,index=2]
- 원본 result SHA-256: 65a77074cd29788022599df8d446d67c879313d0dcc9f03e9dd61e4ada4aa81a
- 변경 지시: docs/validation/peekly-coverage-20261114/criterion-review.json :: changes[23]
- 등록·바이트 확인 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-1.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-5.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-12.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-14.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-15.json

## 검증 범위

raw 집계와 baseline 대응을 원본 report/plan으로 재계산했고, 선행 전체 artifact 감사의 입력 SHA와 job/result/manifest 결합을 확인했습니다.
변경 항목이 인용한 관측 JSON과 선택적 화면 증거는 등록 SHA와 실제 바이트를 다시 비교했습니다. 나머지 artifact의 바이트 판정은 명시된 선행 artifact 감사 시점의 결과입니다.
이 파일은 별도 보고서 집계이며 유효한 새 실행 receipt를 만들거나 원본 receipt를 다시 봉인하지 않습니다.
