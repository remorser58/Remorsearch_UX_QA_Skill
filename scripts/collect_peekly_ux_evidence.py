#!/usr/bin/env python3
"""Extract narrow, reproducible UX signals from already audited observations.

No browser/model requests. Counts are synthetic-persona exposure counts, not
human prevalence. Severity and interpretation require review of the named PNGs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from audit_peekly_scale import artifact_bytes, normalized, sha

RELATIONS = ("나를 맞팔 안 한 사람", "내가 맞팔 안 한 사람", "맞팔 중인 사람")

def signals(observation):
    facts = observation["facts"]
    text = normalized(facts.get("text") or observation["text"])
    controls = facts.get("controls", [])
    labels = [normalized(c.get("label", "")) for c in controls]
    uploaded = (facts.get("last_action") == "upload" and "결과를 불러왔어요" in text
        and all(label in text for label in RELATIONS))
    found = []
    relation_controls = [c for c in controls if any(
        normalized(c.get("label", "")).startswith(label) for label in RELATIONS)]
    if uploaded and len(relation_controls) == 3 and all(c.get("visible") is False for c in relation_controls):
        found.append("UX-01")
    action = normalized(observation.get("action", ""))
    if ("더보기" in action and ("가져" in action or "파일" in action)
            and "약관과 개인정보" in text and "레이더" in text
            and not any("이미 받은 자료로 확인하기" in label for label in labels)):
        found.append("UX-02-detour")
    if any(normalized(c.get("label", "")) == "연결 관리와 다른 방법"
           and c.get("visible") is False for c in controls):
        found.append("UX-02-offscreen")
    if uploaded and "인스타를 한 번 연결" in text:
        found.append("UX-03")
    if ("1 / 3단계" in text and "인스타그램에 내 파일을 요청해요" in text
            and "받은 파일 바로 넣기" in labels):
        found.append("UX-04")
    return found

def collect(audit_paths):
    groups = {key: [] for key in ("UX-01", "UX-02-detour", "UX-02-offscreen", "UX-03", "UX-04")}
    inputs, sessions, failures = [], [], []
    for audit_path in audit_paths:
        raw = Path(audit_path).read_bytes()
        document = json.loads(raw)
        inputs.append({"path": str(audit_path), "sha256": sha(raw)})
        for run in document["runs"]:
            root = Path(run["local_run_root"])
            for session in run["sessions"]:
                sessions.append({"root": str(root), "persona_id": session["persona_id"],
                    "operational_completed": session["operational_completed"],
                    "status": session["queue_status"], "problem": session["problem"]})
                for criterion in session["criteria"]:
                    if criterion["status"] == "failed":
                        failures.append({"persona_id": session["persona_id"], "root": str(root),
                            "criterion": criterion, "independently_confirmed_product_defect": False})
                for descriptor in session["evidence"]["artifacts"]:
                    if descriptor["kind"] != "execution_log":
                        continue
                    obs = json.loads(artifact_bytes(root, descriptor))["observation"]
                    anchor = {"persona_id": session["persona_id"], "job_id": session["job_id"],
                        "run_root": str(root), "observation_id": obs["id"],
                        "log_path": descriptor["path"], "log_sha256": descriptor["sha256"],
                        "action": obs["action"], "viewport": obs["facts"].get("viewport"), "captures": []}
                    for cap in obs["captures"]:
                        relative = (Path("sessions") / session["job_id"] / cap["path"]).as_posix()
                        capture = {"path": relative, "kind": "screenshot", "sha256": cap["sha256"]}
                        artifact_bytes(root, capture)
                        anchor["captures"].append(capture)
                    for key in signals(obs):
                        groups[key].append(anchor)
    return {"schema_version": "peekly-ux-evidence-index.v1", "inputs": inputs,
        "new_model_calls": 0, "new_browser_calls": 0,
        "unique_personas": len({s["persona_id"] for s in sessions}),
        "attempt_sessions": sessions, "signals": {key: {
            "distinct_personas": sorted({row["persona_id"] for row in rows}),
            "distinct_persona_count": len({row["persona_id"] for row in rows}),
            "observations": rows} for key, rows in groups.items()},
        "model_failed_criteria_for_independent_review": failures,
        "real_user_evidence": False, "product_ready": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = collect(args.audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"unique_personas": result["unique_personas"],
        "signals": {key: value["distinct_persona_count"] for key, value in result["signals"].items()}}, ensure_ascii=False))

if __name__ == "__main__":
    main()
