from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1 import FactorDefinition
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import sha256_text


LIFECYCLE_STATES = (
    "BACKTESTED",
    "CONTRACT_DEFINED",
    "DATA_AVAILABLE",
    "DEFERRED",
    "EXPIRED",
    "OPERATOR_APPROVED",
    "POINT_IN_TIME_VALIDATED",
    "REGISTERED_PAPER_FACTOR",
    "REJECTED",
    "RESEARCH_PROPOSAL",
    "RETIRED",
    "REVOKED",
    "ROBUSTNESS_REVIEWED",
    "SUPERSEDED",
)
TERMINAL_STATES = ("DEFERRED", "EXPIRED", "REJECTED", "RETIRED", "REVOKED", "SUPERSEDED")
ALLOWED_TRANSITIONS = {
    "RESEARCH_PROPOSAL": ("CONTRACT_DEFINED", "DEFERRED", "EXPIRED", "REJECTED", "SUPERSEDED"),
    "CONTRACT_DEFINED": ("DATA_AVAILABLE", "DEFERRED", "EXPIRED", "REJECTED", "SUPERSEDED"),
    "DATA_AVAILABLE": ("DEFERRED", "EXPIRED", "POINT_IN_TIME_VALIDATED", "REJECTED", "SUPERSEDED"),
    "POINT_IN_TIME_VALIDATED": ("BACKTESTED", "DEFERRED", "EXPIRED", "REJECTED", "SUPERSEDED"),
    "BACKTESTED": ("DEFERRED", "EXPIRED", "REJECTED", "ROBUSTNESS_REVIEWED", "SUPERSEDED"),
    "ROBUSTNESS_REVIEWED": ("DEFERRED", "EXPIRED", "OPERATOR_APPROVED", "REJECTED", "SUPERSEDED"),
    "OPERATOR_APPROVED": ("REGISTERED_PAPER_FACTOR", "REVOKED"),
    "REGISTERED_PAPER_FACTOR": ("EXPIRED", "RETIRED", "REVOKED", "SUPERSEDED"),
}


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


@dataclass(frozen=True)
class InstitutionalFactorCandidate:
    candidate_id: str
    factor_definition: FactorDefinition
    hypothesis_id: str
    submitted_at_utc: str
    expires_at_utc: str
    supporting_evidence_hashes: tuple[str, ...]
    negative_evidence_hashes: tuple[str, ...] = ()
    operator_registered: bool = True
    calculation_activation_allowed: bool = False
    scoring_allowed: bool = False
    candidate_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", identifier(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "hypothesis_id", identifier(self.hypothesis_id, "hypothesis_id"))
        for name in ("submitted_at_utc", "expires_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.expires_at_utc) <= instant(self.submitted_at_utc):
            raise ValueError("candidate expiry must follow submission")
        if not isinstance(self.factor_definition, FactorDefinition):
            raise ValueError("candidate requires an R11 FactorDefinition")
        if self.factor_definition.lifecycle == "RETIRED":
            raise ValueError("retired factor definition cannot become a candidate")
        supporting = tuple(sorted(sha256_text(item, "supporting_evidence_hash") for item in self.supporting_evidence_hashes))
        negative = tuple(sorted(sha256_text(item, "negative_evidence_hash") for item in self.negative_evidence_hashes))
        if not supporting or len(set(supporting)) != len(supporting) or len(set(negative)) != len(negative):
            raise ValueError("candidate evidence hashes must be nonempty and unique")
        object.__setattr__(self, "supporting_evidence_hashes", supporting)
        object.__setattr__(self, "negative_evidence_hashes", negative)
        if self.operator_registered is not True:
            raise ValueError("candidate requires Operator registration")
        if self.calculation_activation_allowed or self.scoring_allowed:
            raise ValueError("candidate cannot activate calculation or scoring")
        object.__setattr__(
            self,
            "candidate_hash",
            _digest(
                {
                    "candidate_id": self.candidate_id,
                    "expires_at_utc": self.expires_at_utc,
                    "factor_ref": self.factor_definition.natural_key,
                    "hypothesis_id": self.hypothesis_id,
                    "negative_evidence_hashes": list(negative),
                    "submitted_at_utc": self.submitted_at_utc,
                    "supporting_evidence_hashes": list(supporting),
                }
            ),
        )


@dataclass(frozen=True)
class OperatorLifecycleDecision:
    decision_id: str
    candidate_id: str
    from_state: str
    to_state: str
    decided_at_utc: str
    operator_id: str
    rationale_codes: tuple[str, ...]
    predecessor_decision_hash: str | None = None
    operator_authored: bool = True
    automatic_decision: bool = False
    factor_activation_allowed: bool = False
    decision_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("decision_id", "candidate_id", "operator_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        source, target = str(self.from_state).strip().upper(), str(self.to_state).strip().upper()
        if source not in LIFECYCLE_STATES or target not in LIFECYCLE_STATES:
            raise ValueError("lifecycle state is not registered")
        if target not in ALLOWED_TRANSITIONS.get(source, ()):
            raise ValueError("illegal factor lifecycle transition")
        object.__setattr__(self, "from_state", source)
        object.__setattr__(self, "to_state", target)
        object.__setattr__(self, "decided_at_utc", utc(self.decided_at_utc, "decided_at_utc"))
        reasons = tuple(sorted(identifier(item, "rationale_code") for item in self.rationale_codes))
        if not reasons or len(set(reasons)) != len(reasons):
            raise ValueError("decision requires unique rationale codes")
        object.__setattr__(self, "rationale_codes", reasons)
        if self.predecessor_decision_hash is not None:
            object.__setattr__(self, "predecessor_decision_hash", sha256_text(self.predecessor_decision_hash, "predecessor_decision_hash"))
        if self.operator_authored is not True or self.automatic_decision:
            raise ValueError("lifecycle decision must be Operator-authored")
        if self.factor_activation_allowed:
            raise ValueError("lifecycle decision cannot activate a factor")
        object.__setattr__(
            self,
            "decision_hash",
            _digest(
                {
                    "candidate_id": self.candidate_id,
                    "decided_at_utc": self.decided_at_utc,
                    "decision_id": self.decision_id,
                    "from_state": source,
                    "operator_id": self.operator_id,
                    "predecessor_decision_hash": self.predecessor_decision_hash,
                    "rationale_codes": list(reasons),
                    "to_state": target,
                }
            ),
        )
