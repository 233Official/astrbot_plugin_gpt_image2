"""用户可见文本的隐私脱敏工具。"""

from __future__ import annotations

import re
from urllib.parse import urlparse


_URL_RE = re.compile(r"https?://[^\s'\"`<>]+", re.IGNORECASE)
_HOST_PORT_RE = re.compile(
    r"(?<![\w.-])"
    r"(?:"
    r"localhost|"
    r"(?:\d{1,3}\.){3}\d{1,3}|"
    r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"
    r")"
    r":\d{2,5}"
)
_TRAILING_PUNCTUATION = "，。；、)）]】>}>'\"`"


def redact_url_for_user(text: object) -> str:
    """Redact URL host/IP/port in user-visible text while keeping useful path."""
    raw = str(text or "")
    if not raw:
        return raw

    redacted = _URL_RE.sub(_redact_url_match, raw)
    return _HOST_PORT_RE.sub("***", redacted)


def _redact_url_match(match: re.Match[str]) -> str:
    token = match.group(0)
    suffix = ""
    while token and token[-1] in _TRAILING_PUNCTUATION:
        suffix = token[-1] + suffix
        token = token[:-1]
    return _redact_single_url(token) + suffix


def _redact_single_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        if parsed.scheme:
            path = parsed.path or ""
            return f"{parsed.scheme}://***{path}"
    except Exception:
        pass
    return "***"
