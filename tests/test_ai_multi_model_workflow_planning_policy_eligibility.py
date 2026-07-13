"""Tests for multi-model workflow planning D3."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_multi_model_workflow_planning import (
    MODEL_SLOT_TYPES,
    POLICY_ELIGIBILITY_STAGE_ID,
    PolicyEligibilityViolation,
    build_model_slot_assignment,
    build_multi_model_workflow_boundary_contract,
    build_policy_eligibility_manifest,
    build_role_model_slot_binding_manifest,
    validate_policy_eligibility_manifest,
)
from fcf.sidecars.ai_orchestration_runtime_readiness import (
    build_machine_readable_role_contract_manifest,
    build_routing_candidate,
    build_runtime_readiness_boundary_contract,
)


def _role_manifest() -> dict[str, object]:
    return build_machine_readable_role_contract_manifest(
        manifest_id="runtime.roles.v1",
        boundary_contract=(
            build_runtime_readiness_boundary_contract()
        ),
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


def _slot_manifest() -> dict[str, object]:
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

    return build_role_model_slot_binding_manifest(
        manifest_id="multi.model.slots.v1",
        boundary_contract=(
            build_multi_model_workflow_boundary_contract()
        ),
        role_manifest=_role_manifest(),
        assignments_by_role=assignments,
    )


def _candidate(
    *,
    role_id: str,
    slot: dict[str, object],
    suffix: str = "v1",
    registered_artifacts_status: str = "VERIFIED",
    privacy_policy_status: str = "ALLOWED",
    licensing_policy_status: str = "ALLOWED",
    health_status: str = "HEALTHY",
    cost_limit_status: str = "WITHIN_LIMIT",
) -> dict[str, object]:
    return build_routing_candidate(
        candidate_id=(
            f"candidate.{role_id}."
            f"{slot['slot_type'].lower()}.{suffix}"
        ),
        role_id=role_id,
        provider_id=str(slot["provider_id"]),
        model_version_id=str(
            slot["model_registry_entry_id"]
        ),
        prompt_version_id=str(
            slot["prompt_registry_entry_id"]
        ),
        policy_identifier=str(
            slot["policy_identifier"]
        ),
        policy_version=str(slot["policy_version"]),
        policy_digest=str(slot["policy_digest"]),
        config_snapshot_id=str(
            slot["config_snapshot_id"]
        ),
        registered_artifacts_status=(
            registered_artifacts_status
        ),
        privacy_policy_status=privacy_policy_status,
        licensing_policy_status=(
            licensing_policy_status
        ),
        health_status=health_status,
        cost_limit_status=cost_limit_status,
    )


def _candidates() -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []

    for binding in _slot_manifest()["role_bindings"]:
        if binding["role_kind"] != "PLANNED_AI_ROLE":
            continue

        role_id = str(binding["role_id"])

        for slot in binding["model_slots"]:
            candidates.append(
                _candidate(
                    role_id=role_id,
                    slot=slot,
                )
            )

    return candidates


def _manifest() -> dict[str, object]:
    return build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=_slot_manifest(),
        routing_candidates=_candidates(),
    )


def test_valid_manifest_passes_validation() -> None:
    assert validate_policy_eligibility_manifest(
        _manifest()
    ) == []


def test_d3_identity_is_locked() -> None:
    manifest = _manifest()

    assert manifest["stage_id"] == (
        POLICY_ELIGIBILITY_STAGE_ID
    )
    assert manifest["planning_mode"] == "PLANNING_ONLY"
    assert manifest["policy_authority"] == (
        "DETERMINISTIC_POLICY_ONLY"
    )


def test_every_ai_role_slot_is_evaluated() -> None:
    manifest = _manifest()
    slot_manifest = _slot_manifest()

    expected = sum(
        len(binding["model_slots"])
        for binding in slot_manifest["role_bindings"]
    )

    assert manifest["evaluation_count"] == expected
    assert len(manifest["evaluations"]) == expected


def test_all_verified_candidates_require_operator_review() -> None:
    manifest = _manifest()

    assert manifest["manifest_status"] == (
        "ELIGIBLE_FOR_OPERATOR_REVIEW"
    )
    assert manifest["eligible_count"] == (
        manifest["evaluation_count"]
    )

    for evaluation in manifest["evaluations"]:
        assert evaluation["operator_review_required"] is True


def test_missing_candidate_fails_closed() -> None:
    candidates = _candidates()[:-1]

    manifest = build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=_slot_manifest(),
        routing_candidates=candidates,
    )

    assert manifest["blocked_count"] == 1
    assert manifest["manifest_status"] == "DEGRADED"

    blocked = next(
        item
        for item in manifest["evaluations"]
        if item["eligibility_status"] == "BLOCKED"
    )

    assert blocked["blocking_reasons"] == [
        "routing_candidate_missing"
    ]


def test_privacy_block_propagates() -> None:
    slot_manifest = _slot_manifest()
    candidates = _candidates()
    first_binding = next(
        item
        for item in slot_manifest["role_bindings"]
        if item["role_kind"] == "PLANNED_AI_ROLE"
    )
    first_slot = first_binding["model_slots"][0]

    candidates[0] = _candidate(
        role_id=str(first_binding["role_id"]),
        slot=first_slot,
        privacy_policy_status="BLOCKED",
    )

    manifest = build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=slot_manifest,
        routing_candidates=candidates,
    )

    assert manifest["blocked_count"] == 1

    blocked = next(
        item
        for item in manifest["evaluations"]
        if item["eligibility_status"] == "BLOCKED"
    )

    assert "privacy_policy_blocked" in (
        blocked["blocking_reasons"]
    )


def test_degraded_health_propagates() -> None:
    slot_manifest = _slot_manifest()
    candidates = _candidates()
    first_binding = next(
        item
        for item in slot_manifest["role_bindings"]
        if item["role_kind"] == "PLANNED_AI_ROLE"
    )
    first_slot = first_binding["model_slots"][0]

    candidates[0] = _candidate(
        role_id=str(first_binding["role_id"]),
        slot=first_slot,
        health_status="DEGRADED",
    )

    manifest = build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=slot_manifest,
        routing_candidates=candidates,
    )

    assert manifest["degraded_count"] == 1
    assert manifest["manifest_status"] == "DEGRADED"


def test_duplicate_matching_candidates_fail_closed() -> None:
    candidates = _candidates()
    duplicate = deepcopy(candidates[0])
    duplicate["candidate_id"] = "candidate.duplicate.v1"
    candidates.append(duplicate)

    manifest = build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=_slot_manifest(),
        routing_candidates=candidates,
    )

    blocked = next(
        item
        for item in manifest["evaluations"]
        if item["eligibility_status"] == "BLOCKED"
    )

    assert blocked["blocking_reasons"] == [
        "routing_candidate_ambiguous"
    ]


def test_unbound_candidate_is_rejected() -> None:
    candidates = _candidates()
    unbound = deepcopy(candidates[0])
    unbound["candidate_id"] = "candidate.unbound.v1"
    unbound["model_version_id"] = "model.unbound.v1"
    candidates.append(unbound)

    with pytest.raises(PolicyEligibilityViolation):
        build_policy_eligibility_manifest(
            manifest_id="multi.model.policy.v1",
            slot_binding_manifest=_slot_manifest(),
            routing_candidates=candidates,
        )


def test_automatic_actions_remain_blocked() -> None:
    manifest = _manifest()

    assert manifest["automatic_selection_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["automatic_switching_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["automatic_routing_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["model_invocation_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["prompt_execution_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["route_execution_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["runtime_activation_status"] == (
        "NOT_ALLOWED"
    )

    for evaluation in manifest["evaluations"]:
        assert evaluation[
            "automatic_selection_allowed"
        ] is False
        assert evaluation[
            "automatic_switching_allowed"
        ] is False
        assert evaluation[
            "automatic_routing_allowed"
        ] is False


def test_validation_rejects_runtime_activation() -> None:
    manifest = _manifest()
    manifest["runtime_activation_status"] = "ACTIVE"

    assert "runtime_activation_status_invalid" in (
        validate_policy_eligibility_manifest(
            manifest
        )
    )


def test_validation_rejects_selection_activation() -> None:
    manifest = _manifest()
    manifest["evaluations"][0][
        "automatic_selection_allowed"
    ] = True

    assert "automatic_selection_allowed_invalid" in (
        validate_policy_eligibility_manifest(
            manifest
        )
    )


def test_builder_returns_fresh_nested_containers() -> None:
    first = _manifest()
    second = _manifest()
    mutated = deepcopy(first)

    mutated["evaluations"][0][
        "model_invocation_status"
    ] = "ACTIVE"

    assert second == _manifest()
    assert mutated != second


def test_non_mapping_manifest_is_rejected() -> None:
    assert validate_policy_eligibility_manifest(
        []
    ) == ["manifest_must_be_mapping"]