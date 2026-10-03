# 이전 핸드오프 자료

현재 Mac mini 개발은 저장소 루트의 [HANDOFF.md](../../HANDOFF.md)부터 읽습니다.
이 폴더는 이전 클라우드 작업과 후속 Mac mini 핸드오프를 보관합니다.

[원클릭 개발 이전 Mac mini 핸드오프](mac-mini-before-one-request-20261003.md)는
`611ca99`까지의 루트 핸드오프를 바이트 단위로 옮긴 기록입니다.
SHA-256은 `9507312fafbf6d01c0a98b7040a914354333cb9209ed73a7abf104354e4690a3`입니다.
그 안의 상대 경로는 당시 저장소 루트 기준이며, 오래된 결과와 다음 작업 지시는 현재 상태를 대신하지 않습니다.

[당시 루트 핸드오프](cloud-handoff-through-20261001.md)는 옮기기 전 파일을 바이트 단위로 보존했습니다.
SHA-256은 `55ec71211c9b77e51250a262bb1b22d018d8326ad5a8f02966b32fee0b78e636`입니다.
그 안의 상대 경로는 당시 저장소 루트 기준입니다. 경로를 확인할 때 원래 위치를 고려하세요.

당시 할 일과 처리 수, 미확인 사실, 모델 추천, 작업 브랜치, 공개·삭제 지시는 역사 기록입니다.
현재 작업에 적용하려면 현재 코드·PRD·검증 기록과 대조해야 합니다.
이 폴더의 보존 기록은 설치용 배포물에서 제외되며, 보존을 위해 저장소에서 삭제할 필요는 없습니다.

| 경로 | 보관 내용 |
| --- | --- |
| `cloud-handoff-through-20261001.md` | 이전 핸드오프 원본 |
| `mac-mini-before-one-request-20261003.md` | 원클릭 개발 인계 이전의 Mac mini 핸드오프 원본 |
| `design/owner-decisions.md` | 한국형 팩 구현 당시 소유자 결정 D1~D13과 안전 규칙 S1~S6 |
| `design/design.json`, `design/critique.json`, `design/research.json` | 당시 설계·비판 검토·출처 조사 |
| `design/implement-results.json` | 당시 구현 결과와 미확인 항목 |
| `review/r1-legal.json`, `r2-code.json`, `r3-korean.json`, `r4-docs.json` | 당시 법·코드·한국어·문서 검토 |
| `review/fix-code.json` | 당시 수정 처리 결과 |
| `repro/code-review/`, `repro/legal-review/` | 당시 재현 스크립트와 오프라인 검사 도구 |
| `builders/platforms/`, `builders/statistics/` | 초기 플랫폼·통계 자료 생성 스크립트 |

재현 스크립트와 빌더에는 `/home/user/ux-research-qa-skills`, `/tmp/claude-0/` 같은 옛 경로가 있습니다.
일부 재현은 이후 제거된 동작이나 변경된 계약을 전제로 합니다. 현재 검사는 루트 핸드오프와 연결 문서를 따르세요.
빌더 실행 후 JSON·Markdown에 수동 수정이 있었으므로 그대로 재생성하면 현재 변경이 사라질 수 있습니다.
원문을 읽지 못했던 사실은 당시 확인 상태를 보존한 기록이며, 최신 출처 확인을 대신하지 않습니다.
