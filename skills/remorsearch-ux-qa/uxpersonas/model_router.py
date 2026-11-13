"""OpenAI-compatible local gateway router with ordered model fallback and usage receipts."""
from __future__ import annotations
from dataclasses import dataclass
import json, os, tempfile, time, threading, urllib.error, urllib.request
@dataclass(frozen=True)
class ModelRoute:
    provider: str
    model: str
@dataclass
class RouteStats:
    attempts: int = 0
    successes: int = 0
    rate_limits: int = 0
    failures: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_seconds: float = 0.0
class ModelRouter:
    def __init__(self, base_url, routes, *, timeout=90, max_retries=2, backoff_initial=1.0, backoff_max=20.0, opener=None, sleep=time.sleep, ledger_path=None):
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
        self.lock = threading.RLock()
        self.stats = {r.model: RouteStats() for r in routes}
        self.events = []
    def _request(self, route, messages, max_tokens, temperature):
        body = json.dumps({"model": route.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature, "stream": False}, ensure_ascii=False).encode()
        req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json", "Accept": "application/json"}, method="POST")
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
            choices = data.get("choices")
            if not isinstance(choices, list) or len(choices) != 1: raise ValueError("choices_invalid")
            content = (choices[0].get("message") or {}).get("content")
            if not isinstance(content, str) or not content.strip(): raise ValueError("content_missing")
            elapsed = time.monotonic() - started
            stat = self.stats[route.model]
            with self.lock:
                stat.successes += 1; stat.input_tokens += prompt; stat.output_tokens += completion; stat.elapsed_seconds += elapsed
            receipt = {"provider": route.provider, "requested_model": route.model, "served_model": data.get("model"), "response_id": data.get("id"), "input_tokens": prompt, "output_tokens": completion, "elapsed_seconds": round(elapsed, 4), "status": "success"}
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
            try: retry_after = max(0.0, min(self.backoff_max, float(exc.headers.get("Retry-After", "0"))))
            except (TypeError, ValueError, AttributeError): pass
            receipt = {"provider": route.provider, "requested_model": route.model, "status": "http_error",
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
            receipt = {"provider": route.provider, "requested_model": route.model,
                "status": "transport_or_protocol_error", "error_type": type(exc).__name__,
                "input_tokens": prompt, "output_tokens": completion,
                "elapsed_seconds": round(time.monotonic() - started, 4)}
            with self.lock: self.events.append(receipt); self._persist()
            return None, receipt
    def complete(self, messages, *, max_tokens=512, temperature=0.1, quality_check=None):
        errors = []
        for route in self.routes:
            for attempt in range(self.max_retries + 1):
                with self.lock: self.stats[route.model].attempts += 1
                content, receipt = self._request(route, messages, max_tokens, temperature)
                if content is not None:
                    try: accepted = quality_check is None or quality_check(content)
                    except Exception: accepted = False
                    if accepted: return content, receipt
                    with self.lock:
                        self.events.append(dict(receipt, status="quality_rejected")); self._persist()
                    errors.append({"model": route.model, "reason": "quality_rejected"}); break
                errors.append(receipt)
                retryable = receipt.get("http_status") in (408, 429, 500, 502, 503, 504) or receipt.get("status") == "transport_or_protocol_error"
                if not retryable or attempt >= self.max_retries: break
                delay = receipt.get("retry_after") or min(self.backoff_max, self.backoff_initial * (2 ** attempt))
                self.sleep(min(self.backoff_max, max(0.0, delay)))
        raise RuntimeError("all_model_routes_failed:" + json.dumps(errors, ensure_ascii=False))
    def _persist(self):
        if self.ledger_path is not None:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self.ledger_path.write_text(json.dumps(self.report(), ensure_ascii=False, indent=2))

    def report(self):
        return {"routes": {model: vars(stats).copy() for model, stats in self.stats.items()}, "events": list(self.events), "fallback_order": [r.model for r in self.routes]}
