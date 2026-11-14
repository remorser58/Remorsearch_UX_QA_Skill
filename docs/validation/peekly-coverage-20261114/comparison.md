# Peekly coverage comparison

| 항목 | 696dbe3 | cb0188d | ee4b145 | 신규 요청 32명 |
|---|---:|---:|---:|---:|
| 완료·평가 세션 / 고유 페르소나 | 32 / 32 | 32 / 32 | 24 / 15 | 29 / 29 |
| 세션 통과 / 실패 / 미결론 | 0 / 2 / 30 | 6 / 4 / 22 | 1 / 6 / 17 | 12 / 12 / 5 |
| 전체 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 56 / 4 / 42 / 34 | 35 / 6 / 46 / 17 | 78 / 16 / 8 / 19 |
| 성공 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 51 / 4 / 42 / 7 | 28 / 6 / 46 / 0 | 69 / 16 / 7 / 0 |
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
| 기존 세션 가중치 유지 | 46 | 27 | 14 | 5 | 0 |
| 고유 페르소나·요구사항 | 32 | 19 | 10 | 3 | 0 |

실패로 바뀐 기준도 실행 범위에는 포함되지만 제품 개선을 뜻하지 않습니다. 신규 N/A는 실행 감소 성과로 세지 않습니다.

## 신규 미실행

| 요구사항 | 기준 수 | 페르소나 |
|---|---:|---|
| CONDITIONAL-RECOVERY | 1 | PER-PEEKLY-V2-013 |
| PRD-IDENTITY-LIMIT | 1 | PER-PEEKLY-V2-022 |
| PRD-IMPORT-ACCOUNT | 1 | PER-PEEKLY-V2-011 |
| PRD-IMPORT-HTML | 1 | PER-PEEKLY-V2-011 |
| PRD-PAYWALL-BOUNDARY | 4 | PER-PEEKLY-V2-029, PER-PEEKLY-V2-030, PER-PEEKLY-V2-031, PER-PEEKLY-V2-032 |

정확한 저장 사유와 증거 참조는 summary.json의 not_run_by_requirement에 보존했습니다.

## 저장된 실패 판정

- PER-PEEKLY-V2-013 / PRD-IMPORT-SAVE-FAIL: The one-shot write fault was consumed and prior state preserved, but only 다른 파일 고르기 was offered; no 다시 저장 retry action appeared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pggllnfpmomgbiaefciinnlo/evidence/S-pggllnfpmomgbiaefciinnlo/1/agent-observation-15.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pggllnfpmomgbiaefciinnlo/evidence/S-pggllnfpmomgbiaefciinnlo/1/browser-00245.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-pggllnfpmomgbiaefciinnlo/evidence/S-pggllnfpmomgbiaefciinnlo/1/browser-00257.png
- PER-PEEKLY-V2-014 / PRD-IMPORT-SAVE-FAIL: obs-13 shows the one-shot fault consumed and prior result preserved, but the required 다시 저장 retry control was absent; only 다른 파일 고르기 appeared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-oheandojgflaijgkoigockdl/evidence/S-oheandojgflaijgkoigockdl/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-oheandojgflaijgkoigockdl/evidence/S-oheandojgflaijgkoigockdl/1/browser-00231.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-oheandojgflaijgkoigockdl/evidence/S-oheandojgflaijgkoigockdl/1/browser-00243.png
- PER-PEEKLY-V2-015 / PRD-IMPORT-SIZE: obs-8/9/10 uploaded all size boundaries and preserved the saved hash, but no 128MB or 64MB alert was shown; only obs-26 displayed the 32MB 너무 커요 error. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00151.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-9.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00180.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-10.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00210.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-26.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00666.png
- PER-PEEKLY-V2-015 / PRD-IMPORT-SAVE-FAIL: obs-11 consumed the one-shot write fault and preserved the prior hash, but no 결과를 저장하지 못했어요 alert or visible 다시 저장 control appeared; only file re-selection was offered. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00216.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-eoddcjbgpjchiikdllkckjcf/evidence/S-eoddcjbgpjchiikdllkckjcf/1/browser-00228.png
- PER-PEEKLY-V2-016 / PRD-IMPORT-SAVE-FAIL: obs-11 shows a save-failure notice with prior state preserved, but no 다시 저장 retry control existed (only 다른 파일 고르기); the required retry text and path were therefore untestable and absent. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mjpfaichoklgmcfglleieclo/evidence/S-mjpfaichoklgmcfglleieclo/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mjpfaichoklgmcfglleieclo/evidence/S-mjpfaichoklgmcfglleieclo/1/browser-00215.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mjpfaichoklgmcfglleieclo/evidence/S-mjpfaichoklgmcfglleieclo/1/browser-00227.png
- PER-PEEKLY-V2-021 / PRD-IMPORT-SNAPSHOT-UNKNOWN: After empty-previous then sample-current uploads the summary still said '2026년 11월 14일 기록과 비교했어요 0명'; no '비교할 수 없'/'기록이 없' exclusion text appeared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-10.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/browser-00145.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/agent-observation-21.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-injjambjkacdigcmpjaogaap/evidence/S-injjambjkacdigcmpjaogaap/1/browser-00255.png
- PER-PEEKLY-V2-022 / PRD-IMPORT-SNAPSHOT-UNKNOWN: After the empty previous backup and current sample, the summary compared against the 2026-11-14 record (0 removed), so the unknown snapshot was not excluded. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-9.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/browser-00136.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/agent-observation-45.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-mnemkabchmofljkacpjkooai/evidence/S-mnemkabchmofljkacpjkooai/1/browser-00436.png
- PER-PEEKLY-V2-023 / PRD-IMPORT-SNAPSHOT-UNKNOWN: After uploading empty-previous and then current, the summary compared with the 2026-11-14 record and showed 0명; no '비교할 수 없/기록이 없' exclusion copy appeared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-10.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/browser-00145.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/agent-observation-13.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpcmlkbehhmjifejlcbplfll/evidence/S-lpcmlkbehhmjifejlcbplfll/1/browser-00170.png
- PER-PEEKLY-V2-024 / PRD-IMPORT-SNAPSHOT-UNKNOWN: 빈 이전 백업 업로드 후 0명(obs-8), 현재 샘플 업로드 후 '팔로워에서 빠진 사람'이 '2026년 11월 14일 기록과 비교' 0명으로 표시되고 변화 기록도 2건으로 집계됨(obs-11, obs-16). '비교할 수 없/기록이 없' 제외 문구 없음. 기계 checks index2 failed. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/browser-00119.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-11.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/browser-00151.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/browser-00196.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/agent-observation-35.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-bhipnijdghjoompcjcokbceh/evidence/S-bhipnijdghjoompcjcokbceh/1/browser-00386.png
- PER-PEEKLY-V2-025 / PRD-RESULT-SEARCH: Import gave 팔로워 20명/팔로잉 28명 and 나를 맞팔 안 한 사람 12명 with rows synthetic_search_outgoing_00..11 in username order, but no input with placeholder '아이디나 이름으로 찾기' was present, so the exact-handle narrowing step could not be executed. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-5.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/browser-00050.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/browser-00060.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/agent-observation-7.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lienlcpnibobddnaaekmmami/evidence/S-lienlcpnibobddnaaekmmami/1/browser-00070.png
- PER-PEEKLY-V2-026 / PRD-RESULT-SEARCH: Machine check failed for the 12-row list/search-input requirement even though exact-handle typing later narrowed the list to one row. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/browser-00060.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-7.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/browser-00067.png
- PER-PEEKLY-V2-026 / PRD-PRIVACY-DELETE: Deletion was confirmed, but storage_keys still included peekly_state_v7; required local state key absence was not verified. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-16.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/browser-00152.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/agent-observation-17.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-ebhioimecepninpkpdilghkk/evidence/S-ebhioimecepninpkpdilghkk/1/browser-00162.png
- PER-PEEKLY-V2-027 / PRD-RESULT-SEARCH: 12 username-ordered rows were observed and typing synthetic_search_outgoing_05 narrowed to one row, but the machine check failed because the required search input was absent. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-5.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/browser-00055.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-6.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/browser-00062.png
- PER-PEEKLY-V2-027 / PRD-PRIVACY-DELETE: Deletion confirmation was inspected and 모두 지우기 clicked, but storage keys peekly_state_v7 and peekly_theme_preference remained, so app state was not cleared. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-14.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/browser-00142.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/agent-observation-15.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-lpghnnmpbapicjbemjpnjmdk/evidence/S-lpghnnmpbapicjbemjpnjmdk/1/browser-00152.png
- PER-PEEKLY-V2-028 / PRD-RESULT-SEARCH: obs-7/obs-8 machine check status=failed: the 12-row list opened but the required current-PRD search input was not established; typing still narrowed to one row. — 증거: .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-7.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/browser-00066.png, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/agent-observation-8.json, .ux-loop/peekly-coverage32-20261114/stage-32/sessions/S-kaknpddcajkpeekbgjeiahmd/evidence/S-kaknpddcajkpeekbgjeiahmd/1/browser-00073.png
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

각 비교 열의 source_refs.selector가 사용한 JSON 필드를 명시합니다.
입력 report의 current_valid 기록을 사용했으며 새로운 모델·브라우저 호출이나 이전 영수증 변경은 없습니다.
