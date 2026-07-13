"""Tests for multi-model workflow planning D2."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_multi_model_workflow_planning import (
    MODEL_SLOT_TYPES,
    SLOT_BINDING_STAGE_ID,
    ModelSlotBindingViolation,
    build_model_slot_assignment,
    build_multi_model_workflow_boundary_contract,
    build_role_model_slot_binding_manifest,
    validate_role_model_slot_binding_manifest,
)
from fcf.sidecars.ai_orchestration_runtime_readiness import (
    build_machine_readable_role_contract_manifest,
    build_runtime_readiness_boundary_contract,
)


def _runtime_boundary() -> dict[str, object]:
    return build_runtime_readiness_boundary_contract()


def _role_manifest() -> dict[str, object]:
    return build_machine_readable_role_contract_manifest(
        manifest_id="runtime.roles.v1",
        boundary_contract=_runtime_boundary(),
    )


def _slot(
    *,
    role_id: str,
    slot_type: str,
) -> dict[str, object]:
    location = (
        "CLOUD"
        if slot_type == "CLOUD_APPROVED"
        else "LOCAL"
    )

    return build_model_slot_assignment(
        slot_type=slot_type,
        model_registry_entry_id=(
            f"model.{role_id}.{slot_type.lower()}.v1"
        ),
        prompt_registry_entry_id=(
            f"prompt.{role_id}.{slot_type.lower()}.v1"
        ),
        provider_id=(
            "provider.cloud"
            if location == "CLOUD"
            else "provider.local"
        ),
        execution_location=location,
        policy_identifier="FCF.POLICY.MODEL.SLOT",
        policy_version="1.0.0",
        policy_digest="policy.digest.v1",
        config_snapshot_id="config.snapshot.v1",
    )


def _assignments() -> dict[str, list[dict[str, object]]]:
    assignments: dict[
        str,
        list[dict[str, object]],
    ] = {}

    for role in _role_manifest()["roles"]:
        if role["role_kind"] != "PLANNED_AI_ROLE":
            continue

        role_id = str(role["role_id"])
        assignments[role_id] = [
            _slot(
                role_id=role_id,
                slot_type=slot_type,
            )
            for slot_type in MODEL_SLOT_TYPES
        ]

    return assignments


def _manifest() -> dict[str, object]:
    return build_role_model_slot_binding_manifest(
        manifest_id="multi.model.slots.v1",
        boundary_contract=(
            build_multi_model_workflow_boundary_contract()
        ),
        role_manifest=_role_manifest(),
        assignments_by_role=_assignments(),
    )


def test_valid_manifest_passes_validation() -> None:
    assert validate_role_model_slot_binding_manifest(
        _manifest()
    ) == []


def test_d2_identity_is_locked() -> None:
    manifest = _manifest()

    assert manifest["stage_id"] == SLOT_BINDING_STAGE_ID
    assert manifest["planning_mode"] == "PLANNING_ONLY"
    assert manifest["manifest_status"] == (
        "READY_FOR_POLICY_ELIGIBILITY_PLANNING"
    )


def test_existing_role_order_is_preserved() -> None:
    source_role_ids = [
        role["role_id"]
        for role in _role_manifest()["roles"]
    ]
    binding_role_ids = [
        binding["role_id"]
        for binding in _manifest()["role_bindings"]
    ]

    assert binding_role_ids == source_role_ids
    assert binding_role_ids[-1] == "human_operator"


def test_only_planned_ai_roles_receive_model_slots() -> None:
    manifest = _manifest()

    for binding in manifest["role_bindings"]:
        if binding["role_kind"] == "PLANNED_AI_ROLE":
            assert binding["model_slots"]
            assert binding["slot_binding_status"] == (
                "PLANNED_NOT_ACTIVE"
            )
        else:
            assert binding["model_slots"] == []
            assert binding["required_slot_types"] == []
            assert binding["slot_binding_status"] == (
                "NOT_APPLICABLE"
            )


def test_each_ai_role_has_all_locked_slot_types() -> None:
    manifest = _manifest()

    for binding in manifest["role_bindings"]:
        if binding["role_kind"] != "PLANNED_AI_ROLE":
            continue

        assert binding["required_slot_types"] == list(
            MODEL_SLOT_TYPES
        )
        assert [
            slot["slot_type"]
            for slot in binding["model_slots"]
        ] == list(MODEL_SLOT_TYPES)


def test_slots_bind_existing_registry_references() -> None:
    manifest = _manifest()

    for binding in manifest["role_bindings"]:
        for slot in binding["model_slots"]:
            assert slot["model_registry_entry_id"]
            assert slot["prompt_registry_entry_id"]
            assert slot["policy_identifier"]
            assert slot["policy_version"]
            assert slot["policy_digest"]
            assert slot["config_snapshot_id"]


def test_cloud_slot_requires_deterministic_policy_review() -> None:
    manifest = _manifest()

    for binding in manifest["role_bindings"]:
        for slot in binding["model_slots"]:
            if slot["slot_type"] != "CLOUD_APPROVED":
                continue

            assert slot["execution_location"] == "CLOUD"
            assert slot["cloud_eligibility_status"] == (
                "POLICY_REVIEW_REQUIRED"
            )
            assert slot["operator_review_required"] is True


def test_local_only_slot_requires_local_location() -> None:
    with pytest.raises(ModelSlotBindingViolation):
        build_model_slot_assignment(
            slot_type="LOCAL_ONLY",
            model_registry_entry_id="model.local.v1",
            prompt_registry_entry_id="prompt.local.v1",
            provider_id="provider.cloud",
            execution_location="CLOUD",
            policy_identifier="FCF.POLICY.MODEL.SLOT",
            policy_version="1.0.0",
            policy_digest="policy.digest.v1",
            config_snapshot_id="config.snapshot.v1",
        )


def test_cloud_approved_slot_requires_cloud_location() -> None:
    with pytest.raises(ModelSlotBindingViolation):
        build_model_slot_assignment(
            slot_type="CLOUD_APPROVED",
            model_registry_entry_id="model.cloud.v1",
            prompt_registry_entry_id="prompt.cloud.v1",
            provider_id="provider.local",
            execution_location="LOCAL",
            policy_identifier="FCF.POLICY.MODEL.SLOT",
            policy_version="1.0.0",
            policy_digest="policy.digest.v1",
            config_snapshot_id="config.snapshot.v1",
        )


def test_automatic_selection_switching_and_invocation_are_blocked() -> None:
    manifest = _manifest()

    assert manifest["automatic_selection_status"] == "NOT_ALLOWED"
    assert manifest["automatic_switching_status"] == "NOT_ALLOWED"
    assert manifest["model_invocation_status"] == "NOT_ALLOWED"
    assert manifest["prompt_execution_status"] == "NOT_ALLOWED"
    assert manifest["runtime_activation_status"] == "NOT_ALLOWED"

    for binding in manifest["role_bindings"]:
        assert binding["automatic_selection_status"] == (
            "NOT_ALLOWED"
        )
        assert binding["automatic_switching_status"] == (
            "NOT_ALLOWED"
        )
        assert binding["model_invocation_status"] == (
            "NOT_ALLOWED"
        )


def test_builder_rejects_unknown_role_assignment() -> None:
    assignments = _assignments()
    assignments["unknown_role"] = []

    with pytest.raises(ModelSlotBindingViolation):
        build_role_model_slot_binding_manifest(
            manifest_id="multi.model.slots.v1",
            boundary_contract=(
                build_multi_model_workflow_boundary_contract()
            ),
            role_manifest=_role_manifest(),
            assignments_by_role=assignments,
        )


def test_builder_rejects_missing_required_slot() -> None:
    assignments = _assignments()
    role_id = sorted(assignments.keys())[0]
    assignments[role_id] = assignments[role_id][:-1]

    with pytest.raises(ModelSlotBindingViolation):
        build_role_model_slot_binding_manifest(
            manifest_id="multi.model.slots.v1",
            boundary_contract=(
                build_multi_model_workflow_boundary_contract()
            ),
            role_manifest=_role_manifest(),
            assignments_by_role=assignments,
        )


def test_builder_rejects_duplicate_slot_type() -> None:
    assignments = _assignments()
    role_id = sorted(assignments.keys())[0]
    assignments[role_id][-1] = deepcopy(
        assignments[role_id][0]
    )

    with pytest.raises(ModelSlotBindingViolation):
        build_role_model_slot_binding_manifest(
            manifest_id="multi.model.slots.v1",
            boundary_contract=(
                build_multi_model_workflow_boundary_contract()
            ),
            role_manifest=_role_manifest(),
            assignments_by_role=assignments,
        )


def test_builder_rejects_model_binding_for_operator() -> None:
    assignments = _assignments()
    assignments["human_operator"] = [
        _slot(
            role_id="human_operator",
            slot_type=slot_type,
        )
        for slot_type in MODEL_SLOT_TYPES
    ]

    with pytest.raises(ModelSlotBindingViolation):
        build_role_model_slot_binding_manifest(
            manifest_id="multi.model.slots.v1",
            boundary_contract=(
                build_multi_model_workflow_boundary_contract()
            ),
            role_manifest=_role_manifest(),
            assignments_by_role=assignments,
        )


def test_validation_rejects_model_invocation_activation() -> None:
    manifest = _manifest()
    manifest["model_invocation_status"] = "ACTIVE"

    assert "model_invocation_status_invalid" in (
        validate_role_model_slot_binding_manifest(
            manifest
        )
    )


def test_validation_rejects_slot_selection_activation() -> None:
    manifest = _manifest()
    first_ai_binding = next(
        binding
        for binding in manifest["role_bindings"]
        if binding["role_kind"] == "PLANNED_AI_ROLE"
    )
    first_ai_binding["model_slots"][0][
        "automatic_selection_allowed"
    ] = True

    assert "automatic_selection_allowed_invalid" in (
        validate_role_model_slot_binding_manifest(
            manifest
        )
    )


def test_builder_returns_fresh_nested_containers() -> None:
    first = _manifest()
    second = _manifest()
    mutated = deepcopy(first)

    first_ai_binding = next(
        binding
        for binding in mutated["role_bindings"]
        if binding["role_kind"] == "PLANNED_AI_ROLE"
    )
    first_ai_binding["model_slots"][0][
        "model_invocation_status"
    ] = "ACTIVE"

    assert second == _manifest()
    assert mutated != second


def test_non_mapping_manifest_is_rejected() -> None:
    assert validate_role_model_slot_binding_manifest(
        []
    ) == ["manifest_must_be_mapping"]