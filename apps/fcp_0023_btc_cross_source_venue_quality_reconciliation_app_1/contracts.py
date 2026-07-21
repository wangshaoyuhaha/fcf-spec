from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import re
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    BTCBookDelta,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCObservation,
    BTCReferencePriceObservation,
    BTCRegisteredArtifact,
    BTCTradeObservation,
    canonical_sha256,
    decimal_text,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


OBSERVATION_TYPES = (
    BTCTradeObservation,
    BTCBookSnapshot,
    BTCBookDelta,
    BTCReferencePriceObservation,
    BTCFundingObservation,
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be lowercase SHA-256")
    result = value
    if _SHA256.fullmatch(result) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return result


def comparison_key(observation: BTCObservation) -> tuple[str, str, str, str]:
    header = observation.header
    return (
        header.instrument_id,
        header.instrument_kind,
        header.observation_kind,
        header.event_at_utc,
    )


def comparison_key_text(observation: BTCObservation) -> str:
    return ":".join(comparison_key(observation))


def _bounded_decimal(value: object, name: str, upper: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must use an exact decimal value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite() or result < 0 or result > Decimal(upper):
        raise ValueError(f"{name} is outside its bounded domain")
    return result


@dataclass(frozen=True)
class RegisteredCanonicalBTCObservationSet:
    dataset_id: str
    source_id: str
    artifact: BTCRegisteredArtifact
    observations: tuple[BTCObservation, ...]
    as_of_utc: str
    venue_semantics_id: str
    rights_state: str = "DECLARED_LOCAL_RESEARCH"
    retention_state: str = "LOCAL_DERIVED_ONLY"
    operator_registered: bool = True
    local_only: bool = True
    provider_selected: bool = False
    schema_version: str = "btc-observation-set-v1"
    dataset_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "dataset_id", identifier(self.dataset_id, "dataset_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(
            self,
            "venue_semantics_id",
            identifier(self.venue_semantics_id, "venue_semantics_id"),
        )
        if not isinstance(self.artifact, BTCRegisteredArtifact):
            raise ValueError("dataset requires a registered BTC artifact")
        observations = tuple(self.observations)
        if not observations or not all(isinstance(item, OBSERVATION_TYPES) for item in observations):
            raise ValueError("dataset requires typed BTC observations")
        keys = tuple(comparison_key(item) for item in observations)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("dataset observations must have unique deterministic comparison keys")
        if any(item.header.artifact_id != self.artifact.artifact_id for item in observations):
            raise ValueError("dataset observation artifact lineage mismatch")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if any(instant(item.header.ingested_at_utc) > instant(as_of) for item in observations):
            raise ValueError("dataset cannot contain knowledge after as_of_utc")
        if self.rights_state not in {"UNRESOLVED", "DECLARED_LOCAL_RESEARCH"}:
            raise ValueError("rights_state is not registered")
        if self.retention_state not in {"UNRESOLVED", "LOCAL_DERIVED_ONLY"}:
            raise ValueError("retention_state is not registered")
        if self.schema_version != "btc-observation-set-v1":
            raise ValueError("schema_version is not registered")
        if self.operator_registered is not True or self.local_only is not True or self.provider_selected is not False:
            raise ValueError("dataset must remain registered-local and provider-unselected")
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "dataset_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact.artifact_id,
                    "artifact_sha256": self.artifact.content_sha256,
                    "as_of_utc": as_of,
                    "dataset_id": self.dataset_id,
                    "observation_hashes": [item.observation_hash for item in observations],
                    "retention_state": self.retention_state,
                    "rights_state": self.rights_state,
                    "schema_version": self.schema_version,
                    "source_id": self.source_id,
                    "venue_semantics_id": self.venue_semantics_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCCrossSourceReconciliationPolicy:
    policy_id: str
    price_tolerance: Decimal = Decimal("0")
    quantity_tolerance: Decimal = Decimal("0")
    funding_rate_tolerance: Decimal = Decimal("0")
    clock_tolerance_seconds: int = 0
    require_same_venue: bool = True
    operator_registered: bool = True
    source_selection_allowed: bool = False
    policy_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_id", identifier(self.policy_id, "policy_id"))
        price = _bounded_decimal(self.price_tolerance, "price_tolerance", "1000000")
        quantity = _bounded_decimal(self.quantity_tolerance, "quantity_tolerance", "1000000")
        funding = _bounded_decimal(self.funding_rate_tolerance, "funding_rate_tolerance", "1")
        if (
            isinstance(self.clock_tolerance_seconds, bool)
            or not isinstance(self.clock_tolerance_seconds, int)
            or not 0 <= self.clock_tolerance_seconds <= 86400
        ):
            raise ValueError("clock_tolerance_seconds is outside its bounded domain")
        if not isinstance(self.require_same_venue, bool):
            raise ValueError("require_same_venue must be boolean")
        if self.operator_registered is not True or self.source_selection_allowed is not False:
            raise ValueError("policy requires Operator registration and cannot select a source")
        object.__setattr__(self, "price_tolerance", price)
        object.__setattr__(self, "quantity_tolerance", quantity)
        object.__setattr__(self, "funding_rate_tolerance", funding)
        object.__setattr__(
            self,
            "policy_hash",
            canonical_sha256(
                {
                    "clock_tolerance_seconds": self.clock_tolerance_seconds,
                    "funding_rate_tolerance": decimal_text(funding),
                    "policy_id": self.policy_id,
                    "price_tolerance": decimal_text(price),
                    "quantity_tolerance": decimal_text(quantity),
                    "require_same_venue": self.require_same_venue,
                }
            ),
        )


@dataclass(frozen=True)
class BTCCrossSourceFinding:
    code: str
    severity: str
    dataset_ids: tuple[str, ...]
    comparison_key: str | None = None
    field_name: str | None = None
    detail: Mapping[str, str] = field(default_factory=dict)
    finding_hash: str = field(init=False)

    def __post_init__(self) -> None:
        code = identifier(self.code, "finding code")
        if self.severity not in {"BLOCK", "WARN"}:
            raise ValueError("finding severity is not registered")
        datasets = tuple(sorted(set(identifier(item, "dataset_id") for item in self.dataset_ids)))
        if not datasets:
            raise ValueError("finding requires dataset lineage")
        if self.comparison_key is not None and not str(self.comparison_key).strip():
            raise ValueError("comparison_key cannot be blank")
        if self.field_name is not None:
            object.__setattr__(self, "field_name", identifier(self.field_name, "field_name"))
        detail = {identifier(key, "detail key"): str(value) for key, value in self.detail.items()}
        object.__setattr__(self, "code", code)
        object.__setattr__(self, "dataset_ids", datasets)
        object.__setattr__(self, "detail", MappingProxyType(detail))
        object.__setattr__(
            self,
            "finding_hash",
            canonical_sha256(
                {
                    "code": code,
                    "comparison_key": self.comparison_key,
                    "dataset_ids": datasets,
                    "detail": detail,
                    "field_name": self.field_name,
                    "severity": self.severity,
                }
            ),
        )


@dataclass(frozen=True)
class BTCCrossSourceReconciliationResult:
    dataset_hashes: tuple[str, ...]
    policy_hash: str
    union_key_count: int
    overlap_key_count: int
    findings: tuple[BTCCrossSourceFinding, ...]
    quality_state: str
    operator_review_required: bool = True
    source_selected: bool = False
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        hashes = tuple(_digest(item, "dataset_hash") for item in self.dataset_hashes)
        policy_hash = _digest(self.policy_hash, "policy_hash")
        findings = tuple(self.findings)
        if len(hashes) < 2 or len(hashes) != len(set(hashes)):
            raise ValueError("result requires distinct dataset hashes")
        if not all(isinstance(item, BTCCrossSourceFinding) for item in findings):
            raise ValueError("result findings must be typed")
        if findings != tuple(sorted(findings, key=lambda item: item.finding_hash)):
            raise ValueError("result findings must be deterministically ordered")
        blocked = any(item.severity == "BLOCK" for item in findings)
        if self.quality_state not in {"CONSISTENT", "QUARANTINE_REVIEW_REQUIRED"}:
            raise ValueError("quality_state is not registered")
        if (self.quality_state == "QUARANTINE_REVIEW_REQUIRED") != blocked:
            raise ValueError("quality_state and findings disagree")
        if self.operator_review_required is not True or self.source_selected is not False:
            raise ValueError("reconciliation cannot bypass review or select a source")
        counts = (self.union_key_count, self.overlap_key_count)
        if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in counts):
            raise ValueError("reconciliation key counts must be nonnegative integers")
        if self.overlap_key_count > self.union_key_count:
            raise ValueError("reconciliation key counts are inconsistent")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("reconciliation authority identities are immutable")
        object.__setattr__(self, "findings", findings)
        object.__setattr__(self, "dataset_hashes", hashes)
        object.__setattr__(self, "policy_hash", policy_hash)
        object.__setattr__(
            self,
            "result_hash",
            canonical_sha256(
                {
                    "dataset_hashes": hashes,
                    "finding_hashes": [item.finding_hash for item in findings],
                    "overlap_key_count": self.overlap_key_count,
                    "policy_hash": policy_hash,
                    "quality_state": self.quality_state,
                    "union_key_count": self.union_key_count,
                }
            ),
        )
