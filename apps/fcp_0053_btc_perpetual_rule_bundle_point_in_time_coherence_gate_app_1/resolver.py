from __future__ import annotations

from apps.fcp_0046_btc_perpetual_venue_contract_lifecycle_registry_app_1 import (
    BTCPerpetualContractLifecycleRegistry,
    resolve_btc_perpetual_contract_version,
)
from apps.fcp_0047_btc_perpetual_margin_risk_tier_evidence_registry_app_1 import (
    BTCPerpetualMarginRiskTierRegistry,
    resolve_btc_perpetual_margin_rule_version,
)
from apps.fcp_0048_btc_perpetual_funding_method_schedule_evidence_registry_app_1 import (
    BTCPerpetualFundingMethodScheduleRegistry,
    resolve_btc_perpetual_funding_rule_version,
)
from apps.fcp_0049_btc_perpetual_fee_rebate_schedule_evidence_registry_app_1 import (
    BTCPerpetualFeeRebateScheduleRegistry,
    resolve_btc_perpetual_fee_rebate_rule_version,
)

from .contracts import BTCPerpetualRuleBundleSnapshot


def resolve_btc_perpetual_rule_bundle(
    contract_registry: BTCPerpetualContractLifecycleRegistry,
    margin_registry: BTCPerpetualMarginRiskTierRegistry,
    funding_registry: BTCPerpetualFundingMethodScheduleRegistry,
    fee_registry: BTCPerpetualFeeRebateScheduleRegistry,
    *,
    venue_id: str,
    contract_id: str,
    margin_mode: str,
    position_mode: str,
    at_utc: str,
) -> BTCPerpetualRuleBundleSnapshot:
    if not isinstance(contract_registry, BTCPerpetualContractLifecycleRegistry):
        raise TypeError("contract_registry must be typed FCP-0046 evidence")
    if not isinstance(margin_registry, BTCPerpetualMarginRiskTierRegistry):
        raise TypeError("margin_registry must be typed FCP-0047 evidence")
    if not isinstance(funding_registry, BTCPerpetualFundingMethodScheduleRegistry):
        raise TypeError("funding_registry must be typed FCP-0048 evidence")
    if not isinstance(fee_registry, BTCPerpetualFeeRebateScheduleRegistry):
        raise TypeError("fee_registry must be typed FCP-0049 evidence")

    contract_registry_hash = contract_registry.registry_hash
    dependent_contract_hashes = (
        margin_registry.contract_registry.registry_hash,
        funding_registry.contract_registry.registry_hash,
        fee_registry.contract_registry.registry_hash,
    )
    if any(value != contract_registry_hash for value in dependent_contract_hashes):
        raise ValueError("dependent registries require one exact FCP-0046 registry")

    contract = resolve_btc_perpetual_contract_version(
        contract_registry,
        venue_id=venue_id,
        contract_id=contract_id,
        at_utc=at_utc,
    )
    margin = resolve_btc_perpetual_margin_rule_version(
        margin_registry,
        venue_id=venue_id,
        contract_id=contract_id,
        margin_mode=margin_mode,
        position_mode=position_mode,
        at_utc=at_utc,
    )
    funding = resolve_btc_perpetual_funding_rule_version(
        funding_registry,
        venue_id=venue_id,
        contract_id=contract_id,
        at_utc=at_utc,
    )
    fee = resolve_btc_perpetual_fee_rebate_rule_version(
        fee_registry,
        venue_id=venue_id,
        contract_id=contract_id,
        at_utc=at_utc,
    )
    if any(
        value != contract.entry_hash
        for value in (
            margin.contract_entry_hash,
            funding.contract_entry_hash,
            fee.contract_entry_hash,
        )
    ):
        raise ValueError("resolved rules require one exact contract entry")

    return BTCPerpetualRuleBundleSnapshot(
        venue_id=contract.venue_id,
        contract_id=contract.contract_id,
        effective_at_utc=at_utc,
        margin_mode=margin.margin_mode,
        position_mode=margin.position_mode,
        lifecycle_state=contract.lifecycle_state,
        contract_registry_hash=contract_registry_hash,
        margin_registry_hash=margin_registry.registry_hash,
        funding_registry_hash=funding_registry.registry_hash,
        fee_registry_hash=fee_registry.registry_hash,
        contract_entry_hash=contract.entry_hash,
        margin_rule_entry_hash=margin.entry_hash,
        funding_rule_entry_hash=funding.entry_hash,
        fee_rule_entry_hash=fee.entry_hash,
        contract_effective_from_utc=contract.effective_from_utc,
        margin_effective_from_utc=margin.effective_from_utc,
        funding_effective_from_utc=funding.effective_from_utc,
        fee_effective_from_utc=fee.effective_from_utc,
    )
