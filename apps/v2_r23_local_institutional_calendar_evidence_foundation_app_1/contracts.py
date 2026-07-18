from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)


EVENT_TYPES = (
    "CENTRAL_BANK_DECISION",
    "CORPORATE_ACTION",
    "EARNINGS_DISCLOSURE",
    "EXCHANGE_RULE_CHANGE",
    "HOLIDAY",
    "INDEX_FUTURES_EVENT",
    "MACRO_RELEASE",
    "MARKET_STRUCTURE_EVENT",
    "POLICY_MEETING",
    "PROTOCOL_EVENT",
)
SOURCE_KINDS = ("LICENSED", "OFFICIAL")
REVISION_STATES = ("CANCELLED", "ORIGINAL", "REVISED")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha256_text(value: object, name: str) -> str:
    normalized = str(value).strip().lower()
    if _SHA256.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


def _hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class InstitutionalCalendarSource:
    source_id: str
    source_kind: str
    registered_artifact_id: str
    artifact_version: str
    license_id: str
    permitted_use: str
    retention_days: int
    operator_confirmed: bool = True
    local_artifact_only: bool = True
    redistribution_allowed: bool = False
    network_retrieval_allowed: bool = False

    def __post_init__(self) -> None:
        for name in (
            "source_id",
            "registered_artifact_id",
            "artifact_version",
            "license_id",
            "permitted_use",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        source_kind = str(self.source_kind).strip().upper()
        if source_kind not in SOURCE_KINDS:
            raise ValueError("source_kind must be OFFICIAL or LICENSED")
        object.__setattr__(self, "source_kind", source_kind)
        if self.permitted_use.upper() in {"DENIED", "NONE", "PROHIBITED"}:
            raise ValueError("permitted_use denies local calendar research")
        if (
            isinstance(self.retention_days, bool)
            or not isinstance(self.retention_days, int)
            or self.retention_days <= 0
        ):
            raise ValueError("retention_days must be positive")
        if self.operator_confirmed is not True or self.local_artifact_only is not True:
            raise ValueError("calendar source requires Operator-confirmed local artifact")
        if self.redistribution_allowed or self.network_retrieval_allowed:
            raise ValueError("calendar source exceeds registered-local scope")


@dataclass(frozen=True)
class InstitutionalCalendarEvent:
    record_id: str
    calendar_id: str
    event_id: str
    event_type: str
    market: str
    horizon: str
    event_at_utc: str
    publication_at_utc: str
    first_legally_available_at_utc: str
    retrieved_at_utc: str
    ingested_at_utc: str
    first_tradable_at_utc: str
    source: InstitutionalCalendarSource
    content_sha256: str
    revision_number: int = 0
    revision_state: str = "ORIGINAL"
    revises_record_hash: str | None = None
    observed_not_inferred: bool = True
    confirmed_schedule: bool = True
    operator_registered: bool = True
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("record_id", "calendar_id", "event_id", "market", "horizon"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        event_type = str(self.event_type).strip().upper()
        if event_type not in EVENT_TYPES:
            raise ValueError("event_type is not registered")
        object.__setattr__(self, "event_type", event_type)
        for name in (
            "event_at_utc",
            "publication_at_utc",
            "first_legally_available_at_utc",
            "retrieved_at_utc",
            "ingested_at_utc",
            "first_tradable_at_utc",
        ):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        publication = instant(self.publication_at_utc)
        legal = instant(self.first_legally_available_at_utc)
        retrieved = instant(self.retrieved_at_utc)
        ingested = instant(self.ingested_at_utc)
        tradable = instant(self.first_tradable_at_utc)
        if not publication <= legal <= retrieved <= ingested:
            raise ValueError("publication, legal availability, retrieval, and ingest must be ordered")
        if tradable < legal:
            raise ValueError("first tradable time cannot precede legal availability")
        if not isinstance(self.source, InstitutionalCalendarSource):
            raise ValueError("source must be InstitutionalCalendarSource")
        object.__setattr__(
            self, "content_sha256", sha256_text(self.content_sha256, "content_sha256")
        )
        if isinstance(self.revision_number, bool) or self.revision_number < 0:
            raise ValueError("revision_number must be a nonnegative integer")
        revision_state = str(self.revision_state).strip().upper()
        if revision_state not in REVISION_STATES:
            raise ValueError("revision_state is not registered")
        object.__setattr__(self, "revision_state", revision_state)
        if self.revision_number == 0:
            if revision_state != "ORIGINAL" or self.revises_record_hash is not None:
                raise ValueError("revision zero must be ORIGINAL without predecessor")
        else:
            if revision_state == "ORIGINAL" or self.revises_record_hash is None:
                raise ValueError("later revision must identify its predecessor")
            object.__setattr__(
                self,
                "revises_record_hash",
                sha256_text(self.revises_record_hash, "revises_record_hash"),
            )
        if self.observed_not_inferred is not True or self.confirmed_schedule is not True:
            raise ValueError("calendar event must be confirmed registered evidence")
        if self.operator_registered is not True:
            raise ValueError("calendar event requires Operator registration")
        payload = {
            "calendar_id": self.calendar_id,
            "confirmed_schedule": self.confirmed_schedule,
            "content_sha256": self.content_sha256,
            "event_at_utc": self.event_at_utc,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "first_legally_available_at_utc": self.first_legally_available_at_utc,
            "first_tradable_at_utc": self.first_tradable_at_utc,
            "horizon": self.horizon,
            "ingested_at_utc": self.ingested_at_utc,
            "market": self.market,
            "observed_not_inferred": self.observed_not_inferred,
            "operator_registered": self.operator_registered,
            "publication_at_utc": self.publication_at_utc,
            "record_id": self.record_id,
            "retrieved_at_utc": self.retrieved_at_utc,
            "revision_number": self.revision_number,
            "revision_state": self.revision_state,
            "revises_record_hash": self.revises_record_hash,
            "source": {
                "artifact_version": self.source.artifact_version,
                "license_id": self.source.license_id,
                "local_artifact_only": self.source.local_artifact_only,
                "network_retrieval_allowed": self.source.network_retrieval_allowed,
                "operator_confirmed": self.source.operator_confirmed,
                "permitted_use": self.source.permitted_use,
                "registered_artifact_id": self.source.registered_artifact_id,
                "redistribution_allowed": self.source.redistribution_allowed,
                "retention_days": self.source.retention_days,
                "source_id": self.source.source_id,
                "source_kind": self.source.source_kind,
            },
        }
        object.__setattr__(self, "record_hash", _hash(payload))


@dataclass(frozen=True)
class CalendarFreshnessPolicy:
    policy_id: str
    max_age_seconds: int
    operator_registered: bool = True
    stale_data_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", identifier(self.policy_id, "policy_id"))
        if (
            isinstance(self.max_age_seconds, bool)
            or not isinstance(self.max_age_seconds, int)
            or self.max_age_seconds <= 0
        ):
            raise ValueError("max_age_seconds must be positive")
        if self.operator_registered is not True:
            raise ValueError("freshness policy requires Operator registration")
        if self.stale_data_allowed:
            raise ValueError("stale calendar evidence cannot be enabled")
