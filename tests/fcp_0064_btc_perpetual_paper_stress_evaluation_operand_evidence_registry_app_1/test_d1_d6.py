from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.fcp_0064_btc_perpetual_paper_stress_evaluation_operand_evidence_registry_app_1 import (
    BTCPerpetualPaperStressEvaluationOperandEvidenceObservation,
    build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry,
    resolve_btc_perpetual_paper_stress_evaluation_operand_evidence,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import LocalEventRights
from tests.fcp_0063_btc_perpetual_paper_stress_evaluation_operand_schema_registry_app_1.test_d1_d6 import (
    _snapshot as _operand_schema,
)


def _rights() -> LocalEventRights:
    return LocalEventRights("registered-local-test-v1", "paper-research", 30)


def _value(metric_id: str, role_id: str) -> Decimal:
    values = {
        "collateral-index-reference-level": (Decimal("1.00"), Decimal("0.82")),
        "funding-reference-rate": (Decimal("0.0001"), Decimal("0.0015")),
        "liquidation-distance-reference-rate": (Decimal("0.08"), Decimal("0.08")),
        "consecutive-loss-reference-count": (Decimal("4"), Decimal("4")),
        "mark-reference-price": (Decimal("65000"), Decimal("61000")),
        "resync-lag-reference-seconds": (Decimal("12"), Decimal("12")),
        "bid-ask-depth-reference-notional": (Decimal("500000"), Decimal("80000")),
        "heartbeat-age-reference-seconds": (Decimal("30"), Decimal("30")),
    }
    return values[metric_id][1 if role_id == "current" else 0]


def _observations():
    snapshot = _operand_schema()
    result = []
    for index, requirement in enumerate(snapshot.requirements):
        minute = index * 2
        result.append(
            BTCPerpetualPaperStressEvaluationOperandEvidenceObservation(
                observation_id=f"operand-observation-{index + 1:02d}",
                scenario_kind=requirement.scenario_kind,
                mode_id=requirement.mode_id,
                role_id=requirement.role_id,
                metric_id=requirement.metric_id,
                value=_value(requirement.metric_id, requirement.role_id),
                unit_id=requirement.unit_id,
                venue_id=snapshot.venue_id,
                contract_id=snapshot.contract_id,
                source_artifact_id=f"registered-operand-source-{index + 1:02d}",
                source_content_sha256=f"{index + 1:064x}",
                event_at_utc=f"2026-07-22T07:{minute:02d}:00Z",
                available_at_utc=f"2026-07-22T07:{minute + 1:02d}:00Z",
                rights=_rights(),
            )
        )
    return tuple(result)


def _registry():
    return build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
        _operand_schema(), _observations(), as_of_utc="2026-07-22T08:00:00Z"
    )


def test_exact_fcp_0063_schema_and_typed_operands_build_registry():
    registry = _registry()
    assert len(registry.observations) == 12
    assert registry.registration_only is True
    assert registry.direction_defined is False
    assert len(registry.registry_hash) == 64


def test_requires_typed_fcp_0063_evidence():
    with pytest.raises(TypeError, match="FCP-0063"):
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            "unsafe", _observations(), as_of_utc="2026-07-22T08:00:00Z"
        )


def test_resolves_one_exact_kind_role():
    item = resolve_btc_perpetual_paper_stress_evaluation_operand_evidence(
        _registry(), scenario_kind="price_gap", role_id="current"
    )
    assert item.value == Decimal("61000")


@pytest.mark.parametrize("mutation", ("missing", "extra", "reordered"))
def test_exact_schema_coverage_fails_closed(mutation):
    observations = _observations()
    if mutation == "missing":
        observations = observations[:-1]
    elif mutation == "extra":
        observations = observations + (observations[-1],)
    else:
        observations = (observations[1], observations[0]) + observations[2:]
    with pytest.raises(ValueError, match="schema exactly"):
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            _operand_schema(), observations, as_of_utc="2026-07-22T08:00:00Z"
        )


def test_duplicate_observation_identity_fails_closed():
    observations = _observations()
    duplicate = replace(observations[1], observation_id=observations[0].observation_id)
    with pytest.raises(ValueError, match="identities must be unique"):
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            _operand_schema(),
            (observations[0], duplicate) + observations[2:],
            as_of_utc="2026-07-22T08:00:00Z",
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("scenario_kind", "FUNDING_SHOCK"),
        ("mode_id", "THRESHOLD_OBSERVATION"),
        ("role_id", "current"),
        ("metric_id", "funding-reference-rate"),
        ("unit_id", "seconds"),
    ),
)
def test_cross_schema_substitution_fails_closed(field, value):
    observations = _observations()
    with pytest.raises(ValueError):
        changed = replace(observations[0], **{field: value})
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            _operand_schema(),
            (changed,) + observations[1:],
            as_of_utc="2026-07-22T08:00:00Z",
        )


def test_untyped_observation_fails_closed():
    observations = _observations()
    with pytest.raises(ValueError, match="typed operand"):
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            _operand_schema(),
            ("unsafe",) + observations[1:],
            as_of_utc="2026-07-22T08:00:00Z",
        )


def test_contract_lineage_substitution_fails_closed():
    observations = _observations()
    changed = replace(observations[0], contract_id="other-contract")
    with pytest.raises(ValueError, match="contract lineage"):
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            _operand_schema(),
            (changed,) + observations[1:],
            as_of_utc="2026-07-22T08:00:00Z",
        )


def test_future_availability_fails_closed():
    observations = _observations()
    changed = replace(observations[-1], available_at_utc="2026-07-22T08:01:00Z")
    with pytest.raises(ValueError, match="future availability"):
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            _operand_schema(),
            observations[:-1] + (changed,),
            as_of_utc="2026-07-22T08:00:00Z",
        )


def test_event_after_availability_fails_closed():
    with pytest.raises(ValueError, match="cannot follow availability"):
        replace(
            _observations()[0],
            event_at_utc="2026-07-22T07:02:00Z",
            available_at_utc="2026-07-22T07:01:00Z",
        )


def test_paired_baseline_must_strictly_precede_current():
    observations = _observations()
    changed = replace(observations[1], event_at_utc=observations[0].event_at_utc)
    with pytest.raises(ValueError, match="baseline event must precede"):
        build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
            _operand_schema(),
            (observations[0], changed) + observations[2:],
            as_of_utc="2026-07-22T08:00:00Z",
        )


@pytest.mark.parametrize(
    "index,value,message",
    (
        (0, Decimal("0"), "collateral index"),
        (4, Decimal("1.01"), "liquidation distance"),
        (5, Decimal("1.5"), "nonnegative integers"),
        (6, Decimal("0"), "price and depth"),
        (9, Decimal("-1"), "price and depth"),
    ),
)
def test_operand_value_domains_fail_closed(index, value, message):
    with pytest.raises(ValueError, match=message):
        replace(_observations()[index], value=value)


def test_binary_float_fails_closed():
    with pytest.raises(ValueError, match="exact decimal"):
        replace(_observations()[2], value=0.2)


def test_hash_is_deterministic_and_upstream_bound():
    assert _registry().registry_hash == _registry().registry_hash
    changed = build_btc_perpetual_paper_stress_evaluation_operand_evidence_registry(
        _operand_schema(),
        _observations(),
        as_of_utc="2026-07-22T08:00:00Z",
        registry_id="changed-operand-evidence-registry",
    )
    assert changed.registry_hash != _registry().registry_hash


def test_registry_rejects_authority_escalation():
    registry = _registry()
    for update in (
        {"operator_review_required": False},
        {"registration_only": False},
        {"direction_defined": True},
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
        with pytest.raises(ValueError, match="only register"):
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


def test_registry_and_observations_are_frozen():
    with pytest.raises(FrozenInstanceError):
        _registry().registry_id = "changed"
    with pytest.raises(FrozenInstanceError):
        _observations()[0].value = Decimal("2")
