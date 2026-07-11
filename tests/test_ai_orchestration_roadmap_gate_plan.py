"""Tests for planning-only gate and failure controls."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_roadmap import (
    ALLOWED_INPUTS,
    RETRY_POLICY,
    TIMEOUT_POLICY,
    GatePlanViolation,
    build_deterministic_governance_dag_plan,
    build_governance_gate_plan,
    build_registered_artifact_dependency_plan,
    build_registered_artifact_reference,
    validate_governance_gate_plan,
)


def _artifact_plan() -> dict:
    references = [
        build_registered_artifact_reference(
            artifact_id=f"artifact-{index:02d}",
            artifact_type=artifact_type,
            artifact_version=f"1.0.{index}",
            registration_status="REGISTERED",
            dependency_role="GOVERNANCE_EVIDENCE",
            correlation_id="correlation-001",
            research_run_id="research-run-001",
            version_pin_status="PINNED",
        )
        for index, artifact_type in enumerate(
            ALLOWED_INPUTS,
            start=1,
        )
    ]

    return build_registered_artifact_dependency_plan(
        plan_id="artifact-plan-001",
        artifact_references=references,
    )


def _dag_plan() -> dict:
    return build_deterministic_governance_dag_plan(
        dag_plan_id="dag-plan-001",
        artifact_plan=_artifact_plan(),
    )


def _gate_plan(
    failures: dict[str, str] | None = None,
) -> dict:
    return build_governance_gate_plan(
        gate_plan_id="gate-plan-001",
        dag_plan=_dag_plan(),
        registered_failure_states=failures,
    )


def test_clean_gate_plan_is_ready_for_role_planning() -> None:
    plan = _gate_plan()

    assert plan["gate_plan_status"] == (
        "READY_FOR_ROLE_PLANNING"
    )
    assert plan["reason_codes"] == [
        "NO_REGISTERED_FAILURE"
    ]


def test_gate_plan_validation_passes() -> None:
    assert validate_governance_gate_plan(
        _gate_plan()
    ) == []


def test_every_dag_edge_has_one_gate() -> None:
    dag_plan = _dag_plan()
    gate_plan = _gate_plan()

    assert len(gate_plan["gates"]) == len(
        dag_plan["edges"]
    )
    assert {
        gate["edge_id"]
        for gate in gate_plan["gates"]
    } == {
        edge["edge_id"]
        for edge in dag_plan["edges"]
    }


def test_every_gate_is_blocking_and_operator_reviewed() -> None:
    plan = _gate_plan()

    assert all(
        gate["blocking"] is True
        for gate in plan["gates"]
    )
    assert all(
        gate["operator_review_status"]
        == "REVIEW_REQUIRED"
        for gate in plan["gates"]
    )


def test_automatic_retry_is_never_planned() -> None:
    plan = _gate_plan()

    assert all(
        gate["retry_policy"] == RETRY_POLICY
        for gate in plan["gates"]
    )


def test_timeout_policy_requires_manual_review() -> None:
    plan = _gate_plan()

    assert all(
        gate["timeout_policy"] == TIMEOUT_POLICY
        for gate in plan["gates"]
    )


def test_registered_timeout_requires_review_hold() -> None:
    edge_id = _dag_plan()["edges"][0]["edge_id"]
    plan = _gate_plan(
        {edge_id: "TIMEOUT_RECORDED"}
    )

    gate = next(
        item
        for item in plan["gates"]
        if item["edge_id"] == edge_id
    )

    assert plan["gate_plan_status"] == "REVIEW_REQUIRED"
    assert gate["gate_status"] == "REVIEW_REQUIRED"
    assert gate["degradation_policy"] == (
        "READ_ONLY_REVIEW_HOLD"
    )


def test_validation_failure_stops_progression() -> None:
    edge_id = _dag_plan()["edges"][0]["edge_id"]
    plan = _gate_plan(
        {edge_id: "VALIDATION_FAILED"}
    )

    gate = next(
        item
        for item in plan["gates"]
        if item["edge_id"] == edge_id
    )

    assert gate["gate_status"] == "BLOCKED"
    assert gate["degradation_policy"] == "STOP_AND_HOLD"


def test_unknown_failure_edge_is_rejected() -> None:
    with pytest.raises(
        GatePlanViolation,
        match="unknown_failure_edge_ids",
    ):
        _gate_plan(
            {"edge-unknown": "TIMEOUT_RECORDED"}
        )


def test_invalid_failure_state_is_rejected() -> None:
    edge_id = _dag_plan()["edges"][0]["edge_id"]

    with pytest.raises(
        GatePlanViolation,
        match="failure_state_invalid",
    ):
        _gate_plan({edge_id: "AUTO_RETRY"})


def test_validation_rejects_automatic_retry() -> None:
    plan = _gate_plan()
    plan["gates"][0]["retry_policy"] = "AUTOMATIC_RETRY"

    errors = validate_governance_gate_plan(plan)

    assert any(
        "automatic_retry_must_not_be_allowed" in error
        for error in errors
    )


def test_runtime_execution_remains_forbidden() -> None:
    plan = _gate_plan()
    plan["runtime_execution_status"] = "ALLOWED"

    assert "runtime_execution_must_not_be_allowed" in (
        validate_governance_gate_plan(plan)
    )


def test_prompt_execution_remains_forbidden() -> None:
    plan = _gate_plan()
    plan["safety_flags"]["prompt_execution_allowed"] = True

    assert "prompt_execution_allowed_must_be_false" in (
        validate_governance_gate_plan(plan)
    )


def test_builder_returns_fresh_containers() -> None:
    first = _gate_plan()
    second = _gate_plan()
    mutated = deepcopy(first)

    mutated["gates"][0]["gate_status"] = "EXECUTING"
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _gate_plan()
    assert mutated != second


def test_non_mapping_gate_plan_is_rejected() -> None:
    assert validate_governance_gate_plan(
        []
    ) == ["gate_plan_must_be_mapping"]
