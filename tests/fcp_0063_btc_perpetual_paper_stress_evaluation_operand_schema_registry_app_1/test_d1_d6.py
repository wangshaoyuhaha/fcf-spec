from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0063_btc_perpetual_paper_stress_evaluation_operand_schema_registry_app_1 import (
    BTC_STRESS_EVALUATION_OPERAND_SCHEMA,
    BTCPerpetualPaperStressEvaluationOperandRequirement,
    build_btc_perpetual_paper_stress_evaluation_operand_schema_snapshot,
)
from tests.fcp_0062_btc_perpetual_paper_stress_evaluation_readiness_parameter_domain_coherence_hardening_app_1.test_d1_d6 import (
    _snapshot as _extended_readiness,
)


def _snapshot():
    return build_btc_perpetual_paper_stress_evaluation_operand_schema_snapshot(
        _extended_readiness()
    )


def test_exact_fcp_0062_evidence_produces_operand_schema():
    extended = _extended_readiness()
    snapshot = build_btc_perpetual_paper_stress_evaluation_operand_schema_snapshot(extended)
    assert snapshot.extended_readiness_snapshot_hash == extended.snapshot_hash
    assert snapshot.schema_only is True
    assert snapshot.direction_defined is False
    assert len(snapshot.snapshot_hash) == 64


def test_requires_typed_fcp_0062_evidence():
    with pytest.raises(TypeError, match="FCP-0062"):
        build_btc_perpetual_paper_stress_evaluation_operand_schema_snapshot("unsafe")


def test_closed_schema_covers_every_scenario_kind_once():
    snapshot = _snapshot()
    assert tuple(item[0] for item in BTC_STRESS_EVALUATION_OPERAND_SCHEMA) == snapshot.scenario_kinds


def test_paired_scenarios_require_baseline_then_current():
    paired = {
        kind: tuple(role for role, _, _ in operands)
        for kind, mode, operands in BTC_STRESS_EVALUATION_OPERAND_SCHEMA
        if mode == "PAIRED_BASELINE_CURRENT"
    }
    assert paired == {
        "COLLATERAL_DRAWDOWN": ("baseline", "current"),
        "FUNDING_SHOCK": ("baseline", "current"),
        "PRICE_GAP": ("baseline", "current"),
        "THIN_BOOK": ("baseline", "current"),
    }


def test_threshold_scenarios_require_one_observation():
    threshold = {
        kind: tuple(role for role, _, _ in operands)
        for kind, mode, operands in BTC_STRESS_EVALUATION_OPERAND_SCHEMA
        if mode == "THRESHOLD_OBSERVATION"
    }
    assert threshold == {
        "LIQUIDATION_DISTANCE": ("observed",),
        "LOSS_STREAK": ("observed",),
        "RESYNC": ("observed",),
        "VENUE_OUTAGE": ("observed",),
    }


def test_requirements_preserve_fcp_0058_metric_units():
    assert {(item.metric_id, item.unit_id) for item in _snapshot().requirements} == {
        ("bid-ask-depth-reference-notional", "quote-notional"),
        ("collateral-index-reference-level", "ratio"),
        ("consecutive-loss-reference-count", "count"),
        ("funding-reference-rate", "ratio"),
        ("heartbeat-age-reference-seconds", "seconds"),
        ("liquidation-distance-reference-rate", "ratio"),
        ("mark-reference-price", "quote-per-base"),
        ("resync-lag-reference-seconds", "seconds"),
    }


def test_unregistered_mode_fails_closed():
    with pytest.raises(ValueError, match="mode_id is not registered"):
        BTCPerpetualPaperStressEvaluationOperandRequirement(
            "PRICE_GAP", "UNKNOWN", "baseline", "mark-reference-price", "quote-per-base"
        )


def test_missing_requirement_fails_closed():
    snapshot = _snapshot()
    with pytest.raises(ValueError, match="closed schema exactly"):
        replace(snapshot, requirements=snapshot.requirements[:-1])


def test_extra_requirement_fails_closed():
    snapshot = _snapshot()
    with pytest.raises(ValueError, match="closed schema exactly"):
        replace(snapshot, requirements=snapshot.requirements + (snapshot.requirements[-1],))


def test_cross_kind_requirement_fails_closed():
    snapshot = _snapshot()
    changed = replace(snapshot.requirements[0], scenario_kind="FUNDING_SHOCK")
    with pytest.raises(ValueError, match="closed schema exactly"):
        replace(snapshot, requirements=(changed,) + snapshot.requirements[1:])


def test_untyped_requirement_fails_closed():
    snapshot = _snapshot()
    with pytest.raises(ValueError, match="typed requirements"):
        replace(snapshot, requirements=("unsafe",) + snapshot.requirements[1:])


def test_schema_hash_substitution_fails_closed():
    with pytest.raises(ValueError, match="does not match"):
        replace(_snapshot(), operand_schema_hash="f" * 64)


def test_hash_is_deterministic_and_upstream_bound():
    assert _snapshot().snapshot_hash == _snapshot().snapshot_hash
    changed = build_btc_perpetual_paper_stress_evaluation_operand_schema_snapshot(
        _extended_readiness(), registry_id="changed-operand-schema"
    )
    assert _snapshot().snapshot_hash != changed.snapshot_hash


def test_snapshot_rejects_authority_escalation():
    snapshot = _snapshot()
    for update in (
        {"operator_review_required": False},
        {"schema_only": False},
        {"direction_defined": True},
        {"evaluation_allowed": True},
        {"calculation_allowed": True},
        {"account_state_allowed": True},
        {"execution_allowed": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot direct, evaluate, calculate"):
            replace(snapshot, **update)


def test_snapshot_rejects_authority_identity_changes():
    snapshot = _snapshot()
    for update in (
        {"calculation_authority": "AI"},
        {"evidence_authority": "UNREGISTERED"},
        {"ai_role": "AUTHORITATIVE"},
    ):
        with pytest.raises(ValueError, match="authority identities"):
            replace(snapshot, **update)


def test_snapshot_is_frozen():
    snapshot = _snapshot()
    with pytest.raises(FrozenInstanceError):
        snapshot.registry_id = "changed"
