from __future__ import annotations

from decimal import Decimal, InvalidOperation

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import (
    BTCPerpetualMarginRiskTierRegistry,
    BTCPerpetualMarginRuleVersion,
)


def _exact_nonnegative_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must use an exact decimal value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return result


def resolve_btc_perpetual_margin_rule_version(
    registry: BTCPerpetualMarginRiskTierRegistry,
    *,
    venue_id: str,
    contract_id: str,
    margin_mode: str,
    position_mode: str,
    at_utc: str,
) -> BTCPerpetualMarginRuleVersion:
    if not isinstance(registry, BTCPerpetualMarginRiskTierRegistry):
        raise TypeError("registry must be typed FCP-0047 evidence")
    target = instant(utc(at_utc, "at_utc"))
    margin = str(margin_mode).strip().upper()
    position = str(position_mode).strip().upper()
    matches = tuple(
        item
        for item in registry.versions
        if item.venue_id == venue_id
        and item.contract_id == contract_id
        and item.margin_mode == margin
        and item.position_mode == position
        and instant(item.effective_from_utc) <= target
        and (item.effective_to_utc is None or target < instant(item.effective_to_utc))
    )
    if len(matches) != 1:
        raise LookupError("point-in-time margin evidence is missing or ambiguous")
    return matches[0]


def resolve_btc_perpetual_margin_risk_tier(
    version: BTCPerpetualMarginRuleVersion,
    *,
    notional: object,
):
    if not isinstance(version, BTCPerpetualMarginRuleVersion):
        raise TypeError("version must be typed FCP-0047 evidence")
    target = _exact_nonnegative_decimal(notional, "notional")
    matches = tuple(
        item
        for item in version.tiers
        if item.notional_floor <= target < item.notional_cap
    )
    if len(matches) != 1:
        raise LookupError("notional risk-tier evidence is missing or ambiguous")
    return matches[0]


def resolve_btc_collateral_haircut_rule(
    version: BTCPerpetualMarginRuleVersion,
    *,
    collateral_asset: str,
    valuation_asset: str,
):
    if not isinstance(version, BTCPerpetualMarginRuleVersion):
        raise TypeError("version must be typed FCP-0047 evidence")
    matches = tuple(
        item
        for item in version.collateral_rules
        if item.collateral_asset == collateral_asset
        and item.valuation_asset == valuation_asset
    )
    if len(matches) != 1:
        raise LookupError("collateral haircut evidence is missing or ambiguous")
    return matches[0]
