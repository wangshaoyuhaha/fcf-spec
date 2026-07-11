"""Tests for registered roadmap artifacts and version locks."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_roadmap import (
    ALLOWED_INPUTS,
    ArtifactPlanViolation,
    build_registered_artifact_dependency_plan,
    build_registered_artifact_reference,
    validate_registered_artifact_dependency_plan,
    validate_registered_artifact_reference,
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


def _complete_references() -> list[dict]:
    return [
        _reference(index, artifact_type)
        for index, artifact_type in enumerate(
            ALLOWED_INPUTS,
            start=1,
        )
    ]


def _complete_plan() -> dict:
    return build_registered_artifact_dependency_plan(
        plan_id="artifact-plan-001",
        artifact_references=_complete_references(),
    )


def test_registered_reference_validation_passes() -> None:
    reference = _reference(
        1,
        ALLOWED_INPUTS[0],
    )

    assert validate_registered_artifact_reference(
        reference
    ) == []


def test_complete_pinned_plan_is_ready_for_dag() -> None:
    plan = _complete_plan()

    assert plan["plan_status"] == (
        "READY_FOR_DAG_PLANNING"
    )
    assert plan["missing_required_artifact_types"] == []


def test_plan_validation_passes() -> None:
    assert validate_registered_artifact_dependency_plan(
        _complete_plan()
    ) == []


def test_missing_artifact_type_requires_review() -> None:
    references = _complete_references()[:-1]

    plan = build_registered_artifact_dependency_plan(
        plan_id="artifact-plan-001",
        artifact_references=references,
    )

    assert plan["plan_status"] == "REVIEW_REQUIRED"
    assert plan["missing_required_artifact_types"] == [
        ALLOWED_INPUTS[-1]
    ]


def test_unpinned_version_requires_review() -> None:
    references = _complete_references()
    references[0]["version_pin_status"] = "REVIEW_REQUIRED"

    plan = build_registered_artifact_dependency_plan(
        plan_id="artifact-plan-001",
        artifact_references=references,
    )

    assert plan["plan_status"] == "REVIEW_REQUIRED"


def test_blocked_artifact_blocks_plan() -> None:
    references = _complete_references()
    references[0]["registration_status"] = "BLOCKED"

    plan = build_registered_artifact_dependency_plan(
        plan_id="artifact-plan-001",
        artifact_references=references,
    )

    assert plan["plan_status"] == "BLOCKED"


def test_version_locks_are_deterministic() -> None:
    references = list(reversed(_complete_references()))

    plan = build_registered_artifact_dependency_plan(
        plan_id="artifact-plan-001",
        artifact_references=references,
    )

    assert plan["artifact_references"] == sorted(
        plan["artifact_references"],
        key=lambda item: (
            item["artifact_type"],
            item["artifact_id"],
            item["artifact_version"],
        ),
    )

    assert [
        lock["artifact_id"]
        for lock in plan["version_locks"]
    ] == [
        reference["artifact_id"]
        for reference in plan["artifact_references"]
    ]


def test_duplicate_artifact_id_is_rejected() -> None:
    references = _complete_references()
    references[1]["artifact_id"] = references[0][
        "artifact_id"
    ]

    with pytest.raises(
        ArtifactPlanViolation,
        match="duplicate_artifact_id",
    ):
        build_registered_artifact_dependency_plan(
            plan_id="artifact-plan-001",
            artifact_references=references,
        )


def test_unknown_artifact_type_is_rejected() -> None:
    reference = _reference(
        1,
        ALLOWED_INPUTS[0],
    )
    reference["artifact_type"] = "UNREGISTERED_ARTIFACT"

    assert "artifact_type_invalid" in (
        validate_registered_artifact_reference(reference)
    )


def test_runtime_execution_remains_forbidden() -> None:
    plan = _complete_plan()
    plan["runtime_execution_status"] = "ALLOWED"

    assert "runtime_execution_must_not_be_allowed" in (
        validate_registered_artifact_dependency_plan(plan)
    )


def test_live_model_execution_flag_is_rejected() -> None:
    plan = _complete_plan()
    plan["safety_flags"][
        "live_model_invocation_allowed"
    ] = True

    assert "live_model_invocation_allowed_must_be_false" in (
        validate_registered_artifact_dependency_plan(plan)
    )


def test_traceability_ids_are_required() -> None:
    reference = _reference(
        1,
        ALLOWED_INPUTS[0],
    )
    reference["correlation_id"] = ""

    assert "correlation_id_invalid" in (
        validate_registered_artifact_reference(reference)
    )


def test_builder_returns_fresh_containers() -> None:
    first = _complete_plan()
    second = _complete_plan()
    mutated = deepcopy(first)

    mutated["present_artifact_types"].append("UNKNOWN")
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _complete_plan()
    assert mutated != second


def test_non_mapping_plan_is_rejected() -> None:
    assert validate_registered_artifact_dependency_plan(
        []
    ) == ["artifact_plan_must_be_mapping"]
