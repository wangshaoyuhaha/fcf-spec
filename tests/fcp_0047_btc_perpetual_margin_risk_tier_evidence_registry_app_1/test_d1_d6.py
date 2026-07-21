from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal

import pytest

from apps.fcp_0046_btc_perpetual_venue_contract_lifecycle_registry_app_1 import (
    BTCPerpetualContractLifecycleRegistry,
    BTCPerpetualContractVersion,
    RegisteredBTCContractRuleArtifact,
)
from apps.fcp_0047_btc_perpetual_margin_risk_tier_evidence_registry_app_1 import (
    BTCCollateralHaircutRule,
    BTCMarginRiskTier,
    BTCPerpetualMarginRiskTierRegistry,
    BTCPerpetualMarginRuleVersion,
    RegisteredBTCMarginRuleArtifact,
    resolve_btc_collateral_haircut_rule,
    resolve_btc_perpetual_margin_rule_version,
    resolve_btc_perpetual_margin_risk_tier,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _rights():
    return LocalEventRights("synthetic-test", "local-paper-research", 30)


def _contract_artifact():
    content = b"contract-rules\n"
    return RegisteredBTCContractRuleArtifact(
        artifact_id="contract-rules",
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights=_rights(),
        observed_at_utc="2026-07-21T00:00:00Z",
        registered_at_utc="2026-07-21T00:01:00Z",
    )


def _contract_version():
    return BTCPerpetualContractVersion(
        entry_id="contract-entry-v1",
        version_id="contract-v1",
        artifact_id="contract-rules",
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        venue_symbol="BTCUSDT",
        settlement_type="LINEAR",
        base_asset="BTC",
        quote_asset="USDT",
        settlement_asset="USDT",
        collateral_assets=("USDT",),
        contract_multiplier=Decimal("1"),
        price_tick=Decimal("0.1"),
        quantity_step=Decimal("0.001"),
        minimum_quantity=Decimal("0.001"),
        minimum_notional=Decimal("5"),
        effective_from_utc="2026-01-01T00:00:00Z",
        effective_to_utc=None,
        lifecycle_state="ACTIVE",
    )


def _contract_registry():
    return BTCPerpetualContractLifecycleRegistry(
        registry_id="btc-contract-registry-v1",
        artifact=_contract_artifact(),
        entries=(_contract_version(),),
        as_of_utc="2026-07-21T00:02:00Z",
    )


def _margin_artifact():
    content = b"margin-rules\n"
    return RegisteredBTCMarginRuleArtifact(
        artifact_id="margin-rules",
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights=_rights(),
        observed_at_utc="2026-07-21T00:03:00Z",
        registered_at_utc="2026-07-21T00:04:00Z",
    )


def _tier(name="tier-1", floor="0", cap="100000", **updates):
    values = {
        "tier_id": name,
        "notional_floor": Decimal(floor),
        "notional_cap": Decimal(cap),
        "initial_margin_rate": Decimal("0.10"),
        "maintenance_margin_rate": Decimal("0.05"),
        "maintenance_amount_deduction": Decimal("0"),
        "risk_limit": Decimal(cap),
    }
    values.update(updates)
    return BTCMarginRiskTier(**values)


def _collateral(asset="USDT", valuation="USD", haircut="0"):
    return BTCCollateralHaircutRule(
        collateral_asset=asset,
        valuation_asset=valuation,
        haircut_rate=haircut,
    )


def _version(name="margin-v1", **updates):
    contract = _contract_version()
    values = {
        "entry_id": f"entry-{name}",
        "version_id": name,
        "artifact_id": "margin-rules",
        "contract_entry_hash": contract.entry_hash,
        "venue_id": "venue-a",
        "contract_id": "BTC-USDT-PERP",
        "margin_mode": "ISOLATED",
        "position_mode": "ONE_WAY",
        "tiers": (_tier(),),
        "collateral_rules": (_collateral(),),
        "effective_from_utc": "2026-01-01T00:00:00Z",
        "effective_to_utc": None,
    }
    values.update(updates)
    return BTCPerpetualMarginRuleVersion(**values)


def _registry(*versions, contract_registry=None, artifact=None):
    return BTCPerpetualMarginRiskTierRegistry(
        registry_id="btc-margin-registry-v1",
        artifact=artifact or _margin_artifact(),
        contract_registry=contract_registry or _contract_registry(),
        versions=tuple(versions or (_version(),)),
        as_of_utc="2026-07-21T00:05:00Z",
    )


def test_margin_rule_preserves_exact_modes_tiers_and_collateral():
    registry = _registry()
    version = registry.versions[0]

    assert version.margin_mode == "ISOLATED"
    assert version.position_mode == "ONE_WAY"
    assert version.tiers[0].initial_margin_rate == Decimal("0.10")
    assert version.collateral_rules[0].haircut_rate == Decimal("0")
    assert len(version.entry_hash) == len(registry.registry_hash) == 64


def test_margin_tier_rejects_float_and_invalid_rate_order():
    with pytest.raises(ValueError, match="exact decimal"):
        _tier(initial_margin_rate=0.1)
    with pytest.raises(ValueError, match="maintenance <= initial"):
        _tier(initial_margin_rate=Decimal("0.04"))


def test_margin_tier_rejects_invalid_interval_and_risk_limit():
    with pytest.raises(ValueError, match="strictly increasing"):
        _tier(floor="100", cap="100")
    with pytest.raises(ValueError, match="cannot be below"):
        _tier(risk_limit=Decimal("10"))


def test_tiers_must_begin_at_zero_and_be_contiguous():
    with pytest.raises(ValueError, match="begin at zero"):
        _version(tiers=(_tier(floor="1"),))
    first = _tier(cap="100")
    second = _tier(name="tier-2", floor="101", cap="200")
    with pytest.raises(ValueError, match="contiguous"):
        _version(tiers=(first, second))


def test_collateral_haircut_requires_exact_rate_below_one():
    with pytest.raises(ValueError, match="exact decimal"):
        _collateral(haircut=0.1)
    with pytest.raises(ValueError, match="unit rate"):
        _collateral(haircut="1")


def test_registry_binds_exact_fcp_0046_contract_entry():
    registry = _registry()
    assert registry.contract_registry.registry_hash

    with pytest.raises(ValueError, match="FCP-0046 contract lineage"):
        _registry(_version(contract_entry_hash="0" * 64))


def test_registry_rejects_margin_artifact_lineage_mismatch():
    with pytest.raises(ValueError, match="artifact lineage mismatch"):
        _registry(_version(artifact_id="other-margin-rules"))


def test_point_in_time_lookup_uses_half_open_effective_intervals():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(
        name="margin-v2",
        effective_from_utc="2026-06-01T00:00:00Z",
        tiers=(_tier(initial_margin_rate=Decimal("0.20")),),
    )
    registry = _registry(first, second)

    assert resolve_btc_perpetual_margin_rule_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        margin_mode="isolated",
        position_mode="one_way",
        at_utc="2026-05-31T23:59:59Z",
    ).version_id == "margin-v1"
    assert resolve_btc_perpetual_margin_rule_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        margin_mode="ISOLATED",
        position_mode="ONE_WAY",
        at_utc="2026-06-01T00:00:00Z",
    ).version_id == "margin-v2"


def test_registry_rejects_effective_interval_overlap():
    first = _version(effective_to_utc="2026-07-01T00:00:00Z")
    second = _version(name="margin-v2", effective_from_utc="2026-06-01T00:00:00Z")

    with pytest.raises(ValueError, match="intervals overlap"):
        _registry(first, second)


def test_risk_tier_lookup_is_exact_and_half_open():
    first = _tier(cap="100")
    second = _tier(
        name="tier-2",
        floor="100",
        cap="200",
        initial_margin_rate=Decimal("0.20"),
        maintenance_margin_rate=Decimal("0.10"),
    )
    version = _version(tiers=(first, second))

    assert resolve_btc_perpetual_margin_risk_tier(version, notional=Decimal("99.99")).tier_id == "tier-1"
    assert resolve_btc_perpetual_margin_risk_tier(version, notional=Decimal("100")).tier_id == "tier-2"


def test_risk_tier_lookup_rejects_float_and_missing_evidence():
    version = _version()
    with pytest.raises(ValueError, match="exact decimal"):
        resolve_btc_perpetual_margin_risk_tier(version, notional=1.0)
    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_margin_risk_tier(version, notional=Decimal("100000"))


def test_collateral_lookup_fails_closed():
    version = _version(collateral_rules=(_collateral("USDC", "USD", "0.02"), _collateral()))
    assert resolve_btc_collateral_haircut_rule(
        version,
        collateral_asset="USDC",
        valuation_asset="USD",
    ).haircut_rate == Decimal("0.02")
    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_collateral_haircut_rule(
            version,
            collateral_asset="BTC",
            valuation_asset="USD",
        )


def test_registry_rejects_evidence_or_contract_state_after_as_of():
    late_artifact = replace(_margin_artifact(), registered_at_utc="2026-07-22T00:00:00Z")
    with pytest.raises(ValueError, match="evidence after as_of"):
        _registry(artifact=late_artifact)
    late_contract = replace(_contract_registry(), as_of_utc="2026-07-22T00:00:00Z")
    with pytest.raises(ValueError, match="newer than margin"):
        _registry(contract_registry=late_contract)


def test_registry_is_deterministic_and_requires_stable_order():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(name="margin-v2", effective_from_utc="2026-06-01T00:00:00Z")
    assert _registry(first, second) == _registry(first, second)
    with pytest.raises(ValueError, match="deterministically ordered"):
        _registry(second, first)


def test_registry_authority_boundary_is_immutable():
    registry = _registry()
    for changes in (
        {"operator_review_required": False},
        {"source_selected": True},
        {"balance_calculation_allowed": True},
        {"position_calculation_allowed": True},
        {"margin_calculation_allowed": True},
        {"pnl_calculation_allowed": True},
        {"liquidation_calculation_allowed": True},
        {"funding_calculation_allowed": True},
        {"fee_calculation_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot calculate, select, execute, or close"):
            replace(registry, **changes)
