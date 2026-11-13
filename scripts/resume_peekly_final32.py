#!/usr/bin/env python3
"""Safely settle zero-cap free-route transport uncertainties and resume queued v3 jobs."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa/scripts"))
from live_scale_browser import _route
from uxpersonas.scale_browser_host import ScaleBrowserHost
from uxpersonas.scale_run import execute_scale
from uxpersonas.swarm_queue import Queue
from uxresearch.canonical import canonical
from uxresearch.storage import atomic

RUN = ROOT / ".ux-loop/peekly-explicit-success-32-final/stage-32"
FIXTURES = ROOT / ".ux-loop/peekly-fixtures-v4"
SKILL = ROOT / "skills/remorsearch-ux-qa"


async def main() -> None:
    summary = json.loads((RUN / "stage-summary.json").read_text())
    if summary.get("browser_shutdown_confirmed") is not True:
        raise RuntimeError("prior_browser_shutdown_not_confirmed")
    if summary.get("configured_routes") != ["TOKENMAXX/deepseek-v4.1-flash-free"]:
        raise RuntimeError("unexpected_or_paid_route_in_prior_stage")
    if summary.get("budget", {}).get("ceiling") != 0:
        raise RuntimeError("free_route_zero_cap_not_verified")

    queue = Queue(RUN)
    router, providers, spec, routes = _route(RUN / "model-router-ledger.resume.live.json")
    old_ledger = json.loads((RUN / "model-router-ledger.live.json").read_text())
    report = queue.report()
    uncertain = [op for op in report["operations"] if op["state"] == "uncertain"]
    for op in uncertain:
        if op["kind"] not in {"model", "review"} or op["provider"] != "local-router" or op["reserved"] != 0:
            raise RuntimeError("uncertain_operation_outside_reviewed_free_zero_cap")
        events = [event for event in old_ledger.get("events", []) if event.get("call_id") == op["id"]]
        if not events or any(event.get("status") != "transport_or_protocol_error" for event in events):
            raise RuntimeError("uncertain_operation_has_non_transport_receipt")
        if any(event.get("input_tokens") is not None or event.get("output_tokens") is not None for event in events):
            raise RuntimeError("uncertain_operation_has_usage_receipt_preserve_for_review")
        reference = (
            "stage-32/model-router-ledger.live.json call_id=" + op["id"]
            + "; transport_or_protocol_error only; no response or usage receipt; "
              "user-authorized TOKENMAXX/deepseek-v4.1-flash-free only; reviewed price cap and reservation are zero; "
              "settled at reviewed zero-cap policy amount, NOT an independently verified provider invoice; "
              "browser shutdown confirmed; no automatic replay of this operation"
        )
        queue.resolve_unknown(op["id"], actor="host-operator",
            evidence_reference=reference, stopped=True, charged_microusd=0)

    host = ScaleBrowserHost(target_url="http://127.0.0.1:4174/",
        chrome=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        node=Path("/Users/m4mini/.aside/runtime/bin/node"),
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
                consent_reference="2026-11-13 user authorized the final fixed-engine 32-persona v3 rerun using free TOKENMAXX only; no paid fallback; resume queued jobs only; never resend uncertain operation IDs",
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
    final_report = queue.report()
    atomic(RUN / "resume-report.json", canonical(final_report))
    atomic(RUN / "model-router-ledger.resume.json", canonical(router.report()))
    print({"counts": final_report["counts"], "operations": len(final_report["operations"]),
        "budget": final_report["budget"], "configured_routes": routes,
        "browser_shutdown_confirmed": stopped, "provider_invoice_verified": False,
        "settled_unknown_operations": len(uncertain),
        "remaining_queued": final_report["counts"]["queued"]}, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
