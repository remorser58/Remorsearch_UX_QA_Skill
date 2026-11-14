# Peekly 최종 findings — 미평가 3건과 미실행 8건

확정일: **2026-11-15 (Asia/Seoul)**. 대상은 `17d78c6baa5936085440341e87689d1e181aeabc`에 발행된 새 32명 코호트의 독립 검토 결과다. 코호트는 2026-11-15 07:14:57 KST에 종료됐다. 이번 마감은 저장된 증거와 동결 소스의 읽기 전용 대조이며, 추가 실제 실행 없이 제외 사유와 남은 미실행을 확정한다.

## 1. 최종 비교와 분모

| 항목 | 최초 696dbe3 | 이번 최종 증거 검토 |
| --- | ---: | ---: |
| 완료·평가 세션 | 32 | 27 |
| 세션 통과 / 실패 / 미결론 | **0 / 2 / 30** | **13 / 10 / 4** |
| 성공 기준 통과 / 실패 / 미실행 / N/A | 미보존·미확인 | 71 / 10 / 7 / 0 |
| 복구 기준 통과 / 실패 / 미실행 / N/A | 미보존·미확인 | 12 / 0 / 1 / 14 |
| 전체 기준 통과 / 실패 / 미실행 / N/A | 미보존·미확인 | **83 / 10 / 8 / 14** |
| 별도 미평가 기준 | 미보존·미확인 | **21** |

새 32명 큐는 완료 28·불확실 4로 종료됐다. 030은 큐 완료이지만 운영상 실행 미완료여서, 평가 가능한 세션은 27개다. **115개 평가 기준 + 21개 미평가 = 계획 136개**이며, **83 통과 + 10 실패 + 8 미실행 + 14 N/A + 21 미평가 = 136**이다. 세션 미결론 4개와 제외 세션 5개를 합쳐 같은 지표로 쓰지 않는다.

직전 미실행 23개의 대응 결과는 **20 통과·3 미평가**다. 그 3개는 아래 025 SEARCH·029 PAYWALL·030 PAYWALL이다. 이번 전체 미실행 8개는 이 23개 집합 밖에 있다. 최초와 현재의 평가 인원·제품 버전이 달라, 세션 결과의 단순 차이를 동일 조건의 제품 개선량으로 해석하지 않는다. 이전 네 열과 전체 대응 행은 [최종 비교표](comparison-reviewed.md)에 그대로 보존했다.

정량 기준의 정본은 [reviewed-summary.json](reviewed-summary.json), 명시적 판정 정본은 [criterion-review.json](criterion-review.json)이다. 각각 SHA-256은 `dcb5f1189797f61ddf8409a9984bbb60f4634ec1c5065896d3b1aa9607edb5f1`, `2c461f874df9278872e94c62e2912afd383e0fbacf830037fdb8372321b97c93`이며 이번 마감에서 변경하지 않았다.

## 2. 미평가 3건의 공통 원시 증거 경로

아래 경로는 모두 레포 루트 기준이다. 각 사례의 Q/L/R 선택자는 이 파일에서 해당 작업·요청을 정확히 가리킨다.

| 증거 ID | 실제 경로 | 확인 범위 |
| --- | --- | --- |
| Q | `.ux-loop/peekly-completion32-pinned-20261115/stage-32/queue.sqlite` | 읽기 전용으로 jobs·operations 조회; 해당 request/checkpoint/result의 canonical 봉인 재계산 |
| L | `.ux-loop/peekly-completion32-pinned-20261115/stage-32/model-router-ledger.json` | events·call_delivery, 실제 시도 수와 전달 결과 |
| R | `.ux-loop/peekly-completion32-pinned-20261115/stage-32/report.json` | tasks의 현재 증거 유효성, 결과·평가 자격 |

L의 파일 SHA-256은 `15ed29997181435272f3217ebbd19fb3969fa3bec0b7c1408500c6ce9cfca775`, R은 `14838cef25d4e90b4ea84a78392e409e2d5b4c13b8fb2fa5b05c22b4ffa96a7e`다. 아래 request/checkpoint/result SHA는 해당 레코드 본문의 봉인이며, SQLite 파일 전체 해시를 뜻하지 않는다.

### 025 SEARCH — 원래 최종 review 요청의 전달 불확실

- Job: `S-ocglonedchibimababmanahg`.
- 원래 review operation: `op-420e1a6c72f19969085fcab1f74c90ed1d667fb1`.
- Q의 `jobs[id=job]`: `status=uncertain`, `problem=model_delivery_uncertain`, result와 result SHA 없음. 턴 19·review 단계·부분 관측 18개.
- Q의 `operations[id=operation]`: `kind=review`, `slot=0`, `state=uncertain`, reply와 reply SHA 없음.
- L의 `events[call_id=operation]`: 정확히 **1회** 시도, `TimeoutError`, **150.0059초**, `delivery_state=uncertain`, `can_retry=false`. `call_delivery[operation]`도 uncertain이다.
- 불확실 요청 이후 같은 job에 생성된 operation은 **0개**다. 재전송하지 않았다.
- Request SHA: `74855f10d4e71d04738725cf57ba9a4b1ce0431b498ddf4523a967271f4789be`.
- Checkpoint SHA: `af7cb53e90253e1489debb10f41872d5ffd87e1cc880c6027e16d45939868201`.

**확정 판정: SEARCH 미평가.** 최종 응답과 완료 결과가 없어 이 세션의 성공 3개·복구 1개 모두 미평가다. 부분 검색 관측에는 완료 세션의 평가 자격을 부여하지 않는다. timeout과 결과 부재는 입증됐지만, 제공자가 실제 처리했는지와 네트워크·제공자 내부의 근본 원인은 미확정이다.

### 029 PAYWALL — 원래 최종 review 요청의 전달 불확실

- Job: `S-cmkbfkbjcjonakfbhgkpeaod`.
- 원래 review operation: `op-3dec06a91069c876ebef12568133b8814b406db3`.
- Q의 `jobs[id=job]`: `status=uncertain`, `problem=model_delivery_uncertain`, result와 result SHA 없음. 턴 64·review 단계·부분 관측 62개.
- Q의 `operations[id=operation]`: `kind=review`, `slot=0`, `state=uncertain`, reply와 reply SHA 없음.
- L의 `events[call_id=operation]`: 정확히 **1회** 시도, `TimeoutError`, **150.6345초**, `delivery_state=uncertain`, `can_retry=false`. `call_delivery[operation]`도 uncertain이다.
- 불확실 요청 이후 같은 job에 생성된 operation은 **0개**다. 재전송하지 않았다.
- Request SHA: `26f901de72b152e8b5265a0f1837927a701b29d9ab4a5928573f5e1321ed6edf`.
- Checkpoint SHA: `bdcd08570b606ebbbdae1e6fd1929b3f7172c95f795a8486ebc5194161692e1f`.

**확정 판정: PAYWALL 미평가.** 최종 응답과 완료 결과가 없어 이 세션의 네 기준 모두 미평가다. 부분 Pro/PAYWALL 관측은 진단으로 보존했다. 025와 마찬가지로, timeout이 발생한 네트워크·제공자 내부의 근본 원인까지 확정한 것은 아니다.

### 030 PAYWALL — 전송 전 로컬 요청 본문 상한 초과

- Job: `S-dhjdnlebpigdchpmkmnblafj`.
- Q의 `jobs[id=job].result`: 큐는 complete, `operational_completed=false`, `problem=host_protocol`, `ux_outcome=inconclusive`, `first_judgment_sha256=null`.
- Result SHA: `204b3b42d12402b6235f4cfbf722518994f1584896ee19699a19596984c5c98e`.
- Checkpoint SHA: `263e446abe61e93b3a8e6d004e41a01d19a8019e915e88a132da9f9a91d1c216`.
- 마지막 실제 모델 operation: `op-34a8b26a1424e301722359ba1561420c932e38a9`, model slot 67, done·응답 있음.
- 마지막 실제 request SHA: `aac5646e7bcaf43333dcac4535158c203b5f475c670b7f597fc78fd10bb8aa57`.
- Q에서 다음 model slot 68과 review operation은 모두 없음. 기존 model 68개·tool 68개·close 1개는 모두 done이다.

동결 소스와 기존 체크포인트로 계산한 직전 요청 **261,027B**는 실제 저장된 요청과 바이트 단위로 같다. 다음 파생 요청은 **265,147B**로 **262,144B** 상한을 **3,003B** 초과했다. 모델 턴은 **12개** 남아 있었다. 파생 본문 SHA `0d80bb191059128da8a65c3702f4ee0859771682498697e71ae0adf9bd8c0d30`는 전송되지 않은 재계산 값이다.

동결 버전 `f50d082a197e683b5961d17919fe219dc48c4d55`의 다음 소스 경로를 확인했다.

- `skills/remorsearch-ux-qa/uxpersonas/scale_run.py`: `payload()`의 본문 한도 적용이 `dispatch()/q.begin`보다 먼저 수행된다.
- `skills/remorsearch-ux-qa/uxpersonas/agent_run.py`: `_data()`가 상한 초과를 `host_protocol`로 보고한다.
- `skills/remorsearch-ux-qa/uxresearch/canonical.py`: 실제 저장 요청과 재계산에 같은 canonical serialization을 적용한다.

**확정 판정: PAYWALL 미평가.** 현재 artifact validation은 통과했지만 운영상 실행 완료와 최종 판정이 없어 네 기준 모두 평가에서 제외했다. 이 원인은 전송 전 로컬 본문 제한이며, 전달 불확실·스크린샷 제한·턴 상한으로 분류하지 않는다. 상세 재계산과 정상 종료 증거는 [본문 제한 진단](cohort-030-payload-limit.md)에 있다. 본문 축소나 상한 변경을 구현했다는 주장은 하지 않는다.

### 세 사례의 보존 위치와 범위

[cohort-review-025-032.json](cohort-review-025-032.json)의 `unassessed_cases[0]`·`[1]`·`[2]`가 각각 025·029·030이며, [해설](cohort-review-025-032.md)에 원래 요청과 부분 증거를 보존했다. 이 세 세션의 12개 미평가 기준에 011/014의 9개를 합치면 전체 미평가 **21개**다. 기존 검토 조각의 취득 당시 종료 대기 필드는 그대로 보존하며, 최종 종료 상태는 [terminal-cohort-integrity-review.md](terminal-cohort-integrity-review.md)와 `.ux-loop/peekly-completion32-pinned-20261115/stage-32/browser-lifecycle-summary.json`에서 확인한다. 소유 그룹 32개 모두 종료됐다.

## 3. 미실행 8건 — 판정 유지

미실행은 평가 가능한 완료 세션에서 해당 행동·노출·복구를 입증하지 못한 기준이다. 아래 여덟 건을 통과나 N/A로 바꾸지 않았다.

| 페르소나 | 기준 위치 | 요구사항 | 원시 → 최종 | 확정한 실행 공백 |
| --- | --- | --- | --- | --- |
| 001 | success/2 | PRD-PRIVACY-LOCAL | 통과 → **미실행** | 안내 DOM에 문구가 있지만 실제 안내 viewport에 노출되지 않았고, 관측 1–3 뒤 스크롤·후속 노출 없음 |
| 002 | success/2 | PRD-PRIVACY-LOCAL | 통과 → **미실행** | 해당 세션에서 같은 노출 공백을 독립 확인 |
| 003 | success/2 | PRD-PRIVACY-LOCAL | 통과 → **미실행** | 해당 세션에서 같은 노출 공백을 독립 확인 |
| 004 | success/2 | PRD-PRIVACY-LOCAL | 통과 → **미실행** | 해당 세션에서 같은 노출 공백을 독립 확인 |
| 015 | recovery/0 | CONDITIONAL-RECOVERY | N/A → **미실행** | obs-14의 실제 저장 실패로 복구 조건이 발생했으나 일반 재가져오기·저장 복구 없이 종료 |
| 026 | success/1 | PRD-PRIVACY-LOCAL | 통과 → **미실행** | 안내 obs-3·정책 obs-12에서 필요한 처리·미전송 안내가 노출되지 않았고 정책 본문 스크롤 없음 |
| 027 | success/1 | PRD-PRIVACY-LOCAL | 통과 → **미실행** | 안내 obs-3·정책 obs-11에서 같은 노출 공백을 독립 확인 |
| 028 | success/1 | PRD-PRIVACY-LOCAL | 통과 → **미실행** | 안내 obs-4·정책 obs-13에서 같은 노출 공백을 독립 확인 |

개인정보 안내가 제품에 없다는 뜻이나 제품 복구 자체가 실패했다는 뜻으로 확대하지 않는다. 개인정보 기준에 새로운 동일 화면 조건을 추가하지 않았다. 전체 교차 관측·PNG·최종 판정 연결은 [기준별 증거 목록](evidence-review.md)에 있고, 아래는 이번 마감에서 바이트 해시를 다시 확인한 대표 등록 로그다.

### 대표 로그 경로와 SHA-256

- **001:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljlmeakahgnhmnnffbajmljk/evidence/S-ljlmeakahgnhmnnffbajmljk/1/agent-observation-3.json`
  SHA `97a0a5cfecf20be60fcdedc4d337411630af2be4ea5663ca7d03dfa801a7f97a`.
- **002:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-ljffmnkkgdhopplfbhhegkma/evidence/S-ljffmnkkgdhopplfbhhegkma/1/agent-observation-3.json`
  SHA `c736929fe01dfb2ce9a7dbfe9f9f4c7018c85f315c86a19162b377e9c522ba14`.
- **003:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gimbpjkdealchomaigbnfkap/evidence/S-gimbpjkdealchomaigbnfkap/1/agent-observation-3.json`
  SHA `12dad02f4e3cab6d1bd834848dcb08d89c77567f08119a5b680a318d00dd2365`.
- **004:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-gppbnocdodpcpfackcopdgal/evidence/S-gppbnocdodpcpfackcopdgal/1/agent-observation-3.json`
  SHA `91fc6f7853a577ec33a3e516910dc73a67537810e31148af92298b6ccd55369d`.
- **015:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-jjlepgjfpnolfggebebihpij/evidence/S-jjlepgjfpnolfggebebihpij/1/agent-observation-14.json`
  SHA `f67307f55e89cc563f4d6c52657e5c0f7ff0eec6f17ad7b49b8e7d42327211e3`.
- **026:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-fcdfflmjpojkfdegbldhmpac/evidence/S-fcdfflmjpojkfdegbldhmpac/1/agent-observation-3.json`
  SHA `3a450895b0bdc4c61b49b13b9a8b0847375730ff16cfbc24a3528568a7e7bc15`.
- **027:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-noaaccdboboeobgidckidpei/evidence/S-noaaccdboboeobgidckidpei/1/agent-observation-3.json`
  SHA `204fce26519db4913af52250e03e7b9bfdb9cded7cef5fd4077f6f50b23c56b9`.
- **028:** `.ux-loop/peekly-completion32-pinned-20261115/stage-32/sessions/S-glflnkckgjoefhkcefjfjhih/evidence/S-glflnkckgjoefhkcefjfjhih/1/agent-observation-4.json`
  SHA `b044bbb121ad58d18a75c32f594eeeebebb164d8e8516ad45da98d0055d9d3de`.

## 4. 마감 보존 확인

원시 다섯 보고 파일, 원래 요청·응답·큐 상태, 명시 판정과 검토 집계 JSON, 이전 네 비교 열을 보존했다. 미평가 세 사례에 대한 재전송이나 추가 브라우저·모델 실행은 **0회**다. 기존 실제 실행은 승인된 `TOKENMAXX/deepseek-v4.1-flash-free` 경로만 사용했고, 유료 폴백·불확실 재전송은 0회다.

제품 결함의 P2/P3 분류와 18개 판정 정정은 [최종 보고서](final-review.md)에 유지했다. 이번 마감은 미평가·미실행의 사유와 증거를 확정한 것이며, 남은 실행 공백이 해소됐다는 주장은 하지 않는다.
