from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import RegisteredClockEventState


SUPPLY_TYPES = (
    "LOCK_UP_EXPIRY",
    "PLANNED_REDUCTION",
    "PLACEMENT",
    "SECONDARY_OFFERING",
    "CONVERTIBLE_ACTION",
    "JUDICIAL_AUCTION",
)
OBSERVATION_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")
MAX_ABSOLUTE_VALUE = Decimal("1E30")


def _hash(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("ascii")
    ).hexdigest()


def decimal_value(value: object, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite decimal")
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be a finite decimal") from exc
    if not normalized.is_finite() or abs(normalized) > MAX_ABSOLUTE_VALUE:
        raise ValueError(f"{name} must be a finite bounded decimal")
    return normalized


def _bps(numerator: Decimal, denominator: Decimal) -> int | None:
    if denominator == 0:
        return None
    return int(
        ((numerator / denominator) * Decimal("10000")).quantize(
            Decimal("1"), rounding=ROUND_HALF_EVEN
        )
    )


@dataclass(frozen=True)
class RegisteredEquitySupplyEvent:
    supply_event_id: str
    subject_id: str
    market: str
    supply_type: str
    holder_class: str
    legally_sellable_at_utc: str
    available_at_utc: str
    source_event: InstitutionalCalendarEvent
    event_state: RegisteredClockEventState | None = None
    operator_registered: bool = True
    supply_event_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("supply_event_id", "subject_id", "market", "holder_class"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        supply_type = str(self.supply_type).strip().upper()
        if supply_type not in SUPPLY_TYPES:
            raise ValueError("supply_type is not registered")
        object.__setattr__(self, "supply_type", supply_type)
        for name in ("legally_sellable_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if not isinstance(self.source_event, InstitutionalCalendarEvent):
            raise ValueError("equity supply event requires registered R23 evidence")
        if self.source_event.event_type != "CORPORATE_ACTION":
            raise ValueError("equity supply source must be a corporate action")
        if self.source_event.market != self.market:
            raise ValueError("equity supply source market must match")
        if instant(self.legally_sellable_at_utc) != instant(self.source_event.event_at_utc):
            raise ValueError("legally sellable time must equal registered event time")
        if instant(self.available_at_utc) < instant(self.source_event.ingested_at_utc):
            raise ValueError("supply event availability cannot precede source ingest")
        if self.event_state is not None:
            if not isinstance(self.event_state, RegisteredClockEventState):
                raise ValueError("event_state must be registered R24 evidence")
            if self.event_state.source_event.record_hash != self.source_event.record_hash:
                raise ValueError("event_state must share the registered supply event")
        if self.operator_registered is not True:
            raise ValueError("equity supply event requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "event_state_hash": None if self.event_state is None else self.event_state.state_hash,
            "holder_class": self.holder_class,
            "legally_sellable_at_utc": self.legally_sellable_at_utc,
            "market": self.market,
            "operator_registered": self.operator_registered,
            "source_event_hash": self.source_event.record_hash,
            "subject_id": self.subject_id,
            "supply_event_id": self.supply_event_id,
            "supply_type": self.supply_type,
        }
        object.__setattr__(self, "supply_event_hash", _hash(payload))


@dataclass(frozen=True)
class RegisteredEquitySupplyObservation:
    observation_id: str
    supply_event: RegisteredEquitySupplyEvent
    observed_at_utc: str
    available_at_utc: str
    legally_sellable_shares: Decimal | str | int | None
    free_float_shares: Decimal | str | int | None
    market_price: Decimal | str | int | None
    average_traded_value: Decimal | str | int | None
    pledged_shares: Decimal | str | int | None
    actual_sold_shares: Decimal | str | int | None
    observation_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_id", identifier(self.observation_id, "observation_id"))
        if not isinstance(self.supply_event, RegisteredEquitySupplyEvent):
            raise ValueError("supply observation requires registered supply event")
        for name in ("observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.available_at_utc) < max(
            instant(self.observed_at_utc), instant(self.supply_event.available_at_utc)
        ):
            raise ValueError("supply observation availability cannot precede evidence")
        state = str(self.observation_state).strip().upper()
        if state not in OBSERVATION_STATES:
            raise ValueError("observation_state is not registered")
        object.__setattr__(self, "observation_state", state)
        names = (
            "legally_sellable_shares",
            "free_float_shares",
            "market_price",
            "average_traded_value",
            "pledged_shares",
            "actual_sold_shares",
        )
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields)
        object.__setattr__(self, "missing_fields", missing)
        if len(set(missing)) != len(missing):
            raise ValueError("missing_fields cannot contain duplicates")
        if state == "OBSERVED":
            if missing or any(getattr(self, name) is None for name in names):
                raise ValueError("observed supply evidence requires complete measurements")
            for name in names:
                object.__setattr__(self, name, decimal_value(getattr(self, name), name))
            if self.free_float_shares <= 0 or self.market_price <= 0 or self.average_traded_value <= 0:  # type: ignore[operator]
                raise ValueError("float, price, and traded value must be positive")
            if any(getattr(self, name) < 0 for name in ("legally_sellable_shares", "pledged_shares", "actual_sold_shares")):
                raise ValueError("share measurements must be nonnegative")
            if self.actual_sold_shares > self.legally_sellable_shares:  # type: ignore[operator]
                raise ValueError("actual sold shares cannot exceed legally sellable shares")
        else:
            if not missing:
                raise ValueError("non-observed supply evidence requires missing_fields")
            if any(getattr(self, name) is not None for name in names):
                raise ValueError("non-observed supply evidence cannot carry partial measurements")
        if self.operator_registered is not True:
            raise ValueError("supply observation requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "measurements": {name: None if getattr(self, name) is None else str(getattr(self, name)) for name in names},
            "missing_fields": list(self.missing_fields),
            "observation_id": self.observation_id,
            "observation_state": self.observation_state,
            "observed_at_utc": self.observed_at_utc,
            "operator_registered": self.operator_registered,
            "supply_event_hash": self.supply_event.supply_event_hash,
        }
        object.__setattr__(self, "observation_hash", _hash(payload))


@dataclass(frozen=True)
class EquitySupplyPressureRecord:
    record_id: str
    observation: RegisteredEquitySupplyObservation
    available_at_utc: str
    unlock_equals_sale_claim: bool = False
    forced_sale_claim: bool = False
    holder_intent_claim: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    supply_to_float_bps: int = field(init=False)
    supply_market_value: Decimal = field(init=False)
    absorption_days: Decimal = field(init=False)
    pledge_to_float_bps: int = field(init=False)
    actual_sale_to_supply_bps: int | None = field(init=False)
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", identifier(self.record_id, "record_id"))
        if not isinstance(self.observation, RegisteredEquitySupplyObservation):
            raise ValueError("pressure record requires registered supply observation")
        if self.observation.observation_state != "OBSERVED":
            raise ValueError("non-observed supply evidence cannot create pressure metrics")
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if instant(self.available_at_utc) < instant(self.observation.available_at_utc):
            raise ValueError("pressure record availability cannot precede observation")
        item = self.observation
        supply_to_float = _bps(item.legally_sellable_shares, item.free_float_shares)  # type: ignore[arg-type]
        pledge_to_float = _bps(item.pledged_shares, item.free_float_shares)  # type: ignore[arg-type]
        if supply_to_float is None or pledge_to_float is None:
            raise ValueError("pressure metrics require positive free float")
        market_value = item.legally_sellable_shares * item.market_price  # type: ignore[operator]
        absorption_days = (market_value / item.average_traded_value).quantize(  # type: ignore[operator]
            Decimal("0.0001"), rounding=ROUND_HALF_EVEN
        )
        actual_sale = _bps(item.actual_sold_shares, item.legally_sellable_shares)  # type: ignore[arg-type]
        object.__setattr__(self, "supply_to_float_bps", supply_to_float)
        object.__setattr__(self, "supply_market_value", market_value)
        object.__setattr__(self, "absorption_days", absorption_days)
        object.__setattr__(self, "pledge_to_float_bps", pledge_to_float)
        object.__setattr__(self, "actual_sale_to_supply_bps", actual_sale)
        if self.unlock_equals_sale_claim:
            raise ValueError("unlock cannot be treated as actual sale")
        if self.forced_sale_claim:
            raise ValueError("pledge evidence cannot create a forced-sale claim")
        if self.holder_intent_claim:
            raise ValueError("supply evidence cannot create a holder-intent claim")
        if self.factor_activated:
            raise ValueError("supply evidence cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("pressure record requires Operator registration")
        payload = {
            "absorption_days": str(self.absorption_days),
            "actual_sale_to_supply_bps": self.actual_sale_to_supply_bps,
            "available_at_utc": self.available_at_utc,
            "factor_activated": self.factor_activated,
            "forced_sale_claim": self.forced_sale_claim,
            "holder_intent_claim": self.holder_intent_claim,
            "observation_hash": item.observation_hash,
            "operator_registered": self.operator_registered,
            "pledge_to_float_bps": self.pledge_to_float_bps,
            "record_id": self.record_id,
            "supply_market_value": str(self.supply_market_value),
            "supply_to_float_bps": self.supply_to_float_bps,
            "unlock_equals_sale_claim": self.unlock_equals_sale_claim,
        }
        object.__setattr__(self, "record_hash", _hash(payload))
