"""Best-effort redaction of credentials and personal identifiers.

Runs on every document before it is returned to the agent or written to disk.
Patterns are deliberately broad: a false positive costs a look at the source,
a false negative leaks data. Only counts are ever reported, never matched values.
Sources that hold health or HR records should be excluded in sources.yml instead
of relying on redaction.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Callable, Optional, Union

Replacement = Union[None, str, Callable[[re.Match], Optional[str]]]


def _luhn_ok(digits: str) -> bool:
    total, double = 0, False
    for ch in reversed(digits):
        d = int(ch)
        if double:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        double = not double
    return total % 10 == 0


def _card(match: re.Match) -> Optional[str]:
    digits = re.sub(r"\D", "", match.group(0))
    if 13 <= len(digits) <= 19 and _luhn_ok(digits):
        return "[REDACTED:card]"
    return None  # not a card number; leave unchanged


_RULES: list[tuple[str, re.Pattern, Replacement]] = [
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), None),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})"), None),
    ("atlassian_token", re.compile(r"\bATATT3[A-Za-z0-9_\-=]{20,}"), None),
    ("aws_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), None),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), None),
    ("bearer", re.compile(r"(?i)\bbearer\s+(?!\[REDACTED)[A-Za-z0-9\-._~+/]{20,}=*"), "Bearer [REDACTED:bearer]"),
    ("url_credentials", re.compile(r"(?i)\b([a-z][a-z0-9+.\-]*://)[^\s/:@]+:[^\s/@]+@"), r"\1[REDACTED:credentials]@"),
    ("secret", re.compile(
        r"(?i)\b(password|passwd|pwd|secret|client[_-]?secret|api[_-]?key)(\s*[:=]\s*)([\"']?)(?!\[REDACTED)[^\s\"']{3,}\3"),
        r"\1\2[REDACTED:secret]"),
    ("secret", re.compile(
        r"(?i)\b([a-z_\-]*token)(\s*[:=]\s*)([\"']?)(?!\[REDACTED)[^\s\"']{16,}\3"),
        r"\1\2[REDACTED:secret]"),
    ("card", re.compile(r"\b\d(?:[ -]?\d){12,18}\b"), _card),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), None),
    ("aadhaar", re.compile(r"\b[2-9]\d{3}[ -]?\d{4}[ -]?\d{4}\b"), None),
    ("pan", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), None),
    ("passport", re.compile(r"\b[A-Z]\d{7}\b"), None),
    ("driving_licence", re.compile(r"\b[A-Z]{2}[ -]?\d{2}[ -]?(?:19|20)\d{2}[ -]?\d{7}\b"), None),
    ("medical_record", re.compile(
        r"(?i)\b(MRN|medical record (?:number|no\.?)|patient (?:id|name|number))(\s*[:=#]\s*)[^\n]+"),
        r"\1\2[REDACTED:medical_record]"),
]

_EMAIL = ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), None)


def redact(text: str, emails: bool = False) -> tuple[str, dict[str, int]]:
    """Return (redacted_text, counts_by_type)."""
    if not text:
        return text, {}
    counts: Counter[str] = Counter()
    rules = _RULES + ([_EMAIL] if emails else [])
    for name, pattern, repl in rules:
        def _sub(match: re.Match, name=name, repl=repl) -> str:
            if callable(repl):
                out = repl(match)
                if out is None:
                    return match.group(0)
            elif isinstance(repl, str):
                out = match.expand(repl)
            else:
                out = f"[REDACTED:{name}]"
            counts[name] += 1
            return out
        text = pattern.sub(_sub, text)
    return text, dict(counts)
