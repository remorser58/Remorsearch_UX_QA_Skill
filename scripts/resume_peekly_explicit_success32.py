#!/usr/bin/env python3
"""Reconcile only proven completed-but-rejected model responses, then resume queued sessions.

No uncertain request is resent. The two reconciliations are limited to operations
whose local router ledger contains a completed response and quality rejection,
with no subsequent browser tool operation for that session. The free TOKENMAXX
rate review is retained as the cost basis; invoice verification remains false.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa/scripts"))
from live_scale_browser import BASE_URL, CHROME_DEFAULT, NODE_DEFAULT, _route
from uxpersonas.scale_browser_host import ScaleBrowserHost
from uxpersonas.scale_run import execute_scale
from uxpersonas.swarm_queue import Queue
from uxresearch.canonical import canonical
from uxresearch.storage import atomic


RUN = ROOT / ".ux-loop/peekly-explicit-success-32/stage-32"
FIXTURES = ROOT / ".ux-loop/peekly-fixtures-v4"
SKILL = ROOT / "skills/remorsearch-ux-qa"


async def main() -> None:
    queue = Queue(RUN)
    ledger_path = RUN / "model-router-ledger.live.json"
    router, providers, spec, routes = _route(ledger_path)

    # Resolve only the two quality-rejected model responses after verifying
    # completed TOKENMAXX response receipts and no later tool dispatch.
    unresolved = [op for op in queue.report()["operations"] if op["state"] == "uncertain"]
    ledger = json.loads(ledger_path.read_text())
    for op in unresolved:
        if op["kind"] != "model":
            raise RuntimeError("unexpected_uncertain_non_model_operation_preserved")
        events = [event for event in ledger["events"] if event.get("call_id") == op["id"]]
        successful = [event for event in events if event.get("status") == "success"]
        rejected = [event for event in events if event.get("status") == "quality_rejected"]
        if not successful or not rejected or any(not event.get("input_tokens") for event in successful):
            raise RuntimeError("uncertain_operation_lacks_completed_response_receipt:" + op["id"])
        report = queue.report()
        task_ops = [row for row in report["operations"] if row["job_id"] == op["job_id"]]
        ordered = sorted(task_ops, key=lambda row: row["started"])
        if ordered[-1]["id"] != op["id"] or any(row["kind"] == "tool" and row["started"] > op["started"] for row in task_ops):
            raise RuntimeError("uncertain_operation_has_later_side_effect_preserved:" + op["id"])
        reference = ("stage-32/model-router-ledger.live.json call_id=" + op["id"]
            + "; completed TOKENMAXX response and quality_rejected receipts; no subsequent tool dispatch; "
              "reviewed free TOKENMAXX route; provider invoice not independently verified; browser shutdown confirmed")
        queue.resolve_unknown(op["id"], actor="host-operator", evidence_reference=reference,
            stopped=True, charged_microusd=0)

    host = ScaleBrowserHost(target_url="http://127.0.0.1:4174/",
        chrome=Path(CHROME_DEFAULT), node=Path(NODE_DEFAULT),
        driver_path=SKILL / "drivers/web/scale_browser_cdp.mjs",
        adapter_path=SKILL / "uxpersonas/scale_browser_host.py",
        fixtures_path=FIXTURES, parallel_safe=True)
    stopped = False
    try:
        previous_done = -1
        while queue.report()["counts"]["queued"]:
            before = queue.report()
            done_before = sum(op["state"] == "done" for op in before["operations"])
            queue.authorize(plan_sha256=queue.plan_sha256,
                actor="user-approved-chat-instruction",
                consent_reference="2026-11-13 user authorized same frozen 32-persona Peekly run, free TOKENMAXX only, no paid fallback; resume only queued jobs and never resend uncertain operations",
                budget_microusd=0, expires_at=time.time() + 3600)
            queue.control("resume")
            await execute_scale(RUN, providers, host, reviewed=True, max_idle_seconds=60)
            after = queue.report()
            done_after = sum(op["state"] == "done" for op in after["operations"])
            if after["counts"]["queued"] and done_after == done_before:
                if previous_done == done_after:
                    break
                previous_done = done_after
        stopped = await host.shutdown()
    finally:
        if host.processes:
            await host.shutdown()
    if not stopped:
        raise RuntimeError("browser_shutdown_unconfirmed")
    report = queue.report()
    atomic(RUN / "resume-report.json", canonical(report))
    atomic(RUN / "model-router-ledger.json", canonical(router.report()))
    print({"counts": report["counts"], "operations": len(report["operations"]),
        "budget": report["budget"], "fallback_routes": routes,
        "browser_shutdown_confirmed": stopped,
        "provider_invoice_verified": False,
        "resume_stopped_with_queued": report["counts"]["queued"] > 0}, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
