from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0059_btc_perpetual_paper_stress_evaluation_input_domain_semantics_hardening_app_1 import (
    BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA,
    build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot,
)
from tests.fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_app_1.test_d1_d6 import (
    _observation,
    _observations,
    _registry,
)


def _registry_with(kind: str, value: Decimal):
    observations = tuple(
        _observation(item, value=value) if item == kind else _observation(item)
        for item in BTC_STRESS_SCENARIO_KINDS
    )
    return _registry(observations)


def test_complete_registry_produces_exact_domain_snapshot():
    registry = _registry()
    snapshot = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        registry
    )

    assert snapshot.input_registry_hash == registry.registry_hash
    assert snapshot.coverage_snapshot_hash == registry.coverage_snapshot.snapshot_hash
    assert snapshot.validated_scenario_kinds == BTC_STRESS_SCENARIO_KINDS
    assert snapshot.validated_observation_hashes == tuple(
        item.observation_hash for item in registry.observations
    )
    assert len(snapshot.domain_schema_hash) == len(snapshot.snapshot_hash) == 64


def test_domain_schema_matches_every_closed_kind_and_metric():
    assert tuple(item[0] for item in BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA) == (
        BTC_STRESS_SCENARIO_KINDS
    )
    assert len({item[1] for item in BTC_STRESS_EVALUATION_INPUT_DOMAIN_SCHEMA}) == 8


def test_negative_funding_rate_is_valid_registered_evidence():
    registry = _registry_with("FUNDING_SHOCK", Decimal("-0.0001"))
    snapshot = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        registry
    )

    assert registry.observations[1].value == Decimal("-0.0001")
    assert snapshot.validation_only is True


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-0.1")])
def test_collateral_index_requires_positive_value(value):
    with pytest.raises(ValueError, match="collateral index input must be positive"):
        _observation("COLLATERAL_DRAWDOWN", value=value)


@pytest.mark.parametrize("value", [Decimal("-0.1"), Decimal("1.1")])
def test_liquidation_distance_is_bounded(value):
    with pytest.raises(ValueError, match="between zero and one"):
        _observation("LIQUIDATION_DISTANCE", value=value)


@pytest.mark.parametrize("kind", ["LOSS_STREAK", "RESYNC", "VENUE_OUTAGE"])
@pytest.mark.parametrize("value", [Decimal("-1"), Decimal("1.5")])
def test_count_and_seconds_are_nonnegative_integers(kind, value):
    with pytest.raises(ValueError, match="nonnegative integers"):
        _observation(kind, value=value)


@pytest.mark.parametrize("kind", ["PRICE_GAP", "THIN_BOOK"])
@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1")])
def test_price_and_depth_require_positive_values(kind, value):
    with pytest.raises(ValueError, match="price and depth inputs must be positive"):
        _observation(kind, value=value)


def test_binary_float_funding_is_rejected():
    with pytest.raises(ValueError, match="exact decimal"):
        _observation("FUNDING_SHOCK", value=-0.0001)


def test_hardening_requires_typed_fcp_0058_registry():
    with pytest.raises(TypeError, match="typed FCP-0058"):
        build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot("unsafe")


def test_snapshot_hash_is_deterministic_and_registry_bound():
    first = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        _registry()
    )
    second = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        _registry()
    )
    changed = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        _registry_with("FUNDING_SHOCK", Decimal("-0.0001"))
    )

    assert first.snapshot_hash == second.snapshot_hash
    assert first.snapshot_hash != changed.snapshot_hash


def test_snapshot_rejects_authority_escalation():
    snapshot = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        _registry()
    )
    for update in (
        {"operator_review_required": False},
        {"validation_only": False},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot evaluate, calculate, execute, or close"):
            replace(snapshot, **update)


def test_snapshot_rejects_authority_identity_changes():
    snapshot = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        _registry()
    )
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(snapshot, **update)


def test_domain_snapshot_is_frozen():
    snapshot = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        _registry(_observations())
    )
    with pytest.raises(FrozenInstanceError):
        snapshot.hardening_id = "changed"
