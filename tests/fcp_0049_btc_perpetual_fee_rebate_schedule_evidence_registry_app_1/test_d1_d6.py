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
from apps.fcp_0049_btc_perpetual_fee_rebate_schedule_evidence_registry_app_1 import (
    BTCFeeRebateTier,
    BTCPerpetualFeeRebateRuleVersion,
    BTCPerpetualFeeRebateScheduleRegistry,
    RegisteredBTCFeeRebateRuleArtifact,
    resolve_btc_perpetual_fee_rebate_rule_version,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _rights():
    return LocalEventRights("synthetic-test", "local-paper-research", 30)


def _contract_artifact():
    content = b"contract-rules\n"
    return RegisteredBTCContractRuleArtifact(
        "contract-rules", hashlib.sha256(content).hexdigest(), len(content),
        _rights(), "2026-07-21T00:00:00Z", "2026-07-21T00:01:00Z",
    )


def _contract_version():
    return BTCPerpetualContractVersion(
        entry_id="contract-entry-v1", version_id="contract-v1",
        artifact_id="contract-rules", venue_id="venue-a",
        contract_id="BTC-USDT-PERP", venue_symbol="BTCUSDT",
        settlement_type="LINEAR", base_asset="BTC", quote_asset="USDT",
        settlement_asset="USDT", collateral_assets=("USDT",),
        contract_multiplier=Decimal("1"), price_tick=Decimal("0.1"),
        quantity_step=Decimal("0.001"), minimum_quantity=Decimal("0.001"),
        minimum_notional=Decimal("5"), effective_from_utc="2026-01-01T00:00:00Z",
        effective_to_utc=None, lifecycle_state="ACTIVE",
    )


def _contract_registry():
    return BTCPerpetualContractLifecycleRegistry(
        "btc-contract-registry-v1", _contract_artifact(),
        (_contract_version(),), "2026-07-21T00:02:00Z",
    )


def _artifact():
    content = b"fee-rules\n"
    return RegisteredBTCFeeRebateRuleArtifact(
        "fee-rules", hashlib.sha256(content).hexdigest(), len(content),
        _rights(), "2026-07-21T00:03:00Z", "2026-07-21T00:04:00Z",
    )


def _tier(name="tier-1", floor="0", cap="100000", **updates):
    values = {
        "tier_id": name,
        "trailing_volume_floor": Decimal(floor),
        "trailing_volume_cap": Decimal(cap),
        "maker_rate": Decimal("-0.0001"),
        "taker_rate": Decimal("0.0005"),
    }
    values.update(updates)
    return BTCFeeRebateTier(**values)


def _version(name="fee-v1", **updates):
    values = {
        "entry_id": f"entry-{name}", "version_id": name,
        "artifact_id": "fee-rules", "contract_entry_hash": _contract_version().entry_hash,
        "venue_id": "venue-a", "contract_id": "BTC-USDT-PERP",
        "measurement_asset": "USDT", "trailing_window_seconds": 2592000,
        "fee_assets": ("USDT",), "tiers": (_tier(),),
        "effective_from_utc": "2026-01-01T00:00:00Z", "effective_to_utc": None,
    }
    values.update(updates)
    return BTCPerpetualFeeRebateRuleVersion(**values)


def _registry(*versions, artifact=None, contract_registry=None):
    return BTCPerpetualFeeRebateScheduleRegistry(
        registry_id="btc-fee-registry-v1", artifact=artifact or _artifact(),
        contract_registry=contract_registry or _contract_registry(),
        versions=tuple(versions or (_version(),)), as_of_utc="2026-07-21T00:05:00Z",
    )


def test_fee_schedule_preserves_exact_signed_maker_rebate():
    registry = _registry()
    tier = registry.versions[0].tiers[0]
    assert tier.maker_rate == Decimal("-0.0001")
    assert tier.taker_rate == Decimal("0.0005")
    assert len(tier.tier_hash) == len(registry.registry_hash) == 64


def test_fee_rate_rejects_float_nonfinite_and_out_of_range():
    with pytest.raises(ValueError, match="exact decimal"):
        _tier(maker_rate=-0.0001)
    with pytest.raises(ValueError, match="finite"):
        _tier(taker_rate=Decimal("Infinity"))
    with pytest.raises(ValueError, match="signed unit rate"):
        _tier(taker_rate=Decimal("1.1"))


def test_volume_tier_interval_must_be_nonnegative_and_increasing():
    with pytest.raises(ValueError, match="nonnegative and increasing"):
        _tier(floor="100", cap="100")
    with pytest.raises(ValueError, match="nonnegative and increasing"):
        _tier(floor="-1")


def test_fee_tiers_begin_at_zero_and_are_contiguous():
    with pytest.raises(ValueError, match="begin at zero"):
        _version(tiers=(_tier(floor="1"),))
    first = _tier(cap="100")
    second = _tier(name="tier-2", floor="101", cap="200")
    with pytest.raises(ValueError, match="contiguous"):
        _version(tiers=(first, second))


def test_fee_assets_are_ordered_unique_and_nonempty():
    assert _version(fee_assets=("USDC", "USDT")).fee_assets == ("USDC", "USDT")
    for assets in ((), ("USDT", "USDT"), ("USDT", "USDC")):
        with pytest.raises(ValueError, match="ordered, and unique"):
            _version(fee_assets=assets)


def test_trailing_window_must_be_positive_integer():
    with pytest.raises(ValueError, match="positive integer"):
        _version(trailing_window_seconds=0)
    with pytest.raises(ValueError, match="positive integer"):
        _version(trailing_window_seconds=True)


def test_registry_binds_exact_fcp_0046_contract_entry():
    assert _registry().contract_registry.registry_hash
    with pytest.raises(ValueError, match="FCP-0046 contract lineage"):
        _registry(_version(contract_entry_hash="0" * 64))


def test_registry_rejects_artifact_lineage_mismatch():
    with pytest.raises(ValueError, match="artifact lineage mismatch"):
        _registry(_version(artifact_id="other-fee-rules"))


def test_point_in_time_lookup_uses_half_open_effective_intervals():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(name="fee-v2", effective_from_utc="2026-06-01T00:00:00Z")
    registry = _registry(first, second)
    assert resolve_btc_perpetual_fee_rebate_rule_version(
        registry, venue_id="venue-a", contract_id="BTC-USDT-PERP",
        at_utc="2026-05-31T23:59:59Z",
    ).version_id == "fee-v1"
    assert resolve_btc_perpetual_fee_rebate_rule_version(
        registry, venue_id="venue-a", contract_id="BTC-USDT-PERP",
        at_utc="2026-06-01T00:00:00Z",
    ).version_id == "fee-v2"


def test_lookup_fails_closed_on_missing_evidence():
    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_fee_rebate_rule_version(
            _registry(), venue_id="venue-a", contract_id="BTC-USDT-PERP",
            at_utc="2025-01-01T00:00:00Z",
        )


def test_registry_rejects_effective_interval_overlap():
    first = _version(effective_to_utc="2026-07-01T00:00:00Z")
    second = _version(name="fee-v2", effective_from_utc="2026-06-01T00:00:00Z")
    with pytest.raises(ValueError, match="intervals overlap"):
        _registry(first, second)


def test_registry_rejects_evidence_or_contract_state_after_as_of():
    late_artifact = replace(_artifact(), registered_at_utc="2026-07-22T00:00:00Z")
    with pytest.raises(ValueError, match="evidence after as_of"):
        _registry(artifact=late_artifact)
    late_contract = replace(_contract_registry(), as_of_utc="2026-07-22T00:00:00Z")
    with pytest.raises(ValueError, match="newer than fee"):
        _registry(contract_registry=late_contract)


def test_registry_is_deterministic_and_requires_stable_order():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(name="fee-v2", effective_from_utc="2026-06-01T00:00:00Z")
    assert _registry(first, second) == _registry(first, second)
    with pytest.raises(ValueError, match="deterministically ordered"):
        _registry(second, first)


def test_registry_authority_boundary_is_immutable():
    registry = _registry()
    for changes in (
        {"operator_review_required": False}, {"source_selected": True},
        {"account_tier_selection_allowed": True}, {"fee_calculation_allowed": True},
        {"rebate_calculation_allowed": True}, {"balance_calculation_allowed": True},
        {"position_calculation_allowed": True}, {"pnl_calculation_allowed": True},
        {"liquidation_calculation_allowed": True}, {"funding_calculation_allowed": True},
        {"execution_allowed": True}, {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot calculate, select, execute, or close"):
            replace(registry, **changes)
