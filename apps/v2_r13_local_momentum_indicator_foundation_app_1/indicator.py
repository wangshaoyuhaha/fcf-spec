import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence
from apps.v2_r12_local_technical_indicator_foundation_app_1 import RegisteredPriceSeries

from .contracts import MomentumIndicatorPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class MomentumIndicatorEvidence:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    series_id: str
    state: str
    window: int
    sample_count: int
    rsi: Decimal | None
    rate_of_change: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"MOMENTUM_READY", "BLOCKED"}:
            raise ValueError("invalid momentum indicator evidence state")
        if self.operator_review_required is not True:
            raise ValueError("momentum evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef"
            for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_momentum_indicator(
    series: RegisteredPriceSeries,
    registry: FactorRegistryEvidence,
    policy: MomentumIndicatorPolicy,
    *,
    as_of_utc: str,
) -> MomentumIndicatorEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    reasons: list[str] = []
    rsi = rate_of_change = None
    required_samples = policy.window + 1
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
    elif len(series.points) < required_samples:
        reasons.append("INSUFFICIENT_WINDOW_BLOCKED")
    else:
        values = tuple(point.close for point in series.points[-required_samples:])
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            if policy.indicator_type == "RSI":
                changes = tuple(
                    values[index] - values[index - 1]
                    for index in range(1, len(values))
                )
                gains = sum((max(change, Decimal("0")) for change in changes), Decimal("0"))
                losses = sum((max(-change, Decimal("0")) for change in changes), Decimal("0"))
                if gains == 0 and losses == 0:
                    raw_rsi = Decimal("50")
                elif losses == 0:
                    raw_rsi = Decimal("100")
                elif gains == 0:
                    raw_rsi = Decimal("0")
                else:
                    relative_strength = gains / losses
                    raw_rsi = Decimal("100") - (
                        Decimal("100") / (Decimal("1") + relative_strength)
                    )
                rsi = raw_rsi.quantize(quantum, rounding=ROUND_HALF_EVEN)
            else:
                raw_roc = (
                    (values[-1] - values[0]) / values[0] * Decimal("100")
                )
                rate_of_change = raw_roc.quantize(
                    quantum, rounding=ROUND_HALF_EVEN
                )
        reasons.append("REGISTERED_LOCAL_MOMENTUM_INDICATOR_READY")
    state = "MOMENTUM_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    payload = {
        "evaluated_at_utc": evaluated,
        "factor_definition_ref": policy.factor_definition_ref,
        "indicator_id": policy.indicator_id,
        "indicator_type": policy.indicator_type,
        "indicator_version": policy.indicator_version,
        "rate_of_change": _text(rate_of_change),
        "reason_codes": reasons,
        "registry_evidence_hash": registry.evidence_hash,
        "rsi": _text(rsi),
        "sample_count": len(series.points),
        "series_id": series.series_id,
        "state": state,
        "window": policy.window,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return MomentumIndicatorEvidence(
        policy.indicator_id,
        policy.indicator_version,
        policy.indicator_type,
        policy.factor_definition_ref,
        series.series_id,
        state,
        policy.window,
        len(series.points),
        rsi,
        rate_of_change,
        tuple(reasons),
        evaluated,
        True,
        digest,
    )
