from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def identifier(value: object, name: str) -> str:
    result = str(value).strip()
    if _ID.fullmatch(result) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return result


def utc(value: object, name: str) -> str:
    result = str(value).strip()
    try:
        parsed = datetime.fromisoformat(result.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be UTC")
    return result


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def digest(payload: object) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def sha256_value(value: object, name: str) -> str:
    result = str(value).strip().lower()
    if len(result) != 64 or any(char not in "0123456789abcdef" for char in result):
        raise ValueError(f"{name} must be SHA-256")
    return result


class CandidateDisposition(str, Enum):
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ABSTAINED = "ABSTAINED"


@dataclass(frozen=True)
class DecisionAlternative:
    candidate_id: str
    disposition: CandidateDisposition
    reason_codes: tuple[str, ...]
    evidence_hashes: tuple[str, ...]
    expected_utility_bps: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", identifier(self.candidate_id, "candidate_id"))
        try:
            object.__setattr__(self, "disposition", CandidateDisposition(self.disposition))
        except (TypeError, ValueError) as exc:
            raise ValueError("disposition is not registered") from exc
        reasons = tuple(sorted({identifier(item, "reason_code") for item in self.reason_codes}))
        evidence = tuple(sorted({sha256_value(item, "evidence_hash") for item in self.evidence_hashes}))
        if not reasons or not evidence:
            raise ValueError("alternative requires reasons and registered evidence")
        object.__setattr__(self, "reason_codes", reasons)
        object.__setattr__(self, "evidence_hashes", evidence)
        if self.expected_utility_bps is not None and not isinstance(self.expected_utility_bps, int):
            raise ValueError("expected_utility_bps must be an integer or none")

    def payload(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "disposition": self.disposition.value,
            "evidence_hashes": self.evidence_hashes,
            "expected_utility_bps": self.expected_utility_bps,
            "reason_codes": self.reason_codes,
        }


@dataclass(frozen=True)
class ResearchDecisionSnapshot:
    journal_id: str
    decision_id: str
    decided_at_utc: str
    information_cutoff_utc: str
    alternatives: tuple[DecisionAlternative, ...]
    predecessor_hash: str | None = None
    operator_authored: bool = True
    automatic_decision: bool = False
    decision_rewrite_allowed: bool = False
    decision_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("journal_id", "decision_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("decided_at_utc", "information_cutoff_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.information_cutoff_utc) > instant(self.decided_at_utc):
            raise ValueError("information cutoff cannot follow the decision")
        alternatives = tuple(sorted(self.alternatives, key=lambda item: item.candidate_id))
        if not alternatives or not all(isinstance(item, DecisionAlternative) for item in alternatives):
            raise ValueError("decision requires alternatives")
        if len({item.candidate_id for item in alternatives}) != len(alternatives):
            raise ValueError("decision alternatives must be unique")
        selected = sum(item.disposition is CandidateDisposition.SELECTED for item in alternatives)
        abstained = sum(item.disposition is CandidateDisposition.ABSTAINED for item in alternatives)
        if selected > 1 or (selected == 0 and abstained == 0):
            raise ValueError("decision requires one selection or an abstention")
        object.__setattr__(self, "alternatives", alternatives)
        if self.predecessor_hash is not None:
            object.__setattr__(self, "predecessor_hash", sha256_value(self.predecessor_hash, "predecessor_hash"))
        if not self.operator_authored or self.automatic_decision or self.decision_rewrite_allowed:
            raise ValueError("decision must be immutable and Operator-authored")
        object.__setattr__(self, "decision_hash", digest({
            "alternatives": [item.payload() for item in alternatives],
            "decided_at_utc": self.decided_at_utc,
            "decision_id": self.decision_id,
            "information_cutoff_utc": self.information_cutoff_utc,
            "journal_id": self.journal_id,
            "predecessor_hash": self.predecessor_hash,
        }))


@dataclass(frozen=True)
class RegisteredOutcome:
    outcome_id: str
    decision_hash: str
    candidate_id: str
    observed_at_utc: str
    realized_utility_bps: int
    evidence_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcome_id", identifier(self.outcome_id, "outcome_id"))
        object.__setattr__(self, "candidate_id", identifier(self.candidate_id, "candidate_id"))
        object.__setattr__(self, "decision_hash", sha256_value(self.decision_hash, "decision_hash"))
        object.__setattr__(self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc"))
        if not isinstance(self.realized_utility_bps, int):
            raise ValueError("realized_utility_bps must be an integer")
        evidence = tuple(sorted({sha256_value(item, "evidence_hash") for item in self.evidence_hashes}))
        if not evidence:
            raise ValueError("outcome requires registered evidence")
        object.__setattr__(self, "evidence_hashes", evidence)


@dataclass(frozen=True)
class CounterfactualFinding:
    candidate_id: str
    disposition: str
    classification: str
    realized_utility_bps: int | None
    selected_delta_bps: int | None
    outcome_evidence_hashes: tuple[str, ...]
    post_hoc_contamination: bool = False

    def __post_init__(self) -> None:
        if self.post_hoc_contamination:
            raise ValueError("post-hoc contamination cannot be hidden")
