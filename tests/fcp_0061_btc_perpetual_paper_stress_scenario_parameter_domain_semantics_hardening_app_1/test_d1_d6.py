from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
    BTCStressScenarioParameter,
)
from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    build_btc_perpetual_paper_stress_coverage_snapshot,
)
from apps.fcp_0061_btc_perpetual_paper_stress_scenario_parameter_domain_semantics_hardening_app_1 import (
    BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA,
    build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot,
)
from tests.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1.test_d1_d6 import (
    _definition,
    _registry,
)


def _evidence(kind: str | None = None, value: Decimal | None = None):
    if kind is None:
        registry = _registry()
    else:
        schema = {
            row_kind: (parameter_id, unit_id)
            for row_kind, parameter_id, unit_id, _ in (
                BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA
            )
        }
        parameter_id, unit_id = schema[kind]
        definitions = tuple(
            _definition(
                item,
                parameters=(
                    BTCStressScenarioParameter(parameter_id, value, unit_id),
                ),
            )
            if item == kind
            else _definition(item)
            for item in BTC_STRESS_SCENARIO_KINDS
        )
        registry = _registry(definitions)
    coverage = build_btc_perpetual_paper_stress_coverage_snapshot(registry)
    return registry, coverage


def _snapshot():
    return build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
        *_evidence()
    )


def test_exact_registry_and_coverage_produce_immutable_domain_snapshot():
    registry, coverage = _evidence()
    snapshot = build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
        registry, coverage
    )

    assert snapshot.registry_hash == registry.registry_hash
    assert snapshot.coverage_snapshot_hash == coverage.snapshot_hash
    assert snapshot.validated_scenario_kinds == BTC_STRESS_SCENARIO_KINDS
    assert snapshot.validated_definition_hashes == coverage.definition_hashes
    assert snapshot.validation_only is True
    assert snapshot.direction_defined is False
    assert len(snapshot.parameter_domain_schema_hash) == len(snapshot.snapshot_hash) == 64


def test_domain_schema_matches_every_closed_kind_and_fcp_0057_parameter():
    assert tuple(row[0] for row in BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA) == (
        BTC_STRESS_SCENARIO_KINDS
    )
    assert len({row[3] for row in BTC_STRESS_SCENARIO_PARAMETER_DOMAIN_SCHEMA}) == 4


def test_signed_funding_shock_is_preserved():
    registry, coverage = _evidence("FUNDING_SHOCK", Decimal("-0.0001"))
    snapshot = build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
        registry, coverage
    )

    assert registry.definitions[1].parameters[0].value == Decimal("-0.0001")
    assert snapshot.domain_validated is True


@pytest.mark.parametrize("kind", ["COLLATERAL_DRAWDOWN", "PRICE_GAP"])
@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-0.1"), Decimal("1.1")])
def test_positive_bounded_ratios_fail_closed(kind, value):
    registry, coverage = _evidence(kind, value)
    with pytest.raises(ValueError, match="positive bounded"):
        build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
            registry, coverage
        )


@pytest.mark.parametrize("kind", ["LIQUIDATION_DISTANCE", "THIN_BOOK"])
@pytest.mark.parametrize("value", [Decimal("-0.1"), Decimal("1.1")])
def test_bounded_ratios_fail_closed(kind, value):
    registry, coverage = _evidence(kind, value)
    with pytest.raises(ValueError, match="bounded stress parameter"):
        build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
            registry, coverage
        )


@pytest.mark.parametrize("kind", ["LOSS_STREAK", "RESYNC", "VENUE_OUTAGE"])
@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1"), Decimal("1.5")])
def test_positive_integral_counts_and_seconds_fail_closed(kind, value):
    registry, coverage = _evidence(kind, value)
    with pytest.raises(ValueError, match="positive integral"):
        build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
            registry, coverage
        )


@pytest.mark.parametrize("index, message", [(0, "FCP-0056"), (1, "FCP-0057")])
def test_hardening_requires_typed_upstream_evidence(index, message):
    evidence = list(_evidence())
    evidence[index] = "unsafe"
    with pytest.raises(TypeError, match=message):
        build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(*evidence)


def test_registry_substitution_fails_closed():
    registry, coverage = _evidence()
    changed = replace(registry, registry_id="changed-registry")
    with pytest.raises(ValueError, match="registry lineage mismatch"):
        build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
            changed, coverage
        )


def test_cross_contract_coverage_fails_closed():
    registry, coverage = _evidence()
    changed = replace(coverage, contract_id="ETH-USDT-PERP")
    with pytest.raises(ValueError, match="venue or contract lineage mismatch"):
        build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
            registry, changed
        )


def test_snapshot_hash_is_deterministic_and_definition_bound():
    first = _snapshot()
    second = _snapshot()
    registry, coverage = _evidence("FUNDING_SHOCK", Decimal("-0.0001"))
    changed = build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(
        registry, coverage
    )

    assert first.snapshot_hash == second.snapshot_hash
    assert first.snapshot_hash != changed.snapshot_hash


def test_snapshot_rejects_authority_escalation():
    snapshot = _snapshot()
    for update in (
        {"operator_review_required": False},
        {"validation_only": False},
        {"domain_validated": False},
        {"direction_defined": True},
        {"source_selected": True},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot direct, evaluate, calculate"):
            replace(snapshot, **update)


def test_snapshot_rejects_authority_identity_changes():
    snapshot = _snapshot()
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(snapshot, **update)


def test_domain_snapshot_is_frozen():
    snapshot = _snapshot()
    with pytest.raises(FrozenInstanceError):
        snapshot.hardening_id = "changed"
