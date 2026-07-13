"""Tests for multi-model workflow planning D6."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_multi_model_workflow_planning import (
    FINAL_HANDOFF_STAGE_ID,
    MODEL_SLOT_TYPES,
    WorkflowFinalHandoffViolation,
    build_assignment_profile_manifest,
    build_model_slot_assignment,
    build_multi_model_workflow_boundary_contract,
    build_policy_eligibility_manifest,
    build_role_model_slot_binding_manifest,
    build_workflow_final_handoff,
    build_workflow_review_packet,
    validate_workflow_final_handoff,
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


def _build_sources(
    *,
    policy_candidates_enabled: bool = True,
    runtime_health_status: str = "HEALTHY",
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    role_manifest = (
        build_machine_readable_role_contract_manifest(
            manifest_id="runtime.roles.v1",
            boundary_contract=(
                build_runtime_readiness_boundary_contract()
            ),
        )
    )
    boundary = (
        build_multi_model_workflow_boundary_contract()
    )

    assignments: dict[
        str,
        list[dict[str, object]],
    ] = {}

    for role in role_manifest["roles"]:
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

    slot_manifest = (
        build_role_model_slot_binding_manifest(
            manifest_id="multi.model.slots.v1",
            boundary_contract=boundary,
            role_manifest=role_manifest,
            assignments_by_role=assignments,
        )
    )

    healthy_candidates: list[dict[str, object]] = []
    runtime_candidates: list[dict[str, object]] = []

    for binding in slot_manifest["role_bindings"]:
        if binding["role_kind"] != "PLANNED_AI_ROLE":
            continue

        role_id = str(binding["role_id"])

        for slot in binding["model_slots"]:
            common = {
                "candidate_id": (
                    f"candidate.{role_id}."
                    f"{slot['slot_type'].lower()}.v1"
                ),
                "role_id": role_id,
                "provider_id": str(slot["provider_id"]),
                "model_version_id": str(
                    slot["model_registry_entry_id"]
                ),
                "prompt_version_id": str(
                    slot["prompt_registry_entry_id"]
                ),
                "policy_identifier": str(
                    slot["policy_identifier"]
                ),
                "policy_version": str(
                    slot["policy_version"]
                ),
                "policy_digest": str(
                    slot["policy_digest"]
                ),
                "config_snapshot_id": str(
                    slot["config_snapshot_id"]
                ),
                "registered_artifacts_status": "VERIFIED",
                "privacy_policy_status": "ALLOWED",
                "licensing_policy_status": "ALLOWED",
                "cost_limit_status": "WITHIN_LIMIT",
            }

            healthy_candidates.append(
                build_routing_candidate(
                    **common,
                    health_status="HEALTHY",
                )
            )
            runtime_candidates.append(
                build_routing_candidate(
                    **common,
                    health_status=runtime_health_status,
                )
            )

    policy_manifest = build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=slot_manifest,
        routing_candidates=(
            healthy_candidates
            if policy_candidates_enabled
            else []
        ),
    )

    routing_contract = (
        build_routing_eligibility_contract(
            routing_contract_id="runtime.routing.v1",
            role_manifest=role_manifest,
            candidates=runtime_candidates,
        )
    )

    runtime_bundle = (
        build_runtime_limit_contract_bundle(
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
                    str(
                        runtime_candidates[0][
                            "candidate_id"
                        ]
                    ),
                ],
            ),
            cost_contract=build_cost_contract(
                currency="USD",
                per_request_limit_microunits=1_000_000,
                workflow_limit_microunits=5_000_000,
                daily_limit_microunits=20_000_000,
            ),
        )
    )

    metadata: dict[str, dict[str, str]] = {}
    bundles: dict[str, dict[str, object]] = {}

    for evaluation in policy_manifest["evaluations"]:
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
        bundles[key] = deepcopy(runtime_bundle)

    assignment_manifest = (
        build_assignment_profile_manifest(
            manifest_id="multi.model.assignments.v1",
            policy_eligibility_manifest=policy_manifest,
            profile_metadata_by_role_slot=metadata,
            runtime_limit_bundles_by_role_slot=bundles,
        )
    )

    packet = build_workflow_review_packet(
        review_packet_id="multi.model.review.v1",
        boundary_contract=boundary,
        slot_binding_manifest=slot_manifest,
        policy_eligibility_manifest=policy_manifest,
        assignment_profile_manifest=(
            assignment_manifest
        ),
    )

    return (
        boundary,
        slot_manifest,
        policy_manifest,
        assignment_manifest,
        packet,
    )


def _handoff(
    *,
    policy_candidates_enabled: bool = True,
    runtime_health_status: str = "HEALTHY",
) -> dict[str, object]:
    (
        boundary,
        slot_manifest,
        policy_manifest,
        assignment_manifest,
        packet,
    ) = _build_sources(
        policy_candidates_enabled=(
            policy_candidates_enabled
        ),
        runtime_health_status=runtime_health_status,
    )

    return build_workflow_final_handoff(
        handoff_id="multi.model.handoff.v1",
        review_packet=packet,
        boundary_contract=boundary,
        slot_binding_manifest=slot_manifest,
        policy_eligibility_manifest=policy_manifest,
        assignment_profile_manifest=assignment_manifest,
    )


def test_valid_handoff_passes_validation() -> None:
    sources = _build_sources()
    (
        boundary,
        slot_manifest,
        policy_manifest,
        assignment_manifest,
        packet,
    ) = sources

    handoff = build_workflow_final_handoff(
        handoff_id="multi.model.handoff.v1",
        review_packet=packet,
        boundary_contract=boundary,
        slot_binding_manifest=slot_manifest,
        policy_eligibility_manifest=policy_manifest,
        assignment_profile_manifest=assignment_manifest,
    )

    assert validate_workflow_final_handoff(
        handoff,
        review_packet=packet,
        boundary_contract=boundary,
        slot_binding_manifest=slot_manifest,
        policy_eligibility_manifest=policy_manifest,
        assignment_profile_manifest=assignment_manifest,
    ) == []


def test_stage_identity_is_locked() -> None:
    assert _handoff()["stage_id"] == (
        FINAL_HANDOFF_STAGE_ID
    )


def test_ready_packet_is_merge_review_eligible() -> None:
    handoff = _handoff()

    assert handoff["handoff_status"] == (
        "READY_FOR_OPERATOR_MERGE_REVIEW"
    )
    assert handoff["main_merge_review_eligible"] is True
    assert handoff["repair_required"] is False


def test_degraded_packet_requires_operator_review() -> None:
    handoff = _handoff(
        runtime_health_status="DEGRADED"
    )

    assert handoff["handoff_status"] == (
        "DEGRADED_OPERATOR_REVIEW_REQUIRED_BEFORE_MERGE_REVIEW"
    )
    assert handoff["main_merge_review_eligible"] is False
    assert handoff["repair_required"] is False


def test_blocked_packet_requires_repair() -> None:
    handoff = _handoff(
        policy_candidates_enabled=False
    )

    assert handoff["handoff_status"] == (
        "BLOCKED_REPAIR_REQUIRED"
    )
    assert handoff["main_merge_review_eligible"] is False
    assert handoff["repair_required"] is True


def test_source_chain_is_preserved() -> None:
    handoff = _handoff()

    assert handoff["source_review_packet_id"] == (
        "multi.model.review.v1"
    )
    assert handoff["source_contract_id"] == (
        "fcf.multi_model_workflow.planning.v1"
    )
    assert handoff["branch_name"] == (
        "sidecar-ai-multi-model-workflow-planning-app-1"
    )


def test_operator_action_is_required() -> None:
    handoff = _handoff()

    assert handoff["operator_action_required"] is True
    assert handoff["operator_decision_status"] == "PENDING"
    assert (
        "APPROVE_MAIN_MERGE_REVIEW"
        in handoff["allowed_operator_actions"]
    )


def test_runtime_release_and_execution_are_disabled() -> None:
    handoff = _handoff()

    for field in (
        "main_merge_allowed_without_operator_confirmation",
        "automatic_selection_allowed",
        "automatic_switching_allowed",
        "automatic_routing_allowed",
        "automatic_retry_allowed",
        "automatic_fallback_allowed",
        "model_invocation_allowed",
        "prompt_execution_allowed",
        "runtime_execution_allowed",
        "archive_writing_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ):
        assert handoff[field] is False


def test_builder_rejects_invalid_handoff_id() -> None:
    (
        boundary,
        slot_manifest,
        policy_manifest,
        assignment_manifest,
        packet,
    ) = _build_sources()

    with pytest.raises(WorkflowFinalHandoffViolation):
        build_workflow_final_handoff(
            handoff_id="invalid handoff",
            review_packet=packet,
            boundary_contract=boundary,
            slot_binding_manifest=slot_manifest,
            policy_eligibility_manifest=policy_manifest,
            assignment_profile_manifest=assignment_manifest,
        )


def test_builder_rejects_tampered_packet() -> None:
    (
        boundary,
        slot_manifest,
        policy_manifest,
        assignment_manifest,
        packet,
    ) = _build_sources()

    packet["automatic_selection_status"] = "ALLOWED"

    with pytest.raises(WorkflowFinalHandoffViolation):
        build_workflow_final_handoff(
            handoff_id="multi.model.handoff.v1",
            review_packet=packet,
            boundary_contract=boundary,
            slot_binding_manifest=slot_manifest,
            policy_eligibility_manifest=policy_manifest,
            assignment_profile_manifest=assignment_manifest,
        )


def test_validation_rejects_automatic_merge() -> None:
    (
        boundary,
        slot_manifest,
        policy_manifest,
        assignment_manifest,
        packet,
    ) = _build_sources()

    handoff = build_workflow_final_handoff(
        handoff_id="multi.model.handoff.v1",
        review_packet=packet,
        boundary_contract=boundary,
        slot_binding_manifest=slot_manifest,
        policy_eligibility_manifest=policy_manifest,
        assignment_profile_manifest=assignment_manifest,
    )

    handoff[
        "main_merge_allowed_without_operator_confirmation"
    ] = True

    errors = validate_workflow_final_handoff(
        handoff,
        review_packet=packet,
        boundary_contract=boundary,
        slot_binding_manifest=slot_manifest,
        policy_eligibility_manifest=policy_manifest,
        assignment_profile_manifest=assignment_manifest,
    )

    assert (
        "main_merge_allowed_without_operator_confirmation_mismatch"
        in errors
    )
    assert (
        "main_merge_allowed_without_operator_confirmation_must_be_false"
        in errors
    )


def test_builder_returns_fresh_action_list() -> None:
    first = _handoff()
    second = _handoff()

    first["allowed_operator_actions"].append(
        "AUTOMATIC_MERGE"
    )

    assert second == _handoff()
    assert first != second


def test_non_mapping_handoff_is_rejected() -> None:
    (
        boundary,
        slot_manifest,
        policy_manifest,
        assignment_manifest,
        packet,
    ) = _build_sources()

    assert validate_workflow_final_handoff(
        [],
        review_packet=packet,
        boundary_contract=boundary,
        slot_binding_manifest=slot_manifest,
        policy_eligibility_manifest=policy_manifest,
        assignment_profile_manifest=assignment_manifest,
    ) == ["handoff_must_be_mapping"]