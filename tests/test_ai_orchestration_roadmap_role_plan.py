"""Tests for planning-only role responsibility matrices."""

from copy import deepcopy

from fcf.sidecars.ai_orchestration_roadmap import (
    ALLOWED_INPUTS,
    HUMAN_OPERATOR_ROLE_ID,
    build_deterministic_governance_dag_plan,
    build_governance_gate_plan,
    build_registered_artifact_dependency_plan,
    build_registered_artifact_reference,
    build_role_responsibility_plan,
    validate_role_responsibility_plan,
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


def test_clean_role_plan_is_ready_for_review_packet() -> None:
    plan = _role_plan()

    assert plan["role_plan_status"] == (
        "READY_FOR_REVIEW_PACKET"
    )


def test_role_plan_validation_passes() -> None:
    assert validate_role_responsibility_plan(
        _role_plan()
    ) == []


def test_human_operator_is_terminal_role() -> None:
    plan = _role_plan()

    assert plan["human_operator_terminal_role_id"] == (
        HUMAN_OPERATOR_ROLE_ID
    )
    assert plan["roles"][-1]["role_id"] == (
        HUMAN_OPERATOR_ROLE_ID
    )
    assert plan["roles"][-1]["role_kind"] == (
        "HUMAN_OPERATOR"
    )


def test_every_role_requires_operator_gate() -> None:
    plan = _role_plan()

    assert all(
        role["operator_gate_required"] is True
        for role in plan["roles"]
    )


def test_roles_are_non_executable() -> None:
    plan = _role_plan()

    assert all(
        role["runtime_execution_status"] == "NOT_ALLOWED"
        for role in plan["roles"]
    )
    assert all(
        role["automatic_activation_allowed"] is False
        for role in plan["roles"]
    )


def test_output_ownership_is_unique() -> None:
    plan = _role_plan()
    output_types = [
        item["output_artifact_type"]
        for item in plan["output_ownership"]
    ]

    assert len(output_types) == len(set(output_types))


def test_timeout_keeps_role_plan_in_review() -> None:
    edge_id = _dag_plan()["edges"][0]["edge_id"]

    plan = _role_plan(
        {edge_id: "TIMEOUT_RECORDED"}
    )

    assert plan["role_plan_status"] == "REVIEW_REQUIRED"
    assert all(
        role["role_status"] == "REVIEW_REQUIRED"
        for role in plan["roles"]
    )


def test_blocked_gate_plan_blocks_roles() -> None:
    plan = _role_plan(blocked=True)

    assert plan["role_plan_status"] == "BLOCKED"
    assert all(
        role["role_status"] == "BLOCKED"
        for role in plan["roles"]
    )


def test_validation_rejects_automatic_activation() -> None:
    plan = _role_plan()
    plan["roles"][0][
        "automatic_activation_allowed"
    ] = True

    errors = validate_role_responsibility_plan(plan)

    assert any(
        "automatic_activation_allowed_must_be_false"
        in error
        for error in errors
    )


def test_validation_rejects_automatic_routing() -> None:
    plan = _role_plan()
    plan["automatic_route_selection_status"] = "ALLOWED"

    assert (
        "automatic_route_selection_status_must_be_not_allowed"
        in validate_role_responsibility_plan(plan)
    )


def test_validation_rejects_role_switching() -> None:
    plan = _role_plan()
    plan["automatic_role_switching_status"] = "ALLOWED"

    assert (
        "automatic_role_switching_status_must_be_not_allowed"
        in validate_role_responsibility_plan(plan)
    )


def test_validation_rejects_model_invocation() -> None:
    plan = _role_plan()
    plan["model_invocation_status"] = "ALLOWED"

    assert "model_invocation_status_must_be_not_allowed" in (
        validate_role_responsibility_plan(plan)
    )


def test_validation_rejects_prompt_execution() -> None:
    plan = _role_plan()
    plan["prompt_execution_status"] = "ALLOWED"

    assert "prompt_execution_status_must_be_not_allowed" in (
        validate_role_responsibility_plan(plan)
    )


def test_validation_detects_ownership_change() -> None:
    plan = _role_plan()
    plan["output_ownership"][0]["owner_role_id"] = (
        "unknown_role"
    )

    assert "output_ownership_mismatch" in (
        validate_role_responsibility_plan(plan)
    )


def test_builder_returns_fresh_containers() -> None:
    first = _role_plan()
    second = _role_plan()
    mutated = deepcopy(first)

    mutated["roles"][0]["role_status"] = "EXECUTING"
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _role_plan()
    assert mutated != second


def test_non_mapping_role_plan_is_rejected() -> None:
    assert validate_role_responsibility_plan(
        []
    ) == ["role_plan_must_be_mapping"]
