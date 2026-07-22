from dataclasses import FrozenInstanceError, replace

import pytest

import apps.fcp_0071_btc_perpetual_paper_stress_trigger_result_review_registry_app_1 as fcp_0071
from apps.fcp_0071_btc_perpetual_paper_stress_trigger_result_review_registry_app_1 import (
    build_btc_perpetual_paper_stress_trigger_result_review_registry,
)
from tests.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1.test_d1_d6 import (
    _registry as _scenario_registry,
)
from tests.fcp_0070_btc_perpetual_paper_stress_deterministic_trigger_evaluation_app_1.test_d1_d6 import (
    _evaluation,
)


def _registry():
    return build_btc_perpetual_paper_stress_trigger_result_review_registry(
        _evaluation(),
        _scenario_registry(),
        registered_at_utc="2026-07-22T12:30:00Z",
    )


def test_exact_typed_evaluation_and_scenarios_build_eight_review_records():
    registry = _registry()
    assert len(registry.records) == 8
    assert registry.registration_only is True
    assert registry.operator_review_required is True
    assert all(
        item.operator_review_status == "PENDING_OPERATOR_REVIEW"
        for item in registry.records
    )
    assert len(registry.registry_hash) == 64


def test_records_copy_exact_result_and_scenario_lineage_without_recalculation():
    evaluation = _evaluation()
    scenarios = _scenario_registry()
    registry = _registry()
    for record, result, definition in zip(
        registry.records,
        evaluation.results,
        scenarios.definitions,
        strict=True,
    ):
        assert record.scenario_kind == result.scenario_kind == definition.scenario_kind
        assert record.scenario_id == definition.scenario_id
        assert record.version_id == definition.version_id
        assert record.definition_hash == definition.definition_hash
        assert record.severity == definition.severity
        assert record.horizon_seconds == definition.horizon_seconds
        assert record.result_hash == result.result_hash
        assert record.measure_value == result.measure_value
        assert record.transformed_parameter_value == result.transformed_parameter_value
        assert record.triggered is result.triggered


def test_nontriggered_results_remain_visible_for_operator_review():
    evaluation_by_kind = {item.scenario_kind: item for item in _evaluation().results}
    records_by_kind = {item.scenario_kind: item for item in _registry().records}
    nontriggered = {
        kind for kind, result in evaluation_by_kind.items() if result.triggered is False
    }
    assert nontriggered
    assert nontriggered == {
        kind for kind, record in records_by_kind.items() if record.triggered is False
    }


@pytest.mark.parametrize("position,message", ((0, "FCP-0070"), (1, "FCP-0056")))
def test_requires_exact_typed_upstream_evidence(position, message):
    values = [_evaluation(), _scenario_registry()]
    values[position] = "unsafe"
    with pytest.raises(TypeError, match=message):
        build_btc_perpetual_paper_stress_trigger_result_review_registry(
            *values,
            registered_at_utc="2026-07-22T12:30:00Z",
        )


def test_scenario_registry_substitution_fails_closed():
    with pytest.raises(ValueError, match="scenario registry lineage"):
        build_btc_perpetual_paper_stress_trigger_result_review_registry(
            replace(_evaluation(), scenario_registry_hash="f" * 64),
            _scenario_registry(),
            registered_at_utc="2026-07-22T12:30:00Z",
        )


def test_complete_rule_bundle_substitution_fails_closed():
    with pytest.raises(ValueError, match="complete rule bundle lineage"):
        build_btc_perpetual_paper_stress_trigger_result_review_registry(
            replace(_evaluation(), complete_rule_bundle_hash="f" * 64),
            _scenario_registry(),
            registered_at_utc="2026-07-22T12:30:00Z",
        )


def test_contract_substitution_fails_closed():
    with pytest.raises(ValueError, match="venue or contract"):
        build_btc_perpetual_paper_stress_trigger_result_review_registry(
            replace(_evaluation(), contract_id="other-contract"),
            _scenario_registry(),
            registered_at_utc="2026-07-22T12:30:00Z",
        )


def test_review_registration_cannot_precede_evaluation():
    with pytest.raises(ValueError, match="cannot precede evaluation"):
        build_btc_perpetual_paper_stress_trigger_result_review_registry(
            _evaluation(),
            _scenario_registry(),
            registered_at_utc="2026-07-22T11:59:59Z",
        )


def test_registry_hash_is_deterministic_and_identity_bound():
    assert _registry().registry_hash == _registry().registry_hash
    changed = build_btc_perpetual_paper_stress_trigger_result_review_registry(
        _evaluation(),
        _scenario_registry(),
        registered_at_utc="2026-07-22T12:30:00Z",
        registry_id="changed-review-registry",
    )
    assert changed.registry_hash != _registry().registry_hash


def test_records_and_registry_are_immutable():
    registry = _registry()
    with pytest.raises(FrozenInstanceError):
        registry.records[0].severity = "LOW"
    with pytest.raises(FrozenInstanceError):
        registry.registry_id = "changed"


@pytest.mark.parametrize(
    "records",
    (
        lambda values: values[:-1],
        lambda values: values + (values[-1],),
        lambda values: (values[1], values[0]) + values[2:],
    ),
)
def test_missing_duplicate_or_reordered_records_fail_closed(records):
    registry = _registry()
    with pytest.raises(ValueError, match="every closed scenario kind"):
        replace(registry, records=records(registry.records))


def test_record_evaluation_hash_substitution_fails_closed():
    registry = _registry()
    changed = replace(registry.records[0], evaluation_snapshot_hash="f" * 64)
    with pytest.raises(ValueError, match="evaluation lineage"):
        replace(registry, records=(changed,) + registry.records[1:])


def test_record_review_status_cannot_self_approve():
    with pytest.raises(ValueError, match="pending Operator review"):
        replace(_registry().records[0], operator_review_status="APPROVED")


def test_registry_rejects_authority_escalation():
    registry = _registry()
    for update in (
        {"operator_review_required": False},
        {"registration_only": False},
        {"recalculation_allowed": True},
        {"recommendation_allowed": True},
        {"account_state_allowed": True},
        {"margin_calculation_allowed": True},
        {"leverage_calculation_allowed": True},
        {"liquidation_action_allowed": True},
        {"balance_calculation_allowed": True},
        {"position_calculation_allowed": True},
        {"pnl_calculation_allowed": True},
        {"insurance_fund_mutation_allowed": True},
        {"adl_action_allowed": True},
        {"order_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot calculate"):
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


def test_module_exposes_no_calculation_recommendation_or_action_api():
    for name in (
        "calculate",
        "evaluate",
        "recommend",
        "account",
        "margin",
        "leverage",
        "liquidate",
        "order",
        "execute",
    ):
        assert not hasattr(fcp_0071, name)
