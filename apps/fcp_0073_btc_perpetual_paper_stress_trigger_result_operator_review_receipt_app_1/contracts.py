from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0072_btc_perpetual_paper_stress_trigger_result_operator_review_packet_app_1.contracts import (
    BTCPerpetualPaperStressTriggerResultOperatorReviewPacket,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


REVIEW_DISPOSITIONS = (
    "REVIEWED_NO_RESOLUTION",
    "DEFERRED_PENDING_EVIDENCE",
    "ESCALATED_FOR_RESEARCH",
)


@dataclass(frozen=True)
class BTCPerpetualPaperStressTriggerResultOperatorReviewReceipt:
    receipt_id: str
    review_packet: BTCPerpetualPaperStressTriggerResultOperatorReviewPacket
    reviewer_reference: str
    reviewed_at_utc: str
    disposition: str
    operator_review_completed: bool = True
    receipt_only: bool = True
    evidence_approved: bool = False
    evidence_rejected: bool = False
    result_resolved: bool = False
    recommendation_allowed: bool = False
    account_state_allowed: bool = False
    margin_calculation_allowed: bool = False
    leverage_calculation_allowed: bool = False
    liquidation_action_allowed: bool = False
    balance_calculation_allowed: bool = False
    position_calculation_allowed: bool = False
    pnl_calculation_allowed: bool = False
    insurance_fund_mutation_allowed: bool = False
    adl_action_allowed: bool = False
    order_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    schema_version: str = (
        "btc-perpetual-paper-stress-trigger-result-operator-review-receipt-v1"
    )
    packet_hash: str = field(init=False)
    review_registry_hash: str = field(init=False)
    evaluation_snapshot_hash: str = field(init=False)
    scenario_registry_hash: str = field(init=False)
    complete_rule_bundle_hash: str = field(init=False)
    venue_id: str = field(init=False)
    contract_id: str = field(init=False)
    packet_created_at_utc: str = field(init=False)
    record_hashes: tuple[str, ...] = field(init=False)
    triggered_record_hashes: tuple[str, ...] = field(init=False)
    non_triggered_record_hashes: tuple[str, ...] = field(init=False)
    triggered_count: int = field(init=False)
    non_triggered_count: int = field(init=False)
    receipt_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "receipt_id", identifier(self.receipt_id, "receipt_id"))
        packet = self.review_packet
        if type(packet) is not BTCPerpetualPaperStressTriggerResultOperatorReviewPacket:
            raise ValueError("review receipt requires one exact typed FCP-0072 packet")
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
            self.recommendation_allowed,
            self.account_state_allowed,
            self.margin_calculation_allowed,
            self.leverage_calculation_allowed,
            self.liquidation_action_allowed,
            self.balance_calculation_allowed,
            self.position_calculation_allowed,
            self.pnl_calculation_allowed,
            self.insurance_fund_mutation_allowed,
            self.adl_action_allowed,
            self.order_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.operator_review_completed is not True
            or self.receipt_only is not True
            or any(forbidden)
        ):
            raise ValueError("review receipt cannot approve, resolve, recommend, act, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("review receipt authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-trigger-result-operator-review-receipt-v1"
        ):
            raise ValueError("schema_version is not registered")

        values = {
            "packet_hash": packet.packet_hash,
            "review_registry_hash": packet.review_registry_hash,
            "evaluation_snapshot_hash": packet.evaluation_snapshot_hash,
            "scenario_registry_hash": packet.scenario_registry_hash,
            "complete_rule_bundle_hash": packet.complete_rule_bundle_hash,
            "venue_id": packet.venue_id,
            "contract_id": packet.contract_id,
            "packet_created_at_utc": packet.packet_created_at_utc,
            "record_hashes": packet.record_hashes,
            "triggered_record_hashes": packet.triggered_record_hashes,
            "non_triggered_record_hashes": packet.non_triggered_record_hashes,
            "triggered_count": packet.triggered_count,
            "non_triggered_count": packet.non_triggered_count,
        }
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "reviewer_reference", reviewer)
        object.__setattr__(self, "reviewed_at_utc", reviewed)
        object.__setattr__(
            self,
            "receipt_hash",
            canonical_sha256(
                {
                    "disposition": self.disposition,
                    "non_triggered_record_hashes": list(packet.non_triggered_record_hashes),
                    "packet_hash": packet.packet_hash,
                    "receipt_id": self.receipt_id,
                    "record_hashes": list(packet.record_hashes),
                    "reviewed_at_utc": reviewed,
                    "reviewer_reference": reviewer,
                    "schema_version": self.schema_version,
                    "triggered_record_hashes": list(packet.triggered_record_hashes),
                }
            ),
        )
