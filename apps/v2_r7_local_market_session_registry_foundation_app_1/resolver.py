from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import instant, utc

from .contracts import MarketSessionDefinition


@dataclass(frozen=True)
class SessionResolutionEvidence:
    registry_id: str
    definition_hash: str
    observed_at_utc: str
    evaluated_at_utc: str
    state: str
    phase: str | None
    interval_id: str | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"RESOLVED", "BLOCKED"}:
            raise ValueError("invalid session resolution state")
        if self.operator_review_required is not True:
            raise ValueError("session resolution requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")


def resolve_market_session(
    definition: MarketSessionDefinition,
    *,
    observed_at_utc: str,
    as_of_utc: str,
) -> SessionResolutionEvidence:
    observed_text = utc(observed_at_utc, "observed_at_utc")
    evaluated_text = utc(as_of_utc, "as_of_utc")
    observed = instant(observed_text)
    as_of = instant(evaluated_text)
    if observed > as_of:
        raise ValueError("session resolution cannot use future observation")

    reasons: list[str] = []
    phase: str | None = None
    interval_id: str | None = None
    state = "BLOCKED"
    if instant(definition.available_at_utc) > as_of:
        reasons.append("DEFINITION_NOT_AVAILABLE_AT_AS_OF")
    elif not (
        instant(definition.effective_from_utc)
        <= observed
        < instant(definition.expires_at_utc)
    ):
        reasons.append("DEFINITION_NOT_EFFECTIVE")
    else:
        matches = tuple(
            item
            for item in definition.intervals
            if instant(item.start_at_utc) <= observed < instant(item.end_at_utc)
        )
        if not matches:
            reasons.append("OUTSIDE_REGISTERED_SESSION")
        elif instant(matches[0].available_at_utc) > as_of:
            reasons.append("INTERVAL_NOT_AVAILABLE_AT_AS_OF")
        else:
            state = "RESOLVED"
            phase = matches[0].phase
            interval_id = matches[0].interval_id
            reasons.append("REGISTERED_SESSION_RESOLVED")

    payload = {
        "definition_hash": definition.definition_hash,
        "evaluated_at_utc": evaluated_text,
        "interval_id": interval_id,
        "observed_at_utc": observed_text,
        "phase": phase,
        "reason_codes": reasons,
        "registry_id": definition.registry_id,
        "state": state,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return SessionResolutionEvidence(
        registry_id=definition.registry_id,
        definition_hash=definition.definition_hash,
        observed_at_utc=observed_text,
        evaluated_at_utc=evaluated_text,
        state=state,
        phase=phase,
        interval_id=interval_id,
        reason_codes=tuple(reasons),
        operator_review_required=True,
        evidence_hash=digest,
    )
