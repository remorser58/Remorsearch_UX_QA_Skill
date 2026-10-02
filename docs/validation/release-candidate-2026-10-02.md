# 초기 통합 후보의 검증 기록 — 2026-10-02

이 문서는 같은 날 진행한 초기 패키지 실험의 보관 기록입니다. 아래 구성·파일·검사 수와
`ready: true`는 그때의 후보에만 해당합니다. 현재 후보의 완료 판정에 사용하지 않습니다.
현재는 `remorsearch-ux-qa`를 설치하고, 그 안의 `references/insane-search`에서 검색 자료를
사용합니다. 현재 빌드·검사 방법은 [release.md](../release.md)에 있습니다. 이 저장소에는
아래의 이전 ZIP과 로컬 검사 결과 파일이 포함되어 있지 않습니다.

초기 실험에서는 `insane-search` 안에서 Remorsearch의 research, persona-qa, ergonomics, loop 모드를 호출하는 로컬 후보를 검사했습니다. 당시 실제 배포, 설치된 스킬 변경, 커밋 푸시, PR 병합은 하지 않았습니다.

- 당시 배포물: `dist/release-candidate/bundle/insane-search-remorsearch.zip`
- 당시 기계 판독 결과: `dist/release-candidate/validation.json` — `ready: true`, `published: false`
- 재현 방법: [release.md](../release.md)
- 크기: 3,479,066바이트. 내용 명세에 217개 파일과 별도 명세 파일을 포함합니다.
- ZIP SHA-256: `8f0396f2e7782dd7ebde9a85070e6889bcb2b814cc5344111e48f464bebf9fa7`

검증은 Python 3.12.14, Node.js 22.23.3, Playwright 1.56.1과 해당 Chromium으로 수행했습니다. Python 테스트 786개와 압축을 푼 설치본의 브라우저 검사 387개가 모두 통과했습니다. 조사 엔진의 merge/gate/report-check/export-audience/minimize, loop의 권한·재개·실패 처리도 합성 자료로 실행했습니다. 설치 위치 변경, 무결성, 라이선스 보존, 서로 다른 출력 경로에서 만든 ZIP의 바이트 단위 재현성을 확인했습니다. 브라우저 실행 뒤 파일 무결성과 최종 소스 일치도 통과했습니다.

독립 실행 평가에서는 별도 Sol 에이전트가 제공된 QA 자료를 검증하고 임시 작업 공간에서 문구 수정과 재검증 자료 처리를 완료했습니다. 결과는 `fixture_only_pass_not_product_verification`, `product_complete: false`입니다. 이 검사는 실제 사용자 선호, 실사이트 접근, Figma 접근 또는 제품 접근성 인증을 입증하지 않습니다.

검토에서 수정한 주요 문제는 배포물의 웹 예제 누락, Python 버전 검사 불일치, 다른 `scripts` 패키지와의 충돌, 잘못된 근거 등급 절 번호와 오래된 gate 안내, Codex 설치 경로, 지원 Node 범위, 일반 실행 폴더로 인한 무결성 오탐입니다. 내부 import 해시를 전화·카드 번호로 오인하던 간헐적 minimize 실패도 고정된 입력으로 재현해 수정했습니다. 실제 개인정보와 출처가 맞지 않는 내부 참조를 거부하는 회귀 검사는 유지됩니다.

모델 분담은 GPT-6.1 Sol max의 구현·실행 평가, GLM 5.3 max의 런타임 검토, Grok 4.7 xhigh의 문서·배포 검토, GLM 5.3 Flash max의 통합 패키지 검토였습니다. GLM·Grok의 하위 에이전트 암호화 전달 오류는 같은 모델을 로컬 CLI로 호출해 해결했습니다. Flash는 설정된 Z.AI Coding Plan 경로를 사용했습니다. 별도 Fast 서비스 옵션과 사용자가 말한 Start plan 쿼터의 강제 지정·적용 여부는 제공된 실행 도구로 확인할 수 없었습니다.

원본 검색 스킬의 MIT 라이선스는 [공식 원문](https://github.com/fivetaku/insane-search/blob/main/LICENSE)을 그대로 보존해 `LICENSE.insane-search`로 포함했습니다. 원본 스킬은 읽기 전용 입력으로 사용했습니다. Remorsearch의 라이선스·제3자 고지도 포함했고 내부 인수인계 자료와 로컬 실행 데이터는 배포물에서 제외했습니다.

현재 후보에서 검색 자료의 라이선스는 `references/insane-search/upstream-LICENSE`에 보존합니다.
