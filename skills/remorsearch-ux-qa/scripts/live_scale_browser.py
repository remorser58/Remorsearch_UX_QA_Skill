"""Execute existing saved research personas through ScaleExecution, local model router and owned headless Chrome.

This entry never creates personas or a product target. It refuses missing/stale
libraries and only opens an explicit loopback app URL in isolated Chrome profiles.
"""
from __future__ import annotations
import argparse
import asyncio
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sys
import time
import urllib.request

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL))
from uxresearch.canonical import byte_digest, canonical
from uxresearch.storage import atomic, read_bytes, safe_path
from uxpersonas.library import Library
from uxpersonas.scale_entry import ScaleLimits, prepare_scale_goal, preview
from uxpersonas.scale_run import execute_scale
from uxpersonas.swarm_providers import ProviderSpec
from uxpersonas.model_router import ModelRoute, ModelRouter, RoutedScaleProvider
from uxpersonas.scale_browser_host import ScaleBrowserHost
from uxpersonas.agent_run import Tool

NODE_DEFAULT = "/Users/m4mini/.aside/runtime/bin/node"
CHROME_DEFAULT = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE_URL = "http://127.0.0.1:10100/v1"

TOOLS = [
    Tool("observe", "Read the current page title, visible text and visible controls; capture a screenshot.", {}, "owned_fixture_write"),
    Tool("click", "Click one visible, enabled, non-submit control by exact CSS selector and its exact visible label. The label is rechecked at action time to avoid stale selectors.", {"selector":"string","label":"string"}, "owned_fixture_write"),
    Tool("type", "Enter synthetic non-sensitive text into a visible text or textarea control by exact CSS selector.", {"selector":"string","value":"string"}, "owned_fixture_write"),
    Tool("upload", "Choose one hash-verified synthetic fixture from the reviewed fixture manifest for a visible or hidden single-file input.", {"selector":"string","file":"string"}, "owned_fixture_write"),
    Tool("scroll", "Scroll the current page by a bounded signed pixel delta.", {"delta":"integer"}, "owned_fixture_write"),
    Tool("wait", "Wait briefly for the current page to settle.", {"ms":"integer"}, "owned_fixture_write"),
]


def _route(ledger_path=None):
    secret = __import__("os").environ.get("PROXY_API_KEY")
    if not isinstance(secret, str) or not secret or len(secret) > 4096 or any(ord(c) < 33 or ord(c) > 126 for c in secret):
        raise RuntimeError("local_opencodex_auth_unavailable")
    request = urllib.request.Request(BASE_URL + "/models", headers={
        "Accept":"application/json", "Authorization":"Bearer " + secret})
    with urllib.request.urlopen(request, timeout=10) as response:
        catalog = json.loads(response.read(2 * 1024 * 1024 + 1))
    if not isinstance(catalog, dict) or not isinstance(catalog.get("data"), list):
        raise RuntimeError("open_codex_model_catalog_invalid")
    model_ids = {row.get("id") for row in catalog["data"] if isinstance(row, dict) and isinstance(row.get("id"), str)}
    primary = "TOKENMAXX/deepseek-v4.1-flash-free"
    if primary not in model_ids:
        # OpenCodex may omit a configured TOKENMAXX free default from /v1/models
        # while still accepting it at chat/completions. Permit only the exact
        # user-approved default/selected model from its local non-secret config.
        config_path = Path.home() / ".opencodex" / "config.json"
        try:
            config = json.loads(config_path.read_text())
            tokenmaxx = config["providers"]["TOKENMAXX"]
            configured = tokenmaxx.get("defaultModel") == "deepseek-v4.1-flash-free" or (
                "deepseek-v4.1-flash-free" in tokenmaxx.get("selectedModels", []))
            configured = configured and tokenmaxx.get("baseUrl") == "https://oc.hyeon.space/v1"
        except (OSError, ValueError, KeyError, TypeError):
            configured = False
        if not configured:
            raise RuntimeError("tokenmaxx_deepseek_v4_1_flash_free_not_in_local_catalog_or_provider_config")
    routes = [ModelRoute("TOKENMAXX", primary, "0", "0", 30,
        ("TOKENMAXX/deepseek-v4.1-flash-free", "deepseek-v4.1-flash-free", "deepseek-v4.1-flash"))]
    router = ModelRouter(BASE_URL, routes, timeout=60, max_retries=2,
        backoff_initial=2, backoff_max=30, ledger_path=ledger_path)
    # ProviderSpec's internal identifier intentionally excludes '/' while the
    # router retains and sends the exact catalog model ID above.
    spec = ProviderSpec(key="local-router", protocol="callback", model="tokenmaxx-deepseek-v4-1-flash-free",
        concurrency=2, requests_per_minute=30,
        input_price_per_million=0, output_price_per_million=0,
        input_token_cap=262144, output_token_cap=16384, timeout_seconds=240)
    provider = RoutedScaleProvider(spec, router)
    return router, {"local-router":provider}, spec, [route.model for route in routes]


def _load_personas(library_path, product_id, count):
    if not (library_path / "library.json").is_file():
        raise RuntimeError("saved_persona_library_missing")
    with Library(library_path) as library:
        rows = library.list(product_id)["personas"]
        reusable = [row for row in rows if row.get("reusable")]
    if len(reusable) < count:
        raise RuntimeError("insufficient_current_saved_personas:"+str(len(reusable)))
    return [row["persona_id"] for row in reusable[:count]]


async def run_stage(args, persona_ids, index):
    run_root = safe_path(args.run_root / ("stage-"+str(index)))
    if run_root.exists():
        raise RuntimeError("stage_output_exists")
    router, providers, spec, configured_routes = _route(run_root / "model-router-ledger.live.json")
    host = ScaleBrowserHost(target_url=args.url, chrome=args.chrome, node=args.node,
        driver_path=SKILL / "drivers/web/scale_browser_cdp.mjs",
        adapter_path=SKILL / "uxpersonas/scale_browser_host.py",
        fixtures_path=args.fixtures, parallel_safe=True)
    build = dict(id=args.build_id, artifact_path=str(args.build_artifact),
        sha256=byte_digest(read_bytes(args.build_artifact)))
    limits = ScaleLimits(parallel=2, turns=args.turns, call_seconds=240, task_seconds=1800,
        lease_seconds=300, budget_microusd=0, max_model_calls=len(persona_ids)*(args.turns+1))
    billing_review = {"input_token_cap":spec.input_token_cap,"output_token_cap":spec.output_token_cap,
        "input_price_per_million":spec.input_price_per_million,
        "output_price_per_million":spec.output_price_per_million,
        "no_unpriced_features":True,
        "free_tier":True,"billing_source":"free",
        "requested_model":"TOKENMAXX/deepseek-v4.1-flash-free",
        "source":"User-supplied Mac mini OpenCodex diagnostic confirms TOKENMAXX free billing; direct authenticated chat/completions probe returned served model deepseek-v4.1-flash-free and usage cost 0. No paid fallback.",
        "checked_at":datetime.now(timezone.utc).isoformat()}
    started = time.monotonic()
    with Library(args.library) as library:
        queue = prepare_scale_goal(library, run_root, providers, host, TOOLS,
            product_id=args.product_id, target=args.target, goal=args.goal, build=build,
            limits=limits, persona_ids=persona_ids,
            credential_scopes={"local-router":"local OpenCodex provider configuration; no key material exposed"},
            reviewed=True, tool_provenance="owned_browser",
            billing_reviews={"local-router":billing_review},
            provider_destinations={"local-router":BASE_URL})
    plan_preview = preview(queue)
    atomic(run_root / "preview.json", canonical(plan_preview))
    approval = queue.authorize(plan_sha256=queue.plan_sha256,
        actor="user-approved-chat-instruction",
        consent_reference="2026-11-13 user instruction: use only free TOKENMAXX DeepSeek for Peekly 4/16/32 sessions; isolated local browser journeys; zero paid fallback; report actual usage.",
        budget_microusd=limits.budget_microusd,
        expires_at=time.time()+3600)
    queue.control("resume")
    atomic(run_root / "approval.json", canonical({"approval_id":approval,"plan_sha256":queue.plan_sha256,
        "budget_microusd":limits.budget_microusd,"expires_in_seconds":3600}))
    try:
        report = await execute_scale(run_root, providers, host, reviewed=True, max_idle_seconds=30)
    finally:
        stopped = await host.shutdown()
    if not stopped:
        raise RuntimeError("browser_shutdown_unconfirmed")
    atomic(run_root / "model-router-ledger.json", canonical(router.report()))
    atomic(run_root / "report.json", canonical(report))
    usage = report.get("provider_usage", [])
    route_stats = router.report()["routes"]
    route_stats = {model: dict(stats, failure_rate=((stats["failures"]+stats["quality_rejections"]) / stats["attempts"] if stats["attempts"] else 0.0))
                   for model, stats in route_stats.items()}
    events = [event for event in router.report()["events"]
              if event.get("status") != "quality_rejected"]
    completed = sum(bool((task.get("result") or {}).get("operational_completed"))
                    for task in report.get("tasks", []))
    validation = report.get("evidence_validation", {})
    ready = (completed == len(persona_ids) and report["counts"]["complete"] == len(persona_ids)
        and validation.get("current_valid_sessions") == len(persona_ids)
        and not any(report["counts"][key] for key in ("queued", "running", "uncertain", "blocked", "cancelled")))
    summary = {
        "stage_cumulative_sessions":index,"sessions":len(persona_ids),"persona_ids":persona_ids,
        "counts":report["counts"],"elapsed_seconds":round(time.monotonic()-started,3),
        "actual_model_calls":report["actual_model_calls"],"actual_browser_tool_calls":sum(
            op["kind"]=="tool" and op["state"]=="done" for op in report["operations"]),
        "provider_usage":usage,"budget":report["budget"],
        "fallback_model_attempts":0,
        "model_attempts":route_stats,"configured_routes":configured_routes,
        "fixture_manifest_sha256":byte_digest(read_bytes(args.fixtures / "fixture-manifest.json")),
        "browser_shutdown_confirmed":stopped,
        "current_evidence_validation":report.get("evidence_validation"),
        "operational_completed_sessions":completed,
        "stage_ready_for_expansion":ready,
        "input_tokens_all_attempts":sum(row["input_tokens"] for row in route_stats.values()),
        "output_tokens_all_attempts":sum(row["output_tokens"] for row in route_stats.values()),
        "cost_record":{"authorized_route":"user_confirmed_free_TOKENMAXX",
            "policy_cost_usd":0,
            "provider_reported_cost_values":[event.get("provider_reported_cost") for event in events],
            "billing_source_values":[event.get("billing_source") for event in events],
            "missing_cost_responses":sum(event.get("provider_reported_cost") is None for event in events),
            "provider_invoice_verified":False},
        "real_user_evidence":False,"product_ready":False,
    }
    atomic(run_root / "stage-summary.json", canonical(summary))
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    return summary


async def main(args):
    args.library = safe_path(args.library)
    args.run_root = safe_path(args.run_root)
    args.build_artifact = safe_path(args.build_artifact)
    args.fixtures = safe_path(args.fixtures)
    if not args.library.is_dir() or not args.build_artifact.is_file() or not args.fixtures.is_dir():
        raise RuntimeError("library_build_or_fixture_artifact_missing")
    fixture_manifest = json.loads((args.fixtures / "fixture-manifest.json").read_text())
    if fixture_manifest.get("schema_version") != "peekly-synthetic-fixtures.v1" or not fixture_manifest.get("files"):
        raise RuntimeError("peekly_fixture_manifest_invalid")
    if args.run_root.exists():
        raise RuntimeError("run_root_exists_preserved")
    args.run_root.mkdir(parents=True,mode=0o700)
    if args.start_index < 0 or args.start_index >= 32:
        raise RuntimeError("persona_start_index_out_of_range")
    all_ids = _load_personas(args.library,args.product_id,max(args.stages))
    cursor=args.start_index; stages=[]
    for count in args.stages:
        ids=all_ids[cursor:count]; cursor=count
        summary=await run_stage(args,ids,count)
        stages.append(summary)
        atomic(args.run_root / "stages.json", canonical({"stages":stages,
            "total_sessions":sum(x["sessions"] for x in stages),
            "actual_model_calls":sum(x["actual_model_calls"] for x in stages),
            "real_user_evidence":False,"product_ready":False}))
        if not summary["stage_ready_for_expansion"]:
            raise RuntimeError("stage_incomplete_preserved:"+str(count))


def parse_args():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--library",required=True,type=Path)
    p.add_argument("--product-id",required=True)
    p.add_argument("--url",required=True,help="Running owned product app on localhost/127.0.0.1")
    p.add_argument("--target",required=True)
    p.add_argument("--goal",required=True)
    p.add_argument("--build-id",required=True)
    p.add_argument("--build-artifact",required=True,type=Path)
    p.add_argument("--fixtures",required=True,type=Path)
    p.add_argument("--run-root",required=True,type=Path)
    p.add_argument("--node",type=Path,default=Path(NODE_DEFAULT))
    p.add_argument("--chrome",type=Path,default=Path(CHROME_DEFAULT))
    p.add_argument("--stages",type=int,nargs="+",default=[4,16,32],
        help="cumulative persona indices to execute (e.g. 4 16 32)")
    p.add_argument("--start-index",type=int,default=0,
        help="zero-based first saved persona index; use to continue cumulative batches without replaying prior personas")
    p.add_argument("--turns", type=int, default=16, help="bounded model decisions per persona (4..24)")
    args=p.parse_args()
    if not 4 <= args.turns <= 24:
        p.error("turns must be from 4 to 24")
    if args.start_index < 0 or args.start_index >= 32:
        p.error("start-index must be between 0 and 31")
    if any(n<=args.start_index or n>32 for n in args.stages) or args.stages != sorted(set(args.stages)):
        p.error("cumulative stage endpoints must be strictly increasing values after start-index and at most 32")
    return args

if __name__=="__main__":
    try:
        asyncio.run(main(parse_args()))
    except Exception as exc:
        print(json.dumps({"result":"blocked","error_type":type(exc).__name__,
            "reason":str(exc)[:240]},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)
