from dataclasses import FrozenInstanceError, replace

import pytest

import apps.fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_app_1 as fcp_0067
from apps.fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA,
    BTCPerpetualPaperStressMeasureFormulaSemantics,
    build_btc_perpetual_paper_stress_measure_formula_semantics_registry,
)
from tests.fcp_0066_btc_perpetual_paper_stress_evaluation_direction_semantics_registry_app_1.test_d1_d6 import (
    _registry as _direction_registry,
)


def _registry():
    return build_btc_perpetual_paper_stress_measure_formula_semantics_registry(
        _direction_registry(),
        as_of_utc="2026-07-22T10:30:00Z",
    )


def test_exact_typed_fcp_0066_registry_builds_formula_registry():
    registry = _registry()
    assert registry.direction_registry_hash == _direction_registry().registry_hash
    assert len(registry.semantics) == 8
    assert registry.formula_semantics_only is True
    assert registry.formula_registered is True
    assert registry.evaluation_allowed is False
    assert registry.calculation_allowed is False
    assert len(registry.registry_hash) == 64


def test_closed_formula_schema_is_exact_and_ordered():
    observed = tuple(
        (
            item.scenario_kind,
            item.formula_family_id,
            item.operand_roles,
            item.parameter_id,
            item.parameter_unit_id,
            item.output_unit_id,
            item.parameter_transform_id,
            item.denominator_policy_id,
        )
        for item in _registry().semantics
    )
    assert observed == BTC_STRESS_EVALUATION_MEASURE_FORMULA_SCHEMA


def test_formula_schema_has_expected_denominator_and_transform_policies():
    by_kind = {item.scenario_kind: item for item in _registry().semantics}
    assert by_kind["COLLATERAL_DRAWDOWN"].denominator_policy_id == (
        "REJECT_NONPOSITIVE_BASELINE"
    )
    assert by_kind["PRICE_GAP"].denominator_policy_id == (
        "REJECT_NONPOSITIVE_BASELINE"
    )
    assert by_kind["THIN_BOOK"].denominator_policy_id == (
        "REJECT_NONPOSITIVE_BASELINE"
    )
    assert by_kind["FUNDING_SHOCK"].parameter_transform_id == (
        "ABSOLUTE_PARAMETER_MAGNITUDE"
    )


def test_requires_typed_fcp_0066_registry():
    with pytest.raises(TypeError, match="FCP-0066"):
        build_btc_perpetual_paper_stress_measure_formula_semantics_registry(
            "unsafe",
            as_of_utc="2026-07-22T10:30:00Z",
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("formula_family_id", "DIRECT_OBSERVATION"),
        ("operand_roles", ("current", "baseline")),
        ("parameter_id", "gap-rate"),
        ("parameter_unit_id", "seconds"),
        ("output_unit_id", "count"),
        ("parameter_transform_id", "ABSOLUTE_PARAMETER_MAGNITUDE"),
        ("denominator_policy_id", "NOT_APPLICABLE"),
    ),
)
def test_kind_formula_substitution_fails_closed(field, value):
    item = _registry().semantics[0]
    with pytest.raises(ValueError, match="closed kind schema"):
        replace(item, **{field: value})


def test_unknown_kind_fails_closed():
    source = _registry().semantics[0]
    with pytest.raises(ValueError, match="scenario_kind"):
        BTCPerpetualPaperStressMeasureFormulaSemantics(
            scenario_kind="UNKNOWN",
            formula_family_id=source.formula_family_id,
            operand_roles=source.operand_roles,
            parameter_id=source.parameter_id,
            parameter_unit_id=source.parameter_unit_id,
            output_unit_id=source.output_unit_id,
            parameter_transform_id=source.parameter_transform_id,
            denominator_policy_id=source.denominator_policy_id,
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


def test_formula_schema_hash_substitution_fails_closed():
    with pytest.raises(ValueError, match="formula_schema_hash"):
        replace(_registry(), formula_schema_hash="f" * 64)


def test_registry_cannot_precede_direction_registry():
    with pytest.raises(ValueError, match="cannot precede"):
        build_btc_perpetual_paper_stress_measure_formula_semantics_registry(
            _direction_registry(),
            as_of_utc="2026-07-22T09:00:00Z",
        )


def test_registry_hash_is_deterministic_and_direction_bound():
    assert _registry().registry_hash == _registry().registry_hash
    changed = build_btc_perpetual_paper_stress_measure_formula_semantics_registry(
        _direction_registry(),
        as_of_utc="2026-07-22T10:30:00Z",
        registry_id="changed-formula-registry",
    )
    assert changed.registry_hash != _registry().registry_hash


def test_registry_rejects_authority_escalation():
    registry = _registry()
    for update in (
        {"operator_review_required": False},
        {"formula_semantics_only": False},
        {"direction_defined": False},
        {"formula_registered": False},
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
    assert not hasattr(fcp_0067, "evaluate")
    assert not hasattr(fcp_0067, "calculate")


def test_registry_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _registry().registry_id = "changed"
