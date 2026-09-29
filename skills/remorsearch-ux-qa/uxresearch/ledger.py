"""Per-run state shared by every reader: pacing, budgets, host stops, caches.

`start` creates the run folder, by default
${XDG_STATE_HOME:-~/.local/state}/remorsearch-ux-qa/runs/<id>, outside any
project so page text never lands in a repository. It holds:

  run.json             run id, versions, policy, hashes of the brief and routes
  salt                 random key for author and thread keys (0600; deleted at close)
  brief.json           the research brief, when one was given
  routes.json          the route table this run uses
  hosts.json           per-host pacing, counters, stop state; robots.txt cache
  access-ledger.jsonl  append-only, URL-masked record of every request and outcome;
                       at close every URL in it is cut to its scheme and host
  pages/<fetch_id>.txt page text kept for later verbatim checks (0600; purged
                       after 72 h; deleted at close). Raw HTML is never written.

Volume rules, enforced for all parallel readers through an exclusive flock on
state.lock: one request at a time per host (a lease), at least min_interval
seconds apart (default 8, never below 5) or the robots.txt Crawl-delay if
longer, plus 0-4 s of jitter; a per-host and a per-run budget of document
requests (30 and 200 by default, raisable with a recorded reason to at most 100
and 500; robots.txt requests are not charged); after a rate-limit signal one
wait of at most 5 minutes, and a second signal stops the host; three unreadable
URLs in a row stop the host as bot_filter_persistent (a URL counts only once no
allowed rung is left for it; a successful render capture resets the count).
While another reader holds a host, a caller polls until its own max wait runs
out. When the next slot is further away than the caller's max wait, the reader
is told to come back later (Deferred) instead of blocking.
"""
from __future__ import annotations

import fcntl
import hashlib
import hmac
import json
import math
import os
import random
import re
import secrets
import shutil
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from urllib.parse import urlsplit

from . import RULES_VERSION, USER_AGENT, VERSION, net
from .privacy import mask_url, origin_only

RUN_SCHEMA = "ux-research-run.v1"
HOSTS_SCHEMA = "ux-research-hosts.v1"
BRIEF_SCHEMA = "ux-research-brief.v1"
DEFAULTS = {"per_host": 30, "per_run": 200, "min_interval_s": 8.0, "search_queries": 120}
CEILINGS = {"per_host": 100, "per_run": 500}
MIN_INTERVAL_FLOOR_S = 5.0
JITTER_MAX_S = 4.0
LEASE_S = 150.0
POLL_S = 1.0
PAGE_TTL_S = 72 * 3600
DEFAULT_RATE_LIMIT_WAIT_S = 60.0
MAX_RATE_LIMIT_WAIT_S = 300.0
UNREADABLE_STREAK = 3
ROBOTS_RETRY_S = 900.0
DEFAULT_MAX_WAIT_S = 60.0
DEFAULT_ACCEPT_LANGUAGE = "ko-KR,ko;q=0.9,en;q=0.8"
RENDER_MODES = ("driver", "host_browser", "off")
AUDIENCE_QUESTIONS = ("segments", "weight", "priority", "devices_and_grips", "abilities_and_conditions",
                      "contexts_of_use", "key_tasks", "pain_points")
_URL_FIELDS = ("url", "final_url", "location", "requested_url", "route_url")
_LEDGER_URL_KEYS = frozenset(_URL_FIELDS) | {"from", "to"}
BRIEF_FIELDS = ("schema_version", "product", "personas_for", "audience_questions", "languages", "channels",
                "time_windows", "budgets", "access_policy", "team_analytics_available", "report_lang")
_LANG_TAG = re.compile(r"^[A-Za-z]{1,8}(-[A-Za-z0-9]{1,8}){0,3}$")
_HOST_NAME = re.compile(r"^(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{1,63}$")
_PATH_PREFIX = re.compile(r"^/[^\s?#]{0,200}$")
COMMUNITY_FIELDS = ("host", "name", "why", "path_prefix")
MAX_COMMUNITIES = 20


class RunError(Exception):
    """A usage or policy refusal (exit code 2)."""


class Deferred(Exception):
    def __init__(self, retry_after_s: float, host: str, why: str = "pacing"):
        super().__init__(f"{host}: next slot in {retry_after_s:.0f} s ({why})")
        self.retry_after_s = int(math.ceil(retry_after_s))
        self.host = host
        self.why = why


class HostStopped(Exception):
    def __init__(self, host: str, stop: dict):
        super().__init__(f"{host} is stopped for this run ({stop.get('class')})")
        self.host = host
        self.stop = stop


class BudgetExceeded(Exception):
    def __init__(self, scope: str, host: str, limit: int):
        super().__init__(f"{scope} budget of {limit} document requests is used up")
        self.scope = scope
        self.host = host
        self.limit = limit


def iso(moment: float) -> str:
    return datetime.fromtimestamp(moment, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def default_root() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base).expanduser() / "remorsearch-ux-qa" / "runs"


def _atomic_write(path: Path, text: str) -> None:
    if path.is_symlink():
        raise RunError(f"refusing to write through a symlink: {path}")
    fd, name = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _write_new(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)


def _read_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise RunError(f"missing or unsafe run file: {path.name}")
    if path.stat().st_size > 64 * 1024 * 1024:
        raise RunError(f"run file too large: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def accept_language(primary: str | None, secondary=()) -> str:
    tags: list[str] = []
    for tag in [primary, *secondary]:
        if not tag:
            continue
        if not _LANG_TAG.match(tag):
            raise RunError(f"invalid language tag: {tag!r}")
        for item in (tag, tag.split("-")[0]):
            if item not in tags:
                tags.append(item)
    if not tags:
        return DEFAULT_ACCEPT_LANGUAGE
    return ",".join(t if i == 0 else f"{t};q={max(0.1, 1 - 0.1 * i):.1f}" for i, t in enumerate(tags[:6]))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RunError(message)


_NESTED_FIELDS = {
    "product": ("name", "surface", "url", "locale", "category", "release_date", "current_version"),
    "languages": ("primary", "secondary"),
    "channels": ("include", "exclude"),
    "budgets": ("per_host", "per_run", "search_queries", "min_interval_s", "reason"),
    "access_policy": ("engine_opt_in", "deny_hosts", "allow_wayback_for_official", "render", "signed_in_communities"),
}


def validate_brief(brief) -> None:
    """Shape checks for ux-research-brief.v1 (schemas/ux-research-brief.v1.schema.json)."""
    _require(isinstance(brief, dict), "the brief must be a JSON object")
    extra = sorted(set(brief) - set(BRIEF_FIELDS))
    _require(not extra, f"unknown brief fields: {', '.join(extra)}")
    for name, allowed in _NESTED_FIELDS.items():
        if isinstance(brief.get(name), dict):
            extra = sorted(set(brief[name]) - set(allowed))
            _require(not extra, f"unknown brief.{name} fields: {', '.join(extra)}")
    _require(brief.get("schema_version") == BRIEF_SCHEMA, f"brief schema_version must be {BRIEF_SCHEMA}")
    product = brief.get("product")
    _require(isinstance(product, dict) and isinstance(product.get("name"), str) and product["name"].strip() != "",
             "brief.product.name is required")
    if "personas_for" in brief:
        _require(brief["personas_for"] in ("persona-qa", "ergonomics", "both"),
                 "brief.personas_for must be persona-qa, ergonomics or both")
    if "audience_questions" in brief:
        questions = brief["audience_questions"]
        _require(isinstance(questions, list) and all(q in AUDIENCE_QUESTIONS for q in questions),
                 f"brief.audience_questions must name: {', '.join(AUDIENCE_QUESTIONS)}")
    budgets = brief.get("budgets", {})
    _require(isinstance(budgets, dict), "brief.budgets must be an object")
    for name in ("per_host", "per_run", "search_queries"):
        if name in budgets:
            _require(type(budgets[name]) is int and budgets[name] >= 1, f"brief.budgets.{name} must be a positive integer")
    if "min_interval_s" in budgets:
        _require(isinstance(budgets["min_interval_s"], (int, float)) and not isinstance(budgets["min_interval_s"], bool),
                 "brief.budgets.min_interval_s must be a number")
    policy = brief.get("access_policy", {})
    _require(isinstance(policy, dict), "brief.access_policy must be an object")
    if "engine_opt_in" in policy:
        _require(isinstance(policy["engine_opt_in"], bool), "brief.access_policy.engine_opt_in must be true or false")
    if "deny_hosts" in policy:
        _require(isinstance(policy["deny_hosts"], list) and all(isinstance(h, str) and h for h in policy["deny_hosts"]),
                 "brief.access_policy.deny_hosts must be a list of host names")
    if "render" in policy:
        _require(policy["render"] in RENDER_MODES, f"brief.access_policy.render must be one of {', '.join(RENDER_MODES)}")
    if "signed_in_communities" in policy:
        communities = policy["signed_in_communities"]
        _require(isinstance(communities, list) and len(communities) <= MAX_COMMUNITIES,
                 f"brief.access_policy.signed_in_communities must be a list of at most {MAX_COMMUNITIES} communities")
        for item in communities:
            _require(isinstance(item, dict) and not set(item) - set(COMMUNITY_FIELDS),
                     "each signed-in community is {host, name, why} with an optional path_prefix")
            for key in ("host", "name", "why"):
                _require(isinstance(item.get(key), str) and item[key].strip() != "",
                         f"a signed-in community needs a non-empty {key}")
            _require(bool(_HOST_NAME.match(item["host"].strip().lower().rstrip("."))),
                     f"signed-in community host {item['host']!r} must be a host name, without a scheme or a path")
            if "path_prefix" in item:
                _require(isinstance(item["path_prefix"], str) and bool(_PATH_PREFIX.match(item["path_prefix"])),
                         "a signed-in community's path_prefix must start with / and hold no spaces, ? or #")
    languages = brief.get("languages", {})
    _require(isinstance(languages, dict), "brief.languages must be an object")


def build_policy(brief: dict | None, overrides: dict) -> dict:
    """Defaults, then the brief, then command-line values. Refuses anything past the ceilings."""
    policy = {**DEFAULTS, "max_wait_s": DEFAULT_MAX_WAIT_S, "accept_language": DEFAULT_ACCEPT_LANGUAGE,
              "deny_hosts": [], "engine_opt_in": False, "render": "host_browser",
              "allow_wayback_for_official": True, "raise_reason": None, "signed_in_communities": []}
    if brief:
        budgets = brief.get("budgets", {})
        for name in ("per_host", "per_run", "search_queries", "min_interval_s"):
            if name in budgets:
                policy[name] = budgets[name]
        if budgets.get("reason"):
            policy["raise_reason"] = str(budgets["reason"])
        access = brief.get("access_policy", {})
        for name in ("engine_opt_in", "deny_hosts", "render", "allow_wayback_for_official"):
            if name in access:
                policy[name] = access[name]
        # Only the user's brief authorises signed-in reading; there is no command-line switch for it.
        policy["signed_in_communities"] = [
            {"host": item["host"].strip().lower().rstrip("."), "name": item["name"].strip(), "why": item["why"].strip(),
             **({"path_prefix": item["path_prefix"]} if item.get("path_prefix") else {})}
            for item in access.get("signed_in_communities", [])]
        languages = brief.get("languages", {})
        if languages.get("primary"):
            secondary = languages.get("secondary") or []
            policy["accept_language"] = accept_language(languages["primary"],
                                                        [secondary] if isinstance(secondary, str) else secondary)
    for name, value in overrides.items():
        if value is not None and value != []:
            policy[name] = value
    policy["deny_hosts"] = sorted({h.strip().lower() for h in policy["deny_hosts"] if h.strip()})
    for name in ("per_host", "per_run"):
        _require(type(policy[name]) is int and policy[name] >= 1, f"{name} must be a positive integer")
        _require(policy[name] <= CEILINGS[name],
                 f"{name} {policy[name]} is above the hard ceiling of {CEILINGS[name]}; this is refused")
        if policy[name] > DEFAULTS[name]:
            _require(bool(policy["raise_reason"] and str(policy["raise_reason"]).strip()),
                     f"raising {name} above {DEFAULTS[name]} needs --reason (it is recorded)")
    policy["min_interval_s"] = float(policy["min_interval_s"])
    _require(policy["min_interval_s"] >= MIN_INTERVAL_FLOOR_S,
             f"min_interval_s cannot be below {MIN_INTERVAL_FLOOR_S:.0f} seconds")
    _require(float(policy["max_wait_s"]) >= 0, "max_wait_s cannot be negative")
    _require(policy["render"] in RENDER_MODES, f"render must be one of {', '.join(RENDER_MODES)}")
    _require(policy["engine_opt_in"] is False,
             "the opt-in engine rung (R4) is not available in this version; it ships with the engine adapter")
    return policy


def create(path: Path | None, policy: dict, *, brief: dict | None = None, routes: dict,
           routes_source: str, clock=time.time) -> Path:
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(clock()))
    run_id = f"run-{stamp}-{secrets.token_hex(3)}"
    path = Path(path) if path else default_root() / run_id
    if path.is_symlink():
        raise RunError("the run folder cannot be a symlink")
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise RunError(f"{path} already exists and is not an empty folder")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)
    (path / "pages").mkdir(mode=0o700)
    _write_new(path / "salt", secrets.token_bytes(32))
    routes_text = json.dumps(routes, ensure_ascii=False, indent=2) + "\n"
    _write_new(path / "routes.json", routes_text.encode("utf-8"))
    brief_sha = None
    if brief is not None:
        raw = (json.dumps(brief, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        _write_new(path / "brief.json", raw)
        brief_sha = hashlib.sha256(raw).hexdigest()
    meta = {"schema_version": RUN_SCHEMA, "run_id": run_id, "created_at": iso(clock()), "version": VERSION,
            "rules_version": RULES_VERSION, "user_agent": USER_AGENT, "policy": policy,
            "brief_sha256": brief_sha, "routes": {"source": routes_source,
                                                   "sha256": hashlib.sha256(routes_text.encode()).hexdigest()},
            "engine_rung": "off", "test_hooks": net.test_hooks_enabled(), "closed_at": None}
    _write_new(path / "run.json", (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    hosts = {"schema_version": HOSTS_SCHEMA, "run": {"docs": 0, "policy_requests": 0}, "hosts": {}, "robots": {}}
    _write_new(path / "hosts.json", (json.dumps(hosts, indent=2) + "\n").encode("utf-8"))
    _write_new(path / "access-ledger.jsonl", b"")
    return path


def _new_host() -> dict:
    return {"docs": 0, "policy_requests": 0, "next_allowed_at": 0.0, "lease": None, "last_request_at": None,
            "crawl_delay": None, "rate_limits": 0, "unreadable_streak": 0, "stopped": None}


class Slot:
    def __init__(self, host: str, token: str, started: float, waited: float):
        self.host, self.token, self.started, self.waited = host, token, started, waited


class Run:
    def __init__(self, path, *, clock=time.time, sleeper=time.sleep, jitter=None):
        self.path = Path(path).expanduser()
        if self.path.is_symlink() or not (self.path / "run.json").is_file():
            raise RunError(f"no run at {self.path}; create one with `ux_research.py start`")
        self.meta = _read_json(self.path / "run.json")
        if self.meta.get("schema_version") != RUN_SCHEMA:
            raise RunError("unsupported run folder")
        self.policy = self.meta["policy"]
        self.clock = clock
        self.sleeper = sleeper
        self.jitter = jitter or (lambda: random.SystemRandom().uniform(0.0, JITTER_MAX_S))
        self._routes = None
        if not self.closed:
            self.purge_pages()

    # ------------------------------------------------------------ basics

    @property
    def closed(self) -> bool:
        return bool(self.meta.get("closed_at"))

    def require_open(self) -> None:
        if self.closed:
            raise RunError("this run is closed; start a new run")

    @property
    def routes(self) -> dict:
        if self._routes is None:
            self._routes = _read_json(self.path / "routes.json")
        return self._routes

    @property
    def salt(self) -> bytes:
        path = self.path / "salt"
        if self.closed or path.is_symlink() or not path.is_file():
            raise RunError("the run's salt is gone (the run is closed)")
        return path.read_bytes()

    def url_key(self, url: str) -> str:
        return hmac.new(self.salt, url.encode("utf-8"), hashlib.sha256).hexdigest()[:24]

    def new_fetch_id(self) -> str:
        return f"F-{secrets.token_hex(6)}"

    def now_iso(self) -> str:
        return iso(self.clock())

    @contextmanager
    def _state(self):
        lock_path = self.path / "state.lock"
        fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            state = _read_json(self.path / "hosts.json")
            before = json.dumps(state, sort_keys=True)
            yield state
            after = json.dumps(state, sort_keys=True)
            if after != before:
                _atomic_write(self.path / "hosts.json", json.dumps(state, indent=1, sort_keys=True) + "\n")
        finally:
            os.close(fd)  # closing the descriptor releases the lock, even after a crash

    @staticmethod
    def _host(state: dict, host: str) -> dict:
        entry = state["hosts"].setdefault(host, _new_host())
        for key, value in _new_host().items():
            entry.setdefault(key, value)
        return entry

    # ------------------------------------------------------------ pacing and budgets

    def host_stop(self, host: str) -> dict | None:
        with self._state() as state:
            entry = state["hosts"].get(host)
            return dict(entry["stopped"]) if entry and entry.get("stopped") else None

    def acquire(self, host: str, kind: str = "doc", max_wait: float = DEFAULT_MAX_WAIT_S) -> Slot:
        """Wait (up to max_wait) for this host's next slot; charge the budget for documents."""
        started = self.clock()
        deadline = started + max(0.0, float(max_wait))
        while True:
            with self._state() as state:
                entry = self._host(state, host)
                if entry["stopped"]:
                    raise HostStopped(host, entry["stopped"])
                now = self.clock()
                if kind == "doc":
                    if state["run"]["docs"] >= self.policy["per_run"]:
                        raise BudgetExceeded("run", host, self.policy["per_run"])
                    if entry["docs"] >= self.policy["per_host"]:
                        raise BudgetExceeded("host", host, self.policy["per_host"])
                lease = entry.get("lease")
                busy = bool(lease and lease["expires"] > now)
                ready_at = float(entry["next_allowed_at"] or 0.0)
                if not busy and ready_at <= now:
                    token = secrets.token_hex(8)
                    entry["lease"] = {"token": token, "expires": now + LEASE_S}
                    entry["last_request_at"] = now
                    if kind == "doc":
                        entry["docs"] += 1
                        state["run"]["docs"] += 1
                    else:
                        entry["policy_requests"] += 1
                        state["run"]["policy_requests"] += 1
                    return Slot(host, token, now, now - started)
                interval = max(self.policy["min_interval_s"], float(entry.get("crawl_delay") or 0.0))
            if busy:
                # Another reader's request is in flight. It usually ends within seconds (the lease is only
                # the crash bound), so poll until this caller's own deadline instead of deferring at once.
                if now + POLL_S > deadline:
                    raise Deferred(max(interval, ready_at - now), host, "another request holds this host")
                self.sleeper(POLL_S)
                continue
            wait = ready_at - now
            if now + wait > deadline:
                raise Deferred(wait, host, "pacing")
            self.sleeper(wait)

    def book_render(self, host: str) -> None:
        """A render made outside the reader (R3 via `ingest`) counts against the host like a read
        and pushes the host's next slot back, so reads and renders share one pace."""
        with self._state() as state:
            entry = self._host(state, host)
            if state["run"]["docs"] >= self.policy["per_run"]:
                raise BudgetExceeded("run", host, self.policy["per_run"])
            if entry["docs"] >= self.policy["per_host"]:
                raise BudgetExceeded("host", host, self.policy["per_host"])
            entry["docs"] += 1
            state["run"]["docs"] += 1
            now = self.clock()
            entry["last_request_at"] = now
            interval = max(self.policy["min_interval_s"], float(entry.get("crawl_delay") or 0.0)) + self.jitter()
            entry["next_allowed_at"] = max(float(entry["next_allowed_at"] or 0.0), now + interval)

    def release(self, slot: Slot) -> None:
        with self._state() as state:
            entry = self._host(state, slot.host)
            if entry.get("lease") and entry["lease"].get("token") == slot.token:
                entry["lease"] = None
            now = self.clock()
            interval = max(self.policy["min_interval_s"], float(entry.get("crawl_delay") or 0.0)) + self.jitter()
            entry["next_allowed_at"] = max(float(entry["next_allowed_at"] or 0.0), now + interval)

    def note_rate_limit(self, host: str, retry_after: float | None, reasons=()) -> dict:
        """First signal: one wait (at most 5 minutes). Second signal, or a longer
        Retry-After: the host stops for the run."""
        with self._state() as state:
            entry = self._host(state, host)
            entry["rate_limits"] += 1
            now = self.clock()
            if entry["rate_limits"] >= 2 or (retry_after is not None and retry_after > MAX_RATE_LIMIT_WAIT_S):
                why = "second rate-limit signal" if entry["rate_limits"] >= 2 else "Retry-After longer than 5 minutes"
                entry["stopped"] = {"class": "rate_limit", "reason": why, "at": iso(now), "signals": list(reasons)[:5]}
                return {"stopped": True, "stop": dict(entry["stopped"])}
            wait = min(retry_after if retry_after is not None else DEFAULT_RATE_LIMIT_WAIT_S, MAX_RATE_LIMIT_WAIT_S)
            entry["next_allowed_at"] = max(float(entry["next_allowed_at"] or 0.0), now + wait)
            return {"stopped": False, "wait_s": wait}

    def stop_host(self, host: str, stop_class: str, reason: str, signals=()) -> dict:
        with self._state() as state:
            entry = self._host(state, host)
            if not entry["stopped"]:
                entry["stopped"] = {"class": stop_class, "reason": reason, "at": self.now_iso(),
                                    "signals": list(signals)[:5]}
            return dict(entry["stopped"])

    def note_outcome(self, host: str, bucket: str) -> dict | None:
        """Track unreadable URLs in a row; the third stops the host (bot_filter_persistent)."""
        with self._state() as state:
            entry = self._host(state, host)
            if bucket == "read":
                entry["unreadable_streak"] = 0
            elif bucket == "unread":
                entry["unreadable_streak"] += 1
                if entry["unreadable_streak"] >= UNREADABLE_STREAK and not entry["stopped"]:
                    entry["stopped"] = {"class": "bot_filter_persistent",
                                        "reason": f"{UNREADABLE_STREAK} unreadable URLs in a row",
                                        "at": self.now_iso(), "signals": []}
                    return dict(entry["stopped"])
            return None

    # ------------------------------------------------------------ robots cache

    def robots_record(self, origin: str) -> dict | None:
        with self._state() as state:
            record = state["robots"].get(origin)
            if record is None:
                return None
            if record["status"] == "unreachable" and self.clock() - record.get("stored_at", 0) > ROBOTS_RETRY_S:
                return None
            return dict(record)

    def store_robots(self, origin: str, host: str, record: dict) -> None:
        with self._state() as state:
            state["robots"][origin] = {**record, "stored_at": self.clock()}
            entry = self._host(state, host)
            pace = [x for x in (record.get("crawl_delay"), record.get("request_rate_s")) if x]
            if pace:
                entry["crawl_delay"] = max([float(entry.get("crawl_delay") or 0.0), *map(float, pace)])

    # ------------------------------------------------------------ ledger

    def log(self, entry: dict) -> None:
        clean = {"at": self.now_iso(), **entry}
        for name in _URL_FIELDS:
            if isinstance(clean.get(name), str):
                clean[name] = mask_url(clean[name])
        if isinstance(clean.get("redirects"), list):
            clean["redirects"] = [{k: (mask_url(v) if k in ("from", "to") else v) for k, v in r.items()}
                                  for r in clean["redirects"] if isinstance(r, dict)]
        line = json.dumps(clean, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        with self._state():
            fd = os.open(self.path / "access-ledger.jsonl", os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW,
                         0o600)
            try:
                os.write(fd, line.encode("utf-8"))
            finally:
                os.close(fd)

    def entries(self) -> list:
        """The whole ledger, read under the lock so a concurrent append is never half-read."""
        path = self.path / "access-ledger.jsonl"
        with self._state():
            raw = path.read_text(encoding="utf-8") if path.is_file() and not path.is_symlink() else ""
        return [json.loads(line) for line in raw.splitlines() if line.strip()]

    def last_outcome(self, url_key: str, *, kind: str = "read") -> dict | None:
        found = None
        for entry in self.entries():
            if entry.get("kind") == "outcome" and entry.get("url_key") == url_key and entry.get("source") == kind:
                found = entry
        return found

    def outcomes(self, url_key: str, *, kind: str) -> list:
        return [e for e in self.entries()
                if e.get("kind") == "outcome" and e.get("url_key") == url_key and e.get("source") == kind]

    # ------------------------------------------------------------ page cache

    def save_page(self, fetch_id: str, text: str) -> Path:
        if not re.fullmatch(r"F-[0-9a-f]{12}", fetch_id):
            raise RunError("invalid fetch id")
        path = self.path / "pages" / f"{fetch_id}.txt"
        _write_new(path, text.encode("utf-8"))
        return path

    def purge_pages(self) -> int:
        pages = self.path / "pages"
        if not pages.is_dir():
            return 0
        removed = 0
        now = self.clock()
        for item in pages.glob("*.txt"):
            if now - item.stat().st_mtime > PAGE_TTL_S:
                item.unlink()
                removed += 1
        return removed

    # ------------------------------------------------------------ close

    def summary(self) -> dict:
        outcomes: dict[str, dict] = {}
        requests: dict[str, dict] = {}
        for entry in self.entries():
            if entry.get("kind") == "outcome":
                outcomes[entry.get("url_key") or entry.get("url")] = entry
            elif entry.get("kind") == "request":
                counts = requests.setdefault(entry.get("host", ""), {"documents": 0, "robots": 0})
                counts["robots" if entry.get("purpose") == "robots" else "documents"] += 1
        with self._state() as state:
            hosts_state = json.loads(json.dumps(state))
        hosts: dict[str, dict] = {}
        totals = {"urls": 0, "read": 0, "deferred": 0, "unread": 0, "stopped": 0, "refused": 0, "out_of_scope": 0}

        def new_row(host: str) -> dict:
            return {"host": host, "urls": 0, "read": 0, "deferred": 0, "unread": 0, "stopped": {}, "refused": 0,
                    "out_of_scope": 0, "rungs_used": {}, "untried": {}, "contexts": {}}

        for outcome in outcomes.values():
            host = outcome.get("host") or ""
            row = hosts.setdefault(host, new_row(host))
            bucket = outcome.get("bucket")
            row["urls"] += 1
            totals["urls"] += 1
            if outcome.get("out_of_scope"):  # private channels are outside the research, not coverage gaps
                row["out_of_scope"] += 1
                totals["out_of_scope"] += 1
            elif bucket == "stopped":
                cls = outcome.get("stop_class") or "unknown"
                row["stopped"][cls] = row["stopped"].get(cls, 0) + 1
                totals["stopped"] += 1
            elif bucket in ("read", "deferred", "unread", "refused"):
                row[bucket] += 1
                totals[bucket] += 1
            if bucket == "read" and outcome.get("rung"):
                row["rungs_used"][outcome["rung"]] = row["rungs_used"].get(outcome["rung"], 0) + 1
            for rung in outcome.get("untried") or []:
                row["untried"][rung] = row["untried"].get(rung, 0) + 1
            if outcome.get("context"):
                row["contexts"][outcome["context"]] = row["contexts"].get(outcome["context"], 0) + 1
        for host in requests:  # hosts reached only through official routes or site alternates
            hosts.setdefault(host, new_row(host))
        for host, row in hosts.items():
            state_row = hosts_state["hosts"].get(host, {})
            row["requests"] = requests.get(host, {"documents": 0, "robots": 0})
            row["host_stop"] = state_row.get("stopped")
            row["robots"] = sorted({r["status"] for origin, r in hosts_state["robots"].items()
                                    if (urlsplit(origin).hostname or "") == host})
        return {"run_id": self.meta["run_id"], "engine_rung": self.meta.get("engine_rung", "off"),
                "test_hooks": self.meta.get("test_hooks", False), "totals": totals,
                "requests": hosts_state["run"], "hosts": [hosts[h] for h in sorted(hosts)],
                "signed_in_communities": [c.get("name") for c in self.policy.get("signed_in_communities", [])],
                "buckets": ["read", "deferred", "unread", "stopped"]}

    def _strip_ledger_urls(self) -> int:
        """Cut every URL in the ledger to its scheme and host. Post URLs, which can carry an author's
        ID, then live only in the bundle's source_ref."""
        path = self.path / "access-ledger.jsonl"
        stripped = 0

        def strip(value):
            nonlocal stripped
            if isinstance(value, dict):
                out = {}
                for key, item in value.items():
                    if key in _LEDGER_URL_KEYS and isinstance(item, str):
                        out[key] = origin_only(item)
                        stripped += 1
                    else:
                        out[key] = strip(item)
                return out
            if isinstance(value, list):
                return [strip(item) for item in value]
            return value

        with self._state():
            if path.is_symlink() or not path.is_file():
                return 0
            lines = [json.dumps(strip(json.loads(line)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                     for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            _atomic_write(path, "".join(line + "\n" for line in lines))
        return stripped

    def close(self) -> dict:
        if self.closed:
            return self.meta.get("summary", {})
        summary = self.summary()
        pages = self.path / "pages"
        removed = len(list(pages.glob("*"))) if pages.is_dir() else 0
        if pages.is_dir():
            shutil.rmtree(pages)
        salt = self.path / "salt"
        if salt.exists():
            salt.unlink()
        urls = self._strip_ledger_urls()
        summary["closed"] = {"page_files_deleted": removed, "salt_deleted": True, "ledger_urls_cut_to_host": urls}
        self.meta["closed_at"] = self.now_iso()
        self.meta["summary"] = summary
        _atomic_write(self.path / "run.json", json.dumps(self.meta, ensure_ascii=False, indent=2) + "\n")
        return summary
