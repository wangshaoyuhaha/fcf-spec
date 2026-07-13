"""Tests for multi-model workflow planning D4."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_multi_model_workflow_planning import (
    ASSIGNMENT_PROFILE_STAGE_ID,
    MODEL_SLOT_TYPES,
    AssignmentProfileViolation,
    build_assignment_profile_manifest,
    build_model_slot_assignment,
    build_multi_model_workflow_boundary_contract,
    build_policy_eligibility_manifest,
    build_role_model_slot_binding_manifest,
    validate_assignment_profile_manifest,
)
from fcf.sidecars.ai_orchestration_runtime_readiness import (
    build_cost_contract,
    build_fallback_contract,
    build_machine_readable_role_contract_manifest,
    build_retry_contract,
    build_routing_candidate,
    build_routing_eligibility_contract,
    build_runtime_limit_contract_bundle,
    build_runtime_readiness_boundary_contract,
    build_timeout_contract,
)


def _role_manifest() -> dict[str, object]:
    return build_machine_readable_role_contract_manifest(
        manifest_id="runtime.roles.v1",
        boundary_contract=(
            build_runtime_readiness_boundary_contract()
        ),
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
        slots: list[dict[str, object]] = []

        for slot_type in MODEL_SLOT_TYPES:
            location = (
                "CLOUD"
                if slot_type == "CLOUD_APPROVED"
                else "LOCAL"
            )

            slots.append(
                build_model_slot_assignment(
                    slot_type=slot_type,
                    model_registry_entry_id=(
                        f"model.{role_id}."
                        f"{slot_type.lower()}.v1"
                    ),
                    prompt_registry_entry_id=(
                        f"prompt.{role_id}."
                        f"{slot_type.lower()}.v1"
                    ),
                    provider_id=(
                        "provider.cloud"
                        if location == "CLOUD"
                        else "provider.local"
                    ),
                    execution_location=location,
                    policy_identifier=(
                        "FCF.POLICY.MODEL.SLOT"
                    ),
                    policy_version="1.0.0",
                    policy_digest="policy.digest.v1",
                    config_snapshot_id=(
                        "config.snapshot.v1"
                    ),
                )
            )

        assignments[role_id] = slots

    return build_role_model_slot_binding_manifest(
        manifest_id="multi.model.slots.v1",
        boundary_contract=(
            build_multi_model_workflow_boundary_contract()
        ),
        role_manifest=_role_manifest(),
        assignments_by_role=assignments,
    )


def _candidates(
    *,
    health_status: str = "HEALTHY",
) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []

    for binding in _slot_manifest()["role_bindings"]:
        if binding["role_kind"] != "PLANNED_AI_ROLE":
            continue

        role_id = str(binding["role_id"])

        for slot in binding["model_slots"]:
            candidates.append(
                build_routing_candidate(
                    candidate_id=(
                        f"candidate.{role_id}."
                        f"{slot['slot_type'].lower()}.v1"
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
                    policy_version=str(
                        slot["policy_version"]
                    ),
                    policy_digest=str(
                        slot["policy_digest"]
                    ),
                    config_snapshot_id=str(
                        slot["config_snapshot_id"]
                    ),
                    registered_artifacts_status="VERIFIED",
                    privacy_policy_status="ALLOWED",
                    licensing_policy_status="ALLOWED",
                    health_status=health_status,
                    cost_limit_status="WITHIN_LIMIT",
                )
            )

    return candidates


def _policy_manifest() -> dict[str, object]:
    return build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=_slot_manifest(),
        routing_candidates=_candidates(),
    )


def _runtime_bundle(
    *,
    health_status: str = "HEALTHY",
) -> dict[str, object]:
    candidates = _candidates(
        health_status=health_status
    )

    routing_contract = build_routing_eligibility_contract(
        routing_contract_id="runtime.routing.v1",
        role_manifest=_role_manifest(),
        candidates=candidates,
    )

    return build_runtime_limit_contract_bundle(
        runtime_limit_bundle_id="runtime.limits.v1",
        routing_contract=routing_contract,
        timeout_contract=build_timeout_contract(
            connect_timeout_ms=1000,
            response_timeout_ms=4000,
            total_timeout_ms=5000,
        ),
        retry_contract=build_retry_contract(
            max_attempts=2,
            backoff_ms=[500, 1000],
            retryable_failure_classes=[
                "PROVIDER_TRANSIENT_FAILURE",
                "RATE_LIMIT_TRANSIENT_FAILURE",
            ],
        ),
        fallback_contract=build_fallback_contract(
            fallback_candidate_ids=[
                str(candidates[0]["candidate_id"]),
            ],
        ),
        cost_contract=build_cost_contract(
            currency="USD",
            per_request_limit_microunits=1_000_000,
            workflow_limit_microunits=5_000_000,
            daily_limit_microunits=20_000_000,
        ),
    )


def _profile_metadata() -> dict[
    str,
    dict[str, str],
]:
    metadata: dict[str, dict[str, str]] = {}

    for evaluation in _policy_manifest()["evaluations"]:
        role_id = str(evaluation["role_id"])
        slot_type = str(evaluation["slot_type"])
        key = f"{role_id}::{slot_type}"

        metadata[key] = {
            "output_schema_id": (
                f"schema.{role_id}.{slot_type.lower()}.v1"
            ),
            "output_schema_version": "1.0.0",
            "privacy_level": "PUBLIC_REDACTED",
            "evaluation_baseline_id": (
                f"evaluation.{role_id}.v1"
            ),
        }

    return metadata


def _runtime_bundles(
    *,
    health_status: str = "HEALTHY",
) -> dict[str, dict[str, object]]:
    bundle = _runtime_bundle(
        health_status=health_status
    )
    bundles: dict[str, dict[str, object]] = {}

    for evaluation in _policy_manifest()["evaluations"]:
        key = (
            f"{evaluation['role_id']}::"
            f"{evaluation['slot_type']}"
        )
        bundles[key] = deepcopy(bundle)

    return bundles


def _manifest(
    *,
    health_status: str = "HEALTHY",
) -> dict[str, object]:
    return build_assignment_profile_manifest(
        manifest_id="multi.model.assignments.v1",
        policy_eligibility_manifest=_policy_manifest(),
        profile_metadata_by_role_slot=(
            _profile_metadata()
        ),
        runtime_limit_bundles_by_role_slot=(
            _runtime_bundles(
                health_status=health_status
            )
        ),
    )


def test_valid_manifest_passes_validation() -> None:
    assert validate_assignment_profile_manifest(
        _manifest()
    ) == []


def test_d4_identity_is_locked() -> None:
    manifest = _manifest()

    assert manifest["stage_id"] == (
        ASSIGNMENT_PROFILE_STAGE_ID
    )
    assert manifest["planning_mode"] == "PLANNING_ONLY"
    assert manifest["policy_authority"] == (
        "DETERMINISTIC_POLICY_ONLY"
    )


def test_every_policy_evaluation_has_assignment() -> None:
    manifest = _manifest()

    assert manifest["assignment_count"] == len(
        _policy_manifest()["evaluations"]
    )
    assert manifest["ready_count"] == (
        manifest["assignment_count"]
    )


def test_required_role_assignment_fields_are_present() -> None:
    assignment = _manifest()["assignments"][0]

    assert assignment["output_schema_id"]
    assert assignment["output_schema_version"]
    assert assignment["privacy_level"]
    assert assignment["evaluation_baseline_id"]
    assert assignment["approval_status"] == (
        "REVIEW_REQUIRED"
    )


def test_runtime_limit_bundle_is_bound() -> None:
    assignment = _manifest()["assignments"][0]
    bundle = assignment["runtime_limit_bundle"]

    assert bundle["timeout_contract"]
    assert bundle["retry_contract"]
    assert bundle["fallback_contract"]
    assert bundle["cost_contract"]


def test_degraded_runtime_bundle_degrades_assignments() -> None:
    manifest = _manifest(health_status="DEGRADED")

    assert manifest["degraded_count"] == (
        manifest["assignment_count"]
    )
    assert manifest["manifest_status"] == "DEGRADED"


def test_automatic_runtime_actions_remain_blocked() -> None:
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
    assert manifest["automatic_retry_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["automatic_fallback_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["model_invocation_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["prompt_execution_status"] == (
        "NOT_ALLOWED"
    )
    assert manifest["runtime_execution_status"] == (
        "NOT_ALLOWED"
    )


def test_missing_profile_metadata_is_rejected() -> None:
    metadata = _profile_metadata()
    metadata.pop(sorted(metadata.keys())[0])

    with pytest.raises(AssignmentProfileViolation):
        build_assignment_profile_manifest(
            manifest_id="multi.model.assignments.v1",
            policy_eligibility_manifest=_policy_manifest(),
            profile_metadata_by_role_slot=metadata,
            runtime_limit_bundles_by_role_slot=(
                _runtime_bundles()
            ),
        )


def test_missing_runtime_bundle_is_rejected() -> None:
    bundles = _runtime_bundles()
    bundles.pop(sorted(bundles.keys())[0])

    with pytest.raises(AssignmentProfileViolation):
        build_assignment_profile_manifest(
            manifest_id="multi.model.assignments.v1",
            policy_eligibility_manifest=_policy_manifest(),
            profile_metadata_by_role_slot=(
                _profile_metadata()
            ),
            runtime_limit_bundles_by_role_slot=bundles,
        )


def test_validation_rejects_runtime_activation() -> None:
    manifest = _manifest()
    manifest["runtime_execution_status"] = "ACTIVE"

    assert "runtime_execution_status_invalid" in (
        validate_assignment_profile_manifest(
            manifest
        )
    )


def test_builder_returns_fresh_nested_containers() -> None:
    first = _manifest()
    second = _manifest()
    mutated = deepcopy(first)

    mutated["assignments"][0][
        "runtime_limit_bundle"
    ]["retry_contract"]["backoff_ms"].append(2000)

    assert second == _manifest()
    assert mutated != second


def test_non_mapping_manifest_is_rejected() -> None:
    assert validate_assignment_profile_manifest(
        []
    ) == ["manifest_must_be_mapping"]