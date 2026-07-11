"""Tests for scenario simulation operator review packets."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_scenario_simulation import (
    ScenarioReviewPacketViolation,
    build_cross_scenario_assessment,
    build_registered_consequence_record,
    build_scenario_assumption_bundle,
    build_scenario_branch_record,
    build_scenario_input_record,
    build_scenario_simulation_review_packet,
    validate_scenario_simulation_review_packet,
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


def _assessment(
    polarity_a: str = "POSITIVE",
    polarity_b: str = "NEGATIVE",
    evidence_a: list[str] | None = None,
    evidence_b: list[str] | None = None,
    uncertainty_a: list[str] | None = None,
) -> dict:
    consequences = [
        build_registered_consequence_record(
            consequence_id="consequence-a",
            branch_id="branch-a",
            consequence_key="market_direction",
            consequence_polarity=polarity_a,
            evidence_references=(
                ["shared-evidence"]
                if evidence_a is None
                else evidence_a
            ),
            uncertainty_flags=uncertainty_a or [],
        ),
        build_registered_consequence_record(
            consequence_id="consequence-b",
            branch_id="branch-b",
            consequence_key="market_direction",
            consequence_polarity=polarity_b,
            evidence_references=(
                ["shared-evidence"]
                if evidence_b is None
                else evidence_b
            ),
            uncertainty_flags=[],
        ),
    ]

    return build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=consequences,
    )


def _packet(assessment: dict | None = None) -> dict:
    return build_scenario_simulation_review_packet(
        packet_id="packet-001",
        assessment=assessment or _assessment(),
    )


def test_review_packet_validation_passes() -> None:
    assert validate_scenario_simulation_review_packet(
        _packet()
    ) == []


def test_contradiction_creates_high_priority_review() -> None:
    packet = _packet()

    assert packet["packet_status"] == "REVIEW_REQUIRED"
    assert packet["review_priority"] == "HIGH"
    assert len(packet["contradiction_items"]) == 1


def test_uncertainty_creates_medium_priority_review() -> None:
    packet = _packet(
        _assessment(
            polarity_a="UNKNOWN",
            polarity_b="NEUTRAL",
            uncertainty_a=["TIMING_UNCERTAIN"],
        )
    )

    assert packet["review_priority"] == "MEDIUM"
    assert len(packet["uncertainty_items"]) == 1


def test_evidence_gap_is_preserved() -> None:
    packet = _packet(
        _assessment(
            polarity_a="NEUTRAL",
            polarity_b="NEUTRAL",
            evidence_a=[],
            evidence_b=["evidence-b"],
        )
    )

    assert len(packet["evidence_gap_items"]) == 1
    assert packet["review_priority"] == "MEDIUM"


def test_clean_packet_is_ready_for_operator_review() -> None:
    packet = _packet(
        _assessment(
            polarity_a="NEUTRAL",
            polarity_b="NEUTRAL",
        )
    )

    assert packet["packet_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["review_priority"] == "STANDARD"


def test_truth_probability_rank_and_winner_remain_unset() -> None:
    packet = _packet()

    assert packet["truth_status"] == "UNDETERMINED"
    assert packet["probability_status"] == "NOT_ASSIGNED"
    assert packet["rank_status"] == "NOT_ASSIGNED"
    assert packet["winner_status"] == "NOT_SELECTED"


def test_original_conclusions_are_preserved() -> None:
    packet = _packet()

    assert packet["original_conclusion_references"] == [
        "conclusion-a",
        "conclusion-b",
    ]


def test_invalid_assessment_is_rejected() -> None:
    assessment = _assessment()
    assessment["winner_status"] = "SELECTED"

    with pytest.raises(
        ScenarioReviewPacketViolation,
        match="winner_must_not_be_selected",
    ):
        _packet(assessment)


def test_validation_rejects_auto_approval() -> None:
    packet = _packet()
    packet["operator_review_status"] = "AUTO_APPROVED"

    assert "operator_review_status_invalid" in (
        validate_scenario_simulation_review_packet(
            packet
        )
    )


def test_validation_rejects_trade_action() -> None:
    packet = _packet()
    packet["safety_flags"]["trade_action_allowed"] = True

    assert "trade_action_allowed_must_be_false" in (
        validate_scenario_simulation_review_packet(
            packet
        )
    )


def test_builder_returns_fresh_containers() -> None:
    first = _packet()
    second = _packet()
    mutated = deepcopy(first)

    mutated["branch_ids"].append("branch-x")
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _packet()
    assert mutated != second


def test_non_mapping_packet_is_rejected() -> None:
    assert validate_scenario_simulation_review_packet(
        []
    ) == ["packet_must_be_mapping"]
