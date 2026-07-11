"""Tests for final scenario simulation handoff."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_scenario_simulation import (
    build_cross_scenario_assessment,
    build_registered_consequence_record,
    build_scenario_assumption_bundle,
    build_scenario_branch_record,
    build_scenario_input_record,
    build_scenario_simulation_handoff,
    build_scenario_simulation_review_packet,
)
from fcf.sidecars.ai_scenario_simulation.handoff import (
    ScenarioHandoffViolation,
    validate_scenario_simulation_handoff,
)


def _branch(suffix: str) -> dict:
    input_record = build_scenario_input_record(
        record_id=f"input-{suffix}",
        source_scenario_id=f"scenario-{suffix}",
        source_artifact_id=f"artifact-{suffix}",
        source_artifact_type=(
            "REGISTERED_MARKET_SCENARIO_DEFINITION"
        ),
        source_artifact_version="1.0.0",
        registered_at_utc="2026-07-11T04:00:00Z",
        scenario_label=f"scenario_{suffix}",
        assumption_ids=[f"assumption-{suffix}"],
        evidence_references=[f"evidence-{suffix}"],
        risk_flags=[f"RISK_{suffix.upper()}"],
        source_review_status="REGISTERED",
        original_conclusion_reference=(
            f"conclusion-{suffix}"
        ),
    )

    bundle = build_scenario_assumption_bundle(
        bundle_id=f"bundle-{suffix}",
        scenario_input_record_id=f"input-{suffix}",
        source_scenario_id=f"scenario-{suffix}",
        assumption_ids=[f"assumption-{suffix}"],
        evidence_references=[f"evidence-{suffix}"],
        risk_flags=[f"RISK_{suffix.upper()}"],
        bundle_status="READY_FOR_BRANCH_CONSTRUCTION",
    )

    return build_scenario_branch_record(
        branch_id=f"branch-{suffix}",
        branch_label=f"branch_{suffix}",
        input_record=input_record,
        assumption_bundle=bundle,
    )


def _packet() -> dict:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[
            build_registered_consequence_record(
                consequence_id="consequence-a",
                branch_id="branch-a",
                consequence_key="market_direction",
                consequence_polarity="POSITIVE",
                evidence_references=["shared-evidence"],
                uncertainty_flags=[],
            ),
            build_registered_consequence_record(
                consequence_id="consequence-b",
                branch_id="branch-b",
                consequence_key="market_direction",
                consequence_polarity="NEGATIVE",
                evidence_references=["shared-evidence"],
                uncertainty_flags=[],
            ),
        ],
    )

    return build_scenario_simulation_review_packet(
        packet_id="packet-001",
        assessment=assessment,
    )


def _handoff() -> dict:
    return build_scenario_simulation_handoff(
        handoff_id="handoff-001",
        review_packet=_packet(),
    )


def test_handoff_validation_passes() -> None:
    assert validate_scenario_simulation_handoff(
        _handoff()
    ) == []


def test_handoff_preserves_source_references() -> None:
    handoff = _handoff()

    assert handoff["branch_ids"] == [
        "branch-a",
        "branch-b",
    ]
    assert handoff["original_conclusion_references"] == [
        "conclusion-a",
        "conclusion-b",
    ]


def test_handoff_requires_operator_and_archive_review() -> None:
    handoff = _handoff()

    assert handoff["handoff_status"] == "REVIEW_REQUIRED"
    assert handoff["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )
    assert handoff["archive_registration_required"] is True
    assert handoff["archive_execution_allowed"] is False


def test_handoff_preserves_interpretation_boundary() -> None:
    handoff = _handoff()

    assert handoff["truth_status"] == "UNDETERMINED"
    assert handoff["probability_status"] == "NOT_ASSIGNED"
    assert handoff["rank_status"] == "NOT_ASSIGNED"
    assert handoff["winner_status"] == "NOT_SELECTED"


def test_invalid_review_packet_is_rejected() -> None:
    packet = _packet()
    packet["winner_status"] = "SELECTED"

    with pytest.raises(
        ScenarioHandoffViolation,
        match="winner_must_not_be_selected",
    ):
        build_scenario_simulation_handoff(
            handoff_id="handoff-001",
            review_packet=packet,
        )


def test_validation_rejects_archive_execution() -> None:
    handoff = _handoff()
    handoff["archive_execution_allowed"] = True

    assert "archive_execution_allowed_must_be_false" in (
        validate_scenario_simulation_handoff(handoff)
    )


def test_validation_rejects_operator_bypass() -> None:
    handoff = _handoff()
    handoff["operator_review_status"] = "AUTO_APPROVED"

    assert "operator_review_status_invalid" in (
        validate_scenario_simulation_handoff(handoff)
    )


def test_validation_rejects_trade_action() -> None:
    handoff = _handoff()
    handoff["safety_flags"]["trade_action_allowed"] = True

    assert "trade_action_allowed_must_be_false" in (
        validate_scenario_simulation_handoff(handoff)
    )


def test_builder_returns_fresh_containers() -> None:
    first = _handoff()
    second = _handoff()
    mutated = deepcopy(first)

    mutated["branch_ids"].append("branch-x")
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _handoff()
    assert mutated != second


def test_non_mapping_handoff_is_rejected() -> None:
    assert validate_scenario_simulation_handoff(
        []
    ) == ["handoff_must_be_mapping"]
