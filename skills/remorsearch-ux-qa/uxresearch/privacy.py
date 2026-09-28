"""URL masking, PII scrubbing, salted author and thread keys, excerpt limits.

- mask_url removes user:password@ and masks the values of credential-like query
  or fragment parameters (token, key, secret, sig, signature, auth, session,
  code, state, password and their common variants).
- scrub replaces e-mail addresses, Korean phone numbers, resident-registration-
  like numbers, card-like digit runs, @handles, profile URLs and full or partial
  IP addresses such as '(118.235)'. The patterns are imperfect; excerpts are
  also kept short and verifier-sampled later.
- author_key is an HMAC-SHA256 of the run's salt with the platform and handle,
  truncated to 16 hex characters. The handle itself is never written anywhere.
  thread_key is the same over a normalised thread URL.
- Excerpts are at most 300 characters, and at most 5 per source.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import unicodedata
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit

MAX_EXCERPT_CHARS = 300
MAX_EXCERPTS_PER_SOURCE = 5
MASK = "***"
_SECRET_EXACT = frozenset({"token", "key", "secret", "sig", "signature", "auth", "session", "code", "state",
                           "password", "passwd", "pwd", "pw", "apikey", "sid", "otp", "ticket", "nonce",
                           "credential", "credentials", "jsessionid", "phpsessid", "sessid"})
_SECRET_SUFFIX = re.compile(r"(token|secret|signature|password|passwd|sessionid|sessid|apikey)$"
                            r"|(^|[_.-])(key|sig|auth|code|state|session|pass)$")
_TRACKING = re.compile(r"^(utm_[a-z]+|fbclid|gclid|dclid|msclkid|igshid|mc_eid|_ga)$", re.I)

_PATTERNS = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,253}\.[A-Za-z]{2,24}"), "[email]"),
    ("id_number", re.compile(r"(?<!\d)\d{6}\s?-\s?[1-8]\d{6}(?!\d)"), "[id-number]"),
    ("card", re.compile(r"(?<!\d)(?:\d{4}[ -]?){3}\d{1,7}(?!\d)"), "[card]"),
    ("phone", re.compile(r"(?<![\d+])(?:\+?82[ -]?)?0?1[016789][ -.]?\d{3,4}[ -.]?\d{4}(?!\d)"), "[phone]"),
    ("phone", re.compile(r"(?<!\d)0(?:2|[3-6][1-5]|70|50\d?)[ -.)]\d{3,4}[ -.]\d{4}(?!\d)"), "[phone]"),
    ("profile_url", re.compile(r"https?://[^\s<>\"')]+/(?:@[\w.-]+|(?:user|users|u|profile|profiles|member|members|"
                               r"people|author|authors|mypage)/[^\s<>\"')]*)", re.I), "[profile-url]"),
    ("ip", re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"), "[ip]"),
    ("partial_ip", re.compile(r"\(\s*\d{1,3}\.\d{1,3}\s*\)"), "([ip])"),
    ("handle", re.compile(r"(?<![\w@.])@[^\W\d_][\w.]{1,30}"), "[handle]"),
]


def _is_secret(name: str) -> bool:
    lowered = unquote(name).strip().lower()
    return lowered in _SECRET_EXACT or bool(_SECRET_SUFFIX.search(lowered))


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


def scrub(text: str) -> tuple[str, dict]:
    """Replace personal identifiers; returns the scrubbed text and a count per category."""
    counts: dict[str, int] = {}
    for name, pattern, replacement in _PATTERNS:
        text, n = pattern.subn(replacement, text)
        if n:
            counts[name] = counts.get(name, 0) + n
    return text, counts


def _key(salt: bytes, *parts: str) -> str:
    message = "\x1f".join(parts).encode("utf-8")
    return hmac.new(salt, message, hashlib.sha256).hexdigest()[:16]


def author_key(salt: bytes, platform: str, handle: str) -> str:
    if not handle or not handle.strip():
        raise ValueError("handle is empty")
    normalized = unicodedata.normalize("NFC", handle.strip()).casefold()
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
