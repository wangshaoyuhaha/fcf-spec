from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    identifier,
    instant,
    utc,
)
from apps.v2_r23_local_institutional_calendar_evidence_foundation_app_1.contracts import (
    sha256_text,
)


EVIDENCE_SCOPES = ("MACRO", "SECTOR", "INSTRUMENT", "MICROSTRUCTURE")
EVIDENCE_STANCES = ("SUPPORTING", "OPPOSING", "NEUTRAL")
EVIDENCE_USABILITY = ("USABLE", "AMBIGUOUS", "MISSING", "BLOCKED")
DEPENDENCE_TYPES = ("INDEPENDENT", "SHARED_SOURCE", "DERIVED", "CORRELATED")
BUDGET_STATES = ("READY_FOR_OPERATOR_REVIEW", "ABSTAIN", "BLOCKED")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _basis_points(value: int, name: str, *, positive: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be integer basis points")
    minimum = 1 if positive else 0
    if value < minimum or value > 10_000:
        raise ValueError(f"{name} is outside registered basis-point bounds")
    return value


def _identifiers(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    normalized = tuple(sorted(identifier(value, name) for value in values))
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} values must be unique")
    return normalized


def _hashes(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    normalized = tuple(sorted(sha256_text(value, name) for value in values))
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{name} values must be unique")
    return normalized


@dataclass(frozen=True)
class RegisteredEvidenceClaim:
    claim_id: str
    scope: str
    stance: str
    usability: str
    requested_confidence_bps: int
    dependence_group_id: str
    taxonomy_ids: tuple[str, ...]
    source_artifact_hashes: tuple[str, ...]
    reason_codes: tuple[str, ...]
    observed_at_utc: str
    available_at_utc: str
    operator_registered: bool = True
    claim_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("claim_id", "dependence_group_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name, allowed in (
            ("scope", EVIDENCE_SCOPES),
            ("stance", EVIDENCE_STANCES),
            ("usability", EVIDENCE_USABILITY),
        ):
            value = str(getattr(self, name)).strip().upper()
            if value not in allowed:
                raise ValueError(f"{name} is not registered")
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "requested_confidence_bps",
            _basis_points(self.requested_confidence_bps, "requested_confidence_bps"),
        )
        taxonomies = _identifiers(tuple(self.taxonomy_ids), "taxonomy_id")
        if not taxonomies:
            raise ValueError("evidence claim requires taxonomy attribution")
        if self.usability == "AMBIGUOUS" and len(taxonomies) < 2:
            raise ValueError("ambiguous evidence requires multiple taxonomy ids")
        hashes = _hashes(tuple(self.source_artifact_hashes), "source_artifact_hash")
        if self.usability in {"USABLE", "AMBIGUOUS"} and not hashes:
            raise ValueError("usable or ambiguous evidence requires registered sources")
        if self.usability == "MISSING" and self.requested_confidence_bps != 0:
            raise ValueError("missing evidence cannot request confidence")
        reasons = _identifiers(tuple(self.reason_codes), "reason_code")
        if not reasons:
            raise ValueError("evidence claim requires reason codes")
        observed = utc(self.observed_at_utc, "observed_at_utc")
        available = utc(self.available_at_utc, "available_at_utc")
        if instant(available) < instant(observed):
            raise ValueError("evidence availability cannot precede observation")
        if self.operator_registered is not True:
            raise ValueError("evidence claim requires Operator registration")
        object.__setattr__(self, "taxonomy_ids", taxonomies)
        object.__setattr__(self, "source_artifact_hashes", hashes)
        object.__setattr__(self, "reason_codes", reasons)
        object.__setattr__(self, "observed_at_utc", observed)
        object.__setattr__(self, "available_at_utc", available)
        object.__setattr__(
            self,
            "claim_hash",
            _digest(
                {
                    "available_at_utc": available,
                    "claim_id": self.claim_id,
                    "dependence_group_id": self.dependence_group_id,
                    "observed_at_utc": observed,
                    "operator_registered": self.operator_registered,
                    "reason_codes": reasons,
                    "requested_confidence_bps": self.requested_confidence_bps,
                    "scope": self.scope,
                    "source_artifact_hashes": hashes,
                    "stance": self.stance,
                    "taxonomy_ids": taxonomies,
                    "usability": self.usability,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredDependenceGroup:
    group_id: str
    dependence_type: str
    claim_ids: tuple[str, ...]
    group_cap_bps: int
    policy_id: str
    registered_evidence_hashes: tuple[str, ...]
    operator_registered: bool = True
    group_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("group_id", "policy_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        dependence_type = str(self.dependence_type).strip().upper()
        if dependence_type not in DEPENDENCE_TYPES:
            raise ValueError("dependence_type is not registered")
        claims = _identifiers(tuple(self.claim_ids), "claim_id")
        if not claims:
            raise ValueError("dependence group requires claims")
        if dependence_type == "INDEPENDENT" and len(claims) != 1:
            raise ValueError("independent dependence group requires one claim")
        if dependence_type != "INDEPENDENT" and len(claims) < 2:
            raise ValueError("dependent evidence group requires multiple claims")
        hashes = _hashes(
            tuple(self.registered_evidence_hashes), "registered_evidence_hash"
        )
        object.__setattr__(
            self,
            "group_cap_bps",
            _basis_points(self.group_cap_bps, "group_cap_bps", positive=True),
        )
        if self.operator_registered is not True:
            raise ValueError("dependence group requires Operator registration")
        object.__setattr__(self, "dependence_type", dependence_type)
        object.__setattr__(self, "claim_ids", claims)
        object.__setattr__(self, "registered_evidence_hashes", hashes)
        object.__setattr__(
            self,
            "group_hash",
            _digest(
                {
                    "claim_ids": claims,
                    "dependence_type": dependence_type,
                    "group_cap_bps": self.group_cap_bps,
                    "group_id": self.group_id,
                    "operator_registered": self.operator_registered,
                    "policy_id": self.policy_id,
                    "registered_evidence_hashes": hashes,
                }
            ),
        )


@dataclass(frozen=True)
class ConfidenceBudgetPolicy:
    policy_id: str
    global_cap_bps: int
    minimum_usable_bps: int
    conflict_abstention_ratio_bps: int
    operator_registered: bool = True
    automatic_scoring: bool = False
    automatic_weight_change: bool = False
    policy_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", identifier(self.policy_id, "policy_id"))
        for name in (
            "global_cap_bps",
            "minimum_usable_bps",
            "conflict_abstention_ratio_bps",
        ):
            object.__setattr__(self, name, _basis_points(getattr(self, name), name))
        if self.global_cap_bps == 0:
            raise ValueError("global confidence budget must be positive")
        if self.minimum_usable_bps > self.global_cap_bps:
            raise ValueError("minimum usable confidence exceeds global budget")
        if self.operator_registered is not True:
            raise ValueError("confidence budget policy requires Operator registration")
        if self.automatic_scoring or self.automatic_weight_change:
            raise ValueError("confidence budget policy cannot change scoring or weights")
        object.__setattr__(
            self,
            "policy_hash",
            _digest(
                {
                    "automatic_scoring": self.automatic_scoring,
                    "automatic_weight_change": self.automatic_weight_change,
                    "conflict_abstention_ratio_bps": self.conflict_abstention_ratio_bps,
                    "global_cap_bps": self.global_cap_bps,
                    "minimum_usable_bps": self.minimum_usable_bps,
                    "operator_registered": self.operator_registered,
                    "policy_id": self.policy_id,
                }
            ),
        )


@dataclass(frozen=True)
class ClaimBudgetAllocation:
    claim_id: str
    group_id: str
    requested_confidence_bps: int
    allocated_confidence_bps: int
    signed_contribution_bps: int
    suppression_reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        identifier(self.claim_id, "claim_id")
        identifier(self.group_id, "group_id")
        _basis_points(self.requested_confidence_bps, "requested_confidence_bps")
        _basis_points(self.allocated_confidence_bps, "allocated_confidence_bps")
        if self.allocated_confidence_bps > self.requested_confidence_bps:
            raise ValueError("allocated confidence exceeds request")
        if abs(self.signed_contribution_bps) > self.allocated_confidence_bps:
            raise ValueError("signed contribution exceeds allocation")
        _identifiers(tuple(self.suppression_reasons), "suppression_reason")


@dataclass(frozen=True)
class DependenceGroupFinding:
    group_id: str
    dependence_type: str
    claim_ids: tuple[str, ...]
    requested_usable_bps: int
    group_cap_bps: int
    allocated_confidence_bps: int
    repeated_confirmation_prevented: bool

    def __post_init__(self) -> None:
        identifier(self.group_id, "group_id")
        if self.dependence_type not in DEPENDENCE_TYPES:
            raise ValueError("finding dependence type is not registered")
        _identifiers(tuple(self.claim_ids), "claim_id")
        for name in ("requested_usable_bps", "group_cap_bps", "allocated_confidence_bps"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be nonnegative integer basis points")
        if self.group_cap_bps > 10_000:
            raise ValueError("group cap exceeds registered basis-point bounds")
        if self.allocated_confidence_bps > self.group_cap_bps:
            raise ValueError("group allocation exceeds group cap")
        if not isinstance(self.repeated_confirmation_prevented, bool):
            raise ValueError("repeated confirmation finding must be boolean")


@dataclass(frozen=True)
class ConfidenceBudgetEvaluation:
    state: str
    policy_id: str
    allocations: tuple[ClaimBudgetAllocation, ...]
    group_findings: tuple[DependenceGroupFinding, ...]
    gross_requested_bps: int
    gross_allocated_bps: int
    supporting_bps: int
    opposing_bps: int
    neutral_bps: int
    net_confidence_bps: int
    abstention_reasons: tuple[str, ...]
    operator_review_required: bool
    scoring_authority_claimed: bool
    evaluation_hash: str

    def __post_init__(self) -> None:
        if self.state not in BUDGET_STATES:
            raise ValueError("confidence budget state is not registered")
        if self.operator_review_required is not True or self.scoring_authority_claimed:
            raise ValueError("confidence budget evaluation authority violation")
        if self.gross_allocated_bps != (
            self.supporting_bps + self.opposing_bps + self.neutral_bps
        ):
            raise ValueError("confidence budget allocation totals do not reconcile")
        if self.net_confidence_bps != self.supporting_bps - self.opposing_bps:
            raise ValueError("confidence budget net total does not reconcile")
        if self.gross_allocated_bps > self.gross_requested_bps:
            raise ValueError("allocated confidence exceeds gross request")
