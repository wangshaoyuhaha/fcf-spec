import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)

from .contracts import HolidayLiquidityMeasurement, RegisteredHolidayLiquidityObservation
from .registry import LocalHolidayLiquidityRegistry


@dataclass(frozen=True)
class HolidayLiquiditySnapshot:
    subject_id: str
    market: str
    evaluated_at_utc: str
    state: str
    observation: RegisteredHolidayLiquidityObservation | None
    measurement: HolidayLiquidityMeasurement | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        allowed = {
            "MISSING_OBSERVATION",
            "MISSING",
            "STALE",
            "CONFLICT",
            "MISSING_MEASUREMENT",
            "RESOLVED",
        }
        if self.state not in allowed or self.operator_review_required is not True:
            raise ValueError("invalid holiday liquidity snapshot")


def resolve_holiday_liquidity(
    registry: LocalHolidayLiquidityRegistry,
    *,
    subject_id: str,
    market: str,
    as_of_utc: str,
) -> HolidayLiquiditySnapshot:
    subject = identifier(subject_id, "subject_id")
    market_id = identifier(market, "market")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    visible = tuple(
        sorted(
            (
                item
                for item in registry.observations
                if item.subject_id == subject
                and item.market == market_id
                and instant(item.available_at_utc) <= as_of
            ),
            key=lambda item: (item.observed_at_utc, item.observation_id),
        )
    )
    observation = visible[-1] if visible else None
    measurement = next(
        (
            item
            for item in reversed(registry.measurements)
            if observation is not None
            and item.observation.observation_hash == observation.observation_hash
            and instant(item.available_at_utc) <= as_of
        ),
        None,
    )
    if observation is None:
        state, reasons = "MISSING_OBSERVATION", [
            "NO_REGISTERED_HOLIDAY_LIQUIDITY_OBSERVATION_AT_AS_OF"
        ]
    elif observation.observation_state == "MISSING":
        state, reasons = "MISSING", ["REGISTERED_HOLIDAY_OBSERVATION_IS_MISSING"]
    elif observation.observation_state == "STALE":
        state, reasons = "STALE", ["REGISTERED_HOLIDAY_OBSERVATION_IS_STALE"]
    elif observation.observation_state == "CONFLICT":
        state, reasons = "CONFLICT", [
            "REGISTERED_HOLIDAY_OBSERVATION_IS_CONFLICTED"
        ]
    elif measurement is None:
        state, reasons = "MISSING_MEASUREMENT", [
            "NO_REGISTERED_HOLIDAY_LIQUIDITY_MEASUREMENT_AT_AS_OF"
        ]
    else:
        state, reasons = "RESOLVED", [
            "REGISTERED_HOLIDAY_LIQUIDITY_EVIDENCE_RESOLVED",
            "NO_FIXED_LAST_THREE_DAYS_RULE",
            "NO_FIXED_THRESHOLD",
            "NO_STRESS_DIRECTION",
        ]
    payload = {
        "evaluated_at_utc": evaluated,
        "market": market_id,
        "measurement": None if measurement is None else measurement.measurement_hash,
        "observation": None if observation is None else observation.observation_hash,
        "reasons": reasons,
        "state": state,
        "subject_id": subject,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return HolidayLiquiditySnapshot(
        subject,
        market_id,
        evaluated,
        state,
        observation,
        measurement,
        tuple(reasons),
        True,
        digest,
    )
