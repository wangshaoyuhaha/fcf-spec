from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


AUTHORITY_DOMAIN_ORDER = (
    "PROVIDER_IDENTITY",
    "RIGHTS_AND_RETENTION",
    "REVISION_LINEAGE",
    "CORPORATE_ACTION_LINEAGE",
    "ADJUSTMENT_FACTOR_AUTHORITY",
    "TRADING_STATUS_AUTHORITY",
    "EXPECTED_CALENDAR_AUTHORITY",
    "POINT_IN_TIME_AVAILABILITY",
)


def _instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@dataclass(frozen=True)
class CandidateDailyAuthorityReference:
    artifact_id: str
    artifact_hash: str
    domain: str
    observed_at_utc: str
    registered_artifact: bool = True
    reference_hash: str = field(init=False)

    def __post_init__(self) -> None:
        artifact_id = identifier(self.artifact_id, "artifact_id")
        artifact_hash = digest(self.artifact_hash, "artifact_hash")
        observed_at_utc = utc(self.observed_at_utc, "observed_at_utc")
        if self.domain not in AUTHORITY_DOMAIN_ORDER:
            raise ValueError("authority domain is not registered")
        if self.registered_artifact is not True:
            raise ValueError("authority reference requires a registered artifact")
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "observed_at_utc", observed_at_utc)
        object.__setattr__(
            self,
            "reference_hash",
            canonical_sha256(
                {
                    "artifact_id": artifact_id,
                    "artifact_hash": artifact_hash,
                    "domain": self.domain,
                    "observed_at_utc": observed_at_utc,
                    "registered_artifact": True,
                }
            ),
        )


@dataclass(frozen=True)
class CandidateDailyPromotionReadinessGate:
    gate_id: str
    evaluated_at_utc: str
    quality_evidence_hash: str
    authority_references: tuple[CandidateDailyAuthorityReference, ...]
    blocker_codes: tuple[str, ...]
    status: str
    ready_for_operator_review: bool
    candidate_promotion_allowed: bool = False
    factor_calculation_allowed: bool = False
    training_label_allowed: bool = False
    provider_selection_allowed: bool = False
    operator_review_mandatory: bool = True
    schema_version: str = "a-share-candidate-daily-promotion-readiness-v1"
    gate_hash: str = field(init=False)

    def __post_init__(self) -> None:
        gate_id = identifier(self.gate_id, "gate_id")
        evaluated_at_utc = utc(self.evaluated_at_utc, "evaluated_at_utc")
        quality_evidence_hash = digest(self.quality_evidence_hash, "quality_evidence_hash")
        references = tuple(self.authority_references)
        if any(type(item) is not CandidateDailyAuthorityReference for item in references):
            raise ValueError("authority references must be exact typed references")
        domains = tuple(item.domain for item in references)
        expected_subset = tuple(domain for domain in AUTHORITY_DOMAIN_ORDER if domain in domains)
        if domains != expected_subset or len(domains) != len(set(domains)):
            raise ValueError("authority references must be unique and in closed domain order")
        if len({item.artifact_id for item in references}) != len(references):
            raise ValueError("authority artifact identities must be unique")
        if len({item.artifact_hash for item in references}) != len(references):
            raise ValueError("authority artifact hashes must be unique")
        if any(_instant(item.observed_at_utc) > _instant(evaluated_at_utc) for item in references):
            raise ValueError("authority evidence cannot postdate gate evaluation")
        blockers = tuple(self.blocker_codes)
        if len(blockers) != len(set(blockers)):
            raise ValueError("blocker codes must be unique")
        expected_status = (
            "BLOCKED_NOT_READY_FOR_OPERATOR_REVIEW"
            if blockers
            else "READY_FOR_OPERATOR_REVIEW_NOT_PROMOTED"
        )
        expected_ready = not blockers
        if self.status != expected_status or self.ready_for_operator_review is not expected_ready:
            raise ValueError("gate status and review readiness must match exact blockers")
        forbidden = (
            self.candidate_promotion_allowed,
            self.factor_calculation_allowed,
            self.training_label_allowed,
            self.provider_selection_allowed,
        )
        if any(forbidden) or self.operator_review_mandatory is not True:
            raise ValueError("gate cannot promote, calculate, label, select, or waive review")
        if self.schema_version != "a-share-candidate-daily-promotion-readiness-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "gate_id", gate_id)
        object.__setattr__(self, "evaluated_at_utc", evaluated_at_utc)
        object.__setattr__(self, "quality_evidence_hash", quality_evidence_hash)
        object.__setattr__(self, "authority_references", references)
        object.__setattr__(self, "blocker_codes", blockers)
        object.__setattr__(
            self,
            "gate_hash",
            canonical_sha256(
                {
                    "gate_id": gate_id,
                    "evaluated_at_utc": evaluated_at_utc,
                    "quality_evidence_hash": quality_evidence_hash,
                    "authority_reference_hashes": [
                        item.reference_hash for item in references
                    ],
                    "blocker_codes": list(blockers),
                    "status": self.status,
                    "ready_for_operator_review": expected_ready,
                    "operator_review_mandatory": True,
                    "schema_version": self.schema_version,
                }
            ),
        )
