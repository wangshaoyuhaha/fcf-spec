from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
)


CLOCK_TYPES = ("MACRO", "INSTITUTIONAL", "CAPITAL", "INDUSTRY", "COMPANY")
STATE_KINDS = (
    "PRE_EVENT",
    "RELEASED_NOT_TRADABLE",
    "FIRST_TRADABLE_REACTION",
    "POST_EVENT_DIGESTION",
    "EXPIRY_WINDOW",
    "HOLIDAY_LIQUIDITY",
    "EARNINGS_REBUILD",
    "STALE_OR_CONFLICTED",
)
EVIDENCE_GROUPS = ("SUPPORTING", "OPPOSING", "NEUTRAL", "MISSING", "STALE", "BLOCKED")
MISSING_STATES = (
    "AVAILABLE",
    "NOT_APPLICABLE",
    "NOT_YET_PUBLISHED",
    "MISSING",
    "SOURCE_FAILURE",
)
FRESHNESS_STATES = ("FRESH", "STALE", "UNKNOWN")


def _hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class RegisteredClockEventState:
    state_id: str
    state_version: str
    clock_type: str
    state_kind: str
    evidence_group: str
    hypothesis_id: str
    market: str
    horizon: str
    effective_from_utc: str
    effective_to_utc: str
    available_at_utc: str
    source_event: InstitutionalCalendarEvent
    confidence_bps: int
    missing_state: str = "AVAILABLE"
    freshness_state: str = "FRESH"
    operator_registered: bool = True
    state_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "state_id",
            "state_version",
            "hypothesis_id",
            "market",
            "horizon",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name, allowed in (
            ("clock_type", CLOCK_TYPES),
            ("state_kind", STATE_KINDS),
            ("evidence_group", EVIDENCE_GROUPS),
            ("missing_state", MISSING_STATES),
            ("freshness_state", FRESHNESS_STATES),
        ):
            value = str(getattr(self, name)).strip().upper()
            if value not in allowed:
                raise ValueError(f"{name} is not registered")
            object.__setattr__(self, name, value)
        for name in ("effective_from_utc", "effective_to_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.effective_to_utc) <= instant(self.effective_from_utc):
            raise ValueError("clock state end must follow start")
        if not isinstance(self.source_event, InstitutionalCalendarEvent):
            raise ValueError("source_event must be registered R23 evidence")
        if instant(self.available_at_utc) < instant(self.source_event.ingested_at_utc):
            raise ValueError("clock state availability cannot precede source ingest")
        if isinstance(self.confidence_bps, bool) or not 0 <= self.confidence_bps <= 10000:
            raise ValueError("confidence_bps must be between zero and 10000")
        if self.evidence_group == "MISSING":
            if self.missing_state == "AVAILABLE" or self.confidence_bps != 0:
                raise ValueError("missing evidence requires explicit missing state and zero confidence")
        elif self.evidence_group in {"SUPPORTING", "OPPOSING", "NEUTRAL"}:
            if self.missing_state != "AVAILABLE":
                raise ValueError("usable evidence cannot carry a missing state")
        if self.freshness_state == "STALE" and self.evidence_group not in {"STALE", "BLOCKED"}:
            raise ValueError("stale evidence must remain stale or blocked")
        if self.evidence_group == "STALE" and self.freshness_state != "STALE":
            raise ValueError("stale evidence group requires stale freshness")
        if self.source_event.revision_state == "CANCELLED" and self.evidence_group != "BLOCKED":
            raise ValueError("cancelled source event must remain blocked")
        if self.operator_registered is not True:
            raise ValueError("clock state requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "clock_type": self.clock_type,
            "confidence_bps": self.confidence_bps,
            "effective_from_utc": self.effective_from_utc,
            "effective_to_utc": self.effective_to_utc,
            "evidence_group": self.evidence_group,
            "freshness_state": self.freshness_state,
            "horizon": self.horizon,
            "hypothesis_id": self.hypothesis_id,
            "market": self.market,
            "missing_state": self.missing_state,
            "operator_registered": self.operator_registered,
            "source_event_hash": self.source_event.record_hash,
            "state_id": self.state_id,
            "state_kind": self.state_kind,
            "state_version": self.state_version,
        }
        object.__setattr__(self, "state_hash", _hash(payload))
