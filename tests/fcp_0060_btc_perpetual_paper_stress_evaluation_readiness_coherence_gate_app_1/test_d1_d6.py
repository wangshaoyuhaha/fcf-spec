from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    build_btc_perpetual_paper_stress_coverage_snapshot,
)
from apps.fcp_0059_btc_perpetual_paper_stress_evaluation_input_domain_semantics_hardening_app_1 import (
    build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot,
)
from apps.fcp_0060_btc_perpetual_paper_stress_evaluation_readiness_coherence_gate_app_1 import (
    build_btc_perpetual_paper_stress_evaluation_readiness_snapshot,
)
from tests.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1.test_d1_d6 import (
    _registry as _scenario_registry,
)
from tests.fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_app_1.test_d1_d6 import (
    _registry as _input_registry,
)


def _evidence():
    scenario_registry = _scenario_registry()
    coverage = build_btc_perpetual_paper_stress_coverage_snapshot(scenario_registry)
    input_registry = _input_registry(coverage=coverage)
    domain = build_btc_perpetual_paper_stress_evaluation_input_domain_snapshot(
        input_registry
    )
    return scenario_registry.complete_rule_bundle, coverage, domain


def _readiness():
    return build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(*_evidence())


def test_exact_upstream_evidence_produces_immutable_readiness_snapshot():
    bundle, coverage, domain = _evidence()
    snapshot = build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
        bundle, coverage, domain
    )

    assert snapshot.complete_rule_bundle_hash == bundle.snapshot_hash
    assert snapshot.coverage_snapshot_hash == coverage.snapshot_hash
    assert snapshot.input_domain_snapshot_hash == domain.snapshot_hash
    assert snapshot.scenario_kinds == coverage.covered_scenario_kinds
    assert snapshot.readiness_only is True
    assert snapshot.evaluation_allowed is False
    assert len(snapshot.snapshot_hash) == 64


@pytest.mark.parametrize("index, message", [(0, "FCP-0055"), (1, "FCP-0057"), (2, "FCP-0059")])
def test_gate_requires_typed_upstream_evidence(index, message):
    evidence = list(_evidence())
    evidence[index] = "unsafe"
    with pytest.raises(TypeError, match=message):
        build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(*evidence)


def test_complete_rule_snapshot_substitution_fails_closed():
    bundle, coverage, domain = _evidence()
    changed = replace(bundle, position_mode="HEDGE")
    with pytest.raises(ValueError, match="complete-rule snapshot lineage mismatch"):
        build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
            changed, coverage, domain
        )


def test_coverage_snapshot_substitution_fails_closed():
    bundle, coverage, domain = _evidence()
    changed = replace(coverage, gate_id="changed-coverage-gate")
    with pytest.raises(ValueError, match="coverage snapshot lineage mismatch"):
        build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
            bundle, changed, domain
        )


def test_cross_contract_domain_fails_closed():
    bundle, coverage, domain = _evidence()
    changed = replace(domain, contract_id="ETH-USDT-PERP")
    with pytest.raises(ValueError, match="venue or contract lineage mismatch"):
        build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
            bundle, coverage, changed
        )


def test_coverage_cannot_predate_complete_rule_bundle():
    bundle, coverage, domain = _evidence()
    changed_coverage = replace(
        coverage,
        registry_as_of_utc="2026-07-21T23:59:59Z",
    )
    changed_domain = replace(
        domain,
        coverage_snapshot_hash=changed_coverage.snapshot_hash,
    )
    with pytest.raises(ValueError, match="time lineage must be monotonic"):
        build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
            bundle, changed_coverage, changed_domain
        )


def test_input_domain_cannot_predate_coverage():
    bundle, coverage, domain = _evidence()
    changed = replace(domain, as_of_utc="2026-07-22T00:02:59Z")
    with pytest.raises(ValueError, match="time lineage must be monotonic"):
        build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
            bundle, coverage, changed
        )


def test_readiness_hash_is_deterministic_and_lineage_bound():
    first = _readiness()
    second = _readiness()
    bundle, coverage, domain = _evidence()
    changed_domain = replace(domain, hardening_id="changed-domain-hardening")
    changed = build_btc_perpetual_paper_stress_evaluation_readiness_snapshot(
        bundle, coverage, changed_domain
    )

    assert first.snapshot_hash == second.snapshot_hash
    assert first.snapshot_hash != changed.snapshot_hash


def test_readiness_snapshot_rejects_authority_escalation():
    snapshot = _readiness()
    for update in (
        {"operator_review_required": False},
        {"readiness_only": False},
        {"coherence_validated": False},
        {"source_selected": True},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot evaluate, calculate, execute, or close"):
            replace(snapshot, **update)


def test_readiness_snapshot_rejects_authority_identity_changes():
    snapshot = _readiness()
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(snapshot, **update)


def test_readiness_snapshot_is_frozen():
    snapshot = _readiness()
    with pytest.raises(FrozenInstanceError):
        snapshot.gate_id = "changed"
