from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0065_btc_perpetual_paper_stress_evaluation_context_coherence_gate_app_1 import (
    build_btc_perpetual_paper_stress_evaluation_context_snapshot,
)
from tests.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1.test_d1_d6 import (
    _registry as _scenario_registry,
)
from tests.fcp_0062_btc_perpetual_paper_stress_evaluation_readiness_parameter_domain_coherence_hardening_app_1.test_d1_d6 import (
    _snapshot as _extended_readiness,
)
from tests.fcp_0064_btc_perpetual_paper_stress_evaluation_operand_evidence_registry_app_1.test_d1_d6 import (
    _registry as _operand_evidence,
)


def _snapshot():
    return build_btc_perpetual_paper_stress_evaluation_context_snapshot(
        _scenario_registry(),
        _extended_readiness(),
        _operand_evidence(),
        as_of_utc="2026-07-22T08:10:00Z",
    )


def test_exact_typed_upstream_evidence_builds_context():
    snapshot = _snapshot()
    assert len(snapshot.scenario_kinds) == 8
    assert len(snapshot.operand_observation_hashes) == 12
    assert snapshot.context_only is True
    assert snapshot.direction_defined is False
    assert len(snapshot.snapshot_hash) == 64


@pytest.mark.parametrize("index,message", ((0, "FCP-0056"), (1, "FCP-0062"), (2, "FCP-0064")))
def test_requires_typed_upstream_evidence(index, message):
    inputs = [_scenario_registry(), _extended_readiness(), _operand_evidence()]
    inputs[index] = "unsafe"
    with pytest.raises(TypeError, match=message):
        build_btc_perpetual_paper_stress_evaluation_context_snapshot(
            *inputs, as_of_utc="2026-07-22T08:10:00Z"
        )


def test_definition_substitution_fails_closed():
    readiness = replace(
        _extended_readiness(),
        definition_hashes=("f" * 64,) + _extended_readiness().definition_hashes[1:],
    )
    with pytest.raises(ValueError, match="definition lineage"):
        build_btc_perpetual_paper_stress_evaluation_context_snapshot(
            _scenario_registry(), readiness, _operand_evidence(), as_of_utc="2026-07-22T08:10:00Z"
        )


def test_rule_bundle_substitution_fails_closed():
    changed = replace(_extended_readiness(), complete_rule_bundle_hash="f" * 64)
    with pytest.raises(ValueError, match="complete rule bundle"):
        build_btc_perpetual_paper_stress_evaluation_context_snapshot(
            _scenario_registry(), changed, _operand_evidence(), as_of_utc="2026-07-22T08:10:00Z"
        )


@pytest.mark.parametrize(
    "field,message",
    (
        ("extended_readiness_snapshot_hash", "extended readiness ancestry"),
        ("coverage_snapshot_hash", "coverage snapshot lineage"),
        ("parameter_domain_snapshot_hash", "parameter domain lineage"),
        ("complete_rule_bundle_hash", "operand schema rule bundle"),
    ),
)
def test_operand_schema_ancestry_substitution_fails_closed(field, message):
    evidence = _operand_evidence()
    changed_schema = replace(evidence.operand_schema_snapshot, **{field: "f" * 64})
    changed_evidence = replace(evidence, operand_schema_snapshot=changed_schema)
    with pytest.raises(ValueError, match=message):
        build_btc_perpetual_paper_stress_evaluation_context_snapshot(
            _scenario_registry(), _extended_readiness(), changed_evidence, as_of_utc="2026-07-22T08:10:00Z"
        )


def test_cross_contract_fails_closed():
    changed = replace(_extended_readiness(), contract_id="ETH-USDT-PERP")
    with pytest.raises(ValueError, match="extended readiness ancestry"):
        build_btc_perpetual_paper_stress_evaluation_context_snapshot(
            _scenario_registry(), changed, _operand_evidence(), as_of_utc="2026-07-22T08:10:00Z"
        )


def test_context_time_reversal_fails_closed():
    with pytest.raises(ValueError, match="UTC lineage"):
        build_btc_perpetual_paper_stress_evaluation_context_snapshot(
            _scenario_registry(), _extended_readiness(), _operand_evidence(), as_of_utc="2026-07-22T07:59:00Z"
        )


def test_hash_is_deterministic_and_upstream_bound():
    assert _snapshot().snapshot_hash == _snapshot().snapshot_hash
    changed = build_btc_perpetual_paper_stress_evaluation_context_snapshot(
        _scenario_registry(),
        _extended_readiness(),
        _operand_evidence(),
        as_of_utc="2026-07-22T08:10:00Z",
        gate_id="changed-context-gate",
    )
    assert changed.snapshot_hash != _snapshot().snapshot_hash


def test_context_rejects_authority_escalation():
    snapshot = _snapshot()
    for update in (
        {"operator_review_required": False},
        {"context_only": False},
        {"coherence_validated": False},
        {"direction_defined": True},
        {"formula_registered": True},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot direct"):
            replace(snapshot, **update)


def test_context_rejects_authority_identity_changes():
    snapshot = _snapshot()
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(snapshot, **update)


def test_context_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _snapshot().gate_id = "changed"
