from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import build_btc_perpetual_paper_stress_coverage_snapshot
from apps.fcp_0060_btc_perpetual_paper_stress_evaluation_readiness_coherence_gate_app_1 import build_btc_perpetual_paper_stress_evaluation_readiness_snapshot
from apps.fcp_0061_btc_perpetual_paper_stress_scenario_parameter_domain_semantics_hardening_app_1 import build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot
from apps.fcp_0062_btc_perpetual_paper_stress_evaluation_readiness_parameter_domain_coherence_hardening_app_1 import build_btc_perpetual_paper_stress_extended_readiness_snapshot
from tests.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1.test_d1_d6 import _registry as _scenario_registry
from tests.fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_app_1.test_d1_d6 import _registry as _input_registry
from apps.fcp_0059_btc_perpetual_paper_stress_evaluation_input_domain_semantics_hardening_app_1 import build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot


def _evidence():
    registry = _scenario_registry()
    coverage = build_btc_perpetual_paper_stress_coverage_snapshot(registry)
    input_domain = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(_input_registry(coverage=coverage))
    readiness = build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(registry.complete_rule_bundle, coverage, input_domain)
    parameter_domain = build_btc_perpetual_paper_stress_scenario_parameter_domain_snapshot(registry, coverage)
    return readiness, parameter_domain


def _snapshot():
    return build_btc_perpetual_paper_stress_extended_readiness_snapshot(*_evidence())


def test_exact_evidence_produces_extended_readiness():
    readiness, parameter_domain = _evidence()
    snapshot = build_btc_perpetual_paper_stress_extended_readiness_snapshot(readiness, parameter_domain)
    assert snapshot.readiness_snapshot_hash == readiness.snapshot_hash
    assert snapshot.parameter_domain_snapshot_hash == parameter_domain.snapshot_hash
    assert snapshot.extended_readiness_only is True
    assert snapshot.direction_defined is False
    assert len(snapshot.snapshot_hash) == 64


@pytest.mark.parametrize("index, message", [(0, "FCP-0060"), (1, "FCP-0061")])
def test_requires_typed_upstream_evidence(index, message):
    evidence = list(_evidence()); evidence[index] = "unsafe"
    with pytest.raises(TypeError, match=message):
        build_btc_perpetual_paper_stress_extended_readiness_snapshot(*evidence)


def test_coverage_substitution_fails_closed():
    readiness, parameter_domain = _evidence()
    changed = replace(parameter_domain, coverage_snapshot_hash="f" * 64)
    with pytest.raises(ValueError, match="coverage lineage mismatch"):
        build_btc_perpetual_paper_stress_extended_readiness_snapshot(readiness, changed)


def test_definition_substitution_fails_closed():
    readiness, parameter_domain = _evidence()
    changed = replace(parameter_domain, validated_definition_hashes=("f" * 64,) + parameter_domain.validated_definition_hashes[1:])
    with pytest.raises(ValueError, match="definition lineage mismatch"):
        build_btc_perpetual_paper_stress_extended_readiness_snapshot(readiness, changed)


def test_cross_contract_fails_closed():
    readiness, parameter_domain = _evidence()
    changed = replace(parameter_domain, contract_id="ETH-USDT-PERP")
    with pytest.raises(ValueError, match="venue or contract lineage mismatch"):
        build_btc_perpetual_paper_stress_extended_readiness_snapshot(readiness, changed)


def test_parameter_domain_time_mismatch_fails_closed():
    readiness, parameter_domain = _evidence()
    changed = replace(parameter_domain, as_of_utc="2026-07-22T00:02:59Z")
    with pytest.raises(ValueError, match="parameter-domain time lineage mismatch"):
        build_btc_perpetual_paper_stress_extended_readiness_snapshot(readiness, changed)


def test_hash_is_deterministic_and_upstream_bound():
    assert _snapshot().snapshot_hash == _snapshot().snapshot_hash
    readiness, parameter_domain = _evidence()
    changed = replace(parameter_domain, hardening_id="changed-hardening")
    assert _snapshot().snapshot_hash != build_btc_perpetual_paper_stress_extended_readiness_snapshot(readiness, changed).snapshot_hash


def test_snapshot_rejects_authority_escalation():
    snapshot = _snapshot()
    for update in ({"operator_review_required": False}, {"extended_readiness_only": False}, {"coherence_validated": False}, {"direction_defined": True}, {"evaluation_allowed": True}, {"calculation_allowed": True}, {"account_state_allowed": True}, {"execution_allowed": True}, {"gap_closed": True}):
        with pytest.raises(ValueError, match="cannot direct, evaluate, calculate"):
            replace(snapshot, **update)


def test_snapshot_rejects_authority_identity_changes():
    snapshot = _snapshot()
    for update in ({"calculation_authority": "AI"}, {"evidence_authority": "UNREGISTERED"}, {"ai_role": "AUTHORITATIVE"}):
        with pytest.raises(ValueError, match="authority identities"):
            replace(snapshot, **update)


def test_snapshot_is_frozen():
    snapshot = _snapshot()
    with pytest.raises(FrozenInstanceError):
        snapshot.hardening_id = "changed"
