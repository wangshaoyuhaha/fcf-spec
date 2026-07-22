from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0071_btc_perpetual_paper_stress_trigger_result_review_registry_app_1.contracts import (
    BTCPerpetualPaperStressTriggerResultReviewRegistry,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


@dataclass(frozen=True)
class BTCPerpetualPaperStressTriggerResultOperatorReviewPacket:
    packet_id: str
    review_registry: BTCPerpetualPaperStressTriggerResultReviewRegistry
    packet_created_at_utc: str
    operator_review_state: str = "OPERATOR_REVIEW_REQUIRED"
    operator_review_required: bool = True
    packet_only: bool = True
    disposition_assigned: bool = False
    evidence_approved: bool = False
    evidence_rejected: bool = False
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
        "btc-perpetual-paper-stress-trigger-result-operator-review-packet-v1"
    )
    review_registry_hash: str = field(init=False)
    evaluation_snapshot_hash: str = field(init=False)
    scenario_registry_hash: str = field(init=False)
    complete_rule_bundle_hash: str = field(init=False)
    venue_id: str = field(init=False)
    contract_id: str = field(init=False)
    registry_registered_at_utc: str = field(init=False)
    record_hashes: tuple[str, ...] = field(init=False)
    triggered_record_hashes: tuple[str, ...] = field(init=False)
    non_triggered_record_hashes: tuple[str, ...] = field(init=False)
    triggered_count: int = field(init=False)
    non_triggered_count: int = field(init=False)
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "packet_id", identifier(self.packet_id, "packet_id"))
        registry = self.review_registry
        if type(registry) is not BTCPerpetualPaperStressTriggerResultReviewRegistry:
            raise ValueError("review packet requires one exact typed FCP-0071 registry")
        if (
            registry.operator_review_required is not True
            or registry.registration_only is not True
            or registry.recalculation_allowed is not False
            or registry.recommendation_allowed is not False
        ):
            raise ValueError("review registry authority boundary is invalid")
        created = utc(self.packet_created_at_utc, "packet_created_at_utc")
        if instant(created) < instant(registry.registered_at_utc):
            raise ValueError("review packet cannot precede registry evidence")
        if self.operator_review_state != "OPERATOR_REVIEW_REQUIRED":
            raise ValueError("review packet must require Operator review")
        forbidden = (
            self.disposition_assigned,
            self.evidence_approved,
            self.evidence_rejected,
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
            self.operator_review_required is not True
            or self.packet_only is not True
            or any(forbidden)
        ):
            raise ValueError("review packet cannot decide, recommend, act, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("review packet authority identities are immutable")
        if self.schema_version != (
            "btc-perpetual-paper-stress-trigger-result-operator-review-packet-v1"
        ):
            raise ValueError("schema_version is not registered")

        hashes = tuple(item.review_record_hash for item in registry.records)
        triggered = tuple(
            item.review_record_hash for item in registry.records if item.triggered
        )
        non_triggered = tuple(
            item.review_record_hash for item in registry.records if not item.triggered
        )
        if (
            len(set(hashes)) != len(hashes)
            or set(triggered).intersection(non_triggered)
            or set(triggered).union(non_triggered) != set(hashes)
            or len(triggered) + len(non_triggered) != len(hashes)
        ):
            raise ValueError("review packet trigger groups must be complete")

        values = {
            "review_registry_hash": registry.registry_hash,
            "evaluation_snapshot_hash": registry.evaluation_snapshot_hash,
            "scenario_registry_hash": registry.scenario_registry_hash,
            "complete_rule_bundle_hash": registry.complete_rule_bundle_hash,
            "venue_id": registry.venue_id,
            "contract_id": registry.contract_id,
            "registry_registered_at_utc": registry.registered_at_utc,
            "record_hashes": hashes,
            "triggered_record_hashes": triggered,
            "non_triggered_record_hashes": non_triggered,
            "triggered_count": len(triggered),
            "non_triggered_count": len(non_triggered),
        }
        for name, value in values.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "packet_created_at_utc", created)
        object.__setattr__(
            self,
            "packet_hash",
            canonical_sha256(
                {
                    "complete_rule_bundle_hash": registry.complete_rule_bundle_hash,
                    "contract_id": registry.contract_id,
                    "evaluation_snapshot_hash": registry.evaluation_snapshot_hash,
                    "non_triggered_record_hashes": list(non_triggered),
                    "operator_review_state": self.operator_review_state,
                    "packet_created_at_utc": created,
                    "packet_id": self.packet_id,
                    "record_hashes": list(hashes),
                    "review_registry_hash": registry.registry_hash,
                    "scenario_registry_hash": registry.scenario_registry_hash,
                    "schema_version": self.schema_version,
                    "triggered_record_hashes": list(triggered),
                    "venue_id": registry.venue_id,
                }
            ),
        )
