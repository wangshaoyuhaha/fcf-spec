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
from apps.fcp_0048_btc_perpetual_funding_method_schedule_evidence_registry_app_1 import (
    BTCPerpetualFundingMethodScheduleRegistry,
    BTCPerpetualFundingRuleVersion,
    RegisteredBTCFundingRuleArtifact,
    resolve_btc_perpetual_funding_rule_version,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _rights():
    return LocalEventRights("synthetic-test", "local-paper-research", 30)


def _contract_artifact():
    content = b"contract-rules\n"
    return RegisteredBTCContractRuleArtifact(
        "contract-rules",
        hashlib.sha256(content).hexdigest(),
        len(content),
        _rights(),
        "2026-07-21T00:00:00Z",
        "2026-07-21T00:01:00Z",
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
        "btc-contract-registry-v1",
        _contract_artifact(),
        (_contract_version(),),
        "2026-07-21T00:02:00Z",
    )


def _artifact():
    content = b"funding-rules\n"
    return RegisteredBTCFundingRuleArtifact(
        "funding-rules",
        hashlib.sha256(content).hexdigest(),
        len(content),
        _rights(),
        "2026-07-21T00:03:00Z",
        "2026-07-21T00:04:00Z",
    )


def _version(name="funding-v1", **updates):
    values = {
        "entry_id": f"entry-{name}",
        "version_id": name,
        "artifact_id": "funding-rules",
        "contract_entry_hash": _contract_version().entry_hash,
        "venue_id": "venue-a",
        "contract_id": "BTC-USDT-PERP",
        "funding_method": "PREMIUM_INDEX_CLAMPED",
        "funding_basis": "PREMIUM_INDEX",
        "funding_interval_seconds": 28800,
        "settlement_anchor_utc": "2026-01-01T00:00:00Z",
        "rate_floor": Decimal("-0.0075"),
        "rate_cap": Decimal("0.0075"),
        "interest_component_rate": Decimal("0.0001"),
        "positive_rate_payer": "LONG",
        "effective_from_utc": "2026-01-01T00:00:00Z",
        "effective_to_utc": None,
    }
    values.update(updates)
    return BTCPerpetualFundingRuleVersion(**values)


def _registry(*versions, artifact=None, contract_registry=None):
    return BTCPerpetualFundingMethodScheduleRegistry(
        registry_id="btc-funding-registry-v1",
        artifact=artifact or _artifact(),
        contract_registry=contract_registry or _contract_registry(),
        versions=tuple(versions or (_version(),)),
        as_of_utc="2026-07-21T00:05:00Z",
    )


def test_funding_rule_preserves_exact_method_schedule_and_direction():
    registry = _registry()
    item = registry.versions[0]

    assert item.funding_method == "PREMIUM_INDEX_CLAMPED"
    assert item.funding_basis == "PREMIUM_INDEX"
    assert item.funding_interval_seconds == 28800
    assert item.rate_floor == Decimal("-0.0075")
    assert item.positive_rate_payer == "LONG"
    assert len(item.entry_hash) == len(registry.registry_hash) == 64


def test_signed_rates_reject_float_and_nonfinite_values():
    with pytest.raises(ValueError, match="exact decimal"):
        _version(rate_cap=0.01)
    with pytest.raises(ValueError, match="finite"):
        _version(rate_cap=Decimal("Infinity"))


def test_rate_floor_cannot_exceed_cap():
    with pytest.raises(ValueError, match="floor cannot exceed cap"):
        _version(rate_floor=Decimal("0.01"), rate_cap=Decimal("0"))


def test_funding_interval_must_be_positive_integer():
    with pytest.raises(ValueError, match="positive integer"):
        _version(funding_interval_seconds=0)
    with pytest.raises(ValueError, match="positive integer"):
        _version(funding_interval_seconds=True)


def test_funding_method_and_basis_are_closed_and_consistent():
    direct = _version(funding_method="DIRECT_VENUE_RATE", funding_basis="DIRECT_RATE")
    assert direct.funding_basis == "DIRECT_RATE"
    with pytest.raises(ValueError, match="direct-rate basis"):
        _version(funding_method="DIRECT_VENUE_RATE")
    with pytest.raises(ValueError, match="derived basis"):
        _version(funding_basis="DIRECT_RATE")


def test_positive_rate_payer_is_closed():
    assert _version(positive_rate_payer="short").positive_rate_payer == "SHORT"
    with pytest.raises(ValueError, match="payer is not registered"):
        _version(positive_rate_payer="BOTH")


def test_registry_binds_exact_fcp_0046_contract_entry():
    assert _registry().contract_registry.registry_hash
    with pytest.raises(ValueError, match="FCP-0046 contract lineage"):
        _registry(_version(contract_entry_hash="0" * 64))


def test_registry_rejects_artifact_lineage_mismatch():
    with pytest.raises(ValueError, match="artifact lineage mismatch"):
        _registry(_version(artifact_id="other-funding-rules"))


def test_point_in_time_lookup_uses_half_open_effective_intervals():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(
        name="funding-v2",
        effective_from_utc="2026-06-01T00:00:00Z",
        funding_interval_seconds=14400,
    )
    registry = _registry(first, second)

    assert resolve_btc_perpetual_funding_rule_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        at_utc="2026-05-31T23:59:59Z",
    ).version_id == "funding-v1"
    assert resolve_btc_perpetual_funding_rule_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        at_utc="2026-06-01T00:00:00Z",
    ).version_id == "funding-v2"


def test_lookup_fails_closed_on_missing_evidence():
    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_funding_rule_version(
            _registry(),
            venue_id="venue-a",
            contract_id="BTC-USDT-PERP",
            at_utc="2025-01-01T00:00:00Z",
        )


def test_registry_rejects_effective_interval_overlap():
    first = _version(effective_to_utc="2026-07-01T00:00:00Z")
    second = _version(name="funding-v2", effective_from_utc="2026-06-01T00:00:00Z")
    with pytest.raises(ValueError, match="intervals overlap"):
        _registry(first, second)


def test_registry_rejects_evidence_or_contract_state_after_as_of():
    late_artifact = replace(_artifact(), registered_at_utc="2026-07-22T00:00:00Z")
    with pytest.raises(ValueError, match="evidence after as_of"):
        _registry(artifact=late_artifact)
    late_contract = replace(_contract_registry(), as_of_utc="2026-07-22T00:00:00Z")
    with pytest.raises(ValueError, match="newer than funding"):
        _registry(contract_registry=late_contract)


def test_registry_is_deterministic_and_requires_stable_order():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(name="funding-v2", effective_from_utc="2026-06-01T00:00:00Z")
    assert _registry(first, second) == _registry(first, second)
    with pytest.raises(ValueError, match="deterministically ordered"):
        _registry(second, first)


def test_registry_authority_boundary_is_immutable():
    registry = _registry()
    for changes in (
        {"operator_review_required": False},
        {"source_selected": True},
        {"funding_rate_calculation_allowed": True},
        {"funding_payment_calculation_allowed": True},
        {"balance_calculation_allowed": True},
        {"position_calculation_allowed": True},
        {"pnl_calculation_allowed": True},
        {"liquidation_calculation_allowed": True},
        {"fee_calculation_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot calculate, select, execute, or close"):
            replace(registry, **changes)
