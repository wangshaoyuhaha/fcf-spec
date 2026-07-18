from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1 import (
    InstitutionalCalendarEvent,
)
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    RegisteredClockEventState,
)
from apps.v2_r26_local_consensus_expectation_gap_foundation_app_1 import (
    ExpectationGapRecord,
)


REACTION_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")
CROSS_MARKET_STATES = ("CONFIRMED", "DIVERGENT", "NOT_AVAILABLE")
REACTION_LABELS = (
    "ALIGNED_POSITIVE",
    "ALIGNED_NEGATIVE",
    "FAVORABLE_WEAK_REACTION",
    "UNFAVORABLE_RESILIENT_REACTION",
    "OBSERVED_UNLINKED",
)
MAX_ABSOLUTE_VALUE = Decimal("1E30")
ONE_BPS = Decimal("1")


def _hash(payload: object) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


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


def _bps(numerator: Decimal, denominator: Decimal) -> int:
    if denominator == 0:
        raise ValueError("reaction return denominator cannot be zero")
    return int(
        ((numerator / denominator) * Decimal("10000")).quantize(
            ONE_BPS, rounding=ROUND_HALF_EVEN
        )
    )


@dataclass(frozen=True)
class RegisteredReactionWindow:
    window_id: str
    subject_id: str
    market: str
    horizon: str
    source_event: InstitutionalCalendarEvent
    clock_state: RegisteredClockEventState
    expectation_gap: ExpectationGapRecord | None
    reference_at_utc: str
    first_tradable_at_utc: str
    window_end_utc: str
    matures_at_utc: str
    available_at_utc: str
    operator_registered: bool = True
    window_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("window_id", "subject_id", "market", "horizon"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in (
            "reference_at_utc",
            "first_tradable_at_utc",
            "window_end_utc",
            "matures_at_utc",
            "available_at_utc",
        ):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if not isinstance(self.source_event, InstitutionalCalendarEvent):
            raise ValueError("reaction window requires registered R23 event evidence")
        if not isinstance(self.clock_state, RegisteredClockEventState):
            raise ValueError("reaction window requires registered R24 clock state")
        if self.expectation_gap is not None and not isinstance(
            self.expectation_gap, ExpectationGapRecord
        ):
            raise ValueError("expectation_gap must be registered R26 evidence")
        if self.market != self.clock_state.market or self.horizon != self.clock_state.horizon:
            raise ValueError("reaction window and clock dimensions must match")
        ordered = (
            instant(self.reference_at_utc),
            instant(self.first_tradable_at_utc),
            instant(self.window_end_utc),
            instant(self.matures_at_utc),
        )
        if not ordered[0] <= ordered[1] < ordered[2] <= ordered[3]:
            raise ValueError("reaction window times must be ordered")
        if instant(self.available_at_utc) < max(
            instant(self.source_event.ingested_at_utc),
            instant(self.clock_state.available_at_utc),
        ):
            raise ValueError("reaction window availability cannot precede evidence")
        if self.expectation_gap is not None and instant(self.available_at_utc) < instant(
            self.expectation_gap.available_at_utc
        ):
            raise ValueError("reaction window availability cannot precede expectation gap")
        if self.operator_registered is not True:
            raise ValueError("reaction window requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "clock_state_hash": self.clock_state.state_hash,
            "expectation_gap_hash": None
            if self.expectation_gap is None
            else self.expectation_gap.gap_hash,
            "first_tradable_at_utc": self.first_tradable_at_utc,
            "horizon": self.horizon,
            "market": self.market,
            "matures_at_utc": self.matures_at_utc,
            "operator_registered": self.operator_registered,
            "reference_at_utc": self.reference_at_utc,
            "source_event_hash": self.source_event.record_hash,
            "subject_id": self.subject_id,
            "window_end_utc": self.window_end_utc,
            "window_id": self.window_id,
        }
        object.__setattr__(self, "window_hash", _hash(payload))


@dataclass(frozen=True)
class RegisteredReactionObservation:
    observation_id: str
    window: RegisteredReactionWindow
    observed_at_utc: str
    available_at_utc: str
    previous_close: Decimal | str | int | None
    first_tradable_price: Decimal | str | int | None
    high_price: Decimal | str | int | None
    low_price: Decimal | str | int | None
    close_price: Decimal | str | int | None
    volume_ratio_bps: int | None
    turnover_bps: int | None
    spread_bps: int | None
    depth_imbalance_bps: int | None
    breadth_bps: int | None
    futures_basis_bps: int | None
    volatility_bps: int | None
    cross_market_state: str
    reaction_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "observation_id", identifier(self.observation_id, "observation_id"))
        if not isinstance(self.window, RegisteredReactionWindow):
            raise ValueError("reaction observation requires registered window")
        for name in ("observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.observed_at_utc) < instant(self.window.window_end_utc):
            raise ValueError("reaction observation cannot close before window end")
        if instant(self.available_at_utc) < max(
            instant(self.observed_at_utc), instant(self.window.available_at_utc)
        ):
            raise ValueError("reaction observation availability cannot precede evidence")
        state = str(self.reaction_state).strip().upper()
        cross_market = str(self.cross_market_state).strip().upper()
        if state not in REACTION_STATES:
            raise ValueError("reaction_state is not registered")
        if cross_market not in CROSS_MARKET_STATES:
            raise ValueError("cross_market_state is not registered")
        object.__setattr__(self, "reaction_state", state)
        object.__setattr__(self, "cross_market_state", cross_market)
        numeric_names = (
            "previous_close",
            "first_tradable_price",
            "high_price",
            "low_price",
            "close_price",
        )
        metric_names = (
            "volume_ratio_bps",
            "turnover_bps",
            "spread_bps",
            "depth_imbalance_bps",
            "breadth_bps",
            "futures_basis_bps",
            "volatility_bps",
        )
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields)
        if len(set(missing)) != len(missing):
            raise ValueError("missing_fields cannot contain duplicates")
        object.__setattr__(self, "missing_fields", missing)
        if state == "OBSERVED":
            if missing or any(getattr(self, name) is None for name in (*numeric_names, *metric_names)):
                raise ValueError("observed reaction requires complete registered measurements")
            for name in numeric_names:
                value = decimal_value(getattr(self, name), name)
                if value <= 0:
                    raise ValueError(f"{name} must be positive")
                object.__setattr__(self, name, value)
            if not self.low_price <= self.close_price <= self.high_price:  # type: ignore[operator]
                raise ValueError("close price must remain inside observed range")
            if not self.low_price <= self.first_tradable_price <= self.high_price:  # type: ignore[operator]
                raise ValueError("first tradable price must remain inside observed range")
            for name in metric_names:
                value = getattr(self, name)
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f"{name} must be an integer")
            if not 0 <= self.breadth_bps <= 10000:  # type: ignore[operator]
                raise ValueError("breadth_bps must be between zero and 10000")
            if not -10000 <= self.depth_imbalance_bps <= 10000:  # type: ignore[operator]
                raise ValueError("depth_imbalance_bps must be between -10000 and 10000")
            for name in ("volume_ratio_bps", "turnover_bps", "spread_bps", "volatility_bps"):
                if getattr(self, name) < 0:
                    raise ValueError(f"{name} must be nonnegative")
        else:
            if not missing:
                raise ValueError("non-observed reaction requires explicit missing_fields")
            if any(getattr(self, name) is not None for name in (*numeric_names, *metric_names)):
                raise ValueError("non-observed reaction cannot carry partial measurements")
        if self.operator_registered is not True:
            raise ValueError("reaction observation requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "cross_market_state": self.cross_market_state,
            "measurements": {
                name: None if getattr(self, name) is None else str(getattr(self, name))
                for name in (*numeric_names, *metric_names)
            },
            "missing_fields": list(self.missing_fields),
            "observation_id": self.observation_id,
            "observed_at_utc": self.observed_at_utc,
            "operator_registered": self.operator_registered,
            "reaction_state": self.reaction_state,
            "window_hash": self.window.window_hash,
        }
        object.__setattr__(self, "observation_hash", _hash(payload))


@dataclass(frozen=True)
class EventReactionQualityRecord:
    quality_id: str
    observation: RegisteredReactionObservation
    available_at_utc: str
    factor_activated: bool = False
    operator_registered: bool = True
    gap_return_bps: int = field(init=False)
    close_return_bps: int = field(init=False)
    intrawindow_range_bps: int = field(init=False)
    close_location_bps: int | None = field(init=False)
    persistence_state: str = field(init=False)
    reaction_label: str = field(init=False)
    quality_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "quality_id", identifier(self.quality_id, "quality_id"))
        if not isinstance(self.observation, RegisteredReactionObservation):
            raise ValueError("reaction quality requires registered observation")
        if self.observation.reaction_state != "OBSERVED":
            raise ValueError("non-observed reaction cannot create quality record")
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if instant(self.available_at_utc) < max(
            instant(self.observation.available_at_utc),
            instant(self.observation.window.matures_at_utc),
        ):
            raise ValueError("reaction quality cannot mature before observation window")
        previous = self.observation.previous_close
        first = self.observation.first_tradable_price
        high = self.observation.high_price
        low = self.observation.low_price
        close = self.observation.close_price
        gap_return = _bps(first - previous, previous)  # type: ignore[operator]
        close_return = _bps(close - previous, previous)  # type: ignore[operator]
        range_bps = _bps(high - low, previous)  # type: ignore[operator]
        close_location = None if high == low else _bps(close - low, high - low)  # type: ignore[operator]
        if gap_return == 0 or close_return == 0:
            persistence = "FLAT_OR_MIXED"
        elif (gap_return > 0) == (close_return > 0):
            persistence = "PERSISTENT"
        else:
            persistence = "REVERSED"
        gap = self.observation.window.expectation_gap
        if gap is None or gap.standardized_gap is None or gap.standardized_gap == 0:
            label = "OBSERVED_UNLINKED"
        elif gap.standardized_gap > 0 and close_return <= 0:
            label = "FAVORABLE_WEAK_REACTION"
        elif gap.standardized_gap < 0 and close_return >= 0:
            label = "UNFAVORABLE_RESILIENT_REACTION"
        elif close_return > 0:
            label = "ALIGNED_POSITIVE"
        else:
            label = "ALIGNED_NEGATIVE"
        if label not in REACTION_LABELS:
            raise ValueError("reaction label is not registered")
        object.__setattr__(self, "gap_return_bps", gap_return)
        object.__setattr__(self, "close_return_bps", close_return)
        object.__setattr__(self, "intrawindow_range_bps", range_bps)
        object.__setattr__(self, "close_location_bps", close_location)
        object.__setattr__(self, "persistence_state", persistence)
        object.__setattr__(self, "reaction_label", label)
        if self.factor_activated:
            raise ValueError("reaction quality cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("reaction quality requires Operator registration")
        payload = {
            "available_at_utc": self.available_at_utc,
            "close_location_bps": self.close_location_bps,
            "close_return_bps": self.close_return_bps,
            "factor_activated": self.factor_activated,
            "gap_return_bps": self.gap_return_bps,
            "intrawindow_range_bps": self.intrawindow_range_bps,
            "observation_hash": self.observation.observation_hash,
            "operator_registered": self.operator_registered,
            "persistence_state": self.persistence_state,
            "quality_id": self.quality_id,
            "reaction_label": self.reaction_label,
        }
        object.__setattr__(self, "quality_hash", _hash(payload))
