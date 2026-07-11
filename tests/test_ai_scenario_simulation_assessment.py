"""Tests for deterministic cross-scenario assessment."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_scenario_simulation import (
    ScenarioAssessmentViolation,
    build_cross_scenario_assessment,
    build_registered_consequence_record,
    build_scenario_assumption_bundle,
    build_scenario_branch_record,
    build_scenario_input_record,
    validate_cross_scenario_assessment,
    validate_registered_consequence_record,
)


def _input(
    suffix: str,
    source_review_status: str = "REGISTERED",
) -> dict:
    return build_scenario_input_record(
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
        source_review_status=source_review_status,
        original_conclusion_reference=(
            f"conclusion-{suffix}"
        ),
    )


def _bundle(
    suffix: str,
    bundle_status: str = "READY_FOR_BRANCH_CONSTRUCTION",
) -> dict:
    return build_scenario_assumption_bundle(
        bundle_id=f"bundle-{suffix}",
        scenario_input_record_id=f"input-{suffix}",
        source_scenario_id=f"scenario-{suffix}",
        assumption_ids=[f"assumption-{suffix}"],
        evidence_references=[f"evidence-{suffix}"],
        risk_flags=[f"RISK_{suffix.upper()}"],
        bundle_status=bundle_status,
    )


def _branch(
    suffix: str,
    source_review_status: str = "REGISTERED",
    bundle_status: str = "READY_FOR_BRANCH_CONSTRUCTION",
) -> dict:
    return build_scenario_branch_record(
        branch_id=f"branch-{suffix}",
        branch_label=f"branch_{suffix}",
        input_record=_input(
            suffix,
            source_review_status,
        ),
        assumption_bundle=_bundle(
            suffix,
            bundle_status,
        ),
    )


def _consequence(
    suffix: str,
    polarity: str,
    evidence: list[str],
    uncertainty: list[str] | None = None,
    consequence_key: str = "market_direction",
) -> dict:
    return build_registered_consequence_record(
        consequence_id=f"consequence-{suffix}",
        branch_id=f"branch-{suffix}",
        consequence_key=consequence_key,
        consequence_polarity=polarity,
        evidence_references=evidence,
        uncertainty_flags=uncertainty or [],
    )


def test_registered_consequence_validation_passes() -> None:
    record = _consequence(
        "a",
        "POSITIVE",
        ["shared-evidence"],
    )

    assert validate_registered_consequence_record(
        record
    ) == []


def test_cross_scenario_assessment_detects_contradiction() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[
            _consequence(
                "a",
                "POSITIVE",
                ["shared-evidence"],
            ),
            _consequence(
                "b",
                "NEGATIVE",
                ["shared-evidence"],
            ),
        ],
    )

    assert assessment["summary"]["contradiction_count"] == 1
    assert assessment["assessment_status"] == (
        "REVIEW_REQUIRED"
    )
    assert "EXPLICIT_POLARITY_CONTRADICTION" in (
        assessment["reason_codes"]
    )


def test_shared_evidence_is_preserved() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[
            _consequence(
                "a",
                "POSITIVE",
                ["shared-evidence"],
            ),
            _consequence(
                "b",
                "NEGATIVE",
                ["shared-evidence"],
            ),
        ],
    )

    item = assessment["comparison_items"][0]

    assert item["shared_evidence_references"] == [
        "shared-evidence"
    ]


def test_uncertainty_is_detected() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[
            _consequence(
                "a",
                "UNKNOWN",
                ["evidence-a"],
                ["TIMING_UNCERTAIN"],
            ),
            _consequence(
                "b",
                "NEUTRAL",
                ["evidence-b"],
            ),
        ],
    )

    assert assessment["summary"]["uncertainty_count"] == 1
    assert "UNCERTAINTY_REGISTERED" in (
        assessment["reason_codes"]
    )


def test_missing_evidence_is_detected() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[
            _consequence("a", "POSITIVE", []),
            _consequence(
                "b",
                "POSITIVE",
                ["evidence-b"],
            ),
        ],
    )

    item = assessment["comparison_items"][0]

    assert item["missing_evidence_branch_ids"] == [
        "branch-a"
    ]
    assert assessment["summary"]["evidence_gap_count"] == 1


def test_missing_branch_coverage_is_detected() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[
            _consequence(
                "a",
                "POSITIVE",
                ["evidence-a"],
            )
        ],
    )

    item = assessment["comparison_items"][0]

    assert item["missing_branch_coverage_ids"] == [
        "branch-b"
    ]
    assert assessment["summary"]["coverage_gap_count"] == 1


def test_no_consequences_requires_review() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[],
    )

    assert assessment["reason_codes"] == [
        "NO_REGISTERED_CONSEQUENCES"
    ]
    assert assessment["assessment_status"] == (
        "REVIEW_REQUIRED"
    )


def test_clean_registered_comparison_is_ready() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[
            _consequence(
                "a",
                "NEUTRAL",
                ["shared-evidence"],
            ),
            _consequence(
                "b",
                "NEUTRAL",
                ["shared-evidence"],
            ),
        ],
    )

    assert assessment["assessment_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )


def test_blocked_branch_blocks_assessment() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[
            _branch(
                "a",
                source_review_status="BLOCKED",
            ),
            _branch("b"),
        ],
        consequence_records=[],
    )

    assert assessment["assessment_status"] == "BLOCKED"


def test_truth_probability_rank_and_winner_remain_unset() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[],
    )

    assert assessment["truth_status"] == "UNDETERMINED"
    assert assessment["probability_status"] == "NOT_ASSIGNED"
    assert assessment["rank_status"] == "NOT_ASSIGNED"
    assert assessment["winner_status"] == "NOT_SELECTED"


def test_unknown_branch_reference_is_rejected() -> None:
    record = _consequence(
        "a",
        "POSITIVE",
        ["evidence-a"],
    )
    record["branch_id"] = "branch-unknown"

    with pytest.raises(
        ScenarioAssessmentViolation,
        match="unknown_branch_id",
    ):
        build_cross_scenario_assessment(
            assessment_id="assessment-001",
            branch_records=[_branch("a"), _branch("b")],
            consequence_records=[record],
        )


def test_duplicate_branch_id_is_rejected() -> None:
    branch = _branch("a")

    with pytest.raises(
        ScenarioAssessmentViolation,
        match="duplicate_branch_id",
    ):
        build_cross_scenario_assessment(
            assessment_id="assessment-001",
            branch_records=[branch, deepcopy(branch)],
            consequence_records=[],
        )


def test_at_least_two_branches_are_required() -> None:
    with pytest.raises(
        ScenarioAssessmentViolation,
        match="at_least_two_branches_required",
    ):
        build_cross_scenario_assessment(
            assessment_id="assessment-001",
            branch_records=[_branch("a")],
            consequence_records=[],
        )


def test_assessment_validation_passes() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[],
    )

    assert validate_cross_scenario_assessment(
        assessment
    ) == []


def test_validation_rejects_winner_selection() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[],
    )
    assessment["winner_status"] = "SELECTED"

    assert "winner_must_not_be_selected" in (
        validate_cross_scenario_assessment(assessment)
    )


def test_validation_rejects_trade_action() -> None:
    assessment = build_cross_scenario_assessment(
        assessment_id="assessment-001",
        branch_records=[_branch("a"), _branch("b")],
        consequence_records=[],
    )
    assessment["safety_flags"]["trade_action_allowed"] = True

    assert "trade_action_allowed_must_be_false" in (
        validate_cross_scenario_assessment(assessment)
    )
