from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)


SESSION_PHASES = (
    "PRE_OPEN",
    "CALL_AUCTION",
    "CONTINUOUS_SESSION",
    "LATE_SESSION",
    "CLOSE",
    "POST_CLOSE",
)


def _sha256(value: object, name: str) -> str:
    normalized = str(value).strip()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class RegisteredSessionInterval:
    interval_id: str
    sequence: int
    phase: str
    start_at_utc: str
    end_at_utc: str
    available_at_utc: str
    source_artifact_hash: str
    observed_not_inferred: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "interval_id", identifier(self.interval_id, "interval_id"))
        if isinstance(self.sequence, bool) or self.sequence <= 0:
            raise ValueError("session interval sequence must be positive")
        phase = str(self.phase).strip().upper()
        if phase not in SESSION_PHASES:
            raise ValueError("session phase is not registered")
        object.__setattr__(self, "phase", phase)
        object.__setattr__(self, "start_at_utc", utc(self.start_at_utc, "start_at_utc"))
        object.__setattr__(self, "end_at_utc", utc(self.end_at_utc, "end_at_utc"))
        object.__setattr__(
            self, "available_at_utc", utc(self.available_at_utc, "available_at_utc")
        )
        if instant(self.end_at_utc) <= instant(self.start_at_utc):
            raise ValueError("session interval end must follow start")
        object.__setattr__(
            self,
            "source_artifact_hash",
            _sha256(self.source_artifact_hash, "source_artifact_hash"),
        )
        if self.observed_not_inferred is not True:
            raise ValueError("session interval must be registered, not inferred")


@dataclass(frozen=True)
class MarketSessionDefinition:
    registry_id: str
    venue: str
    market: str
    trade_date: str
    timezone: str
    calendar_version: str
    rule_version: str
    available_at_utc: str
    effective_from_utc: str
    expires_at_utc: str
    intervals: tuple[RegisteredSessionInterval, ...]
    continuous_market: bool = False
    operator_registered: bool = True
    definition_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "registry_id",
            "venue",
            "market",
            "timezone",
            "calendar_version",
            "rule_version",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        try:
            date.fromisoformat(self.trade_date)
        except (TypeError, ValueError) as error:
            raise ValueError("trade_date must be ISO date") from error
        for name in ("available_at_utc", "effective_from_utc", "expires_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.expires_at_utc) <= instant(self.effective_from_utc):
            raise ValueError("session definition expiry must follow effective time")
        intervals = tuple(self.intervals)
        if not 1 <= len(intervals) <= 32:
            raise ValueError("session definition interval count is invalid")
        object.__setattr__(self, "intervals", intervals)
        if tuple(item.sequence for item in intervals) != tuple(range(1, len(intervals) + 1)):
            raise ValueError("session interval sequence must be contiguous")
        if len({item.interval_id for item in intervals}) != len(intervals):
            raise ValueError("duplicate session interval id is prohibited")
        for previous, current in zip(intervals, intervals[1:]):
            if instant(current.start_at_utc) < instant(previous.end_at_utc):
                raise ValueError("registered session intervals overlap")
        if self.operator_registered is not True:
            raise ValueError("session definition must be Operator-registered")
        payload = {
            "available_at_utc": self.available_at_utc,
            "calendar_version": self.calendar_version,
            "continuous_market": self.continuous_market,
            "effective_from_utc": self.effective_from_utc,
            "expires_at_utc": self.expires_at_utc,
            "intervals": [
                {
                    "available_at_utc": item.available_at_utc,
                    "end_at_utc": item.end_at_utc,
                    "interval_id": item.interval_id,
                    "phase": item.phase,
                    "sequence": item.sequence,
                    "source_artifact_hash": item.source_artifact_hash,
                    "start_at_utc": item.start_at_utc,
                }
                for item in intervals
            ],
            "market": self.market,
            "registry_id": self.registry_id,
            "rule_version": self.rule_version,
            "timezone": self.timezone,
            "trade_date": self.trade_date,
            "venue": self.venue,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
        ).hexdigest()
        object.__setattr__(self, "definition_hash", digest)
