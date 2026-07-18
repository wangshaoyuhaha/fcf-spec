from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
)


DISCLOSURE_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")


def _hash(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _decimal(value: object, name: str, *, positive: bool = False) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not result.is_finite() or result < 0 or result > Decimal("1E30"):
        raise ValueError(f"{name} must be bounded and nonnegative")
    if positive and result == 0:
        raise ValueError(f"{name} must be positive")
    return result


def _bps(value: Decimal) -> int:
    return int(
        (value * Decimal("10000")).quantize(
            Decimal("1"), rounding=ROUND_HALF_EVEN
        )
    )


@dataclass(frozen=True)
class RegisteredInstitutionalHoldingDisclosure:
    disclosure_id: str
    subject_id: str
    market: str
    fund_id: str
    report_period_end_utc: str
    published_at_utc: str
    available_at_utc: str
    shares_held: Decimal | str | int | None
    prior_shares_held: Decimal | str | int | None
    free_float_shares: Decimal | str | int | None
    average_daily_traded_shares: Decimal | str | int | None
    source_event: InstitutionalCalendarEvent
    disclosure_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    disclosure_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("disclosure_id", "subject_id", "market", "fund_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in (
            "report_period_end_utc",
            "published_at_utc",
            "available_at_utc",
        ):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if not isinstance(self.source_event, InstitutionalCalendarEvent):
            raise ValueError("holding disclosure requires registered R23 evidence")
        if instant(self.published_at_utc) < instant(self.report_period_end_utc):
            raise ValueError("publication cannot precede report period")
        if instant(self.available_at_utc) < max(
            instant(self.published_at_utc), instant(self.source_event.ingested_at_utc)
        ):
            raise ValueError("availability cannot precede registered evidence")
        state = str(self.disclosure_state).strip().upper()
        if state not in DISCLOSURE_STATES:
            raise ValueError("disclosure_state is not registered")
        object.__setattr__(self, "disclosure_state", state)
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields)
        object.__setattr__(self, "missing_fields", missing)
        names = (
            "shares_held",
            "prior_shares_held",
            "free_float_shares",
            "average_daily_traded_shares",
        )
        if state == "OBSERVED":
            if any(getattr(self, name) is None for name in names) or missing:
                raise ValueError("observed disclosure requires complete values")
            shares = _decimal(self.shares_held, "shares_held")
            prior = _decimal(self.prior_shares_held, "prior_shares_held")
            free_float = _decimal(
                self.free_float_shares, "free_float_shares", positive=True
            )
            average = _decimal(
                self.average_daily_traded_shares,
                "average_daily_traded_shares",
                positive=True,
            )
            if shares > free_float or prior > free_float:
                raise ValueError("fund holding cannot exceed free float")
            for name, value in zip(names, (shares, prior, free_float, average)):
                object.__setattr__(self, name, value)
        elif any(getattr(self, name) is not None for name in names) or not missing:
            raise ValueError(
                "non-observed disclosure requires null values and missing_fields"
            )
        if self.operator_registered is not True:
            raise ValueError("holding disclosure requires Operator registration")
        values = {
            name: None if getattr(self, name) is None else str(getattr(self, name))
            for name in names
        }
        object.__setattr__(
            self,
            "disclosure_hash",
            _hash(
                {
                    "available_at_utc": self.available_at_utc,
                    "disclosure_id": self.disclosure_id,
                    "fund_id": self.fund_id,
                    "market": self.market,
                    "missing_fields": list(missing),
                    "published_at_utc": self.published_at_utc,
                    "report_period_end_utc": self.report_period_end_utc,
                    "source_event_hash": self.source_event.record_hash,
                    "state": state,
                    "subject_id": self.subject_id,
                    "values": values,
                }
            ),
        )


@dataclass(frozen=True)
class InstitutionalCrowdingRecord:
    record_id: str
    disclosures: tuple[RegisteredInstitutionalHoldingDisclosure, ...]
    available_at_utc: str
    current_manager_action_inference: bool = False
    quarter_end_motive_inference: bool = False
    manipulation_claim: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    disclosed_ownership_bps: int = field(init=False)
    normalized_concentration_bps: int = field(init=False)
    ownership_change_bps: int = field(init=False)
    exit_days_milli: int = field(init=False)
    disclosure_age_days: int = field(init=False)
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", identifier(self.record_id, "record_id"))
        disclosures = tuple(self.disclosures)
        if not disclosures or any(
            not isinstance(item, RegisteredInstitutionalHoldingDisclosure)
            or item.disclosure_state != "OBSERVED"
            for item in disclosures
        ):
            raise ValueError("crowding metrics require observed disclosures")
        if len({item.fund_id for item in disclosures}) != len(disclosures):
            raise ValueError("one disclosure per fund is required")
        identity = {
            (
                item.subject_id,
                item.market,
                item.report_period_end_utc,
                item.free_float_shares,
                item.average_daily_traded_shares,
            )
            for item in disclosures
        }
        if len(identity) != 1:
            raise ValueError("crowding disclosures require a common basis")
        object.__setattr__(self, "disclosures", disclosures)
        object.__setattr__(
            self, "available_at_utc", utc(self.available_at_utc, "available_at_utc")
        )
        if instant(self.available_at_utc) < max(
            instant(item.available_at_utc) for item in disclosures
        ):
            raise ValueError("metrics availability cannot precede disclosures")
        total = sum((item.shares_held for item in disclosures), Decimal("0"))
        prior = sum((item.prior_shares_held for item in disclosures), Decimal("0"))
        free_float = disclosures[0].free_float_shares
        average = disclosures[0].average_daily_traded_shares
        if total > free_float:
            raise ValueError("aggregate disclosed holdings cannot exceed free float")
        concentration = (
            Decimal("0")
            if total == 0
            else sum(
                ((item.shares_held / total) ** 2 for item in disclosures),
                Decimal("0"),
            )
        )
        ownership_bps = _bps(total / free_float)
        concentration_bps = _bps(concentration)
        change_bps = _bps((total - prior) / free_float)
        exit_days_milli = int(
            ((total / average) * Decimal("1000")).quantize(
                Decimal("1"), rounding=ROUND_HALF_EVEN
            )
        )
        age_seconds = (
            instant(self.available_at_utc)
            - instant(disclosures[0].report_period_end_utc)
        ).total_seconds()
        age_days = int(age_seconds // 86400)
        object.__setattr__(self, "disclosed_ownership_bps", ownership_bps)
        object.__setattr__(self, "normalized_concentration_bps", concentration_bps)
        object.__setattr__(self, "ownership_change_bps", change_bps)
        object.__setattr__(self, "exit_days_milli", exit_days_milli)
        object.__setattr__(self, "disclosure_age_days", age_days)
        if self.current_manager_action_inference:
            raise ValueError("disclosure cannot infer current manager action")
        if self.quarter_end_motive_inference:
            raise ValueError("disclosure cannot infer quarter-end motive")
        if self.manipulation_claim:
            raise ValueError("disclosure cannot claim manipulation")
        if self.factor_activated:
            raise ValueError("crowding evidence cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("crowding record requires Operator registration")
        object.__setattr__(
            self,
            "record_hash",
            _hash(
                {
                    "available_at_utc": self.available_at_utc,
                    "disclosure_hashes": sorted(
                        item.disclosure_hash for item in disclosures
                    ),
                    "metrics": [
                        ownership_bps,
                        concentration_bps,
                        change_bps,
                        exit_days_milli,
                        age_days,
                    ],
                    "record_id": self.record_id,
                }
            ),
        )
