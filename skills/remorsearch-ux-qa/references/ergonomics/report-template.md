# Report Template

`scripts/ergo_qa.py swarm` writes `report.md` in this structure. When editing it
by hand, keep the evidence boundaries.

```text
# 인간공학 페르소나 스웜 QA 보고서 — <제품/화면>

## 1. 범위와 증거 경계
- 표면(URL/앱/빌드), 기기·방향, 시나리오, 실행 수, 프로필 수
- 실측(observed) / 모델 예측(inferred) / 판단(inferred) 구분
- "k/n 시뮬레이션 프로필"은 커버리지이며 실제 사용자 비율이 아님
- 도달 모델은 보정 전(단독 P2 상한), 시선 모델은 휴리스틱
- 테스트한 기기, 다루지 않은 커버리지 층, 에이전트 한계/환경 문제

## 2. 실행 목록
run | 시나리오 | 기기 | 상태 | 성공 | 평가 프로필 | 에이전트(모델·입력 채널·실행 방식)

## 3. 프로필 (시나리오 가정)
ID | 설명 | 기기 | 표본 방식(커버리지 층/기저율) | 페르소나 데이터셋 연결(revision)

## 4. 발견 요약 (심각도 → 신뢰도 순)
ID | 심각도 | 범주 | 근거 | 대상 | 커버리지 | 차이 조건

## 5. 발견 상세
- 체크, 근거(실측/모델/판단), 모델 ID
- 관찰(수치와 기준), 스냅샷·관찰 ID
- 커버리지 k/n, 차이 조건(예: grip=one_hand_left)
- 원인 가설(표면 → 상호작용 → 제품/서비스 메커니즘)
- 권장 수정(수정 계층)과 트레이드오프
- 근거 문헌

## 6. 판단 계층과 휴리스틱 검토
- WCAG 예외, 비가역성, 시각적 위계, 광고 유사성
- UXD 체크(기대 vs 실제), 다크패턴 감사(별도 패스)

## 7. 시뮬레이션 담론(선택)
[시뮬레이션 · 합성 담론 · 실제 사용자 발화 아님] — 논점 유형과 검증 방법만, 수치 없음

## 8. 테스트하지 않은 것
플랫폼, 기기, 파지, 조건, 연령, 보조기술, 네트워크 상태

## 9. 다음 검증
- P0/P1 및 모델 기반 P2: 해당 조건의 실제 사용자 과제 테스트
- 커뮤니티 리서치(aside-community-ux-research) 검색어
- 수정 후 같은 시나리오·기기·프로필 재실행
```

Wording rules: state conditions, not frequencies ("왼손 한 손 파지·6.1인치 이상
폰에서 결제 버튼이 엄지 도달 범위 밖"), never "사용자의 N%"; no "예측", "users
will", or satisfaction/conversion claims without a measurement plan.
