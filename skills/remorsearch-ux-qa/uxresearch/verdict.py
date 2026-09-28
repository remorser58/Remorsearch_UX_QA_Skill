"""One verdict or stop class per response. HTTP 200 is never success on its own.

Precedence (the first match wins):
  opted_out    robots.txt, TDM reservation, noai, the researcher's deny list
  gone         404/410, or deleted-post words on a thin page
  auth_gate    401/407; a redirect to a login page; a password field plus a login
               word plus thin main content; membership, age or identity words on a
               thin page; for captures, signs of a signed-in view
  paywall      JSON-LD isAccessibleForFree=false, or paywall words on a thin page
  human_check  an interactive challenge widget on a thin or challenge-status page,
               or challenge words with a structural hint (stops the whole host)
  rate_limit   429, 503 with Retry-After, or rate-limit words on a thin page
  geo_block    geo words on a thin page
  legal_block  451, a redirect to a legal-block host, or legal words on a thin page
  js_check     a self-clearing interstitial (escalates)
  bot_filter   403/405/406 or other 4xx without other markers, or block words (escalates)
  js_shell     almost no visible text plus an SPA root or a noscript notice (escalates)
  suspect      no usable text, or a redirect to the site root (escalates)
  ok_weak      readable text
  ok_strong    readable text plus an --expect term, a JSON-LD body or an official feed

Word markers count only when the main content is thin, so a forum post about
captchas, or a page with a login box in its header and a full post below, is
read, not stopped. Structural markers are checked before words.
"""
from __future__ import annotations

import functools
import json
import re
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit

DATA = Path(__file__).resolve().parent / "data"
VERDICTS = ("ok_strong", "ok_weak", "suspect", "js_shell", "js_check", "bot_filter")
STOP_CLASSES = ("auth_gate", "paywall", "human_check", "opted_out", "rate_limit", "geo_block", "legal_block",
                "gone", "budget", "host_stopped")
ESCALATE = frozenset({"js_shell", "js_check", "bot_filter", "suspect"})
OK = frozenset({"ok_strong", "ok_weak"})
HOST_STOPPING = frozenset({"human_check"})
PRESENTATIONS = ("official_route", "honest_ua", "site_alternate", "real_browser", "browser_equivalent_tls")
BUCKETS = ("read", "deferred", "unread", "stopped")


@dataclass
class Verdict:
    verdict: str | None = None
    stop_class: str | None = None
    reasons: list = field(default_factory=list)
    transient: bool = False
    host_wide: bool = False  # a human check backed by structure or a challenge status stops the whole host

    @property
    def ok(self) -> bool:
        return self.verdict in OK

    @property
    def escalate(self) -> bool:
        return self.verdict in ESCALATE


@functools.lru_cache(maxsize=4)
def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def load_markers() -> dict:
    return _load("markers.json")


def _word_pattern(marker: str) -> str:
    if marker.isascii():
        body = r"\s+".join(re.escape(part) for part in marker.split())
        start = r"(?<![a-z0-9])" if marker[:1].isalnum() else ""
        end = r"(?![a-z0-9])" if marker[-1:].isalnum() else ""
        return start + body + end
    return r"\s*".join(re.escape(part) for part in marker.split())


def _alternation(markers) -> re.Pattern | None:
    items = sorted({m for m in markers if m}, key=len, reverse=True)
    if not items:
        return None
    return re.compile("|".join(_word_pattern(m) for m in items), re.I)


def _langs(section: dict | None) -> list:
    if not section:
        return []
    return [m for values in section.values() for m in values]


class _Compiled:
    def __init__(self, markers: dict):
        self.raw = markers
        self.thresholds = markers["thresholds"]
        self.words = {}
        for key in ("login", "membership", "age_identity", "paywall", "deleted", "rate_limit", "geo", "legal",
                    "bot_filter", "human_check", "js_check"):
            self.words[key] = _alternation(_langs(markers[key].get("words")))
        self.noscript = _alternation(_langs(markers["spa_root"]["noscript_words"]))
        self.promotion = _alternation(_langs(markers["promotion"]))
        self.human_src = _alternation(markers["human_check"]["src"])
        self.human_ident = _alternation(markers["human_check"]["idents"])
        self.human_input = _alternation(markers["human_check"]["inputs"])
        self.js_src = _alternation(markers["js_check"]["src"])
        self.js_ident = _alternation(markers["js_check"]["idents"])
        self.logout_href = _alternation(markers["logged_in"]["href"])
        self.logged_in_lines = {" ".join(x.lower().split()) for x in _langs(markers["logged_in"]["lines"])}
        self.login_paths = [re.compile(p, re.I) for p in markers["login"]["url_path"]]
        self.legal_hosts = frozenset(markers["legal"].get("hosts", []))
        self.spa_ids = frozenset(markers["spa_root"]["ids"])
        self.spa_attrs = frozenset(markers["spa_root"]["attrs"])
        self.spa_tags = frozenset(markers["spa_root"]["tags"])
        self.injection = {
            name: [re.compile(p, re.I | re.S) for p in _langs(section)]
            for name, section in markers["injection"].items()
        }


@functools.lru_cache(maxsize=1)
def compiled() -> _Compiled:
    return _Compiled(load_markers())


_SENTENCE_END = ".!?\n\u3002\u2026"
_QUOTE_PAIRS = (('"', '"'), ("'", "'"), ("\u201c", "\u201d"), ("\u2018", "\u2019"), ("\u300c", "\u300d"),
                ("\u300e", "\u300f"))
_HANGUL = re.compile("[\uac00-\ud7a3]")


def _reported(text: str, start: int, end: int) -> bool:
    """True when a marker is quoted or asked about ('...'라고 떠요, ...나요?): a post talking about
    a notice, not the notice itself."""
    left = max(text.rfind(ch, 0, start) for ch in _SENTENCE_END) + 1
    rights = [i for i in (text.find(ch, end) for ch in _SENTENCE_END) if i != -1]
    right = min(rights) if rights else len(text)
    before, after = text[left:start], text[end:right]
    for opening, closing in _QUOTE_PAIRS:
        if opening == closing:
            if before.count(opening) % 2 == 1 and opening in after:
                return True
        elif before.rfind(opening) > before.rfind(closing) and closing in after:
            return True
    return right < len(text) and text[right] == "?" and bool(_HANGUL.search(text[start:end]))


def _hits(pattern: re.Pattern | None, text: str, limit: int = 5, *, notices_only: bool = False) -> list[str]:
    if pattern is None or not text:
        return []
    found: list[str] = []
    for match in pattern.finditer(text):
        if notices_only and _reported(text, match.start(), match.end()):
            continue
        value = " ".join(match.group(0).split())
        if value.lower() not in (f.lower() for f in found):
            found.append(value)
        if len(found) >= limit:
            break
    return found


def _any_hit(pattern: re.Pattern | None, values) -> list[str]:
    if pattern is None:
        return []
    found = []
    for value in values:
        match = pattern.search(value)
        if match:
            found.append(match.group(0))
            if len(found) >= 3:
                break
    return found


def host_matches(host: str, patterns) -> bool:
    host = host.lower().rstrip(".")
    for pattern in patterns:
        pattern = pattern.lower()
        if pattern.startswith("*."):
            if host.endswith(pattern[1:]) and host != pattern[2:]:
                return True
        elif host == pattern or host.endswith("." + pattern):
            return True
    return False


def is_login_url(url: str, login_hosts=()) -> bool:
    parts = urlsplit(url)
    if host_matches(parts.hostname or "", login_hosts):
        return True
    target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    return any(p.search(target) for p in compiled().login_paths)


def is_legal_block_url(url: str) -> bool:
    return host_matches(urlsplit(url).hostname or "", compiled().legal_hosts)


def _structure_human(page) -> list[str]:
    c = compiled()
    reasons = [f"src:{x}" for x in _any_hit(c.human_src, page.srcs)]
    reasons += [f"ident:{x}" for x in _any_hit(c.human_ident, list(page.ids) + list(page.classes))]
    reasons += [f"input:{x}" for x in _any_hit(c.human_input, page.input_names)]
    if page.challenge_interactive:
        reasons.append("capture:challenge.interactive")
    return reasons


def _structure_js(page) -> list[str]:
    c = compiled()
    reasons = [f"src:{x}" for x in _any_hit(c.js_src, page.srcs)]
    reasons += [f"ident:{x}" for x in _any_hit(c.js_ident, list(page.ids) + list(page.classes))]
    return reasons


def _spa_root(page) -> list[str]:
    c = compiled()
    found = [f"id:{x}" for x in sorted(page.ids & c.spa_ids)]
    found += [f"attr:{x}" for x in sorted(page.attrs & c.spa_attrs)]
    found += [f"tag:{x}" for x in sorted(page.tags & c.spa_tags)]
    return found


def _logged_in(page) -> list[str]:
    c = compiled()
    reasons = [f"href:{x}" for x in _any_hit(c.logout_href, page.hrefs)]
    limit = c.thresholds["standalone_line_chars"]
    for line in page.visible_text.splitlines():
        value = " ".join(line.lower().split())
        if 0 < len(value) <= limit and value in c.logged_in_lines:
            reasons.append(f"line:{value}")
            break
    return reasons


def promotion_flags(text: str) -> list[str]:
    return _hits(compiled().promotion, text, limit=10)


def _stop(stop_class: str, reasons: list) -> Verdict:
    return Verdict(stop_class=stop_class, reasons=reasons)


def classify(*, status: int, headers: dict, page, requested_url: str, final_url: str | None = None,
             redirect_urls=(), expect=(), optouts=(), login_hosts=(), capture: bool = False) -> Verdict:
    """Classify one response (or one render capture when `capture` is true)."""
    c = compiled()
    t = c.thresholds
    final_url = final_url or requested_url
    if optouts:
        return _stop("opted_out", list(optouts))
    main = page.main_chars if page is not None else 0
    thin = main < t["thin_main_chars"]
    thin_note = f"thin_main:{main}"
    notice = ""
    if page is not None:  # what a visitor sees; a JSON-LD body never hides or causes a stop
        notice = "\n".join([page.title, page.visible_text[:20000], *page.alerts, page.noscript_text])

    def words(key: str) -> list[str]:
        return _hits(c.words[key], notice, notices_only=True) if thin else []

    # gone
    if status in (404, 410):
        return _stop("gone", [f"status:{status}"])
    if hit := words("deleted"):
        return _stop("gone", [f"word:{w}" for w in hit] + [thin_note])
    # auth_gate
    if status in (401, 407):
        return _stop("auth_gate", [f"status:{status}"])
    requested_login = is_login_url(requested_url, login_hosts)
    for target in [*redirect_urls, final_url]:
        if target and target != requested_url and not requested_login and is_login_url(target, login_hosts):
            return _stop("auth_gate", ["redirect:login_page"])
    if page is not None and page.login_form and thin:
        login_words = _hits(c.words["login"], notice)
        if login_words:
            return _stop("auth_gate", ["structure:password_field", f"word:{login_words[0]}", thin_note])
    for key in ("membership", "age_identity"):
        if hit := words(key):
            return _stop("auth_gate", [f"word:{w}" for w in hit] + [thin_note])
    if capture and page is not None and (signed_in := _logged_in(page)):
        return _stop("auth_gate", ["capture:signed_in_view", *signed_in])
    # paywall
    if page is not None and page.jsonld_free is False:
        return _stop("paywall", ["structure:json_ld_isAccessibleForFree_false"])
    if hit := words("paywall"):
        return _stop("paywall", [f"word:{w}" for w in hit] + [thin_note])
    # human_check
    if page is not None:
        structure = _structure_human(page)
        interactive = [r for r in structure if not r.startswith("input:")] or \
            (["capture:challenge.interactive"] if page.challenge_interactive else [])
        if interactive and (thin or status in (403, 429, 503)):
            return Verdict(stop_class="human_check", reasons=interactive + [thin_note], host_wide=True)
        hint = structure or status >= 400 or main < t["suspect_main_chars"]
        if hint and (hit := words("human_check")):
            backed = bool(structure) or status >= 400
            return Verdict(stop_class="human_check", host_wide=backed,
                           reasons=[f"word:{w}" for w in hit] + structure + [thin_note] + ([] if backed else ["word_only"]))
    # rate_limit
    if status == 429:
        return _stop("rate_limit", ["status:429"])
    if status == 503 and headers.get("retry-after"):
        return _stop("rate_limit", ["status:503", "header:retry-after"])
    if hit := words("rate_limit"):
        return _stop("rate_limit", [f"word:{w}" for w in hit] + [thin_note])
    # geo_block
    if hit := words("geo"):
        return _stop("geo_block", [f"word:{w}" for w in hit] + [thin_note])
    # legal_block
    if status == 451:
        return _stop("legal_block", ["status:451"])
    for target in [*redirect_urls, final_url]:
        if target and is_legal_block_url(target):
            return _stop("legal_block", ["redirect:legal_block_host"])
    if hit := words("legal"):
        return _stop("legal_block", [f"word:{w}" for w in hit] + [thin_note])
    # js_check
    if page is not None and thin:
        structure = _structure_js(page)
        hit = words("js_check")
        if structure or hit:
            return Verdict("js_check", reasons=structure + [f"word:{w}" for w in hit] + [thin_note])
    if 500 <= status < 600 or status == 408:
        return Verdict(transient=True, reasons=[f"status:{status}"])
    # bot_filter
    if status >= 400:
        return Verdict("bot_filter", reasons=[f"status:{status}"] + [f"word:{w}" for w in words("bot_filter")])
    if hit := words("bot_filter"):
        return Verdict("bot_filter", reasons=[f"word:{w}" for w in hit] + [thin_note])
    if page is None:
        return Verdict("suspect", reasons=[f"status:{status}", "no_page"])
    rescued = page.extraction_source in ("json_ld", "feed", "oembed")
    # js_shell (a render capture has already run the page's scripts, so it is never a shell)
    if not rescued and not capture and page.visible_chars < t["shell_visible_chars"]:
        roots = _spa_root(page)
        notices = _hits(c.noscript, page.noscript_text)
        if roots or notices:
            return Verdict("js_shell", reasons=roots + [f"noscript:{w}" for w in notices] +
                           [f"visible:{page.visible_chars}"])
    # suspect
    if not 200 <= status < 300:
        return Verdict("suspect", reasons=[f"status:{status}"])
    if main < t["suspect_main_chars"] and not rescued:
        return Verdict("suspect", reasons=[thin_note])
    requested_path = urlsplit(requested_url).path or "/"
    if final_url != requested_url and (urlsplit(final_url).path or "/") == "/" and requested_path != "/":
        return Verdict("suspect", reasons=["redirect:site_root"])
    # ok
    strong = []
    lowered = page.text.lower()
    strong += [f"expect:{term}" for term in expect if term and term.lower() in lowered][:3]
    if page.jsonld_body_chars:
        strong.append("json_ld_body")
    if page.extraction_source in ("feed", "oembed"):
        strong.append(f"official:{page.extraction_source}")
    if strong:
        return Verdict("ok_strong", reasons=strong)
    return Verdict("ok_weak", reasons=[f"main:{main}"] + (["expect_missing"] if expect else []))


def robots_challenge(status: int | None, page) -> bool:
    """A challenge page served instead of robots.txt (recorded as unavailable_bot_filtered)."""
    if page is None or status is None:
        return False
    c = compiled()
    thin = page.main_chars < c.thresholds["thin_main_chars"]
    if _structure_human(page) or (thin and _structure_js(page)):
        return True
    if not thin:
        return False
    notice = "\n".join([page.title, page.visible_text[:20000]])
    if any(_hits(c.words[k], notice) for k in ("human_check", "js_check", "bot_filter")):
        return True
    return status in (401, 403, 406) and page.visible_chars > 0


def retry_after_seconds(value: str | None, now: float) -> float | None:
    if not value:
        return None
    value = value.strip()
    if value.isdigit():
        return float(value)
    try:
        moment = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    if moment is None:
        return None
    return max(0.0, moment.timestamp() - now)
