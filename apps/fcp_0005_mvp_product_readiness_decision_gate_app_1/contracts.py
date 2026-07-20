from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_DIMENSIONS = (
    "COMMERCIAL_EVIDENCE",
    "DATA_AND_COMPUTE_ECONOMICS",
    "DATA_RIGHTS_AND_RETENTION",
    "LEGAL_AND_REGULATORY_REVIEW",
    "REPOSITORY_LICENSE_DECISION",
    "TARGET_SUCCESS_AND_STOP_RULES",
)
EVIDENCE_STATES = ("BLOCKED", "READY")
CANDIDATE_STATES = ("BLOCKED", "NEEDS_EVIDENCE", "READY_FOR_OPERATOR_DECISION")
DECISION_STATES = ("ABSTAIN", "READY_FOR_OPERATOR_DECISION")


def safe_id(value: str, name: str) -> str:
    normalized = str(value).strip()
    if not SAFE_ID.fullmatch(normalized):
        raise ValueError(f"{name} is not a safe identifier")
    return normalized


def utc_time(value: datetime, name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{name} must be timezone-aware UTC")
    return value


def digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class MvpMarketCandidate:
    candidate_id: str
    market_id: str
    adapter_id: str
    horizon_id: str
    target_id: str
    candidate_hash: str = field(init=False)

    def __post_init__(self) -> None:
        values = {
            name: safe_id(getattr(self, name), name)
            for name in (
                "candidate_id",
                "market_id",
                "adapter_id",
                "horizon_id",
                "target_id",
            )
        }
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "candidate_hash", digest(values))


@dataclass(frozen=True)
class ProductReadinessEvidence:
    evidence_id: str
    candidate_id: str
    dimension: str
    artifact_id: str
    available_at: datetime
    expires_at: datetime
    state: str
    evidence_digest: str
    registered_local_only: bool = True
    operator_review_required: bool = True
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        values = {
            name: safe_id(getattr(self, name), name)
            for name in ("evidence_id", "candidate_id", "artifact_id")
        }
        if self.dimension not in EVIDENCE_DIMENSIONS:
            raise ValueError("readiness evidence dimension is not registered")
        if self.state not in EVIDENCE_STATES:
            raise ValueError("readiness evidence state is not registered")
        available_at = utc_time(self.available_at, "available_at")
        expires_at = utc_time(self.expires_at, "expires_at")
        if expires_at <= available_at:
            raise ValueError("readiness evidence expiry must follow availability")
        if not HEX_64.fullmatch(self.evidence_digest):
            raise ValueError("evidence_digest must be lowercase SHA-256")
        if not self.registered_local_only or not self.operator_review_required:
            raise ValueError("readiness evidence must remain registered-local and reviewed")
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "evidence_hash",
            digest(
                {
                    **values,
                    "available_at": available_at.isoformat(),
                    "dimension": self.dimension,
                    "evidence_digest": self.evidence_digest,
                    "expires_at": expires_at.isoformat(),
                    "operator_review_required": self.operator_review_required,
                    "registered_local_only": self.registered_local_only,
                    "state": self.state,
                }
            ),
        )


@dataclass(frozen=True)
class MvpProductReadinessRegistry:
    candidates: tuple[MvpMarketCandidate, ...]
    evidence: tuple[ProductReadinessEvidence, ...]
    proposal_id: str = "FCF-FCP-0005"
    proposal_status: str = "NEEDS_RESEARCH"
    operator_decision: str = "PENDING"
    phase_id: str = "NONE"
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        candidates = tuple(sorted(self.candidates, key=lambda item: item.candidate_id))
        evidence = tuple(sorted(self.evidence, key=lambda item: item.evidence_id))
        candidate_ids = tuple(item.candidate_id for item in candidates)
        market_ids = tuple(item.market_id for item in candidates)
        evidence_ids = tuple(item.evidence_id for item in evidence)
        if not candidates:
            raise ValueError("at least one MVP market candidate is required")
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("MVP candidate ids must be unique")
        if len(market_ids) != len(set(market_ids)):
            raise ValueError("one candidate per market is allowed")
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("readiness evidence ids must be unique")
        if any(item.candidate_id not in candidate_ids for item in evidence):
            raise ValueError("readiness evidence references an unknown candidate")
        if self.proposal_id != "FCF-FCP-0005":
            raise ValueError("registry proposal id is not FCF-FCP-0005")
        if self.proposal_status != "NEEDS_RESEARCH" or self.operator_decision != "PENDING":
            raise ValueError("FCP-0005 must remain pending research")
        if self.phase_id != "NONE":
            raise ValueError("readiness registry cannot authorize a phase")
        object.__setattr__(self, "candidates", candidates)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(
            self,
            "registry_hash",
            digest(
                {
                    "candidate_hashes": tuple(item.candidate_hash for item in candidates),
                    "evidence_hashes": tuple(item.evidence_hash for item in evidence),
                    "operator_decision": self.operator_decision,
                    "phase_id": self.phase_id,
                    "proposal_id": self.proposal_id,
                    "proposal_status": self.proposal_status,
                }
            ),
        )


@dataclass(frozen=True)
class CandidateReadinessResult:
    candidate_id: str
    state: str
    evidence_ids: tuple[str, ...]
    missing_dimensions: tuple[str, ...]
    stale_dimensions: tuple[str, ...]
    blocked_dimensions: tuple[str, ...]
    conflict_dimensions: tuple[str, ...]
    not_yet_available_dimensions: tuple[str, ...]
    readiness_hash: str

    def __post_init__(self) -> None:
        safe_id(self.candidate_id, "candidate_id")
        if self.state not in CANDIDATE_STATES:
            raise ValueError("candidate readiness state is not registered")


@dataclass(frozen=True)
class MvpProductReadinessDecision:
    state: str
    as_of_time: datetime
    registry_hash: str
    candidate_results: tuple[CandidateReadinessResult, ...]
    ready_candidate_ids: tuple[str, ...]
    selected_market_id: None
    operator_review_required: bool
    automatic_ranking_applied: bool
    production_gap_closure_claimed: bool
    decision_hash: str

    def __post_init__(self) -> None:
        if self.state not in DECISION_STATES:
            raise ValueError("MVP readiness decision state is not registered")
        utc_time(self.as_of_time, "as_of_time")
        if self.selected_market_id is not None:
            raise ValueError("readiness decision cannot select a market")
        if not self.operator_review_required:
            raise ValueError("MVP readiness decision requires Operator review")
        if self.automatic_ranking_applied or self.production_gap_closure_claimed:
            raise ValueError("readiness decision cannot claim product authority")
