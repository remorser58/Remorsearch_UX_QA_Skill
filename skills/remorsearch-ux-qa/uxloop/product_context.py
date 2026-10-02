"""Opt-in product-context intent protection bound to an immutable goal artifact.

The product-context artifact is authored by the host agent from actual project docs,
memory and the observed product; it is imported evidence, so every check below attests
consistency with the declared sources, never independent authenticity. Packets whose
goal carries no product_context_artifact_id keep the exact v1 behavior: these gates
only run while the binding exists, and the binding can never be added, removed or
replaced on resume because the goal is immutable.
"""
from __future__ import annotations

from pathlib import Path

from .evidence import Evidence
from .io import ContractError, GateStop, safe_relative, timestamp

SOURCE_KINDS = {"project_doc", "memory", "current_user_decision"}
MEMORY_SEARCH_STATUSES = {"searched_available", "searched_not_available"}
SCOPE_KEYS = {"paths", "scenario_ids"}


def context_binding(packet: dict) -> str | None:
    value = packet["goal"].get("product_context_artifact_id")
    return value if isinstance(value, str) and value else None


def _scope(record: dict, goal: dict, where: str) -> tuple[set[str], set[str]]:
    scope = record.get("scope")
    if not isinstance(scope, dict) or set(scope) - SCOPE_KEYS:
        raise GateStop("blocked", f"product context {where}: scope must name paths and/or scenario_ids only")
    paths = scope.get("paths", [])
    scenarios = scope.get("scenario_ids", [])
    if not isinstance(paths, list) or not isinstance(scenarios, list) or not (paths or scenarios):
        raise GateStop("blocked", f"product context {where}: scope must name at least one path or scenario")
    for name in paths:
        if not isinstance(name, str):
            raise GateStop("blocked", f"product context {where}: scope paths must be strings")
        try:
            safe_relative(name)
        except ContractError as exc:
            raise GateStop("blocked", f"product context {where}: {exc}") from exc
    if any(not isinstance(x, str) for x in scenarios) or set(scenarios) - set(goal["scenario_ids"]):
        raise GateStop("blocked", f"product context {where}: scope names scenarios outside the goal matrix")
    return set(paths), set(scenarios)


def _check_shape(packet: dict, payload: dict) -> None:
    def fail(reason: str) -> GateStop:
        return GateStop("blocked", "product context " + reason)

    if payload.get("kind") != "product_context":
        raise fail("artifact must carry kind=product_context")
    if payload.get("goal_id") != packet["goal"]["id"]:
        raise fail("goal_id does not match this goal")
    memory = payload.get("memory_search")
    if not isinstance(memory, dict) or memory.get("status") not in MEMORY_SEARCH_STATUSES:
        raise fail("memory_search must explicitly record searched_available or searched_not_available; "
                   "absent memory may not be presented as searched-and-found or fabricated")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise fail("must record at least one inspectable source (project docs, memory or a current user decision)")
    source_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("id"), str) or not source["id"]:
            raise fail("source entries need string ids")
        if source["id"] in source_ids:
            raise fail(f"source {source['id']}: duplicate id")
        source_ids.add(source["id"])
        if source.get("kind") not in SOURCE_KINDS:
            raise fail(f"source {source['id']}: kind must be project_doc, memory or current_user_decision; "
                       "intent cannot be inferred from code alone")
        for field in ("ref", "version", "checked_at"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise fail(f"source {source['id']}: {field} is required for inspectable source identity")
        if source["kind"] == "memory" and memory["status"] != "searched_available":
            raise fail(f"source {source['id']}: memory cannot be cited when the recorded search found none available")
    for group, text_field in (("constraints", "reason"), ("conflicts", "description")):
        records = payload.get(group)
        if not isinstance(records, list):
            raise fail(f"{group} must be a list")
        seen: set[str] = set()
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str) or not record["id"]:
                raise fail(f"{group}: entries need string ids")
            if record["id"] in seen:
                raise fail(f"{group} {record['id']}: duplicate id")
            seen.add(record["id"])
            if not isinstance(record.get(text_field), str) or not record[text_field].strip():
                raise fail(f"{group} {record['id']}: {text_field} is required")
            if record.get("source_id") not in source_ids:
                raise fail(f"{group} {record['id']}: source_id must reference a recorded source")
            _scope(record, packet["goal"], f"{group} {record['id']}")


def load_context(evidence: Evidence) -> dict:
    """Hash-verified read of the bound context artifact plus its shape contract."""
    binding = context_binding(evidence.packet)
    if binding is None:
        raise GateStop("blocked", "goal has no product_context_artifact_id binding")
    payload = evidence.payload(binding)
    _check_shape(evidence.packet, payload)
    return payload


def _overlapping(records: dict, payload: dict, group: str, fix: dict, goal: dict) -> list[dict]:
    """Entries whose declared scope touches this fix's changed paths or findings' scenarios."""
    fix_paths = set(fix.get("changed_paths") or [])
    fix_scenarios = {records["findings"][x]["scenario_id"] for x in fix["finding_ids"]}
    result = []
    for record in payload[group]:
        paths, scenarios = _scope(record, goal, f"{group} {record['id']}")
        if (paths & fix_paths) or (scenarios & fix_scenarios):
            result.append(record)
    return result


def _require_current_decision(state: dict, fix: dict, actor, context_at, label: str) -> None:
    """Only the operator's own recorded grant counts; a provider's packet claim never does."""
    grant = state["permissions"][fix["kind"]]
    if not isinstance(actor, str) or not actor.strip():
        raise GateStop("blocked", f"Fix {fix['id']} settles {label} without a recorded deciding actor; no code was written")
    if grant["actor"] != actor:
        raise GateStop("blocked", f"Fix {fix['id']} settles {label} as {actor!r}, but the recorded grant belongs to "
                                  f"{grant['actor']!r}; an imported provider claim is not a human decision")
    if timestamp(grant["at"]) < context_at:
        raise GateStop("blocked", f"Fix {fix['id']} relies on a decision about {label} recorded before the product "
                                  "context was authored; a current human decision is required")


def prewrite_gate(state: dict, evidence: Evidence, fix: dict, context: dict) -> None:
    """Runs before any write intent is planned: acknowledge every applicable constraint,
    and settle every overlapping unresolved conflict with a current human decision."""
    packet = evidence.packet
    goal = packet["goal"]
    records = evidence.records
    context_at = timestamp(evidence.artifacts[context_binding(packet)]["created_at"])
    acks = {x["constraint_id"]: x for x in (fix.get("constraint_acknowledgements") or [])}
    for constraint in _overlapping(records, context, "constraints", fix, goal):
        ack = acks.get(constraint["id"])
        if ack is None:
            raise GateStop("blocked", f"Fix {fix['id']} does not acknowledge preserved constraint "
                                      f"{constraint['id']}; no code was written")
        if not isinstance(ack.get("evidence"), str) or not ack["evidence"].strip():
            raise GateStop("blocked", f"Fix {fix['id']} acknowledges {constraint['id']} without a concrete "
                                      "prewrite decision; no code was written")
        if ack["decision"] == "authorized_change":
            _require_current_decision(state, fix, ack.get("actor"), context_at, f"constraint {constraint['id']}")
    resolutions = {x["conflict_id"] for x in (fix.get("conflict_resolutions") or [])}
    for conflict in _overlapping(records, context, "conflicts", fix, goal):
        if conflict["id"] not in resolutions:
            raise GateStop("blocked", f"Unresolved material intent conflict {conflict['id']} overlaps fix "
                                      f"{fix['id']}; settle it with a current human decision before any write")


def _review_entry(entry: dict, review_id: str, replay: dict, evidence: Evidence, label: str,
                  expected_outcome: str, scope_scenarios: set[str], kind: str) -> None:
    if not isinstance(entry.get("evidence"), str) or not entry["evidence"].strip():
        raise GateStop("unknown", f"Intent review {review_id} {kind} entry for {label} lacks concrete replay evidence")
    run_id = entry.get("run_id")
    if run_id not in set(replay["run_ids"]):
        raise GateStop("unknown", f"Intent review {review_id} cites run {run_id!r} outside this round's replay")
    if scope_scenarios and evidence.runs[run_id]["scenario_id"] not in scope_scenarios:
        raise GateStop("unknown", f"Intent review {review_id} cites a run outside the declared scope of {label}")
    if entry.get("outcome") != expected_outcome:
        raise GateStop("unknown", f"Intent review {review_id} outcome for {label} contradicts the recorded decision")


def verify_intent_review(state: dict, evidence: Evidence, replay: dict, revision: str, context: dict) -> None:
    """Completion gate: a fresh, replay-linked review must cover every applicable preserved
    constraint and resolved conflict with actual declared scenario evidence."""
    packet = evidence.packet
    goal = packet["goal"]
    records = evidence.records
    fixes = {x["id"]: x for x in packet["fixes"]}
    review_id = replay.get("intent_review_artifact_id")
    if not review_id:
        raise GateStop("blocked", f"Replay {replay['id']} has no linked intent review; preserved developer "
                                  "intent is unverified, so completion is refused")
    payload = evidence.payload(review_id)
    identity = {"kind": "intent_review", "replay_id": replay["id"], "code_revision": revision,
                "run_ids": replay["run_ids"]}
    if any(payload.get(k) != v for k, v in identity.items()):
        raise GateStop("unknown", f"Intent review {review_id} is stale, cross-round or contradicts the replayed revision")
    applied = [x["fix_id"] for x in state["applied_fixes"]]
    if payload.get("fix_ids") != applied:
        raise GateStop("unknown", f"Intent review {review_id} does not cover exactly the fixes applied so far")
    constraint_by_id = {x["id"]: x for x in context["constraints"]}
    conflict_by_id = {x["id"]: x for x in context["conflicts"]}
    expected_constraints: dict[tuple[str, str], str] = {}
    expected_conflicts: dict[tuple[str, str], str] = {}
    for fix_id in applied:
        fix = fixes[fix_id]
        acks = {x["constraint_id"]: x for x in (fix.get("constraint_acknowledgements") or [])}
        for constraint in _overlapping(records, context, "constraints", fix, goal):
            ack = acks.get(constraint["id"])
            if ack is None:
                raise GateStop("blocked", f"Applied fix {fix_id} was written without acknowledging {constraint['id']}")
            expected_constraints[(fix_id, constraint["id"])] = (
                "preserved" if ack["decision"] == "preserved" else "intentionally_changed")
        resolutions = {x["conflict_id"] for x in (fix.get("conflict_resolutions") or [])}
        for conflict in _overlapping(records, context, "conflicts", fix, goal):
            if conflict["id"] not in resolutions:
                raise GateStop("blocked", f"Applied fix {fix_id} was written despite unresolved conflict {conflict['id']}")
            expected_conflicts[(fix_id, conflict["id"])] = "resolved"
    for entries, expected, kind in ((payload.get("constraint_results") or [], expected_constraints, "constraint"),
                                    (payload.get("conflict_results") or [], expected_conflicts, "conflict")):
        if not isinstance(entries, list):
            raise GateStop("unknown", f"Intent review {review_id} {kind}_results must be a list")
        seen: set[tuple[str, str]] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise GateStop("unknown", f"Intent review {review_id} has a malformed {kind} entry")
            key = (entry.get("fix_id"), entry.get("constraint_id") if kind == "constraint" else entry.get("conflict_id"))
            if key in seen:
                raise GateStop("unknown", f"Intent review {review_id} duplicates {kind} coverage for {key[1]}")
            seen.add(key)
            outcome = expected.pop(key, None)
            if outcome is None:
                raise GateStop("unknown", f"Intent review {review_id} covers a {kind} that is not applicable: {key[1]}")
            record = (constraint_by_id if kind == "constraint" else conflict_by_id).get(key[1], {})
            _, scope_scenarios = _scope(record, goal, f"{kind} {key[1]}") if record else (set(), set())
            _review_entry(entry, review_id, replay, evidence, key[1], outcome, scope_scenarios, kind)
        if expected:
            missing = ", ".join(sorted(cid for _, cid in expected))
            raise GateStop("unknown", f"Intent review {review_id} does not cover applicable {kind}s: {missing}")
    capture_at = timestamp(evidence.artifacts[review_id]["created_at"])
    if capture_at < max(timestamp(evidence.runs[x]["ended_at"]) for x in replay["run_ids"]):
        raise GateStop("unknown", f"Intent review {review_id} predates its replay runs and is not fresh evidence")


def context_summary(state: dict) -> dict | None:
    """Best-effort report view; never turns an unreadable context into fabricated success."""
    packet = state["packet"]
    artifact_id = context_binding(packet)
    if artifact_id is None:
        return None
    summary: dict = {"artifact_id": artifact_id,
                     "intent_review_artifact_ids": {x["id"]: x.get("intent_review_artifact_id")
                                                    for x in packet["replays"]}}
    try:
        evidence = Evidence(packet, Path(state["evidence_root"]))
        context = load_context(evidence)
        summary["memory_search"] = context["memory_search"]["status"]
        summary["constraints"] = [{"id": x["id"], "title": x.get("title", ""), "scope": x["scope"]}
                                  for x in context["constraints"]]
        summary["unresolved_conflicts"] = [{"id": x["id"], "scope": x["scope"]} for x in context["conflicts"]]
        fixes = {x["id"]: x for x in packet["fixes"]}
        decisions = {}
        for applied in state["applied_fixes"]:
            fix = fixes[applied["fix_id"]]
            decisions[fix["id"]] = {
                "applicable_constraints": [x["id"] for x in _overlapping(
                    evidence.records, context, "constraints", fix, packet["goal"])],
                "acknowledgements": {x["constraint_id"]: x["decision"]
                                     for x in (fix.get("constraint_acknowledgements") or [])}}
        summary["applied_fix_decisions"] = decisions
    except (ContractError, GateStop, OSError, UnicodeError) as exc:
        summary["unavailable"] = str(exc)
    return summary
