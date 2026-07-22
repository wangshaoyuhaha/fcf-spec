from __future__ import annotations

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import (
    BTCPerpetualLiquidationMechanicsRegistry,
    BTCPerpetualLiquidationMechanicsVersion,
)


def resolve_btc_perpetual_liquidation_mechanics_version(
    registry: BTCPerpetualLiquidationMechanicsRegistry,
    *,
    venue_id: str,
    contract_id: str,
    at_utc: str,
) -> BTCPerpetualLiquidationMechanicsVersion:
    if not isinstance(registry, BTCPerpetualLiquidationMechanicsRegistry):
        raise TypeError("registry must be typed FCP-0054 evidence")
    target = instant(utc(at_utc, "at_utc"))
    matches = tuple(
        item
        for item in registry.versions
        if item.venue_id == venue_id
        and item.contract_id == contract_id
        and instant(item.effective_from_utc) <= target
        and (
            item.effective_to_utc is None
            or target < instant(item.effective_to_utc)
        )
    )
    if len(matches) != 1:
        raise LookupError("point-in-time liquidation evidence is missing or ambiguous")
    return matches[0]
