# 인수인계 자료 (클라우드 세션 → 로컬)

이 폴더는 클라우드 세션의 임시 작업 폴더에만 있던 자료를 옮겨 둔 것입니다. 무엇부터 할지는
레포 루트의 [`HANDOFF.md`](../../HANDOFF.md)를 먼저 읽으세요.

**공개 배포 전에 이 폴더, `HANDOFF.md`, `COORDINATION.md`를 모두 지웁니다.** 내부 작업 기록이고,
외부 문서를 요약한 내용이 섞여 있습니다.

## 들어 있는 것

| 경로 | 내용 | 언제 보나 |
| --- | --- | --- |
| `design/owner-decisions.md` | 한국형 팩(K1·K2) 구현 때 따른 소유자 결정 D1~D13과 안전 규칙 S1~S6(영어) | 규칙이 왜 그런지 확인할 때. 그 뒤 추가된 결정은 `HANDOFF.md` 3절 |
| `design/design.json` | 한국형 팩 설계: 파일별 개요, 설명문 변경안, 한국어 관례, 소유자 질문 | 설계 의도를 볼 때 |
| `design/critique.json` | 설계 비판 검토 26건(모두 반영하기로 한 것) | 반영 여부를 다시 볼 때 |
| `design/research.json` | 설계 전 조사 3묶음(발견과 출처 URL, 빈틈) | 사실을 다시 확인할 때의 출처 목록 |
| `design/implement-results.json` | 구현 에이전트 9명의 보고: 바뀐 파일, 인터페이스 메모, 설계와 다른 점, 미확인 사실, 남은 문제 | 코드와 문서가 왜 그렇게 되었는지 볼 때 |
| `review/r1-legal.json` | 법·안전 반박 검토 L-01~L-23 | 수정 대상 목록 |
| `review/r2-code.json` | 코드 정확성 반박 검토 C-01~C-17 | 수정 대상 목록 |
| `review/r3-korean.json` | 한국어 내용·사실 검토 K-01~K-16, 확인한 사실과 확인 못 한 사실 | 한국어 팩 수정 |
| `review/r4-docs.json` | 문서 일관성·패키징 검토 D-01~D-16 | 영어 문서·README 수정 |
| `review/fix-code.json` | 코드 수정 담당이 항목별로 남긴 처리 결과(fixed / partly_fixed / not_started / not_a_problem) | 무엇이 남았는지 볼 때 |
| `repro/code-review/` | 코드 검토자의 재현 스크립트 | 수정 뒤 문제가 사라졌는지 확인 |
| `repro/legal-review/` | 법·안전 검토자의 재현 스크립트와 오프라인 하네스(`harness.py`: 모든 DNS·연결을 거부하고 기록) | 같은 용도 |
| `builders/platforms/` | `korea-platforms.json`과 `platform-map.md`의 생성부를 만든 스크립트 | 플랫폼 지도를 다시 구성할 때 |
| `builders/statistics/` | `korea-statistics.json`을 만든 스크립트 | 통계 자료를 다시 만들 때 |

## 주의

- **재현 스크립트와 빌더에는 클라우드 경로가 박혀 있습니다.** `/home/user/ux-research-qa-skills`, `/tmp/claude-0/...` 같은 경로를 로컬 경로로 바꿔야 돌아갑니다.
- **빌더 결과는 지금 파일과 다릅니다.** 생성 뒤에 통합 에이전트와 코드 수정 담당이 JSON과 Markdown을 손으로 고쳤습니다. 빌더를 그대로 다시 돌리면 그 수정이 사라집니다. 먼저 출력과 현재 파일을 비교하세요. JSON과 Markdown을 함께 고치지 않으면 `tests/test_korean_pack.py`의 일치 검사가 깨집니다.
- **대부분의 한국 사이트는 클라우드 프록시에 막혀 있었습니다.** law.go.kr, ftc.go.kr, korea.kr, kosis.kr, 플랫폼 약관 페이지, developers.google.com이 그렇습니다. 문서에 `미확인` 또는 `미확인(요약)`으로 표시된 사실은 로컬에서 원문으로 다시 확인할 대상입니다.
