"""Tests for roadmap review packets and operator handoffs."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_roadmap import (
    ALLOWED_INPUTS,
    RoadmapHandoffViolation,
    build_deterministic_governance_dag_plan,
    build_governance_gate_plan,
    build_registered_artifact_dependency_plan,
    build_registered_artifact_reference,
    build_roadmap_operator_handoff,
    build_roadmap_review_packet,
    build_role_responsibility_plan,
    validate_roadmap_operator_handoff,
    validate_roadmap_review_packet,
)


def _artifact_plan(blocked: bool = False) -> dict:
    references = [
        build_registered_artifact_reference(
            artifact_id=f"artifact-{index:02d}",
            artifact_type=artifact_type,
            artifact_version=f"1.0.{index}",
            registration_status=(
                "BLOCKED"
                if blocked and index == 1
                else "REGISTERED"
            ),
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


def _dag_plan(blocked: bool = False) -> dict:
    return build_deterministic_governance_dag_plan(
        dag_plan_id="dag-plan-001",
        artifact_plan=_artifact_plan(blocked),
    )


def _gate_plan(
    failures: dict[str, str] | None = None,
    blocked: bool = False,
) -> dict:
    return build_governance_gate_plan(
        gate_plan_id="gate-plan-001",
        dag_plan=_dag_plan(blocked),
        registered_failure_states=failures,
    )


def _role_plan(
    failures: dict[str, str] | None = None,
    blocked: bool = False,
) -> dict:
    return build_role_responsibility_plan(
        role_plan_id="role-plan-001",
        gate_plan=_gate_plan(failures, blocked),
    )


def _packet(
    role_plan: dict | None = None,
) -> dict:
    return build_roadmap_review_packet(
        packet_id="roadmap-packet-001",
        role_plan=role_plan or _role_plan(),
    )


def _handoff(
    packet: dict | None = None,
) -> dict:
    return build_roadmap_operator_handoff(
        handoff_id="roadmap-handoff-001",
        review_packet=packet or _packet(),
    )


def test_review_packet_validation_passes() -> None:
    assert validate_roadmap_review_packet(
        _packet()
    ) == []


def test_operator_handoff_validation_passes() -> None:
    assert validate_roadmap_operator_handoff(
        _handoff()
    ) == []


def test_ready_role_plan_is_ready_for_operator_review() -> None:
    packet = _packet()

    assert packet["packet_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["review_priority"] == "STANDARD"


def test_timeout_requires_high_priority_review() -> None:
    edge_id = _dag_plan()["edges"][0]["edge_id"]
    packet = _packet(
        _role_plan(
            {edge_id: "TIMEOUT_RECORDED"}
        )
    )

    assert packet["packet_status"] == "REVIEW_REQUIRED"
    assert packet["review_priority"] == "HIGH"


def test_blocked_plan_creates_critical_packet() -> None:
    packet = _packet(_role_plan(blocked=True))

    assert packet["packet_status"] == "BLOCKED"
    assert packet["review_priority"] == "CRITICAL"


def test_review_summary_preserves_role_counts() -> None:
    packet = _packet()
    summary = packet["review_summary"]

    assert summary["role_count"] == len(
        packet["role_ids"]
    )
    assert summary["human_operator_role_count"] == 1
    assert summary["planned_ai_role_count"] == (
        summary["role_count"] - 1
    )
    assert summary["planned_output_count"] == len(
        packet["planned_output_artifact_types"]
    )


def test_runtime_implementation_is_not_authorized() -> None:
    packet = _packet()

    assert packet[
        "runtime_implementation_authorized"
    ] is False
    assert packet["runtime_orchestrator_status"] == (
        "NOT_CREATED"
    )
    assert packet["runtime_execution_status"] == (
        "NOT_ALLOWED"
    )


def test_handoff_requires_separate_future_approval() -> None:
    handoff = _handoff()

    assert handoff[
        "separate_architecture_review_required"
    ] is True
    assert handoff[
        "separate_operator_approval_required"
    ] is True
    assert handoff[
        "future_runtime_implementation_status"
    ] == "NOT_AUTHORIZED"
    assert handoff["next_phase_status"] == "NOT_SELECTED"


def test_invalid_role_plan_is_rejected() -> None:
    role_plan = _role_plan()
    role_plan["automatic_route_selection_status"] = (
        "ALLOWED"
    )

    with pytest.raises(
        RoadmapHandoffViolation,
        match=(
            "automatic_route_selection_status_"
            "must_be_not_allowed"
        ),
    ):
        _packet(role_plan)


def test_packet_validation_rejects_runtime_authorization() -> None:
    packet = _packet()
    packet["runtime_implementation_authorized"] = True

    assert (
        "runtime_implementation_authorized_must_be_false"
        in validate_roadmap_review_packet(packet)
    )


def test_packet_validation_rejects_automatic_routing() -> None:
    packet = _packet()
    packet["automatic_routing_status"] = "ALLOWED"

    assert "automatic_routing_status_must_be_not_allowed" in (
        validate_roadmap_review_packet(packet)
    )


def test_handoff_validation_rejects_selected_next_phase() -> None:
    handoff = _handoff()
    handoff["next_phase_status"] = "RUNTIME_ORCHESTRATOR"

    assert "next_phase_status_must_be_not_selected" in (
        validate_roadmap_operator_handoff(handoff)
    )


def test_handoff_validation_rejects_model_invocation() -> None:
    handoff = _handoff()
    handoff["model_invocation_status"] = "ALLOWED"

    assert "model_invocation_status_must_be_not_allowed" in (
        validate_roadmap_operator_handoff(handoff)
    )


def test_builder_returns_fresh_containers() -> None:
    first_packet = _packet()
    second_packet = _packet()
    first_handoff = _handoff(first_packet)
    second_handoff = _handoff(second_packet)

    mutated_packet = deepcopy(first_packet)
    mutated_handoff = deepcopy(first_handoff)

    mutated_packet["role_ids"].append("runtime_agent")
    mutated_packet["safety_flags"][
        "real_execution_allowed"
    ] = True

    mutated_handoff["completed_stages"].append(
        "RUNTIME_EXECUTION"
    )
    mutated_handoff["safety_flags"][
        "prompt_execution_allowed"
    ] = True

    assert second_packet == _packet()
    assert second_handoff == _handoff(second_packet)
    assert mutated_packet != second_packet
    assert mutated_handoff != second_handoff


def test_non_mapping_review_packet_is_rejected() -> None:
    assert validate_roadmap_review_packet(
        []
    ) == ["review_packet_must_be_mapping"]


def test_non_mapping_handoff_is_rejected() -> None:
    assert validate_roadmap_operator_handoff(
        []
    ) == ["handoff_must_be_mapping"]
