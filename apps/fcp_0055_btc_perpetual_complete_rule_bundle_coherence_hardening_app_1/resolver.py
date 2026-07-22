from __future__ import annotations

from apps.fcp_0053_btc_perpetual_rule_bundle_point_in_time_coherence_gate_app_1 import (
    BTCPerpetualRuleBundleSnapshot,
)
from apps.fcp_0054_btc_perpetual_mark_index_liquidation_mechanics_evidence_registry_app_1 import (
    BTCPerpetualLiquidationMechanicsRegistry,
    resolve_btc_perpetual_liquidation_mechanics_version,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant

from .contracts import BTCPerpetualCompleteRuleBundleSnapshot


def resolve_btc_perpetual_complete_rule_bundle(
    base_bundle: BTCPerpetualRuleBundleSnapshot,
    liquidation_registry: BTCPerpetualLiquidationMechanicsRegistry,
) -> BTCPerpetualCompleteRuleBundleSnapshot:
    if not isinstance(base_bundle, BTCPerpetualRuleBundleSnapshot):
        raise TypeError("base_bundle must be typed FCP-0053 evidence")
    if not isinstance(
        liquidation_registry,
        BTCPerpetualLiquidationMechanicsRegistry,
    ):
        raise TypeError("liquidation_registry must be typed FCP-0054 evidence")
    if (
        liquidation_registry.contract_registry.registry_hash
        != base_bundle.contract_registry_hash
    ):
        raise ValueError("complete bundle requires one exact FCP-0046 registry")
    target = instant(base_bundle.effective_at_utc)
    if instant(liquidation_registry.as_of_utc) > target:
        raise ValueError("liquidation registry cannot be newer than bundle instant")
    if instant(liquidation_registry.artifact.registered_at_utc) > target:
        raise ValueError("liquidation artifact cannot be newer than bundle instant")
    liquidation = resolve_btc_perpetual_liquidation_mechanics_version(
        liquidation_registry,
        venue_id=base_bundle.venue_id,
        contract_id=base_bundle.contract_id,
        at_utc=base_bundle.effective_at_utc,
    )
    if liquidation.contract_entry_hash != base_bundle.contract_entry_hash:
        raise ValueError("complete bundle requires one exact contract entry")
    return BTCPerpetualCompleteRuleBundleSnapshot(
        venue_id=base_bundle.venue_id,
        contract_id=base_bundle.contract_id,
        effective_at_utc=base_bundle.effective_at_utc,
        margin_mode=base_bundle.margin_mode,
        position_mode=base_bundle.position_mode,
        lifecycle_state=base_bundle.lifecycle_state,
        base_rule_bundle_hash=base_bundle.snapshot_hash,
        contract_registry_hash=base_bundle.contract_registry_hash,
        margin_registry_hash=base_bundle.margin_registry_hash,
        funding_registry_hash=base_bundle.funding_registry_hash,
        fee_registry_hash=base_bundle.fee_registry_hash,
        liquidation_registry_hash=liquidation_registry.registry_hash,
        contract_entry_hash=base_bundle.contract_entry_hash,
        margin_rule_entry_hash=base_bundle.margin_rule_entry_hash,
        funding_rule_entry_hash=base_bundle.funding_rule_entry_hash,
        fee_rule_entry_hash=base_bundle.fee_rule_entry_hash,
        liquidation_rule_entry_hash=liquidation.entry_hash,
        liquidation_effective_from_utc=liquidation.effective_from_utc,
    )
