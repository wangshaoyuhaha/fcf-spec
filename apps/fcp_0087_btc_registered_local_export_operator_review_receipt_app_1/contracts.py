from __future__ import annotations

from dataclasses import dataclass, field
import json

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0085_btc_registered_local_export_validation_runner_app_1.runner import (
    build_reference_result,
)
from apps.fcp_0086_btc_registered_local_export_operator_review_packet_app_1 import (
    BTCLocalExportOperatorReviewPacket,
    build_operator_review_packet,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


REVIEW_DISPOSITIONS = (
    "REVIEWED_NO_PROMOTION",
    "DEFERRED_PENDING_EVIDENCE",
    "ESCALATED_FOR_RESEARCH",
)


@dataclass(frozen=True)
class BTCLocalExportOperatorReviewReceipt:
    receipt_id: str
    review_packet: BTCLocalExportOperatorReviewPacket
    reviewer_reference: str
    reviewed_at_utc: str
    disposition: str
    operator_review_completed: bool = True
    receipt_only: bool = True
    evidence_approved: bool = False
    evidence_rejected: bool = False
    result_resolved: bool = False
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
    schema_version: str = "btc-local-export-operator-review-receipt-v1"
    packet_hash: str = field(init=False)
    validation_result_hash: str = field(init=False)
    review_item_hashes: tuple[str, ...] = field(init=False)
    receipt_hash: str = field(init=False)

    def __post_init__(self) -> None:
        receipt_id = identifier(self.receipt_id, "receipt_id")
        packet = self.review_packet
        if type(packet) is not BTCLocalExportOperatorReviewPacket:
            raise ValueError("review receipt requires one exact typed FCP-0086 packet")
        if (
            packet.operator_review_required is not True
            or packet.packet_only is not True
            or packet.disposition_assigned is not False
            or packet.evidence_approved is not False
            or packet.evidence_rejected is not False
        ):
            raise ValueError("review packet authority boundary is invalid")
        reviewer = identifier(self.reviewer_reference, "reviewer_reference")
        reviewed = utc(self.reviewed_at_utc, "reviewed_at_utc")
        if instant(reviewed) < instant(packet.packet_created_at_utc):
            raise ValueError("review receipt cannot precede packet evidence")
        if self.disposition not in REVIEW_DISPOSITIONS:
            raise ValueError("review disposition is not registered")
        forbidden = (
            self.evidence_approved,
            self.evidence_rejected,
            self.result_resolved,
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
            self.operator_review_completed is not True
            or self.receipt_only is not True
            or any(forbidden)
        ):
            raise ValueError("review receipt cannot approve, resolve, promote, activate, or act")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("review receipt authority identities are immutable")
        if self.schema_version != "btc-local-export-operator-review-receipt-v1":
            raise ValueError("schema_version is not registered")
        item_hashes = tuple(item.item_hash for item in packet.review_items)
        if len(item_hashes) != len(set(item_hashes)):
            raise ValueError("review item lineage must be unique")
        object.__setattr__(self, "receipt_id", receipt_id)
        object.__setattr__(self, "reviewer_reference", reviewer)
        object.__setattr__(self, "reviewed_at_utc", reviewed)
        object.__setattr__(self, "packet_hash", packet.packet_hash)
        object.__setattr__(self, "validation_result_hash", packet.validation_result_hash)
        object.__setattr__(self, "review_item_hashes", item_hashes)
        object.__setattr__(
            self,
            "receipt_hash",
            canonical_sha256(
                {
                    "disposition": self.disposition,
                    "packet_hash": packet.packet_hash,
                    "receipt_id": receipt_id,
                    "review_item_hashes": list(item_hashes),
                    "reviewed_at_utc": reviewed,
                    "reviewer_reference": reviewer,
                    "schema_version": self.schema_version,
                    "validation_result_hash": packet.validation_result_hash,
                }
            ),
        )

    def to_record(self) -> dict[str, object]:
        return {
            "authority": {
                "ai_role": self.ai_role,
                "calculation_authority": self.calculation_authority,
                "evidence_approved": False,
                "evidence_authority": self.evidence_authority,
                "evidence_promotion_allowed": False,
                "evidence_rejected": False,
                "execution_allowed": False,
                "gap_closed": False,
                "network_used": False,
                "operator_review_completed": True,
                "order_allowed": False,
                "provider_selected": False,
                "replay_activation_allowed": False,
                "result_resolved": False,
                "sdk_used": False,
                "venue_selected": False,
            },
            "disposition": self.disposition,
            "lineage": {
                "packet_hash": self.packet_hash,
                "review_item_hashes": list(self.review_item_hashes),
                "validation_result_hash": self.validation_result_hash,
            },
            "receipt_hash": self.receipt_hash,
            "receipt_id": self.receipt_id,
            "reviewed_at_utc": self.reviewed_at_utc,
            "reviewer_reference": self.reviewer_reference,
            "schema_version": self.schema_version,
        }


def render_operator_review_receipt_json(
    receipt: BTCLocalExportOperatorReviewReceipt,
) -> str:
    if type(receipt) is not BTCLocalExportOperatorReviewReceipt:
        raise TypeError("receipt must be exact BTCLocalExportOperatorReviewReceipt")
    return json.dumps(
        receipt.to_record(), ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ) + "\n"


def build_reference_receipt() -> BTCLocalExportOperatorReviewReceipt:
    packet = build_operator_review_packet(
        build_reference_result(),
        packet_id="btc-local-export-review-packet-v1",
        packet_created_at_utc="2026-07-21T00:00:21Z",
    )
    return BTCLocalExportOperatorReviewReceipt(
        receipt_id="btc-local-export-review-receipt-v1",
        review_packet=packet,
        reviewer_reference="operator-reference-v1",
        reviewed_at_utc="2026-07-21T00:00:22Z",
        disposition="REVIEWED_NO_PROMOTION",
    )
