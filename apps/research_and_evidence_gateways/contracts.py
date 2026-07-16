from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping
from urllib.parse import urlsplit, urlunsplit


_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def require_identifier(value: object, name: str) -> str:
    text = str(value).strip()
    if _ID.fullmatch(text) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return text


def require_utc(value: object, name: str) -> str:
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be UTC")
    return text


def require_https_url(value: object) -> str:
    text = str(value).strip()
    parsed = urlsplit(text)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("source_url must use absolute HTTPS")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("source_url must not contain user information")
    if parsed.fragment:
        raise ValueError("source_url must not contain a fragment")
    if parsed.port not in (None, 443):
        raise ValueError("source_url must use the HTTPS default port")
    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("source_url host must not be loopback metadata")
    canonical = urlunsplit(("https", host, parsed.path or "/", parsed.query, ""))
    if canonical != text:
        raise ValueError("source_url must be canonical")
    return canonical


class SourceClass(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class CrossVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True)
class ResearchSource:
    source_id: str
    source_url: str
    source_class: SourceClass
    trust_level: str
    license_policy_id: str
    freshness_policy_id: str
    evidence_id: str
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for name in ("source_id", "trust_level", "license_policy_id", "freshness_policy_id", "evidence_id"):
            object.__setattr__(self, name, require_identifier(getattr(self, name), name))
        object.__setattr__(self, "source_url", require_https_url(self.source_url))
        object.__setattr__(self, "source_class", SourceClass(self.source_class))
        object.__setattr__(self, "trust_level", self.trust_level.upper())
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType({
            "evidence_id": self.evidence_id,
            "freshness_policy_id": self.freshness_policy_id,
            "license_policy_id": self.license_policy_id,
            "operator_review_required": self.operator_review_required,
            "source_class": self.source_class.value,
            "source_id": self.source_id,
            "source_url": self.source_url,
            "trust_level": self.trust_level,
        })


@dataclass(frozen=True)
class ResearchQuery:
    query_id: str
    correlation_id: str
    query_text: str
    requested_at_utc: str
    approved_source_ids: tuple[str, ...]
    peer_host: str = "127.0.0.1"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        for name in ("query_id", "correlation_id"):
            object.__setattr__(self, name, require_identifier(getattr(self, name), name))
        query_text = " ".join(str(self.query_text).strip().split())
        if not query_text or len(query_text) > 512:
            raise ValueError("query_text must contain 1 to 512 normalized characters")
        object.__setattr__(self, "query_text", query_text)
        object.__setattr__(self, "requested_at_utc", require_utc(self.requested_at_utc, "requested_at_utc"))
        sources = tuple(sorted({require_identifier(item, "approved_source_id") for item in self.approved_source_ids}))
        if not sources:
            raise ValueError("approved_source_ids must not be empty")
        object.__setattr__(self, "approved_source_ids", sources)
        if self.peer_host != "127.0.0.1":
            raise ValueError("research query peer must be exactly 127.0.0.1")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
