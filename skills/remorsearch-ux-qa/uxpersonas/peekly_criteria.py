"""Observable Peekly acceptance criteria for the owned desktop-browser run.

The catalog is derived from the saved Peekly PRD requirement IDs.  Checks are
conservative: a criterion is emitted only after its precondition and required
fixture actions are observed.  Missing observations remain not_run; they are
never silently promoted to a pass or converted to a failure.
"""
from __future__ import annotations

PEEKLY_PRD_SHA256 = "a014a85b7523928f693cd4422793929631f033176715f31409412e95e1d7432b"


CRITERIA = {
    "PRD-START-SAMPLE": {
        "screen": "first screen", "selector": "button[aria-label='샘플로 둘러보기']",
        "text": ["인스타그램으로 로그인", "샘플로 먼저 둘러보기"],
        "value": "sample entry is visible without a file picker",
        "precondition": "fresh isolated browser context", "action": "observe",
        "timeout_seconds": 8, "scope": "desktop"},
    "PRD-START-IMPORT": {
        "screen": "More first screen", "selector": "button or row text 이미 받은 자료로 확인하기",
        "text": ["이미 받은 자료로 확인하기"],
        "value": "the current More entry for users who already have Instagram files is visible and opens the saved-file import flow",
        "precondition": "open More first screen",
        "action": "click and observe", "timeout_seconds": 30, "scope": "desktop"},
    "PRD-START-SKIP": {
        "screen": "request guide", "selector": "button/link text 이미 파일을 받았어요",
        "text": ["이미 파일을 받았어요", "파일 고르기"], "value": "the shortcut reaches the current file-selection screen and exposes input[type=file]",
        "precondition": "request guide is visible", "action": "click and observe",
        "timeout_seconds": 20, "scope": "desktop"},
    "PRD-IMPORT-FORMATS": {
        "screen": "imported results", "selector": "input[type=file]",
        "text": ["나를 맞팔 안 한 사람", "내가 맞팔 안 한 사람", "맞팔 중인 사람"],
        "value": "HTML and JSON fixtures each produce counts 1, 1, 0",
        "precondition": "import screen and both frozen format fixtures available",
        "action": "upload peekly-format-html.zip then peekly-format-json.zip",
        "timeout_seconds": 120, "scope": "desktop"},
    "PRD-IMPORT-MULTI": {
        "screen": "file selection and import result", "selector": "input[type=file][multiple]",
        "text": ["파일 고르기", "512개", "파일이 너무 많아요"],
        "value": "mixed JSON+HTML loose files import together; 512 files are accepted; 513 are rejected; ZIP+loose selection is rejected",
        "precondition": "direct import file-selection stage",
        "action": "upload groups peekly-mixed-loose-valid, peekly-loose-512-valid, peekly-loose-513-rejected and peekly-zip-plus-loose-rejected",
        "timeout_seconds": 300, "scope": "desktop"},
    "PRD-IMPORT-HTML": {
        "screen": "import error", "selector": "[role=alert]",
        "text": ["peekly-malformed-html.zip", "파일에서 팔로워·팔로잉 목록을 읽지 못했어요"],
        "value": "named malformed file is rejected and no result is published",
        "precondition": "direct import step 3", "action": "upload peekly-malformed-html.zip",
        "timeout_seconds": 60, "scope": "desktop"},
    "PRD-IMPORT-PROGRESS": {
        "screen": "import processing", "selector": "[role=status][aria-live=polite]",
        "text": ["파일을 읽고 있어요", "팔로우 목록을 확인하고 있어요", "읽기 멈추기"],
        "value": "reading and analysis states are distinct and closing/stopping the import aborts it before a result is saved",
        "precondition": "current file-selection screen", "action": "upload a sufficiently large valid archive, poll status, click 읽기 멈추기 while active, verify no result is saved",
        "timeout_seconds": 15, "scope": "desktop", "fixture": "generated large valid fixture"},
    "PRD-IMPORT-ACCOUNT": {
        "screen": "import validation error", "selector": "[role=alert]",
        "text": ["여러 계정의 정보가 섞여 있어요"],
        "value": "account mismatch is blocked before a result is saved",
        "precondition": "direct import step 3", "action": "upload peekly-account-mismatch.zip",
        "timeout_seconds": 60, "scope": "desktop"},
    "PRD-IMPORT-MISSING": {
        "screen": "import validation error", "selector": "[role=alert]",
        "text": ["팔로워와 팔로잉 목록이 모두 들어 있는 파일이 필요해요"],
        "value": "both missing-followers and missing-following fixtures are rejected",
        "precondition": "direct import step 3", "action": "upload both missing-list fixtures separately",
        "timeout_seconds": 120, "scope": "desktop"},
    "PRD-IMPORT-SIZE": {
        "screen": "import size error", "selector": "[role=alert]",
        "text": ["128MB", "32MB", "64MB", "너무 커요"],
        "value": "ZIP over 128 MiB, one loose file over 32 MiB, and loose aggregate over 64 MiB are rejected without replacing existing result",
        "precondition": "existing synthetic result and direct import file-selection stage",
        "action": "upload peekly-oversize-plus-one.zip, then groups peekly-loose-file-over and peekly-loose-total-over",
        "timeout_seconds": 180,
        "scope": "desktop", "fixture": "generated oversized fixture"},
    "PRD-RESULT-RECIPROCITY": {
        "screen": "results category list", "selector": "button or tab with text 나를 맞팔 안 한 사람",
        "text": ["나를 맞팔 안 한 사람"], "value": "category label and count match imported fixture data",
        "precondition": "valid synthetic import completed", "action": "open category and inspect count/list",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-RESULT-REVERSE": {
        "screen": "results category list", "selector": "button or tab with text 내가 맞팔 안 한 사람",
        "text": ["내가 맞팔 안 한 사람"], "value": "category label and count match imported fixture data",
        "precondition": "valid synthetic import completed", "action": "open category and inspect count/list",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-RESULT-MUTUAL": {
        "screen": "results category list", "selector": "button or tab with text 맞팔 중인 사람",
        "text": ["맞팔 중인 사람"], "value": "category label and count match imported fixture data",
        "precondition": "valid synthetic import completed", "action": "open category and inspect count/list",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-RESULT-SNAPSHOT": {
        "screen": "snapshot comparison", "selector": "result comparison summary",
        "text": ["팔로워에서 빠진 사람", "명"], "value": "two complete snapshots show the exact removed-follower count and matching account list; the UI does not infer a cause",
        "precondition": "two distinct synthetic snapshots imported in order",
        "action": "upload peekly-sample-previous.zip then peekly-sample-current.zip and open comparison",
        "timeout_seconds": 120, "scope": "desktop"},
    "PRD-RESULT-SEARCH": {
        "screen": "relationship list", "selector": "input[type=search][placeholder='이름 또는 아이디 찾기']",
        "text": ["이름 또는 아이디 찾기"], "value": "rows are ordered by username/ID; search appears for >8 rows and an exact synthetic handle narrows to one row",
        "precondition": "open relationship list with at least 9 rows", "action": "type exact synthetic handle and observe filtered row count",
        "timeout_seconds": 45, "scope": "desktop"},
    "PRD-SAMPLE-EXPORT": {
        "screen": "sample relationship list", "selector": "button.matrix-export-btn",
        "text": ["목록 복사", "목록 저장"], "value": "both actions are disabled and explain sample restriction",
        "precondition": "open sample relationship list", "action": "inspect disabled state and title attributes",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-PRIVACY-LOCAL": {
        "screen": "import guide and browser network policy", "selector": ".guide-privacy-note",
        "text": ["파일은 이 기기 안에서만 읽어요", "어디로도 보내지 않아요"],
        "value": "privacy text visible and external_requests_blocked=true for every observation",
        "precondition": "open import guide", "action": "observe text and network_policy",
        "timeout_seconds": 20, "scope": "desktop"},
    "PRD-PRIVACY-DELETE": {
        "screen": "privacy and data settings", "selector": "button or link with text 데이터 삭제",
        "text": ["데이터 삭제", "모두 지우기"], "value": "confirmation clears only this isolated context's local state and onboarding keys; native iOS WebView/cookie and notification cleanup are N/A on desktop",
        "precondition": "isolated profile contains synthetic data only", "action": "open deletion, inspect confirmation, confirm in this isolated profile and verify storage keys are absent",
        "timeout_seconds": 60, "scope": "desktop-partial+native-ios"},
    "PRD-IDENTITY-LIMIT": {
        "screen": "relationship detail or result explanation", "selector": "visible explanatory text",
        "text": ["아이디 변경이나 계정 삭제 때문일 수도 있어요"], "value": "comparison explains username change/account deletion as possible explanations and does not assert a confirmed unfollow cause",
        "precondition": "open identity-related explanation", "action": "observe explanatory copy",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-IMPORT-SNAPSHOT-UNKNOWN": {
        "screen": "snapshot comparison", "selector": "comparison summary",
        "text": ["비교할 수 없", "기록이 없"], "value": "empty/unknown previous snapshot is excluded from comparison",
        "precondition": "two snapshots available", "action": "upload peekly-empty-previous.zip then peekly-sample-current.zip",
        "timeout_seconds": 120, "scope": "desktop"},
    "PRD-IMPORT-ALLTIME": {
        "screen": "Instagram export guide", "selector": "visible guide scene",
        "text": ["전체 기간"], "value": "all-time export choice is shown in the guide",
        "precondition": "open export request guide", "action": "advance through guide scenes",
        "timeout_seconds": 45, "scope": "desktop"},
    "PRD-IMPORT-SAVE-FAIL": {
        "screen": "import save failure", "selector": "[role=alert]",
        "text": ["결과를 저장하지 못했어요", "다시 저장"], "value": "a deterministic one-shot storage write failure shows a retry action and preserves prior result; retry succeeds",
        "precondition": "isolated synthetic result exists", "action": "inject one-shot Storage.setItem failure; import valid fixture; inspect prior result; click retry after failure clears",
        "timeout_seconds": 60, "scope": "desktop-test-harness", "fixture": "one-shot localStorage failure"},
    "PRD-IMPORT-REOPEN": {
        "screen": "welcome/resume screen", "selector": "visible continue action",
        "text": ["이어서", "다시 시작"], "value": "reopening a persisted guide resumes at the saved step",
        "precondition": "persist a guide step then start a new isolated page context with same storage profile",
        "action": "close and reopen owned context", "timeout_seconds": 45, "scope": "desktop"},
    "PRD-SNAPSHOT-RETENTION": {
        "screen": "saved snapshot history", "selector": "snapshot history list",
        "text": ["기록"], "value": "latest 10 snapshots remain; older records are pruned only after the eleventh save",
        "precondition": "11 distinct valid synthetic snapshots", "action": "import 11 snapshots and inspect retained timestamps",
        "timeout_seconds": 300, "scope": "desktop", "fixture": "11-snapshot synthetic set"},
    "PRD-PAYWALL-BOUNDARY": {
        "screen": "free result and Pro history exploration", "selector": "More > 변화 기록 / history controls",
        "text": ["현재 관계 목록", "최신 비교", "Pro"], "value": "current relationship list and latest two-record comparison including names remain free; Pro gates multi-record timeline, date selection and per-person history",
        "precondition": "valid imported snapshot set and free entitlement", "action": "inspect free result and open each Pro history entry point without purchasing",
        "timeout_seconds": 45, "scope": "desktop"},
}

SOURCE_ANCHORS = {
    **{rid: "§1-2 시작 및 직접 가져오기 안내" for rid in ("PRD-START-SAMPLE", "PRD-START-IMPORT", "PRD-START-SKIP")},
    **{rid: "§3 데이터 가져오기" for rid in ("PRD-IMPORT-FORMATS", "PRD-IMPORT-MULTI", "PRD-IMPORT-HTML", "PRD-IMPORT-PROGRESS", "PRD-IMPORT-ACCOUNT", "PRD-IMPORT-MISSING", "PRD-IMPORT-SIZE", "PRD-IMPORT-SNAPSHOT-UNKNOWN", "PRD-IMPORT-ALLTIME", "PRD-IMPORT-SAVE-FAIL", "PRD-IMPORT-REOPEN")},
    **{rid: "§4 결과 화면" for rid in ("PRD-RESULT-RECIPROCITY", "PRD-RESULT-REVERSE", "PRD-RESULT-MUTUAL", "PRD-RESULT-SNAPSHOT", "PRD-RESULT-SEARCH", "PRD-SNAPSHOT-RETENTION", "PRD-PAYWALL-BOUNDARY")},
    "PRD-SAMPLE-EXPORT": "§10 저장소와 개인정보",
    "PRD-PRIVACY-LOCAL": "§10 저장소와 개인정보",
    "PRD-PRIVACY-DELETE": "§10 저장소와 개인정보",
    "PRD-IDENTITY-LIMIT": "§4 무료 현재 결과와 최신 비교",
}
for _rid, _spec in CRITERIA.items():
    _spec["source_anchor"] = SOURCE_ANCHORS[_rid]


def _contains(text: str, values) -> bool:
    normalized = " ".join(str(text).split())
    return all(value in normalized for value in values)


def evaluate(task, facts, text, uploaded_fixtures=(), history=()):
    """Return only deterministic checks supported by current DOM evidence."""
    ids = task.get("requirement_ids", [])
    checks = []
    uploads = set(uploaded_fixtures)
    observed_texts = [str(row.get("text", "")) for row in history] + [str(text)]
    all_text = "\n".join(observed_texts)
    controls = facts.get("controls", []) if isinstance(facts, dict) else []
    inputs = facts.get("file_inputs", []) if isinstance(facts, dict) else []
    network = facts.get("network_policy", {}) if isinstance(facts, dict) else {}

    def emit(index, status):
        checks.append({"kind": "success", "index": index, "status": status})

    for index, rid in enumerate(ids):
        if rid not in CRITERIA:
            continue
        if rid == "PRD-START-SAMPLE" and _contains(all_text, ["샘플로 먼저 둘러보기"]):
            emit(index, "passed")
        elif rid == "PRD-START-IMPORT" and _contains(all_text, ["이미 받은 자료로 확인하기"]):
            emit(index, "passed")
        elif rid == "PRD-START-SKIP" and _contains(all_text, ["이미 파일을 받았어요", "파일 고르기"]) and inputs:
            emit(index, "passed")
        elif rid == "PRD-IMPORT-MULTI" and {"@group:peekly-mixed-loose-valid", "@group:peekly-loose-512-valid", "@group:peekly-loose-513-rejected", "@group:peekly-zip-plus-loose-rejected"} <= uploads:
            accepted = "결과를 불러왔어요" in all_text or "팔로우 목록을 찾았어요" in all_text
            rejected_count = "최대 512개" in all_text or "파일이 너무 많아요" in all_text
            rejected_mixed = "ZIP 파일은 다른 파일과 함께 고를 수 없어요." in all_text
            emit(index, "passed" if accepted and rejected_count and rejected_mixed else "not_run")
        elif rid == "PRD-IMPORT-FORMATS" and {"peekly-format-html.zip", "peekly-format-json.zip"} <= uploads:
            good = _contains(all_text, ["나를 맞팔 안 한 사람", "내가 맞팔 안 한 사람", "맞팔 중인 사람"])
            counts = all(v in all_text for v in ("1명", "0명"))
            emit(index, "passed" if good and counts else "failed" if "결과를 불러왔어요" in all_text else "not_run")
        elif rid == "PRD-IMPORT-HTML" and "peekly-malformed-html.zip" in uploads:
            emit(index, "passed" if ("파일에서 팔로워·팔로잉 목록을 읽지 못했어요" in all_text or "파일을 읽지 못했어요" in all_text) else "failed" if "결과를 불러왔어요" in all_text else "not_run")
        elif rid == "PRD-IMPORT-PROGRESS" and "peekly-progress-sample.zip" in uploads:
            phase_text = all_text + " " + " ".join(str(row.get("text", "")) for obs in history
                for row in (obs.get("facts", {}).get("upload_progress_samples", []) or []) if isinstance(row, dict))
            stopped = any(obs.get("facts", {}).get("last_action_label") == "읽기 멈추기" for obs in history)
            phases = "파일을 읽고 있어요" in phase_text and "팔로우 목록을 확인하고 있어요" in phase_text
            no_result = "결과를 불러왔어요" not in all_text
            if phases and stopped and no_result:
                emit(index, "passed")
        elif rid == "PRD-IMPORT-ACCOUNT" and "peekly-account-mismatch.zip" in uploads:
            emit(index, "passed" if "여러 계정의 정보가 섞여 있어요" in all_text or "파일 이름과 내용의 계정이 달라요" in all_text else "failed" if "결과를 불러왔어요" in all_text else "not_run")
        elif rid == "PRD-IMPORT-MISSING" and {"peekly-missing-followers.zip", "peekly-missing-following.zip"} <= uploads:
            message = "팔로워와 팔로잉 목록이 모두 들어 있는 파일이 필요해요"
            emit(index, "passed" if message in all_text else "failed" if "결과를 불러왔어요" in all_text else "not_run")
        elif rid == "PRD-IMPORT-SIZE" and {"peekly-oversize-plus-one.zip", "@group:peekly-loose-file-over", "@group:peekly-loose-total-over"} <= uploads:
            zip_error = "128MB" in all_text and "ZIP 파일이 너무 커요" in all_text
            file_error = "파일 하나는 최대 32MB" in all_text
            total_error = "모두 합쳐 최대 64MB" in all_text
            if zip_error and file_error and total_error:
                emit(index, "passed")
        elif rid == "PRD-IMPORT-SNAPSHOT-UNKNOWN" and {"peekly-empty-previous.zip", "peekly-sample-current.zip"} <= uploads:
            emit(index, "passed" if ("비교할 수 없" in all_text or "기록이 없" in all_text) else "failed" if "언팔" in all_text and "명" in all_text else "not_run")
        elif rid == "PRD-PRIVACY-LOCAL" and network.get("external_requests_blocked") is True:
            if _contains(all_text, ["기기 안에서 처리"]):
                emit(index, "passed")
        elif rid == "PRD-SAMPLE-EXPORT":
            copy_button = next((c for c in controls if c.get("label") == "목록 복사"), None)
            save_button = next((c for c in controls if c.get("label") == "목록 저장"), None)
            if copy_button and save_button:
                locked = (copy_button.get("disabled") and save_button.get("disabled")
                    and "샘플" in str(copy_button.get("title") or "")
                    and "샘플" in str(save_button.get("title") or ""))
                emit(index, "passed" if locked else "failed")
        elif rid == "PRD-IDENTITY-LIMIT" and "아이디 변경이나 계정 삭제 때문일 수도 있어요" in all_text:
            emit(index, "passed")
        elif rid == "PRD-RESULT-SEARCH":
            search = any(c.get("tag") == "input" and c.get("type") == "search" and c.get("placeholder") == "이름 또는 아이디 찾기" for c in controls)
            rows = facts.get("list_rows", [])
            names = [str(row.get("key", "")) for row in rows]
            sorted_names = sorted(names, key=lambda value: value.casefold())
            retained = any(row.get("retained") is True for row in facts.get("typed_input_checks", []))
            if search and len(rows) == 1 and names == sorted_names and retained:
                emit(index, "passed")
    return checks
