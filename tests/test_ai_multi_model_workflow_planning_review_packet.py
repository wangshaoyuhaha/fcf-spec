"""Tests for multi-model workflow planning D5."""

from copy import deepcopy

from fcf.sidecars.ai_multi_model_workflow_planning import (
    MODEL_SLOT_TYPES,
    REVIEW_PACKET_STAGE_ID,
    build_assignment_profile_manifest,
    build_model_slot_assignment,
    build_multi_model_workflow_boundary_contract,
    build_policy_eligibility_manifest,
    build_role_model_slot_binding_manifest,
    build_workflow_review_packet,
    validate_workflow_review_packet,
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


def _boundary() -> dict[str, object]:
    return build_multi_model_workflow_boundary_contract()


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
        boundary_contract=_boundary(),
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


def _policy_manifest(
    *,
    candidates: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    return build_policy_eligibility_manifest(
        manifest_id="multi.model.policy.v1",
        slot_binding_manifest=_slot_manifest(),
        routing_candidates=(
            _candidates()
            if candidates is None
            else candidates
        ),
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


def _assignment_manifest(
    *,
    policy_manifest: dict[str, object] | None = None,
    health_status: str = "HEALTHY",
) -> dict[str, object]:
    policy = (
        _policy_manifest()
        if policy_manifest is None
        else policy_manifest
    )

    metadata: dict[str, dict[str, str]] = {}
    bundles: dict[str, dict[str, object]] = {}
    bundle = _runtime_bundle(
        health_status=health_status
    )

    for evaluation in policy["evaluations"]:
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
        bundles[key] = deepcopy(bundle)

    return build_assignment_profile_manifest(
        manifest_id="multi.model.assignments.v1",
        policy_eligibility_manifest=policy,
        profile_metadata_by_role_slot=metadata,
        runtime_limit_bundles_by_role_slot=bundles,
    )


def _packet(
    *,
    policy_manifest: dict[str, object] | None = None,
    assignment_manifest: dict[str, object] | None = None,
) -> dict[str, object]:
    policy = (
        _policy_manifest()
        if policy_manifest is None
        else policy_manifest
    )
    assignment = (
        _assignment_manifest(
            policy_manifest=policy
        )
        if assignment_manifest is None
        else assignment_manifest
    )

    return build_workflow_review_packet(
        review_packet_id="multi.model.review.v1",
        boundary_contract=_boundary(),
        slot_binding_manifest=_slot_manifest(),
        policy_eligibility_manifest=policy,
        assignment_profile_manifest=assignment,
    )


def test_valid_packet_passes_validation() -> None:
    policy = _policy_manifest()
    assignment = _assignment_manifest(
        policy_manifest=policy
    )
    packet = _packet(
        policy_manifest=policy,
        assignment_manifest=assignment,
    )

    assert validate_workflow_review_packet(
        packet,
        boundary_contract=_boundary(),
        slot_binding_manifest=_slot_manifest(),
        policy_eligibility_manifest=policy,
        assignment_profile_manifest=assignment,
    ) == []


def test_d5_identity_is_locked() -> None:
    packet = _packet()

    assert packet["stage_id"] == REVIEW_PACKET_STAGE_ID
    assert packet["planning_mode"] == "PLANNING_ONLY"
    assert packet["policy_authority"] == (
        "DETERMINISTIC_POLICY_ONLY"
    )


def test_source_chain_is_preserved() -> None:
    packet = _packet()

    assert packet["source_contract_id"] == (
        _boundary()["contract_id"]
    )
    assert packet["source_slot_manifest_id"] == (
        _slot_manifest()["manifest_id"]
    )
    assert packet["source_policy_manifest_id"] == (
        _policy_manifest()["manifest_id"]
    )


def test_ready_packet_requires_operator_review() -> None:
    packet = _packet()

    assert packet["overall_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )
    assert packet["operator_decision_status"] == "PENDING"


def test_degraded_assignments_create_warnings() -> None:
    policy = _policy_manifest()
    assignment = _assignment_manifest(
        policy_manifest=policy,
        health_status="DEGRADED",
    )
    packet = _packet(
        policy_manifest=policy,
        assignment_manifest=assignment,
    )

    assert packet["overall_status"] == "DEGRADED"
    assert packet["warnings"]
    assert packet["blocking_reasons"] == []


def test_all_blocked_assignments_block_packet() -> None:
    policy = _policy_manifest(candidates=[])
    assignment = _assignment_manifest(
        policy_manifest=policy
    )
    packet = _packet(
        policy_manifest=policy,
        assignment_manifest=assignment,
    )

    assert packet["overall_status"] == "BLOCKED"
    assert packet["blocked_count"] == (
        packet["assignment_count"]
    )
    assert packet["blocking_reasons"]


def test_automatic_actions_remain_blocked() -> None:
    packet = _packet()

    for field in (
        "automatic_selection_status",
        "automatic_switching_status",
        "automatic_routing_status",
        "automatic_retry_status",
        "automatic_fallback_status",
        "model_invocation_status",
        "prompt_execution_status",
        "runtime_execution_status",
        "archive_writing_status",
        "real_execution_status",
    ):
        assert packet[field] == "NOT_ALLOWED"


def test_validation_rejects_automatic_selection() -> None:
    policy = _policy_manifest()
    assignment = _assignment_manifest(
        policy_manifest=policy
    )
    packet = _packet(
        policy_manifest=policy,
        assignment_manifest=assignment,
    )
    packet["automatic_selection_status"] = "ALLOWED"

    errors = validate_workflow_review_packet(
        packet,
        boundary_contract=_boundary(),
        slot_binding_manifest=_slot_manifest(),
        policy_eligibility_manifest=policy,
        assignment_profile_manifest=assignment,
    )

    assert "automatic_selection_status_mismatch" in errors
    assert "automatic_selection_status_invalid" in errors


def test_validation_rejects_operator_auto_approval() -> None:
    policy = _policy_manifest()
    assignment = _assignment_manifest(
        policy_manifest=policy
    )
    packet = _packet(
        policy_manifest=policy,
        assignment_manifest=assignment,
    )
    packet["operator_decision_status"] = "APPROVED"

    errors = validate_workflow_review_packet(
        packet,
        boundary_contract=_boundary(),
        slot_binding_manifest=_slot_manifest(),
        policy_eligibility_manifest=policy,
        assignment_profile_manifest=assignment,
    )

    assert "operator_decision_status_mismatch" in errors
    assert "operator_decision_status_invalid" in errors


def test_packet_returns_fresh_reason_lists() -> None:
    first = _packet()
    second = _packet()

    first["warnings"].append("mutated.warning")
    first["blocking_reasons"].append("mutated.block")

    assert second == _packet()
    assert first != second


def test_non_mapping_packet_is_rejected() -> None:
    assert validate_workflow_review_packet(
        [],
        boundary_contract=_boundary(),
        slot_binding_manifest=_slot_manifest(),
        policy_eligibility_manifest=_policy_manifest(),
        assignment_profile_manifest=(
            _assignment_manifest()
        ),
    ) == ["review_packet_must_be_mapping"]