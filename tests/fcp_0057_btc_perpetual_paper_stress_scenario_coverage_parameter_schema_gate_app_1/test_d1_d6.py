from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.fcp_0055_btc_perpetual_complete_rule_bundle_coherence_hardening_app_1 import (
    BTCPerpetualCompleteRuleBundleSnapshot,
)
from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
    BTCPerpetualPaperStressScenarioDefinition,
    BTCPerpetualPaperStressScenarioRegistry,
    BTCStressScenarioParameter,
    RegisteredBTCStressScenarioArtifact,
)
from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    BTC_STRESS_PARAMETER_SCHEMA,
    build_btc_perpetual_paper_stress_coverage_snapshot,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _bundle():
    return BTCPerpetualCompleteRuleBundleSnapshot(
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        effective_at_utc="2026-07-22T00:00:00Z",
        margin_mode="ISOLATED",
        position_mode="ONE_WAY",
        lifecycle_state="ACTIVE",
        base_rule_bundle_hash="1" * 64,
        contract_registry_hash="2" * 64,
        margin_registry_hash="3" * 64,
        funding_registry_hash="4" * 64,
        fee_registry_hash="5" * 64,
        liquidation_registry_hash="6" * 64,
        contract_entry_hash="7" * 64,
        margin_rule_entry_hash="8" * 64,
        funding_rule_entry_hash="9" * 64,
        fee_rule_entry_hash="a" * 64,
        liquidation_rule_entry_hash="b" * 64,
        liquidation_effective_from_utc="2026-01-01T00:00:00Z",
    )


def _artifact():
    content = b"registered complete BTC stress suite\n"
    return RegisteredBTCStressScenarioArtifact(
        "btc-stress-definitions-v1",
        hashlib.sha256(content).hexdigest(),
        len(content),
        LocalEventRights("synthetic-test", "local-paper-research", 30),
        "2026-07-22T00:01:00Z",
        "2026-07-22T00:02:00Z",
    )


def _value(unit_id: str) -> Decimal:
    return {
        "count": Decimal("3"),
        "ratio": Decimal("0.1"),
        "seconds": Decimal("60"),
    }[unit_id]


def _definition(kind: str, *, suffix="v1", parameters=None):
    schema = dict(BTC_STRESS_PARAMETER_SCHEMA)[kind]
    typed_parameters = tuple(
        BTCStressScenarioParameter(parameter_id, _value(unit_id), unit_id)
        for parameter_id, unit_id in schema
    )
    return BTCPerpetualPaperStressScenarioDefinition(
        scenario_id=f"{kind.lower().replace('_', '-')}-{suffix}",
        version_id=f"version-{kind.lower().replace('_', '-')}-{suffix}",
        artifact_id="btc-stress-definitions-v1",
        complete_rule_bundle_hash=_bundle().snapshot_hash,
        venue_id="venue-a",
        contract_id="BTC-USDT-PERP",
        scenario_kind=kind,
        severity="HIGH",
        horizon_seconds=60,
        parameters=typed_parameters if parameters is None else tuple(parameters),
    )


def _registry(definitions=None):
    items = tuple(
        _definition(kind) for kind in BTC_STRESS_SCENARIO_KINDS
    ) if definitions is None else tuple(definitions)
    return BTCPerpetualPaperStressScenarioRegistry(
        registry_id="btc-stress-registry-v1",
        artifact=_artifact(),
        complete_rule_bundle=_bundle(),
        definitions=items,
        as_of_utc="2026-07-22T00:03:00Z",
    )


def test_complete_registry_produces_exact_immutable_coverage_snapshot():
    registry = _registry()
    snapshot = build_btc_perpetual_paper_stress_coverage_snapshot(registry)

    assert snapshot.registry_hash == registry.registry_hash
    assert snapshot.complete_rule_bundle_hash == registry.complete_rule_bundle.snapshot_hash
    assert snapshot.covered_scenario_kinds == BTC_STRESS_SCENARIO_KINDS
    assert snapshot.definition_hashes == tuple(
        definition.definition_hash for definition in registry.definitions
    )
    assert len(snapshot.parameter_schema_hash) == len(snapshot.snapshot_hash) == 64


def test_parameter_schema_matches_closed_kind_vocabulary_exactly():
    assert tuple(kind for kind, _ in BTC_STRESS_PARAMETER_SCHEMA) == BTC_STRESS_SCENARIO_KINDS
    assert all(parameters for _, parameters in BTC_STRESS_PARAMETER_SCHEMA)


def test_missing_kind_fails_closed():
    with pytest.raises(ValueError, match="coverage is incomplete"):
        build_btc_perpetual_paper_stress_coverage_snapshot(
            _registry(tuple(_definition(kind) for kind in BTC_STRESS_SCENARIO_KINDS[:-1]))
        )


def test_duplicate_kind_fails_closed():
    definitions = list(_definition(kind) for kind in BTC_STRESS_SCENARIO_KINDS)
    definitions.insert(5, _definition("PRICE_GAP", suffix="v2"))
    with pytest.raises(ValueError, match="duplicate kinds"):
        build_btc_perpetual_paper_stress_coverage_snapshot(_registry(definitions))


def test_empty_parameter_definition_is_rejected_before_gate():
    with pytest.raises(ValueError, match="typed parameters"):
        _definition("PRICE_GAP", parameters=())


def test_unknown_parameter_fails_closed():
    wrong = (BTCStressScenarioParameter("unknown-rate", Decimal("0.1"), "ratio"),)
    definitions = [
        _definition(kind, parameters=wrong) if kind == "PRICE_GAP" else _definition(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    ]
    with pytest.raises(ValueError, match="parameter schema mismatch"):
        build_btc_perpetual_paper_stress_coverage_snapshot(_registry(definitions))


def test_unit_mismatch_fails_closed():
    wrong = (BTCStressScenarioParameter("gap-rate", Decimal("0.1"), "count"),)
    definitions = [
        _definition(kind, parameters=wrong) if kind == "PRICE_GAP" else _definition(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    ]
    with pytest.raises(ValueError, match="parameter schema mismatch"):
        build_btc_perpetual_paper_stress_coverage_snapshot(_registry(definitions))


def test_extra_parameter_fails_closed():
    wrong = (
        BTCStressScenarioParameter("extra-rate", Decimal("0.1"), "ratio"),
        BTCStressScenarioParameter("gap-rate", Decimal("0.1"), "ratio"),
    )
    definitions = [
        _definition(kind, parameters=wrong) if kind == "PRICE_GAP" else _definition(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    ]
    with pytest.raises(ValueError, match="parameter schema mismatch"):
        build_btc_perpetual_paper_stress_coverage_snapshot(_registry(definitions))


def test_gate_requires_typed_fcp_0056_registry():
    with pytest.raises(TypeError, match="typed FCP-0056"):
        build_btc_perpetual_paper_stress_coverage_snapshot("unsafe")


def test_snapshot_hash_is_deterministic_and_registry_bound():
    first = build_btc_perpetual_paper_stress_coverage_snapshot(_registry())
    second = build_btc_perpetual_paper_stress_coverage_snapshot(_registry())
    changed = build_btc_perpetual_paper_stress_coverage_snapshot(
        _registry(
            tuple(
                _definition(kind, suffix="v2")
                for kind in BTC_STRESS_SCENARIO_KINDS
            )
        )
    )

    assert first.snapshot_hash == second.snapshot_hash
    assert first.snapshot_hash != changed.snapshot_hash


def test_snapshot_rejects_authority_escalation():
    snapshot = build_btc_perpetual_paper_stress_coverage_snapshot(_registry())
    for update in (
        {"operator_review_required": False},
        {"validation_only": False},
        {"coverage_complete": False},
        {"source_selected": True},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot evaluate, calculate, execute, or close"):
            replace(snapshot, **update)


def test_snapshot_rejects_authority_identity_changes():
    snapshot = build_btc_perpetual_paper_stress_coverage_snapshot(_registry())
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(snapshot, **update)


def test_snapshot_is_frozen():
    snapshot = build_btc_perpetual_paper_stress_coverage_snapshot(_registry())
    with pytest.raises(FrozenInstanceError):
        snapshot.gate_id = "changed"
