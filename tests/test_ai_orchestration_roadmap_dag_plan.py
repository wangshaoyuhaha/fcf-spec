"""Tests for deterministic one-way governance DAG planning."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_roadmap import (
    ALLOWED_INPUTS,
    DEFAULT_ARTIFACT_TYPE_ORDER,
    DagPlanViolation,
    build_deterministic_governance_dag_plan,
    build_registered_artifact_dependency_plan,
    build_registered_artifact_reference,
    validate_deterministic_governance_dag_plan,
)


def _reference(
    index: int,
    artifact_type: str,
    registration_status: str = "REGISTERED",
    version_pin_status: str = "PINNED",
) -> dict:
    return build_registered_artifact_reference(
        artifact_id=f"artifact-{index:02d}",
        artifact_type=artifact_type,
        artifact_version=f"1.0.{index}",
        registration_status=registration_status,
        dependency_role="GOVERNANCE_EVIDENCE",
        correlation_id="correlation-001",
        research_run_id="research-run-001",
        version_pin_status=version_pin_status,
    )


def _artifact_plan(
    references: list[dict] | None = None,
) -> dict:
    selected = references or [
        _reference(index, artifact_type)
        for index, artifact_type in enumerate(
            ALLOWED_INPUTS,
            start=1,
        )
    ]

    return build_registered_artifact_dependency_plan(
        plan_id="artifact-plan-001",
        artifact_references=selected,
    )


def _dag_plan(
    artifact_plan: dict | None = None,
) -> dict:
    return build_deterministic_governance_dag_plan(
        dag_plan_id="dag-plan-001",
        artifact_plan=artifact_plan or _artifact_plan(),
    )


def test_complete_dag_is_ready_for_gate_planning() -> None:
    plan = _dag_plan()

    assert plan["dag_status"] == (
        "READY_FOR_GATE_PLANNING"
    )
    assert plan["cycle_detected"] is False
    assert plan["orphan_node_ids"] == []


def test_dag_validation_passes() -> None:
    assert validate_deterministic_governance_dag_plan(
        _dag_plan()
    ) == []


def test_topological_order_matches_planned_type_order() -> None:
    plan = _dag_plan()
    node_type_by_id = {
        node["node_id"]: node["artifact_type"]
        for node in plan["nodes"]
    }

    assert [
        node_type_by_id[node_id]
        for node_id in plan["topological_order"]
    ] == list(DEFAULT_ARTIFACT_TYPE_ORDER)


def test_all_edges_move_forward() -> None:
    plan = _dag_plan()
    index_by_node_id = {
        node["node_id"]: node["topological_index"]
        for node in plan["nodes"]
    }

    assert all(
        index_by_node_id[edge["source_node_id"]]
        < index_by_node_id[edge["target_node_id"]]
        for edge in plan["edges"]
    )


def test_every_edge_requires_operator_gate() -> None:
    plan = _dag_plan()

    assert all(
        edge["operator_gate_required"] is True
        for edge in plan["edges"]
    )


def test_operator_review_is_terminal_planned_node() -> None:
    plan = _dag_plan()
    last_node = plan["nodes"][-1]

    assert last_node["artifact_type"] == (
        "REGISTERED_OPERATOR_REVIEW_ARTIFACT"
    )


def test_missing_artifact_keeps_dag_in_review() -> None:
    references = [
        _reference(index, artifact_type)
        for index, artifact_type in enumerate(
            ALLOWED_INPUTS[:-1],
            start=1,
        )
    ]

    plan = _dag_plan(_artifact_plan(references))

    assert plan["dag_status"] == "REVIEW_REQUIRED"


def test_blocked_artifact_blocks_dag() -> None:
    references = [
        _reference(index, artifact_type)
        for index, artifact_type in enumerate(
            ALLOWED_INPUTS,
            start=1,
        )
    ]
    references[0]["registration_status"] = "BLOCKED"

    plan = _dag_plan(_artifact_plan(references))

    assert plan["dag_status"] == "BLOCKED"


def test_multiple_artifacts_for_one_type_are_rejected() -> None:
    references = [
        _reference(index, artifact_type)
        for index, artifact_type in enumerate(
            ALLOWED_INPUTS,
            start=1,
        )
    ]
    references[-1]["artifact_type"] = (
        references[0]["artifact_type"]
    )

    with pytest.raises(
        DagPlanViolation,
        match="multiple_artifacts_for_type",
    ):
        _dag_plan(_artifact_plan(references))


def test_validation_rejects_reverse_edge() -> None:
    plan = _dag_plan()
    edge = plan["edges"][0]
    source = edge["source_node_id"]

    edge["source_node_id"] = edge["target_node_id"]
    edge["target_node_id"] = source

    errors = validate_deterministic_governance_dag_plan(
        plan
    )

    assert any(
        "edge_direction_must_be_forward" in error
        for error in errors
    )


def test_validation_rejects_unknown_edge_node() -> None:
    plan = _dag_plan()
    plan["edges"][0]["target_node_id"] = "node:unknown"

    errors = validate_deterministic_governance_dag_plan(
        plan
    )

    assert any(
        "target_node_id_invalid" in error
        for error in errors
    )


def test_runtime_execution_remains_forbidden() -> None:
    plan = _dag_plan()
    plan["runtime_execution_status"] = "ALLOWED"

    assert "runtime_execution_must_not_be_allowed" in (
        validate_deterministic_governance_dag_plan(plan)
    )


def test_live_model_invocation_remains_forbidden() -> None:
    plan = _dag_plan()
    plan["safety_flags"][
        "live_model_invocation_allowed"
    ] = True

    assert "live_model_invocation_allowed_must_be_false" in (
        validate_deterministic_governance_dag_plan(plan)
    )


def test_builder_returns_fresh_containers() -> None:
    first = _dag_plan()
    second = _dag_plan()
    mutated = deepcopy(first)

    mutated["nodes"][0]["node_status"] = "EXECUTING"
    mutated["edges"][0]["edge_status"] = "EXECUTING"
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _dag_plan()
    assert mutated != second


def test_non_mapping_dag_is_rejected() -> None:
    assert validate_deterministic_governance_dag_plan(
        []
    ) == ["dag_plan_must_be_mapping"]
