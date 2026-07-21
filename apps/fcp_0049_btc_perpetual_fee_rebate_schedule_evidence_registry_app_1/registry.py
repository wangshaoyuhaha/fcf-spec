from __future__ import annotations

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import BTCPerpetualFeeRebateRuleVersion, BTCPerpetualFeeRebateScheduleRegistry


def resolve_btc_perpetual_fee_rebate_rule_version(
    registry: BTCPerpetualFeeRebateScheduleRegistry,
    *,
    venue_id: str,
    contract_id: str,
    at_utc: str,
) -> BTCPerpetualFeeRebateRuleVersion:
    if not isinstance(registry, BTCPerpetualFeeRebateScheduleRegistry):
        raise TypeError("registry must be typed FCP-0049 evidence")
    target = instant(utc(at_utc, "at_utc"))
    matches = tuple(
        item
        for item in registry.versions
        if item.venue_id == venue_id
        and item.contract_id == contract_id
        and instant(item.effective_from_utc) <= target
        and (item.effective_to_utc is None or target < instant(item.effective_to_utc))
    )
    if len(matches) != 1:
        raise LookupError("point-in-time fee evidence is missing or ambiguous")
    return matches[0]
