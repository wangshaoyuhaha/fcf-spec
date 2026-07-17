import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc

from .contracts import RegisteredTurnoverObservation, TurnoverPolicy


def _text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return "0" if normalized == 0 else format(normalized, "f")


@dataclass(frozen=True)
class TurnoverEvidence:
    definition_id: str
    definition_version: str
    observation_id: str
    state: str
    denominator_type: str
    output_unit: str
    traded_volume: Decimal
    share_base: Decimal
    turnover: Decimal | None
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"TURNOVER_READY", "BLOCKED"}:
            raise ValueError("invalid turnover evidence state")
        if self.operator_review_required is not True:
            raise ValueError("turnover evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def build_turnover(observation: RegisteredTurnoverObservation, policy: TurnoverPolicy, *, as_of_utc: str) -> TurnoverEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    reasons: list[str] = []
    turnover: Decimal | None = None
    state = "BLOCKED"
    if instant(observation.observed_at_utc) > as_of:
        reasons.append("FUTURE_OBSERVATION_BLOCKED")
    elif instant(observation.volume_available_at_utc) > as_of:
        reasons.append("FUTURE_VOLUME_AVAILABILITY_BLOCKED")
    elif instant(observation.share_base_available_at_utc) > as_of:
        reasons.append("FUTURE_SHARE_BASE_AVAILABILITY_BLOCKED")
    elif observation.instrument_id != policy.instrument_id:
        reasons.append("INSTRUMENT_MISMATCH")
    elif observation.phase != policy.phase or observation.interval_id != policy.interval_id:
        reasons.append("SESSION_IDENTITY_MISMATCH")
    elif observation.slot_index != policy.slot_index:
        reasons.append("SLOT_MISMATCH")
    elif observation.denominator_type != policy.denominator_type:
        reasons.append("DENOMINATOR_TYPE_MISMATCH")
    elif observation.share_base == 0:
        reasons.append("ZERO_SHARE_BASE_BLOCKED")
    else:
        multiplier = Decimal("100") if policy.output_unit == "PERCENT" else Decimal("1")
        quantum = Decimal(1).scaleb(-policy.decimal_places)
        with localcontext() as context:
            context.prec = 96
            turnover = ((observation.traded_volume / observation.share_base) * multiplier).quantize(quantum, rounding=ROUND_HALF_EVEN)
        state = "TURNOVER_READY"
        reasons.append("REGISTERED_LOCAL_TURNOVER_READY")
    payload = {
        "definition_id": policy.definition_id,
        "definition_version": policy.definition_version,
        "denominator_type": policy.denominator_type,
        "evaluated_at_utc": evaluated,
        "observation_id": observation.observation_id,
        "output_unit": policy.output_unit,
        "reason_codes": reasons,
        "share_base": _text(observation.share_base),
        "state": state,
        "traded_volume": _text(observation.traded_volume),
        "turnover": _text(turnover),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return TurnoverEvidence(policy.definition_id, policy.definition_version, observation.observation_id, state, policy.denominator_type, policy.output_unit, observation.traded_volume, observation.share_base, turnover, tuple(reasons), evaluated, True, digest)
