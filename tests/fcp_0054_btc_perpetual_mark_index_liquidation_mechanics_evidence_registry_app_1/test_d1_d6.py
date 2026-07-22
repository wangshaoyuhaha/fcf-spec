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
from apps.fcp_0054_btc_perpetual_mark_index_liquidation_mechanics_evidence_registry_app_1 import (
    BTCPartialLiquidationTier,
    BTCPerpetualLiquidationMechanicsRegistry,
    BTCPerpetualLiquidationMechanicsVersion,
    RegisteredBTCLiquidationMechanicsArtifact,
    resolve_btc_perpetual_liquidation_mechanics_version,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _rights():
    return LocalEventRights("synthetic-test", "local-paper-research", 30)


def _artifact(cls, artifact_id: str, minute: int):
    content = f"{artifact_id}\n".encode("ascii")
    return cls(
        artifact_id,
        hashlib.sha256(content).hexdigest(),
        len(content),
        _rights(),
        f"2026-07-21T00:{minute:02d}:00Z",
        f"2026-07-21T00:{minute + 1:02d}:00Z",
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
        artifact=_artifact(RegisteredBTCContractRuleArtifact, "contract-rules", 0),
        entries=(_contract_version(),),
        as_of_utc="2026-07-21T00:02:00Z",
    )


def _tier(name="tier-1", floor="0", cap="100000", **updates):
    values = {
        "tier_id": name,
        "notional_floor": Decimal(floor),
        "notional_cap": Decimal(cap),
        "position_reduction_rate": Decimal("0.25"),
        "liquidation_fee_rate": Decimal("0.005"),
    }
    values.update(updates)
    return BTCPartialLiquidationTier(**values)


def _version(name="liquidation-v1", **updates):
    values = {
        "entry_id": f"entry-{name}",
        "version_id": name,
        "artifact_id": "liquidation-rules",
        "contract_entry_hash": _contract_version().entry_hash,
        "venue_id": "venue-a",
        "contract_id": "BTC-USDT-PERP",
        "mark_price_method": "INDEX_PREMIUM_CLAMPED",
        "index_price_method": "WEIGHTED_COMPONENT_SET",
        "index_component_set_hash": "1" * 64,
        "bankruptcy_price_method_id": "bankruptcy-linear-v1",
        "liquidation_price_method_id": "liquidation-maintenance-v1",
        "liquidation_mode": "PARTIAL_LADDER",
        "partial_liquidation_tiers": (_tier(),),
        "liquidation_fee_asset": "USDT",
        "insurance_fund_policy_id": "insurance-deficit-v1",
        "adl_ranking_method": "PROFIT_LEVERAGE",
        "cascade_state_policy_id": "cascade-state-v1",
        "effective_from_utc": "2026-01-01T00:00:00Z",
        "effective_to_utc": None,
    }
    values.update(updates)
    return BTCPerpetualLiquidationMechanicsVersion(**values)


def _registry(*versions, contract_registry=None, artifact=None, **updates):
    values = {
        "registry_id": "btc-liquidation-registry-v1",
        "artifact": artifact
        or _artifact(
            RegisteredBTCLiquidationMechanicsArtifact,
            "liquidation-rules",
            3,
        ),
        "contract_registry": contract_registry or _contract_registry(),
        "versions": tuple(versions or (_version(),)),
        "as_of_utc": "2026-07-21T00:05:00Z",
    }
    values.update(updates)
    return BTCPerpetualLiquidationMechanicsRegistry(**values)


def test_registry_preserves_exact_methods_tiers_and_policy_lineage():
    registry = _registry()
    version = registry.versions[0]

    assert version.mark_price_method == "INDEX_PREMIUM_CLAMPED"
    assert version.index_price_method == "WEIGHTED_COMPONENT_SET"
    assert version.partial_liquidation_tiers[0].position_reduction_rate == Decimal(
        "0.25"
    )
    assert version.adl_ranking_method == "PROFIT_LEVERAGE"
    assert len(version.entry_hash) == len(registry.registry_hash) == 64


def test_tier_rejects_float_nonfinite_and_invalid_unit_rates():
    with pytest.raises(ValueError, match="exact decimal"):
        _tier(position_reduction_rate=0.25)
    with pytest.raises(ValueError, match="registered range"):
        _tier(liquidation_fee_rate=Decimal("Infinity"))
    with pytest.raises(ValueError, match="unit rate"):
        _tier(position_reduction_rate=Decimal("0"))
    with pytest.raises(ValueError, match="unit rate"):
        _tier(liquidation_fee_rate=Decimal("1.1"))


def test_tier_interval_must_be_strictly_increasing():
    with pytest.raises(ValueError, match="strictly increasing"):
        _tier(floor="100", cap="100")


def test_partial_tiers_must_begin_at_zero_and_be_contiguous():
    with pytest.raises(ValueError, match="begin at zero"):
        _version(partial_liquidation_tiers=(_tier(floor="1"),))
    first = _tier(cap="100")
    second = _tier(name="tier-2", floor="101", cap="200")
    with pytest.raises(ValueError, match="contiguous"):
        _version(partial_liquidation_tiers=(first, second))


def test_liquidation_mode_controls_partial_tier_presence():
    full = _version(
        liquidation_mode="FULL",
        partial_liquidation_tiers=(),
    )
    assert full.liquidation_mode == "FULL"
    with pytest.raises(ValueError, match="requires tiers"):
        _version(partial_liquidation_tiers=())
    with pytest.raises(ValueError, match="cannot declare"):
        _version(liquidation_mode="FULL")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("mark_price_method", "UNKNOWN", "mark_price_method"),
        ("index_price_method", "UNKNOWN", "index_price_method"),
        ("liquidation_mode", "UNKNOWN", "liquidation_mode"),
        ("adl_ranking_method", "UNKNOWN", "adl_ranking_method"),
    ),
)
def test_closed_method_vocabularies_reject_unknown_values(field, value, message):
    with pytest.raises(ValueError, match=message):
        _version(**{field: value})


def test_index_component_lineage_requires_exact_digest():
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        _version(index_component_set_hash="not-a-digest")


def test_registry_binds_exact_fcp_0046_contract_entry():
    assert _registry().contract_registry.registry_hash
    with pytest.raises(ValueError, match="FCP-0046 contract lineage"):
        _registry(_version(contract_entry_hash="0" * 64))


def test_registry_rejects_artifact_lineage_mismatch():
    with pytest.raises(ValueError, match="artifact lineage mismatch"):
        _registry(_version(artifact_id="other-liquidation-rules"))


def test_point_in_time_lookup_uses_half_open_effective_intervals():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(
        name="liquidation-v2",
        effective_from_utc="2026-06-01T00:00:00Z",
        mark_price_method="MEDIAN_REFERENCE_CLAMPED",
    )
    registry = _registry(first, second)

    assert resolve_btc_perpetual_liquidation_mechanics_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        at_utc="2026-05-31T23:59:59Z",
    ).version_id == "liquidation-v1"
    assert resolve_btc_perpetual_liquidation_mechanics_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        at_utc="2026-06-01T00:00:00Z",
    ).version_id == "liquidation-v2"


def test_lookup_fails_closed_on_missing_evidence():
    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_liquidation_mechanics_version(
            _registry(),
            venue_id="venue-a",
            contract_id="BTC-USDT-PERP",
            at_utc="2025-01-01T00:00:00Z",
        )


def test_registry_rejects_effective_interval_overlap():
    first = _version(effective_to_utc="2026-07-01T00:00:00Z")
    second = _version(
        name="liquidation-v2",
        effective_from_utc="2026-06-01T00:00:00Z",
    )
    with pytest.raises(ValueError, match="effective intervals overlap"):
        _registry(first, second)


def test_registry_rejects_future_artifact_and_contract_lineage():
    future_artifact = replace(
        _artifact(
            RegisteredBTCLiquidationMechanicsArtifact,
            "liquidation-rules",
            3,
        ),
        observed_at_utc="2026-07-21T00:06:00Z",
        registered_at_utc="2026-07-21T00:07:00Z",
    )
    with pytest.raises(ValueError, match="evidence after as_of"):
        _registry(artifact=future_artifact)
    early_artifact = replace(
        _artifact(
            RegisteredBTCLiquidationMechanicsArtifact,
            "liquidation-rules",
            3,
        ),
        observed_at_utc="2026-07-21T00:00:00Z",
        registered_at_utc="2026-07-21T00:00:30Z",
    )
    with pytest.raises(ValueError, match="contract registry cannot be newer"):
        _registry(
            artifact=early_artifact,
            as_of_utc="2026-07-21T00:01:00Z",
        )


def test_registry_rejects_authority_escalation():
    for update in (
        {"operator_review_required": False},
        {"source_selected": True},
        {"price_calculation_allowed": True},
        {"margin_calculation_allowed": True},
        {"liquidation_calculation_allowed": True},
        {"balance_calculation_allowed": True},
        {"position_calculation_allowed": True},
        {"pnl_calculation_allowed": True},
        {"insurance_fund_mutation_allowed": True},
        {"adl_action_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(
            ValueError,
            match="cannot calculate, mutate, select, execute, or close",
        ):
            _registry(**update)


def test_registry_hash_is_deterministic_and_changes_with_rules():
    first = _registry()
    second = _registry()
    changed = _registry(_version(index_component_set_hash="2" * 64))

    assert first.registry_hash == second.registry_hash
    assert first.registry_hash != changed.registry_hash
