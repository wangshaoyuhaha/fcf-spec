import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence

from .contracts import RegisteredPriceSeries, TechnicalIndicatorPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class TechnicalIndicatorEvidence:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    series_id: str
    state: str
    window: int
    sample_count: int
    sma: Decimal | None
    standard_deviation: Decimal | None
    upper_band: Decimal | None
    lower_band: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"INDICATOR_READY", "BLOCKED"}:
            raise ValueError("invalid technical indicator evidence state")
        if self.operator_review_required is not True:
            raise ValueError("technical indicator evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(character not in "0123456789abcdef" for character in self.evidence_hash):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_technical_indicator(
    series: RegisteredPriceSeries,
    registry: FactorRegistryEvidence,
    policy: TechnicalIndicatorPolicy,
    *,
    as_of_utc: str,
) -> TechnicalIndicatorEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    reasons: list[str] = []
    sma = standard_deviation = upper = lower = None
    if registry.state != "REGISTRY_READY":
        reasons.append("REGISTRY_NOT_READY")
    elif registry.registry_id != policy.registry_id or registry.registry_version != policy.registry_version:
        reasons.append("REGISTRY_IDENTITY_MISMATCH")
    elif policy.factor_definition_ref not in registry.definition_keys:
        reasons.append("FACTOR_DEFINITION_NOT_REGISTERED")
    elif series.instrument_id != policy.instrument_id or series.interval_id != policy.interval_id:
        reasons.append("SERIES_IDENTITY_MISMATCH")
    elif any(instant(point.observed_at_utc) > as_of for point in series.points):
        reasons.append("FUTURE_OBSERVATION_BLOCKED")
    elif any(instant(point.available_at_utc) > as_of for point in series.points):
        reasons.append("FUTURE_AVAILABILITY_BLOCKED")
    elif len(series.points) < policy.window:
        reasons.append("INSUFFICIENT_WINDOW_BLOCKED")
    else:
        values = tuple(point.close for point in series.points[-policy.window :])
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            mean = sum(values, Decimal("0")) / Decimal(policy.window)
            sma = mean.quantize(quantum, rounding=ROUND_HALF_EVEN)
            if policy.indicator_type == "BOLLINGER_BANDS":
                variance = sum(((value - mean) ** 2 for value in values), Decimal("0")) / Decimal(policy.window)
                raw_deviation = variance.sqrt(context=context)
                standard_deviation = raw_deviation.quantize(quantum, rounding=ROUND_HALF_EVEN)
                upper = (mean + policy.standard_deviation_multiplier * raw_deviation).quantize(quantum, rounding=ROUND_HALF_EVEN)
                lower = (mean - policy.standard_deviation_multiplier * raw_deviation).quantize(quantum, rounding=ROUND_HALF_EVEN)
        reasons.append("REGISTERED_LOCAL_TECHNICAL_INDICATOR_READY")
    state = "INDICATOR_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    payload = {
        "evaluated_at_utc": evaluated,
        "factor_definition_ref": policy.factor_definition_ref,
        "indicator_id": policy.indicator_id,
        "indicator_type": policy.indicator_type,
        "indicator_version": policy.indicator_version,
        "lower_band": _text(lower),
        "reason_codes": reasons,
        "registry_evidence_hash": registry.evidence_hash,
        "sample_count": len(series.points),
        "series_id": series.series_id,
        "sma": _text(sma),
        "standard_deviation": _text(standard_deviation),
        "state": state,
        "upper_band": _text(upper),
        "window": policy.window,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return TechnicalIndicatorEvidence(policy.indicator_id, policy.indicator_version, policy.indicator_type, policy.factor_definition_ref, series.series_id, state, policy.window, len(series.points), sma, standard_deviation, upper, lower, tuple(reasons), evaluated, True, digest)
