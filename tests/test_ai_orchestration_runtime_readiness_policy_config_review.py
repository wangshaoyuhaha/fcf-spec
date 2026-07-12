
"""Tests for AI orchestration runtime readiness D5 review linkage."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    PolicyConfigReviewViolation,
    build_cost_contract,
    build_fallback_contract,
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
    validate_operator_handoff,
    validate_policy_config_snapshot_link,
    validate_runtime_readiness_review_packet,
)


def _chain(
    *,
    policy_status: str = "VERIFIED",
    config_status: str = "VERIFIED",
    health_status: str = "HEALTHY",
) -> tuple[
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
    dict[str, object],
]:
    boundary = build_runtime_readiness_boundary_contract()
    roles = build_machine_readable_role_contract_manifest(
        manifest_id="fcf.runtime.roles.v1",
        boundary_contract=boundary,
    )
    candidate = build_routing_candidate(
        candidate_id="candidate.approved.v1",
        role_id="market_narrative_context_analyst",
        provider_id="provider.approved.v1",
        model_version_id="model.version.v1",
        prompt_version_id="prompt.version.v1",
        policy_identifier="FCF.POLICY.RUNTIME.ROUTING.V1",
        policy_version="1.0.0",
        policy_digest="sha256.routing",
        config_snapshot_id="config.snapshot.v1",
        registered_artifacts_status="VERIFIED",
        privacy_policy_status="ALLOWED",
        licensing_policy_status="ALLOWED",
        health_status=health_status,
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
            response_timeout_ms=3000,
            total_timeout_ms=4000,
        ),
        retry_contract=build_retry_contract(
            max_attempts=2,
            backoff_ms=[100, 200],
            retryable_failure_classes=[
                "NETWORK_ERROR",
                "RATE_LIMIT",
            ],
        ),
        fallback_contract=build_fallback_contract(
            fallback_candidate_ids=[
                "candidate.approved.v1"
            ],
        ),
        cost_contract=build_cost_contract(
            currency="USD",
            per_request_limit_microunits=1000,
            workflow_limit_microunits=5000,
            daily_limit_microunits=10000,
        ),
    )
    link = build_policy_config_snapshot_link(
        link_id="fcf.runtime.policy-config.v1",
        runtime_limit_bundle=limits,
        policy_identifier="FCF.POLICY.RUNTIME.V1",
        policy_version="1.0.0",
        policy_digest="sha256.policy",
        policy_registration_status=policy_status,
        config_snapshot_id="config.snapshot.v1",
        config_version="1.0.0",
        config_digest="sha256.config",
        config_registration_status=config_status,
    )
    return boundary, roles, routing, limits, link


def _packet(
    *,
    policy_status: str = "VERIFIED",
    config_status: str = "VERIFIED",
    health_status: str = "HEALTHY",
) -> dict[str, object]:
    boundary, roles, routing, limits, link = _chain(
        policy_status=policy_status,
        config_status=config_status,
        health_status=health_status,
    )
    return build_runtime_readiness_review_packet(
        review_packet_id="fcf.runtime.review.v1",
        boundary_contract=boundary,
        role_manifest=roles,
        routing_contract=routing,
        runtime_limit_bundle=limits,
        policy_config_link=link,
    )


def test_verified_link_passes_validation() -> None:
    link = _chain()[-1]

    assert link["link_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert validate_policy_config_snapshot_link(link) == []


def test_policy_and_config_versions_are_preserved() -> None:
    link = _chain()[-1]

    assert link["policy_version"] == "1.0.0"
    assert link["policy_digest"] == "sha256.policy"
    assert link["config_version"] == "1.0.0"
    assert link["config_digest"] == "sha256.config"


def test_missing_policy_blocks_link() -> None:
    link = _chain(policy_status="MISSING")[-1]

    assert link["link_status"] == "BLOCKED"
    assert "policy_registration_missing" in link[
        "blocking_reasons"
    ]


def test_mismatched_config_blocks_link() -> None:
    link = _chain(config_status="MISMATCH")[-1]

    assert link["link_status"] == "BLOCKED"
    assert "config_registration_mismatch" in link[
        "blocking_reasons"
    ]


def test_degraded_limit_bundle_degrades_link() -> None:
    link = _chain(health_status="DEGRADED")[-1]

    assert link["link_status"] == "DEGRADED"
    assert "runtime_limit_bundle_degraded" in link[
        "degradation_reasons"
    ]


def test_policy_activation_and_runtime_enforcement_are_inactive() -> None:
    link = _chain()[-1]

    assert link["automatic_policy_activation_status"] == (
        "NOT_ALLOWED"
    )
    assert link["runtime_enforcement_status"] == "NOT_ACTIVE"


def test_valid_review_packet_passes_validation() -> None:
    packet = _packet()

    assert packet["overall_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert validate_runtime_readiness_review_packet(
        packet
    ) == []


def test_review_packet_preserves_full_chain_links() -> None:
    packet = _packet()

    assert packet["source_boundary_contract_version"] == "1.0.0"
    assert packet["source_role_manifest_id"] == (
        "fcf.runtime.roles.v1"
    )
    assert packet["source_routing_contract_id"] == (
        "fcf.runtime.routing.v1"
    )
    assert packet["source_runtime_limit_bundle_id"] == (
        "fcf.runtime.limits.v1"
    )
    assert packet["source_policy_config_link_id"] == (
        "fcf.runtime.policy-config.v1"
    )


def test_blocked_link_blocks_review_packet() -> None:
    packet = _packet(policy_status="MISSING")

    assert packet["overall_status"] == "BLOCKED"


def test_degraded_link_degrades_review_packet() -> None:
    packet = _packet(health_status="DEGRADED")

    assert packet["overall_status"] == "DEGRADED"


def test_review_packet_cannot_archive_or_execute() -> None:
    packet = _packet()

    assert packet["archive_authorization_status"] == (
        "NOT_GRANTED"
    )
    assert packet["archive_writing_status"] == "NOT_ALLOWED"
    assert packet["model_invocation_status"] == "NOT_ALLOWED"
    assert packet["prompt_execution_status"] == "NOT_ALLOWED"
    assert packet["runtime_execution_status"] == "NOT_ALLOWED"


def test_valid_operator_handoff_passes_validation() -> None:
    handoff = build_operator_handoff(
        handoff_id="fcf.runtime.handoff.v1",
        review_packet=_packet(),
    )

    assert handoff["handoff_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert validate_operator_handoff(handoff) == []


def test_operator_handoff_is_manual_only() -> None:
    handoff = build_operator_handoff(
        handoff_id="fcf.runtime.handoff.v1",
        review_packet=_packet(),
    )

    assert handoff["operator_action_required"] is True
    assert handoff["manual_archive_authorization_status"] == (
        "NOT_GRANTED"
    )
    assert handoff["automatic_archive_status"] == "NOT_ALLOWED"
    assert handoff["automatic_routing_status"] == "NOT_ALLOWED"


def test_invalid_chain_linkage_is_rejected() -> None:
    boundary, roles, routing, limits, link = _chain()
    tampered = deepcopy(link)
    tampered["source_runtime_limit_bundle_id"] = (
        "fcf.runtime.limits.other"
    )

    with pytest.raises(PolicyConfigReviewViolation):
        build_runtime_readiness_review_packet(
            review_packet_id="fcf.runtime.review.v1",
            boundary_contract=boundary,
            role_manifest=roles,
            routing_contract=routing,
            runtime_limit_bundle=limits,
            policy_config_link=tampered,
        )


def test_invalid_identifier_is_rejected() -> None:
    _, _, _, limits, _ = _chain()

    with pytest.raises(PolicyConfigReviewViolation):
        build_policy_config_snapshot_link(
            link_id="invalid link id",
            runtime_limit_bundle=limits,
            policy_identifier="FCF.POLICY.RUNTIME.V1",
            policy_version="1.0.0",
            policy_digest="sha256.policy",
            policy_registration_status="VERIFIED",
            config_snapshot_id="config.snapshot.v1",
            config_version="1.0.0",
            config_digest="sha256.config",
            config_registration_status="VERIFIED",
        )


def test_builders_return_fresh_nested_containers() -> None:
    first = _packet()
    second = _packet()
    mutated = deepcopy(first)

    mutated["component_statuses"][
        "policy_config_link_status"
    ] = "BLOCKED"

    assert second == _packet()
    assert mutated != second


def test_non_mapping_values_are_rejected() -> None:
    assert validate_policy_config_snapshot_link([]) == [
        "policy_config_link_must_be_mapping"
    ]
    assert validate_runtime_readiness_review_packet([]) == [
        "review_packet_must_be_mapping"
    ]
    assert validate_operator_handoff([]) == [
        "operator_handoff_must_be_mapping"
    ]
