from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError, replace
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
)
from apps.fcp_0048_btc_perpetual_funding_method_schedule_evidence_registry_app_1 import (
    BTCPerpetualFundingMethodScheduleRegistry,
    BTCPerpetualFundingRuleVersion,
    RegisteredBTCFundingRuleArtifact,
)
from apps.fcp_0049_btc_perpetual_fee_rebate_schedule_evidence_registry_app_1 import (
    BTCFeeRebateTier,
    BTCPerpetualFeeRebateRuleVersion,
    BTCPerpetualFeeRebateScheduleRegistry,
    RegisteredBTCFeeRebateRuleArtifact,
)
from apps.fcp_0053_btc_perpetual_rule_bundle_point_in_time_coherence_gate_app_1 import (
    BTCPerpetualRuleBundleSnapshot,
    resolve_btc_perpetual_rule_bundle,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _rights():
    return LocalEventRights("synthetic-test", "local-paper-research", 30)


def _artifact(cls, artifact_id: str, observed_minute: int):
    content = f"{artifact_id}\n".encode("ascii")
    return cls(
        artifact_id=artifact_id,
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights=_rights(),
        observed_at_utc=f"2026-07-21T00:{observed_minute:02d}:00Z",
        registered_at_utc=f"2026-07-21T00:{observed_minute + 1:02d}:00Z",
    )


def _contract_version(
    name: str = "contract-v1",
    *,
    effective_from: str = "2026-01-01T00:00:00Z",
    effective_to: str | None = None,
    price_tick: str = "0.1",
):
    return BTCPerpetualContractVersion(
        entry_id=f"entry-{name}",
        version_id=name,
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
        price_tick=Decimal(price_tick),
        quantity_step=Decimal("0.001"),
        minimum_quantity=Decimal("0.001"),
        minimum_notional=Decimal("5"),
        effective_from_utc=effective_from,
        effective_to_utc=effective_to,
        lifecycle_state="ACTIVE",
    )


def _contract_registry(*entries):
    return BTCPerpetualContractLifecycleRegistry(
        registry_id="btc-contract-registry-v1",
        artifact=_artifact(
            RegisteredBTCContractRuleArtifact,
            "contract-rules",
            0,
        ),
        entries=tuple(entries or (_contract_version(),)),
        as_of_utc="2026-07-21T00:02:00Z",
    )


def _margin_registry(contract_registry, contract_entry_hash=None):
    contract_entry_hash = contract_entry_hash or contract_registry.entries[0].entry_hash
    version = BTCPerpetualMarginRuleVersion(
        entry_id="entry-margin-v1",
        version_id="margin-v1",
        artifact_id="margin-rules",
        contract_entry_hash=contract_entry_hash,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        margin_mode="ISOLATED",
        position_mode="ONE_WAY",
        tiers=(
            BTCMarginRiskTier(
                tier_id="tier-1",
                notional_floor=Decimal("0"),
                notional_cap=Decimal("100000"),
                initial_margin_rate=Decimal("0.10"),
                maintenance_margin_rate=Decimal("0.05"),
                maintenance_amount_deduction=Decimal("0"),
                risk_limit=Decimal("100000"),
            ),
        ),
        collateral_rules=(
            BTCCollateralHaircutRule(
                collateral_asset="USDT",
                valuation_asset="USD",
                haircut_rate=Decimal("0"),
            ),
        ),
        effective_from_utc="2026-01-01T00:00:00Z",
        effective_to_utc=None,
    )
    return BTCPerpetualMarginRiskTierRegistry(
        registry_id="btc-margin-registry-v1",
        artifact=_artifact(RegisteredBTCMarginRuleArtifact, "margin-rules", 3),
        contract_registry=contract_registry,
        versions=(version,),
        as_of_utc="2026-07-21T00:05:00Z",
    )


def _funding_registry(contract_registry, contract_entry_hash=None):
    contract_entry_hash = contract_entry_hash or contract_registry.entries[0].entry_hash
    version = BTCPerpetualFundingRuleVersion(
        entry_id="entry-funding-v1",
        version_id="funding-v1",
        artifact_id="funding-rules",
        contract_entry_hash=contract_entry_hash,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        funding_method="PREMIUM_INDEX_CLAMPED",
        funding_basis="PREMIUM_INDEX",
        funding_interval_seconds=28800,
        settlement_anchor_utc="2026-01-01T00:00:00Z",
        rate_floor=Decimal("-0.0075"),
        rate_cap=Decimal("0.0075"),
        interest_component_rate=Decimal("0.0001"),
        positive_rate_payer="LONG",
        effective_from_utc="2026-01-01T00:00:00Z",
        effective_to_utc=None,
    )
    return BTCPerpetualFundingMethodScheduleRegistry(
        registry_id="btc-funding-registry-v1",
        artifact=_artifact(RegisteredBTCFundingRuleArtifact, "funding-rules", 6),
        contract_registry=contract_registry,
        versions=(version,),
        as_of_utc="2026-07-21T00:08:00Z",
    )


def _fee_registry(contract_registry, contract_entry_hash=None):
    contract_entry_hash = contract_entry_hash or contract_registry.entries[0].entry_hash
    version = BTCPerpetualFeeRebateRuleVersion(
        entry_id="entry-fee-v1",
        version_id="fee-v1",
        artifact_id="fee-rules",
        contract_entry_hash=contract_entry_hash,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        measurement_asset="USDT",
        trailing_window_seconds=2592000,
        fee_assets=("USDT",),
        tiers=(
            BTCFeeRebateTier(
                tier_id="tier-1",
                trailing_volume_floor=Decimal("0"),
                trailing_volume_cap=Decimal("100000"),
                maker_rate=Decimal("-0.0001"),
                taker_rate=Decimal("0.0005"),
            ),
        ),
        effective_from_utc="2026-01-01T00:00:00Z",
        effective_to_utc=None,
    )
    return BTCPerpetualFeeRebateScheduleRegistry(
        registry_id="btc-fee-registry-v1",
        artifact=_artifact(RegisteredBTCFeeRebateRuleArtifact, "fee-rules", 9),
        contract_registry=contract_registry,
        versions=(version,),
        as_of_utc="2026-07-21T00:11:00Z",
    )


def _bundle(contract_registry=None, *, entry_hash=None):
    contract_registry = contract_registry or _contract_registry()
    return resolve_btc_perpetual_rule_bundle(
        contract_registry,
        _margin_registry(contract_registry, entry_hash),
        _funding_registry(contract_registry, entry_hash),
        _fee_registry(contract_registry, entry_hash),
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        margin_mode="isolated",
        position_mode="one_way",
        at_utc="2026-07-21T01:00:00Z",
    )


def test_bundle_resolves_exact_typed_point_in_time_lineage():
    bundle = _bundle()

    assert bundle.lifecycle_state == "ACTIVE"
    assert bundle.margin_mode == "ISOLATED"
    assert bundle.position_mode == "ONE_WAY"
    assert len(bundle.snapshot_hash) == 64
    assert bundle.operator_review_required is True
    assert bundle.evidence_authority == "REGISTERED_EVIDENCE"
    assert bundle.source_selected is False


def test_bundle_hash_is_deterministic_and_snapshot_is_immutable():
    first = _bundle()
    second = _bundle()

    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    with pytest.raises(FrozenInstanceError):
        first.venue_id = "venue-b"


def test_bundle_rejects_cross_registry_contract_lineage():
    primary = _contract_registry()
    alternate = _contract_registry(_contract_version(price_tick="0.01"))

    with pytest.raises(ValueError, match="one exact FCP-0046 registry"):
        resolve_btc_perpetual_rule_bundle(
            primary,
            _margin_registry(primary),
            _funding_registry(alternate),
            _fee_registry(primary),
            venue_id="venue-a",
            contract_id="BTC-USDT-PERP",
            margin_mode="ISOLATED",
            position_mode="ONE_WAY",
            at_utc="2026-07-21T01:00:00Z",
        )


def test_bundle_rejects_resolved_contract_entry_mismatch():
    first = _contract_version(effective_to="2026-06-01T00:00:00Z")
    second = _contract_version(
        "contract-v2",
        effective_from="2026-06-01T00:00:00Z",
        price_tick="0.01",
    )
    registry = _contract_registry(first, second)

    with pytest.raises(ValueError, match="one exact contract entry"):
        _bundle(registry, entry_hash=first.entry_hash)


def test_bundle_fails_closed_when_any_effective_rule_is_missing():
    registry = _contract_registry()
    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_rule_bundle(
            registry,
            _margin_registry(registry),
            _funding_registry(registry),
            _fee_registry(registry),
            venue_id="venue-a",
            contract_id="BTC-USDT-PERP",
            margin_mode="CROSS",
            position_mode="ONE_WAY",
            at_utc="2026-07-21T01:00:00Z",
        )


def test_snapshot_rejects_authority_escalation():
    snapshot = _bundle()
    for update in (
        {"operator_review_required": False},
        {"source_selected": True},
        {"account_state_allowed": True},
        {"calculation_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot select, calculate, execute, or close"):
            replace(snapshot, **update)


def test_snapshot_contains_hash_lineage_not_account_or_calculated_values():
    fields = set(BTCPerpetualRuleBundleSnapshot.__dataclass_fields__)

    assert {
        "contract_registry_hash",
        "margin_registry_hash",
        "funding_registry_hash",
        "fee_registry_hash",
        "contract_entry_hash",
        "margin_rule_entry_hash",
        "funding_rule_entry_hash",
        "fee_rule_entry_hash",
    } <= fields
    forbidden = {
        "account_id",
        "balance",
        "position",
        "notional",
        "leverage",
        "margin_amount",
        "liquidation_price",
        "funding_payment",
        "fee_amount",
        "pnl",
        "order_id",
    }
    assert fields.isdisjoint(forbidden)
