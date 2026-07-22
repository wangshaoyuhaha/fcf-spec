from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0085_btc_registered_local_export_validation_runner_app_1.contracts import (
    BTCLocalExportValidationResult,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


REVIEW_ITEM_IDS = (
    "source-lineage",
    "profile-lineage",
    "observation-coverage",
    "sequence-bounds",
    "clock-bounds",
    "local-only-authority",
)


@dataclass(frozen=True)
class BTCLocalExportOperatorReviewItem:
    item_id: str
    evidence_digest: str
    review_state: str = "OPERATOR_REVIEW_REQUIRED"
    operator_review_required: bool = True
    approved: bool = False
    rejected: bool = False
    item_hash: str = field(init=False)

    def __post_init__(self) -> None:
        item_id = identifier(self.item_id, "item_id")
        if item_id not in REVIEW_ITEM_IDS:
            raise ValueError("review item is not registered")
        digest = str(self.evidence_digest)
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("evidence_digest must be lowercase SHA-256")
        if (
            self.review_state != "OPERATOR_REVIEW_REQUIRED"
            or self.operator_review_required is not True
            or self.approved is not False
            or self.rejected is not False
        ):
            raise ValueError("review item cannot assign a disposition")
        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(
            self,
            "item_hash",
            canonical_sha256(
                {
                    "evidence_digest": digest,
                    "item_id": item_id,
                    "review_state": self.review_state,
                }
            ),
        )

    def to_record(self) -> dict[str, object]:
        return {
            "approved": False,
            "evidence_digest": self.evidence_digest,
            "item_hash": self.item_hash,
            "item_id": self.item_id,
            "operator_review_required": True,
            "rejected": False,
            "review_state": self.review_state,
        }


@dataclass(frozen=True)
class BTCLocalExportOperatorReviewPacket:
    packet_id: str
    validation_result: BTCLocalExportValidationResult
    packet_created_at_utc: str
    review_items: tuple[BTCLocalExportOperatorReviewItem, ...]
    operator_review_state: str = "OPERATOR_REVIEW_REQUIRED"
    operator_review_required: bool = True
    packet_only: bool = True
    disposition_assigned: bool = False
    evidence_approved: bool = False
    evidence_rejected: bool = False
    evidence_promotion_allowed: bool = False
    replay_activation_allowed: bool = False
    provider_selected: bool = False
    venue_selected: bool = False
    network_used: bool = False
    sdk_used: bool = False
    recommendation_allowed: bool = False
    account_state_allowed: bool = False
    margin_calculation_allowed: bool = False
    leverage_calculation_allowed: bool = False
    liquidation_action_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    order_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    schema_version: str = "btc-local-export-operator-review-packet-v1"
    validation_result_hash: str = field(init=False)
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        packet_id = identifier(self.packet_id, "packet_id")
        result = self.validation_result
        if type(result) is not BTCLocalExportValidationResult:
            raise ValueError("review packet requires one exact typed FCP-0085 result")
        created = utc(self.packet_created_at_utc, "packet_created_at_utc")
        if instant(created) < instant(result.as_of_utc):
            raise ValueError("review packet cannot precede validation")
        items = tuple(self.review_items)
        if not all(type(item) is BTCLocalExportOperatorReviewItem for item in items):
            raise ValueError("review_items must contain exact typed items")
        if tuple(item.item_id for item in items) != REVIEW_ITEM_IDS:
            raise ValueError("review_items must use the closed order")
        if len({item.item_hash for item in items}) != len(items):
            raise ValueError("review_items must be unique")
        forbidden = (
            self.disposition_assigned,
            self.evidence_approved,
            self.evidence_rejected,
            self.evidence_promotion_allowed,
            self.replay_activation_allowed,
            self.provider_selected,
            self.venue_selected,
            self.network_used,
            self.sdk_used,
            self.recommendation_allowed,
            self.account_state_allowed,
            self.margin_calculation_allowed,
            self.leverage_calculation_allowed,
            self.liquidation_action_allowed,
            self.position_calculation_allowed,
            self.pnl_calculation_allowed,
            self.order_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_state != "OPERATOR_REVIEW_REQUIRED"
            or self.operator_review_required is not True
            or self.packet_only is not True
            or any(forbidden)
        ):
            raise ValueError("review packet cannot decide, activate, promote, or act")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("review packet authority identities are immutable")
        if self.schema_version != "btc-local-export-operator-review-packet-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "packet_id", packet_id)
        object.__setattr__(self, "packet_created_at_utc", created)
        object.__setattr__(self, "review_items", items)
        object.__setattr__(self, "validation_result_hash", result.result_hash)
        object.__setattr__(
            self,
            "packet_hash",
            canonical_sha256(
                {
                    "operator_review_state": self.operator_review_state,
                    "packet_created_at_utc": created,
                    "packet_id": packet_id,
                    "review_item_hashes": [item.item_hash for item in items],
                    "schema_version": self.schema_version,
                    "validation_result_hash": result.result_hash,
                }
            ),
        )

    def to_record(self) -> dict[str, object]:
        result = self.validation_result
        return {
            "authority": {
                "ai_role": self.ai_role,
                "calculation_authority": self.calculation_authority,
                "disposition_assigned": False,
                "evidence_approved": False,
                "evidence_authority": self.evidence_authority,
                "evidence_promotion_allowed": False,
                "evidence_rejected": False,
                "execution_allowed": False,
                "gap_closed": False,
                "network_used": False,
                "operator_review_required": True,
                "order_allowed": False,
                "provider_selected": False,
                "replay_activation_allowed": False,
                "sdk_used": False,
                "venue_selected": False,
            },
            "packet_created_at_utc": self.packet_created_at_utc,
            "packet_hash": self.packet_hash,
            "packet_id": self.packet_id,
            "review_items": [item.to_record() for item in self.review_items],
            "review_state": self.operator_review_state,
            "schema_version": self.schema_version,
            "validation": {
                "canonical_artifact_sha256": result.canonical_artifact_sha256,
                "event_range": [result.event_start_utc, result.event_end_utc],
                "ingested_range": [result.ingested_start_utc, result.ingested_end_utc],
                "manifest_hash": result.manifest_hash,
                "observation_count": result.observation_count,
                "observation_kind_counts": dict(result.observation_kind_counts),
                "profile_hash": result.profile_hash,
                "quality_state": result.quality_state,
                "received_range": [result.received_start_utc, result.received_end_utc],
                "result_hash": result.result_hash,
                "sequence_range": [result.sequence_min, result.sequence_max],
                "source_artifact_sha256": result.source_artifact_sha256,
            },
        }
