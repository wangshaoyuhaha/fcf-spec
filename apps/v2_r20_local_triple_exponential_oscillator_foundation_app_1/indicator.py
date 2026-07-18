import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorRegistryEvidence
from apps.v2_r12_local_technical_indicator_foundation_app_1 import RegisteredPriceSeries

from .contracts import TrixPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


def _ema_sequence(values: tuple[Decimal, ...], window: int) -> tuple[Decimal, ...]:
    alpha = Decimal(2) / Decimal(window + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append(result[-1] + alpha * (value - result[-1]))
    return tuple(result)


@dataclass(frozen=True)
class TrixEvidence:
    indicator_id: str
    indicator_version: str
    indicator_type: str
    factor_definition_ref: str
    series_id: str
    state: str
    smoothing_window: int
    signal_window: int
    required_samples: int
    sample_count: int
    trix_line: Decimal | None
    signal_line: Decimal | None
    histogram: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"TRIX_READY", "BLOCKED"}:
            raise ValueError("invalid TRIX evidence state")
        if self.operator_review_required is not True:
            raise ValueError("TRIX evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(character not in "0123456789abcdef" for character in self.evidence_hash):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_trix(series: RegisteredPriceSeries, registry: FactorRegistryEvidence, policy: TrixPolicy, *, as_of_utc: str) -> TrixEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    required_samples = 3 * policy.smoothing_window + policy.signal_window - 2
    reasons: list[str] = []
    trix_line = signal_line = histogram = None
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
    elif len(series.points) < required_samples:
        reasons.append("INSUFFICIENT_WINDOW_BLOCKED")
    else:
        values = tuple(point.close for point in series.points[-required_samples:])
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            ema_one = _ema_sequence(values, policy.smoothing_window)
            ema_two = _ema_sequence(ema_one, policy.smoothing_window)
            ema_three = _ema_sequence(ema_two, policy.smoothing_window)
            trix_values = tuple((ema_three[index] - ema_three[index - 1]) / ema_three[index - 1] * Decimal("100") for index in range(1, len(ema_three)))
            raw_trix = trix_values[-1]
            raw_signal = _ema_sequence(trix_values, policy.signal_window)[-1]
            trix_line = raw_trix.quantize(quantum, rounding=ROUND_HALF_EVEN)
            signal_line = raw_signal.quantize(quantum, rounding=ROUND_HALF_EVEN)
            histogram = (raw_trix - raw_signal).quantize(quantum, rounding=ROUND_HALF_EVEN)
        reasons.append("REGISTERED_LOCAL_TRIX_READY")
    state = "TRIX_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    payload = {"evaluated_at_utc": evaluated, "factor_definition_ref": policy.factor_definition_ref, "histogram": _text(histogram), "indicator_id": policy.indicator_id, "indicator_type": policy.indicator_type, "indicator_version": policy.indicator_version, "reason_codes": reasons, "registry_evidence_hash": registry.evidence_hash, "required_samples": required_samples, "sample_count": len(series.points), "series_id": series.series_id, "signal_line": _text(signal_line), "signal_window": policy.signal_window, "smoothing_window": policy.smoothing_window, "state": state, "trix_line": _text(trix_line)}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return TrixEvidence(policy.indicator_id, policy.indicator_version, policy.indicator_type, policy.factor_definition_ref, series.series_id, state, policy.smoothing_window, policy.signal_window, required_samples, len(series.points), trix_line, signal_line, histogram, tuple(reasons), evaluated, True, digest)
