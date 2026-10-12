# 호스트 복구와 인체공학 집계 검증 (2026-10-12)

맥미니에서 세션 중단·재개와 소스 변경 시 복구 동작을 확인했다. 인체공학 분석에서는 판단 불가 결과를 정상 비교 근거로 쓰던 오류를 고쳤다. 실제 앱의 접근성 기록은 [UniClub PR #1](https://github.com/remorser58/UniClub/pull/1)에서 별도로 관리한다. 이전 실행과 실패 자료는 모두 보존했다.

## 소스와 작업 범위

- 스킬 소스 핀: `2bec0934eec1b38fbea4511b939056dfcd6bf011` (branch codex/ios-evidence-adapter-20261012). 호스트·재배치 검증은 이 리비전의 git archive 추출본으로 수행했다. Python 전체 검사는 같은 리비전에 아래 두 파일의 집계 수정을 적용한 소스로 수행했고, 검사 전후 해시가 같다.
- 전역 설치 없음, 새 하니스·새 테스트 프레임워크 없음, UniClub은 Draft PR로 유지하며 병합·배포하지 않았다.
- 쓰기는 작업 전용 검증 폴더와 아래 집계 수정 두 파일로 한정했다. 자격증명 미열람, 계정 전환 없음.

## 세션 복구

- 수용 기준(원본 §7): "수정 후 세션 중단/재개와 concurrent source edit — 실제 체크포인트·현재 입력을 대조하고 이미 반영한 수정을 중복 적용하지 않음. 구 revision의 pass를 최신 결과로 재사용하지 않음." SIGTERM/비정상 종료 문면은 기준에 없다.
- 기존 ux_loop.py CLI만으로 소유 픽스처에서 실행: A 수정 전 중단→재개(exit 6→0, goal 동일), B 수정 후 중단→재개(6→0, 파일·적용 수 불변), C 수정 전 동시 편집(6→3, "Workspace drift before fix", 무기록), D 수정 후 동시 편집(6→4, "Scoped source changed after the recorded fix"), E workspace 불일치(2), E2 권한 revoke→blocked(3)→재승인→complete(0).
- 실제 Codex 모델 세션 2턴(신규 1 + 정확한 동일 스레드 재개 1)으로도 중단·재개 동작을 확인했다: 모델이 기존 CLI로 demo를 실행해 exit 6에서 정지, 재개 턴에서 resume exit 0, applied_fixes 1, 파일 해시 불변, report decision fixture_only_pass_not_product_verification. 이는 제어된 pause/resume 확인이며 SIGTERM 등 비정상 종료 복구는 미검증이다.

## 설치 위치 변경과 실제 호스트 사용

- 태스크 로컬 재배치(relocated): 파일 229개, payload sha256 `21c07825041343b2939aa9332904962ef682af9239e2eb40900acd2b51747872`(2bec 핀과 일치), 구 설치본 경로 참조 0건, node_modules 없음.
- 채택 검사: ux_loop.py --help·smoke_loop·validate·ref 모두 exit 0, missing-context improve는 exit 3(거부). 릴리스 번들은 2bec 추출본에서 기존 빌드 도구로 생성·검증(valid true).
- 구·신 설치본 구별: 구 SKILL.md `a564a03c...` → 신 `60fa8d05...`, uxloop/cli.py 변경, engine.py·product_context.py 동일. 구 설치본은 어떤 실행에도 쓰지 않았다.
- 실제 Codex 호스트 채택은 모델 세션 2턴으로만 제한 검증했다. 전역 skills·config·account는 변경하지 않았고(확인 근거: config sha256·skills 개수·실행 명령 범위), 다른 호스트는 미검증이다.

## 판단 불가 프로필의 비교군 제외

- 전체 파이썬 스위트: 1060 tests, OK, 0 skip (python-suite.log, 원본 hash `c23ebbc08e13381e370738c54c1bb2ea2c88ff4eabcb56b6875f76a82f87a0bf`).
- 수정 패치: swarm-unknown-correction.patch. 대상 파일 해시 — skills/remorsearch-ux-qa/ergoqa/swarm.py `b29ada24fc64f50755d0e205dbc2266465cc2ada1a10b58c316915bcbf20edd1`, tests/test_ergo_fixes.py `845cbe14feae4e048f486343d8627030920cb925060d1668f1856701c6ef0b1a`. diff --check 통과, 코드 변경은 이 두 파일뿐.
- 수정 계약: 같은 scenario/check/selector 그룹에서 명시적 inconclusive가 있는 프로필은 정상 비교군에서 제외한다. 앞 단계의 pass가 뒤 단계의 판정 불가를 덮지 않는다. 확정 실패와 판정 불가가 함께 있으면 실패로 유지한다.
- 최초 수정(393bf35b...)은 두 단계 반례(S-1 통과, S-2에서 고령 프로필만 확정 실패·젊은 프로필 판정 불가)로 실패해 교정했고, receipt.json·review.md는 첫 검증 시점 기록으로 보존했다. 이 집계 수정 후 벤치마크를 다시 실행하지 않았다. 기존 캡처에는 해당 inconclusive가 없어 성능 개선을 입증하는 자료가 되지 않는다.

## 과거 인체공학 실패

- heldout-2 noise 1.75(기준 0.35) 실패 판정 유지. H5 C3 0.083·C4@14 0.125 실패 유지. game-desktop 결과는 알려진 데이터의 회귀 검사로만 기록한다. 이번 수정은 과거 N/H5 문제를 해결한 것으로 주장하지 않는다.

## 원본 클라우드 실행 기록 확인

- heldout2-cloud-recovery.json: 실제 Claude 클라우드 세션에서 원본 cwd(`/home/user/ux-research-qa-skills`), 산출 경로(.ergo-bench/h2), 원본 command 4줄(record·analyse·analyse variant·score)을 회수했다. 트랜스크립트 결과: record/analyse exit 0, 녹화 25/26 성공, 1건 exit 3.
- 봉인 입력(sealed inputs) 원본 바이트는 미회수다. 파일 접근 UI가 "세션 파일을 보려면 세션을 시작하세요"를 요구했고, 클라우드 재시작·새 모델 턴은 하지 않았다. 읽기 전용으로 정확한 명령·경로를 확인했다. 현재 파일의 존재와 원본 바이트는 확인하지 못했다.

## 미검증 범위

- 모델 호스트 채택과 픽스처 실행은 완료했지만 제품 완성(product_complete)은 false다. 호스트 실행 결과는 fixture_only_pass_not_product_verification이다. 실사용자 효과·실기기·라이브 제공자 검증은 포함하지 않는다.
- SIGTERM 등 비정상 종료 복구, pending_intent 미해소 창, 다중 호스트, Figma·optional-source 라이브 실패 주입은 미검증으로 남긴다.

## 원본 증거

- 맥미니 루트: `/Volumes/SanDisk2TB/m4mini/remorsearch-validation-20261012`. `host-recovery-20261012/m07`, `host-recovery-20261012/m08/model-case`, `continuation-swarm-validation`에 원본 실행 기록이 있다.
- 로컬 루트: `/Users/r3m0r5e/.codex/visualizations/2026/10/02/01a0f9f0-f99f-74a0-b870-c3264edfd286/validation-20261012/continuation`. `host-execution`, `swarm-unknown`, `heldout2-cloud-recovery.json`과 `supervisor-acceptance.json`에 검토용 사본·해시·확인 결과가 있다.
- 현재 집계 코드와 호스트를 검증한 추출본의 버전은 구분했다. 패키지를 공개하거나 전역 스킬 설치본을 변경하지 않았다.
