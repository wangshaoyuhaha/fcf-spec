from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0055_btc_perpetual_complete_rule_bundle_coherence_hardening_app_1 import (
    BTCPerpetualCompleteRuleBundleSnapshot,
    resolve_btc_perpetual_complete_rule_bundle,
)
from tests.fcp_0053_btc_perpetual_rule_bundle_point_in_time_coherence_gate_app_1.test_d1_d6 import (
    _bundle,
    _contract_registry,
    _contract_version,
)
from tests.fcp_0054_btc_perpetual_mark_index_liquidation_mechanics_evidence_registry_app_1.test_d1_d6 import (
    _registry as _liquidation_registry,
    _version as _liquidation_version,
)


def _coherent_inputs():
    contract_registry = _contract_registry()
    base_bundle = _bundle(contract_registry)
    liquidation_registry = _liquidation_registry(
        _liquidation_version(
            contract_entry_hash=contract_registry.entries[0].entry_hash,
        ),
        contract_registry=contract_registry,
    )
    return base_bundle, liquidation_registry


def _complete_bundle():
    return resolve_btc_perpetual_complete_rule_bundle(*_coherent_inputs())


def test_complete_bundle_preserves_exact_five_registry_lineage():
    base_bundle, liquidation_registry = _coherent_inputs()
    complete = resolve_btc_perpetual_complete_rule_bundle(
        base_bundle,
        liquidation_registry,
    )

    assert complete.base_rule_bundle_hash == base_bundle.snapshot_hash
    assert complete.contract_registry_hash == base_bundle.contract_registry_hash
    assert complete.liquidation_registry_hash == liquidation_registry.registry_hash
    assert complete.contract_entry_hash == base_bundle.contract_entry_hash
    assert complete.operator_review_required is True
    assert complete.evidence_authority == "REGISTERED_EVIDENCE"
    assert len(complete.snapshot_hash) == 64


def test_complete_bundle_is_deterministic_and_immutable():
    first = _complete_bundle()
    second = _complete_bundle()

    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    with pytest.raises(FrozenInstanceError):
        first.venue_id = "venue-b"


def test_complete_bundle_requires_typed_inputs():
    base_bundle, liquidation_registry = _coherent_inputs()
    with pytest.raises(TypeError, match="typed FCP-0053"):
        resolve_btc_perpetual_complete_rule_bundle(object(), liquidation_registry)
    with pytest.raises(TypeError, match="typed FCP-0054"):
        resolve_btc_perpetual_complete_rule_bundle(base_bundle, object())


def test_complete_bundle_rejects_cross_registry_lineage():
    base_bundle, _ = _coherent_inputs()
    alternate = _contract_registry(_contract_version(price_tick="0.01"))
    liquidation_registry = _liquidation_registry(
        _liquidation_version(
            contract_entry_hash=alternate.entries[0].entry_hash,
        ),
        contract_registry=alternate,
    )

    with pytest.raises(ValueError, match="one exact FCP-0046 registry"):
        resolve_btc_perpetual_complete_rule_bundle(
            base_bundle,
            liquidation_registry,
        )


def test_complete_bundle_rejects_resolved_contract_entry_mismatch():
    first = _contract_version(effective_to="2026-06-01T00:00:00Z")
    second = _contract_version(
        "contract-v2",
        effective_from="2026-06-01T00:00:00Z",
        price_tick="0.01",
    )
    contract_registry = _contract_registry(first, second)
    base_bundle = _bundle(contract_registry, entry_hash=second.entry_hash)
    liquidation_registry = _liquidation_registry(
        _liquidation_version(contract_entry_hash=first.entry_hash),
        contract_registry=contract_registry,
    )

    with pytest.raises(ValueError, match="one exact contract entry"):
        resolve_btc_perpetual_complete_rule_bundle(
            base_bundle,
            liquidation_registry,
        )


def test_complete_bundle_fails_closed_when_liquidation_rule_is_missing():
    contract_registry = _contract_registry()
    base_bundle = _bundle(contract_registry)
    liquidation_registry = _liquidation_registry(
        _liquidation_version(
            contract_entry_hash=contract_registry.entries[0].entry_hash,
            effective_from_utc="2027-01-01T00:00:00Z",
        ),
        contract_registry=contract_registry,
    )

    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_complete_rule_bundle(
            base_bundle,
            liquidation_registry,
        )


def test_complete_bundle_rejects_registry_newer_than_lookup_instant():
    contract_registry = _contract_registry()
    base_bundle = _bundle(contract_registry)
    liquidation_registry = _liquidation_registry(
        _liquidation_version(
            contract_entry_hash=contract_registry.entries[0].entry_hash,
        ),
        contract_registry=contract_registry,
        as_of_utc="2026-07-21T02:00:00Z",
    )

    with pytest.raises(ValueError, match="newer than bundle instant"):
        resolve_btc_perpetual_complete_rule_bundle(
            base_bundle,
            liquidation_registry,
        )


def test_complete_bundle_rejects_authority_escalation():
    complete = _complete_bundle()
    for update in (
        {"operator_review_required": False},
        {"source_selected": True},
        {"account_state_allowed": True},
        {"calculation_allowed": True},
        {"insurance_fund_mutation_allowed": True},
        {"adl_action_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(
            ValueError,
            match="cannot calculate, mutate, select, execute, or close",
        ):
            replace(complete, **update)


def test_complete_snapshot_contains_hashes_not_account_or_calculated_values():
    fields = set(BTCPerpetualCompleteRuleBundleSnapshot.__dataclass_fields__)

    assert {
        "base_rule_bundle_hash",
        "contract_registry_hash",
        "margin_registry_hash",
        "funding_registry_hash",
        "fee_registry_hash",
        "liquidation_registry_hash",
        "contract_entry_hash",
        "liquidation_rule_entry_hash",
    } <= fields
    assert fields.isdisjoint(
        {
            "account_id",
            "balance",
            "position",
            "notional",
            "leverage",
            "margin_amount",
            "mark_price",
            "liquidation_price",
            "funding_payment",
            "fee_amount",
            "pnl",
            "order_id",
        }
    )
