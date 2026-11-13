"""Observable Peekly acceptance criteria for the owned desktop-browser run.

The catalog is derived from the saved Peekly PRD requirement IDs.  Checks are
conservative: a criterion is emitted only after its precondition and required
fixture actions are observed.  Missing observations remain not_run; they are
never silently promoted to a pass or converted to a failure.
"""
from __future__ import annotations

import re

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
        "screen": "More first screen and existing-file import route",
        "selector": "button or row text 이미 받은 자료로 확인하기",
        "text": ["이미 받은 자료로 확인하기", "파일 고르기"],
        "value": "the current PRD requires the More entry to open the existing-file import flow; a separate request-guide shortcut labelled '이미 파일을 받았어요' is not required",
        "precondition": "open More and select the existing-file entry",
        "action": "verify the file picker is reached; do not require a legacy request-guide link",
        "timeout_seconds": 20, "scope": "desktop"},
    "PRD-IMPORT-FORMATS": {
        "screen": "imported results", "selector": "input[type=file]",
        "text": ["나를 맞팔 안 한 사람", "내가 맞팔 안 한 사람", "맞팔 중인 사람"],
        "value": "each valid complete Instagram HTML and JSON fixture produces counts 1, 1, 0; an incomplete HTML test fixture is not product evidence",
        "precondition": "import screen, both frozen format fixtures and fixture-shape validation available",
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
        "screen": "relationship list", "selector": "input[placeholder='아이디나 이름으로 찾기']",
        "text": ["아이디나 이름으로 찾기"], "value": "rows are ordered by username/ID; the text input appears for >8 rows and an exact synthetic handle narrows to one row",
        "precondition": "open relationship list with at least 9 rows", "action": "type exact synthetic handle and observe filtered row count",
        "timeout_seconds": 45, "scope": "desktop"},
    "PRD-SAMPLE-EXPORT": {
        "screen": "sample relationship list", "selector": "button.matrix-export-btn",
        "text": ["목록 복사", "목록 저장"], "value": "both actions are disabled and explain sample restriction",
        "precondition": "enter sample mode and open More > 관계 목록 (MatrixTab); a real-data relationship list is not this criterion",
        "action": "inspect both controls, disabled state and sample-specific title attributes; do not try to bypass disabled actions",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-PRIVACY-LOCAL": {
        "screen": "import guide and browser network policy", "selector": ".guide-privacy-note",
        "text": ["파일은 이 기기 안에서만 읽어요", "어디로도 보내지 않아요"],
        "value": "the product's own local-processing and no-send notice is visible; a host-enforced network block is not product privacy evidence",
        "precondition": "open import guide", "action": "observe the product privacy notice itself",
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
        "text": ["기록"], "value": "up to 10 snapshots are retained; under storage pressure older records may be removed, while the latest two must remain available",
        "precondition": "11 distinct valid synthetic snapshots and no observed storage-pressure condition",
        "action": "import 11 distinct snapshots and inspect retained timestamps; if storage pressure is observed, verify the latest two remain and record the reduced retention",
        "timeout_seconds": 300, "scope": "desktop", "fixture": "11-snapshot synthetic set"},
    "PRD-PAYWALL-BOUNDARY": {
        "screen": "free result and Pro history exploration", "selector": "More > 변화 기록 / history controls",
        "text": ["현재 관계 목록", "최신 비교", "Pro"], "value": "current relationship list and latest two-record comparison including names remain free; Pro gates extra multi-record timeline, date selection and per-person history; no upsell is required with fewer than two records",
        "precondition": "two valid snapshots for the same synthetic account and free entitlement",
        "action": "verify the current list and latest two-record comparison are free; open history/date-selection/per-person Pro entry points without purchasing",
        "timeout_seconds": 45, "scope": "desktop"},
}

SOURCE_ANCHORS = {
    **{rid: "§1-2 시작 및 직접 가져오기 안내" for rid in ("PRD-START-SAMPLE", "PRD-START-IMPORT", "PRD-START-SKIP")},
    **{rid: "§3 데이터 가져오기" for rid in ("PRD-IMPORT-FORMATS", "PRD-IMPORT-MULTI", "PRD-IMPORT-HTML", "PRD-IMPORT-PROGRESS", "PRD-IMPORT-ACCOUNT", "PRD-IMPORT-MISSING", "PRD-IMPORT-SIZE", "PRD-IMPORT-SNAPSHOT-UNKNOWN", "PRD-IMPORT-ALLTIME", "PRD-IMPORT-SAVE-FAIL", "PRD-IMPORT-REOPEN")},
    **{rid: "§4 결과 화면" for rid in ("PRD-RESULT-RECIPROCITY", "PRD-RESULT-REVERSE", "PRD-RESULT-MUTUAL", "PRD-RESULT-SNAPSHOT", "PRD-RESULT-SEARCH")},
    "PRD-SNAPSHOT-RETENTION": "§4 관계 기록 보관과 저장 공간",
    "PRD-PAYWALL-BOUNDARY": "§4 무료 최신 비교와 Pro 기록 기능 경계",
    "PRD-SAMPLE-EXPORT": "§10 저장소와 개인정보",
    "PRD-PRIVACY-LOCAL": "§10 저장소와 개인정보",
    "PRD-PRIVACY-DELETE": "§10 저장소와 개인정보",
    "PRD-IDENTITY-LIMIT": "§4 무료 현재 결과와 최신 비교",
}
for _rid, _spec in CRITERIA.items():
    _spec["source_anchor"] = SOURCE_ANCHORS[_rid]


def _contains(text: str, values) -> bool:
    normalized = " ".join(str(text).replace("\u00a0", " ").split())
    return all(value in normalized for value in values)


def _rows(history, text, facts):
    rows = []
    for item in history or ():
        if isinstance(item, dict):
            rows.append({"text": str(item.get("text", "")),
                         "facts": item.get("facts", {}) if isinstance(item.get("facts"), dict) else {}})
    rows.append({"text": str(text), "facts": facts if isinstance(facts, dict) else {}})
    return rows


def _row_uploads(row, fallback=()):
    values = row.get("facts", {}).get("fixture_uploads")
    return set(values) if isinstance(values, (list, tuple, set)) else set(fallback)


def _uploaded_rows(rows, fixture_name):
    return [row for row in rows
            if row.get("facts", {}).get("uploaded_fixture") == fixture_name]


def _fixture_validation(rows):
    validated = {}
    for row in rows:
        values = row.get("facts", {}).get("fixture_validation", [])
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, dict) and isinstance(item.get("fixture"), str):
                validated[item["fixture"]] = item
    return validated


def _controls(row):
    values = row.get("facts", {}).get("controls", [])
    return values if isinstance(values, list) else []


def _matrix_screen(row):
    text = row.get("text", "")
    controls = _controls(row)
    search = any(c.get("tag") == "input" and c.get("placeholder") == "아이디나 이름으로 찾기"
                 for c in controls)
    markers = (_contains(text, ["미맞팔", "나만 팔로우"])
               and ("맞팔 해제" in text or "맞팔 중인 사람" in text))
    return search or markers


def _sample_matrix_context(rows, index, row):
    controls = _controls(row)
    if any("샘플" in str(c.get("title") or "") for c in controls):
        return True
    if _contains(row.get("text", ""), ["샘플을 보고 있어요"]):
        return True
    if "샘플 닫기" in row.get("text", ""):
        return True
    entered_sample = any(
        previous.get("facts", {}).get("last_action_label") in {"샘플로 먼저 둘러보기", "샘플로 둘러보기"}
        or "샘플을 보고 있어요" in previous.get("text", "")
        or "샘플 닫기" in previous.get("text", "")
        for previous in rows[:index]
    )
    # A MatrixTab reached after the sample CTA and before any import is still
    # sample mode even when the tab itself has no banner text.
    return entered_sample and not _row_uploads(row)


def _category_counts(text):
    normalized = " ".join(str(text).split())
    result = {}
    for label in ("나를 맞팔 안 한 사람", "내가 맞팔 안 한 사람", "맞팔 중인 사람"):
        match = re.search(re.escape(label) + r".{0,64}?(\d+)\s*명", normalized)
        if not match:
            return None
        result[label] = int(match.group(1))
    return result


def _comparison_with_names(row):
    text = row.get("text", "")
    rows = row.get("facts", {}).get("list_rows", [])
    return ("팔로워에서 빠진 사람" in text and "명" in text
            and isinstance(rows, list) and len(rows) > 0)


def evaluate(task, facts, text, uploaded_fixtures=(), history=()):
    """Return only deterministic checks supported by current DOM evidence."""
    ids = task.get("requirement_ids", [])
    checks = []
    uploads = set(uploaded_fixtures)
    rows = _rows(history, text, facts)
    observed_texts = [row["text"] for row in rows]
    all_text = "\n".join(observed_texts)
    controls = facts.get("controls", []) if isinstance(facts, dict) else []
    inputs = facts.get("file_inputs", []) if isinstance(facts, dict) else []
    network = facts.get("network_policy", {}) if isinstance(facts, dict) else {}
    validations = _fixture_validation(rows)

    def emit(index, status, reason=None):
        check = {"kind": "success", "index": index, "status": status}
        if reason:
            check["reason"] = str(reason)[:320]
        checks.append(check)

    def import_route_state():
        entry_visible = any(_contains(row["text"], ["이미 받은 자료로 확인하기"]) for row in rows)
        picker_visible = any(
            bool(row["facts"].get("file_inputs")) or _contains(row["text"], ["파일 고르기"])
            for row in rows
        )
        entry_clicked = any(
            row["facts"].get("last_action_label") == "이미 받은 자료로 확인하기"
            for row in rows
        )
        return entry_visible, picker_visible, entry_clicked

    for index, rid in enumerate(ids):
        if rid not in CRITERIA:
            continue
        if rid == "PRD-START-SAMPLE" and _contains(all_text, ["샘플로 먼저 둘러보기"]):
            emit(index, "passed")
        elif rid in {"PRD-START-IMPORT", "PRD-START-SKIP"}:
            entry_visible, picker_visible, entry_clicked = import_route_state()
            if entry_visible and picker_visible:
                emit(index, "passed")
            elif entry_clicked:
                emit(index, "failed", "The current PRD More entry was clicked but the existing-file picker did not open.")
            else:
                emit(index, "not_run", "The current PRD More > 이미 받은 자료로 확인하기 route was not observed through to the file picker.")
        elif rid == "PRD-IMPORT-MULTI" and {"@group:peekly-mixed-loose-valid", "@group:peekly-loose-512-valid", "@group:peekly-loose-513-rejected", "@group:peekly-zip-plus-loose-rejected"} <= uploads:
            accepted = "결과를 불러왔어요" in all_text or "팔로우 목록을 찾았어요" in all_text
            rejected_count = "최대 512개" in all_text or "파일이 너무 많아요" in all_text
            rejected_mixed = "ZIP 파일은 다른 파일과 함께 고를 수 없어요." in all_text
            emit(index, "passed" if accepted and rejected_count and rejected_mixed else "not_run")
        elif rid == "PRD-IMPORT-FORMATS" and {"peekly-format-html.zip", "peekly-format-json.zip"} <= uploads:
            html_validation = validations.get("peekly-format-html.zip")
            if html_validation is None:
                emit(index, "not_run", "The HTML fixture's document shape was not validated; format parity cannot be attributed to the product.")
            elif html_validation.get("complete_html_documents") is not True:
                emit(index, "not_run", "The uploaded HTML fixture is incomplete (missing a complete html/body document); this is a fixture defect, not a product failure.")
            else:
                html_row = next((row for row in rows
                    if "peekly-format-html.zip" in _row_uploads(row)
                    and "peekly-format-json.zip" not in _row_uploads(row)), None)
                json_row = next((row for row in rows
                    if "peekly-format-json.zip" in _row_uploads(row)), None)
                expected = {"나를 맞팔 안 한 사람": 1, "내가 맞팔 안 한 사람": 1, "맞팔 중인 사람": 0}
                html_counts = _category_counts(html_row["text"]) if html_row else None
                json_counts = _category_counts(json_row["text"]) if json_row else None
                if html_counts == expected and json_counts == expected:
                    emit(index, "passed")
                elif html_counts is not None or json_counts is not None:
                    emit(index, "failed", "A valid HTML or JSON fixture produced counts that differ from the frozen expected result.")
                else:
                    emit(index, "not_run", "Both format-specific result observations were not captured.")
        elif rid == "PRD-IMPORT-HTML":
            attempts = _uploaded_rows(rows, "peekly-malformed-html.zip")
            if not attempts:
                emit(index, "not_run", "The named malformed-HTML fixture was not uploaded; a different HTML fixture cannot trigger this criterion.")
            else:
                attempted_text = "\n".join(row["text"] for row in attempts)
                if "파일에서 팔로워·팔로잉 목록을 읽지 못했어요" in attempted_text or "파일을 읽지 못했어요" in attempted_text:
                    emit(index, "passed")
                elif "결과를 불러왔어요" in attempted_text:
                    emit(index, "failed", "The explicitly malformed HTML fixture was accepted as a result.")
                else:
                    emit(index, "not_run", "The malformed-HTML upload was observed but its own result state was not captured.")
        elif rid == "PRD-IMPORT-PROGRESS" and "peekly-progress-sample.zip" in uploads:
            phase_text = all_text + " " + " ".join(str(row.get("text", "")) for obs in history
                for row in (obs.get("facts", {}).get("upload_progress_samples", []) or []) if isinstance(row, dict))
            stopped = any(obs.get("facts", {}).get("last_action_label") == "읽기 멈추기" for obs in history)
            phases = "파일을 읽고 있어요" in phase_text and "팔로우 목록을 확인하고 있어요" in phase_text
            no_result = "결과를 불러왔어요" not in all_text
            if phases and stopped and no_result:
                emit(index, "passed")
        elif rid == "PRD-IMPORT-ACCOUNT":
            attempts = _uploaded_rows(rows, "peekly-account-mismatch.zip")
            if not attempts:
                emit(index, "not_run", "The named account-mismatch fixture was not uploaded; another fixture's prior result cannot trigger this criterion.")
            else:
                attempted_text = "\n".join(row["text"] for row in attempts)
                if "여러 계정의 정보가 섞여 있어요" in attempted_text or "파일 이름과 내용의 계정이 달라요" in attempted_text:
                    emit(index, "passed")
                elif "결과를 불러왔어요" in attempted_text:
                    emit(index, "failed", "The explicitly mismatched-account fixture was accepted as a result.")
                else:
                    emit(index, "not_run", "The account-mismatch upload was observed but its own result state was not captured.")
        elif rid == "PRD-IMPORT-MISSING":
            follower_attempts = _uploaded_rows(rows, "peekly-missing-followers.zip")
            following_attempts = _uploaded_rows(rows, "peekly-missing-following.zip")
            if not follower_attempts or not following_attempts:
                emit(index, "not_run", "Both named missing-list fixtures were not uploaded; an unrelated previous result cannot trigger this criterion.")
            else:
                attempted_text = "\n".join(row["text"] for row in follower_attempts + following_attempts)
                message = "팔로워와 팔로잉 목록이 모두 들어 있는 파일이 필요해요"
                if message in attempted_text:
                    emit(index, "passed")
                elif "결과를 불러왔어요" in attempted_text:
                    emit(index, "failed", "A named missing-list fixture was accepted as a result.")
                else:
                    emit(index, "not_run", "Both missing-list uploads were observed but their result state was not captured.")
        elif rid == "PRD-IMPORT-SIZE" and {"peekly-oversize-plus-one.zip", "@group:peekly-loose-file-over", "@group:peekly-loose-total-over"} <= uploads:
            zip_error = "128MB" in all_text and "ZIP 파일이 너무 커요" in all_text
            file_error = "파일 하나는 최대 32MB" in all_text
            total_error = "모두 합쳐 최대 64MB" in all_text
            if zip_error and file_error and total_error:
                emit(index, "passed")
        elif rid == "PRD-IMPORT-SNAPSHOT-UNKNOWN" and {"peekly-empty-previous.zip", "peekly-sample-current.zip"} <= uploads:
            emit(index, "passed" if ("비교할 수 없" in all_text or "기록이 없" in all_text) else "failed" if "언팔" in all_text and "명" in all_text else "not_run")
        elif rid == "PRD-PRIVACY-LOCAL":
            guide_open = any("파일 고르기" in row["text"] or row["facts"].get("file_inputs") for row in rows)
            notice = _contains(all_text, ["파일은 이 기기 안에서만 읽어요", "어디로도 보내지 않아요"])
            if notice:
                emit(index, "passed")
            elif guide_open:
                emit(index, "failed", "The import guide was reached but the product's own local-processing notice was absent; host network blocking is not product evidence.")
        elif rid == "PRD-SAMPLE-EXPORT":
            sample_matrix = [(i, row) for i, row in enumerate(rows)
                             if _matrix_screen(row) and _sample_matrix_context(rows, i, row)]
            sample_entered = any(
                row["facts"].get("last_action_label") in {"샘플로 먼저 둘러보기", "샘플로 둘러보기"}
                or "샘플을 보고 있어요" in row["text"]
                or "샘플 닫기" in row["text"] for row in rows)
            if sample_matrix:
                matrix_row = sample_matrix[-1][1]
                matrix_controls = _controls(matrix_row)
                copy_button = next((c for c in matrix_controls if c.get("label") == "목록 복사"), None)
                save_button = next((c for c in matrix_controls if c.get("label") == "목록 저장"), None)
                if not copy_button or not save_button:
                    emit(index, "failed", "Sample MatrixTab was observed, but one or both required copy/save controls were missing.")
                else:
                    copy_locked = (copy_button.get("disabled") is True
                                   and "샘플" in str(copy_button.get("title") or "")
                                   and "복사" in str(copy_button.get("title") or ""))
                    save_locked = (save_button.get("disabled") is True
                                   and "샘플" in str(save_button.get("title") or "")
                                   and "저장" in str(save_button.get("title") or ""))
                    emit(index, "passed" if copy_locked and save_locked else "failed",
                         None if copy_locked and save_locked else "Sample export controls must both be disabled and explain the sample-only restriction.")
            elif sample_entered:
                emit(index, "not_run", "Sample mode was entered, but the actual More > 관계 목록 MatrixTab was not observed; a sample dashboard or detail modal is not the export screen.")
            else:
                emit(index, "not_run", "Sample mode was not observed; real-data export controls cannot be judged against the sample restriction.")
        elif rid == "PRD-IDENTITY-LIMIT" and "아이디 변경이나 계정 삭제 때문일 수도 있어요" in all_text:
            emit(index, "passed")
        elif rid == "PRD-RESULT-SEARCH":
            list_rows = [(row, row["facts"].get("list_rows", [])) for row in rows
                         if isinstance(row["facts"].get("list_rows"), list)]
            large_list = any(len(items) >= 9 for _, items in list_rows)
            search_visible = any(c.get("tag") == "input"
                and c.get("placeholder") == "아이디나 이름으로 찾기"
                for row in rows for c in _controls(row))
            typed_retained = any(check.get("retained") is True
                for row in rows for check in (row["facts"].get("typed_input_checks", []) or [])
                if isinstance(check, dict))
            latest_rows = next((items for _, items in reversed(list_rows) if items), [])
            names = [str(row.get("key", "")) for row in latest_rows]
            if large_list and not search_visible:
                emit(index, "failed", "A relationship list with at least nine rows was observed without the current PRD search input.")
            elif large_list and search_visible and len(latest_rows) == 1 and names == sorted(names, key=lambda value: value.casefold()) and typed_retained:
                emit(index, "passed")
            elif large_list:
                emit(index, "not_run", "The search control was present, but an exact-handle filtering observation was not captured.")
        elif rid == "PRD-RESULT-SNAPSHOT":
            if {"peekly-sample-previous.zip", "peekly-sample-current.zip"} <= uploads:
                if any(_comparison_with_names(row) for row in rows):
                    emit(index, "passed")
                elif "비교할 수 없" in all_text or "기록이 없" in all_text:
                    emit(index, "failed", "Two valid same-account snapshots were imported, but the latest comparison was unavailable.")
                else:
                    emit(index, "not_run", "Two snapshots were imported, but the latest comparison and its names were not opened.")
            else:
                emit(index, "not_run", "The two required distinct snapshots were not both imported.")
        elif rid == "PRD-SNAPSHOT-RETENTION":
            retention_uploads = {name for name in uploads
                if re.fullmatch(r"peekly-retention-snapshot-\d{2}\.zip", name)}
            if len(retention_uploads) < 11:
                emit(index, "not_run", f"Retention requires 11 distinct valid snapshot imports; observed {len(retention_uploads)}.")
            else:
                history_text = "\n".join(row["text"] for row in rows if "변화 기록" in row["text"] or "번의 관계 기록" in row["text"])
                count_match = re.search(r"(\d+)\s*(?:번|개)의 관계 기록", history_text)
                count = int(count_match.group(1)) if count_match else None
                storage_pressure = "저장 공간이 부족" in history_text or "storage pressure" in history_text.lower()
                if count == 10:
                    emit(index, "passed")
                elif count and count > 10:
                    emit(index, "failed", "The saved history exceeded the PRD maximum of ten retained snapshots.")
                elif storage_pressure and count and count >= 2:
                    emit(index, "passed", "Storage pressure was observed and the recent records remain available.")
                else:
                    emit(index, "not_run", "Eleven uploads were observed, but the retained-history count or storage-pressure explanation was not established.")
        elif rid == "PRD-PAYWALL-BOUNDARY":
            two_snapshots = {"peekly-sample-previous.zip", "peekly-sample-current.zip"} <= uploads
            if not two_snapshots:
                emit(index, "not_run", "The paywall boundary requires two valid snapshots for the same synthetic account.")
            else:
                free_comparison = any(_comparison_with_names(row) for row in rows)
                history_open = any(
                    ("기록 살펴보기" in row["text"] or "비교 시작 기록" in row["text"])
                    for row in rows
                )
                all_controls = [c for row in rows for c in _controls(row)]
                start_select = next((c for c in all_controls if c.get("tag") == "select"
                    and ("시작 기록" in str(c.get("label") or "") or "비교 시작" in str(c.get("label") or ""))), None)
                end_select = next((c for c in all_controls if c.get("tag") == "select"
                    and ("종료 기록" in str(c.get("label") or "") or "비교 종료" in str(c.get("label") or ""))), None)
                date_selects_locked = bool(start_select and end_select
                    and start_select.get("disabled") is True and end_select.get("disabled") is True)
                date_selects_enabled = bool(start_select and end_select
                    and start_select.get("disabled") is not True and end_select.get("disabled") is not True)
                pro_text = all(any(term in all_text for term in terms) for terms in (
                    ("변화 타임라인", "여러 기록의 변화", "여러 시점의 변화"),
                    ("두 날짜 선택 비교", "두 시점 비교", "날짜 선택"),
                    ("사람별 관계 이력", "개인별 이력", "한 사람의 관계 이력"),
                ))
                if free_comparison and history_open and date_selects_locked and pro_text:
                    emit(index, "passed")
                elif history_open and date_selects_enabled:
                    emit(index, "failed", "The free account exposed date-selection controls that the current PRD reserves for Pro.")
                else:
                    emit(index, "not_run", "The latest free comparison, history controls and Pro feature explanation were not all observed.")
    return checks
