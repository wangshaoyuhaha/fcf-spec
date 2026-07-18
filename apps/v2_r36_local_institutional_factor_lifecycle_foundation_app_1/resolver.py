from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import InstitutionalFactorCandidate, OperatorLifecycleDecision, TERMINAL_STATES
from .registry import LocalInstitutionalFactorLifecycleRegistry


TERMINAL_REASON_CODES = {
    "DEFERRED": "DEFERRED_HISTORY_PRESERVED",
    "EXPIRED": "EXPIRED_HISTORY_PRESERVED",
    "REJECTED": "REJECTED_HISTORY_PRESERVED",
    "RETIRED": "RETIRED_HISTORY_PRESERVED",
    "REVOKED": "REVOKED_HISTORY_PRESERVED",
    "SUPERSEDED": "SUPERSEDED_HISTORY_PRESERVED",
}


@dataclass(frozen=True)
class FactorLifecycleSnapshot:
    candidate_id: str
    evaluated_at_utc: str
    state: str
    candidate: InstitutionalFactorCandidate | None
    decisions: tuple[OperatorLifecycleDecision, ...]
    terminal: bool
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str


def resolve_factor_lifecycle(registry: LocalInstitutionalFactorLifecycleRegistry, *, candidate_id: str, as_of_utc: str) -> FactorLifecycleSnapshot:
    identifier_value = identifier(candidate_id, "candidate_id")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    candidate = next((item for item in registry.candidates if item.candidate_id == identifier_value), None)
    if candidate is None:
        state, visible, terminal, reasons = "MISSING", (), False, ("NO_REGISTERED_FACTOR_CANDIDATE",)
    elif instant(candidate.submitted_at_utc) > as_of:
        state, visible, terminal, reasons = "FUTURE_ONLY", (), False, ("FACTOR_CANDIDATE_NOT_YET_AVAILABLE",)
    else:
        visible = tuple(item for item in registry.history(identifier_value) if instant(item.decided_at_utc) <= as_of)
        state = visible[-1].to_state if visible else "RESEARCH_PROPOSAL"
        terminal = state in TERMINAL_STATES
        reasons_list = ["REGISTERED_OPERATOR_LIFECYCLE_HISTORY"]
        if state in TERMINAL_REASON_CODES:
            reasons_list.append(TERMINAL_REASON_CODES[state])
        if instant(candidate.expires_at_utc) <= as_of and not terminal:
            reasons_list.append("EXPIRY_OPERATOR_REVIEW_REQUIRED")
        if state in {"OPERATOR_APPROVED", "REGISTERED_PAPER_FACTOR"}:
            reasons_list.append("NO_FACTOR_ACTIVATION")
        reasons = tuple(reasons_list)
    payload = {"candidate": None if candidate is None else candidate.candidate_hash, "decisions": [item.decision_hash for item in visible], "evaluated_at_utc": evaluated, "reasons": list(reasons), "state": state}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return FactorLifecycleSnapshot(identifier_value, evaluated, state, candidate, visible, terminal, tuple(reasons), True, digest)
