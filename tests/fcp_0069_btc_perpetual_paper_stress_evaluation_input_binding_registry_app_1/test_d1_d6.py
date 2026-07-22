from dataclasses import FrozenInstanceError, replace

import pytest

import apps.fcp_0069_btc_perpetual_paper_stress_evaluation_input_binding_registry_app_1 as fcp_0069
from apps.fcp_0069_btc_perpetual_paper_stress_evaluation_input_binding_registry_app_1 import (
    build_btc_perpetual_paper_stress_evaluation_input_binding_registry,
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


def _registry():
    return build_btc_perpetual_paper_stress_evaluation_input_binding_registry(
        _predicate_registry(),
        _operand_registry(),
        _scenario_registry(),
        as_of_utc="2026-07-22T11:30:00Z",
    )


def test_exact_typed_upstream_registries_build_input_bindings():
    registry = _registry()
    assert len(registry.bindings) == 8
    assert registry.input_binding_only is True
    assert registry.evaluation_allowed is False
    assert registry.calculation_allowed is False
    assert len(registry.registry_hash) == 64


def test_bindings_preserve_exact_predicate_observation_and_parameter_lineage():
    predicate = _predicate_registry()
    operands = _operand_registry()
    scenarios = _scenario_registry()
    registry = _registry()
    assert registry.predicate_registry_hash == predicate.registry_hash
    assert registry.operand_evidence_registry_hash == operands.registry_hash
    assert registry.scenario_registry_hash == scenarios.registry_hash
    for binding, semantics in zip(registry.bindings, predicate.semantics, strict=True):
        assert binding.scenario_kind == semantics.scenario_kind
        assert binding.predicate_semantics_hash == semantics.semantics_hash
        observations = tuple(
            item
            for item in operands.observations
            if item.scenario_kind == binding.scenario_kind
        )
        assert binding.operand_roles == tuple(item.role_id for item in observations)
        assert binding.observation_hashes == tuple(
            item.observation_hash for item in observations
        )


@pytest.mark.parametrize(
    "position",
    (0, 1, 2),
)
def test_requires_typed_upstream_registries(position):
    values = [_predicate_registry(), _operand_registry(), _scenario_registry()]
    values[position] = "unsafe"
    with pytest.raises(TypeError, match=("FCP-0068", "FCP-0064", "FCP-0056")[position]):
        build_btc_perpetual_paper_stress_evaluation_input_binding_registry(
            *values,
            as_of_utc="2026-07-22T11:30:00Z",
        )


def test_predicate_operand_lineage_mismatch_fails_closed():
    with pytest.raises(ValueError, match="operand evidence registry"):
        build_btc_perpetual_paper_stress_evaluation_input_binding_registry(
            replace(_predicate_registry(), operand_evidence_registry_hash="f" * 64),
            _operand_registry(),
            _scenario_registry(),
            as_of_utc="2026-07-22T11:30:00Z",
        )


def test_predicate_scenario_lineage_mismatch_fails_closed():
    with pytest.raises(ValueError, match="scenario registry"):
        build_btc_perpetual_paper_stress_evaluation_input_binding_registry(
            replace(_predicate_registry(), scenario_registry_hash="f" * 64),
            _operand_registry(),
            _scenario_registry(),
            as_of_utc="2026-07-22T11:30:00Z",
        )


@pytest.mark.parametrize(
    "bindings",
    (
        lambda values: values[:-1],
        lambda values: values + (values[-1],),
        lambda values: (values[1], values[0]) + values[2:],
    ),
)
def test_missing_duplicate_or_reordered_bindings_fail_closed(bindings):
    registry = _registry()
    with pytest.raises(ValueError, match="every closed scenario kind"):
        replace(registry, bindings=bindings(registry.bindings))


@pytest.mark.parametrize(
    "field,value",
    (
        ("predicate_semantics_hash", "f" * 64),
        ("operand_roles", ("current", "baseline")),
        ("observation_hashes", ("f" * 64, "e" * 64)),
        ("parameter_id", "gap-rate"),
        ("parameter_hash", "f" * 64),
    ),
)
def test_binding_substitution_changes_closed_schema_hash(field, value):
    registry = _registry()
    changed = replace(registry.bindings[0], **{field: value})
    with pytest.raises(ValueError, match="binding_schema_hash"):
        replace(registry, bindings=(changed,) + registry.bindings[1:])


def test_binding_schema_hash_substitution_fails_closed():
    with pytest.raises(ValueError, match="binding_schema_hash"):
        replace(_registry(), binding_schema_hash="f" * 64)


def test_registry_cannot_precede_any_registered_input():
    with pytest.raises(ValueError, match="cannot precede"):
        build_btc_perpetual_paper_stress_evaluation_input_binding_registry(
            _predicate_registry(),
            _operand_registry(),
            _scenario_registry(),
            as_of_utc="2026-07-22T10:00:00Z",
        )


def test_registry_hash_is_deterministic_and_identity_bound():
    assert _registry().registry_hash == _registry().registry_hash
    changed = build_btc_perpetual_paper_stress_evaluation_input_binding_registry(
        _predicate_registry(),
        _operand_registry(),
        _scenario_registry(),
        as_of_utc="2026-07-22T11:30:00Z",
        registry_id="changed-input-binding-registry",
    )
    assert changed.registry_hash != _registry().registry_hash


def test_registry_rejects_authority_escalation():
    registry = _registry()
    for update in (
        {"operator_review_required": False},
        {"input_binding_only": False},
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
    assert not hasattr(fcp_0069, "evaluate")
    assert not hasattr(fcp_0069, "calculate")


def test_registry_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _registry().registry_id = "changed"
