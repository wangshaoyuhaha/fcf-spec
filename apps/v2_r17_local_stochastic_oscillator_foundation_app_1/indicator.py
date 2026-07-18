import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence
from apps.v2_r15_local_volatility_indicator_foundation_app_1 import (
    RegisteredOHLCSeries,
)

from .contracts import StochasticIndicatorPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class StochasticIndicatorEvidence:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    series_id: str
    state: str
    window: int
    smoothing_period: int
    seed: Decimal
    sample_count: int
    rsv: Decimal | None
    k_value: Decimal | None
    d_value: Decimal | None
    j_value: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"STOCHASTIC_READY", "BLOCKED"}:
            raise ValueError("invalid stochastic indicator evidence state")
        if self.operator_review_required is not True:
            raise ValueError("stochastic evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_stochastic_indicator(
    series: RegisteredOHLCSeries,
    registry: FactorRegistryEvidence,
    policy: StochasticIndicatorPolicy,
    *,
    as_of_utc: str,
) -> StochasticIndicatorEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    reasons: list[str] = []
    rsv = k_value = d_value = j_value = None
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
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        period = Decimal(policy.smoothing_period)
        prior_weight = Decimal(policy.smoothing_period - 1)
        with localcontext() as context:
            context.prec = 96
            raw_k = policy.seed
            raw_d = policy.seed
            raw_rsv = policy.seed
            for end in range(policy.window - 1, len(series.points)):
                points = series.points[end - policy.window + 1 : end + 1]
                upper = max(point.high for point in points)
                lower = min(point.low for point in points)
                width = upper - lower
                raw_rsv = (
                    Decimal("50")
                    if width == 0
                    else (points[-1].close - lower) / width * Decimal("100")
                )
                raw_k = (prior_weight * raw_k + raw_rsv) / period
                raw_d = (prior_weight * raw_d + raw_k) / period
            raw_j = Decimal("3") * raw_k - Decimal("2") * raw_d
            rsv = raw_rsv.quantize(quantum, rounding=ROUND_HALF_EVEN)
            k_value = raw_k.quantize(quantum, rounding=ROUND_HALF_EVEN)
            d_value = raw_d.quantize(quantum, rounding=ROUND_HALF_EVEN)
            j_value = raw_j.quantize(quantum, rounding=ROUND_HALF_EVEN)
        reasons.append("REGISTERED_LOCAL_STOCHASTIC_INDICATOR_READY")
    state = "STOCHASTIC_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    payload = {
        "d_value": _text(d_value),
        "evaluated_at_utc": evaluated,
        "factor_definition_ref": policy.factor_definition_ref,
        "indicator_id": policy.indicator_id,
        "indicator_type": policy.indicator_type,
        "indicator_version": policy.indicator_version,
        "j_value": _text(j_value),
        "k_value": _text(k_value),
        "reason_codes": reasons,
        "registry_evidence_hash": registry.evidence_hash,
        "rsv": _text(rsv),
        "sample_count": len(series.points),
        "seed": _text(policy.seed),
        "series_id": series.series_id,
        "smoothing_period": policy.smoothing_period,
        "state": state,
        "window": policy.window,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return StochasticIndicatorEvidence(
        policy.indicator_id,
        policy.indicator_version,
        policy.indicator_type,
        policy.factor_definition_ref,
        series.series_id,
        state,
        policy.window,
        policy.smoothing_period,
        policy.seed,
        len(series.points),
        rsv,
        k_value,
        d_value,
        j_value,
        tuple(reasons),
        evaluated,
        True,
        digest,
    )
