import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence
from apps.v2_r15_local_volatility_indicator_foundation_app_1 import (
    RegisteredOHLCSeries,
)

from .contracts import ChannelIndicatorPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class ChannelIndicatorEvidence:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    series_id: str
    state: str
    window: int
    sample_count: int
    upper_channel: Decimal | None
    lower_channel: Decimal | None
    midpoint: Decimal | None
    channel_width: Decimal | None
    close_position_percent: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"CHANNEL_READY", "BLOCKED"}:
            raise ValueError("invalid channel indicator evidence state")
        if self.operator_review_required is not True:
            raise ValueError("channel evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_channel_indicator(
    series: RegisteredOHLCSeries,
    registry: FactorRegistryEvidence,
    policy: ChannelIndicatorPolicy,
    *,
    as_of_utc: str,
) -> ChannelIndicatorEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    reasons: list[str] = []
    upper = lower = midpoint = width = position = None
    if registry.state != "REGISTRY_READY":
        reasons.append("REGISTRY_NOT_READY")
    elif (
        registry.registry_id != policy.registry_id
        or registry.registry_version != policy.registry_version
    ):
        reasons.append("REGISTRY_IDENTITY_MISMATCH")
    elif policy.factor_definition_ref not in registry.definition_keys:
        reasons.append("FACTOR_DEFINITION_NOT_REGISTERED")
    elif (
        series.instrument_id != policy.instrument_id
        or series.interval_id != policy.interval_id
    ):
        reasons.append("SERIES_IDENTITY_MISMATCH")
    elif any(instant(point.observed_at_utc) > as_of for point in series.points):
        reasons.append("FUTURE_OBSERVATION_BLOCKED")
    elif any(instant(point.available_at_utc) > as_of for point in series.points):
        reasons.append("FUTURE_AVAILABILITY_BLOCKED")
    elif len(series.points) < policy.window:
        reasons.append("INSUFFICIENT_WINDOW_BLOCKED")
    else:
        points = series.points[-policy.window :]
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            raw_upper = max(point.high for point in points)
            raw_lower = min(point.low for point in points)
            raw_width = raw_upper - raw_lower
            raw_midpoint = (raw_upper + raw_lower) / Decimal("2")
            raw_position = (
                Decimal("50")
                if raw_width == 0
                else (points[-1].close - raw_lower) / raw_width * Decimal("100")
            )
            upper = raw_upper.quantize(quantum, rounding=ROUND_HALF_EVEN)
            lower = raw_lower.quantize(quantum, rounding=ROUND_HALF_EVEN)
            midpoint = raw_midpoint.quantize(quantum, rounding=ROUND_HALF_EVEN)
            width = raw_width.quantize(quantum, rounding=ROUND_HALF_EVEN)
            position = raw_position.quantize(quantum, rounding=ROUND_HALF_EVEN)
        reasons.append("REGISTERED_LOCAL_CHANNEL_INDICATOR_READY")
    state = "CHANNEL_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    payload = {
        "channel_width": _text(width),
        "close_position_percent": _text(position),
        "evaluated_at_utc": evaluated,
        "factor_definition_ref": policy.factor_definition_ref,
        "indicator_id": policy.indicator_id,
        "indicator_type": policy.indicator_type,
        "indicator_version": policy.indicator_version,
        "lower_channel": _text(lower),
        "midpoint": _text(midpoint),
        "reason_codes": reasons,
        "registry_evidence_hash": registry.evidence_hash,
        "sample_count": len(series.points),
        "series_id": series.series_id,
        "state": state,
        "upper_channel": _text(upper),
        "window": policy.window,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return ChannelIndicatorEvidence(
        policy.indicator_id,
        policy.indicator_version,
        policy.indicator_type,
        policy.factor_definition_ref,
        series.series_id,
        state,
        policy.window,
        len(series.points),
        upper,
        lower,
        midpoint,
        width,
        position,
        tuple(reasons),
        evaluated,
        True,
        digest,
    )
