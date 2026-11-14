"""Observable Peekly acceptance criteria for the owned desktop-browser run.

The catalog is derived from the saved Peekly PRD requirement IDs.  Checks are
conservative: a criterion is emitted only after its precondition and required
fixture actions are observed.  Missing observations remain not_run; they are
never silently promoted to a pass or converted to a failure.
"""
from __future__ import annotations

import hashlib
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
        "precondition": "current file-selection screen with saved small synthetic baseline", "action": "use upload_cancel with peekly-progress-sample.zip; verify both scoped processing phases, actual active stop and unchanged persisted state",
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
        "precondition": "pinned current synthetic import completed", "action": "open category and inspect count/list",
        "fixture": "peekly-sample-current.zip",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-RESULT-REVERSE": {
        "screen": "results category list", "selector": "button or tab with text 내가 맞팔 안 한 사람",
        "text": ["내가 맞팔 안 한 사람"], "value": "category label and count match imported fixture data",
        "precondition": "pinned current synthetic import completed", "action": "open category and inspect count/list",
        "fixture": "peekly-sample-current.zip",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-RESULT-MUTUAL": {
        "screen": "results category list", "selector": "button or tab with text 맞팔 중인 사람",
        "text": ["맞팔 중인 사람"], "value": "category label and count match imported fixture data",
        "precondition": "pinned current synthetic import completed", "action": "open category and inspect count/list",
        "fixture": "peekly-sample-current.zip",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-RESULT-SNAPSHOT": {
        "screen": "snapshot comparison", "selector": "result comparison summary",
        "text": ["팔로워에서 빠진 사람", "명"], "value": "two complete snapshots show the exact removed-follower count and matching account list; the UI does not infer a cause",
        "precondition": "two distinct synthetic snapshots imported in order",
        "action": "upload peekly-sample-previous.zip then peekly-sample-current.zip and open comparison",
        "timeout_seconds": 120, "scope": "desktop"},
    "PRD-RESULT-SEARCH": {
        "screen": "results relationship list", "selector": "input[type='search']",
        "text": ["이름 또는 아이디 찾기"], "value": "rows are ordered by username/ID; a visible enabled search input appears for >8 rows and an actual exact synthetic handle query narrows to one matching row",
        "precondition": "import peekly-search-ready.zip then open 나를 맞팔 안 한 사람 with 12 rows", "action": "type exact synthetic handle synthetic_search_outgoing_05 and observe one matching row",
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
        "precondition": "import same-account previous/current pair and open actual latest comparison account list", "action": "observe explanatory copy on the comparison, not the first-record preview",
        "timeout_seconds": 30, "scope": "desktop"},
    "PRD-IMPORT-SNAPSHOT-UNKNOWN": {
        "screen": "snapshot comparison", "selector": "comparison summary",
        "text": ["비교할 수 없", "기록이 없"], "value": "a legacy snapshot with unknown included-file provenance is excluded; a recognized empty import is known-empty",
        "precondition": "a legacy snapshot without includedFiles is configured and verified in the owned profile",
        "action": "not_run until an approved legacy-state setup capability exists; the known-empty ZIP cannot substitute for this precondition",
        "timeout_seconds": 120, "scope": "desktop"},
    "PRD-IMPORT-ALLTIME": {
        "screen": "Instagram export guide", "selector": "visible guide scene",
        "text": ["전체 기간"], "value": "all-time export choice is shown in the guide",
        "precondition": "open export request guide", "action": "advance through guide scenes",
        "timeout_seconds": 45, "scope": "desktop"},
    "PRD-IMPORT-SAVE-FAIL": {
        "screen": "import save failure", "selector": "[role=alert]",
        "text": ["결과를 저장하지 못했어요", "다시 저장"], "value": "a deterministic one-shot storage write failure shows a retry action and preserves prior result; retry succeeds",
        "precondition": "peekly-sample-current.zip has been saved in the isolated profile", "action": "use upload_save_failure with peekly-sample-previous.zip; verify error and unchanged state; click visible 다시 저장 and verify successful persisted retry before another action",
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
    return all(" ".join(str(value).replace("\u00a0", " ").split()) in normalized
               for value in values)


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
    text = " ".join(str(row.get("text", "")).replace("\u00a0", " ").split())
    rows = row.get("facts", {}).get("list_rows", [])
    return ("팔로워에서 빠진 사람" in text and "명" in text
            and isinstance(rows, list) and len(rows) > 0)


def _storage_available(snapshot):
    return (isinstance(snapshot, dict) and snapshot.get("available") is True
            and isinstance(snapshot.get("keys"), list)
            and bool(re.fullmatch(r"[0-9a-f]{64}", str(snapshot.get("sha256", "")))))


def _same_storage(before, after):
    return (_storage_available(before) and _storage_available(after)
            and before["sha256"] == after["sha256"]
            and sorted(before["keys"]) == sorted(after["keys"]))


NAMED_IMPORT_FIXTURE_SHA256 = {
    "peekly-malformed-html.zip": "9bc5fdf9bc926f3fada2b986508ab93bb018f450cd5bb597d407b998677e190d",
    "peekly-account-mismatch.zip": "a0fa22372bb16645faed613d09c962ccc7611421dd7f934d54bb32c59aaad795",
    "peekly-search-ready.zip": "c1901b1151716053a5fc31ec9eb9dee7d51cbb3c665dbf8d7607849fdea8e6e2",
}


def _named_import_attempt(row, fixture):
    """Bind a named fixture to its own reviewed upload, never nearby copy."""
    facts = row.get("facts", {})
    attempt = facts.get("import_attempt")
    if not isinstance(attempt, dict) or fixture not in NAMED_IMPORT_FIXTURE_SHA256:
        return None
    attempt_id = attempt.get("attempt_id")
    if (
        facts.get("last_action") == "upload" and facts.get("uploaded_fixture") == fixture
        and attempt.get("tool") == "upload"
        and attempt.get("schema_version") == "peekly-import-attempt.v1"
        and attempt.get("fixture") == fixture
        and attempt.get("fixture_sha256") == NAMED_IMPORT_FIXTURE_SHA256.get(fixture)
        and isinstance(attempt_id, str) and bool(attempt_id)
        and facts.get("import_attempt_id") == attempt_id
    ):
        return attempt
    return None


def _preserved_named_rejection(row, fixture):
    """New rejection wording requires its own pinned upload and unchanged state."""
    attempt = _named_import_attempt(row, fixture)
    if attempt is None:
        return False
    before, after = attempt.get("storage_before"), attempt.get("storage_after")
    return (
        attempt.get("persistence_unchanged") is True
        and _same_storage(before, after)
        and _same_storage(after, row["facts"].get("storage_snapshot"))
    )


def _accepted_named_import(row, fixture):
    """Acceptance needs completion and a new saved state in the same attempt."""
    attempt = _named_import_attempt(row, fixture)
    if attempt is None:
        return False
    before, after = attempt.get("storage_before"), attempt.get("storage_after")
    phases = attempt.get("phase_samples", [])
    complete = isinstance(phases, list) and any(
        isinstance(phase, dict) and _contains(phase.get("text", ""), ["결과를 불러왔어요"])
        for phase in phases)
    return (
        complete and attempt.get("persistence_unchanged") is False
        and attempt.get("cancel_dispatched") is not True
        and _storage_available(before) and _storage_available(after)
        and not _same_storage(before, after)
        and _same_storage(after, row["facts"].get("storage_snapshot"))
    )


def _import_attempts(rows, tool):
    for position, row in enumerate(rows):
        attempt = row.get("facts", {}).get("import_attempt")
        if (isinstance(attempt, dict)
                and attempt.get("schema_version") == "peekly-import-attempt.v1"
                and attempt.get("tool") == tool
                and isinstance(attempt.get("attempt_id"), str)
                and re.fullmatch(r"[0-9a-f]{64}", str(attempt.get("fixture_sha256", "")))):
            yield position, row, attempt


def _attempt_rows(rows, start, attempt_id):
    return [row for row in rows[start:]
            if row.get("facts", {}).get("import_attempt_id") == attempt_id
            or (isinstance(row.get("facts", {}).get("import_attempt"), dict)
                and row["facts"]["import_attempt"].get("attempt_id") == attempt_id)]


def _progress_check(rows):
    attempts = [(position, row, attempt) for position, row, attempt
                in _import_attempts(rows, "upload_cancel")
                if attempt.get("fixture") == "peekly-progress-sample.zip"]
    if not attempts:
        return "not_run", "Use upload_cancel on the approved progress fixture; a requested stop label or a fast completed upload does not prove an active cancellation."
    failure = None
    passed = False
    for _, _, attempt in attempts:
        actual_cancel = attempt.get("cancel_active") is True and attempt.get("cancel_dispatched") is True
        terminal = attempt.get("terminal_state")
        before, after = attempt.get("storage_before"), attempt.get("storage_after")
        if (actual_cancel and terminal == "completed_after_cancel"
                and _storage_available(before) and _storage_available(after)
                and not _same_storage(before, after)):
            failure = ("failed", "A verified active cancel was dispatched, but completion was then observed with changed persisted state for that upload.")
        if not actual_cancel or terminal != "cancelled_without_new_result":
            continue
        if not _same_storage(attempt.get("storage_before"), attempt.get("storage_after")):
            continue
        # Read/analysis sub-obligations may be observed in a separate upload of
        # the exact same approved fixture in this session. Never use global
        # setup-result text or a phase from another fixture.
        phases = []
        for row in rows:
            candidate = row.get("facts", {}).get("import_attempt", {})
            if (isinstance(candidate, dict)
                    and candidate.get("schema_version") == "peekly-import-attempt.v1"
                    and candidate.get("fixture") == attempt["fixture"]
                    and candidate.get("fixture_sha256") == attempt["fixture_sha256"]):
                phases.extend(str(item.get("text", "")) for item in candidate.get("phase_samples", [])
                              if isinstance(item, dict))
        if _contains(" ".join(phases), ["파일을 읽고 있어요", "팔로우 목록을 확인하고 있어요"]):
            passed = True
    return failure or (("passed", None) if passed else ("not_run", "The active cancel, both scoped phases and unchanged persisted result were not all observed; a missed timing window is not a product failure."))


def _save_failure_check(rows):
    attempts = list(_import_attempts(rows, "upload_save_failure"))
    if not attempts:
        return "not_run", "Use the bounded upload_save_failure tool with a saved synthetic baseline, then verify the visible retry action and its persisted result."
    passed = False
    for position, row, attempt in attempts:
        fault = attempt.get("storage_fault", {})
        before, after = attempt.get("storage_before"), attempt.get("storage_after")
        if not (isinstance(fault, dict) and fault.get("key") == "peekly_state_v7" and fault.get("consumed") is True
                and fault.get("restored") is True and _storage_available(before)
                and "peekly_state_v7" in before["keys"]):
            continue
        related = _attempt_rows(rows, position, attempt["attempt_id"])
        error_rows = [item for item in related if any(
            _contains(item["text"], [message]) for message in (
                "결과를 저장하지 못했어요", "저장 공간이 부족해서 저장하지 못했어요"))]
        if not error_rows:
            continue
        if _storage_available(after) and not _same_storage(before, after):
            return "failed", "The injected save failure displayed an error but changed the previously persisted state."
        if not _same_storage(before, after):
            continue
        for error_row in error_rows:
            controls = _controls(error_row)
            complete_controls = 0 < len(controls) < 100
            picker = any(c.get("visible") is True and c.get("disabled") is not True
                         and _contains(c.get("label", ""), ["다른 파일 고르기"]) for c in controls)
            retry_control = any(_contains(c.get("label", ""), ["다시 저장"]) for c in controls)
            if complete_controls and picker and not retry_control:
                return "failed", "The write-failure notice and unchanged persisted state were observed, but the PRD-required direct save-retry control was absent; only file re-selection was offered."
        retry_seen = False
        for item in related:
            current_facts = item.get("facts", {})
            dispatch = current_facts.get("click_dispatch", {})
            is_retry = (isinstance(dispatch, dict) and dispatch.get("dispatched") is True
                        and dispatch.get("hit_test") is True
                        and _contains(dispatch.get("label", ""), ["다시 저장"]))
            if is_retry:
                retry_seen = True
            elif current_facts.get("last_action", "observe") not in {"observe", "wait"}:
                # The attempt ID persists until the next upload. A later sample,
                # reset or navigation click cannot establish retry success.
                retry_seen = False
            snapshot = item.get("facts", {}).get("storage_snapshot")
            saved = (_storage_available(snapshot) and "peekly_state_v7" in snapshot["keys"]
                     and snapshot["sha256"] != before["sha256"])
            if (retry_seen and saved and not any(_contains(item["text"], [message]) for message in (
                    "결과를 저장하지 못했어요", "저장 공간이 부족해서 저장하지 못했어요"))
                    and (_contains(item["text"], ["결과를 불러왔어요"])
                         or _category_counts(item["text"]) is not None)):
                passed = True
    return ("passed", None) if passed else ("not_run", "The consumed/restored fault, original-result preservation, actual retry click and successful new persisted result were not all observed for the same upload attempt.")


# Frozen oracle derived from the hash-verified v7 owned fixture's relationship JSON.
# These synthetic names are input expectations, never inferred from a sample screen.
RESULT_CURRENT_FIXTURE = "peekly-sample-current.zip"
RESULT_CURRENT_SHA256 = "938514f0010f47ace5c2a2fdae17d2c237fd82838cedd78829e0915d367ca186"
RESULT_SCOPE_KEYS = {
    "PRD-RESULT-RECIPROCITY": frozenset(("atelier.luna_", "ina.archive", "junho.jeong", "minsu.kim_", "taeo.kang_")),
    "PRD-RESULT-REVERSE": frozenset(("haneul.song", "seongsu.coffee")),
    "PRD-RESULT-MUTUAL": frozenset(("dohyun.fit", "haerin.daily", "minji_kim", "seojun.park", "yuna.choi")),
}


def result_scope_evidence(rows, requirement_id):
    """Bind one result category to an actual current-fixture import and list visit.

    Rows are admitted observations from one session, in order. Earlier incomplete
    visits do not veto a later complete visit; a proven failure remains visible.
    Returned indices name the import, category click, and actual list evidence.
    """
    if requirement_id not in RESULT_SCOPE_KEYS:
        return None
    label = CRITERIA[requirement_id]["text"][0]
    expected = RESULT_SCOPE_KEYS[requirement_id]
    norm = lambda value: " ".join(str(value or "").split())
    missing = {
        "status": "not_run", "indices": [],
        "reason": "The pinned current fixture and a subsequent matching category click/count/list were not observed in the same import attempt. Sample, stale, or unrelated lists cannot satisfy this criterion.",
    }
    anchor = opened = passed = failed = None
    known_digests = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        facts = row.get("facts", {})
        if not isinstance(facts, dict):
            continue
        text = str(row.get("text", ""))
        action = facts.get("last_action")
        requested_label = norm(facts.get("last_action_label"))
        if (_contains(text, ["샘플을 보고 있어요"]) or "샘플 닫기" in text
                or requested_label in {"샘플로 먼저 둘러보기", "샘플로 둘러보기"}):
            anchor = opened = None
            continue
        attempt = facts.get("import_attempt")
        if action in {"upload", "upload_cancel", "upload_save_failure"} or facts.get("uploaded_fixture"):
            anchor = opened = None
            if not isinstance(attempt, dict):
                continue
            attempt_id = attempt.get("attempt_id")
            before, after = attempt.get("storage_before"), attempt.get("storage_after")
            phases = attempt.get("phase_samples", [])
            complete = isinstance(phases, list) and any(
                isinstance(phase, dict) and _contains(phase.get("text", ""), ["결과를 불러왔어요"])
                for phase in phases)
            bound = (
                action == "upload" and attempt.get("tool") == "upload"
                and attempt.get("schema_version") == "peekly-import-attempt.v1"
                and facts.get("uploaded_fixture") == RESULT_CURRENT_FIXTURE
                and attempt.get("fixture") == RESULT_CURRENT_FIXTURE
                and attempt.get("fixture_sha256") == RESULT_CURRENT_SHA256
                and isinstance(attempt_id, str) and bool(attempt_id)
                and facts.get("import_attempt_id") == attempt_id
                and complete and _contains(text, ["결과를 불러왔어요"])
                and _storage_available(before) and _storage_available(after)
                and _same_storage(after, facts.get("storage_snapshot"))
                and attempt.get("cancel_dispatched") is not True
                and (not _same_storage(before, after) or after["sha256"] in known_digests)
            )
            if bound:
                anchor = {"id": attempt_id, "storage": after, "index": index}
                known_digests.add(after["sha256"])
            continue
        if anchor is None:
            continue
        if (facts.get("import_attempt_id") != anchor["id"]
                or not _same_storage(facts.get("storage_snapshot"), anchor["storage"])):
            anchor = opened = None
            continue
        if action == "click":
            opened = None
            click = facts.get("click_dispatch", {})
            actual_label = norm(click.get("label")) if isinstance(click, dict) else ""
            if (not isinstance(click, dict) or click.get("dispatched") is not True
                    or click.get("hit_test") is not True
                    or not isinstance(click.get("verified_selector"), str)
                    or not click["verified_selector"]
                    or actual_label != requested_label
                    or not actual_label.startswith(label + " ")):
                continue
            counts = re.findall(r"(\d+)\s*명", actual_label)
            if len(counts) != 1:
                continue
            opened = {"index": index, "count": int(counts[0])}
        elif action not in {"observe", "wait", "scroll"}:
            opened = None
        if opened is None:
            continue
        # A dashboard label is not the opened Sheet heading. The latter is a
        # separate exact line, as rendered by ResultsTab's LIST_COPY/openList.
        headings = [re.fullmatch(re.escape(label) + r"\s+(\d+)\s*명", norm(line))
                    for line in text.splitlines()]
        headings = [int(match.group(1)) for match in headings if match]
        people = facts.get("list_rows")
        if len(headings) != 1 or not isinstance(people, list) or not people:
            continue
        keys = [person.get("key") for person in people if isinstance(person, dict)]
        if len(keys) != len(people) or any(not isinstance(key, str) or not key for key in keys):
            continue
        indices = list(dict.fromkeys((anchor["index"], opened["index"], index)))
        if (opened["count"] != len(expected) or headings[0] != len(expected)
                or len(keys) != len(expected) or set(keys) != expected):
            failed = {
                "status": "failed", "indices": indices,
                "reason": "The category was inspected after the pinned current import, but its card count, opened-list count, or account keys differ from the fixture oracle.",
            }
        else:
            passed = {"status": "passed", "indices": indices}
    return failed or passed or missing


SEARCH_REQUIREMENT = "PRD-RESULT-SEARCH"
SEARCH_FIXTURE = "peekly-search-ready.zip"
SEARCH_QUERY = "synthetic_search_outgoing_05"
SEARCH_KEYS = tuple(f"synthetic_search_outgoing_{index:02d}" for index in range(12))
SEARCH_QUERY_SHA256 = hashlib.sha256(SEARCH_QUERY.encode("utf-8")).hexdigest()


def search_scope_evidence(rows):
    """Observe ResultsTab's actual field and one fresh exact-query/filter step."""
    missing = {
        "status": "not_run", "indices": [],
        "reason": "The owned 12-row list, visible enabled search input, and an actual exact-query/filter observation in the same list attempt were not all captured.",
    }
    anchor = baseline = passed = failed = None

    def search_field(row):
        fields = [control for control in _controls(row)
                  if control.get("tag") == "input" and control.get("type") == "search"
                  and control.get("visible") is True and control.get("disabled") is False
                  and control.get("readonly") is not True
                  and isinstance(control.get("selector"), str) and control["selector"]]
        return fields[0] if len(fields) == 1 else None

    def signature(facts, selector):
        checks = facts.get("typed_input_checks")
        if not isinstance(checks, list):
            return None
        matches = [check for check in checks if isinstance(check, dict)
                   and check.get("selector") == selector]
        if len(matches) != 1:
            return None
        check = matches[0]
        return (check.get("retained") is True, check.get("expected_sha256"), check.get("actual_sha256"))

    expected_signature = (True, SEARCH_QUERY_SHA256, SEARCH_QUERY_SHA256)
    for index, row in enumerate(rows):
        facts = row.get("facts", {})
        if facts.get("last_action") == "upload":
            anchor = baseline = None
            if _accepted_named_import(row, SEARCH_FIXTURE):
                anchor = {"index": index, "attempt": facts["import_attempt_id"],
                          "storage": facts["storage_snapshot"]}
            continue
        if (anchor is None or facts.get("import_attempt_id") != anchor["attempt"]
                or not _same_storage(facts.get("storage_snapshot"), anchor["storage"])
                or _contains(row.get("text", ""), ["샘플을 보고 있어요"])):
            anchor = baseline = None
            continue
        field = search_field(row)
        people = facts.get("list_rows")
        keys = [person.get("key") for person in people if isinstance(person, dict)] if isinstance(people, list) else None
        if (field is None or keys is None or len(keys) != len(people)
                or any(not isinstance(key, str) or not key for key in keys)
                or SEARCH_FIXTURE not in _row_uploads(row)):
            baseline = None
            continue
        action, selector = facts.get("last_action"), field["selector"]
        if baseline and (facts["import_attempt_id"] != baseline["attempt"]
                or not _same_storage(facts["storage_snapshot"], baseline["storage"])
                or selector != baseline["selector"]):
            baseline = None
        if action == "type":
            previous = rows[index - 1].get("facts", {}) if index else {}
            # A retained value from an old/wrong-field action cannot stand in for
            # this type event. The reviewed driver adds/updates this selector's
            # expected hash only when it actually dispatches that text input.
            if (baseline and isinstance(previous.get("typed_input_checks"), list)
                    and signature(facts, selector) == expected_signature
                    and signature(previous, selector) != expected_signature):
                indices = [anchor["index"], baseline["index"], index]
                if baseline["ordered"] and keys == [SEARCH_QUERY]:
                    passed = {"status": "passed", "indices": indices,
                              "summary": "Verified ordered 12-row ResultsTab list, visible enabled search field, actual exact-query input, and the one matching account."}
                else:
                    failed = {"status": "failed", "indices": indices,
                              "reason": "The exact query was entered into the observed search field, but the original list order or the one-account filtering result did not match the fixture."}
            baseline = None
            continue
        if len(keys) == 12 and set(keys) == set(SEARCH_KEYS):
            baseline = {"index": index, "selector": selector,
                        "attempt": facts["import_attempt_id"], "storage": facts["storage_snapshot"],
                        "ordered": keys == list(SEARCH_KEYS)}
        elif action not in {"observe", "wait", "scroll"}:
            baseline = None
    return failed or passed or missing


LEGACY_UNKNOWN_REQUIREMENT = "PRD-IMPORT-SNAPSHOT-UNKNOWN"
LEGACY_UNKNOWN_REASON = (
    "No approved host capability configured a legacy snapshot without includedFiles. "
    "The recognized known-empty ZIP and a later normal comparison do not exercise this precondition."
)


def unsupported_legacy_criterion(task, criterion):
    requirements, index = task.get("requirement_ids", []), criterion.get("index")
    return (criterion.get("kind") == "success" and isinstance(requirements, list)
            and isinstance(index, int) and 0 <= index < len(requirements)
            and requirements[index] == LEGACY_UNKNOWN_REQUIREMENT)


def unsupported_native_failure(task, criterion, observations):
    """Limit historical native-failure corrections to two explicit scope errors."""
    if unsupported_legacy_criterion(task, criterion):
        return True
    requirements, index = task.get("requirement_ids", []), criterion.get("index")
    return (criterion.get("kind") == "success" and isinstance(requirements, list)
            and isinstance(index, int) and 0 <= index < len(requirements)
            and requirements[index] == SEARCH_REQUIREMENT
            and search_scope_evidence(observations)["status"] != "failed")


def guard_peekly_scope(task, criteria, observations):
    """Bind only the explicitly reviewed Peekly requirements to their prerequisites.

    Relationship failures and unrelated criterion decisions remain untouched.
    Legacy-unknown has no configured setup. Search requires a fresh exact query;
    its historical placeholder-only failure is replaced by scoped DOM evidence.
    Both receipt paths use this after native merges and normal validation.
    """
    requirements = task.get("requirement_ids", [])
    if not isinstance(requirements, list):
        return criteria
    for criterion in criteria:
        if unsupported_legacy_criterion(task, criterion):
            criterion.update(status="not_run", evidence_ids=[], observation=LEGACY_UNKNOWN_REASON)
            continue
        index = criterion.get("index")
        if (criterion.get("kind") != "success"
                or not isinstance(index, int) or index < 0 or index >= len(requirements)
                or requirements[index] not in {*RESULT_SCOPE_KEYS, SEARCH_REQUIREMENT}):
            continue
        is_search = requirements[index] == SEARCH_REQUIREMENT
        if not is_search and criterion.get("status") != "passed":
            continue
        proof = (search_scope_evidence(observations) if is_search
                 else result_scope_evidence(observations, requirements[index]))
        sources = [observations[i] for i in proof["indices"]]
        captures_bound = bool(sources) and all(
            any(artifact.get("kind") == "screenshot" for artifact in source.get("artifacts", []))
            for source in sources)
        if proof["status"] == "not_run" or not captures_bound:
            criterion.update(
                status="not_run", evidence_ids=[],
                observation=proof.get("reason") or "The scoped criterion evidence has no bound screenshot for every required step.")
        else:
            criterion.update(
                status=proof["status"],
                observation=proof.get("reason") or proof.get("summary") or "Verified current-fixture import, subsequent category click, and matching count/account list in the same attempt.",
                evidence_ids=list(dict.fromkeys(
                    artifact["id"] for source in sources for artifact in source["artifacts"])))
    return criteria


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
                current_rejection = any(
                    _preserved_named_rejection(row, "peekly-malformed-html.zip")
                    and _contains(row["text"], ["[followers.html] 파일에서 팔로워·팔로잉 목록을 읽지 못해 불러오지 않았어요."])
                    for row in attempts)
                if any(_accepted_named_import(row, "peekly-malformed-html.zip") for row in attempts):
                    emit(index, "failed", "The pinned malformed HTML fixture completed and saved a new result in its own import attempt.")
                elif current_rejection or "파일에서 팔로워·팔로잉 목록을 읽지 못했어요" in attempted_text or "파일을 읽지 못했어요" in attempted_text:
                    emit(index, "passed")
                else:
                    emit(index, "not_run", "The malformed-HTML upload was observed but its own result state was not captured.")
        elif rid == "PRD-IMPORT-PROGRESS":
            status, reason = _progress_check(rows)
            emit(index, status, reason)
        elif rid == "PRD-IMPORT-SAVE-FAIL":
            status, reason = _save_failure_check(rows)
            emit(index, status, reason)
        elif rid == "PRD-IMPORT-ACCOUNT":
            attempts = _uploaded_rows(rows, "peekly-account-mismatch.zip")
            if not attempts:
                emit(index, "not_run", "The named account-mismatch fixture was not uploaded; another fixture's prior result cannot trigger this criterion.")
            else:
                attempted_text = "\n".join(row["text"] for row in attempts)
                current_rejection = any(
                    _preserved_named_rejection(row, "peekly-account-mismatch.zip")
                    and _contains(row["text"], ["계정의 파일이에요.", "지금 기록된 계정은", "같은 계정의 파일을 골라 주세요."])
                    for row in attempts)
                if any(_accepted_named_import(row, "peekly-account-mismatch.zip") for row in attempts):
                    emit(index, "failed", "The pinned account-mismatch fixture completed and saved a new result in its own import attempt.")
                elif current_rejection or "여러 계정의 정보가 섞여 있어요" in attempted_text or "파일 이름과 내용의 계정이 달라요" in attempted_text:
                    emit(index, "passed")
                else:
                    emit(index, "not_run", "The account-mismatch upload was observed but its own result state was not captured.")
        elif rid == "PRD-IMPORT-MISSING":
            follower_attempts = _uploaded_rows(rows, "peekly-missing-followers.zip")
            following_attempts = _uploaded_rows(rows, "peekly-missing-following.zip")
            if not follower_attempts or not following_attempts:
                emit(index, "not_run", "Both named missing-list fixtures were not uploaded; an unrelated previous result cannot trigger this criterion.")
            else:
                message = "팔로워와 팔로잉 목록이 모두 들어 있는 파일이 필요해요"
                rejected = [any(_contains(row["text"], [message]) for row in attempts)
                            for attempts in (follower_attempts, following_attempts)]
                accepted = any(_contains(row["text"], ["결과를 불러왔어요"])
                               for row in follower_attempts + following_attempts)
                if accepted:
                    emit(index, "failed", "A named missing-list fixture was accepted as a result.")
                elif all(rejected):
                    emit(index, "passed")
                else:
                    emit(index, "not_run", "Each missing-list fixture needs its own observed rejection; one fixture's message cannot establish both outcomes.")
        elif rid == "PRD-IMPORT-SIZE" and {"peekly-oversize-plus-one.zip", "@group:peekly-loose-file-over", "@group:peekly-loose-total-over"} <= uploads:
            zip_error = "128MB" in all_text and "ZIP 파일이 너무 커요" in all_text
            file_error = "파일 하나는 최대 32MB" in all_text
            total_error = "모두 합쳐 최대 64MB" in all_text
            if zip_error and file_error and total_error:
                emit(index, "passed")
        elif rid == LEGACY_UNKNOWN_REQUIREMENT:
            emit(index, "not_run", LEGACY_UNKNOWN_REASON)
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
        elif rid == "PRD-IDENTITY-LIMIT":
            comparison_rows = [row for row in rows if _comparison_with_names(row)]
            if any(_contains(row["text"], ["아이디 변경이나 계정 삭제 때문일 수도 있어요"])
                   for row in comparison_rows):
                emit(index, "passed")
            elif comparison_rows:
                emit(index, "failed", "The actual latest comparison and its account list were observed without the required identity-change/account-deletion explanation.")
            else:
                emit(index, "not_run", "Open the actual latest comparison explanation and its account list; a first-record preview or loading screen cannot establish this disclosure criterion.")
        elif rid in RESULT_SCOPE_KEYS:
            proof = result_scope_evidence(rows, rid)
            emit(index, proof["status"], proof.get("reason"))
        elif rid == SEARCH_REQUIREMENT:
            proof = search_scope_evidence(rows)
            emit(index, proof["status"], proof.get("reason"))
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
                # A count seen before the eleventh distinct import is not the
                # retained result. Read the latest qualifying history state.
                history_states = []
                for position, row in enumerate(rows):
                    row_uploads = _row_uploads(row, uploads if position == len(rows) - 1 else ())
                    if len(retention_uploads & row_uploads) < 11:
                        continue
                    normalized = " ".join(row["text"].split())
                    if re.search(r"(\d+)\s*(?:번|개)의 관계 기록", normalized):
                        history_states.append(normalized)
                history_text = history_states[-1] if history_states else ""
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
