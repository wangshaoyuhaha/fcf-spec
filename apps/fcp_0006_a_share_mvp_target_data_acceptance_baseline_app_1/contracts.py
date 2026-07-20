from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
TARGET_FAMILIES = (
    "FIVE_SESSION_EXCESS_RETURN",
    "LATE_SESSION_TO_NEXT_OPEN_EXCESS_RETURN",
    "NEXT_SESSION_EXCESS_RETURN",
)
DATA_DOMAINS = (
    "CORPORATE_ACTION",
    "INSTRUMENT_MASTER",
    "MARKET_CALENDAR",
    "OHLCV",
    "PRICE_LIMIT_AND_HALT",
    "QUOTE_L1",
    "SECTOR_CLASSIFICATION",
    "TRADE_PRINT",
    "UNIVERSE_SNAPSHOT",
)
REQUIREMENT_LEVELS = ("CONDITIONAL", "REQUIRED")
OBLIGATION_CATEGORIES = (
    "COST_MODEL",
    "FAILURE_THRESHOLD",
    "LEAKAGE_CONTROL",
    "REPLAY_PROTOCOL",
    "STOP_RULE",
    "SUCCESS_THRESHOLD",
)
EVIDENCE_STATES = ("EVIDENCE_REQUIRED", "REGISTERED")
BASELINE_STATES = (
    "BASELINE_INCOMPLETE",
    "READY_FOR_EVIDENCE_COLLECTION",
    "READY_FOR_OPERATOR_EVIDENCE_REGISTRATION",
)


def safe_id(value: str, name: str) -> str:
    normalized = str(value).strip()
    if not SAFE_ID.fullmatch(normalized):
        raise ValueError(f"{name} is not a safe identifier")
    return normalized


def digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class AShareTargetContract:
    target_id: str
    target_family: str
    horizon_id: str
    benchmark_id: str
    universe_policy_id: str
    label_maturity_id: str
    market_id: str = "A-SHARE"
    target_hash: str = field(init=False)

    def __post_init__(self) -> None:
        values = {
            name: safe_id(getattr(self, name), name)
            for name in (
                "target_id",
                "horizon_id",
                "benchmark_id",
                "universe_policy_id",
                "label_maturity_id",
                "market_id",
            )
        }
        if self.target_family not in TARGET_FAMILIES:
            raise ValueError("target family is not registered")
        if values["market_id"] != "A-SHARE":
            raise ValueError("FCP-0006 target must remain A-share specific")
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "target_hash",
            digest({**values, "target_family": self.target_family}),
        )


@dataclass(frozen=True)
class PointInTimeDataRequirement:
    field_id: str
    domain: str
    source_semantics_id: str
    requirement_level: str = "REQUIRED"
    point_in_time_required: bool = True
    availability_time_required: bool = True
    market_session_version_required: bool = True
    provider_id: None = None
    entitlement_approved: bool = False
    requirement_hash: str = field(init=False)

    def __post_init__(self) -> None:
        values = {
            name: safe_id(getattr(self, name), name)
            for name in ("field_id", "source_semantics_id")
        }
        if self.domain not in DATA_DOMAINS:
            raise ValueError("data domain is not registered")
        if self.requirement_level not in REQUIREMENT_LEVELS:
            raise ValueError("data requirement level is not registered")
        if not self.point_in_time_required or not self.availability_time_required:
            raise ValueError("data requirements must preserve point-in-time availability")
        if self.provider_id is not None or self.entitlement_approved:
            raise ValueError("FCP-0006 cannot select a provider or approve entitlement")
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "requirement_hash",
            digest(
                {
                    **values,
                    "availability_time_required": self.availability_time_required,
                    "domain": self.domain,
                    "entitlement_approved": self.entitlement_approved,
                    "market_session_version_required": self.market_session_version_required,
                    "point_in_time_required": self.point_in_time_required,
                    "provider_id": self.provider_id,
                    "requirement_level": self.requirement_level,
                }
            ),
        )


@dataclass(frozen=True)
class AcceptanceEvidenceObligation:
    obligation_id: str
    category: str
    metric_id: str
    evidence_state: str = "EVIDENCE_REQUIRED"
    evidence_artifact_id: str | None = None
    evidence_digest: str | None = None
    empirical_threshold: None = None
    obligation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        obligation_id = safe_id(self.obligation_id, "obligation_id")
        metric_id = safe_id(self.metric_id, "metric_id")
        if self.category not in OBLIGATION_CATEGORIES:
            raise ValueError("acceptance obligation category is not registered")
        if self.evidence_state not in EVIDENCE_STATES:
            raise ValueError("acceptance evidence state is not registered")
        if self.empirical_threshold is not None:
            raise ValueError("empirical thresholds require separate registered evidence")
        if self.evidence_state == "REGISTERED":
            if self.evidence_artifact_id is None or self.evidence_digest is None:
                raise ValueError("registered obligation requires artifact and digest")
            artifact_id = safe_id(self.evidence_artifact_id, "evidence_artifact_id")
            if not HEX_64.fullmatch(self.evidence_digest):
                raise ValueError("evidence_digest must be lowercase SHA-256")
        else:
            if self.evidence_artifact_id is not None or self.evidence_digest is not None:
                raise ValueError("unregistered obligation cannot claim evidence")
            artifact_id = None
        object.__setattr__(self, "obligation_id", obligation_id)
        object.__setattr__(self, "metric_id", metric_id)
        object.__setattr__(self, "evidence_artifact_id", artifact_id)
        object.__setattr__(
            self,
            "obligation_hash",
            digest(
                {
                    "category": self.category,
                    "empirical_threshold": self.empirical_threshold,
                    "evidence_artifact_id": artifact_id,
                    "evidence_digest": self.evidence_digest,
                    "evidence_state": self.evidence_state,
                    "metric_id": metric_id,
                    "obligation_id": obligation_id,
                }
            ),
        )


@dataclass(frozen=True)
class AShareMvpBaselineRegistry:
    targets: tuple[AShareTargetContract, ...]
    data_requirements: tuple[PointInTimeDataRequirement, ...]
    obligations: tuple[AcceptanceEvidenceObligation, ...]
    proposal_id: str = "FCF-FCP-0006"
    proposal_status: str = "ACCEPTED_ARCHITECTURE"
    operator_decision: str = "ACCEPTED_ARCHITECTURE"
    phase_id: str = "NONE"
    research_priority_market_id: str = "A-SHARE"
    selected_market_id: None = None
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        targets = tuple(sorted(self.targets, key=lambda item: item.target_id))
        requirements = tuple(
            sorted(self.data_requirements, key=lambda item: item.field_id)
        )
        obligations = tuple(
            sorted(self.obligations, key=lambda item: item.obligation_id)
        )
        if not targets or not requirements or not obligations:
            raise ValueError("A-share MVP baseline registry cannot be empty")
        identities = (
            ("target ids", tuple(item.target_id for item in targets)),
            ("target families", tuple(item.target_family for item in targets)),
            ("data field ids", tuple(item.field_id for item in requirements)),
            ("obligation ids", tuple(item.obligation_id for item in obligations)),
            ("obligation categories", tuple(item.category for item in obligations)),
        )
        for name, values in identities:
            if len(values) != len(set(values)):
                raise ValueError(f"{name} must be unique")
        if self.proposal_id != "FCF-FCP-0006":
            raise ValueError("baseline proposal id is not FCF-FCP-0006")
        if (
            self.proposal_status != "ACCEPTED_ARCHITECTURE"
            or self.operator_decision != "ACCEPTED_ARCHITECTURE"
        ):
            raise ValueError("FCP-0006 must remain accepted architecture only")
        if self.phase_id != "NONE":
            raise ValueError("A-share MVP baseline cannot authorize a product phase")
        if self.research_priority_market_id != "A-SHARE":
            raise ValueError("research priority must remain A-share")
        if self.selected_market_id is not None:
            raise ValueError("research priority cannot select a product market")
        object.__setattr__(self, "targets", targets)
        object.__setattr__(self, "data_requirements", requirements)
        object.__setattr__(self, "obligations", obligations)
        object.__setattr__(
            self,
            "registry_hash",
            digest(
                {
                    "obligation_hashes": tuple(
                        item.obligation_hash for item in obligations
                    ),
                    "operator_decision": self.operator_decision,
                    "phase_id": self.phase_id,
                    "proposal_id": self.proposal_id,
                    "proposal_status": self.proposal_status,
                    "requirement_hashes": tuple(
                        item.requirement_hash for item in requirements
                    ),
                    "research_priority_market_id": self.research_priority_market_id,
                    "selected_market_id": self.selected_market_id,
                    "target_hashes": tuple(item.target_hash for item in targets),
                }
            ),
        )


@dataclass(frozen=True)
class AShareMvpBaselineResult:
    state: str
    registry_hash: str
    missing_target_families: tuple[str, ...]
    missing_data_domains: tuple[str, ...]
    missing_obligation_categories: tuple[str, ...]
    evidence_required_obligation_ids: tuple[str, ...]
    registered_evidence_obligation_ids: tuple[str, ...]
    research_priority_market_id: str
    selected_market_id: None
    fcp_0005_readiness_claimed: bool
    product_phase_authorized: bool
    production_gap_closure_claimed: bool
    result_hash: str

    def __post_init__(self) -> None:
        if self.state not in BASELINE_STATES:
            raise ValueError("A-share MVP baseline state is not registered")
        if self.research_priority_market_id != "A-SHARE":
            raise ValueError("baseline result must remain A-share research priority")
        if self.selected_market_id is not None:
            raise ValueError("baseline result cannot select a market")
        if (
            self.fcp_0005_readiness_claimed
            or self.product_phase_authorized
            or self.production_gap_closure_claimed
        ):
            raise ValueError("baseline result cannot claim product authority")
