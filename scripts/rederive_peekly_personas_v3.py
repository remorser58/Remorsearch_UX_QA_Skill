#!/usr/bin/env python3
"""Create a v3 current-PRD persona library without mutating the v2 source."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa"))
from uxpersonas.library import Library


REQUIREMENTS = {
    "PRD-START-SAMPLE": ("§1 제품 정의", "첫 화면에는 인스타그램으로 로그인 버튼과 샘플로 먼저 둘러보기 링크가 있다."),
    "PRD-START-IMPORT": ("§1 제품 정의", "이미 Instagram 자료를 받은 사용자는 더보기 첫 화면의 **이미 받은 자료로 확인하기**에서 직접 가져오기 흐름을 바로 연다."),
    "PRD-START-SKIP": ("§2 시작 안내", "1단계에는 **이미 파일을 받았어요** 링크가 있어 3단계로 바로 갈 수 있다."),
    "PRD-IMPORT-FORMATS": ("§3 데이터 가져오기", "Instagram이 HTML 형식으로 만든 백업과 JSON 형식으로 만든 백업을 똑같이 읽는다."),
    "PRD-IMPORT-MULTI": ("§3 데이터 가져오기", "ZIP 1개, 또는 압축을 푼 JSON·HTML 파일을 최대 512개까지 가져올 수 있다."),
    "PRD-IMPORT-HTML": ("§3 데이터 가져오기", "팔로워·팔로잉 HTML 목록에서 아이디를 읽지 못한 항목이 하나라도 있으면, 그 사람이 떠난 것처럼 보이지 않도록 파일 이름을 담은 오류로 멈춘다."),
    "PRD-IMPORT-PROGRESS": ("§3 데이터 가져오기", "가져오기는 백그라운드 워커에서 처리한다."),
    "PRD-IMPORT-ACCOUNT": ("§3 데이터 가져오기", "이미 기록된 계정과 다른 계정의 파일은 막는다."),
    "PRD-IMPORT-MISSING": ("§3 데이터 가져오기", "팔로워와 팔로잉이 모두 있어야 결과를 만들고, 하나라도 없으면 [팔로워 및 팔로잉]을 골랐는지 확인하라고 안내한다."),
    "PRD-IMPORT-SIZE": ("§3 데이터 가져오기", "ZIP은 최대 128MB까지 지원한다."),
    "PRD-RESULT-RECIPROCITY": ("§4 결과 화면", "나를 맞팔 안 한 사람 | 내가 팔로우하는데 나를 팔로우하지 않는다."),
    "PRD-RESULT-REVERSE": ("§4 결과 화면", "내가 맞팔 안 한 사람 | 나를 팔로우하는데 내가 팔로우하지 않는다."),
    "PRD-RESULT-MUTUAL": ("§4 결과 화면", "맞팔 중인 사람 | 서로 팔로우한다."),
    "PRD-RESULT-SNAPSHOT": ("§4 결과 화면", "같은 계정의 시점이 다른 완전한 기록이 두 개 있으면 최신 비교의 숫자와 계정 이름을 무료로 보여 준다."),
    "PRD-RESULT-SEARCH": ("§4 결과 화면", "목록은 아이디 순으로 정렬하고, 8명이 넘으면 아이디 찾기 칸을 표시한다."),
    "PRD-SAMPLE-EXPORT": ("§10 저장소와 개인정보", "샘플의 공유는 비활성화한다."),
    "PRD-PRIVACY-LOCAL": ("§10 저장소와 개인정보", "직접 연결·파일에서 받은 관계 목록과 기록 비교는 기기 안에서 처리한다."),
    "PRD-PRIVACY-DELETE": ("§10 저장소와 개인정보", "전체 초기화는 폴더 북마크와 로컬 저장소 키(v7·v6·legacy 상태, 시작 안내 단계·연결 정보·조회 일정 포함)를 지우고, 예약된 알림을 취소하고, iOS WebView 데이터와 쿠키 저장소를 삭제한다."),
    "PRD-IDENTITY-LIMIT": ("§4 결과 화면", "안정적 ID가 없는 백업 비교에는 이름 변경도 포함될 수 있다는 안내를 붙인다."),
    "PRD-IMPORT-SNAPSHOT-UNKNOWN": ("§3 데이터 가져오기", "목록이 실제로 비어 있었는지 알 수 없는 과거 백업은 비교 대상에서 제외한다."),
    "PRD-IMPORT-ALLTIME": ("§2 시작 안내", "기간 [전체 기간] → 내보내기 시작."),
    "PRD-IMPORT-SAVE-FAIL": ("§3 데이터 가져오기", "쓰기 실패 시 안내와 다시 저장 버튼을 표시한다."),
    "PRD-IMPORT-REOPEN": ("§2 시작 안내", "앱을 다시 열면 첫 화면에 이어서 할 일을 표시하고, 버튼을 누르면 저장된 단계에서 다시 시작한다."),
    "PRD-SNAPSHOT-RETENTION": ("§1 제품 정의", "무료·유료 모두 최근 최대 10개라는 기존 보관 범위를 유지한다."),
    "PRD-PAYWALL-BOUNDARY": ("§9 결제와 권한", "연결·현재 관계 목록과 이름·최신 두 기록 비교·직접 확인 기록은 무료다."),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-library", type=Path, required=True)
    parser.add_argument("--prd", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--diff-report", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_library.resolve(strict=True)
    prd = args.prd.resolve(strict=True)
    destination = args.destination.resolve()
    diff_path = args.diff_report.resolve()
    if destination.exists() or diff_path.exists():
        raise SystemExit("v3_destination_exists_preserved")
    raw = prd.read_bytes()
    prd_text = raw.decode("utf-8")
    prd_sha = hashlib.sha256(raw).hexdigest()
    requirements = []
    for rid, (anchor, excerpt) in REQUIREMENTS.items():
        if excerpt not in prd_text:
            raise SystemExit("current_prd_excerpt_missing:" + rid)
        requirements.append({"id": rid, "source_anchor": anchor, "excerpt": excerpt})
    source_doc = json.loads((source / "library.json").read_text())
    entries = source_doc["state"]["entries"]
    selected = []
    diff = {"schema_version": "peekly-persona-prd-diff.v1", "source_library": str(source),
        "source_prd_sha256": "5c18b75a9e4c5d31a1b8b45df60818a2391ea464d4010d976b94a0e908a6bb2d",
        "current_prd": str(prd), "current_prd_sha256": prd_sha,
        "persona_count": 0, "personas": [],
        "global_changes": [
            "Use current 51110f4 PRD's first-screen and More > saved-file entry labels; do not assume an older 3-step entry layout.",
            "Enforce 512 loose JSON/HTML files, 32 MiB per file, 64 MiB aggregate, and prohibit ZIP mixed with loose files.",
            "Use the current free latest-two-snapshot comparison and Pro multi-record timeline/date/person history boundary.",
            "Do not test native iOS WebView/cookie deletion, notification cancellation, or native share-sheet behavior in desktop Chrome; mark those N/A.",
            "Keep current list search label and username sorting requirement; no PRD requirement for a new alphabetical sort variant beyond username order.",
        ]}
    for key, history in sorted(entries.items()):
        if not key.startswith("peekly/PER-PEEKLY-V2-"):
            continue
        old = history[-1]
        profile = copy.deepcopy(old["profile"])
        ids = list(profile["requirement_ids"])
        if not ids or any(rid not in REQUIREMENTS for rid in ids):
            raise SystemExit("persona_requirement_mapping_missing:" + old["persona_id"])
        # Preserve each persona's behavioral identity and goals, while adding a
        # current-PRD execution directive to its existing behavior/context.
        profile["behaviors"].append("v3 판정: 51110f4 현재 PRD의 명시 기준과 해당 화면 증거로만 성공을 판단한다.")
        profile["assumptions"].append("판정 기준의 정본은 51110f4 docs/PRD.md이며 이전 PRD 문구는 성공 판정에 사용하지 않는다.")
        context = {"prd_path": str(prd), "prd_sha256": prd_sha, "requirements": requirements}
        selected.append({"persona_id": old["persona_id"], **profile, "claim_ids": []})
        diff["personas"].append({"persona_id": old["persona_id"], "preserved_revision": old["revision"],
            "new_requirement_ids": ids, "removed_requirement_ids": [],
            "excerpt_changes": [rid for rid in ids],
            "behavior_identity_preserved": True,
            "v3_execution_directive_added": True})
    if len(selected) != 32:
        raise SystemExit("expected_exactly_32_existing_peekly_personas")
    shutil.copytree(source, destination, copy_function=shutil.copy2)
    try:
        with Library(destination) as library:
            result = library.import_profiles({"schema_version": "ux-persona-library-input.v1",
                "product_id": "peekly", "mode": "prd_hypothesis",
                "context": {"prd_path": str(prd), "prd_sha256": prd_sha, "requirements": requirements},
                "personas": selected, "review_days": 30})
            current = library.list("peekly")["personas"]
        if len(current) != 32 or any(not row.get("reusable") for row in current):
            raise SystemExit("v3_library_revalidation_failed")
        diff["persona_count"] = len(selected)
        diff["new_revision_count"] = sum(bool(row["changed"]) for row in result["imported"])
        diff["current_reusable_count"] = sum(bool(row.get("reusable")) for row in current)
        diff["revision_map"] = [{"persona_id": row["persona_id"], "revision": row["revision"],
            "changed": row["changed"]} for row in result["imported"]]
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(json.dumps(diff, ensure_ascii=False, indent=2) + "\n")
        diff_path.chmod(0o600)
    except Exception:
        # Preserve the incomplete copy for inspection; never touch source.
        raise
    print(json.dumps({"persona_count": len(selected), "new_revision_count": diff["new_revision_count"],
        "current_reusable_count": diff["current_reusable_count"], "prd_sha256": prd_sha,
        "destination": str(destination), "diff_report": str(diff_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
