"""The reader ladder for one public URL, and `ingest` for render captures.

Rungs, cheapest and most honest first. Each runs at most once per URL:

  R0 official_route  the route table's feeds or oEmbed for this host
                     (data/routes.json); at most 2 requests. An unverified route
                     that fails, for example with a 404, falls through.
  R1 honest_ua       one GET with the identifying User-Agent and the brief's
                     Accept-Language. No Referer, no cookies.
  R2 site_alternate  the page's own declared mobile, AMP or feed alternate on the
                     same registrable domain, then the route table's twins, then a
                     generic www.-to-m. rewrite only if that name resolves; at most
                     2 requests. A JSON-LD body is used on any rung when it is
                     longer than the visible text.
  R3 real_browser    an unmodified browser render in an anonymous context. In this
                     version the researcher's own browser renders the page and the
                     capture is handed in with `ingest`; `read` exits 4 and says how.
                     A community the brief authorises may be captured signed in.

Before any rung, the page's own URL is checked against the deny list, the route
table's out-of-scope private channels and its own robots.txt; a disallowed path
stops there, so no official route or alternate is read for it. Escalation
happens only on js_shell, js_check, bot_filter or suspect. Any stop class ends
the URL. The whole host stops for the run on a human check backed by a widget or
a challenge status, on any human check in a render capture, on a second
rate-limit signal, and after three URLs in a row that no allowed rung could read
(a URL still waiting for its render does not count). robots.txt that cannot be
fetched (5xx, 429, network failure) disallows everything for now: the URL is
deferred until it is checked again. Every request, redirect hop, official route
and alternate goes through the same checks as a new URL: deny list,
out-of-scope channels, robots.txt. Redirects are followed only within one origin
and only to paths robots.txt allows; a redirect to a login page is an auth_gate
stop.
"""
from __future__ import annotations

import functools
import hashlib
import ipaddress
import json
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlsplit

from . import ROBOTS_TOKEN, USER_AGENT, extract, net, privacy, robots, verdict
from .envelope import scan as scan_injection
from .ledger import ROBOTS_RETRY_S, BudgetExceeded, Deferred, HostStopped, Run

DATA = Path(__file__).resolve().parent / "data"
PRESENTATION = {"R0": "official_route", "R1": "honest_ua", "R2": "site_alternate", "R3": "real_browser"}
RUNGS = tuple(PRESENTATION)
R0_MAX_REQUESTS = 2
R2_MAX_REQUESTS = 2
EXIT = {"read": 0, "refused": 2, "stopped": 3, "unread": 4, "deferred": 5}
TRANSIENT_RETRY_S = 120
INGEST_MAX_BYTES = 8 * 1024 * 1024
PAGE_ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
FEED_ACCEPT = "application/rss+xml,application/atom+xml,application/xml;q=0.9,text/xml;q=0.9,*/*;q=0.5"
JSON_ACCEPT = "application/json;q=1.0,*/*;q=0.5"
ROBOTS_ACCEPT = "text/plain,*/*;q=0.5"
HTML_TYPES = frozenset({"text/html", "application/xhtml+xml"})
FEED_TYPES = frozenset({"application/rss+xml", "application/atom+xml", "application/xml", "text/xml"})
INGEST_HELP = ("Render it yourself: open the URL in a private or signed-out browser window (a signed-in session "
               "only for a community the brief authorises), let a self-clearing check finish (at most 15 s), scroll "
               "only (no typing, no clicks), save the page as HTML or copy its text, then run: ux_research.py ingest "
               "--run RUN --url URL --file FILE --context anonymous")
AUTHORISED_NOTE = ("member content from an authorised community: shared outputs keep authored summaries only "
                   "(no quotes, no post URLs, no member's personal data)")
ROBOTS_UNREACHABLE = ("robots.txt could not be fetched (5xx, 429 or a network failure), so nothing may be read "
                      "there until it is checked again")
CONTEXTS = ("anonymous", "unknown", "signed_in")


# ---------------------------------------------------------------- site data


@functools.lru_cache(maxsize=1)
def _suffix_data() -> dict:
    return json.loads((DATA / "suffixes.json").read_text(encoding="utf-8"))


def registrable_domain(host: str) -> str:
    """The registrable domain, honouring multi-label and hosting suffixes (data/suffixes.json)."""
    host = host.lower().rstrip(".")
    try:
        ipaddress.ip_address(host.strip("[]"))
        return host
    except ValueError:
        pass
    data = _suffix_data()
    suffixes = set(data["public_suffixes"]) | set(data["hosting_suffixes"])
    labels = host.split(".")
    for i in range(1, len(labels)):
        if ".".join(labels[i:]) in suffixes:
            return ".".join(labels[i - 1:])
    return ".".join(labels[-2:])


_TEMPLATE_VAR = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def expand(template: str, values: dict) -> str | None:
    missing: list[str] = []

    def replace(match: re.Match) -> str:
        if match.group(1) not in values:
            missing.append(match.group(1))
            return ""
        return str(values[match.group(1)])

    result = _TEMPLATE_VAR.sub(replace, template)
    return None if missing else result


def _variables(url: str, groups: dict) -> dict:
    parts = urlsplit(url)
    host = parts.hostname or ""
    values = {"scheme": parts.scheme, "host": host, "port_suffix": f":{parts.port}" if parts.port else "",
              "path": parts.path or "/", "query": parts.query, "url_enc": quote(url, safe=""),
              "registrable": registrable_domain(host)}
    values.update(groups)
    for name, value in parse_qsl(parts.query):
        if re.fullmatch(r"[A-Za-z0-9_]{1,40}", name):
            values.setdefault(f"q_{name}", quote(value, safe=""))
    return values


class Routes:
    def __init__(self, data: dict):
        self.platforms = [p for p in data.get("platforms", []) if isinstance(p, dict)]
        self.excluded_hosts = [o for o in data.get("out_of_scope", []) if isinstance(o, dict)]
        self.login_hosts = sorted({h for p in self.platforms for h in p.get("login_hosts", []) if h})

    def match(self, url: str) -> tuple[dict | None, dict]:
        parts = urlsplit(url)
        for platform in self.platforms:
            if not verdict.host_matches(parts.hostname or "", platform.get("hosts", [])):
                continue
            groups: dict = {}
            if platform.get("path"):
                found = re.match(platform["path"], parts.path or "/")
                if not found:
                    continue
                groups = {k: v for k, v in found.groupdict().items() if v is not None}
            return platform, _variables(url, groups)
        return None, {}

    def excluded(self, url: str) -> str | None:
        parts = urlsplit(url)
        for item in self.excluded_hosts:
            prefix = item.get("path_prefix") or "/"
            if verdict.host_matches(parts.hostname or "", [item.get("host", "")]) and \
                    (parts.path or "/").startswith(prefix):
                return item.get("reason", "out of scope")
        return None


# ---------------------------------------------------------------- one request


@dataclass
class _Read:
    run: Run
    url: str
    expect: tuple
    max_wait: float
    routes: Routes
    trail: list = field(default_factory=list)
    contacted: bool = False
    target_robots: dict | None = None


@dataclass
class _Attempt:
    url: str
    rung: str
    purpose: str
    response: net.Response | None = None
    fetch_id: str | None = None
    error: str | None = None
    error_detail: str = ""
    stop: str | None = None
    reasons: list = field(default_factory=list)
    contacted: bool = False
    chain: list = field(default_factory=list)
    robots: dict | None = None
    waited_s: float = 0.0
    retry_after_s: int | None = None
    scope: bool = False  # stopped by the deny list or an out-of-scope channel, before any request
    out_of_scope: bool = False


def _headers(run: Run, accept: str) -> dict:
    return {"User-Agent": USER_AGENT, "Accept": accept, "Accept-Language": run.policy["accept_language"]}


def _looks_html(response: net.Response) -> bool:
    if response.content_type in HTML_TYPES:
        return True
    if response.content_type in ("", "text/plain", "application/octet-stream"):
        head = response.body[:1024].lstrip().lower()
        return head.startswith((b"<!doctype html", b"<html")) or b"<body" in head
    return False


def _robots_brief(decision: dict | None) -> dict | None:
    if not decision:
        return None
    return {k: decision.get(k) for k in ("allowed", "decision", "robots_status", "http_status", "group", "rule",
                                         "sha256", "crawl_delay")}


def scope_stop(run: Run, routes: Routes, url: str) -> tuple[str, list, bool] | None:
    """(stop class, reasons, out of scope) when the researcher's deny list or the route table's
    private channels exclude this URL. Checked before any robots.txt, slot or request."""
    if verdict.host_matches(net.host_of(url), run.policy.get("deny_hosts", [])):
        return "opted_out", ["deny_hosts"], False
    excluded = routes.excluded(url)
    if excluded:
        return "auth_gate", [f"private_channel:{excluded}"], True
    return None


def robots_decision(run: Run, url: str, max_wait: float) -> dict:
    """Fetch robots.txt for the URL's origin once per run (paced, not charged) and decide."""
    origin = net.origin_of(url)
    record = run.robots_record(origin)
    if record is None:
        host = net.host_of(url)
        slot = run.acquire(host, "policy", max_wait)
        fetch_id = run.new_fetch_id()
        response, failure = None, None
        entry = {"kind": "request", "purpose": "robots", "fetch_id": fetch_id, "url": origin + "/robots.txt",
                 "host": host, "waited_s": round(slot.waited, 3)}
        try:
            try:
                response = net.fetch(origin + "/robots.txt", headers=_headers(run, ROBOTS_ACCEPT),
                                     max_wire=robots.PARSE_LIMIT_BYTES, max_decoded=robots.PARSE_LIMIT_BYTES,
                                     truncate=True)
            except net.NetError as exc:
                failure = exc
            if failure is not None and (failure.kind in net.REFUSAL_KINDS or failure.kind in ("dns_error", "tls_error")):
                run.log({**entry, "error": failure.kind})
                raise failure
            challenge = False
            parsed = response is not None and 200 <= response.status < 300 and \
                robots.looks_like_robots(response.body[:robots.PARSE_LIMIT_BYTES].decode("utf-8", "replace"))
            if response is not None and not parsed and _looks_html(response):
                # Only a body with no robots.txt lines can be a challenge page: words in a real file's
                # comments never override its rules.
                challenge = verdict.robots_challenge(response.status,
                                                     extract.from_html(response.text()[0], response.final_url))
            record = robots.record_from_fetch(origin, status=response.status if response else None,
                                              body=response.body if response else b"",
                                              error=failure.kind if failure else None, challenge=challenge,
                                              token=ROBOTS_TOKEN, fetched_at=run.now_iso())
            run.store_robots(origin, host, record)  # before release, so a Crawl-delay paces the next request
        finally:
            run.release(slot)
        if response is not None:
            entry.update(status=response.status, wire_bytes=response.wire_bytes, elapsed_ms=response.elapsed_ms,
                         redirects=response.redirects, via_proxy=response.via_proxy, precheck=response.precheck,
                         test_override=response.test_override)
        run.log({**entry, "error": failure.kind if failure else None, "robots_status": record["status"],
                 "sha256": record["sha256"], "crawl_delay": record["crawl_delay"]})
    decision = {"origin": origin, **robots.decide(record, url)}
    if decision["robots_status"] == "unreachable":  # disallowed for now; checked again after ROBOTS_RETRY_S
        stored = float(record.get("stored_at") or run.clock())
        decision["retry_after_s"] = max(1, int(math.ceil(ROBOTS_RETRY_S - (run.clock() - stored))))
    return decision


def _robots_reasons(decision: dict) -> list:
    rule = decision.get("rule") or {}
    return [f"robots.txt:{rule.get('type', 'disallow')} {rule.get('pattern', '')}".strip(),
            f"robots_status:{decision['robots_status']}"]


def _request(st: _Read, url: str, rung: str, *, accept: str = PAGE_ACCEPT, purpose: str = "page") -> _Attempt:
    """Deny list and out-of-scope check, robots.txt, a paced slot, one GET; same-origin redirects
    only; login redirects stop. Every hop gets the same checks as a new URL."""
    run = st.run
    attempt = _Attempt(url=url, rung=rung, purpose=purpose)
    requested_login = verdict.is_login_url(url, st.routes.login_hosts)
    current = url
    hops = 0
    while True:
        parts = urlsplit(current)
        excluded = scope_stop(run, st.routes, current)  # before any slot, robots.txt or request
        if excluded:
            attempt.stop, attempt.reasons, attempt.out_of_scope = excluded
            attempt.scope = True
            return attempt
        try:
            net.check_host(parts.hostname or "", parts.port or (443 if parts.scheme == "https" else 80))
        except net.NetError as exc:
            if exc.kind in net.REFUSAL_KINDS:
                raise
        decision = robots_decision(run, current, st.max_wait)
        attempt.robots = decision
        if not decision["allowed"]:
            if decision["robots_status"] == "unreachable":
                attempt.error, attempt.error_detail = "robots_unreachable", ROBOTS_UNREACHABLE
                attempt.retry_after_s = decision.get("retry_after_s")
                return attempt
            attempt.stop, attempt.reasons = "opted_out", _robots_reasons(decision)
            return attempt
        host = net.host_of(current)
        origin = net.origin_of(current)
        slot = run.acquire(host, "doc", st.max_wait)
        attempt.waited_s += slot.waited
        fetch_id = run.new_fetch_id()

        def follow(source: str, target: str, origin: str = origin) -> bool:
            if net.origin_of(target) != origin or verdict.is_legal_block_url(target):
                return False
            if scope_stop(run, st.routes, target):
                return False
            if not requested_login and verdict.is_login_url(target, st.routes.login_hosts):
                return False
            record = run.robots_record(origin)
            return record is not None and robots.decide(record, target)["allowed"]

        entry = {"kind": "request", "purpose": purpose, "fetch_id": fetch_id, "rung": rung,
                 "presentation": PRESENTATION[rung], "url": current, "host": host}
        try:  # the slot is released whatever happens, so a failure never leaves the host leased
            response = net.fetch(current, headers=_headers(run, accept),
                                 max_redirects=max(0, net.MAX_REDIRECTS - hops), on_redirect=follow)
        except net.NetError as exc:
            attempt.error, attempt.error_detail = exc.kind, exc.detail
            attempt.chain.extend(exc.redirects)
            attempt.contacted = attempt.contacted or exc.kind in ("too_large", "redirect_loop", "protocol_error",
                                                                  "decode_error", "unsupported_encoding")
            st.contacted = st.contacted or attempt.contacted
            run.log({**entry, "error": exc.kind, "redirects": exc.redirects, "waited_s": round(slot.waited, 3)})
            return attempt
        finally:
            run.release(slot)
        attempt.contacted = st.contacted = True
        attempt.chain.extend(response.redirects)
        hops += len(response.redirects)
        if response.location is None:
            attempt.response, attempt.fetch_id = response, fetch_id
            return attempt
        run.log({**entry, "status": response.status, "location": response.location, "redirects": response.redirects,
                 "wire_bytes": response.wire_bytes, "elapsed_ms": response.elapsed_ms,
                 "waited_s": round(slot.waited, 3), "test_override": response.test_override,
                 "precheck": response.precheck})
        if not requested_login and verdict.is_login_url(response.location, st.routes.login_hosts):
            attempt.stop, attempt.reasons = "auth_gate", ["redirect:login_page"]
            return attempt
        if verdict.is_legal_block_url(response.location):
            attempt.stop, attempt.reasons = "legal_block", ["redirect:legal_block_host"]
            return attempt
        current = response.location  # another origin, or a same-origin path robots.txt disallows


def _log_attempt(run: Run, attempt: _Attempt, v: verdict.Verdict | None = None, page=None) -> None:
    response = attempt.response
    entry = {"kind": "request", "purpose": attempt.purpose, "fetch_id": attempt.fetch_id, "rung": attempt.rung,
             "presentation": PRESENTATION[attempt.rung], "url": attempt.url, "final_url": response.final_url,
             "host": net.host_of(response.final_url), "status": response.status,
             "content_type": response.content_type, "wire_bytes": response.wire_bytes,
             "elapsed_ms": response.elapsed_ms, "waited_s": round(attempt.waited_s, 3),
             "redirects": response.redirects, "via_proxy": response.via_proxy, "precheck": response.precheck,
             "test_override": response.test_override, "truncated": response.truncated,
             "robots": _robots_brief(attempt.robots)}
    if v is not None:
        entry.update(verdict=v.verdict, stop_class=v.stop_class, transient=v.transient)
    if page is not None:
        entry.update(text_chars=len(page.text), extraction_source=page.extraction_source,
                     content_sha256=hashlib.sha256(page.text.encode("utf-8")).hexdigest())
    run.log(entry)


def _evaluate(st: _Read, attempt: _Attempt, *, requested: str, feed_target: str | None = None,
              feed_scope: str = "item"):
    response = attempt.response
    text, _ = response.text()
    page = None
    if _looks_html(response):
        page = extract.from_html(text, response.final_url)
    elif response.content_type in FEED_TYPES or text.lstrip()[:200].startswith(("<?xml", "<rss", "<feed")):
        page = extract.from_feed(text, feed_target or response.final_url, feed_scope if feed_target else "all")
    elif response.content_type.startswith("text/"):
        page = extract.from_text(text)
    optouts = robots.page_optouts(response.headers, page.meta_robots if page else [],
                                  page.tdm_meta if page else None, ROBOTS_TOKEN, response.x_robots)
    v = verdict.classify(status=response.status, headers=response.headers, page=page, requested_url=requested,
                         final_url=response.final_url, redirect_urls=[r["to"] for r in attempt.chain],
                         expect=st.expect, optouts=optouts, login_hosts=st.routes.login_hosts)
    _log_attempt(st.run, attempt, v, page)
    return page, v


def _trail(st: _Read, rung: str, outcome: str, *, url: str | None = None, attempt: _Attempt | None = None,
           v: verdict.Verdict | None = None, note: str | None = None) -> None:
    item = {"rung": rung, "presentation": PRESENTATION[rung], "outcome": outcome}
    if url:
        item["url"] = privacy.mask_url(url)
    if attempt is not None:
        if attempt.fetch_id:
            item["fetch_id"] = attempt.fetch_id
        if attempt.response is not None:
            item["status"] = attempt.response.status
        if attempt.error:
            item["error"] = attempt.error
        if attempt.stop:
            item["stop_class"] = attempt.stop
    if v is not None:
        item.update({k: val for k, val in (("verdict", v.verdict), ("stop_class", v.stop_class)) if val})
        item["reasons"] = v.reasons[:4]
    if note:
        item["note"] = note
    st.trail.append(item)


# ---------------------------------------------------------------- outcomes


def _remaining(st: _Read) -> tuple[list, list]:
    untried, notes = [], []
    render = st.run.policy.get("render", "host_browser")
    if render != "off":
        untried.append("R3")
        if render == "driver":
            notes.append("the render driver is not available in this version; use the host browser and ingest")
    else:
        notes.append("render disabled by the brief")
    return untried, notes


def _done(st: _Read, bucket: str, *, stop: str | None = None, verdict_: str | None = None, reasons=(),
          rung: str | None = None, attempt: _Attempt | None = None, page=None, untried=(), error: str | None = None,
          retry_after_s: int | None = None, host_stop: dict | None = None, next_step: str | None = None,
          notes=(), out_of_scope: bool = False, access_basis: str = "public_anonymous") -> dict:
    run = st.run
    host = net.host_of(st.url)
    response = attempt.response if attempt is not None else None
    # The source's robots record is its own page's decision, not a route or alternate host's, unless
    # another host's robots.txt is what stopped or deferred it.
    robots_source = st.target_robots
    if attempt is not None and attempt.robots and (robots_source is None or not attempt.robots.get("allowed")):
        robots_source = attempt.robots
    robots_info = _robots_brief(robots_source)
    result = {"source": "read", "bucket": bucket, "exit_code": EXIT[bucket], "url": privacy.mask_url(st.url),
              "final_url": privacy.mask_url(response.final_url) if response else None, "host": host,
              "verdict": verdict_, "stop_class": stop, "reasons": list(reasons)[:10], "rung": rung,
              "presentation": PRESENTATION.get(rung) if rung else None,
              "fetch_id": attempt.fetch_id if attempt is not None else None, "trail": st.trail,
              "untried": list(untried), "error": error, "retry_after_s": retry_after_s, "host_stop": host_stop,
              "next_step": next_step, "notes": list(notes), "robots": robots_info, "fetched_at": run.now_iso(),
              "render": "needs_host_render" if "R3" in untried else None,
              "context": "anonymous", "access_basis": access_basis if bucket == "read" else None}
    if out_of_scope:
        result["out_of_scope"] = True
        result["notes"].append("a private channel: out of the research's scope, not a coverage gap")
    text = None
    if bucket == "read" and page is not None:
        text = page.text
        result.update(extraction_source=page.extraction_source, text_chars=len(text), truncated=page.truncated,
                      content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                      injection=scan_injection(text), promo_flags=verdict.promotion_flags(text),
                      meta=page.metadata())
        run.save_page(attempt.fetch_id, text)
    elif stop == "paywall" and page is not None:
        result["meta"] = page.metadata()
    # Only a URL with no allowed rung left counts toward bot_filter_persistent: a page that is waiting
    # for its render (R3 untried) has not been found unreadable yet.
    if bucket == "read" or (bucket == "unread" and not untried):
        streak = run.note_outcome(host, bucket)
        if streak:
            result["host_stop"] = streak
            result["notes"].append("this host is now stopped for the run: " + streak["reason"])
    run.log({"kind": "outcome", "source": "read", "url": st.url, "url_key": run.url_key(st.url), "host": host,
             "fetched_at": result["fetched_at"], "context": "anonymous",
             "access_basis": result["access_basis"], "out_of_scope": out_of_scope or None,
             "robots": {"decision": (robots_info or {}).get("decision"), "status": (robots_info or {}).get("robots_status")},
             "bucket": bucket, "verdict": verdict_, "stop_class": stop, "rung": rung,
             "presentation": result["presentation"], "fetch_id": result["fetch_id"], "untried": result["untried"],
             "error": error, "retry_after_s": retry_after_s, "contacted": st.contacted,
             "reasons": result["reasons"][:6], "trail": st.trail, "text_chars": result.get("text_chars"),
             "content_sha256": result.get("content_sha256"), "extraction_source": result.get("extraction_source"),
             "injection_risk": (result.get("injection") or {}).get("risk"),
             "host_stop": (result["host_stop"] or {}).get("class")})
    result["text"] = text
    return result


def _refused(run: Run, url, kind: str, detail: str, st: _Read | None = None) -> dict:
    masked = privacy.mask_url(url) if isinstance(url, str) else ""
    host = net.host_of(url) if isinstance(url, str) else ""
    result = {"source": "read", "bucket": "refused", "exit_code": EXIT["refused"], "url": masked, "host": host,
              "verdict": None, "stop_class": None, "error": kind, "reasons": [detail] if detail else [],
              "trail": st.trail if st else [], "untried": [], "fetched_at": run.now_iso(), "text": None}
    run.log({"kind": "outcome", "source": "read", "url": url if isinstance(url, str) else "", "host": host,
             "bucket": "refused", "error": kind, "contacted": bool(st and st.contacted)})
    return result


def _error_outcome(st: _Read, attempt: _Attempt) -> dict:
    if attempt.error in net.REFUSAL_KINDS:
        return _refused(st.run, st.url, attempt.error, attempt.error_detail, st)
    if attempt.error == "robots_unreachable":
        return _done(st, "deferred", error=attempt.error, reasons=["robots_unreachable", attempt.error_detail],
                     rung=attempt.rung, attempt=attempt, retry_after_s=attempt.retry_after_s)
    if attempt.error in net.TRANSIENT_KINDS:
        return _done(st, "deferred", error=attempt.error, reasons=[attempt.error_detail], rung=attempt.rung,
                     attempt=attempt, retry_after_s=TRANSIENT_RETRY_S)
    untried, notes = _remaining(st)
    return _done(st, "unread", error=attempt.error, reasons=[attempt.error_detail], rung=attempt.rung,
                 attempt=attempt, untried=untried, notes=notes, next_step=INGEST_HELP if "R3" in untried else None)


def _rate_limited(st: _Read, attempt: _Attempt, v: verdict.Verdict, rung: str) -> dict | None:
    response = attempt.response
    host = net.host_of(response.final_url)
    wait = verdict.retry_after_seconds(response.headers.get("retry-after"), st.run.clock())
    noted = st.run.note_rate_limit(host, wait, v.reasons)
    if noted["stopped"]:
        return _done(st, "stopped", stop="rate_limit", reasons=v.reasons + [noted["stop"]["reason"]], rung=rung,
                     attempt=attempt, host_stop=noted["stop"])
    _trail(st, rung, "rate_limited", attempt=attempt, v=v, note=f"one wait of {noted['wait_s']:.0f} s, then one retry")
    return None


def _host_signal(v: verdict.Verdict) -> bool:
    """A 429 or a 503 with Retry-After: one polite wait, then the host stops. A rate-limit notice
    without those statuses stops only its URL."""
    return v.stop_class == "rate_limit" and v.host_wide


def _terminal(st: _Read, attempt: _Attempt, page, v: verdict.Verdict, rung: str) -> dict | None:
    if v.stop_class:
        host_stop = None
        if v.stop_class in verdict.HOST_STOPPING and v.host_wide:
            host_stop = st.run.stop_host(net.host_of(attempt.response.final_url), v.stop_class,
                                         "interactive human check", v.reasons)
        return _done(st, "stopped", stop=v.stop_class, reasons=v.reasons, rung=rung, attempt=attempt,
                     page=page if v.stop_class == "paywall" else None, host_stop=host_stop)
    if v.transient:
        return _done(st, "deferred", reasons=v.reasons, rung=rung, attempt=attempt, retry_after_s=TRANSIENT_RETRY_S)
    if v.ok:
        return _done(st, "read", verdict_=v.verdict, reasons=v.reasons, rung=rung, attempt=attempt, page=page)
    return None


# ---------------------------------------------------------------- rungs


def _rung0(st: _Read, platform: dict | None, values: dict) -> dict | None:
    if not platform or not platform.get("official"):
        return None
    requests = 0
    for route in platform["official"]:
        kind = route.get("kind")
        if requests >= R0_MAX_REQUESTS:
            _trail(st, "R0", "skipped", note="R0 request cap reached")
            break
        if kind not in ("feed", "oembed"):
            _trail(st, "R0", "skipped", note=f"{kind} routes need a provider adapter (later phase)")
            continue
        local = dict(values)
        if route.get("auth") == "user_key":
            env = route.get("env", "")
            key = os.environ.get(env) if env else None
            if not key:
                _trail(st, "R0", "skipped", note=f"no user key in ${env}")
                continue
            local["key"] = quote(key, safe="")
        candidate = expand(route.get("url", ""), local)
        try:
            candidate = net.parse_url(candidate) if candidate else None
        except net.NetError:
            candidate = None
        if not candidate:
            _trail(st, "R0", "skipped", note=f"route {platform.get('id')} does not fit this URL")
            continue
        try:
            attempt = _request(st, candidate, "R0", accept=FEED_ACCEPT if kind == "feed" else JSON_ACCEPT,
                               purpose="route")
        except HostStopped as exc:
            _trail(st, "R0", "skipped", url=candidate, note=f"route host stopped ({exc.stop.get('class')})")
            continue
        except BudgetExceeded as exc:
            if exc.scope == "run":
                raise
            _trail(st, "R0", "skipped", url=candidate, note="route host budget used up")
            continue
        except net.NetError as exc:
            _trail(st, "R0", "failed", url=candidate, note=f"route host unusable ({exc.kind})")
            continue
        if attempt.contacted or attempt.error:
            requests += 1
        if attempt.stop or attempt.error:
            note = ", ".join(attempt.reasons[:2]) if attempt.scope else None
            _trail(st, "R0", "skipped" if attempt.scope else "failed", url=candidate, attempt=attempt, note=note)
            continue
        response = attempt.response
        if not 200 <= response.status < 300:
            _log_attempt(st.run, attempt)
            if response.status == 429:
                st.run.note_rate_limit(net.host_of(response.final_url),
                                       verdict.retry_after_seconds(response.headers.get("retry-after"),
                                                                   st.run.clock()), ["status:429"])
            _trail(st, "R0", "failed", url=candidate, attempt=attempt, note="unverified route; falls through")
            continue
        text, _ = response.text()
        page = extract.from_feed(text, st.url, route.get("scope", "item")) if kind == "feed" \
            else extract.from_oembed(text)
        if page is None:
            _log_attempt(st.run, attempt)
            _trail(st, "R0", "failed", url=candidate, attempt=attempt, note="no entry for this page")
            continue
        optouts = robots.page_optouts(response.headers, [], None, ROBOTS_TOKEN, response.x_robots)
        v = verdict.classify(status=response.status, headers=response.headers, page=page, requested_url=candidate,
                             final_url=response.final_url, expect=st.expect, optouts=optouts,
                             login_hosts=st.routes.login_hosts)
        _log_attempt(st.run, attempt, v, page)
        if v.ok:
            basis = "official_api" if route.get("auth") == "user_key" else "public_anonymous"
            return _done(st, "read", verdict_=v.verdict, reasons=v.reasons + [f"route:{platform.get('id')}"],
                         rung="R0", attempt=attempt, page=page, access_basis=basis)
        _trail(st, "R0", "failed", url=candidate, attempt=attempt, v=v)
    return None


def _alternates(st: _Read, platform: dict | None, values: dict, page) -> list[tuple[str, str]]:
    site = registrable_domain(net.host_of(st.url))
    found: list[tuple[str, str]] = []

    def add(url: str | None, source: str) -> None:
        try:
            url = net.parse_url(url) if url else None
        except net.NetError:
            return
        if not url or url == st.url or any(url == u for u, _ in found):
            return
        if registrable_domain(net.host_of(url)) != site:
            _trail(st, "R2", "ignored", url=url, note=f"{source} is on another registrable domain")
            return
        found.append((url, source))

    if page is not None:
        for kind in ("mobile", "amp", "feed"):
            for alternate in page.alternates:
                if alternate["kind"] == kind:
                    add(alternate["href"], f"declared:{kind}")
    for twin in (platform or {}).get("alternates", []):
        add(expand(twin.get("url", ""), values), f"route:{twin.get('kind', 'twin')}")
    host = net.host_of(st.url)
    mobile = None
    if host.startswith("www."):
        mobile = "m." + host[4:]
    elif host == site and not host.startswith("m."):
        mobile = "m." + host
    if mobile and net.resolves(mobile):
        parts = urlsplit(st.url)
        netloc = mobile + (f":{parts.port}" if parts.port else "")
        add(parts._replace(netloc=netloc).geturl(), "generic:m")
    return found


def _ladder(st: _Read) -> dict:
    # The page's own robots.txt decides before any rung: a path the site disallows is never read,
    # not even through an official route or an alternate on another host. This decision, not a
    # route host's, is the source's robots record.
    decision = robots_decision(st.run, st.url, st.max_wait)
    st.target_robots = decision
    if not decision["allowed"]:
        if decision["robots_status"] == "unreachable":
            return _done(st, "deferred", error="robots_unreachable", retry_after_s=decision.get("retry_after_s"),
                         reasons=["robots_unreachable", ROBOTS_UNREACHABLE])
        return _done(st, "stopped", stop="opted_out", reasons=_robots_reasons(decision))
    platform, values = st.routes.match(st.url)
    result = _rung0(st, platform, values)
    if result is not None:
        return result
    # R1: one honest GET, plus at most one polite retry after a first rate-limit signal
    attempt = _request(st, st.url, "R1")
    for _ in range(2):
        if attempt.stop:
            return _done(st, "stopped", stop=attempt.stop, reasons=attempt.reasons, rung="R1", attempt=attempt,
                         out_of_scope=attempt.out_of_scope)
        if attempt.error:
            return _error_outcome(st, attempt)
        page, v = _evaluate(st, attempt, requested=st.url)
        if not _host_signal(v):
            break
        stopped = _rate_limited(st, attempt, v, "R1")
        if stopped is not None:
            return stopped
        attempt = _request(st, st.url, "R1")
    terminal = _terminal(st, attempt, page, v, "R1")
    if terminal is not None:
        return terminal
    _trail(st, "R1", "escalate", attempt=attempt, v=v)
    last = v
    last_rung = "R1"
    # R2: the site's own alternates, at most two requests
    requests = 0
    candidates = _alternates(st, platform, values, page)
    if not candidates:
        _trail(st, "R2", "skipped", note="no alternate on this site")
    for candidate, source in candidates:
        if requests >= R2_MAX_REQUESTS:
            _trail(st, "R2", "skipped", url=candidate, note="R2 request cap reached")
            break
        feed = source.endswith(":feed")
        try:
            alt = _request(st, candidate, "R2", accept=FEED_ACCEPT if feed else PAGE_ACCEPT, purpose="alternate")
        except HostStopped as exc:
            _trail(st, "R2", "skipped", url=candidate, note=f"host stopped ({exc.stop.get('class')})")
            continue
        except BudgetExceeded as exc:
            if exc.scope == "run":
                raise
            _trail(st, "R2", "skipped", url=candidate, note="host budget used up")
            continue
        except net.NetError as exc:
            _trail(st, "R2", "failed", url=candidate, note=f"{source}: host unusable ({exc.kind})")
            continue
        if alt.contacted or alt.error:
            requests += 1
        if alt.scope or alt.stop == "opted_out":
            why = ", ".join(alt.reasons[:1]) if alt.scope else "robots.txt disallows it"
            _trail(st, "R2", "skipped", url=candidate, attempt=alt, note=f"{source}: {why}")
            continue
        if alt.stop:
            return _done(st, "stopped", stop=alt.stop, reasons=alt.reasons, rung="R2", attempt=alt)
        if alt.error:
            _trail(st, "R2", "failed", url=candidate, attempt=alt, note=source)
            continue
        alt_page, alt_v = _evaluate(st, alt, requested=candidate, feed_target=st.url if feed else None)
        if alt_v.stop_class == "gone" and alt.response.status in (404, 410):
            _trail(st, "R2", "failed", url=candidate, attempt=alt, v=alt_v, note=f"{source} does not exist")
            continue
        if _host_signal(alt_v):
            stopped = _rate_limited(st, alt, alt_v, "R2")
            if stopped is not None:
                return stopped
            continue
        if alt_v.transient:
            _trail(st, "R2", "failed", url=candidate, attempt=alt, v=alt_v, note=source)
            continue
        terminal = _terminal(st, alt, alt_page, alt_v, "R2")
        if terminal is not None:
            return terminal
        _trail(st, "R2", "escalate", url=candidate, attempt=alt, v=alt_v, note=source)
        last, last_rung = alt_v, "R2"
    untried, notes = _remaining(st)
    return _done(st, "unread", verdict_=last.verdict, reasons=last.reasons, rung=last_rung, untried=untried,
                 notes=notes, next_step=INGEST_HELP if "R3" in untried else None)


# ---------------------------------------------------------------- entry points


def read(run: Run, url: str, *, expect=(), max_wait: float | None = None) -> dict:
    run.require_open()
    wait = float(run.policy.get("max_wait_s", 60) if max_wait is None else max_wait)
    try:
        target = net.parse_url(url)
    except net.NetError as exc:
        return _refused(run, url, exc.kind, exc.detail)
    st = _Read(run, target, tuple(t for t in expect if t), wait, Routes(run.routes))
    host = net.host_of(target)
    parts = urlsplit(target)
    try:
        net.check_host(host, parts.port or (443 if parts.scheme == "https" else 80))
    except net.NetError as exc:
        if exc.kind in net.REFUSAL_KINDS:
            return _refused(run, target, exc.kind, exc.detail, st)
    excluded = scope_stop(run, st.routes, target)
    if excluded:
        stop, reasons, out_of_scope = excluded
        return _done(st, "stopped", stop=stop, reasons=reasons, out_of_scope=out_of_scope)
    stopped = run.host_stop(host)
    if stopped:
        return _done(st, "stopped", stop="host_stopped", reasons=[f"host_stop:{stopped['class']}"], host_stop=stopped)
    try:
        return _ladder(st)
    except Deferred as exc:
        return _done(st, "deferred", reasons=[f"deferred:{exc.why}"], retry_after_s=exc.retry_after_s)
    except HostStopped as exc:
        return _done(st, "stopped", stop="host_stopped", reasons=[f"host_stop:{exc.stop.get('class')}"],
                     host_stop=exc.stop)
    except BudgetExceeded as exc:
        return _done(st, "stopped", stop="budget", reasons=[f"budget:{exc.scope}:{exc.limit}"])
    except net.NetError as exc:
        if exc.kind in net.REFUSAL_KINDS:
            return _refused(run, target, exc.kind, exc.detail, st)
        return _done(st, "unread", error=exc.kind, reasons=[exc.detail])


def check_robots(run: Run, url: str, *, max_wait: float | None = None) -> dict:
    """What a browser tool may open on this URL's host, without reading the page: the deny list, the
    route table's out-of-scope channels, a host stopped for this run, and robots.txt. Page-level
    opt-outs (noai, TDM) are in the page itself, so only `read` sees them."""
    run.require_open()
    wait = float(run.policy.get("max_wait_s", 60) if max_wait is None else max_wait)
    try:
        target = net.parse_url(url)
        parts = urlsplit(target)
        net.check_host(parts.hostname or "", parts.port or (443 if parts.scheme == "https" else 80))
    except net.NetError as exc:
        if exc.kind in net.REFUSAL_KINDS:
            return {"url": privacy.mask_url(url), "exit_code": EXIT["refused"], "error": exc.kind,
                    "reasons": [exc.detail]}
        target = net.parse_url(url)
    masked = privacy.mask_url(target)
    excluded = scope_stop(run, Routes(run.routes), target)
    if excluded:  # decided before robots.txt is fetched: nothing is sent to an excluded host
        stop, reasons, out_of_scope = excluded
        return {"url": masked, "exit_code": EXIT["stopped"], "allowed": False, "stop_class": stop,
                "reasons": reasons, "out_of_scope": out_of_scope}
    stopped = run.host_stop(net.host_of(target))
    if stopped:
        return {"url": masked, "exit_code": EXIT["stopped"], "allowed": False, "stop_class": "host_stopped",
                "reasons": [f"host_stop:{stopped['class']}"], "host_stop": stopped}
    try:
        decision = robots_decision(run, target, wait)
    except Deferred as exc:
        return {"url": masked, "exit_code": EXIT["deferred"], "allowed": False, "retry_after_s": exc.retry_after_s,
                "reasons": [f"deferred:{exc.why}"]}
    except HostStopped as exc:
        return {"url": masked, "exit_code": EXIT["stopped"], "allowed": False, "stop_class": "host_stopped",
                "host_stop": exc.stop}
    except net.NetError as exc:
        code = EXIT["refused"] if exc.kind in net.REFUSAL_KINDS else EXIT["unread"]
        return {"url": masked, "exit_code": code, "allowed": False, "error": exc.kind, "reasons": [exc.detail]}
    if decision["allowed"]:
        return {"url": masked, "exit_code": EXIT["read"], "stop_class": None, **decision}
    if decision["robots_status"] == "unreachable":
        return {"url": masked, "exit_code": EXIT["deferred"], "stop_class": None, "error": "robots_unreachable",
                "reasons": ["robots_unreachable", ROBOTS_UNREACHABLE], **decision}
    return {"url": masked, "exit_code": EXIT["stopped"], "stop_class": "opted_out", **decision}


PAGE_READ_REQUIRED = {"schema_version": str, "url": str, "final_url": str, "status": int, "text": str,
                      "context": str, "started_at": str, "finished_at": str}


def check_page_read(doc) -> None:
    """Shape checks for ux-page-read.v1 (schemas/ux-page-read.v1.schema.json)."""
    if not isinstance(doc, dict) or doc.get("schema_version") != "ux-page-read.v1":
        raise ValueError("not a ux-page-read.v1 document")
    for name, kind in PAGE_READ_REQUIRED.items():
        if not isinstance(doc.get(name), kind) or isinstance(doc.get(name), bool):
            raise ValueError(f"ux-page-read.v1 needs {name} ({kind.__name__})")
    if len(doc["text"]) > extract.TEXT_CAP_CHARS:
        raise ValueError("ux-page-read.v1 text is longer than 400 KB")
    blocks = doc.get("json_ld", [])
    if not isinstance(blocks, list) or len(blocks) > extract.JSONLD_MAX_BLOCKS:
        raise ValueError("ux-page-read.v1 json_ld must be a list of at most 10 blocks")
    for name in ("meta", "challenge"):
        if name in doc and not isinstance(doc[name], dict):
            raise ValueError(f"ux-page-read.v1 {name} must be an object")


def _ingest_refused(run: Run, url: str, reason: str) -> dict:
    run.log({"kind": "outcome", "source": "ingest", "url": url, "host": net.host_of(url) if url else "",
             "bucket": "refused", "error": "ingest_refused", "reasons": [reason]})
    return {"source": "ingest", "bucket": "refused", "exit_code": EXIT["refused"], "url": privacy.mask_url(url),
            "error": "ingest_refused", "reasons": [reason], "text": None}


def _ingest_stopped(run: Run, target: str, host: str, context: str, stop_class: str, reasons: list,
                    **extra) -> dict:
    """A capture that is not taken in: a host stop or a budget stop decided before it is looked at."""
    run.log({"kind": "outcome", "source": "ingest", "url": target, "url_key": run.url_key(target), "host": host,
             "bucket": "stopped", "stop_class": stop_class, "rung": "R3", "context": context, "reasons": reasons,
             "host_stop": (extra.get("host_stop") or {}).get("class")})
    return {"source": "ingest", "bucket": "stopped", "exit_code": EXIT["stopped"], "url": privacy.mask_url(target),
            "host": host, "verdict": None, "stop_class": stop_class, "reasons": reasons, "rung": "R3",
            "presentation": "real_browser", "context": context, "untried": [],
            "notes": ["the capture text was discarded"], "text": None, **extra}


def authorised_community(run: Run, url: str) -> dict | None:
    """The community in the brief's access_policy.signed_in_communities that covers this URL: its
    host (subdomains included) and, when the entry has one, its path prefix. Only the user's brief
    adds entries; nothing a page says counts as authorisation."""
    try:
        parts = urlsplit(url)
        host = parts.hostname or ""
    except ValueError:
        return None
    path = parts.path or "/"
    for community in run.policy.get("signed_in_communities") or []:
        if not verdict.host_matches(host, [community.get("host", "")]):
            continue
        prefix = (community.get("path_prefix") or "").rstrip("/")
        if not prefix or path == prefix or path.startswith(prefix + "/"):
            return community
    return None


def _capture_blocked(run: Run, target: str, community: dict | None) -> tuple[str | None, dict | None]:
    """(why a capture of this URL may not be taken in, or None; the anonymous read of it).

    A capture needs an earlier anonymous read of the same URL that reached the page and did not
    stop; in an authorised community a membership stop (auth_gate) is the one stop a signed-in
    capture may follow. A capture never replaces a stop, and no capture follows one that stopped."""
    key = run.url_key(target)
    prior = run.last_outcome(key, kind="read")
    if prior is None:
        return "no earlier anonymous read of this URL in this run; run `read` first", None
    bucket, stop = prior.get("bucket"), prior.get("stop_class")
    if bucket == "deferred":
        return "the anonymous read was deferred; run `read` again after its retry_after_s", prior
    member_wall = community is not None and stop == "auth_gate" and not prior.get("out_of_scope")
    if (bucket not in ("read", "unread") or stop) and not member_wall:
        lifted = "; authorisation lifts only a membership stop (auth_gate)" if community is not None else ""
        return f"the anonymous read ended in {stop or bucket}; a capture cannot replace a stop{lifted}", prior
    if not prior.get("contacted"):
        return "the anonymous read made no request for this page; run `read` again", prior
    for earlier in run.outcomes(key, kind="ingest"):
        if earlier.get("bucket") != "stopped":
            continue
        if community is not None and earlier.get("stop_class") == "auth_gate" and earlier.get("context") != "signed_in":
            continue  # an anonymous capture met the membership wall; the authorised member's view may follow
        return (f"an earlier capture of this URL ended in {earlier.get('stop_class')}; "
                "a capture cannot replace a stop"), prior
    return None, prior


def ingest(run: Run, url: str, file_path, *, fmt: str | None = None, context: str, expect=()) -> dict:
    """Accept a render capture (html, txt or ux-page-read.v1) after an anonymous read of the same URL.

    `context` is the browser context the capture came from. `signed_in` is accepted only for a
    community the brief authorises; its text is member content (access_basis authorised_member),
    scrubbed of personal identifiers, and shared outputs keep authored summaries of it only. A
    human check in a capture stops the host, a rate-limit page in it is a rate-limit signal, and
    the capture resets or extends the host's run of unreadable URLs."""
    run.require_open()
    try:
        target = net.parse_url(url)
    except net.NetError as exc:
        return _ingest_refused(run, url if isinstance(url, str) else "", f"{exc.kind}: {exc.detail}")
    if context not in CONTEXTS:
        return _ingest_refused(run, target, f"context must be one of {', '.join(CONTEXTS)}")
    routes = Routes(run.routes)
    excluded = scope_stop(run, routes, target)
    if excluded:
        why = "a private channel, out of this research's scope" if excluded[2] else "a host the researcher excludes"
        return _ingest_refused(run, target, f"this URL is on {why} ({', '.join(excluded[1])}); it is never captured")
    community = authorised_community(run, target) if context == "signed_in" else None
    if context == "signed_in" and community is None:
        return _ingest_refused(run, target, "signed-in captures are accepted only for communities the brief authorises "
                                            "(access_policy.signed_in_communities); capture this page in a private "
                                            "or signed-out window")
    blocked, prior = _capture_blocked(run, target, community)
    if blocked:
        return _ingest_refused(run, target, blocked)
    path = Path(file_path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > INGEST_MAX_BYTES:
        return _ingest_refused(run, target, "the capture must be a regular file of at most 8 MB")
    data = path.read_bytes()
    fmt = fmt or {".json": "page-read", ".txt": "txt", ".text": "txt"}.get(path.suffix.lower(), "html")
    status, final_url = 200, target
    try:
        if fmt == "page-read":
            doc = json.loads(data.decode("utf-8"))
            check_page_read(doc)
            if doc["context"] != "anonymous" or context == "signed_in":
                return _ingest_refused(run, target, "a ux-page-read.v1 capture comes from a fresh anonymous context; "
                                                    "declare it with --context anonymous")
            declared = {net.parse_url(u) for u in (doc.get("url"), doc.get("final_url")) if isinstance(u, str) and u}
            if target not in declared:
                return _ingest_refused(run, target, "the capture is for a different URL")
            page = extract.from_page_read(doc)
            status = int(doc.get("status") or 200)
            if isinstance(doc.get("final_url"), str) and doc["final_url"]:
                final_url = net.parse_url(doc["final_url"])
        elif fmt == "html":
            page = extract.from_html(net.decode_body(data, "text/html")[0], target)
        elif fmt == "txt":
            page = extract.from_text(net.decode_body(data, "text/plain")[0])
        else:
            return _ingest_refused(run, target, f"unknown format {fmt}")
    except (ValueError, TypeError, UnicodeError, net.NetError) as exc:
        return _ingest_refused(run, target, f"unreadable capture: {exc}")
    host = net.host_of(target)
    stopped = run.host_stop(host)
    if stopped and stopped.get("class") in ("rate_limit", "human_check"):
        return _ingest_stopped(run, target, host, context, "host_stopped", [f"host_stop:{stopped['class']}"],
                               host_stop=stopped)
    try:
        run.book_render(host)
    except BudgetExceeded as exc:
        return _ingest_stopped(run, target, host, context, "budget", [f"budget:{exc.scope}:{exc.limit}"])
    optouts = robots.page_optouts({}, page.meta_robots, page.tdm_meta, ROBOTS_TOKEN)
    v = verdict.classify(status=status, headers={}, page=page, requested_url=target, final_url=final_url,
                         expect=tuple(t for t in expect if t), optouts=optouts, login_hosts=routes.login_hosts,
                         capture=True, signed_in=community is not None)
    fetch_id = run.new_fetch_id()
    bucket = "read" if v.ok else "stopped" if v.stop_class else "unread"
    notes: list = []
    host_stop = None
    # A render is what a person's browser shows, so a human check in it stops the whole host, and a
    # rate-limit page in it is a rate-limit signal for the host (one wait, then the host stops).
    if v.stop_class == "human_check":
        host_stop = run.stop_host(host, "human_check", "human check in a render capture", v.reasons)
    elif v.stop_class == "rate_limit":
        noted = run.note_rate_limit(host, None, v.reasons)
        host_stop = noted["stop"] if noted["stopped"] else None
    if bucket in ("read", "unread"):  # a render was the last allowed rung: it resets or extends the streak
        streak = run.note_outcome(host, bucket)
        if streak:
            host_stop = streak
    if host_stop:
        notes.append("this host is now stopped for the run: " + host_stop["reason"])
    basis = ("authorised_member" if community is not None else "public_anonymous") if bucket == "read" else None
    run.log({"kind": "ingest", "fetch_id": fetch_id, "rung": "R3", "presentation": PRESENTATION["R3"],
             "url": target, "final_url": final_url, "host": host, "format": fmt, "context": context,
             "bytes": len(data), "status": status, "verdict": v.verdict, "stop_class": v.stop_class,
             "text_chars": len(page.text) if v.ok else None, "extraction_source": page.extraction_source})
    result = {"source": "ingest", "bucket": bucket, "exit_code": EXIT[bucket], "url": privacy.mask_url(target),
              "final_url": privacy.mask_url(final_url), "host": host, "verdict": v.verdict,
              "stop_class": v.stop_class, "reasons": v.reasons[:10], "rung": "R3", "presentation": "real_browser",
              "context": context, "format": fmt, "fetch_id": fetch_id, "untried": [], "fetched_at": run.now_iso(),
              "access_basis": basis, "host_stop": host_stop, "notes": notes, "text": None}
    if community is not None:
        result["community"] = community.get("name")
    if v.ok:
        text = page.text
        if community is not None:  # member content: no personal identifiers, summaries only downstream
            text, scrubbed = privacy.scrub(text)
            result.update(summary_only=True, scrubbed=scrubbed)
            notes.append(AUTHORISED_NOTE)
        else:
            result["meta"] = page.metadata()
        run.save_page(fetch_id, text)
        result.update(extraction_source=page.extraction_source, text_chars=len(text), truncated=page.truncated,
                      content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                      injection=scan_injection(text), promo_flags=verdict.promotion_flags(text), text=text)
    elif v.stop_class:
        notes.append("the capture text was discarded")
    run.log({"kind": "outcome", "source": "ingest", "url": target, "url_key": run.url_key(target), "host": host,
             "fetched_at": result["fetched_at"],
             "robots": {"decision": (prior.get("robots") or {}).get("decision"),
                        "status": (prior.get("robots") or {}).get("status")},
             "bucket": bucket, "verdict": v.verdict, "stop_class": v.stop_class, "rung": "R3",
             "presentation": "real_browser", "fetch_id": fetch_id, "context": context, "untried": [],
             "access_basis": basis, "community": result.get("community"), "contacted": False,
             "reasons": v.reasons[:6], "text_chars": result.get("text_chars"),
             "content_sha256": result.get("content_sha256"),
             "injection_risk": (result.get("injection") or {}).get("risk"),
             "host_stop": (host_stop or {}).get("class")})
    return result


__all__ = ["read", "ingest", "check_robots", "check_page_read", "robots_decision", "registrable_domain", "Routes",
           "EXIT", "PRESENTATION", "RUNGS"]
