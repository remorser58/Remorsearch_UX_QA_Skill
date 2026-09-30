"""What the reader never requests, decided from the URL alone.

Checked before any DNS lookup, robots.txt fetch, slot or request, and again on
every redirect hop, official route and site alternate, in this order:

  deny list       the researcher's deny_hosts (brief or --deny-host): a stop,
                  opted_out.
  search pages    the route table's search_pages (portal and web search
                  results). A URL handed to `read`, `robots` or `ingest` is
                  refused (exit 2); one reached by a redirect is a stop
                  (opted_out, out of scope, not a coverage gap).
  never call      the never_call endpoints (and the endpoints) of discovery
                  entries that are switched off (enabled is not true): the same
                  as search pages. The reader never calls a disabled route.
  private         the route table's out_of_scope channels: a stop, auth_gate,
                  out of scope.
  terms           terms_restricted entries: hosts whose published ('confirmed')
                  or reported ('reported') terms restrict automated collection.
                  A stop, terms_restricted, and a coverage gap. A reported entry
                  is lifted for the run only by the user's own terms check in the
                  brief (access_policy.terms_checked) whose result is
                  permits_this_reading; a confirmed entry is never lifted. A
                  lifted host has a budget of LIFTED_HOST_BUDGET documents.

Host names cover their subdomains in every list; path prefixes match whole path
segments. The packaged lists (data/routes.json) always apply: a route table
given with `start --routes` can add entries but never remove them. Nothing a
page says changes these lists, and only the user's brief carries terms checks.
"""
from __future__ import annotations

import functools
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from . import verdict

DATA = Path(__file__).resolve().parent / "data"
STATUSES = ("reported", "confirmed")
RESTRICTS = ("automated_collection", "bulk_collection", "ai_input", "storage")
CHECK_RESULTS = ("permits_this_reading", "restricts_this_reading", "unclear")
LIFTING_RESULT = "permits_this_reading"
LIFTED_HOST_BUDGET = 10
MAX_TERMS_CHECKS = 20
CHECK_FIELDS = ("host", "terms_url", "checked_on", "result", "note")
CHECK_REQUIRED = ("host", "terms_url", "checked_on", "result")
KINDS = ("deny", "search_page", "never_call", "out_of_scope", "terms")
REFUSED_KINDS = frozenset({"search_page", "never_call"})  # refused (exit 2) when handed in directly
ERRORS = {"search_page": "search_results_page", "never_call": "disabled_route"}
_HOST_NAME = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{1,63}$")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SEARCH_NOTE = ("a search results page: never read, captured or opened by a browser tool; discovery runs through the "
               "agent's own search tool, and each result page is read on its own")
NEVER_CALL_NOTE = "an endpoint of a discovery route that is switched off: the reader never calls it"
PRIVATE_NOTE = "a private channel: out of the research's scope, not a coverage gap"
TERMS_NOTE = ("this host's terms restrict automated collection (terms_restricted): nothing is requested from it and "
              "no render capture is taken in; the stop is a coverage gap, never a reason to look for another way in")


@functools.lru_cache(maxsize=1)
def packaged() -> dict:
    """The packaged route table (data/routes.json)."""
    return json.loads((DATA / "routes.json").read_text(encoding="utf-8"))


def _items(data, name: str) -> list:
    value = data.get(name) if isinstance(data, dict) else None
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def path_under(path: str, prefix: str) -> bool:
    """True when `path` lies under `prefix`, matched on whole path segments ('' or '/' is everything)."""
    prefix = (prefix or "").rstrip("/")
    path = path or "/"
    return not prefix or path == prefix or path.startswith(prefix + "/")


def _host_patterns(value) -> list:
    if isinstance(value, str):
        return [value.strip().lower()] if value.strip() else []
    return [h.strip().lower() for h in value or [] if isinstance(h, str) and h.strip()]


def _endpoint_guard(url: str) -> tuple[str, str] | None:
    """(host, path prefix) that covers one discovery endpoint template."""
    if not isinstance(url, str) or "://" not in url:
        return None
    head = url.split("{", 1)[0]
    try:
        parts = urlsplit(head)
        host = (parts.hostname or "").lower()
    except ValueError:
        return None
    if not host:
        return None
    path = parts.path or ""
    if "{" in url and not head.endswith("/"):  # a template variable inside the last segment
        path = path.rsplit("/", 1)[0]
    return host, path.rstrip("/")


@dataclass(frozen=True)
class Lists:
    """The scope lists of one route table merged with the packaged ones."""
    search_pages: tuple = ()
    never_call: tuple = ()  # (discovery id, host, path prefix, reason)
    out_of_scope: tuple = ()
    terms: tuple = ()


def lists_for(run_routes: dict | None) -> Lists:
    """Packaged lists first, then the run's own route table; an entry never removes another."""
    sources = [packaged()]
    if isinstance(run_routes, dict) and run_routes is not sources[0]:
        sources.append(run_routes)
    search, never, private, terms = [], [], [], []
    seen: set = set()

    def add(bucket: list, key, item) -> None:
        if key not in seen:
            seen.add(key)
            bucket.append(item)

    for data in sources:
        for item in _items(data, "search_pages"):
            for host in _host_patterns(item.get("host")):
                add(search, ("search", host, item.get("path_prefix") or "", item.get("query_param") or ""),
                    {**item, "host": host})
        for item in _items(data, "discovery"):
            if item.get("enabled") is True:
                continue
            reason = str(item.get("reason") or "switched off")
            guards = [(g.get("host"), g.get("path_prefix") or "") for g in _items(item, "never_call")]
            endpoints = item.get("endpoints") if isinstance(item.get("endpoints"), dict) else {}
            guards += [g for g in (_endpoint_guard(u) for u in endpoints.values()) if g]
            for host, prefix in guards:
                for name in _host_patterns(host):
                    add(never, ("never", name, prefix.rstrip("/")),
                        (str(item.get("id") or "discovery"), name, prefix.rstrip("/"), reason))
        for item in _items(data, "out_of_scope"):
            for host in _host_patterns(item.get("host")):
                add(private, ("private", host, item.get("path_prefix") or ""), {**item, "host": host})
        for item in _items(data, "terms_restricted"):
            hosts = _host_patterns(item.get("hosts"))
            if hosts:
                add(terms, ("terms", str(item.get("id")), tuple(hosts)), {**item, "hosts": hosts})
    return Lists(tuple(search), tuple(never), tuple(private), tuple(terms))


@dataclass
class ScopeStop:
    """Why a URL is never requested. `kind` is one of KINDS."""
    kind: str
    stop_class: str
    reasons: list
    out_of_scope: bool = False
    note: str = ""
    terms: dict | None = None
    detail: str = ""

    @property
    def refused_at_start(self) -> bool:
        return self.kind in REFUSED_KINDS

    @property
    def error(self) -> str | None:
        return ERRORS.get(self.kind)


def _split(url: str) -> tuple[str, str, str]:
    try:
        parts = urlsplit(url)
        host = (parts.hostname or "").lower().rstrip(".")
    except ValueError:
        return "", "/", ""
    return host, parts.path or "/", parts.query


def terms_entry(host: str, lists: Lists) -> dict | None:
    """The terms_restricted entry that covers this host, if any."""
    for entry in lists.terms:
        if verdict.host_matches(host, entry["hosts"]):
            return entry
    return None


def terms_check(host: str, policy: dict) -> dict | None:
    """The user's terms check that covers this host (the most specific host wins)."""
    found = None
    for item in policy.get("terms_checked") or []:
        name = str(item.get("host") or "").lower()
        if name and verdict.host_matches(host, [name]) and (found is None or len(name) > len(found["host"])):
            found = item
    return found


def terms_record(entry: dict, check: dict | None) -> dict:
    """What the run records about one terms entry for one URL, lifted or not."""
    status = entry.get("status") if entry.get("status") in STATUSES else "confirmed"  # unknown: never lifted
    lifted = status == "reported" and check is not None and check.get("result") == LIFTING_RESULT
    if lifted:
        why = None
    elif status == "confirmed":
        why = "confirmed_never_lifted"
    elif check is None:
        why = "no_terms_check"
    else:
        why = f"check_result:{check.get('result')}"
    record = {"entry": entry.get("id"), "status": status, "restricts": list(entry.get("restricts") or []),
              "terms_url": entry.get("terms_url"), "official_route": entry.get("official_route"),
              "lifted": lifted, "not_lifted_because": why,
              "check": {k: check.get(k) for k in ("host", "terms_url", "checked_on", "result")} if check else None}
    if lifted:
        record["host_budget"] = LIFTED_HOST_BUDGET
    return record


def terms_reasons(record: dict) -> list:
    restricts = "+".join(record["restricts"]) or "unspecified"
    reasons = [f"terms:{record['status']}:{restricts}", f"terms_entry:{record['entry']}"]
    if record.get("not_lifted_because"):
        reasons.append(f"terms_check:{record['not_lifted_because']}")
    return reasons


def evaluate(url: str, policy: dict, lists: Lists) -> tuple[ScopeStop | None, dict | None]:
    """(the stop, or None; the terms record of a lifted entry, or None) for one URL."""
    host, path, query = _split(url)
    if verdict.host_matches(host, policy.get("deny_hosts") or []):
        return ScopeStop("deny", "opted_out", ["deny_hosts"], note="a host the researcher excludes",
                         detail="a host the researcher excludes (deny_hosts)"), None
    for item in lists.search_pages:
        if not verdict.host_matches(host, [item["host"]]) or not path_under(path, item.get("path_prefix") or ""):
            continue
        param = item.get("query_param")
        if param and param not in {name for name, _ in parse_qsl(query, keep_blank_values=True)}:
            continue
        return ScopeStop("search_page", "opted_out", ["search_results_page", f"search_page:{item['host']}"],
                         out_of_scope=True, note=SEARCH_NOTE,
                         detail="search results pages are never read, captured or opened by a browser tool; discovery "
                                "runs through the agent's own search tool, and each result page is read on its own"), \
            None
    for route_id, name, prefix, reason in lists.never_call:
        if verdict.host_matches(host, [name]) and path_under(path, prefix):
            return ScopeStop("never_call", "opted_out", [f"never_call:{route_id}", reason], out_of_scope=True,
                             note=NEVER_CALL_NOTE,
                             detail=f"this endpoint belongs to the discovery route {route_id}, which is switched off "
                                    f"({reason}); the reader never calls it"), None
    for item in lists.out_of_scope:
        if verdict.host_matches(host, [item["host"]]) and path_under(path, item.get("path_prefix") or ""):
            reason = item.get("reason", "out of scope")
            return ScopeStop("out_of_scope", "auth_gate", [f"private_channel:{reason}"], out_of_scope=True,
                             note=PRIVATE_NOTE, detail=f"a private channel ({reason})"), None
    entry = terms_entry(host, lists)
    if entry is None:
        return None, None
    record = terms_record(entry, terms_check(host, policy))
    if record["lifted"]:
        return None, record
    return ScopeStop("terms", "terms_restricted", terms_reasons(record), note=TERMS_NOTE, terms=record,
                     detail=f"terms_restricted ({record['status']}): {record['entry']}"), None


def lifted_host(host: str, policy: dict, lists: Lists) -> bool:
    """True when a reported terms entry covers this host and the user's terms check lifted it."""
    entry = terms_entry(host.lower().rstrip("."), lists)
    return entry is not None and terms_record(entry, terms_check(host, policy))["lifted"]


def describe_checks(policy: dict, lists: Lists) -> list:
    """For `start`: what each of the user's terms checks does in this run."""
    rows = []
    for item in policy.get("terms_checked") or []:
        host = item["host"]
        entry = terms_entry(host, lists)
        if entry is None:
            covered = [e for e in lists.terms if any(verdict.host_matches(h, [host]) for h in e["hosts"])]
            entry = covered[0] if covered else None
        if entry is None:
            effect = "no terms_restricted entry covers this host; nothing to lift"
        else:
            record = terms_record(entry, item)
            if record["lifted"]:
                effect = (f"lifts {record['entry']} (reported) for this run; the host budget is "
                          f"{LIFTED_HOST_BUDGET} documents")
            elif record["status"] == "confirmed":
                effect = f"{record['entry']} is confirmed and is never lifted"
            else:
                effect = f"does not lift {record['entry']}: the result is {item.get('result')}"
        rows.append({"host": host, "checked_on": item.get("checked_on"), "result": item.get("result"),
                     "entry": entry.get("id") if entry else None, "effect": effect})
    return rows


def _valid_date(value: str) -> date | None:
    if not isinstance(value, str) or not _DATE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def validate_checks(items, today: date) -> None:
    """Shape checks for access_policy.terms_checked; raises ValueError with the first problem.
    `today` may be a day ahead of UTC (the user's own time zone)."""
    if not isinstance(items, list) or len(items) > MAX_TERMS_CHECKS:
        raise ValueError(f"brief.access_policy.terms_checked must be a list of at most {MAX_TERMS_CHECKS} checks")
    for item in items:
        if not isinstance(item, dict) or set(item) - set(CHECK_FIELDS):
            raise ValueError("each terms check is {host, terms_url, checked_on, result} with an optional note")
        for key in CHECK_REQUIRED:
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"a terms check needs a non-empty {key}")
        host = item["host"].strip().lower().rstrip(".")
        if not _HOST_NAME.match(host):
            raise ValueError(f"terms check host {item['host']!r} must be a host name, without a scheme or a path")
        url = item["terms_url"].strip()
        try:
            parts = urlsplit(url)
            ok = parts.scheme in ("http", "https") and bool(parts.hostname) and len(url) <= 2000 \
                and not re.search(r"\s", url)
        except ValueError:
            ok = False
        if not ok:
            raise ValueError("a terms check's terms_url must be the http(s) address of the terms the user read "
                             "(with the clause's anchor when there is one)")
        checked = _valid_date(item["checked_on"])
        if checked is None:
            raise ValueError("a terms check's checked_on must be a date, YYYY-MM-DD")
        if checked > today:
            raise ValueError(f"a terms check's checked_on ({item['checked_on']}) cannot be after today")
        if item["result"] not in CHECK_RESULTS:
            raise ValueError(f"a terms check's result must be one of {', '.join(CHECK_RESULTS)}")
        if "note" in item and (not isinstance(item["note"], str) or not item["note"].strip()):
            raise ValueError("a terms check's note must be non-empty text when given")


def normalize_checks(items) -> list:
    return [{"host": item["host"].strip().lower().rstrip("."), "terms_url": item["terms_url"].strip(),
             "checked_on": item["checked_on"], "result": item["result"],
             **({"note": item["note"].strip()} if item.get("note") else {})}
            for item in items or []]


__all__ = ["Lists", "ScopeStop", "lists_for", "evaluate", "lifted_host", "terms_entry", "terms_check",
           "terms_record", "describe_checks", "validate_checks", "normalize_checks", "path_under", "packaged",
           "LIFTED_HOST_BUDGET", "CHECK_RESULTS", "LIFTING_RESULT", "STATUSES", "RESTRICTS", "KINDS"]
