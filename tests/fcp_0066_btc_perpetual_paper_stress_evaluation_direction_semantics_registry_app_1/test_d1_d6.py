from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0066_btc_perpetual_paper_stress_evaluation_direction_semantics_registry_app_1 import (
    BTC_STRESS_EVALUATION_DIRECTION_SCHEMA,
    BTCPerpetualPaperStressDirectionSemantics,
    build_btc_perpetual_paper_stress_direction_semantics_registry,
)
from tests.fcp_0065_btc_perpetual_paper_stress_evaluation_context_coherence_gate_app_1.test_d1_d6 import (
    _snapshot as _context,
)


def _registry():
    return build_btc_perpetual_paper_stress_direction_semantics_registry(
        _context(),
        as_of_utc="2026-07-22T09:30:00Z",
    )


def test_exact_typed_fcp_0065_context_builds_direction_registry():
    registry = _registry()
    assert registry.evaluation_context_snapshot_hash == _context().snapshot_hash
    assert len(registry.semantics) == 8
    assert registry.semantics_only is True
    assert registry.direction_defined is True
    assert registry.formula_registered is False
    assert len(registry.registry_hash) == 64


def test_closed_direction_schema_is_exact_and_ordered():
    observed = tuple(
        (
            item.scenario_kind,
            item.direction_id,
            item.comparison_family_id,
            item.operand_roles,
            item.equality_policy_id,
        )
        for item in _registry().semantics
    )
    assert observed == BTC_STRESS_EVALUATION_DIRECTION_SCHEMA


def test_requires_typed_fcp_0065_context():
    with pytest.raises(TypeError, match="FCP-0065"):
        build_btc_perpetual_paper_stress_direction_semantics_registry(
            "unsafe",
            as_of_utc="2026-07-22T09:30:00Z",
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("direction_id", "HIGHER_IS_MORE_STRESSFUL"),
        ("comparison_family_id", "OBSERVED_UPPER_BOUND"),
        ("operand_roles", ("current", "baseline")),
        ("equality_policy_id", "EQUALITY_IS_TRIGGERING"),
    ),
)
def test_kind_semantics_substitution_fails_closed(field, value):
    item = _registry().semantics[0]
    with pytest.raises(ValueError, match="closed kind schema"):
        replace(item, **{field: value})


def test_unknown_kind_fails_closed():
    source = _registry().semantics[0]
    with pytest.raises(ValueError, match="scenario_kind"):
        BTCPerpetualPaperStressDirectionSemantics(
            scenario_kind="UNKNOWN",
            direction_id=source.direction_id,
            comparison_family_id=source.comparison_family_id,
            operand_roles=source.operand_roles,
            equality_policy_id=source.equality_policy_id,
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


def test_direction_schema_hash_substitution_fails_closed():
    with pytest.raises(ValueError, match="direction_schema_hash"):
        replace(_registry(), direction_schema_hash="f" * 64)


def test_registry_cannot_precede_context():
    with pytest.raises(ValueError, match="cannot precede"):
        build_btc_perpetual_paper_stress_direction_semantics_registry(
            _context(),
            as_of_utc="2026-07-22T08:00:00Z",
        )


def test_registry_hash_is_deterministic_and_context_bound():
    assert _registry().registry_hash == _registry().registry_hash
    changed = build_btc_perpetual_paper_stress_direction_semantics_registry(
        _context(),
        as_of_utc="2026-07-22T09:30:00Z",
        registry_id="changed-direction-registry",
    )
    assert changed.registry_hash != _registry().registry_hash


def test_registry_rejects_authority_escalation():
    registry = _registry()
    for update in (
        {"operator_review_required": False},
        {"semantics_only": False},
        {"direction_defined": False},
        {"formula_registered": True},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot formulate"):
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


def test_registry_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _registry().registry_id = "changed"
