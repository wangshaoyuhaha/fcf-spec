from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal

import pytest

from apps.fcp_0046_btc_perpetual_venue_contract_lifecycle_registry_app_1 import (
    BTCPerpetualContractLifecycleRegistry,
    BTCPerpetualContractVersion,
    RegisteredBTCContractRuleArtifact,
    resolve_btc_perpetual_contract_version,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _artifact(name="contract-rules"):
    content = (name + "\n").encode("ascii")
    return RegisteredBTCContractRuleArtifact(
        artifact_id=name,
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights=LocalEventRights("synthetic-test", "local-paper-research", 30),
        observed_at_utc="2026-07-21T00:00:00Z",
        registered_at_utc="2026-07-21T00:01:00Z",
    )


def _version(name="v1", **updates):
    values = {
        "entry_id": f"entry-{name}",
        "version_id": name,
        "artifact_id": "contract-rules",
        "venue_id": "venue-a",
        "contract_id": "BTC-USDT-PERP",
        "venue_symbol": "BTCUSDT",
        "settlement_type": "LINEAR",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "settlement_asset": "USDT",
        "collateral_assets": ("USDT",),
        "contract_multiplier": Decimal("1"),
        "price_tick": Decimal("0.1"),
        "quantity_step": Decimal("0.001"),
        "minimum_quantity": Decimal("0.001"),
        "minimum_notional": Decimal("5"),
        "effective_from_utc": "2026-01-01T00:00:00Z",
        "effective_to_utc": None,
        "lifecycle_state": "ACTIVE",
    }
    values.update(updates)
    return BTCPerpetualContractVersion(**values)


def _registry(*entries):
    rows = entries or (_version(),)
    return BTCPerpetualContractLifecycleRegistry(
        registry_id="btc-contract-registry-v1",
        artifact=_artifact(),
        entries=tuple(rows),
        as_of_utc="2026-07-21T00:02:00Z",
    )


def test_linear_contract_preserves_exact_versioned_semantics():
    registry = _registry()
    item = registry.entries[0]

    assert item.settlement_type == "LINEAR"
    assert item.settlement_asset == item.quote_asset == "USDT"
    assert item.contract_multiplier == Decimal("1")
    assert item.price_tick == Decimal("0.1")
    assert item.quantity_step == Decimal("0.001")
    assert len(item.entry_hash) == len(registry.registry_hash) == 64


def test_inverse_contract_must_settle_in_base_asset():
    inverse = _version(
        settlement_type="INVERSE",
        quote_asset="USD",
        settlement_asset="BTC",
        collateral_assets=("BTC",),
        contract_multiplier=Decimal("100"),
    )
    assert inverse.settlement_asset == "BTC"

    with pytest.raises(ValueError, match="inverse contracts"):
        replace(inverse, settlement_asset="USD", collateral_assets=("USD",))


def test_linear_contract_rejects_non_quote_settlement():
    with pytest.raises(ValueError, match="linear contracts"):
        _version(settlement_asset="BTC", collateral_assets=("BTC",))


def test_precision_and_minimums_reject_float_or_nonpositive_values():
    with pytest.raises(ValueError, match="exact decimal"):
        _version(price_tick=0.1)
    with pytest.raises(ValueError, match="finite and positive"):
        _version(minimum_notional=Decimal("0"))


def test_point_in_time_lookup_uses_half_open_effective_intervals():
    first = _version(
        name="v1",
        effective_to_utc="2026-06-01T00:00:00Z",
    )
    second = _version(
        name="v2",
        entry_id="entry-v2",
        effective_from_utc="2026-06-01T00:00:00Z",
        price_tick=Decimal("0.01"),
    )
    registry = _registry(first, second)

    assert resolve_btc_perpetual_contract_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        at_utc="2026-05-31T23:59:59Z",
    ).version_id == "v1"
    assert resolve_btc_perpetual_contract_version(
        registry,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        at_utc="2026-06-01T00:00:00Z",
    ).version_id == "v2"


def test_point_in_time_lookup_fails_closed_on_gap():
    item = _version(effective_from_utc="2026-06-01T00:00:00Z")

    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_contract_version(
            _registry(item),
            venue_id="venue-a",
            contract_id="BTC-USDT-PERP",
            at_utc="2026-05-01T00:00:00Z",
        )


def test_registry_rejects_effective_interval_overlap():
    first = _version(effective_to_utc="2026-07-01T00:00:00Z")
    second = _version(
        name="v2",
        entry_id="entry-v2",
        effective_from_utc="2026-06-01T00:00:00Z",
    )

    with pytest.raises(ValueError, match="intervals overlap"):
        _registry(first, second)


def test_migration_requires_distinct_target_and_is_hashed():
    migrated = _version(
        lifecycle_state="MIGRATED",
        migration_contract_id="BTC-USDC-PERP",
    )
    assert migrated.migration_contract_id == "BTC-USDC-PERP"

    with pytest.raises(ValueError, match="distinct target"):
        _version(lifecycle_state="MIGRATED")
    with pytest.raises(ValueError, match="only migrated"):
        _version(migration_contract_id="BTC-USDC-PERP")


def test_registry_rejects_artifact_lineage_mismatch():
    with pytest.raises(ValueError, match="artifact lineage mismatch"):
        _registry(_version(artifact_id="foreign-rules"))


def test_registry_rejects_evidence_registered_after_as_of():
    artifact = replace(_artifact(), registered_at_utc="2026-07-22T00:00:00Z")

    with pytest.raises(ValueError, match="after as_of"):
        BTCPerpetualContractLifecycleRegistry(
            "registry",
            artifact,
            (_version(),),
            "2026-07-21T00:02:00Z",
        )


def test_registry_is_deterministic_and_requires_stable_order():
    first = _version(effective_to_utc="2026-06-01T00:00:00Z")
    second = _version(
        name="v2",
        entry_id="entry-v2",
        effective_from_utc="2026-06-01T00:00:00Z",
    )
    assert _registry(first, second) == _registry(first, second)

    with pytest.raises(ValueError, match="deterministically ordered"):
        _registry(second, first)


def test_registry_authority_boundary_is_immutable():
    registry = _registry()

    for changes in (
        {"operator_review_required": False},
        {"source_selected": True},
        {"margin_calculation_allowed": True},
        {"liquidation_calculation_allowed": True},
        {"pnl_calculation_allowed": True},
        {"funding_calculation_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot calculate, select, execute, or close"):
            replace(registry, **changes)
