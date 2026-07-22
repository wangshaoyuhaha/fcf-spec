from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.fcp_0056_btc_perpetual_paper_stress_scenario_definition_registry_app_1 import (
    BTC_STRESS_SCENARIO_KINDS,
)
from apps.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1 import (
    build_btc_perpetual_paper_stress_coverage_snapshot,
)
from apps.fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_app_1 import (
    BTC_STRESS_EVALUATION_INPUT_SCHEMA,
    BTCPerpetualPaperStressEvaluationInputObservation,
    build_btc_perpetual_paper_stress_evaluation_input_registry,
    resolve_btc_perpetual_paper_stress_evaluation_input,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights
from tests.fcp_0057_btc_perpetual_paper_stress_scenario_coverage_parameter_schema_gate_app_1.test_d1_d6 import (
    _registry as _scenario_registry,
)


def _coverage():
    return build_btc_perpetual_paper_stress_coverage_snapshot(_scenario_registry())


def _value(unit_id: str) -> Decimal:
    return {
        "count": Decimal("2"),
        "quote-notional": Decimal("1000000"),
        "quote-per-base": Decimal("50000"),
        "ratio": Decimal("0.1"),
        "seconds": Decimal("30"),
    }[unit_id]


def _observation(
    kind: str,
    *,
    suffix: str = "v1",
    metric_id: str | None = None,
    unit_id: str | None = None,
    venue_id: str = "venue-a",
    contract_id: str = "BTC-USDT-PERP",
    event_at_utc: str = "2026-07-22T00:03:00Z",
    available_at_utc: str = "2026-07-22T00:04:00Z",
    value: object | None = None,
):
    schema = {item[0]: item[1:] for item in BTC_STRESS_EVALUATION_INPUT_SCHEMA}
    expected_metric, expected_unit = schema[kind]
    actual_unit = expected_unit if unit_id is None else unit_id
    content = f"registered {kind} input {suffix}\n".encode("ascii")
    return BTCPerpetualPaperStressEvaluationInputObservation(
        observation_id=f"{kind.lower().replace('_', '-')}-input-{suffix}",
        scenario_kind=kind,
        metric_id=expected_metric if metric_id is None else metric_id,
        value=_value(actual_unit) if value is None else value,
        unit_id=actual_unit,
        venue_id=venue_id,
        contract_id=contract_id,
        source_artifact_id=f"btc-stress-inputs-{suffix}",
        source_content_sha256=hashlib.sha256(content).hexdigest(),
        event_at_utc=event_at_utc,
        available_at_utc=available_at_utc,
        rights=LocalEventRights("synthetic-test", "local-paper-research", 30),
    )


def _observations():
    return tuple(_observation(kind) for kind in BTC_STRESS_SCENARIO_KINDS)


def _registry(observations=None, *, coverage=None, as_of_utc="2026-07-22T00:05:00Z"):
    return build_btc_perpetual_paper_stress_evaluation_input_registry(
        _coverage() if coverage is None else coverage,
        _observations() if observations is None else tuple(observations),
        as_of_utc=as_of_utc,
    )


def test_complete_inputs_produce_exact_immutable_registry():
    coverage = _coverage()
    registry = _registry(coverage=coverage)

    assert registry.coverage_snapshot.snapshot_hash == coverage.snapshot_hash
    assert tuple(item.scenario_kind for item in registry.observations) == (
        BTC_STRESS_SCENARIO_KINDS
    )
    assert len(registry.registry_hash) == 64
    assert registry.registration_only is True
    assert registry.evaluation_allowed is False


def test_input_schema_matches_closed_kind_vocabulary_exactly():
    assert tuple(item[0] for item in BTC_STRESS_EVALUATION_INPUT_SCHEMA) == (
        BTC_STRESS_SCENARIO_KINDS
    )


def test_resolver_returns_one_registered_input():
    registry = _registry()
    resolved = resolve_btc_perpetual_paper_stress_evaluation_input(
        registry,
        scenario_kind="price_gap",
    )

    assert resolved.scenario_kind == "PRICE_GAP"
    assert resolved.metric_id == "mark-reference-price"


def test_missing_kind_fails_closed():
    with pytest.raises(ValueError, match="one ordered observation"):
        _registry(_observations()[:-1])


def test_duplicate_kind_fails_closed():
    observations = list(_observations())
    observations.insert(5, _observation("PRICE_GAP", suffix="v2"))
    with pytest.raises(ValueError, match="one ordered observation"):
        _registry(observations)


def test_metric_mismatch_fails_closed():
    observations = tuple(
        _observation(kind, metric_id="unsafe-metric")
        if kind == "PRICE_GAP"
        else _observation(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    )
    with pytest.raises(ValueError, match="metric schema mismatch"):
        _registry(observations)


def test_unit_mismatch_fails_closed():
    observations = tuple(
        _observation(kind, unit_id="ratio")
        if kind == "PRICE_GAP"
        else _observation(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    )
    with pytest.raises(ValueError, match="metric schema mismatch"):
        _registry(observations)


def test_future_availability_fails_closed():
    observations = tuple(
        _observation(kind, available_at_utc="2026-07-22T00:06:00Z")
        if kind == "PRICE_GAP"
        else _observation(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    )
    with pytest.raises(ValueError, match="future availability"):
        _registry(observations)


def test_event_after_availability_is_rejected():
    with pytest.raises(ValueError, match="event cannot follow availability"):
        _observation(
            "PRICE_GAP",
            event_at_utc="2026-07-22T00:05:00Z",
            available_at_utc="2026-07-22T00:04:00Z",
        )


def test_contract_lineage_mismatch_fails_closed():
    observations = tuple(
        _observation(kind, venue_id="venue-b")
        if kind == "PRICE_GAP"
        else _observation(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    )
    with pytest.raises(ValueError, match="contract lineage mismatch"):
        _registry(observations)


def test_registry_requires_typed_fcp_0057_coverage():
    with pytest.raises(TypeError, match="typed FCP-0057"):
        build_btc_perpetual_paper_stress_evaluation_input_registry(
            "unsafe",
            _observations(),
            as_of_utc="2026-07-22T00:05:00Z",
        )


def test_registry_requires_typed_observations():
    with pytest.raises(ValueError, match="typed evaluation input observations"):
        _registry(("unsafe",))


def test_binary_float_input_is_rejected():
    with pytest.raises(ValueError, match="exact decimal"):
        _observation("PRICE_GAP", value=50000.0)


def test_signed_funding_reference_is_preserved_exactly():
    observations = tuple(
        _observation(kind, value=Decimal("-0.0001"))
        if kind == "FUNDING_SHOCK"
        else _observation(kind)
        for kind in BTC_STRESS_SCENARIO_KINDS
    )
    registry = _registry(observations)

    funding = resolve_btc_perpetual_paper_stress_evaluation_input(
        registry,
        scenario_kind="FUNDING_SHOCK",
    )
    assert funding.value == Decimal("-0.0001")


def test_registry_hash_is_deterministic_and_evidence_bound():
    first = _registry()
    second = _registry()
    changed = _registry(
        tuple(
            _observation(kind, suffix="v2") for kind in BTC_STRESS_SCENARIO_KINDS
        )
    )

    assert first.registry_hash == second.registry_hash
    assert first.registry_hash != changed.registry_hash


def test_registry_rejects_authority_escalation():
    registry = _registry()
    for update in (
        {"operator_review_required": False},
        {"registration_only": False},
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
    ):
        with pytest.raises(ValueError, match="only register reviewed"):
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


def test_registry_and_observation_are_frozen():
    registry = _registry()
    with pytest.raises(FrozenInstanceError):
        registry.registry_id = "changed"
    with pytest.raises(FrozenInstanceError):
        registry.observations[0].metric_id = "changed"
