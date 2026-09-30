"""URL masking, PII scrubbing, salted author and thread keys, excerpt limits.

- mask_url removes user:password@ and masks the values of credential-like query
  or fragment parameters (token, key, secret, sig, signature, auth, session,
  code, state, password and their common variants).
- scrub replaces e-mail addresses, Korean phone numbers (with or without spaces
  around the dashes, and area codes in brackets), resident-registration-like
  numbers (also with the last digits masked, such as '900101-1******'),
  card-like digit runs, bank-account-like numbers (dashed groups of 10 to 16
  digits, or a digit run after an account word such as '계좌'), @handles
  (including dots and hyphens), profile URLs and full or partial IP addresses
  such as '(118.235)'. Profile and post URLs that carry an author's name come
  from the data files: hosts whose first path segment or subdomain is the author
  (data/suffixes.json path_hosted and hosting_suffixes, and routes whose
  author_from is path_segment or subdomain), and a route's profile_paths (such
  as a channel path) on its hosts. `read` and `ingest` scrub all page text before it is printed,
  saved or scanned, so the planned merge verbatim check compares against the
  scrubbed text. The patterns are imperfect; excerpts are also kept short and
  verifier-sampled later.
- origin_only keeps only a URL's scheme and host, for records kept after a run closes.
- author_key is an HMAC-SHA256 of the run's salt with the platform and handle,
  truncated to 16 hex characters. The handle itself is never written anywhere.
  Before keying, the handle is trimmed, NFKC-normalised and case-folded, and a
  trailing partial-IP group such as '(118.235)' is split off. A handle that
  carried such a group (a logged-out poster) or that is a default anonymous
  nickname (data/markers.json anonymous_handles, such as 'ㅇㅇ') is refused: it
  is not an identity, so such posts are counted by thread key instead.
  thread_key is the same over a normalised thread URL.
- Excerpts are at most 300 characters, and at most 5 per source.
"""
from __future__ import annotations

import functools
import hashlib
import hmac
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit

from . import verdict

DATA = Path(__file__).resolve().parent / "data"
MAX_EXCERPT_CHARS = 300
MAX_EXCERPTS_PER_SOURCE = 5
MASK = "***"
_SECRET_EXACT = frozenset({"token", "key", "secret", "sig", "signature", "auth", "session", "code", "state",
                           "password", "passwd", "pwd", "pw", "apikey", "sid", "otp", "ticket", "nonce",
                           "credential", "credentials", "jsessionid", "phpsessid", "sessid"})
_SECRET_SUFFIX = re.compile(r"(token|secret|signature|password|passwd|sessionid|sessid|apikey)$"
                            r"|(^|[_.-])(key|sig|auth|code|state|session|pass)$")
_TRACKING = re.compile(r"^(utm_[a-z]+|fbclid|gclid|dclid|msclkid|igshid|mc_eid|_ga)$", re.I)

_SEP = r"(?:\s?[-.]\s?|\s)"  # a dash or dot with optional spaces around it, or one space
_URL_TAIL = r"[^\s<>\"')]*"
ACCOUNT_DIGITS = (10, 16)  # digits in a bank-account-like number


def _account(match: re.Match) -> str | None:
    """The replacement for an account-like number, or None when its digit count does not fit."""
    number = match.group("number") if "number" in match.re.groupindex else match.group(0)
    digits = sum(ch.isdigit() for ch in number)
    if not ACCOUNT_DIGITS[0] <= digits <= ACCOUNT_DIGITS[1]:
        return None
    return match.group(0).replace(number, "[account]")


_PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,24}"), "[email]"),
    ("id_number", re.compile(r"(?<!\d)\d{6}(?:\s?-\s?|\s)[1-8]\d{6}(?!\d)"), "[id-number]"),
    ("id_number", re.compile(r"(?<!\d)\d{6}\s?-\s?[1-8][*＊xX●○]{6}"), "[id-number]"),
    ("card", re.compile(r"(?<!\d)(?:\d{4}[ -]?){3}\d{1,7}(?!\d)"), "[card]"),
    ("phone", re.compile(r"(?<![\d+])(?:\+?82[ -]?)?0?1[016789]" + _SEP + r"?\d{3,4}" + _SEP + r"?\d{4}(?!\d)"), "[phone]"),
    ("phone", re.compile(r"(?<!\d)\(?0(?:2|[3-6][1-5]|70|50\d?)(?:\)\s?|" + _SEP + r")\d{3,4}" + _SEP + r"\d{4}(?!\d)"),
     "[phone]"),
    ("account", re.compile(r"(?:계좌|입금|송금|account)[^\d\n]{0,16}?(?P<number>\d[\d -]{8,22}\d)(?![\d-])", re.I),
     _account),
    ("account", re.compile(r"(?<![\d.-])\d{2,6}(?:-\d{2,7}){2,3}(?![\d-]|\.\d)"), _account),
    ("profile_url", re.compile(r"https?://[^\s<>\"')]+/(?:@[\w.-]+|(?:user|users|u|profile|profiles|member|members|"
                               r"people|author|authors|mypage)/" + _URL_TAIL + ")", re.I), "[profile-url]"),
    ("ip", re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?!\d|\.\d)"), "[ip]"),
    ("partial_ip", re.compile(r"\(\s*\d{1,3}\.\d{1,3}\s*\)"), "([ip])"),
    ("handle", re.compile(r"(?<![\w@.])@(?=[\w.-]*[^\W\d_])\w[\w.-]{1,30}"), "[handle]"),
]


@functools.lru_cache(maxsize=1)
def _author_urls() -> re.Pattern | None:
    """URLs whose first path segment or subdomain names the author, from the data files only."""
    suffixes = json.loads((DATA / "suffixes.json").read_text(encoding="utf-8"))
    routes = json.loads((DATA / "routes.json").read_text(encoding="utf-8"))
    path_hosts = {item["host"] for item in suffixes.get("path_hosted", []) if item.get("host")}
    path_hosts |= set(suffixes.get("profile_hosts", []))
    sub_hosts = set(suffixes.get("hosting_suffixes", []))
    for platform in routes.get("platforms", []):
        for host in platform.get("hosts", []):
            if platform.get("author_from") == "subdomain" and host.startswith("*."):
                sub_hosts.add(host[2:])
            elif platform.get("author_from") == "path_segment" and not host.startswith("*."):
                path_hosts.add(host)
    parts = [r"(?:www\.|m\.)?" + re.escape(h) + r"/[^\s<>\"'/)]+" + _URL_TAIL
             for h in sorted(path_hosts, key=len, reverse=True)]
    parts += [r"[a-z0-9-]+(?:\.[a-z0-9-]+)*\." + re.escape(h) + r"(?![a-z0-9.-])(?:/" + _URL_TAIL + ")?"
              for h in sorted(sub_hosts, key=len, reverse=True)]
    for platform in routes.get("platforms", []):  # channel or profile paths, such as /channel/<id>
        paths = [p for p in platform.get("profile_paths") or [] if isinstance(p, str) and re.fullmatch(r"[\w.-]+", p)]
        if paths:
            parts += [re.escape(h) + r"/(?:" + "|".join(re.escape(p) for p in paths) + r")/[^\s<>\"'/)]+" + _URL_TAIL
                      for h in platform.get("hosts", []) if isinstance(h, str) and not h.startswith("*.")]
    return re.compile(r"https?://(?:" + "|".join(parts) + ")", re.I) if parts else None


def _is_secret(name: str) -> bool:
    lowered = unquote(name).strip().lower()
    return lowered in _SECRET_EXACT or bool(_SECRET_SUFFIX.search(lowered))


def masks_param(name: str) -> bool:
    """True when mask_url masks the value of a query or fragment parameter with this name."""
    return _is_secret(name)


def _mask_pairs(value: str) -> str:
    pieces = []
    for piece in value.split("&"):
        name, sep, _ = piece.partition("=")
        pieces.append(f"{name}={MASK}" if sep and _is_secret(name) else piece)
    return "&".join(pieces)


def mask_url(url: str) -> str:
    """Drop credentials and mask secret-looking parameter values; keep names for diagnosis."""
    if not isinstance(url, str):
        return ""
    try:
        parts = urlsplit(url)
    except ValueError:
        return "[unparseable-url]"
    netloc = parts.netloc
    if "@" in netloc:
        netloc = f"{MASK}@{netloc.rsplit('@', 1)[1]}"
    return urlunsplit((parts.scheme, netloc, parts.path, _mask_pairs(parts.query) if parts.query else "",
                       _mask_pairs(parts.fragment) if "=" in parts.fragment else parts.fragment))


def origin_only(url: str) -> str:
    """scheme://host[:port] of a URL: what a closed run keeps instead of a post URL."""
    if not isinstance(url, str) or not url:
        return ""
    try:
        parts = urlsplit(url)
        netloc = parts.netloc.rsplit("@", 1)[-1]
    except ValueError:
        return "[unparseable-url]"
    return f"{parts.scheme}://{netloc}" if parts.scheme and netloc else "[url]"


def scrub(text: str) -> tuple[str, dict]:
    """Replace personal identifiers; returns the scrubbed text and a count per category."""
    counts: dict[str, int] = {}
    authors = _author_urls()
    if authors is not None:
        text, n = authors.subn("[profile-url]", text)
        if n:
            counts["profile_url"] = n
    for name, pattern, replacement in _PATTERNS:
        if callable(replacement):  # a check decides whether the match is an identifier at all
            hits = 0

            def replace(match: re.Match, _check=replacement) -> str:
                nonlocal hits
                value = _check(match)
                if value is None:
                    return match.group(0)
                hits += 1
                return value

            text = pattern.sub(replace, text)
            n = hits
        else:
            text, n = pattern.subn(replacement, text)
        if n:
            counts[name] = counts.get(name, 0) + n
    return text, counts


def _key(salt: bytes, *parts: str) -> str:
    message = "\x1f".join(parts).encode("utf-8")
    return hmac.new(salt, message, hashlib.sha256).hexdigest()[:16]


_TRAILING_IP = re.compile(r"\s*\(\s*\d{1,3}(?:\s*\.\s*\d{1,3}){1,3}\s*\)\s*$")
USE_THREAD_KEY = "use --thread-url for a thread key instead"


def normalize_handle(handle: str) -> tuple[str, bool]:
    """(the handle trimmed and NFKC-normalised without a trailing partial-IP group, whether it had one).
    'ㅇㅇ(118.235)' becomes ('ㅇㅇ', True)."""
    value = unicodedata.normalize("NFKC", handle or "").strip()
    stripped = _TRAILING_IP.sub("", value)
    return stripped.strip(), stripped != value


def check_handle(handle: str) -> str:
    """The normalised handle, or ValueError when it is not an identity: empty, carrying a partial IP
    address (a logged-out poster, who can type any nickname) or a default anonymous nickname."""
    value, had_ip = normalize_handle(handle)
    if had_ip:
        raise ValueError("a handle with a partial IP address, such as 'ㅇㅇ(118.235)', is a logged-out poster, "
                         f"not an identity; {USE_THREAD_KEY}")
    if not value:
        raise ValueError("handle is empty")
    if verdict.anonymous_handle(value):  # data/markers.json anonymous_handles
        raise ValueError(f"a default anonymous nickname is not an identity; {USE_THREAD_KEY}")
    return value


def author_key(salt: bytes, platform: str, handle: str) -> str:
    normalized = check_handle(handle).casefold()
    return _key(salt, "author", platform.strip().lower(), normalized)


def normalize_thread_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    for prefix in ("www.", "m."):
        if host.startswith(prefix):
            host = host[len(prefix):]
    query = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if not _TRACKING.match(k))
    path = (parts.path or "/").rstrip("/") or "/"
    return urlunsplit(("", host, quote(unquote(path), safe="/%:@!$&'()*+,;=-._~"), urlencode(query), ""))


def thread_key(salt: bytes, url: str) -> str:
    return _key(salt, "thread", normalize_thread_url(url))


def check_excerpt(text: str) -> str:
    """Return the NFC excerpt, or raise ValueError when it is longer than the limit."""
    value = unicodedata.normalize("NFC", text)
    if len(value) > MAX_EXCERPT_CHARS:
        raise ValueError(f"excerpt is {len(value)} characters; the limit is {MAX_EXCERPT_CHARS}")
    return value
