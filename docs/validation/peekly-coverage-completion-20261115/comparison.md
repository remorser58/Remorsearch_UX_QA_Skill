# Peekly coverage comparison

| 항목 | 696dbe3 | cb0188d | ee4b145 | 65f52f7·직전 증거감사 | 신규 32명·실제 실행 |
|---|---:|---:|---:|---:|---:|
| 완료·평가 세션 / 고유 페르소나 | 32 / 32 | 32 / 32 | 24 / 15 | 29 / 29 | 27 / 27 |
| 세션 통과 / 실패 / 미결론 | 0 / 2 / 30 | 6 / 4 / 22 | 1 / 6 / 17 | 9 / 8 / 12 | 21 / 6 / 0 |
| 전체 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 56 / 4 / 42 / 34 | 35 / 6 / 46 / 17 | 71 / 8 / 23 / 19 | 88 / 6 / 0 / 21 |
| 성공 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 51 / 4 / 42 / 7 | 28 / 6 / 46 / 0 | 62 / 8 / 22 / 0 | 82 / 6 / 0 / 0 |
| 복구 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 5 / 0 / 0 / 27 | 7 / 0 / 0 / 17 | 9 / 0 / 1 / 19 | 6 / 0 / 0 / 21 |
| 완료·평가 세션의 host_protocol | 미보존 / 미확인 | 미보존 / 미확인 | 0 | 0 | 0 |

## 집계 범위

신규 요청 32명 중 완료·평가 27세션을 분모로 사용했습니다. 미평가 5건은 세션·기준 판정에서 제외했습니다.
ee4b145의 24세션은 고유 페르소나 15명입니다. 기존 46행은 동일 페르소나의 반복 세션을 포함합니다.
696dbe3의 전체32 결과는 cb0188d.before로 교차 확인했습니다. 696dbe3 run-summary의 마지막16 결과와 혼합하지 않았습니다.
cb0188d의 성공 기준 N/A 7개는 당시 데스크톱 범위 판단을 보존합니다. 신규 영수증의 N/A를 임의로 재분류하지 않았습니다.

## 기존 미실행 기준의 대응 결과

| 집계 | 기준 수 | 통과 | 실패 | 미실행 | 미평가 |
|---|---:|---:|---:|---:|---:|
| 기존 세션 가중치 유지 | 46 | 29 | 6 | 0 | 11 |
| 고유 페르소나·요구사항 | 32 | 21 | 4 | 0 | 7 |

실패로 바뀐 기준도 실행 범위에는 포함되지만 제품 개선을 뜻하지 않습니다. 신규 N/A는 실행 감소 성과로 세지 않습니다.

## 신규 미실행

완료·평가 세션의 미실행 기준이 없습니다.

## 저장된 실패 판정

- PER-PEEKLY-V2-013 / PRD-IMPORT-SAVE-FAIL: Injected write failure showed '저장 공간이 부족해서 저장하지 못했어요…' with consumed/restored fault and unchanged digest 401ca0…, but no 다시 저장 action existed; only 다른 파일 고르기 was offered. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-12.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00219.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00231.png
- PER-PEEKLY-V2-015 / PRD-IMPORT-SAVE-FAIL: obs-14: one-shot fault consumed/restored and saved digest unchanged, but required 다시 저장 was absent; only 다른 파일 고르기 was offered. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-14.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/browser-00231.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/browser-00243.png
- PER-PEEKLY-V2-016 / PRD-IMPORT-SAVE-FAIL: obs-12에서 저장 오류와 기존 digest 유지(117b0761)는 확인됐으나 필수 '다시 저장' 버튼이 없고 '다른 파일 고르기'만 노출됐다. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-12.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00214.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00226.png
- PER-PEEKLY-V2-026 / PRD-PRIVACY-DELETE: The verified deletion reached its completion notice, but required local-storage keys remained or were recreated. This check evaluates key presence only. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-1.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00014.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-4.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00046.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-15.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00153.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-16.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00163.png
- PER-PEEKLY-V2-027 / PRD-PRIVACY-DELETE: The verified deletion reached its completion notice, but required local-storage keys remained or were recreated. This check evaluates key presence only. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-1.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00014.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-4.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00047.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-14.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00144.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-15.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00154.png
- PER-PEEKLY-V2-028 / PRD-PRIVACY-DELETE: The verified deletion reached its completion notice, but required local-storage keys remained or were recreated. This check evaluates key presence only. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-1.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00014.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-5.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00050.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-16.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00152.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-17.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00162.png

실패 목록은 저장된 판정이며 제품 결함·실행기 결함·판정기 오판의 최종 분류는 별도 검토가 필요합니다.

## 경로와 비용

- 설정 경로: ['TOKENMAXX/deepseek-v4.1-flash-free']
- 실제 시도 경로: {'TOKENMAXX/deepseek-v4.1-flash-free': 651}
- 대체 모델 시도: 0
- 정책 비용 USD: 0
- 비용 필드 누락 응답: 651
- 공급자 청구 확인: 미확인

A configured free route and policy cost of zero do not verify provider billing; missing cost values remain missing.

## 신규 코호트 전달 감사

- 저장된 전달 정책: {'durable_call_id_guard': True, 'known_reply_retries': 2, 'timeout_seconds': 150, 'uncertain_resends': 0}
- 정책 일치 / 원장 감사 유효: True / True
- 실제 요청 응답 기록: 651
- 완료 응답 재시도 / 품질 복구: 9 / 9
- 품질 거절 진단 기록: 9
- 불확실 재전송 위반: 0
- 불확실 재전송 0 검증: True
- 불확실 이벤트 call ID: ['op-3dec06a91069c876ebef12568133b8814b406db3', 'op-420e1a6c72f19969085fcab1f74c90ed1d667fb1']
- 불확실 / 미결 전달 guard call ID: ['op-3dec06a91069c876ebef12568133b8814b406db3', 'op-420e1a6c72f19969085fcab1f74c90ed1d667fb1'] / []
- 위반 call ID: []
- 감사 오류: []
- 원장 SHA-256: 15ed29997181435272f3217ebbd19fb3969fa3bec0b7c1408500c6ce9cfca775

Known completed-reply repairs are distinct from resending an uncertain delivery. Quality-rejected diagnostics are not additional provider attempts.
이 감사는 신규 코호트 원장에만 적용되며 이전 smoke의 재전송 사고 기록을 변경하지 않습니다.

## 숫자 출처

- .ux-loop/peekly-completion32-pinned-20261115/stage-32/report.json — SHA-256 14838cef25d4e90b4ea84a78392e409e2d5b4c13b8fb2fa5b05c22b4ffa96a7e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/stage-summary.json — SHA-256 90272fb8b4263426c91c4e156f42813ad2a13d9ed4555f5d3a91139da619b2f5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/plan.json — SHA-256 660406bc74f05921184be02549ad9ee39a456c33e820283ead5b5476a2d76213
- docs/validation/peekly-coverage-20261114/not-run-baseline.json — SHA-256 e661c293420ccfef537c444bf7f114e72f8e07a7e062ad554abe539177799cee
- 696dbe34e92247ed1b139662577f799b8595baaa:docs/validation/peekly-ux-findings-20261113/run-summary-32.json — SHA-256 622d1d21e15d37f467443b95e80d486477769e0459faa9f21cfa0f70eedbde0d
- cb0188ddf420b3b019facbafef75bde619365a41:docs/validation/peekly-verdict-quality-20261113/verdict-quality-summary.json — SHA-256 c04d166c6fa313bc3fc5a7bbf6ee4f1ea9562984cccbaef49dbf98894a6ace20
- ee4b14571930af428d5a52e0e133deebedba485d:docs/validation/peekly-explicit-success-20261113/summary.json — SHA-256 3b923e06d5df773b2564216d013f997d3d9aa0fbdc2be71feb3639246c536f84
- ee4b14571930af428d5a52e0e133deebedba485d:docs/validation/peekly-explicit-success-20261113/final-session-ledger-20261114.json — SHA-256 c11febc7ae6d12d69067237397145e4c4240a689143df926417a1036e7cbaf5d
- 65f52f78918d097c39ac8eb5ec49ed6daea537bc:docs/validation/peekly-coverage-20261114/reviewed-summary.json — SHA-256 f803cd44fcad79d203c826d36ee2f8e1409538e6f67ae06a240e8c634c21b4dc
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/model-router-ledger.json — SHA-256 15ed29997181435272f3217ebbd19fb3969fa3bec0b7c1408500c6ce9cfca775
- .ux-loop/peekly-completion32-pinned-20261115/run-status.json — SHA-256 1494cada48f976b0fd15eebc3347f045a510e392bfa0a049f5a50d33aaf45f95
- .ux-loop/peekly-completion32-pinned-20261115/input-provenance.json — SHA-256 c530faba1c2d91190b068308cc71adaa37edafa10e77726a71c7f1dabffb4468

각 비교 열의 source_refs.selector가 사용한 JSON 필드를 명시합니다.
입력 report의 current_valid 기록을 사용했으며 새로운 모델·브라우저 호출이나 이전 영수증 변경은 없습니다.

## 직전 65f52f7의 미실행 23개 대응

| 기존 기준 | 통과 | 실패 | 미실행 | 미평가 |
|---:|---:|---:|---:|---:|
| 23 | 20 | 0 | 0 | 3 |

실행 확인은 통과와 실패의 합입니다. 미평가에는 불확실 세션·누락 기준·조건부 N/A가 포함되며 감소 성과로 세지 않습니다.
전체 신규 미실행 수와 기존 23개의 대응 결과를 함께 표시합니다. 분모가 다른 결과를 단순한 제품 개선율로 해석하지 않습니다.

| 페르소나 | 기준 | 새 결과 |
|---|---|---|
| PER-PEEKLY-V2-013 | CONDITIONAL-RECOVERY | passed |
| PER-PEEKLY-V2-017 | PRD-RESULT-RECIPROCITY | passed |
| PER-PEEKLY-V2-017 | PRD-RESULT-REVERSE | passed |
| PER-PEEKLY-V2-017 | PRD-RESULT-MUTUAL | passed |
| PER-PEEKLY-V2-018 | PRD-RESULT-RECIPROCITY | passed |
| PER-PEEKLY-V2-018 | PRD-RESULT-REVERSE | passed |
| PER-PEEKLY-V2-018 | PRD-RESULT-MUTUAL | passed |
| PER-PEEKLY-V2-019 | PRD-RESULT-RECIPROCITY | passed |
| PER-PEEKLY-V2-019 | PRD-RESULT-REVERSE | passed |
| PER-PEEKLY-V2-019 | PRD-RESULT-MUTUAL | passed |
| PER-PEEKLY-V2-020 | PRD-RESULT-RECIPROCITY | passed |
| PER-PEEKLY-V2-020 | PRD-RESULT-REVERSE | passed |
| PER-PEEKLY-V2-020 | PRD-RESULT-MUTUAL | passed |
| PER-PEEKLY-V2-021 | PRD-IMPORT-SNAPSHOT-UNKNOWN | passed |
| PER-PEEKLY-V2-022 | PRD-IDENTITY-LIMIT | passed |
| PER-PEEKLY-V2-022 | PRD-IMPORT-SNAPSHOT-UNKNOWN | passed |
| PER-PEEKLY-V2-023 | PRD-IMPORT-SNAPSHOT-UNKNOWN | passed |
| PER-PEEKLY-V2-024 | PRD-IMPORT-SNAPSHOT-UNKNOWN | passed |
| PER-PEEKLY-V2-025 | PRD-RESULT-SEARCH | unassessed |
| PER-PEEKLY-V2-029 | PRD-PAYWALL-BOUNDARY | unassessed |
| PER-PEEKLY-V2-030 | PRD-PAYWALL-BOUNDARY | unassessed |
| PER-PEEKLY-V2-031 | PRD-PAYWALL-BOUNDARY | passed |
| PER-PEEKLY-V2-032 | PRD-PAYWALL-BOUNDARY | passed |
