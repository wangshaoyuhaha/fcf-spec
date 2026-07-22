from dataclasses import FrozenInstanceError, replace

import pytest

import apps.fcp_0068_btc_perpetual_paper_stress_evaluation_trigger_predicate_semantics_registry_app_1 as fcp_0068
from apps.fcp_0068_btc_perpetual_paper_stress_evaluation_trigger_predicate_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA,
    BTCPerpetualPaperStressTriggerPredicateSemantics,
    build_btc_perpetual_paper_stress_trigger_predicate_semantics_registry,
)
from tests.fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_app_1.test_d1_d6 import (
    _registry as _formula_registry,
)


def _registry():
    return build_btc_perpetual_paper_stress_trigger_predicate_semantics_registry(
        _formula_registry(),
        as_of_utc="2026-07-22T11:00:00Z",
    )


def test_exact_typed_fcp_0067_registry_builds_predicate_registry():
    registry = _registry()
    assert registry.formula_registry_hash == _formula_registry().registry_hash
    assert len(registry.semantics) == 8
    assert registry.predicate_semantics_only is True
    assert registry.predicate_registered is True
    assert registry.evaluation_allowed is False
    assert registry.calculation_allowed is False
    assert len(registry.registry_hash) == 64


def test_closed_predicate_schema_is_exact_and_ordered():
    observed = tuple(
        (
            item.scenario_kind,
            item.comparison_operator_id,
            item.left_role_id,
            item.right_role_id,
            item.parameter_transform_id,
            item.boundary_policy_id,
        )
        for item in _registry().semantics
    )
    assert observed == BTC_STRESS_EVALUATION_TRIGGER_PREDICATE_SCHEMA


def test_strict_and_inclusive_boundaries_are_explicit():
    by_kind = {item.scenario_kind: item for item in _registry().semantics}
    strict = {"COLLATERAL_DRAWDOWN", "FUNDING_SHOCK", "PRICE_GAP", "THIN_BOOK"}
    inclusive = {"LIQUIDATION_DISTANCE", "LOSS_STREAK", "RESYNC", "VENUE_OUTAGE"}
    assert {kind for kind, item in by_kind.items() if item.boundary_policy_id == "STRICT_BOUNDARY"} == strict
    assert {kind for kind, item in by_kind.items() if item.boundary_policy_id == "INCLUSIVE_BOUNDARY"} == inclusive


def test_predicate_roles_are_symbolic_and_fixed():
    for item in _registry().semantics:
        assert item.left_role_id == "measure"
        assert item.right_role_id == "parameter"


def test_requires_typed_fcp_0067_registry():
    with pytest.raises(TypeError, match="FCP-0067"):
        build_btc_perpetual_paper_stress_trigger_predicate_semantics_registry(
            "unsafe",
            as_of_utc="2026-07-22T11:00:00Z",
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("comparison_operator_id", "MEASURE_LESS_THAN_PARAMETER"),
        ("left_role_id", "parameter"),
        ("right_role_id", "measure"),
        ("parameter_transform_id", "ABSOLUTE_PARAMETER_MAGNITUDE"),
        ("boundary_policy_id", "INCLUSIVE_BOUNDARY"),
    ),
)
def test_kind_predicate_substitution_fails_closed(field, value):
    item = _registry().semantics[0]
    with pytest.raises(ValueError, match="closed kind schema"):
        replace(item, **{field: value})


def test_unknown_kind_fails_closed():
    source = _registry().semantics[0]
    with pytest.raises(ValueError, match="scenario_kind"):
        BTCPerpetualPaperStressTriggerPredicateSemantics(
            scenario_kind="UNKNOWN",
            comparison_operator_id=source.comparison_operator_id,
            left_role_id=source.left_role_id,
            right_role_id=source.right_role_id,
            parameter_transform_id=source.parameter_transform_id,
            boundary_policy_id=source.boundary_policy_id,
        )


@pytest.mark.parametrize(
    "semantics",
    (
        lambda values: values[:-1],
        lambda values: values + (values[-1],),
        lambda values: (values[1], values[0]) + values[2:],
    ),
)
def test_missing_duplicate_or_reordered_kinds_fail_closed(semantics):
    registry = _registry()
    with pytest.raises(ValueError, match="closed schema exactly"):
        replace(registry, semantics=semantics(registry.semantics))


def test_predicate_schema_hash_substitution_fails_closed():
    with pytest.raises(ValueError, match="predicate_schema_hash"):
        replace(_registry(), predicate_schema_hash="f" * 64)


def test_registry_cannot_precede_formula_registry():
    with pytest.raises(ValueError, match="cannot precede"):
        build_btc_perpetual_paper_stress_trigger_predicate_semantics_registry(
            _formula_registry(),
            as_of_utc="2026-07-22T10:00:00Z",
        )


def test_registry_hash_is_deterministic_and_formula_bound():
    assert _registry().registry_hash == _registry().registry_hash
    changed = build_btc_perpetual_paper_stress_trigger_predicate_semantics_registry(
        _formula_registry(),
        as_of_utc="2026-07-22T11:00:00Z",
        registry_id="changed-predicate-registry",
    )
    assert changed.registry_hash != _registry().registry_hash


def test_registry_preserves_upstream_lineage():
    formula = _formula_registry()
    registry = _registry()
    assert registry.formula_schema_hash == formula.formula_schema_hash
    assert registry.direction_registry_hash == formula.direction_registry_hash
    assert registry.direction_schema_hash == formula.direction_schema_hash
    assert registry.complete_rule_bundle_hash == formula.complete_rule_bundle_hash


def test_registry_rejects_authority_escalation():
    registry = _registry()
    for update in (
        {"operator_review_required": False},
        {"predicate_semantics_only": False},
        {"direction_defined": False},
        {"formula_registered": False},
        {"predicate_registered": False},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot evaluate"):
            replace(registry, **update)


def test_registry_rejects_authority_identity_changes():
    registry = _registry()
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(registry, **update)


def test_registry_exposes_no_evaluator_or_calculator():
    assert not hasattr(fcp_0068, "evaluate")
    assert not hasattr(fcp_0068, "calculate")


def test_registry_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _registry().registry_id = "changed"
