"""Tests for deterministic scenario branch construction."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_scenario_simulation import (
    ScenarioBranchViolation,
    build_scenario_assumption_bundle,
    build_scenario_branch_record,
    build_scenario_input_record,
    validate_scenario_branch_record,
)


def _input(
    source_review_status: str = "REGISTERED",
) -> dict:
    return build_scenario_input_record(
        record_id="input-001",
        source_scenario_id="scenario-001",
        source_artifact_id="artifact-001",
        source_artifact_type=(
            "REGISTERED_MARKET_SCENARIO_DEFINITION"
        ),
        source_artifact_version="1.0.0",
        registered_at_utc="2026-07-11T04:00:00Z",
        scenario_label="registered_base_case",
        assumption_ids=["assumption-b"],
        evidence_references=["evidence-b"],
        risk_flags=["RISK_B"],
        source_review_status=source_review_status,
        original_conclusion_reference="conclusion-001",
    )


def _bundle(
    bundle_status: str = "READY_FOR_BRANCH_CONSTRUCTION",
) -> dict:
    return build_scenario_assumption_bundle(
        bundle_id="bundle-001",
        scenario_input_record_id="input-001",
        source_scenario_id="scenario-001",
        assumption_ids=["assumption-a"],
        evidence_references=["evidence-a"],
        risk_flags=["RISK_A"],
        bundle_status=bundle_status,
    )


def _branch(
    source_review_status: str = "REGISTERED",
    bundle_status: str = "READY_FOR_BRANCH_CONSTRUCTION",
) -> dict:
    return build_scenario_branch_record(
        branch_id="branch-001",
        branch_label="registered_branch_a",
        input_record=_input(source_review_status),
        assumption_bundle=_bundle(bundle_status),
    )


def test_valid_branch_passes_validation() -> None:
    assert validate_scenario_branch_record(_branch()) == []


def test_branch_merges_registered_metadata() -> None:
    branch = _branch()

    assert branch["assumption_ids"] == [
        "assumption-a",
        "assumption-b",
    ]
    assert branch["evidence_references"] == [
        "evidence-a",
        "evidence-b",
    ]
    assert branch["risk_flags"] == ["RISK_A", "RISK_B"]


def test_branch_does_not_assign_probability_or_rank() -> None:
    branch = _branch()

    assert branch["truth_status"] == "UNDETERMINED"
    assert branch["probability_status"] == "NOT_ASSIGNED"
    assert branch["rank_status"] == "NOT_ASSIGNED"
    assert branch["winner_status"] == "NOT_SELECTED"


def test_ready_sources_create_assessment_ready_branch() -> None:
    assert _branch()["branch_status"] == (
        "READY_FOR_ASSESSMENT"
    )


def test_blocked_source_blocks_branch() -> None:
    assert _branch(
        source_review_status="BLOCKED"
    )["branch_status"] == "BLOCKED"


def test_blocked_bundle_blocks_branch() -> None:
    assert _branch(
        bundle_status="BLOCKED"
    )["branch_status"] == "BLOCKED"


def test_archived_source_archives_branch() -> None:
    assert _branch(
        source_review_status="ARCHIVED"
    )["branch_status"] == "ARCHIVED"


def test_mismatched_input_link_is_rejected() -> None:
    bundle = _bundle()
    bundle["scenario_input_record_id"] = "input-999"

    with pytest.raises(
        ScenarioBranchViolation,
        match="scenario_input_record_link_mismatch",
    ):
        build_scenario_branch_record(
            branch_id="branch-001",
            branch_label="registered_branch_a",
            input_record=_input(),
            assumption_bundle=bundle,
        )


def test_mismatched_scenario_link_is_rejected() -> None:
    bundle = _bundle()
    bundle["source_scenario_id"] = "scenario-999"

    with pytest.raises(
        ScenarioBranchViolation,
        match="source_scenario_link_mismatch",
    ):
        build_scenario_branch_record(
            branch_id="branch-001",
            branch_label="registered_branch_a",
            input_record=_input(),
            assumption_bundle=bundle,
        )


def test_validation_rejects_probability_assignment() -> None:
    branch = _branch()
    branch["probability_status"] = "0.70"

    assert "probability_must_not_be_assigned" in (
        validate_scenario_branch_record(branch)
    )


def test_validation_rejects_winner_selection() -> None:
    branch = _branch()
    branch["winner_status"] = "SELECTED"

    assert "winner_must_not_be_selected" in (
        validate_scenario_branch_record(branch)
    )


def test_validation_rejects_trade_action() -> None:
    branch = _branch()
    branch["safety_flags"]["trade_action_allowed"] = True

    assert "trade_action_allowed_must_be_false" in (
        validate_scenario_branch_record(branch)
    )


def test_builder_returns_fresh_containers() -> None:
    first = _branch()
    second = _branch()
    mutated = deepcopy(first)

    mutated["assumption_ids"].append("assumption-x")
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _branch()
    assert mutated != second


def test_non_mapping_branch_is_rejected() -> None:
    assert validate_scenario_branch_record([]) == [
        "branch_must_be_mapping"
    ]
