"""Tests for registered scenario simulation input schemas."""

from copy import deepcopy

from fcf.sidecars.ai_scenario_simulation import (
    INPUT_SCHEMA_STAGE_ID,
    build_scenario_assumption_bundle,
    build_scenario_input_record,
    validate_scenario_assumption_bundle,
    validate_scenario_input_record,
)


def _record() -> dict:
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
        assumption_ids=["assumption-b", "assumption-a"],
        evidence_references=["evidence-b", "evidence-a"],
        risk_flags=["RISK_B", "RISK_A"],
        source_review_status="REGISTERED",
        original_conclusion_reference="conclusion-001",
    )


def _bundle() -> dict:
    return build_scenario_assumption_bundle(
        bundle_id="bundle-001",
        scenario_input_record_id="input-001",
        source_scenario_id="scenario-001",
        assumption_ids=["assumption-b", "assumption-a"],
        evidence_references=["evidence-b", "evidence-a"],
        risk_flags=["RISK_B", "RISK_A"],
        bundle_status="READY_FOR_BRANCH_CONSTRUCTION",
    )


def test_d2_stage_identity() -> None:
    assert INPUT_SCHEMA_STAGE_ID == "AI-SCENARIO-SIMULATION-D2"


def test_input_record_validation_passes() -> None:
    assert validate_scenario_input_record(_record()) == []


def test_assumption_bundle_validation_passes() -> None:
    assert validate_scenario_assumption_bundle(_bundle()) == []


def test_lists_are_canonical_and_deterministic() -> None:
    record = _record()

    assert record["assumption_ids"] == [
        "assumption-a",
        "assumption-b",
    ]
    assert record["evidence_references"] == [
        "evidence-a",
        "evidence-b",
    ]
    assert record["risk_flags"] == ["RISK_A", "RISK_B"]


def test_truth_status_remains_undetermined() -> None:
    assert _record()["truth_status"] == "UNDETERMINED"
    assert _bundle()["truth_status"] == "UNDETERMINED"


def test_operator_review_remains_required() -> None:
    assert _record()["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )
    assert _bundle()["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )


def test_input_rejects_unregistered_artifact_type() -> None:
    record = _record()
    record["source_artifact_type"] = "LIVE_MODEL_OUTPUT"

    assert "source_artifact_type_invalid" in (
        validate_scenario_input_record(record)
    )


def test_input_rejects_non_utc_timestamp() -> None:
    record = _record()
    record["registered_at_utc"] = "2026-07-11T12:00:00+08:00"

    assert "registered_at_utc_invalid" in (
        validate_scenario_input_record(record)
    )


def test_input_rejects_truth_decision() -> None:
    record = _record()
    record["truth_status"] = "CONFIRMED_TRUE"

    assert "truth_status_must_remain_undetermined" in (
        validate_scenario_input_record(record)
    )


def test_bundle_rejects_invalid_status() -> None:
    bundle = _bundle()
    bundle["bundle_status"] = "WINNING_SCENARIO"

    assert "bundle_status_invalid" in (
        validate_scenario_assumption_bundle(bundle)
    )


def test_bundle_rejects_operator_review_bypass() -> None:
    bundle = _bundle()
    bundle["operator_review_status"] = "AUTO_APPROVED"

    assert "operator_review_status_invalid" in (
        validate_scenario_assumption_bundle(bundle)
    )


def test_safety_boundary_rejects_trade_action() -> None:
    record = _record()
    record["safety_flags"]["trade_action_allowed"] = True

    assert "trade_action_allowed_must_be_false" in (
        validate_scenario_input_record(record)
    )


def test_builders_return_fresh_containers() -> None:
    first = _record()
    second = _record()
    mutated = deepcopy(first)

    mutated["assumption_ids"].append("assumption-x")
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _record()
    assert mutated != second


def test_non_mapping_values_are_rejected() -> None:
    assert validate_scenario_input_record([]) == [
        "record_must_be_mapping"
    ]
    assert validate_scenario_assumption_bundle([]) == [
        "bundle_must_be_mapping"
    ]
