from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import InstitutionalCalendarEvent
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import RegisteredClockEventState


OBSERVATION_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")
MAX_ABSOLUTE_VALUE = Decimal("1E30")
SECONDS_PER_DAY = Decimal("86400")


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
class RegisteredIndexFuturesContract:
    contract_id: str
    contract_family: str
    market: str
    underlying_index_id: str
    expiry_at_utc: str
    available_at_utc: str
    settlement_rule_version: str
    contract_multiplier: Decimal | str | int
    expiry_event: InstitutionalCalendarEvent
    expiry_state: RegisteredClockEventState | None = None
    operator_registered: bool = True
    contract_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "contract_id",
            "contract_family",
            "market",
            "underlying_index_id",
            "settlement_rule_version",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("expiry_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if not isinstance(self.expiry_event, InstitutionalCalendarEvent):
            raise ValueError("index-futures contract requires registered R23 expiry evidence")
        if self.expiry_event.event_type != "INDEX_FUTURES_EVENT":
            raise ValueError("expiry_event must be an index-futures expiry event")
        if self.expiry_event.market != self.market:
            raise ValueError("expiry event market must match contract market")
        if instant(self.expiry_at_utc) != instant(self.expiry_event.event_at_utc):
            raise ValueError("contract expiry must equal registered expiry event time")
        if instant(self.available_at_utc) < instant(self.expiry_event.ingested_at_utc):
            raise ValueError("contract availability cannot precede expiry-event ingest")
        if self.expiry_state is not None:
            if not isinstance(self.expiry_state, RegisteredClockEventState):
                raise ValueError("expiry_state must be registered R24 evidence")
            if self.expiry_state.state_kind != "EXPIRY_WINDOW":
                raise ValueError("expiry_state must preserve EXPIRY_WINDOW")
            if self.expiry_state.source_event.record_hash != self.expiry_event.record_hash:
                raise ValueError("expiry_state must share the registered expiry event")
        multiplier = decimal_value(self.contract_multiplier, "contract_multiplier")
        if multiplier <= 0:
            raise ValueError("contract_multiplier must be positive")
        object.__setattr__(self, "contract_multiplier", multiplier)
        if self.operator_registered is not True:
            raise ValueError("index-futures contract requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "contract_family": self.contract_family,
            "contract_id": self.contract_id,
            "contract_multiplier": str(self.contract_multiplier),
            "expiry_at_utc": self.expiry_at_utc,
            "expiry_event_hash": self.expiry_event.record_hash,
            "expiry_state_hash": None if self.expiry_state is None else self.expiry_state.state_hash,
            "market": self.market,
            "operator_registered": self.operator_registered,
            "settlement_rule_version": self.settlement_rule_version,
            "underlying_index_id": self.underlying_index_id,
        }
        object.__setattr__(self, "contract_hash", _hash(payload))


@dataclass(frozen=True)
class RegisteredFuturesCurveObservation:
    observation_id: str
    front_contract: RegisteredIndexFuturesContract
    next_contract: RegisteredIndexFuturesContract
    observed_at_utc: str
    available_at_utc: str
    spot_index_price: Decimal | str | int | None
    front_futures_price: Decimal | str | int | None
    next_futures_price: Decimal | str | int | None
    front_open_interest: Decimal | str | int | None
    next_open_interest: Decimal | str | int | None
    front_volume: Decimal | str | int | None
    next_volume: Decimal | str | int | None
    observation_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_id", identifier(self.observation_id, "observation_id"))
        if not isinstance(self.front_contract, RegisteredIndexFuturesContract) or not isinstance(
            self.next_contract, RegisteredIndexFuturesContract
        ):
            raise ValueError("curve observation requires registered index-futures contracts")
        front = self.front_contract
        next_item = self.next_contract
        if (front.market, front.contract_family, front.underlying_index_id) != (
            next_item.market,
            next_item.contract_family,
            next_item.underlying_index_id,
        ):
            raise ValueError("curve contracts must share market, family, and underlying")
        if instant(next_item.expiry_at_utc) <= instant(front.expiry_at_utc):
            raise ValueError("next contract expiry must follow front contract expiry")
        for name in ("observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.available_at_utc) < max(
            instant(self.observed_at_utc),
            instant(front.available_at_utc),
            instant(next_item.available_at_utc),
        ):
            raise ValueError("curve observation availability cannot precede evidence")
        if instant(self.observed_at_utc) > instant(front.expiry_at_utc):
            raise ValueError("front-contract observation cannot follow registered expiry")
        state = str(self.observation_state).strip().upper()
        if state not in OBSERVATION_STATES:
            raise ValueError("observation_state is not registered")
        object.__setattr__(self, "observation_state", state)
        names = (
            "spot_index_price",
            "front_futures_price",
            "next_futures_price",
            "front_open_interest",
            "next_open_interest",
            "front_volume",
            "next_volume",
        )
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields)
        object.__setattr__(self, "missing_fields", missing)
        if len(set(missing)) != len(missing):
            raise ValueError("missing_fields cannot contain duplicates")
        if state == "OBSERVED":
            if missing or any(getattr(self, name) is None for name in names):
                raise ValueError("observed curve evidence requires complete measurements")
            for name in names:
                object.__setattr__(self, name, decimal_value(getattr(self, name), name))
            if self.spot_index_price <= 0 or self.front_futures_price <= 0 or self.next_futures_price <= 0:  # type: ignore[operator]
                raise ValueError("curve prices must be positive")
            if any(getattr(self, name) < 0 for name in names[3:]):
                raise ValueError("open-interest and volume values must be nonnegative")
        else:
            if not missing:
                raise ValueError("non-observed curve evidence requires missing_fields")
            if any(getattr(self, name) is not None for name in names):
                raise ValueError("non-observed curve evidence cannot carry partial measurements")
        if self.operator_registered is not True:
            raise ValueError("curve observation requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "front_contract_hash": front.contract_hash,
            "measurements": {name: None if getattr(self, name) is None else str(getattr(self, name)) for name in names},
            "missing_fields": list(self.missing_fields),
            "next_contract_hash": next_item.contract_hash,
            "observation_id": self.observation_id,
            "observation_state": self.observation_state,
            "observed_at_utc": self.observed_at_utc,
            "operator_registered": self.operator_registered,
        }
        object.__setattr__(self, "observation_hash", _hash(payload))


@dataclass(frozen=True)
class IndexFuturesBasisRollRecord:
    record_id: str
    observation: RegisteredFuturesCurveObservation
    available_at_utc: str
    bottom_claim: bool = False
    participant_intent_claim: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    basis_amount: Decimal = field(init=False)
    basis_bps: int = field(init=False)
    annualized_basis_bps: int | None = field(init=False)
    calendar_spread_amount: Decimal = field(init=False)
    next_open_interest_share_bps: int | None = field(init=False)
    next_volume_share_bps: int | None = field(init=False)
    seconds_to_expiry: int = field(init=False)
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", identifier(self.record_id, "record_id"))
        if not isinstance(self.observation, RegisteredFuturesCurveObservation):
            raise ValueError("basis-roll record requires registered curve observation")
        if self.observation.observation_state != "OBSERVED":
            raise ValueError("non-observed curve evidence cannot create basis-roll metrics")
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if instant(self.available_at_utc) < instant(self.observation.available_at_utc):
            raise ValueError("basis-roll availability cannot precede observation")
        item = self.observation
        basis = item.front_futures_price - item.spot_index_price  # type: ignore[operator]
        basis_bps = _bps(basis, item.spot_index_price)  # type: ignore[arg-type]
        if basis_bps is None:
            raise ValueError("basis requires positive spot price")
        seconds = int((instant(item.front_contract.expiry_at_utc) - instant(item.observed_at_utc)).total_seconds())
        if seconds < 0:
            raise ValueError("seconds_to_expiry cannot be negative")
        annualized = None
        if seconds > 0:
            annualized = int(
                (
                    Decimal(basis_bps)
                    * Decimal("365")
                    * SECONDS_PER_DAY
                    / Decimal(seconds)
                ).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
            )
        calendar_spread = item.next_futures_price - item.front_futures_price  # type: ignore[operator]
        next_oi_share = _bps(item.next_open_interest, item.front_open_interest + item.next_open_interest)  # type: ignore[arg-type,operator]
        next_volume_share = _bps(item.next_volume, item.front_volume + item.next_volume)  # type: ignore[arg-type,operator]
        object.__setattr__(self, "basis_amount", basis)
        object.__setattr__(self, "basis_bps", basis_bps)
        object.__setattr__(self, "annualized_basis_bps", annualized)
        object.__setattr__(self, "calendar_spread_amount", calendar_spread)
        object.__setattr__(self, "next_open_interest_share_bps", next_oi_share)
        object.__setattr__(self, "next_volume_share_bps", next_volume_share)
        object.__setattr__(self, "seconds_to_expiry", seconds)
        if self.bottom_claim:
            raise ValueError("basis discount cannot create a bottom claim")
        if self.participant_intent_claim:
            raise ValueError("open interest cannot create a participant-intent claim")
        if self.factor_activated:
            raise ValueError("basis-roll evidence cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("basis-roll record requires Operator registration")
        payload = {
            "annualized_basis_bps": self.annualized_basis_bps,
            "available_at_utc": self.available_at_utc,
            "basis_amount": str(self.basis_amount),
            "basis_bps": self.basis_bps,
            "bottom_claim": self.bottom_claim,
            "calendar_spread_amount": str(self.calendar_spread_amount),
            "factor_activated": self.factor_activated,
            "next_open_interest_share_bps": self.next_open_interest_share_bps,
            "next_volume_share_bps": self.next_volume_share_bps,
            "observation_hash": item.observation_hash,
            "operator_registered": self.operator_registered,
            "participant_intent_claim": self.participant_intent_claim,
            "record_id": self.record_id,
            "seconds_to_expiry": self.seconds_to_expiry,
        }
        object.__setattr__(self, "record_hash", _hash(payload))
