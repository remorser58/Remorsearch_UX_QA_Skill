"""OpenAI-compatible local gateway router with ordered model fallback and usage receipts."""
from __future__ import annotations
from dataclasses import dataclass
import json, os, time, threading, urllib.error, urllib.request
from decimal import Decimal, InvalidOperation, ROUND_CEILING
from email.utils import parsedate_to_datetime
from pathlib import Path
from hashlib import sha256
@dataclass(frozen=True)
class ModelRoute:
    provider: str
    model: str
    input_usd_per_million: str = "0"
    output_usd_per_million: str = "0"
    requests_per_minute: int = 30
    allowed_served_models: tuple = ()
@dataclass
class RouteStats:
    attempts: int = 0
    successes: int = 0
    rate_limits: int = 0
    failures: int = 0
    quality_rejections: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_seconds: float = 0.0
class ModelRouter:
    def __init__(self, base_url, routes, *, timeout=90, max_retries=2, backoff_initial=1.0, backoff_max=20.0, opener=None, sleep=time.sleep, ledger_path=None, respect_rpm=True):
        if not (base_url.startswith("http://127.0.0.1:") or base_url.startswith("http://localhost:")):
            raise ValueError("Only the local OpenCodex gateway is accepted.")
        if not routes or len({(r.provider, r.model) for r in routes}) != len(routes):
            raise ValueError("Routes must be nonempty and unique.")
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.routes = tuple(routes)
        self.timeout, self.max_retries = timeout, max_retries
        self.backoff_initial, self.backoff_max = backoff_initial, backoff_max
        self.opener, self.sleep = opener or urllib.request.urlopen, sleep
        self.ledger_path = ledger_path
        self.respect_rpm = bool(respect_rpm)
        self.lock = threading.RLock()
        self.stats = {r.model: RouteStats() for r in routes}
        self.events = []
        self.conversations = {}
        self.next_allowed = {r.model: 0.0 for r in routes}
        self.cooldown_until = {r.model: 0.0 for r in routes}
    def _throttle(self, route):
        if not self.respect_rpm:
            return
        interval = 60.0 / max(1, min(600, int(route.requests_per_minute)))
        with self.lock:
            now = time.monotonic()
            scheduled = max(self.next_allowed[route.model], self.cooldown_until[route.model])
            wait = max(0.0, scheduled - now)
            self.next_allowed[route.model] = max(now, scheduled) + interval
        if wait:
            self.sleep(wait)

    def _request(self, route, messages, max_tokens, temperature, call_id=None):
        body = json.dumps({"model": route.model, "messages": messages, "max_tokens": max_tokens,
            "temperature": temperature, "stream": False,
            "response_format": {"type": "json_object"}}, ensure_ascii=False).encode()
        # The Mac mini OpenCodex gateway authenticates with the existing
        # PROXY_API_KEY environment variable. Never print, persist or forward it
        # anywhere except this explicitly loopback-only gateway.
        secret = os.environ.get("PROXY_API_KEY")
        if not isinstance(secret, str) or not secret or len(secret) > 4096 or any(ord(c) < 33 or ord(c) > 126 for c in secret):
            raise RuntimeError("local_opencodex_auth_unavailable")
        req = urllib.request.Request(self.url, data=body, headers={
            "Content-Type": "application/json", "Accept": "application/json",
            "Authorization": "Bearer " + secret
        }, method="POST")
        started = time.monotonic()
        prompt = completion = None
        try:
            with self.opener(req, timeout=self.timeout) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
                if len(raw) > 2 * 1024 * 1024: raise ValueError("response_too_large")
                data = json.loads(raw)
                if response.status != 200: raise urllib.error.HTTPError(self.url, response.status, "gateway_error", response.headers, None)
            usage = data.get("usage") or {}
            prompt = usage.get("prompt_tokens", usage.get("input_tokens"))
            completion = usage.get("completion_tokens", usage.get("output_tokens"))
            if type(prompt) is not int or type(completion) is not int or prompt < 0 or completion < 0: raise ValueError("usage_missing_or_invalid")
            served_model = data.get("model")
            if route.provider == "TOKENMAXX" and route.model == "TOKENMAXX/deepseek-v4.1-flash-free":
                # TOKENMAXX documents two upstream served-name spellings for this
                # exact free selector. The requested selector/provider remain the
                # authority; never widen this exception to flash-1m or another route.
                allowed = set(route.allowed_served_models) | {
                    "TOKENMAXX/deepseek-v4.1-flash-free",
                    "deepseek-v4.1-flash-free",
                    "deepseek-v4.1-flash",
                }
            else:
                allowed = set(route.allowed_served_models)
            if allowed and served_model not in allowed:
                elapsed = time.monotonic() - started
                stat = self.stats[route.model]
                with self.lock:
                    stat.failures += 1; stat.input_tokens += prompt; stat.output_tokens += completion; stat.elapsed_seconds += elapsed
                receipt = {"call_id":call_id,"provider":route.provider,"requested_model":route.model,
                    "served_model":served_model,"response_id":data.get("id"),"input_tokens":prompt,
                    "output_tokens":completion,"provider_cost_microusd":None,"cost_basis":"unknown",
                    "elapsed_seconds":round(elapsed,4),"status":"served_model_mismatch"}
                with self.lock:
                    self.events.append(receipt); self._persist()
                return None, receipt
            choices = data.get("choices")
            if not isinstance(choices, list) or not choices or len(choices) > 4: raise ValueError("choices_invalid")
            content = (choices[0].get("message") or {}).get("content")
            if not isinstance(content, str) or not content.strip(): raise ValueError("content_missing")
            elapsed = time.monotonic() - started
            stat = self.stats[route.model]
            with self.lock:
                stat.successes += 1; stat.input_tokens += prompt; stat.output_tokens += completion; stat.elapsed_seconds += elapsed
            reported_cost = usage.get("cost")
            billing_source = usage.get("billing_source")
            cost_basis = "provider_reported" if reported_cost is not None else "provider_cost_not_reported"
            try:
                if reported_cost is not None:
                    cost = Decimal(str(reported_cost))
                    if not cost.is_finite() or cost < 0: raise InvalidOperation()
                    cost_microusd = int((cost * Decimal(1000000)).to_integral_value(rounding=ROUND_CEILING))
                else:
                    cost_microusd = None
            except (InvalidOperation, ValueError, TypeError, OverflowError):
                cost_microusd, cost_basis = None, "unknown"
            receipt = {"call_id": call_id, "provider": route.provider, "requested_model": route.model,
                "served_model": data.get("model"), "response_id": data.get("id"),
                "input_tokens": prompt, "output_tokens": completion,
                "provider_cost_microusd": cost_microusd, "provider_reported_cost": reported_cost,
                "billing_source": billing_source, "cost_basis": cost_basis,
                "elapsed_seconds": round(elapsed, 4), "status": "success"}
            with self.lock:
                self.events.append(receipt)
                self._persist()
            return content, receipt
        except urllib.error.HTTPError as exc:
            stat = self.stats[route.model]
            with self.lock:
                stat.failures += 1
                if exc.code == 429: stat.rate_limits += 1
                if type(prompt) is int and type(completion) is int:
                    stat.input_tokens += prompt; stat.output_tokens += completion
            retry_after = 0.0
            try:
                raw_retry = exc.headers.get("Retry-After", "0")
                try: retry_after = float(raw_retry)
                except (TypeError, ValueError):
                    retry_after = max(0.0, (parsedate_to_datetime(raw_retry).timestamp() - time.time()))
                retry_after = max(0.0, min(86400.0, retry_after))
            except (TypeError, ValueError, AttributeError, OverflowError): pass
            if exc.code == 429:
                with self.lock:
                    self.cooldown_until[route.model] = max(self.cooldown_until[route.model],
                        time.monotonic() + max(retry_after, self.backoff_initial))
            receipt = {"call_id": call_id, "provider": route.provider, "requested_model": route.model, "status": "http_error",
                "http_status": exc.code, "retry_after": retry_after,
                "input_tokens": prompt, "output_tokens": completion,
                "elapsed_seconds": round(time.monotonic() - started, 4)}
            with self.lock: self.events.append(receipt); self._persist()
            return None, receipt
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            stat = self.stats[route.model]
            with self.lock:
                stat.failures += 1
                if type(prompt) is int and type(completion) is int:
                    stat.input_tokens += prompt; stat.output_tokens += completion
            receipt = {"call_id": call_id, "provider": route.provider, "requested_model": route.model,
                "status": "transport_or_protocol_error", "error_type": type(exc).__name__, "error_reason": str(exc)[:120],
                "input_tokens": prompt, "output_tokens": completion,
                "elapsed_seconds": round(time.monotonic() - started, 4)}
            with self.lock: self.events.append(receipt); self._persist()
            return None, receipt
    def complete(self, messages, *, max_tokens=512, temperature=0.1, quality_check=None, call_id=None):
        errors = []
        for route in self.routes:
            for attempt in range(self.max_retries + 1):
                with self.lock: self.stats[route.model].attempts += 1
                self._throttle(route)
                content, receipt = self._request(route, messages, max_tokens, temperature, call_id)
                if content is not None:
                    try: accepted = True if quality_check is None else quality_check(content)
                    except Exception as exc: accepted = "quality_check_error:" + type(exc).__name__
                    if accepted is True: return content, receipt
                    reason = accepted if isinstance(accepted, str) else "quality_rejected"
                    from . import swarm
                    excerpt = swarm.clean(content)[:240]
                    with self.lock:
                        self.stats[route.model].quality_rejections += 1
                        self.events.append(dict(receipt, status="quality_rejected", quality_reason=reason,
                            response_excerpt=excerpt)); self._persist()
                    errors.append({"model": route.model, "reason": reason}); break
                errors.append(receipt)
                retryable = receipt.get("http_status") in (408, 429, 500, 502, 503, 504) or receipt.get("status") == "transport_or_protocol_error"
                if not retryable or attempt >= self.max_retries: break
                if receipt.get("http_status") == 429:
                    if not self.respect_rpm:
                        self.sleep(max(receipt.get("retry_after", 0.0), self.backoff_initial))
                    continue  # _throttle observes the shared provider cooldown before the retry.
                delay = min(self.backoff_max, self.backoff_initial * (2 ** attempt))
                self.sleep(max(0.0, delay))
        raise RuntimeError("all_model_routes_failed:" + json.dumps(errors, ensure_ascii=False))
    def _persist(self):
        if self.ledger_path is not None:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.ledger_path.with_name(self.ledger_path.name + ".tmp")
            tmp.write_text(json.dumps(self.report(), ensure_ascii=False, indent=2))
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.ledger_path)

    def report(self):
        with self.lock:
            return {"routes": {model: vars(stats).copy() for model, stats in self.stats.items()},
                    "events": list(self.events), "fallback_order": [r.model for r in self.routes]}


class RoutedScaleProvider:
    """ScaleExecution provider adapter over the local OpenCodex model router."""
    mode = "live"

    def __init__(self, spec, router):
        self.spec, self.router = spec, router
        self.lock = threading.RLock()
        self.conversations = {}
        self.adapter_sha256 = sha256(Path(__file__).read_bytes() + json.dumps(
            [vars(r) for r in router.routes], sort_keys=True).encode()).hexdigest()

    async def call(self, request):
        import asyncio
        from uxresearch.canonical import digest
        payload = request["payload"]
        system = ("You are one independent synthetic research persona executing one real browser UX journey. "
            "OUTPUT CONTRACT: respond with exactly one valid JSON object and absolutely no prose, preamble, markdown or code fence. "
            "For an action use {\"kind\":\"tool\",\"tool\":\"observe\",\"arguments\":{},\"decision\":\"reason\"}. "
            "For completion use {\"kind\":\"final\",\"judgment\":{...}}. "
            "Use only your persona, current browser observations and approved tool allowlist. "
            "Do not invent actions or observations. Never claim real-user evidence. Preserve failures.")
        context_id = request["context_id"]
        with self.lock:
            messages = list(self.conversations.get(context_id, [{"role":"system","content":system}]))
        messages.append({"role":"user","content":json.dumps(payload,ensure_ascii=False,separators=(",",":"))})
        def parse_decision(content):
            if not isinstance(content, str):
                raise ValueError("decision_not_text")
            text=content.strip()
            if text.startswith("```"):
                lines=text.splitlines()
                if len(lines)>=3 and lines[0].startswith("```") and lines[-1].strip()=="```":
                    text="\n".join(lines[1:-1]).strip()
            value=json.loads(text)
            if not isinstance(value,dict):
                raise ValueError("decision_not_object")
            if value.get("kind")=="tool":
                if set(value)!={"kind","tool","arguments","decision"} or not isinstance(value["arguments"],dict):
                    raise ValueError("tool_decision_schema")
            elif value.get("kind")=="final":
                if set(value)!={"kind","judgment"} or not isinstance(value["judgment"],dict):
                    raise ValueError("final_decision_schema")
            else:
                raise ValueError("decision_kind_invalid")
            return value
        def valid(content):
            try:
                parse_decision(content)
                return True
            except (ValueError,TypeError) as exc:
                return "decision_parse:" + type(exc).__name__ + ":" + str(exc)[:100]
        content, receipt = await asyncio.to_thread(self.router.complete, messages, max_tokens=1536, temperature=0.0, quality_check=valid, call_id=request["operation_id"])
        result=parse_decision(content)
        from . import swarm
        result=swarm.clean(result)
        with self.lock:
            self.conversations[context_id] = messages + [{"role":"assistant","content":content}]
        attempts = [event for event in self.router.report()["events"] if event.get("call_id") == request["operation_id"]]
        unique = {}
        for event in attempts:
            if event.get("response_id"):
                unique[event["response_id"]] = event
            elif event.get("input_tokens") is not None or event.get("output_tokens") is not None:
                unique["error-"+str(len(unique))+"-"+str(event.get("requested_model"))] = event
        usage_rows = list(unique.values())
        input_tokens = sum(event.get("input_tokens") or 0 for event in usage_rows)
        output_tokens = sum(event.get("output_tokens") or 0 for event in usage_rows)
        costs = [event.get("provider_cost_microusd") for event in usage_rows]
        total_cost = sum(costs) if costs and all(type(value) is int for value in costs) else None
        providers = sorted({event["provider"] for event in usage_rows if event.get("provider")})
        models = sorted({event.get("served_model") or event.get("requested_model") for event in usage_rows if event.get("served_model") or event.get("requested_model")})
        bases = {event.get("cost_basis") for event in usage_rows}
        basis = ("aggregated_provider_reported" if bases == {"provider_reported"} else
                 "aggregated_rate_estimate" if bases <= {"provider_reported", "configured_rate_estimate"} and total_cost is not None else
                 "reviewed_rate_fallback")
        usage={"input_tokens":input_tokens,"output_tokens":output_tokens,
               "provider":"+".join(providers) or receipt["provider"],"model":"+".join(models) or (receipt["served_model"] or receipt["requested_model"]),
               "provider_cost_microusd":total_cost,
               "cost_basis":basis}
        return {key:request[key] for key in ("operation_id","context_id","request_sha256")} | {
            "trace_id":receipt.get("response_id") or digest([request["operation_id"],receipt]),
            "result":result,"usage":usage}
