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


OBSERVATION_STATES = ("OBSERVED", "MISSING", "STALE", "CONFLICT")
VALUE_FIELDS = (
    "spread_bps",
    "baseline_spread_bps",
    "depth_units",
    "baseline_depth_units",
    "volume_units",
    "baseline_volume_units",
    "turnover_units",
    "baseline_turnover_units",
    "basis_bps",
    "baseline_basis_bps",
)


def _hash(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _decimal(
    value: object, name: str, *, positive: bool = False, signed: bool = False
) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not result.is_finite() or abs(result) > Decimal("1E30"):
        raise ValueError(f"{name} must be bounded")
    if not signed and result < 0:
        raise ValueError(f"{name} must be nonnegative")
    if positive and result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def _bounded_int(value: object, name: str, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= maximum:
        raise ValueError(f"{name} is outside the registered range")
    return value


def _ratio_bps(value: Decimal, baseline: Decimal) -> int:
    return int(
        ((value / baseline) * Decimal("10000")).quantize(
            Decimal("1"), rounding=ROUND_HALF_EVEN
        )
    )


@dataclass(frozen=True)
class RegisteredHolidayLiquidityObservation:
    observation_id: str
    subject_id: str
    market: str
    horizon: str
    holiday_name: str
    observed_at_utc: str
    available_at_utc: str
    holiday_length_days: int
    overseas_open_days: int
    settlement_mismatch_days: int
    expected_event_count: int
    spread_bps: Decimal | str | int | None
    baseline_spread_bps: Decimal | str | int | None
    depth_units: Decimal | str | int | None
    baseline_depth_units: Decimal | str | int | None
    volume_units: Decimal | str | int | None
    baseline_volume_units: Decimal | str | int | None
    turnover_units: Decimal | str | int | None
    baseline_turnover_units: Decimal | str | int | None
    basis_bps: Decimal | str | int | None
    baseline_basis_bps: Decimal | str | int | None
    source_event: InstitutionalCalendarEvent
    observation_state: str = "OBSERVED"
    missing_fields: tuple[str, ...] = ()
    operator_registered: bool = True
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "observation_id",
            "subject_id",
            "market",
            "horizon",
            "holiday_name",
        ):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("observed_at_utc", "available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if (
            not isinstance(self.source_event, InstitutionalCalendarEvent)
            or self.source_event.event_type != "HOLIDAY"
        ):
            raise ValueError("holiday liquidity requires registered R23 HOLIDAY evidence")
        if instant(self.available_at_utc) < max(
            instant(self.observed_at_utc), instant(self.source_event.ingested_at_utc)
        ):
            raise ValueError("observation availability cannot precede evidence")
        object.__setattr__(
            self,
            "holiday_length_days",
            _bounded_int(self.holiday_length_days, "holiday_length_days", 30),
        )
        object.__setattr__(
            self,
            "overseas_open_days",
            _bounded_int(self.overseas_open_days, "overseas_open_days", 30),
        )
        object.__setattr__(
            self,
            "settlement_mismatch_days",
            _bounded_int(
                self.settlement_mismatch_days, "settlement_mismatch_days", 30
            ),
        )
        object.__setattr__(
            self,
            "expected_event_count",
            _bounded_int(self.expected_event_count, "expected_event_count", 1000),
        )
        state = str(self.observation_state).strip().upper()
        if state not in OBSERVATION_STATES:
            raise ValueError("observation_state is not registered")
        object.__setattr__(self, "observation_state", state)
        missing = tuple(identifier(item, "missing_field") for item in self.missing_fields)
        object.__setattr__(self, "missing_fields", missing)
        if state == "OBSERVED":
            if any(getattr(self, name) is None for name in VALUE_FIELDS) or missing:
                raise ValueError("observed holiday liquidity requires complete values")
            for name in VALUE_FIELDS:
                value = _decimal(
                    getattr(self, name),
                    name,
                    positive=name
                    in {
                        "baseline_spread_bps",
                        "depth_units",
                        "baseline_depth_units",
                        "volume_units",
                        "baseline_volume_units",
                        "turnover_units",
                        "baseline_turnover_units",
                    },
                    signed=name in {"basis_bps", "baseline_basis_bps"},
                )
                object.__setattr__(self, name, value)
        elif any(getattr(self, name) is not None for name in VALUE_FIELDS) or not missing:
            raise ValueError(
                "non-observed holiday liquidity requires null values and missing_fields"
            )
        if self.operator_registered is not True:
            raise ValueError("holiday liquidity requires Operator registration")
        values = {
            name: None if getattr(self, name) is None else str(getattr(self, name))
            for name in VALUE_FIELDS
        }
        object.__setattr__(
            self,
            "observation_hash",
            _hash(
                {
                    "available_at_utc": self.available_at_utc,
                    "calendar": [
                        self.holiday_length_days,
                        self.overseas_open_days,
                        self.settlement_mismatch_days,
                        self.expected_event_count,
                    ],
                    "holiday_name": self.holiday_name,
                    "market": self.market,
                    "missing_fields": list(missing),
                    "observation_id": self.observation_id,
                    "observed_at_utc": self.observed_at_utc,
                    "source_event_hash": self.source_event.record_hash,
                    "state": state,
                    "subject_id": self.subject_id,
                    "values": values,
                }
            ),
        )


@dataclass(frozen=True)
class HolidayLiquidityMeasurement:
    measurement_id: str
    observation: RegisteredHolidayLiquidityObservation
    available_at_utc: str
    fixed_last_three_days_rule: bool = False
    fixed_threshold: bool = False
    stress_direction: bool = False
    factor_activated: bool = False
    operator_registered: bool = True
    spread_ratio_bps: int = field(init=False)
    depth_ratio_bps: int = field(init=False)
    volume_ratio_bps: int = field(init=False)
    turnover_ratio_bps: int = field(init=False)
    basis_change_bps: int = field(init=False)
    measurement_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "measurement_id", identifier(self.measurement_id, "measurement_id")
        )
        if (
            not isinstance(self.observation, RegisteredHolidayLiquidityObservation)
            or self.observation.observation_state != "OBSERVED"
        ):
            raise ValueError("measurement requires an observed holiday observation")
        object.__setattr__(
            self, "available_at_utc", utc(self.available_at_utc, "available_at_utc")
        )
        if instant(self.available_at_utc) < instant(self.observation.available_at_utc):
            raise ValueError("measurement availability cannot precede observation")
        ratios = (
            _ratio_bps(
                self.observation.spread_bps, self.observation.baseline_spread_bps
            ),
            _ratio_bps(
                self.observation.depth_units, self.observation.baseline_depth_units
            ),
            _ratio_bps(
                self.observation.volume_units,
                self.observation.baseline_volume_units,
            ),
            _ratio_bps(
                self.observation.turnover_units,
                self.observation.baseline_turnover_units,
            ),
        )
        basis_change = int(
            (
                self.observation.basis_bps - self.observation.baseline_basis_bps
            ).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)
        )
        for name, value in zip(
            (
                "spread_ratio_bps",
                "depth_ratio_bps",
                "volume_ratio_bps",
                "turnover_ratio_bps",
            ),
            ratios,
        ):
            object.__setattr__(self, name, value)
        object.__setattr__(self, "basis_change_bps", basis_change)
        if self.fixed_last_three_days_rule:
            raise ValueError("fixed last-three-days rule is prohibited")
        if self.fixed_threshold:
            raise ValueError("fixed threshold is prohibited")
        if self.stress_direction:
            raise ValueError("holiday evidence cannot claim stress direction")
        if self.factor_activated:
            raise ValueError("holiday evidence cannot activate a factor")
        if self.operator_registered is not True:
            raise ValueError("measurement requires Operator registration")
        object.__setattr__(
            self,
            "measurement_hash",
            _hash(
                {
                    "available_at_utc": self.available_at_utc,
                    "basis_change_bps": basis_change,
                    "measurement_id": self.measurement_id,
                    "observation_hash": self.observation.observation_hash,
                    "ratios": ratios,
                }
            ),
        )
