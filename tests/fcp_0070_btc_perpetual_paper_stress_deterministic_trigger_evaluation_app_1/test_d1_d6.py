from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

import apps.fcp_0070_btc_perpetual_paper_stress_deterministic_trigger_evaluation_app_1 as fcp_0070
from apps.fcp_0070_btc_perpetual_paper_stress_deterministic_trigger_evaluation_app_1 import (
    evaluate_btc_perpetual_paper_stress_triggers,
)
from apps.fcp_0070_btc_perpetual_paper_stress_deterministic_trigger_evaluation_app_1.evaluator import (
    _compare,
    _measure,
    _transform,
)
from tests.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1.test_d1_d6 import (
    _registry as _scenario_registry,
)
from tests.fcp_0064_btc_perpetual_paper_stress_evaluation_operand_evidence_registry_app_1.test_d1_d6 import (
    _registry as _operand_registry,
)
from tests.fcp_0068_btc_perpetual_paper_stress_evaluation_trigger_predicate_semantics_registry_app_1.test_d1_d6 import (
    _registry as _predicate_registry,
)
from tests.fcp_0069_btc_perpetual_paper_stress_evaluation_input_binding_registry_app_1.test_d1_d6 import (
    _registry as _input_binding_registry,
)


def _evaluation():
    return evaluate_btc_perpetual_paper_stress_triggers(
        _input_binding_registry(),
        _predicate_registry(),
        _operand_registry(),
        _scenario_registry(),
        evaluated_at_utc="2026-07-22T12:00:00Z",
    )


def test_exact_bound_registries_build_eight_reviewed_paper_results():
    evaluation = _evaluation()
    assert len(evaluation.results) == 8
    assert evaluation.paper_evaluation_only is True
    assert evaluation.evaluation_allowed is True
    assert evaluation.calculation_allowed is True
    assert evaluation.operator_review_required is True
    assert len(evaluation.snapshot_hash) == 64


def test_closed_formula_outputs_use_exact_decimal_arithmetic():
    observed = {item.scenario_kind: item.measure_value for item in _evaluation().results}
    assert observed == {
        "COLLATERAL_DRAWDOWN": Decimal("0.18"),
        "FUNDING_SHOCK": Decimal("0.0014"),
        "LIQUIDATION_DISTANCE": Decimal("0.08"),
        "LOSS_STREAK": Decimal("4"),
        "PRICE_GAP": Decimal("4000") / Decimal("65000"),
        "RESYNC": Decimal("12"),
        "THIN_BOOK": Decimal("0.16"),
        "VENUE_OUTAGE": Decimal("30"),
    }
    assert all(not isinstance(value, float) for value in observed.values())


def test_closed_predicates_emit_expected_fixture_triggers():
    observed = {item.scenario_kind: item.triggered for item in _evaluation().results}
    assert observed == {
        "COLLATERAL_DRAWDOWN": True,
        "FUNDING_SHOCK": False,
        "LIQUIDATION_DISTANCE": True,
        "LOSS_STREAK": True,
        "PRICE_GAP": False,
        "RESYNC": False,
        "THIN_BOOK": False,
        "VENUE_OUTAGE": False,
    }


def test_result_lineage_is_exactly_bound_to_registered_inputs():
    evaluation = _evaluation()
    bindings = _input_binding_registry()
    predicates = _predicate_registry()
    assert evaluation.input_binding_registry_hash == bindings.registry_hash
    assert evaluation.predicate_registry_hash == predicates.registry_hash
    for result, binding, predicate in zip(
        evaluation.results,
        bindings.bindings,
        predicates.semantics,
        strict=True,
    ):
        assert result.input_binding_hash == binding.binding_hash
        assert result.predicate_semantics_hash == predicate.semantics_hash


@pytest.mark.parametrize(
    "position,message",
    (
        (0, "FCP-0069"),
        (1, "FCP-0068"),
        (2, "FCP-0064"),
        (3, "FCP-0056"),
    ),
)
def test_requires_exact_typed_upstream_evidence(position, message):
    values = [
        _input_binding_registry(),
        _predicate_registry(),
        _operand_registry(),
        _scenario_registry(),
    ]
    values[position] = "unsafe"
    with pytest.raises(TypeError, match=message):
        evaluate_btc_perpetual_paper_stress_triggers(
            *values,
            evaluated_at_utc="2026-07-22T12:00:00Z",
        )


def test_predicate_registry_substitution_fails_closed():
    with pytest.raises(ValueError, match="predicate registry lineage"):
        evaluate_btc_perpetual_paper_stress_triggers(
            replace(_input_binding_registry(), predicate_registry_hash="f" * 64),
            _predicate_registry(),
            _operand_registry(),
            _scenario_registry(),
            evaluated_at_utc="2026-07-22T12:00:00Z",
        )


def test_operand_registry_substitution_fails_closed():
    with pytest.raises(ValueError, match="operand evidence registry lineage"):
        evaluate_btc_perpetual_paper_stress_triggers(
            replace(_input_binding_registry(), operand_evidence_registry_hash="f" * 64),
            _predicate_registry(),
            _operand_registry(),
            _scenario_registry(),
            evaluated_at_utc="2026-07-22T12:00:00Z",
        )


def test_scenario_registry_substitution_fails_closed():
    with pytest.raises(ValueError, match="scenario registry lineage"):
        evaluate_btc_perpetual_paper_stress_triggers(
            replace(_input_binding_registry(), scenario_registry_hash="f" * 64),
            _predicate_registry(),
            _operand_registry(),
            _scenario_registry(),
            evaluated_at_utc="2026-07-22T12:00:00Z",
        )


def test_evaluation_cannot_precede_bound_inputs():
    with pytest.raises(ValueError, match="cannot precede"):
        evaluate_btc_perpetual_paper_stress_triggers(
            _input_binding_registry(),
            _predicate_registry(),
            _operand_registry(),
            _scenario_registry(),
            evaluated_at_utc="2026-07-22T11:00:00Z",
        )


def test_evaluation_hash_is_deterministic_and_identity_bound():
    assert _evaluation().snapshot_hash == _evaluation().snapshot_hash
    changed = evaluate_btc_perpetual_paper_stress_triggers(
        _input_binding_registry(),
        _predicate_registry(),
        _operand_registry(),
        _scenario_registry(),
        evaluated_at_utc="2026-07-22T12:00:00Z",
        evaluation_id="changed-evaluation",
    )
    assert changed.snapshot_hash != _evaluation().snapshot_hash


def test_result_and_evaluation_are_immutable():
    evaluation = _evaluation()
    with pytest.raises(FrozenInstanceError):
        evaluation.results[0].triggered = False
    with pytest.raises(FrozenInstanceError):
        evaluation.evaluation_id = "changed"


def test_positive_relative_decrease_never_invents_negative_drawdown():
    assert _measure(
        "POSITIVE_RELATIVE_DECREASE",
        (Decimal("1"), Decimal("1.2")),
        "REJECT_NONPOSITIVE_BASELINE",
    ) == Decimal("0")


@pytest.mark.parametrize(
    "formula,values",
    (
        ("POSITIVE_RELATIVE_DECREASE", (Decimal("0"), Decimal("1"))),
        ("ABSOLUTE_RELATIVE_DIFFERENCE", (Decimal("-1"), Decimal("1"))),
        ("CURRENT_BASELINE_RETENTION_RATIO", (Decimal("0"), Decimal("1"))),
    ),
)
def test_relative_formulas_reject_nonpositive_baselines(formula, values):
    with pytest.raises(ValueError, match="positive baseline"):
        _measure(formula, values, "REJECT_NONPOSITIVE_BASELINE")


def test_funding_parameter_uses_registered_absolute_transform():
    assert _transform(
        "ABSOLUTE_PARAMETER_MAGNITUDE",
        Decimal("-0.0001"),
    ) == Decimal("0.0001")


@pytest.mark.parametrize(
    "operator,left,right,expected",
    (
        ("MEASURE_GREATER_THAN_PARAMETER", Decimal("1"), Decimal("1"), False),
        ("MEASURE_GREATER_THAN_PARAMETER", Decimal("2"), Decimal("1"), True),
        ("MEASURE_LESS_THAN_PARAMETER", Decimal("1"), Decimal("1"), False),
        ("MEASURE_LESS_THAN_PARAMETER", Decimal("0"), Decimal("1"), True),
        ("MEASURE_LESS_THAN_OR_EQUAL_PARAMETER", Decimal("1"), Decimal("1"), True),
        ("MEASURE_GREATER_THAN_OR_EQUAL_PARAMETER", Decimal("1"), Decimal("1"), True),
    ),
)
def test_strict_and_inclusive_boundaries_are_exact(operator, left, right, expected):
    assert _compare(operator, left, right) is expected


def test_unknown_formula_transform_and_operator_fail_closed():
    with pytest.raises(ValueError, match="formula family"):
        _measure("UNREGISTERED", (Decimal("1"),), "NOT_APPLICABLE")
    with pytest.raises(ValueError, match="parameter transform"):
        _transform("UNREGISTERED", Decimal("1"))
    with pytest.raises(ValueError, match="comparison operator"):
        _compare("UNREGISTERED", Decimal("1"), Decimal("1"))


def test_evaluation_rejects_authority_escalation():
    evaluation = _evaluation()
    for update in (
        {"operator_review_required": False},
        {"paper_evaluation_only": False},
        {"account_state_allowed": True},
        {"margin_calculation_allowed": True},
        {"leverage_calculation_allowed": True},
        {"liquidation_price_calculation_allowed": True},
        {"balance_calculation_allowed": True},
        {"position_calculation_allowed": True},
        {"pnl_calculation_allowed": True},
        {"insurance_fund_mutation_allowed": True},
        {"adl_action_allowed": True},
        {"order_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="local Paper calculation"):
            replace(evaluation, **update)


def test_evaluation_rejects_authority_identity_changes():
    evaluation = _evaluation()
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(evaluation, **update)


def test_module_exposes_no_account_order_or_execution_api():
    for name in (
        "account",
        "balance",
        "position",
        "margin",
        "leverage",
        "liquidation_price",
        "pnl",
        "order",
        "execute",
    ):
        assert not hasattr(fcp_0070, name)
