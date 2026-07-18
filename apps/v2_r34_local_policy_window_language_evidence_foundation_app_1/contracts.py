from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
)


DOCUMENT_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")
WINDOW_TYPES = (
    "TWO_SESSIONS",
    "JULY_POLITBURO",
    "DECEMBER_CEWC",
    "OTHER_REGISTERED_POLICY",
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _hash(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _sha(value: object, name: str) -> str:
    normalized = str(value).strip().lower()
    if _SHA256.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a sha256 digest")
    return normalized


def _bps(numerator: int, denominator: int) -> int:
    if denominator == 0:
        return 0
    return int(
        ((Decimal(numerator) / Decimal(denominator)) * Decimal("10000")).quantize(
            Decimal("1"), rounding=ROUND_HALF_EVEN
        )
    )


@dataclass(frozen=True)
class RegisteredPolicyDocumentObservation:
    document_id: str
    document_series_id: str
    market: str
    horizon: str
    window_type: str
    published_at_utc: str
    available_at_utc: str
    content_sha256: str | None
    canonical_tokens: tuple[str, ...]
    source_event: InstitutionalCalendarEvent
    document_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    document_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("document_id", "document_series_id", "market", "horizon"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        window = str(self.window_type).strip().upper()
        if window not in WINDOW_TYPES:
            raise ValueError("window_type is not registered")
        object.__setattr__(self, "window_type", window)
        for name in ("published_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if (
            not isinstance(self.source_event, InstitutionalCalendarEvent)
            or self.source_event.event_type != "POLICY_MEETING"
        ):
            raise ValueError("policy document requires registered R23 POLICY_MEETING evidence")
        if instant(self.available_at_utc) < max(
            instant(self.published_at_utc), instant(self.source_event.ingested_at_utc)
        ):
            raise ValueError("document availability cannot precede evidence")
        state = str(self.document_state).strip().upper()
        if state not in DOCUMENT_STATES:
            raise ValueError("document_state is not registered")
        object.__setattr__(self, "document_state", state)
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields)
        object.__setattr__(self, "missing_fields", missing)
        if state == "OBSERVED":
            digest = _sha(self.content_sha256, "content_sha256")
            tokens = tuple(sorted(identifier(item, "canonical_token") for item in self.canonical_tokens))
            if not tokens or len(set(tokens)) != len(tokens) or missing:
                raise ValueError("observed policy document requires unique canonical tokens")
            object.__setattr__(self, "content_sha256", digest)
            object.__setattr__(self, "canonical_tokens", tokens)
        else:
            if self.content_sha256 is not None or self.canonical_tokens or not missing:
                raise ValueError("non-observed document requires empty content and missing_fields")
            tokens = ()
            object.__setattr__(self, "canonical_tokens", tokens)
        if self.operator_registered is not True:
            raise ValueError("policy document requires Operator registration")
        object.__setattr__(
            self,
            "document_hash",
            _hash(
                {
                    "available_at_utc": self.available_at_utc,
                    "content_sha256": self.content_sha256,
                    "document_id": self.document_id,
                    "document_series_id": self.document_series_id,
                    "market": self.market,
                    "missing_fields": list(missing),
                    "published_at_utc": self.published_at_utc,
                    "source_event_hash": self.source_event.record_hash,
                    "state": state,
                    "tokens": list(tokens),
                    "window_type": window,
                }
            ),
        )


@dataclass(frozen=True)
class PolicyLanguageChangeRecord:
    record_id: str
    prior_document: RegisteredPolicyDocumentObservation
    current_document: RegisteredPolicyDocumentObservation
    available_at_utc: str
    semantic_direction: bool = False
    industry_benefit: bool = False
    policy_causation: bool = False
    automatic_taxonomy_mapping: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    added_token_count: int = field(init=False)
    removed_token_count: int = field(init=False)
    retained_token_count: int = field(init=False)
    union_token_count: int = field(init=False)
    novelty_bps: int = field(init=False)
    retention_bps: int = field(init=False)
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", identifier(self.record_id, "record_id"))
        documents = (self.prior_document, self.current_document)
        if any(
            not isinstance(item, RegisteredPolicyDocumentObservation)
            or item.document_state != "OBSERVED"
            for item in documents
        ):
            raise ValueError("language change requires observed policy documents")
        if (
            self.prior_document.document_series_id
            != self.current_document.document_series_id
            or self.prior_document.window_type != self.current_document.window_type
            or self.prior_document.market != self.current_document.market
        ):
            raise ValueError("policy documents require a common comparison identity")
        if instant(self.current_document.available_at_utc) <= instant(
            self.prior_document.available_at_utc
        ):
            raise ValueError("current document must be available after prior document")
        object.__setattr__(
            self, "available_at_utc", utc(self.available_at_utc, "available_at_utc")
        )
        if instant(self.available_at_utc) < instant(self.current_document.available_at_utc):
            raise ValueError("record availability cannot precede current document")
        prior, current = set(self.prior_document.canonical_tokens), set(
            self.current_document.canonical_tokens
        )
        added, removed, retained, union = current - prior, prior - current, prior & current, prior | current
        metrics = (len(added), len(removed), len(retained), len(union))
        for name, value in zip(
            ("added_token_count", "removed_token_count", "retained_token_count", "union_token_count"),
            metrics,
        ):
            object.__setattr__(self, name, value)
        novelty = _bps(len(added | removed), len(union))
        retention = _bps(len(retained), len(prior))
        object.__setattr__(self, "novelty_bps", novelty)
        object.__setattr__(self, "retention_bps", retention)
        if self.semantic_direction:
            raise ValueError("token changes cannot claim semantic direction")
        if self.industry_benefit:
            raise ValueError("token changes cannot claim industry benefit")
        if self.policy_causation:
            raise ValueError("token changes cannot prove policy causation")
        if self.automatic_taxonomy_mapping:
            raise ValueError("automatic taxonomy mapping is prohibited")
        if self.factor_activated:
            raise ValueError("policy evidence cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("language change requires Operator registration")
        object.__setattr__(
            self,
            "record_hash",
            _hash(
                {
                    "available_at_utc": self.available_at_utc,
                    "current_document_hash": self.current_document.document_hash,
                    "metrics": [*metrics, novelty, retention],
                    "prior_document_hash": self.prior_document.document_hash,
                    "record_id": self.record_id,
                }
            ),
        )
