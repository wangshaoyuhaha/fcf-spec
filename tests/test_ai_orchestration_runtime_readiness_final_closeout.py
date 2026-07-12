"""Tests for AI orchestration runtime readiness D6 closeout."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    FINAL_CLOSEOUT_TARGETS,
    FINAL_CLOSEOUT_VERSION,
    FinalCloseoutViolation,
    build_cost_contract,
    build_fallback_contract,
    build_final_readiness_closeout,
    build_machine_readable_role_contract_manifest,
    build_operator_handoff,
    build_policy_config_snapshot_link,
    build_retry_contract,
    build_routing_candidate,
    build_routing_eligibility_contract,
    build_runtime_limit_contract_bundle,
    build_runtime_readiness_boundary_contract,
    build_runtime_readiness_review_packet,
    build_timeout_contract,
    validate_final_readiness_closeout,
)


def _artifacts(
    *,
    policy_registration_status: str = "VERIFIED",
    config_registration_status: str = "VERIFIED",
) -> tuple[dict[str, object], dict[str, object]]:
    boundary = build_runtime_readiness_boundary_contract()
    roles = build_machine_readable_role_contract_manifest(
        manifest_id="fcf.runtime.roles.v1",
        boundary_contract=boundary,
    )
    candidate = build_routing_candidate(
        candidate_id="candidate.primary.v1",
        role_id="market_narrative_context_analyst",
        provider_id="provider.approved.v1",
        model_version_id="model.version.v1",
        prompt_version_id="prompt.version.v1",
        policy_identifier="FCF.POLICY.RUNTIME.ROUTING.V1",
        policy_version="1.0.0",
        policy_digest="sha256.routingdigest",
        config_snapshot_id="config.snapshot.v1",
        registered_artifacts_status="VERIFIED",
        privacy_policy_status="ALLOWED",
        licensing_policy_status="ALLOWED",
        health_status="HEALTHY",
        cost_limit_status="WITHIN_LIMIT",
    )
    routing = build_routing_eligibility_contract(
        routing_contract_id="fcf.runtime.routing.v1",
        role_manifest=roles,
        candidates=[candidate],
    )
    limits = build_runtime_limit_contract_bundle(
        runtime_limit_bundle_id="fcf.runtime.limits.v1",
        routing_contract=routing,
        timeout_contract=build_timeout_contract(
            connect_timeout_ms=1000,
            response_timeout_ms=5000,
            total_timeout_ms=6000,
        ),
        retry_contract=build_retry_contract(
            max_attempts=2,
            backoff_ms=[100, 200],
            retryable_failure_classes=[
                "TIMEOUT",
                "TRANSIENT_NETWORK",
            ],
        ),
        fallback_contract=build_fallback_contract(
            fallback_candidate_ids=[
                "candidate.primary.v1",
            ]
        ),
        cost_contract=build_cost_contract(
            currency="USD",
            per_request_limit_microunits=1000,
            workflow_limit_microunits=5000,
            daily_limit_microunits=50000,
        ),
    )
    link = build_policy_config_snapshot_link(
        link_id="fcf.runtime.policy.config.v1",
        runtime_limit_bundle=limits,
        policy_identifier="FCF.POLICY.RUNTIME.V1",
        policy_version="1.0.0",
        policy_digest="sha256.policydigest",
        policy_registration_status=(
            policy_registration_status
        ),
        config_snapshot_id="config.snapshot.v1",
        config_version="1.0.0",
        config_digest="sha256.configdigest",
        config_registration_status=(
            config_registration_status
        ),
    )
    packet = build_runtime_readiness_review_packet(
        review_packet_id="fcf.runtime.review.v1",
        boundary_contract=boundary,
        role_manifest=roles,
        routing_contract=routing,
        runtime_limit_bundle=limits,
        policy_config_link=link,
    )
    handoff = build_operator_handoff(
        handoff_id="fcf.runtime.handoff.v1",
        review_packet=packet,
    )
    return packet, handoff


def _closeout(
    *,
    policy_registration_status: str = "VERIFIED",
    config_registration_status: str = "VERIFIED",
) -> dict[str, object]:
    packet, handoff = _artifacts(
        policy_registration_status=(
            policy_registration_status
        ),
        config_registration_status=(
            config_registration_status
        ),
    )
    return build_final_readiness_closeout(
        closeout_id="fcf.runtime.closeout.v1",
        review_packet=packet,
        operator_handoff=handoff,
    )


def test_valid_closeout_passes_validation() -> None:
    closeout = _closeout()

    assert validate_final_readiness_closeout(closeout) == []


def test_closeout_identity_and_version() -> None:
    closeout = _closeout()

    assert closeout["closeout_id"] == "fcf.runtime.closeout.v1"
    assert closeout["closeout_version"] == (
        FINAL_CLOSEOUT_VERSION
    )
    assert closeout["implementation_status"] == (
        "D1_D6_IMPLEMENTED"
    )


def test_closeout_waits_for_operator_review() -> None:
    closeout = _closeout()

    assert closeout["overall_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert closeout["handoff_status"] == (
        "WAITING_FOR_OPERATOR_REVIEW"
    )
    assert closeout["operator_review_required"] is True
    assert closeout["operator_review_bypass_allowed"] is False


def test_main_merge_and_sync_are_not_authorized() -> None:
    closeout = _closeout()

    assert closeout["main_merge_authorization_status"] == (
        "NOT_GRANTED"
    )
    assert closeout["control_center_sync_status"] == (
        "NOT_STARTED"
    )
    assert closeout["final_current_state_status"] == (
        "NOT_STARTED"
    )


def test_runtime_and_model_actions_remain_forbidden() -> None:
    closeout = _closeout()

    fields = (
        "model_invocation_status",
        "prompt_execution_status",
        "automatic_routing_status",
        "automatic_fallback_status",
        "automatic_retry_status",
        "automatic_policy_activation_status",
        "automatic_learning_activation_status",
        "automatic_champion_promotion_status",
        "shadow_trading_status",
        "runtime_execution_status",
        "real_execution_status",
        "trading_api_status",
        "trading_credential_access_status",
        "core_mutation_status",
        "p48_expansion_status",
    )

    assert all(
        closeout[field] == "NOT_ALLOWED"
        for field in fields
    )


def test_archive_release_and_deploy_remain_closed() -> None:
    closeout = _closeout()

    assert closeout["manual_archive_authorization_status"] == (
        "NOT_GRANTED"
    )
    assert closeout["automatic_archive_status"] == "NOT_ALLOWED"
    assert closeout["archive_writing_status"] == "NOT_ALLOWED"
    assert closeout["tag_status"] == "NONE"
    assert closeout["release_status"] == "NONE"
    assert closeout["deploy_status"] == "NONE"


def test_target_consumers_are_fixed() -> None:
    closeout = _closeout()

    assert closeout["target_consumers"] == list(
        FINAL_CLOSEOUT_TARGETS
    )


def test_hash_is_deterministic() -> None:
    first = _closeout()
    second = _closeout()

    assert first["closeout_hash"] == second["closeout_hash"]
    assert len(first["closeout_hash"]) == 64


def test_snapshots_are_deep_copied() -> None:
    packet, handoff = _artifacts()
    closeout = build_final_readiness_closeout(
        closeout_id="fcf.runtime.closeout.v1",
        review_packet=packet,
        operator_handoff=handoff,
    )

    packet["component_statuses"][
        "boundary_contract_status"
    ] = "TAMPERED"
    handoff["allowed_operator_actions"].append("TAMPERED")

    assert closeout["review_packet_snapshot"][
        "component_statuses"
    ]["boundary_contract_status"] == "VALID"
    assert "TAMPERED" not in closeout[
        "operator_handoff_snapshot"
    ]["allowed_operator_actions"]


def test_blocked_status_propagates() -> None:
    closeout = _closeout(
        policy_registration_status="MISSING"
    )

    assert closeout["overall_status"] == "BLOCKED"
    assert closeout["handoff_status"] == "BLOCKED"


def test_degraded_status_propagates() -> None:
    packet, handoff = _artifacts()
    packet = deepcopy(packet)
    handoff = deepcopy(handoff)

    packet["component_statuses"][
        "runtime_limit_bundle_status"
    ] = "DEGRADED"
    packet["overall_status"] = "DEGRADED"
    handoff["overall_status"] = "DEGRADED"
    handoff["handoff_status"] = "DEGRADED"

    closeout = build_final_readiness_closeout(
        closeout_id="fcf.runtime.closeout.v1",
        review_packet=packet,
        operator_handoff=handoff,
    )

    assert closeout["handoff_status"] == "DEGRADED"


def test_invalid_handoff_linkage_is_rejected() -> None:
    packet, handoff = _artifacts()
    handoff["source_review_packet_id"] = (
        "fcf.runtime.review.other"
    )

    with pytest.raises(FinalCloseoutViolation):
        build_final_readiness_closeout(
            closeout_id="fcf.runtime.closeout.v1",
            review_packet=packet,
            operator_handoff=handoff,
        )


def test_validation_rejects_operator_bypass() -> None:
    closeout = _closeout()
    closeout["operator_review_bypass_allowed"] = True

    assert (
        "operator_review_bypass_allowed_invalid"
        in validate_final_readiness_closeout(closeout)
    )


def test_validation_rejects_hash_tampering() -> None:
    closeout = _closeout()
    closeout["overall_status"] = "BLOCKED"

    assert "closeout_hash_mismatch" in (
        validate_final_readiness_closeout(closeout)
    )


def test_validation_rejects_forbidden_action_field() -> None:
    closeout = _closeout()
    closeout["trade_instruction"] = "DO_NOT_ALLOW"

    errors = validate_final_readiness_closeout(closeout)

    assert (
        "final_closeout_fields_must_match_schema"
        in errors
    )
    assert "forbidden_action_field:trade_instruction" in errors


def test_builder_returns_fresh_nested_containers() -> None:
    first = _closeout()
    second = _closeout()

    first["review_packet_snapshot"]["component_statuses"][
        "boundary_contract_status"
    ] = "TAMPERED"

    assert second == _closeout()
    assert first != second


def test_non_mapping_closeout_is_rejected() -> None:
    assert validate_final_readiness_closeout(
        []
    ) == ["final_closeout_must_be_mapping"]
