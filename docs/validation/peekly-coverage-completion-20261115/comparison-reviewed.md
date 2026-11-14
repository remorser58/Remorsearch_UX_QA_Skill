# Peekly coverage comparison — listed criteria reviewed

최종 마감 확인: **최초 696dbe3의 통과 0·실패 2·미결론 30 → 이번 통과 13·실패 10·미결론 4**입니다. 최초 평가 세션은 32개, 이번 평가 세션은 27개이며, 이번 제외 5세션의 21개 기준은 별도 미평가입니다.

**미실행 8건은 유지**했습니다. 직전 23개 대상 중 20개는 통과, 025 SEARCH·029 PAYWALL·030 PAYWALL은 미평가입니다. 확정 사유, 원시 증거 경로·봉인, 여덟 개 미실행의 개별 목록은 [findings.md](findings.md)에 있습니다.

이 마감 설명을 추가하면서 아래 기존 비교표·대응 행·출처 목록과 원시 및 판정 JSON을 그대로 보존했습니다.

| 항목 | 696dbe3 | cb0188d | ee4b145 | 65f52f7·직전 증거감사 | 신규32명·명시 기준 증거감사 |
|---|---:|---:|---:|---:|---:|
| 완료·평가 세션 / 고유 페르소나 | 32 / 32 | 32 / 32 | 24 / 15 | 29 / 29 | 27 / 27 |
| 세션 통과 / 실패 / 미결론 | 0 / 2 / 30 | 6 / 4 / 22 | 1 / 6 / 17 | 9 / 8 / 12 | 13 / 10 / 4 |
| 전체 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 56 / 4 / 42 / 34 | 35 / 6 / 46 / 17 | 71 / 8 / 23 / 19 | 83 / 10 / 8 / 14 |
| 성공 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 51 / 4 / 42 / 7 | 28 / 6 / 46 / 0 | 62 / 8 / 22 / 0 | 71 / 10 / 7 / 0 |
| 복구 기준 통과 / 실패 / 미실행 / N/A | 미보존 / 미확인 | 5 / 0 / 0 / 27 | 7 / 0 / 0 / 17 | 9 / 0 / 1 / 19 | 12 / 0 / 1 / 14 |
| 완료·평가 세션의 host_protocol | 미보존 / 미확인 | 미보존 / 미확인 | 0 | 0 | 0 |

## 집계 범위

신규 요청 32명 중 완료·평가 27세션을 분모로 사용했습니다. 미평가 5건은 세션·기준 판정에서 제외했습니다.
ee4b145의 24세션은 고유 페르소나 15명입니다. 기존 46행은 동일 페르소나의 반복 세션을 포함합니다.
696dbe3의 전체32 결과는 cb0188d.before로 교차 확인했습니다. 696dbe3 run-summary의 마지막16 결과와 혼합하지 않았습니다.
cb0188d의 성공 기준 N/A 7개는 당시 데스크톱 범위 판단을 보존합니다. 신규 기준은 명시된 독립 검토 결정만 반영했습니다.

## 기존 미실행 기준의 대응 결과

| 집계 | 기준 수 | 통과 | 실패 | 미실행 | 미평가 |
|---|---:|---:|---:|---:|---:|
| 기존 세션 가중치 유지 | 46 | 22 | 13 | 0 | 11 |
| 고유 페르소나·요구사항 | 32 | 17 | 8 | 0 | 7 |

실패로 바뀐 기준도 실행 범위에는 포함되지만 제품 개선을 뜻하지 않습니다. 신규 N/A는 실행 감소 성과로 세지 않습니다.

## 신규 미실행

| 요구사항 | 기준 수 | 페르소나 |
|---|---:|---|
| CONDITIONAL-RECOVERY | 1 | PER-PEEKLY-V2-015 |
| PRD-PRIVACY-LOCAL | 7 | PER-PEEKLY-V2-001, PER-PEEKLY-V2-002, PER-PEEKLY-V2-003, PER-PEEKLY-V2-004, PER-PEEKLY-V2-026, PER-PEEKLY-V2-027, PER-PEEKLY-V2-028 |

정확한 저장 사유와 증거 참조는 reviewed-summary.json의 candidate.not_run_by_requirement에 보존했습니다.

## 독립 검토를 반영한 실패 판정

- PER-PEEKLY-V2-013 / PRD-IMPORT-SAVE-FAIL: obs-12 actually consumed and restored the one-shot peekly_state_v7 write fault during the distinct previous-fixture import. The admitted save-error DOM and unchanged 401ca05d4e2b93517fe5eb77ebeba21b66891c2695091ce34708a808a561dbb3 baseline establish the failed write with prior-state preservation. Its complete 19-control inventory contains no 다시 저장 action; the viewed frame offers only 다른 파일 고르기. The error paragraph itself is outside the captured viewport. Successful ordinary re-selection afterward does not satisfy or erase the missing direct-save-retry requirement. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-5.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-12.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00231.png
- PER-PEEKLY-V2-015 / PRD-IMPORT-SAVE-FAIL: obs-14 consumed and restored the one-shot peekly_state_v7 fault during the distinct previous-fixture import and retained the saved 0cb983c39b7af7bcd743d34a6b2054dc40a46a68277dfb58adda5de4db148f4b baseline. The admitted save-error DOM and complete 19-control inventory show no 다시 저장 action. The viewed final frame offers 다른 파일 고르기; the error paragraph is outside its captured viewport. This proves the missing direct-save-retry product requirement, independently of general recovery. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-7.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-14.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/browser-00243.png
- PER-PEEKLY-V2-016 / PRD-IMPORT-SAVE-FAIL: obs-12 consumed and restored the one-shot peekly_state_v7 fault during the distinct previous-fixture import and retained the saved 117b07616a1f2aa17fc3df37fa24f904575d3d930bafd9c2d8b58bf01f0cf51b baseline. The admitted save-error DOM and complete 19-control inventory show no 다시 저장 action. The viewed final frame offers 다른 파일 고르기; the error paragraph is outside its captured viewport. This proves the missing direct-save-retry product requirement, independently of general recovery. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-5.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-12.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00226.png
- PER-PEEKLY-V2-017 / PRD-RESULT-SNAPSHOT: The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-5/8 persist the expected pair; obs-10 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-5.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-8.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-10.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/browser-00109.png
- PER-PEEKLY-V2-018 / PRD-RESULT-SNAPSHOT: The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-4/7 persist the expected pair; obs-9 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-4.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-7.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-9.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/browser-00097.png
- PER-PEEKLY-V2-019 / PRD-RESULT-SNAPSHOT: The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-6/7 persist the expected pair; obs-16 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-6.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-9.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-16.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/browser-00164.png
- PER-PEEKLY-V2-020 / PRD-RESULT-SNAPSHOT: The assigned criterion explicitly requires that the UI not infer a cause. Same-session ordinary previous→current imports in obs-4/7 persist the expected pair; obs-9 actually opens the departed-follower sheet and contains the exact six names hyunwoo.k, ina.archive, jimin.han_, junho.jeong, sujin.lee_, yuna.99_. Although its caveat allows ID changes or account deletion, its admitted list rows label ina.archive and junho.jeong as 언팔로우. Those causal labels contradict the no-inferred-cause requirement, so raw PASS becomes FAIL. The PNG visibly shows the caveat and first row; the contradictory badges are in the same admitted DOM below the captured crop, not claimed visible pixels. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-4.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-7.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-9.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/browser-00099.png
- PER-PEEKLY-V2-026 / PRD-PRIVACY-DELETE: The owned fresh profile and pinned synthetic save are bound at obs-1/4. Obs-15 visibly presents the final confirmation; obs-16 contains a hit-tested dispatched 모두 지우기 click, completion notice, and available post-delete storage. Required peekly_state_v7 remains or is recreated, so the assigned key-removal criterion is contradicted. The post-delete filtered storage digest 7b3f3a770f0ac89471a660ccfe9a54f5de96b387ebb22d307e06fadb84f77355 equals the initial empty-profile digest; this key-presence failure is not proof that personal or imported relationship data remains. Native iOS cleanup is outside the desktop scope. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-1.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-4.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-15.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00153.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-16.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00163.png
- PER-PEEKLY-V2-027 / PRD-PRIVACY-DELETE: The fresh owned profile and pinned synthetic save are bound at obs-1/4. Final confirmation is visible at obs-14; obs-15 records a hit-tested dispatched 모두 지우기 click and the completion notice. Required peekly_state_v7 remains or is recreated in available post-delete storage. This contradicts the assigned key-removal criterion. The filtered storage digest returns to the initial empty-profile digest 7b3f3a770f0ac89471a660ccfe9a54f5de96b387ebb22d307e06fadb84f77355; key presence is not proof of retained personal or imported relationship data. Native iOS cleanup is outside this desktop scope. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-1.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-4.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-14.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00144.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-15.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00154.png
- PER-PEEKLY-V2-028 / PRD-PRIVACY-DELETE: The fresh owned profile and pinned synthetic save are bound at obs-1/5. Final confirmation is visible at obs-16; obs-17 records a hit-tested dispatched 모두 지우기 click and the completion notice. Required peekly_state_v7 remains or is recreated in available post-delete storage. This contradicts the assigned key-removal criterion. The filtered storage digest returns to the initial empty-profile digest 7b3f3a770f0ac89471a660ccfe9a54f5de96b387ebb22d307e06fadb84f77355; key presence is not proof of retained personal or imported relationship data. Native iOS cleanup is outside this desktop scope. — 증거: .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-1.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-5.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-16.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00152.png, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-17.json, .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00162.png

명시된 검토 기준의 분류와 원본 대비 변경은 evidence-review.md에 있습니다. 나머지 판정은 원본 상태를 유지합니다.

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
- docs/validation/peekly-coverage-completion-20261115/summary.json — SHA-256 95c043fdd25492bc73772b26fd1c15e0bc9770c24f8caa6c810469db0341c9ac
- docs/validation/peekly-coverage-completion-20261115/comparison.md — SHA-256 0cc6a18cb8196cbd932dd1b7881174e5a126a30c4e76564e4a1dacf25b21b4cc
- docs/validation/peekly-coverage-completion-20261115/not-run-23-baseline.json — SHA-256 66823c35e27e6af1c5017c2ed89678c5b1e128bbb09c5ca838eea5dd0fe6fa0a
- docs/validation/peekly-coverage-completion-20261115/artifact-audit.json — SHA-256 7483eca3a48afac5341a7db63e6d0ac93a37a1ed2bdc962e9ffd23db4951640d
- docs/validation/peekly-coverage-completion-20261115/automated-outcome.json — SHA-256 45f08ec1cd2d7e695a3806e78c071eb3eea5aa0d6c1f7f42e8cace70943b4139
- docs/validation/peekly-coverage-completion-20261115/criterion-review.json — SHA-256 2c461f874df9278872e94c62e2912afd383e0fbacf830037fdb8372321b97c93
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/queue.sqlite — SHA-256 8274a20c7aae52e1720885facb17e95d40e22317d32bc2e2c670b2e5cf06e8e3
- docs/validation/peekly-coverage-20261114/audit_final_artifacts.py — SHA-256 78a7bce46cd9b6b2587e8df1446e7054397a31c11395f52baed3cdd4c2d2e310
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/queue.sqlite-wal — SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljlmeakahgnhmnnffbajmljk/evidence/S-ljlmeakahgnhmnnffbajmljk/1/agent-observation-1.json — SHA-256 e022292823a647ef470853300fe8b082764d8c1693975ae215bb116e38d6eb32
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljlmeakahgnhmnnffbajmljk/evidence/S-ljlmeakahgnhmnnffbajmljk/1/browser-00014.png — SHA-256 bdd0b8b7514ec9249498d858a4ffab440aacb2fbe5f3e7d32e87a181212115df
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljlmeakahgnhmnnffbajmljk/evidence/S-ljlmeakahgnhmnnffbajmljk/1/agent-observation-2.json — SHA-256 89f3022ffdc45d7a9901e2ebd51c8fca65d460a4c8966f8e9ce8498489286dc5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljlmeakahgnhmnnffbajmljk/evidence/S-ljlmeakahgnhmnnffbajmljk/1/browser-00024.png — SHA-256 6ecd5167c7af31507e2f0df2e95ed41f6078c97d7d2efb9a5d77ca74389f7a10
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljlmeakahgnhmnnffbajmljk/evidence/S-ljlmeakahgnhmnnffbajmljk/1/agent-observation-3.json — SHA-256 97a0a5cfecf20be60fcdedc4d337411630af2be4ea5663ca7d03dfa801a7f97a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljlmeakahgnhmnnffbajmljk/evidence/S-ljlmeakahgnhmnnffbajmljk/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljffmnkkgdhopplfbhhegkma/evidence/S-ljffmnkkgdhopplfbhhegkma/1/agent-observation-1.json — SHA-256 34361db413525a5874a27e968ef805f556c5732fe45944bdafc850bc669b7812
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljffmnkkgdhopplfbhhegkma/evidence/S-ljffmnkkgdhopplfbhhegkma/1/browser-00014.png — SHA-256 bdd0b8b7514ec9249498d858a4ffab440aacb2fbe5f3e7d32e87a181212115df
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljffmnkkgdhopplfbhhegkma/evidence/S-ljffmnkkgdhopplfbhhegkma/1/agent-observation-2.json — SHA-256 2428eb172c6927c1749b378b8e7136e73d95754febc3d2d7218d68593620ffd8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljffmnkkgdhopplfbhhegkma/evidence/S-ljffmnkkgdhopplfbhhegkma/1/browser-00024.png — SHA-256 dc3c8eefff6e3fe955ad005d21685378b981a620f8c3ebd6681c582abdbbfe95
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljffmnkkgdhopplfbhhegkma/evidence/S-ljffmnkkgdhopplfbhhegkma/1/agent-observation-3.json — SHA-256 c736929fe01dfb2ce9a7dbfe9f9f4c7018c85f315c86a19162b377e9c522ba14
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljffmnkkgdhopplfbhhegkma/evidence/S-ljffmnkkgdhopplfbhhegkma/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gimbpjkdealchomaigbnfkap/evidence/S-gimbpjkdealchomaigbnfkap/1/agent-observation-1.json — SHA-256 a8266f499fb9df74efeb79157ffe377628e60b98641fece3e3c2751db901b95a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gimbpjkdealchomaigbnfkap/evidence/S-gimbpjkdealchomaigbnfkap/1/browser-00014.png — SHA-256 bdd0b8b7514ec9249498d858a4ffab440aacb2fbe5f3e7d32e87a181212115df
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gimbpjkdealchomaigbnfkap/evidence/S-gimbpjkdealchomaigbnfkap/1/agent-observation-2.json — SHA-256 01849727069496dcf172bb365ddd11093c41c4603fbd653e613dcfb4ea2d5f01
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gimbpjkdealchomaigbnfkap/evidence/S-gimbpjkdealchomaigbnfkap/1/browser-00024.png — SHA-256 6ecd5167c7af31507e2f0df2e95ed41f6078c97d7d2efb9a5d77ca74389f7a10
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gimbpjkdealchomaigbnfkap/evidence/S-gimbpjkdealchomaigbnfkap/1/agent-observation-3.json — SHA-256 12dad02f4e3cab6d1bd834848dcb08d89c77567f08119a5b680a318d00dd2365
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gimbpjkdealchomaigbnfkap/evidence/S-gimbpjkdealchomaigbnfkap/1/browser-00034.png — SHA-256 b6b7eba8b31b1fb714a839c7e176f2deb229c974b66ff9fbeec2491778776790
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gppbnocdodpcpfackcopdgal/evidence/S-gppbnocdodpcpfackcopdgal/1/agent-observation-1.json — SHA-256 ccb30c7f70e199c81dd9bde0081a0f2821643aef6093bb4ffe9cf63262adaad5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gppbnocdodpcpfackcopdgal/evidence/S-gppbnocdodpcpfackcopdgal/1/browser-00014.png — SHA-256 bdd0b8b7514ec9249498d858a4ffab440aacb2fbe5f3e7d32e87a181212115df
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gppbnocdodpcpfackcopdgal/evidence/S-gppbnocdodpcpfackcopdgal/1/agent-observation-2.json — SHA-256 4aae3aba5ca0db577eb8976e00cff1b8fa2c92eae76a4ae41485a979037ceb57
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gppbnocdodpcpfackcopdgal/evidence/S-gppbnocdodpcpfackcopdgal/1/browser-00024.png — SHA-256 89881692be8fdb1fcf6f2840af9e299fa99fbb1b8e03bc385c7d9cf3520593c7
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gppbnocdodpcpfackcopdgal/evidence/S-gppbnocdodpcpfackcopdgal/1/agent-observation-3.json — SHA-256 91fc6f7853a577ec33a3e516910dc73a67537810e31148af92298b6ccd55369d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gppbnocdodpcpfackcopdgal/evidence/S-gppbnocdodpcpfackcopdgal/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/agent-observation-2.json — SHA-256 68f0e2abbcea85caa331246137adbed42b4417d272e4d5af0c8df90edb12e874
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/browser-00024.png — SHA-256 6ecd5167c7af31507e2f0df2e95ed41f6078c97d7d2efb9a5d77ca74389f7a10
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/agent-observation-4.json — SHA-256 7b9f7925eaec697b43616bbbcfc6d912305bdd738d82be7086b349fdd97d5cf4
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/browser-00039.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/agent-observation-5.json — SHA-256 42adb72bc445b356acbb8aaa46ad824cf286d867ba37249c05e1fb9d0962d263
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/browser-00051.png — SHA-256 221fbae5562b8fceb1c0a8346cd3b12a501af2d79642ef71bffc4a56cb978ea8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/agent-observation-7.json — SHA-256 bf46393aa5d84974cf434a1e7a07f53c2b5f6ac81085066c0a988b392bb71e53
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/agent-observation-8.json — SHA-256 583229c96300e7fb7fd4b3d62b8808210ad7db756c35314638315adf79eec5fe
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/browser-00083.png — SHA-256 fdb9cd45e4dc81563683bf3e7662f06acfe44e9175f16b6a6b1c90fc7c1f9d19
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/agent-observation-3.json — SHA-256 f3240afcc3f7be162f7202ae527ad01662d8900a9dc14a041ced242ae8d22378
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ahigmmpldbffjlajeimgmmhg/evidence/S-ahigmmpldbffjlajeimgmmhg/1/browser-00029.png — SHA-256 c687326055688a1f79d90f1d72e417f274581a8915637b6bbee2abab33240271
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/agent-observation-2.json — SHA-256 e59bd9516499f401f1fc1cfa9fa7184cfd0aa6f94c227448b102a95bd9d19d1b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/browser-00024.png — SHA-256 6ecd5167c7af31507e2f0df2e95ed41f6078c97d7d2efb9a5d77ca74389f7a10
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/agent-observation-3.json — SHA-256 55a40a415ed27d955ad53d8354b44474ecd4a60fb3bda8697867331a3f5023ba
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/agent-observation-4.json — SHA-256 56e26f386f83bf33110553268ce52975c3df8d18e2bd2a29594c61936784947c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/browser-00046.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/agent-observation-6.json — SHA-256 876011c167d797ae3af72097e1063748927eef150463fb47264c1dd23fd260ab
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/agent-observation-7.json — SHA-256 823b97a1e240f82733b4ae2b35c4029ee589873e547eacdc6e35a737273a1e50
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/browser-00078.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/agent-observation-1.json — SHA-256 b881ee53d8d7d312914dbae504285e8d8363f54a7ffad45b35b84fa3e92c7fa6
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eaimebeeijnlneijkfognapa/evidence/S-eaimebeeijnlneijkfognapa/1/agent-observation-5.json — SHA-256 6e6d29813b27998e16e80a6046f8f5ec6af53e2fbd2892bee2eda13bb5fa468e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/agent-observation-2.json — SHA-256 0efb13bf22f5bc466b23f9c64bf76565f4ff4c1712db015acb576c13da69b85e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/browser-00024.png — SHA-256 6ecd5167c7af31507e2f0df2e95ed41f6078c97d7d2efb9a5d77ca74389f7a10
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/agent-observation-3.json — SHA-256 af19e35b3eca96152b0f747d6f16719308cb491a58c87a087370881a6ccf2073
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/agent-observation-4.json — SHA-256 b3b0f42be3cced8d596f676982b9b831a434eac3504f0a6ca74a9c8ab29ae912
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/browser-00046.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/agent-observation-6.json — SHA-256 75286d47edcb3c905e32372093080c3d3371c9b2bdbccbe90de3211dbeb0dccf
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/agent-observation-7.json — SHA-256 1f4e7f16fc7f49850dff4e54235b450424dc09815e915e2d67ecbd73645a2117
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/browser-00078.png — SHA-256 221fbae5562b8fceb1c0a8346cd3b12a501af2d79642ef71bffc4a56cb978ea8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/agent-observation-1.json — SHA-256 f5378415b4c31aafab4768c8bc06deff2324db0bc2afbc134eda7c9f85a11876
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-dhklecmcppmmgkgiknilflkl/evidence/S-dhklecmcppmmgkgiknilflkl/1/agent-observation-5.json — SHA-256 4e455660b5b2ce8b45872938d0a6c91d7c257db7e4f98755ea9f8659847fecad
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/agent-observation-2.json — SHA-256 80a0148c3e83920545f0a823a1c8e3989a2a3b19aeb2798fd337082f512fa86f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/browser-00024.png — SHA-256 6ecd5167c7af31507e2f0df2e95ed41f6078c97d7d2efb9a5d77ca74389f7a10
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/agent-observation-3.json — SHA-256 6f72422231e2164a3fac0f3a8a42f5780876913f849fa97f7d0d58cd7019daaf
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/agent-observation-4.json — SHA-256 b8e71cfd2e87ebf134da0ffed997d377b9c9d0b552418546b3416ddc13fbd581
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/browser-00046.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/agent-observation-6.json — SHA-256 c59678bcd76b25a53e9f1948fd29deabe1d549cf42ee2ffe0bbd2cf6d90551f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/agent-observation-7.json — SHA-256 58617c99d6736941aaa10e4b96eed32d461fc5a49d8cc4c89d3b1833cb0df0ee
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/browser-00078.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/agent-observation-1.json — SHA-256 c8b208c9c7186eb8dc6d82036b796924631b861452f43bcab5e5ec2b7030b146
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bjhjihfccjkbmdiedidhoncf/evidence/S-bjhjihfccjkbmdiedidhoncf/1/agent-observation-5.json — SHA-256 2a034b19fa1e962ab90abf5543f98c5f4c848fbb5632521f2d83cdfa94349cfa
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-6.json — SHA-256 26931895c39605d5e0c0c6a439ac0c00bbed0df1960e940dd0cbbc41bb5fa60a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-7.json — SHA-256 ce43b3c8ea82b0c9577c950f056799dc3d193e4c108725c69ac72ec294770679
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00071.png — SHA-256 fdb9cd45e4dc81563683bf3e7662f06acfe44e9175f16b6a6b1c90fc7c1f9d19
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-9.json — SHA-256 e0fbfc1cbcd05e444050662fadac0dc172f11c9b21d162382ca023425ca72831
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-10.json — SHA-256 7e1543980f13daefaf247d6d3ffc181ec0e3e613f458bb1c4ef69c09ee8379ba
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00103.png — SHA-256 fdb9cd45e4dc81563683bf3e7662f06acfe44e9175f16b6a6b1c90fc7c1f9d19
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-13.json — SHA-256 7552d7652f8e1614f752f03d01e8cdc4c394b6f4b6299ea3a131c5a3b94d38ac
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00153.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-14.json — SHA-256 31a4541d0eb471b74501947b2dda614db5fc5c62e3d70e8a272c05fddc4a5807
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00183.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-15.json — SHA-256 9e96d7ba61ffc2b1e52d4a6fbf605e699eba6e568d0bf4f9a95094b34bd4fc10
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00213.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-16.json — SHA-256 d41db44c1a80e57329a0ff40166abb1f1a8f6117dcabb958f1da981b7d6904aa
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00242.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-1.json — SHA-256 c5e3041b92510bb6dfa0a655aa623340b646ad3123aaf22a92e5584274228ed6
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-3.json — SHA-256 584a68c70ddd3a99881f447bb0ea80ba2b50bbb135ed3bfff8c62cbe567c8d90
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-4.json — SHA-256 b806a46db36f5affbef607315ce892210a6cece157673376ad390fb99e390946
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00039.png — SHA-256 f564df2860c5bf67f38a09c07b1a43672a3ef8be0b0f58e045ae2ff53f1e5cf2
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/agent-observation-5.json — SHA-256 7ac1f4ce6a65d34c604456c9342c162ea6c7a4abc0bd1020ef6ecd46afcf95ce
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-pblkjnfjnefpmkcnmhghnikb/evidence/S-pblkjnfjnefpmkcnmhghnikb/1/browser-00049.png — SHA-256 68f23a2790d31bbeac10d90eff51b96505072423aee7c702178b131ae9e26859
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-5.json — SHA-256 7af149f6c581d8c74821d5bead52ced0bf3990356895f6e10d417906de04370b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-6.json — SHA-256 4d685eb4f8f8794a1268e4ab3836fe21ecf73fd1fc577361a61b58cc54a33cd5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/browser-00061.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-8.json — SHA-256 3adda9ea2b284e29991ce7e3d19cb951c8c16ca9605f43c38788aa4b1d3b7f1d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-9.json — SHA-256 2754572772886af5443db1ca91921a4423e14b416f173976a94b3dd1788f7655
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/browser-00093.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-12.json — SHA-256 1cb8307f698c71748d85581bfc48d0211b18d7fe4501b552e1c45b7bd7c22df3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/browser-00142.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-13.json — SHA-256 b8c1a5acffa1dc2be5bb3de34cc73824b80839a22e5e313332bfba59da1eab4f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/browser-00172.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-14.json — SHA-256 1f6199c775890eaefc6fbfe416567aaf5bdfcae335e5c1385b4e91d417f46089
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/browser-00201.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-15.json — SHA-256 07fba5723f43e61ccad635ba9d0ceb70244688cc222b905dfb51babb0c842e53
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/browser-00231.png — SHA-256 6a5f821771ad320c7bec0b72440ebc18e85f46aaf94ef902eca403fa65d7e21e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/agent-observation-4.json — SHA-256 c8e479be6e9448d8d3091001bef124cc308ded10a218b5b4892ae5f082e47a4f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cijopeodbceldieicjneaaji/evidence/S-cijopeodbceldieicjneaaji/1/browser-00049.png — SHA-256 a71e4e6ef759d115ee90e266fc883616d63f3ed97ed0f3c9782f3d2cc7d8977b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-7.json — SHA-256 ab4599cef26916a0e8c5cda973cbe0595ce19783024383c29432d726c87b1be1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-8.json — SHA-256 1afb5a254a7973605fb004e2950a9c6ce1ba6ba9fbea67ac0254e0aa0039f8f5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00068.png — SHA-256 ae0c8b44a759550b59cf03619d3b2b983a89c611efe717d0346e252d5ce6892e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-10.json — SHA-256 bd571353423154548e6bf9d0e1edfa9da86f0392741b293f887abe1a043fd01e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-11.json — SHA-256 4d451e290c7785f51bfdde45db73d5862719096bd841d6d04446e4633313b463
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00101.png — SHA-256 958fe247fe41e155e5be4c53e40529f6b7060271111a7c57830bd3c38fc8693c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-14.json — SHA-256 2d3958b7b179c04a6245e9b974cf1969d85778faac5fef0fa0073c57d31fd662
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00150.png — SHA-256 b01bb7b12b6bbb687aad30f8f535f56c9cd56ef78aa2b6151369798badac5773
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-15.json — SHA-256 9765fd98192e8229711f7f58c5fc6096ac7c9cf0acef5114c29e981b925184c2
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00179.png — SHA-256 b01bb7b12b6bbb687aad30f8f535f56c9cd56ef78aa2b6151369798badac5773
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-16.json — SHA-256 25875667dfeda8b9cb4b7bc3be1df583d5e768127319806a97e8444fbf83823e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00208.png — SHA-256 b01bb7b12b6bbb687aad30f8f535f56c9cd56ef78aa2b6151369798badac5773
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-17.json — SHA-256 cabe38aa7447d128935bec786b61e4971bb750cdca3f2bb2f719afa25b2b19f5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00237.png — SHA-256 b01bb7b12b6bbb687aad30f8f535f56c9cd56ef78aa2b6151369798badac5773
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-3.json — SHA-256 52e6d6767025311dad6328c6b92a7f9b70a9a49d97fd1916745e90bd71399e98
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00029.png — SHA-256 c687326055688a1f79d90f1d72e417f274581a8915637b6bbee2abab33240271
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-4.json — SHA-256 03d0b9dc614fad12e7c60b0926c7d80ae16ea53f42f52018d45fc6d61a1d6aab
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-5.json — SHA-256 52c4806a7f8f49e830dabddc0d2af736ac84944edb560b06b6655a0624ef2821
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/agent-observation-6.json — SHA-256 6224e8372d42d5792985546b75203d491f7eec3102fd749031782089502a7524
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-galdkhommdhbgkalkcfmmefk/evidence/S-galdkhommdhbgkalkcfmmefk/1/browser-00055.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-5.json — SHA-256 76c5e16511673abe36a32ec2281ac02c2173f08180bb935393589fad9252a84c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-8.json — SHA-256 d41fe8777b40785e8c7a7c9c52dafbb13e563388b6c57c17673895b7e0f8a71d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00081.png — SHA-256 19aa780ac481881922d8a7b70c222e19e078c459ce6fade31fddc617bf443dd8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00127.png — SHA-256 67cf66bda48229e08f293f20e6eae009701fdd4226f837827336dd915fd8d1c2
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-9.json — SHA-256 20294af8f7eb68bef17034b15fa3f0dda723f1b1048ee66011da095fa8dd7cbe
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-10.json — SHA-256 4916ed246cc6898a990774f640fb3ec65d046a801f9a78de7b7b3c228db9c256
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-11.json — SHA-256 def86cfa0df6a4ef07ea1f21c9716b43d309613e98fbfeab54703d8fc5181320
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00156.png — SHA-256 a607796665d348b43311f3dba473df9b69d084207c8fbbbdab8b38dea98ecf50
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-12.json — SHA-256 05110ea91763bc74c194c1a1e28168ca176d27aa3aa3cbf1d5bc642758e4903f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00231.png — SHA-256 a607796665d348b43311f3dba473df9b69d084207c8fbbbdab8b38dea98ecf50
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/agent-observation-13.json — SHA-256 34a79138f2cc6742ff479f7337f3ab05a4a3c12cd7d86b45fca619ffbfc7796c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eghkdbdagmmiacobmdheghfg/evidence/S-eghkdbdagmmiacobmdheghfg/1/browser-00243.png — SHA-256 f3be7fb865eee35e290cc4ddc716aeae5a2a3e99238a660fe98d694e4dbaadb5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-7.json — SHA-256 775c9b499028e830c560494fe1890d0981dba2ac393a3e4c22bd90b89c2fb38f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-10.json — SHA-256 23ad6483a7b78142d424760d76ddd1509340928994c4abfc43bf893a069d86c9
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/browser-00101.png — SHA-256 19aa780ac481881922d8a7b70c222e19e078c459ce6fade31fddc617bf443dd8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/browser-00151.png — SHA-256 67cf66bda48229e08f293f20e6eae009701fdd4226f837827336dd915fd8d1c2
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-11.json — SHA-256 c2784da9b8869f25203be3e37404b85d1f10726163c16e345ec7ea0a5ebe63cc
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-12.json — SHA-256 7fe448356f198ec0cddd671de40fcba276ab1bc9af9d0c1acd5d3bb617970d4b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-13.json — SHA-256 a80e24062cec5a4428b8c0f6db7dad7d5e67a186745cecaecf33ab3aa379cc76
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/browser-00178.png — SHA-256 a607796665d348b43311f3dba473df9b69d084207c8fbbbdab8b38dea98ecf50
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-14.json — SHA-256 f67307f55e89cc563f4d6c52657e5c0f7ff0eec6f17ad7b49b8e7d42327211e3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/browser-00243.png — SHA-256 a607796665d348b43311f3dba473df9b69d084207c8fbbbdab8b38dea98ecf50
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-5.json — SHA-256 5498e90fa00f15b4179ac3fc127ae9a6982a352c4056c4a33c90b9ba100a1704
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-8.json — SHA-256 be77fa4edcefbd55bc4790fcc97a2ba3d42767b416662d12f0cfb6b2b99b8b16
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00082.png — SHA-256 a71e4e6ef759d115ee90e266fc883616d63f3ed97ed0f3c9782f3d2cc7d8977b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00134.png — SHA-256 14f20109fb764b09a625fb752f871baf5db66ffc8a55bd0a7f49aa01f25e59da
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-9.json — SHA-256 7deee56881502ede7fe21749a94761c38ab64e4e94e415650793982a88e3bca3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-10.json — SHA-256 1513c6b99ad5e5baf30f12c73f1e650adfa3da59db5102e891310769bf6bee12
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-11.json — SHA-256 76631bf8f9f059c903c0f993f47f5309a6b924d91499b106de9ae5ee9759b29c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00160.png — SHA-256 34fed3ee3d8a6cb98cb0a05736c670fc1058ca6c31f800187acde30f3bef83d8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-12.json — SHA-256 db22a842d9743a11d06c2daff110b820ed64a45a35d0ff615fd9c101aad4a40c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00226.png — SHA-256 34fed3ee3d8a6cb98cb0a05736c670fc1058ca6c31f800187acde30f3bef83d8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/agent-observation-13.json — SHA-256 9edda2b026505870abef40d073d08f89322ab5269b8bcf099906778ad556aedc
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ekcpeodledhmeheieecnhdee/evidence/S-ekcpeodledhmeheieecnhdee/1/browser-00237.png — SHA-256 f3be7fb865eee35e290cc4ddc716aeae5a2a3e99238a660fe98d694e4dbaadb5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-5.json — SHA-256 8ea3a22b0190218fff25651f2f5f79742adbbeb780a2594489621842e37bee24
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-8.json — SHA-256 9599a60335651fee020bfdb1db4061d5b0c340777729936d5eba209e7b5fbf47
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-13.json — SHA-256 e371e63b76d7ae92ba3591a88f73dcb7ae77e1f5f513828049b6d2fa3708a979
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/browser-00139.png — SHA-256 538fb0984f25809c60926d84873671ffc59e758d149eb5e48ed738f5403c3742
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-15.json — SHA-256 0ff859fef3231e71e5705066c1f9fecde5d719f18b072f517ef0b3a17531831f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/browser-00159.png — SHA-256 7435b1cc39ce778d22fff696c935ece40bcbc6634df6ad9baec0234b75b9671b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-17.json — SHA-256 a3f20adf8421da4323be8d13d0c7152d1a7a49abdb24264a465d3598047388b6
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/browser-00179.png — SHA-256 d03831b9ba73a24aa51182c74d90b5264a77e874d8f35448a29d745eddbdf394
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-10.json — SHA-256 b02d300cb654f1c9e9c5947fbf02654d7ea1ea380c5e02789bfc6fc198f03abc
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/browser-00109.png — SHA-256 242f955c94a6d1f8d5a6770ee4b2504ae92c4d16d2738f4fff9053949b433b5d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-1.json — SHA-256 8358d635d3d18f33a0ca3c4db893dd4342c59fd0a86590c64d7a4e4afac82e91
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-2.json — SHA-256 15a7f0aa2a7c2127a8c8bc9974eb8bdd654d288b6422b4d14483adaf8440e8c0
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-3.json — SHA-256 0d20b1f08655ee43e3e526bf3f2996b54ac436d655644aa72e934f1179ca3596
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-4.json — SHA-256 88c5e8f4c427e69ab8566c775bd7e1489fab1e55f2fefdd43cc15377d7836385
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-6.json — SHA-256 31522c585f6071b714ccf0ffc524cd806d5073176ddac0460d834fffda05cc4c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-7.json — SHA-256 a9bec8c73a3e13b086a4cb26e1abece068be1461c8064eb87e9664a2ade15f07
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-9.json — SHA-256 4e656641a355700a1241c21e8e84185531c3d0cded3255894e1f64c2712160f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-11.json — SHA-256 50a5f0f226b9e8faa30aff74b148d59ac66f1b093c3d337b9df7985bdf9791e0
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-12.json — SHA-256 13274721952b2d563451cfa74e27a4ba9651783feb2da28b5ed64e83efe119e5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-14.json — SHA-256 d0bd504d06bd7c18ec5270bd20b089af379b89fc92ad98c1f7a6fc71be7b57e6
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-aiidkoilmlhfjinghfbgbnjf/evidence/S-aiidkoilmlhfjinghfbgbnjf/1/agent-observation-16.json — SHA-256 b4a6e60df6d1aa877eea3e57093a3622f0916ab974aba7c32560d7d723caf003
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-4.json — SHA-256 3166751a75a0cffc533bcef9af3a7eb1df69300272fa27c246607d2aefab8167
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-7.json — SHA-256 51c6023495c93f5fe14fdefb85300af20441851592dec26080f2707f0f3c994e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-12.json — SHA-256 232075a0272e9250a2602dedbd5d0c8dd2a2c608f28354d2c17e5c4a11e72d7c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/browser-00127.png — SHA-256 897c563340d2bfccd33144fc793b998e782c2095dc987ef71f81123d7483f98f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-14.json — SHA-256 2e40d5302b6f28b2bcc388fd768e83067540e0597ced8e363d993abe21913b6e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/browser-00147.png — SHA-256 119dd7e74e9605460a58e1302a35ba0db9cf41bebdb70fbd133f4764b9c7fe96
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-16.json — SHA-256 6c2559c25dbe5e93458c547ae13ba813fb7722788814297f40077e6810962b91
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/browser-00167.png — SHA-256 d03831b9ba73a24aa51182c74d90b5264a77e874d8f35448a29d745eddbdf394
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-9.json — SHA-256 3358eea517fa88e5f279d120e4f78918da72445eca2cf511bafa2227687621e0
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/browser-00097.png — SHA-256 f718331875510acb8d48a5d98e464f6265a95632ed214a6f0eeaedcc9142fe19
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-1.json — SHA-256 e544b58874ac7661a5b44af58797971541624afcfaccaf1ef10417ea90139c14
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-2.json — SHA-256 efcc8835d865d5955dd3b1a8008cd311c368e923319665d133d8047460f3ba03
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-3.json — SHA-256 d337821b8873d44417dede61ae93ced8fcd11d1f1340312d097575859fca5113
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-5.json — SHA-256 06282631ba7fc1eb7026c89bc8b8acdc0d7471c1acf3672b7257914c2dbc5611
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-6.json — SHA-256 b88bd092c8a18480c892397f688dd811cb65bc4d8bd0d2049786debdf4d397e4
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-8.json — SHA-256 17b03eb0b7041b6a70b1ba3ace8d0f647d68db456fa1a5656baf1ca9323a6456
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-10.json — SHA-256 5f6674bb77c2aaacd659eb60a81dbdcca41ffcbb0d03791779619267bdc66b77
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-11.json — SHA-256 cd78e3ba776bd1c716382387b6ccc47ff452043f2b8597e9d365d1393fe3ad01
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-13.json — SHA-256 0fa8e5697e5c40bbbce204e3cc4f5d611e97f3581c2c1644a3645408b34f624d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-eijmndepmkoldnjffcibcchh/evidence/S-eijmndepmkoldnjffcibcchh/1/agent-observation-15.json — SHA-256 9e3c0cd023a27c67e34575ebd11bbdb4617b030e76bc388a4f1405f7c652dac1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-6.json — SHA-256 549479976297dacbe7d50932c891293786caab438bc388c41240c5853dda2911
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-9.json — SHA-256 37f1265684766a4e8626cab02c8d01ef20f0f9188c0cae03065fed7e9bf8de39
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-10.json — SHA-256 b4defe5079fe542c39249471428cd37e43d1e24ae32427be293a9ff481551d05
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/browser-00104.png — SHA-256 a0843e07d160c63dc14aedbbcb9f7d6439a85ffbee9b6c879103be304b16fd4b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-12.json — SHA-256 2d990bd164a324da295a4d25ae53588c3bc678da4366b8e00be03d3769033242
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/browser-00124.png — SHA-256 119dd7e74e9605460a58e1302a35ba0db9cf41bebdb70fbd133f4764b9c7fe96
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-14.json — SHA-256 cf72d19514ec180442c2e511f70b3f969f980a91b30867dfd00b0cb7d35ff697
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/browser-00144.png — SHA-256 e8e82d11d0a46780ef60c80b9db4fdb670e081e293bee9300f9433fd576b563a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-16.json — SHA-256 9fa834e1f64e873b95713cd1b0dc271896638f2044b633164d90529aeef5026c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/browser-00164.png — SHA-256 46d11eecdfff3efc00b3161f80a2334cd6a03ebf1d1ef6d1ac4d313eb348aa02
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-1.json — SHA-256 e8a08bc7ac0bc521d9869e6c46c29c74e1fd76c45befbed915e51591925cbdf8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-2.json — SHA-256 4017b1864e68b09b227192cd13a2aa28475ca9bda9596efa1fc8e6ac68add784
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-3.json — SHA-256 0205a3e138b87d5831061987fa5d527e71950e8c4fcde82398c5eab521ac0a32
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-4.json — SHA-256 f2fe0d335d16c24d7fb6f2b3fbdb283c5348dbf498ef3c6a3dbad1667e4a9fff
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-5.json — SHA-256 1720f6134fd1ad589633cd453dc3923e296ce8a7445344741879214f277ddb7b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-7.json — SHA-256 c1d66fd2e76888e92dafd14009a7d24f9718f2e98cf4299d7cb44395cebdbd5c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-8.json — SHA-256 09d4b847f5eac8765254aa2ab142b38b6209b81628acf2785569807bc7037715
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-11.json — SHA-256 557bf092cf21ac4a21da876d02935a4856ab1f05c4f43332043e43c776526ee3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-13.json — SHA-256 2f03699f0db757e75424199c924330bf3fc7daca2f9f8b66a3888db8c0b4fa98
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-accbhomandanakneabadnkem/evidence/S-accbhomandanakneabadnkem/1/agent-observation-15.json — SHA-256 36750c8e575ed54885dbf88bdebbdf607de8860256530705ce95f60279ca9117
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-4.json — SHA-256 ba756a56452114974ce166d73ab797133b34aa4fa17837c946575c4515cf3019
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-7.json — SHA-256 b62094dddff59f33960f7b8ef514e6a485f38fa53318fcb68a146a658999b07c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-12.json — SHA-256 8673d9331933f0c71e58ffb680197460ac0362e7adc75776b116f25c8b7f96c7
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/browser-00129.png — SHA-256 200d920556700a3522493f7c86e6350c1802299866cfb49053a220df200fb1e1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-14.json — SHA-256 2866224c045eb17b35787d140e8122f067c8e2e07d502aa1cdff7da360c5e510
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/browser-00149.png — SHA-256 7435b1cc39ce778d22fff696c935ece40bcbc6634df6ad9baec0234b75b9671b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-16.json — SHA-256 47985cbd94cc4d326479d1ebe8e62eaf69889d815871d630460fdd2bdd0f8825
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/browser-00169.png — SHA-256 149019a994129c65a943bed393ffce64339c3304abc9b13d18fd9bab1716f158
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-9.json — SHA-256 dcac5226922a0ebf75446fd449b516ef2cf9357bfff0b6efd92ce6d0a2d99be2
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/browser-00099.png — SHA-256 4f24bfaeb8bce9aad9e90c3fde42b3c4d6f15621a8841463b6f7ac605e00eb11
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-1.json — SHA-256 53f0f0fbf7fd7a9309e80295799833315c59bc1b482074a8d62d71e1bf0be489
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-2.json — SHA-256 e378cc18ef51c2adb3541e2911f471f8daba149c99c11b31cc70fd52dfb02e43
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-3.json — SHA-256 ecb1a4977e63f8a0f6e2f281154acac843832e4ee7290af20c0a13917d6d77d5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-5.json — SHA-256 97f3d082690ad38bafdc47190ca861c83648b70e163bd772b115eb40b8f1648c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-6.json — SHA-256 d435180c444a258fa3763c76f06151facc6e3f44db58457ca477eaa40a83f1ce
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-8.json — SHA-256 d5c0ad21c84c338c8e96b004d7eec40a8a9408f282cd4e26f6541c46563e2ae3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-10.json — SHA-256 6994760a81e3158ecc7d79278ed9bad32478d3fe38bb0440dd3cf9fd8744ac5e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-11.json — SHA-256 a3018682d4177eeb7cfe015003ec2be5de4a5b9b4d901092d5a0f12fc3174475
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-13.json — SHA-256 d21a3bad12cbff6cd36680b0498c0e0e73d579531c2eb7153d97ae9db01cd951
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-flmilpmkbnekbambkncmlajo/evidence/S-flmilpmkbnekbambkncmlajo/1/agent-observation-15.json — SHA-256 803a9b4e9fe7dec169506ffa0146e50adb5e99a6c3fd7381008907679070175f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-6.json — SHA-256 3b86d7c67f5b3bad75a6d2f058055c14c47d332a06aba34e9dcac094e219cc4e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-10.json — SHA-256 3a180b3cfcfc068226d4ef15845c3468a5b4a07ec43b746032e64bdf3c141766
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-11.json — SHA-256 170944bbe0ef191db11780df393bd8b731c09660eecbf2f852c6a283522b25ed
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/browser-00135.png — SHA-256 b80d84a1e858054f5a30e8a9b25832268247b47d40c3fe87c024407704ba7442
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-12.json — SHA-256 4f92f721e84ff772a9c58baa5022018281a41073e65f0a9c1b176fab922f338e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-14.json — SHA-256 ed83d93ec7e6cac1dd2fddc955030480fcc1798a38743a36eebea036d7c38b86
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/browser-00201.png — SHA-256 b09b7682370dd5a642b385a610addb8d464d5e0a583e1533a676bee5c249101b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-1.json — SHA-256 caf5498e39b6387939f13e8edb889832299ce7ad6d478ff673f222cf15c4b72b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-2.json — SHA-256 091cc5a14f5e2ef290bb3319c0dcf1848838296f545b9613b124d8dade86fc41
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/agent-observation-7.json — SHA-256 b02d6af58fd54b7788b673c8b89c6341a20a470f33545b3f7fe5c17eca6e0ce9
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/browser-00085.png — SHA-256 855632b8a635256c000f52eb8a0afe53b6f70dcfdbfaa7d528643085c98eb378
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-piofceocafbdlopejgfplabf/evidence/S-piofceocafbdlopejgfplabf/1/browser-00179.png — SHA-256 fe383046c5b18e2210ff7ebc02ff086fbf454ae6e3da952db5748c3ce636c80f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-6.json — SHA-256 0acc7c8e6022449c423c44bc8eaf70d5ef0ab97e2f3be6fc7907d2a300e807a9
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-10.json — SHA-256 e02be2c7fd163914090876eb26f91110369c69903e324228e750bc63a4e5c37c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-11.json — SHA-256 1b28e80bfcad0634ca12eb34671220a9438f86c6c41b5a517c80560b894e1c12
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/browser-00137.png — SHA-256 af7621350440ac964e599c9cee2a15ad3048f59d470a09847173cd53b11dadbd
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-12.json — SHA-256 da928a77dd570a5e90b5e82d15fbf002e921f71ff17d54e254e87d4e37ece43b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-14.json — SHA-256 fecb8e39c9f63c932a10b1427604f3d1d2e0a63ac1cc539555d3f6fa357f7b3e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/browser-00201.png — SHA-256 15696f64de449be3d37015b6ad8f6d7f6233c88a862eb4ca0f4afea23ed0432b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-1.json — SHA-256 50921062505da3e2ac1503764392fd2617afa552548ef8453beffb7dea5bb12f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-2.json — SHA-256 87d1fea6f25964f2a20cc01f463aeef336ca5e4e8f5d7fc064dd23b4690b5986
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/agent-observation-7.json — SHA-256 5f228183a2e90166845c3bdb62411837f90d499b458fca0707e6c554f7bdfbb1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/browser-00084.png — SHA-256 855632b8a635256c000f52eb8a0afe53b6f70dcfdbfaa7d528643085c98eb378
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-amagkkfaamjiaedfeobnkibo/evidence/S-amagkkfaamjiaedfeobnkibo/1/browser-00179.png — SHA-256 fe383046c5b18e2210ff7ebc02ff086fbf454ae6e3da952db5748c3ce636c80f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-6.json — SHA-256 d198a4eeb24bd84f6e5088ced7c18fcc89abce8e04d53e687f90a7cc08b020dc
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-10.json — SHA-256 99e796d716deb6e575257b2551ed966c4052a68eaa89431853833ea32e41b063
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-11.json — SHA-256 a78928260c9b9ccd0449d665e35e4b07593fd884279f58bc6113156703f064c9
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/browser-00137.png — SHA-256 af7621350440ac964e599c9cee2a15ad3048f59d470a09847173cd53b11dadbd
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-12.json — SHA-256 1fbf1fb9c7ef5f97dc69aead18d818fdf42fb8b970671fc490072a45722aec7d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-14.json — SHA-256 f9f60f573219bfb9e55f91d505ce6d13caabb1ea85ce400ff8f0a974c67f6833
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/browser-00203.png — SHA-256 15696f64de449be3d37015b6ad8f6d7f6233c88a862eb4ca0f4afea23ed0432b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-1.json — SHA-256 e2a98b762ba72430ebb2f6614c248f70a667041c7eea1f33656d2d0e70aa8a5e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-2.json — SHA-256 f192fd76d11c173e1320b00ab8c29c747c13af034027ddcfa2a24d6a13800cbe
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/agent-observation-7.json — SHA-256 ffbb9f97fcd89e95261c18326986d41000936963d59a1b31d3d4f2f412ba0c77
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/browser-00084.png — SHA-256 692c6b05781f961b10ba6c3d9b566b19d3dbcdf8ea219190524c0bde85a2b4f5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-cknakkjhlkhdkmajbbhgconh/evidence/S-cknakkjhlkhdkmajbbhgconh/1/browser-00181.png — SHA-256 88413f89cf25397b5c32f73966d904b313d77c1a9e9b04879da3a972d97236e8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-5.json — SHA-256 58c7bbf5c67819a89d8c5c3c59646e671cf168151977a2343f36a9b0d1927c2d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-9.json — SHA-256 4fed92622d0541d2c873acdd5b9013a1ee17f48c61e51be78d0897fd92adc92c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-10.json — SHA-256 091ceda8b3bc6c8757eaf6f608af2556cfd11c0282bc1a93d74ebc5e02a8c27d
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/browser-00126.png — SHA-256 af7621350440ac964e599c9cee2a15ad3048f59d470a09847173cd53b11dadbd
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-11.json — SHA-256 53745f1247b30818d64ebd3eb05aac87916f10e4800347ae89d7bc4c9e53811a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-15.json — SHA-256 d427dc1555709cd6f5150141ae87c7189fbda66c1b2f06d075d28f24bae32d44
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/browser-00214.png — SHA-256 15696f64de449be3d37015b6ad8f6d7f6233c88a862eb4ca0f4afea23ed0432b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-1.json — SHA-256 f725e105437f735abffddd5167818ff0968e8515e614031f7084c7a7b1303dbd
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-2.json — SHA-256 8c7748630cab80e6c89d0cbe39b4e01fd59ae98abb0a1ac6b32d76df766d02d8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/agent-observation-6.json — SHA-256 22c5167ed6ea61c7e21895e7a50c59d5f42f9f3472629d7fd40e7a3a67bfac86
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/browser-00073.png — SHA-256 692c6b05781f961b10ba6c3d9b566b19d3dbcdf8ea219190524c0bde85a2b4f5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-beikkhpkhpdnflofalopgodk/evidence/S-beikkhpkhpdnflofalopgodk/1/browser-00170.png — SHA-256 bd25da383482c4f7185eb4aa3702e7f96c95c657c6edbbc73ad9212ac8c905c7
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-4.json — SHA-256 02af0c2ce4c67a322b9224bc687d403cf1067442c53324ca3cae933fbd3f725f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-5.json — SHA-256 3aff918664f0af0be79bec2ed54a0262d04b675bfb817dc5f630db61cf150407
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-6.json — SHA-256 424425f31d7bd60976f8b0943b8e831f116c09f34b6fff6235cb9cddb54b5e23
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00063.png — SHA-256 4d11e836aac8ed48841ba4e0bd5169bb461b23cddede0a657cd0556ffa419091
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-3.json — SHA-256 3a450895b0bdc4c61b49b13b9a8b0847375730ff16cfbc24a3528568a7e7bc15
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-12.json — SHA-256 aa2a6c2a0b04804988e9ac0c66d4fb26f6170b98ad30403911e2b2fd48429b1b
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00123.png — SHA-256 380a0c88c8ff327d7d35a5d5075d59e8198229e7dcdba066f2801e3542f80806
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-1.json — SHA-256 7ca1a0c9e3cb44efedf4cd18b5b9383bc1659aa53968e69c5838c1c7cb6d85e7
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-15.json — SHA-256 91efd7dd22615ce6fab8b5493db227f0e5412e955399e556291e9fc3ae9e9d97
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00153.png — SHA-256 3732f04c3b50d5b6ec0473f89c63a2331442ba0fef537bc6b8af5da31cb1f629
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-16.json — SHA-256 0c9b8083895f845128bd3fbdc309ccb4ace67cec10fa09c5ee0a9261057ed038
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/browser-00163.png — SHA-256 7fbd177e58d1a06f85cf43a1ed323ef7bbe31a60ec76f4be3d466b91ed483044
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-4.json — SHA-256 1bd8493c2bf32978650296f196003f5e291373005ed994a97731a301eec697ff
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-5.json — SHA-256 01aacf996540ad7e2c85cdabb6f0f770bb7c3305181e988a945393f16e8f7779
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-6.json — SHA-256 65cd84896713e04bdfc6f4fb4aa87cbb9f3fdca2e5c4075980bcf0095389c0f0
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00064.png — SHA-256 4d11e836aac8ed48841ba4e0bd5169bb461b23cddede0a657cd0556ffa419091
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-3.json — SHA-256 204fce26519db4913af52250e03e7b9bfdb9cded7cef5fd4077f6f50b23c56b9
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00034.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-11.json — SHA-256 ea5d4598f424c75b9d8d103022c39cc6556f7ac0c19626dad0be4e1ec7713b2c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00114.png — SHA-256 380a0c88c8ff327d7d35a5d5075d59e8198229e7dcdba066f2801e3542f80806
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-1.json — SHA-256 802c7a8227aebbafd75a7311e5f5f2e7ff8543934a7cd53f4dba7d4c326caf5c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-14.json — SHA-256 387c2511b62e882941693f87dd59bfa62be81a3c0d40c10f9f2ef2e4ff902212
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00144.png — SHA-256 3732f04c3b50d5b6ec0473f89c63a2331442ba0fef537bc6b8af5da31cb1f629
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-15.json — SHA-256 82312601034ea6bfb9bd9720f9957be2116264acf268d9baca89c18ec9d3cb8e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/browser-00154.png — SHA-256 7fbd177e58d1a06f85cf43a1ed323ef7bbe31a60ec76f4be3d466b91ed483044
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-5.json — SHA-256 98f854887e82cdf2ec1c360402abc21105aca8c0838fe91e8bbf1fcb269712a7
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-7.json — SHA-256 0fb0e996cb47594e83038407231ef34cc144251f1fd041fe11ab29ba88f6197a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-8.json — SHA-256 067b83c8e86b2a62fc9f6a7fbcc12549c7ee1fd4da9eb879023cbb88769215ae
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00072.png — SHA-256 4d11e836aac8ed48841ba4e0bd5169bb461b23cddede0a657cd0556ffa419091
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-4.json — SHA-256 b044bbb121ad58d18a75c32f594eeeebebb164d8e8516ad45da98d0055d9d3de
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00039.png — SHA-256 75dc0b4d79d13fcbb9313db077831396f99e8ea74111af894978fa189f09d7f1
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-13.json — SHA-256 aee25cc1e2605c1c2f5dd91d2a183ab2a7e818369139fc48509e353f49bb4e0a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00122.png — SHA-256 37be2f10a38015f372b5a97c0f2f72816eaba4ec839f681d71cbb74831a8e76e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-1.json — SHA-256 94458e332516b04bf77976ce51a774c4f7c5c935d64152c79c66316c7fd88ace
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-16.json — SHA-256 1cd0ef72d1d0dbac866eea57403562f077c675d456a46a2cf3f128f9f9afe98c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00152.png — SHA-256 d234fced843783c2b59b44d25a77c21f1735d63341b2216350b8e7cde27a07a3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-17.json — SHA-256 6d61ae2d78cb1a167c00d5bea858f92f6232463784b1b56bde7bc2ef24dad778
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/browser-00162.png — SHA-256 7fbd177e58d1a06f85cf43a1ed323ef7bbe31a60ec76f4be3d466b91ed483044
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-3.json — SHA-256 185a97ed56b98b5e4732b856d4d96a69f36fa5f3336a299838f4f4c748b31172
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-6.json — SHA-256 661c11919be3a2d43b102462c15f05012796f7b836064f4cb56c31adbb45a4f3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-3.json — SHA-256 83dd521100ba510180192df1d220b8d14555ece234b69de4d5d8edd814bc2c1e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-5.json — SHA-256 8656220665c1b91bfe2651da56c2392cc26176d150a76a4955de184cbe9d21cf
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/browser-00049.png — SHA-256 68ab4f045af554e6b8f11fe8c6ac508a7d23920593b5579176d980c99094533c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-1.json — SHA-256 2c4f2e6b849d80829a1054d9a28d6feb773296b2634f0f86c263727439c265e6
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-9.json — SHA-256 ccad9cdd8be3f5c2e3420c26f492aab7b35f26c44a7ac4d3ca2a76d841cf3963
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-12.json — SHA-256 ed592067a66f0d936ecd24962c021909a38edd064d8f0f7c0ca3c50f0e189129
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-15.json — SHA-256 e632dce108b082db3f987a2b4056feb39f75d0d1a456a61c1434ba3cddf7973f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-18.json — SHA-256 df21e09e397797dbb89881e69c1a5b243d156e4ce4190e1b340aeed1965a1b21
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-21.json — SHA-256 a768ba3a08ec84ad7636df3519cd72d905c21bf745365badde8216ea50ab4722
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-24.json — SHA-256 9285a9c37956adf98bf71668963627e266e9c256220782825c5684e9afdfcc33
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-27.json — SHA-256 3ef3943c39c4319fa88c146ad43d836277f755f7a2a31d2947eaac5c858daf30
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-30.json — SHA-256 99531f4daaa1916c3a39b072ac024d28d355592b69b72f68963c618e428d964f
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-33.json — SHA-256 581923cc3cec4c7b1a9060e2eab201faea0a8980930c12960fae6f37fa3dc936
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-36.json — SHA-256 1a679161d20aed847f881eabc675872194a0c8280040ed93b074eb5effef12cc
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-39.json — SHA-256 e4f6a7da5c29e14aabda0c77e123e8ef70123c4db9a846c2e7963abeaaefa741
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-42.json — SHA-256 352775d57dec754e5a464bec64c54d178170703b1f532882b5780662de35b0ea
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/browser-00445.png — SHA-256 f8387e5261aa87b306a76e936c88e6a16a00b08e2b47f04b7871ef3658ef7f38
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-45.json — SHA-256 65b1b491ab960cd37d53969f2fcd31ecc761086cd74ba8dcbf94e96651a34b45
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-48.json — SHA-256 5fe18ef6ab991557cf30cb75e38a2098a00c7c0548d8e9dc9432640d3685f095
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-50.json — SHA-256 806fc81dcceb941cea16186149fb84d57e94228dc9d01e2496c689e45b7c9806
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/browser-00529.png — SHA-256 5484139481632e985e3d7c82beb8901d01f088b38ba95288f75834aa9c94fbe0
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-57.json — SHA-256 24ef885acb5fd56b6b4070c01c905cf7e8c0cb5080e7b4eb5fb58c40a4bc741a
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/browser-00599.png — SHA-256 0d86660da5453ad659645d277a1727bccd1ec11e626e4cbed78cd2a260fc2815
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/agent-observation-60.json — SHA-256 38b5ad96e01727f37575043ba61732796757a0f6f4bc5555bba886a210877475
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gmlckefolmkmffoakngahepj/evidence/S-gmlckefolmkmffoakngahepj/1/browser-00629.png — SHA-256 633c86301f6dc1cf5b9300de57c73847f0244459cc17314dd0ee852bdf8fe989
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-3.json — SHA-256 9472e7750e2538287255089775a865210be66748760e41733bda5a8117b85aee
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-5.json — SHA-256 ba8af621fae54d0bd4639ed84f21f931fd830755694d49e60c64ab58653d88b3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/browser-00049.png — SHA-256 68ab4f045af554e6b8f11fe8c6ac508a7d23920593b5579176d980c99094533c
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-1.json — SHA-256 5d08d6e78e4801c8832680fd3887fb28cfd4be0d5380db35ed2d134413ff7ece
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-9.json — SHA-256 65fadcae5d8520a604bacab1903a5e36c8982b0d710bf4fe4a5eb2992e1447a5
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-12.json — SHA-256 f4507da0576d4e26c70952a8bf80a72ecb6ac40b35d597436865bffb359a8ad3
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-15.json — SHA-256 815d1d5276069077d7fbfa8bad43be3117a5482f8580c7498037ed4ca7031033
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-18.json — SHA-256 3bdda1f88064177ecde5045e609df877c8765cb2827cf08cfac74baa12de0894
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-21.json — SHA-256 fc8ba6d8d34adf49d4c6aa3f3ab332a91318fb6d258455c9eaf0d1752c2383de
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-24.json — SHA-256 adc5d09f8e033dc9592ee4ca6ae7a1cef1feef3dbb7446806438c5c304d2dcb8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-27.json — SHA-256 936beb2e01568de4312b5e3caf437611cb84ad1d90a8fcd7d344b26ae7d23e07
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-30.json — SHA-256 64a0aa63c0e183bccaf6f0f7b9f640784e93acbbb48d851029497c2f6d1c60d8
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-33.json — SHA-256 1a2f41fcd6a15d5c34c72be0301ca6bc395c0739e01aca0a16c7b7e1d9012788
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-36.json — SHA-256 731ffcbecc358e58d9fcf795b92ab5d6713808883ee846b462724c297827a05e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-39.json — SHA-256 a22515951936d993cb9138d1d93563688447eaddbce060a34656a239b9110963
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-42.json — SHA-256 0a5df32638a8d3b5e6b8fa4159685ae491a1092fbb1510dff047c5ac93af2b3e
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/browser-00442.png — SHA-256 fdc8f080681fdcde96625873b8917824340cf0b2fc3fe89b10cd0146a6372008
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-45.json — SHA-256 41990067bf14aed10d3dd7d07948f3d29053643757c28c15ff936d714e027e86
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-48.json — SHA-256 c5e7c7da3d961e013fd3bc69a3b201ac0f41da5f2baec02b13096b043571c999
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-50.json — SHA-256 6ffe1c74e36f270329c77e750e0a65064b1336119d069d316a5c7ba5e79c5de2
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/browser-00526.png — SHA-256 05e93c07126a2267a2f76adf5695f51329e1d8ccf3d8a43a6dc57f6fee6c5992
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-57.json — SHA-256 885b58064debc34403e9b645bb202d2984462642e668f4c2444e64ec639f08a7
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/browser-00596.png — SHA-256 0d86660da5453ad659645d277a1727bccd1ec11e626e4cbed78cd2a260fc2815
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-60.json — SHA-256 e9f673b2a24d827fc105ea1959cc2081d761b3c6bb02476028e8499f1e805e64
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/browser-00626.png — SHA-256 633c86301f6dc1cf5b9300de57c73847f0244459cc17314dd0ee852bdf8fe989
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-4.json — SHA-256 5435171777807dd8fa8589e1e0f6d32218484e04396b7706822a1cc153ef6096
- .ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-bpnodpobeeifandgemhfnlae/evidence/S-bpnodpobeeifandgemhfnlae/1/agent-observation-8.json — SHA-256 f4560fa7729a55a48aa80341d4667a38525425473790392061b41e74c46e0910
- docs/validation/peekly-coverage-completion-20261115/apply_criterion_review.py — SHA-256 43256fa19c0324f9f81dac95b4f05fbaa329a3ade6eb020fb1d0a5a1dc4a6d25

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

## 독립 검토 및 N/A 분리

기존 4개 비교 열과 원본 영수증은 그대로 보존했습니다. 이번 검토에 명시된 기준만 재판정했고 나머지는 원본 판정을 유지합니다.
위 호환용 대응표의 미평가에는 N/A가 포함됩니다. 아래 표는 N/A를 별도로 분리한 최종 대응 수치입니다.

| 대응 범위 | 기준 수 | 통과 | 실패 | 미실행 | N/A | 미평가 | 실행 확인 | 독립 검토된 실행 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline_23·weighted | 23 | 20 | 0 | 0 | 0 | 3 | 20 | 20 |
| baseline_23·unique | 23 | 20 | 0 | 0 | 0 | 3 | 20 | 20 |
| baseline_46·weighted | 46 | 22 | 13 | 0 | 0 | 11 | 35 | 35 |
| baseline_46·unique | 32 | 17 | 8 | 0 | 0 | 7 | 25 | 25 |

실행 확인은 통과와 실패의 합입니다. N/A·미평가는 감소 성과에 포함하지 않습니다.
원래 46행의 반복 가중치는 새 사람이나 새 실행으로 세지 않습니다. 기존 23개와 신규 전체 분모는 별도입니다.
제품 개선율이나 전체 기준의 독립 검토 완료를 주장하지 않습니다.

검토 입력·변경 목록·증거 해시는 evidence-review.md 및 reviewed-summary.json의 independent_review에 있습니다.
