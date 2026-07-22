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
    BTC_STRESS_SEVERITIES,
    BTCPerpetualPaperStressScenarioDefinition,
    BTCPerpetualPaperStressScenarioRegistry,
    BTCStressScenarioParameter,
    RegisteredBTCStressScenarioArtifact,
    resolve_btc_perpetual_paper_stress_scenario_definition,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


def _bundle(**updates):
    values = {
        "venue_id": "venue-a",
        "contract_id": "BTC-USDT-PERP",
        "effective_at_utc": "2026-07-22T00:00:00Z",
        "margin_mode": "ISOLATED",
        "position_mode": "ONE_WAY",
        "lifecycle_state": "ACTIVE",
        "base_rule_bundle_hash": "1" * 64,
        "contract_registry_hash": "2" * 64,
        "margin_registry_hash": "3" * 64,
        "funding_registry_hash": "4" * 64,
        "fee_registry_hash": "5" * 64,
        "liquidation_registry_hash": "6" * 64,
        "contract_entry_hash": "7" * 64,
        "margin_rule_entry_hash": "8" * 64,
        "funding_rule_entry_hash": "9" * 64,
        "fee_rule_entry_hash": "a" * 64,
        "liquidation_rule_entry_hash": "b" * 64,
        "liquidation_effective_from_utc": "2026-01-01T00:00:00Z",
    }
    values.update(updates)
    return BTCPerpetualCompleteRuleBundleSnapshot(**values)


def _artifact(**updates):
    content = b"registered local BTC stress scenario definitions\n"
    values = {
        "artifact_id": "btc-stress-definitions-v1",
        "content_sha256": hashlib.sha256(content).hexdigest(),
        "byte_length": len(content),
        "rights": LocalEventRights(
            "synthetic-test",
            "local-paper-research",
            30,
        ),
        "observed_at_utc": "2026-07-22T00:01:00Z",
        "registered_at_utc": "2026-07-22T00:02:00Z",
    }
    values.update(updates)
    return RegisteredBTCStressScenarioArtifact(**values)


def _parameter(name="gap-rate", value="-0.1", unit="ratio"):
    return BTCStressScenarioParameter(name, Decimal(value), unit)


def _definition(name="price-gap-v1", **updates):
    bundle = _bundle()
    values = {
        "scenario_id": name,
        "version_id": f"version-{name}",
        "artifact_id": "btc-stress-definitions-v1",
        "complete_rule_bundle_hash": bundle.snapshot_hash,
        "venue_id": "venue-a",
        "contract_id": "BTC-USDT-PERP",
        "scenario_kind": "PRICE_GAP",
        "severity": "HIGH",
        "horizon_seconds": 60,
        "parameters": (_parameter(),),
    }
    values.update(updates)
    return BTCPerpetualPaperStressScenarioDefinition(**values)


def _registry(*definitions, **updates):
    values = {
        "registry_id": "btc-stress-registry-v1",
        "artifact": _artifact(),
        "complete_rule_bundle": _bundle(),
        "definitions": tuple(definitions or (_definition(),)),
        "as_of_utc": "2026-07-22T00:03:00Z",
    }
    values.update(updates)
    return BTCPerpetualPaperStressScenarioRegistry(**values)


def test_registry_preserves_exact_definition_and_fcp_0055_lineage():
    registry = _registry()
    definition = registry.definitions[0]

    assert definition.scenario_kind == "PRICE_GAP"
    assert definition.parameters[0].value == Decimal("-0.1")
    assert definition.complete_rule_bundle_hash == registry.complete_rule_bundle.snapshot_hash
    assert len(definition.definition_hash) == len(registry.registry_hash) == 64


def test_parameters_require_exact_finite_decimals():
    with pytest.raises(ValueError, match="exact decimal"):
        BTCStressScenarioParameter("gap-rate", -0.1, "ratio")
    with pytest.raises(ValueError, match="finite"):
        BTCStressScenarioParameter("gap-rate", Decimal("NaN"), "ratio")


@pytest.mark.parametrize("kind", BTC_STRESS_SCENARIO_KINDS)
def test_closed_scenario_kind_vocabulary_is_accepted(kind):
    assert _definition(scenario_kind=kind).scenario_kind == kind


def test_unknown_kind_and_severity_are_rejected():
    with pytest.raises(ValueError, match="scenario_kind"):
        _definition(scenario_kind="UNKNOWN")
    with pytest.raises(ValueError, match="severity"):
        _definition(severity="CATASTROPHIC")
    assert set(BTC_STRESS_SEVERITIES) == {"LOW", "MEDIUM", "HIGH", "EXTREME"}


@pytest.mark.parametrize("horizon", (True, 0, -1, 31_536_001))
def test_horizon_is_a_bounded_positive_integer(horizon):
    with pytest.raises(ValueError, match="horizon_seconds"):
        _definition(horizon_seconds=horizon)


def test_parameters_must_be_typed_ordered_and_unique():
    with pytest.raises(ValueError, match="typed parameters"):
        _definition(parameters=())
    with pytest.raises(ValueError, match="typed parameters"):
        _definition(parameters=("gap-rate",))
    first = _parameter("z-rate")
    second = _parameter("a-rate")
    with pytest.raises(ValueError, match="ordered and unique"):
        _definition(parameters=(first, second))
    with pytest.raises(ValueError, match="ordered and unique"):
        _definition(parameters=(first, first))


def test_registry_rejects_artifact_bundle_and_contract_lineage_mismatch():
    with pytest.raises(ValueError, match="artifact lineage"):
        _registry(_definition(artifact_id="other-artifact"))
    with pytest.raises(ValueError, match="FCP-0055"):
        _registry(_definition(complete_rule_bundle_hash="0" * 64))
    with pytest.raises(ValueError, match="contract lineage"):
        _registry(_definition(contract_id="OTHER-PERP"))


def test_registry_definitions_must_be_typed_ordered_and_unique():
    with pytest.raises(ValueError, match="typed stress scenario"):
        _registry(definitions=())
    gap = _definition()
    funding = _definition(
        name="funding-shock-v1",
        scenario_kind="FUNDING_SHOCK",
        parameters=(_parameter("funding-rate", "0.01"),),
    )
    with pytest.raises(ValueError, match="ordered and unique"):
        _registry(gap, funding)
    with pytest.raises(ValueError, match="identities must be unique"):
        _registry(
            funding,
            _definition(
                scenario_kind="PRICE_GAP",
                version_id=funding.version_id,
            ),
        )


def test_registry_rejects_future_artifact_and_rule_bundle():
    with pytest.raises(ValueError, match="evidence after as_of"):
        _registry(as_of_utc="2026-07-22T00:01:30Z")
    future_bundle = _bundle(effective_at_utc="2026-07-22T00:04:00Z")
    future_definition = _definition(
        complete_rule_bundle_hash=future_bundle.snapshot_hash,
    )
    with pytest.raises(ValueError, match="newer than stress registry"):
        _registry(future_definition, complete_rule_bundle=future_bundle)


def test_registry_rejects_authority_escalation():
    updates = (
        {"operator_review_required": False},
        {"definition_only": False},
        {"source_selected": True},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"balance_calculation_allowed": True},
        {"position_calculation_allowed": True},
        {"pnl_calculation_allowed": True},
        {"liquidation_action_allowed": True},
        {"insurance_fund_mutation_allowed": True},
        {"adl_action_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    )
    for update in updates:
        with pytest.raises(ValueError, match="only define reviewed local Paper"):
            _registry(**update)


def test_registry_rejects_authority_identity_changes():
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            _registry(**update)


def test_lookup_returns_only_registered_definition_and_fails_closed():
    registry = _registry()
    assert resolve_btc_perpetual_paper_stress_scenario_definition(
        registry,
        scenario_id="price-gap-v1",
    ).definition_hash == registry.definitions[0].definition_hash
    with pytest.raises(LookupError, match="missing or ambiguous"):
        resolve_btc_perpetual_paper_stress_scenario_definition(
            registry,
            scenario_id="missing-scenario",
        )


def test_registry_is_immutable_and_hash_is_deterministic():
    first = _registry()
    second = _registry()
    changed = _registry(_definition(severity="EXTREME"))

    assert first.registry_hash == second.registry_hash
    assert first.registry_hash != changed.registry_hash
    with pytest.raises(FrozenInstanceError):
        first.registry_id = "changed"


def test_artifact_requires_local_registered_rights_and_causal_time():
    with pytest.raises(ValueError, match="registered local rights"):
        _artifact(rights="unsafe")
    with pytest.raises(ValueError, match="observation cannot follow"):
        _artifact(
            observed_at_utc="2026-07-22T00:03:00Z",
            registered_at_utc="2026-07-22T00:02:00Z",
        )
    with pytest.raises(ValueError, match="registered and local"):
        _artifact(local_only=False)
