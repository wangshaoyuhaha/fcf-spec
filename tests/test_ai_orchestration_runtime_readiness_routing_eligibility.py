"""Tests for AI orchestration runtime readiness D3 routing."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    RoutingEligibilityViolation,
    build_machine_readable_role_contract_manifest,
    build_routing_candidate,
    build_routing_eligibility_contract,
    build_runtime_readiness_boundary_contract,
    validate_routing_candidate,
    validate_routing_eligibility_contract,
)


def _role_manifest() -> dict[str, object]:
    return build_machine_readable_role_contract_manifest(
        manifest_id="fcf.runtime.roles.v1",
        boundary_contract=(
            build_runtime_readiness_boundary_contract()
        ),
    )


def _candidate(
    *,
    candidate_id: str = "candidate.openai.v1",
    role_id: str = "market_narrative_context_analyst",
    registered_artifacts_status: str = "VERIFIED",
    privacy_policy_status: str = "ALLOWED",
    licensing_policy_status: str = "ALLOWED",
    health_status: str = "HEALTHY",
    cost_limit_status: str = "WITHIN_LIMIT",
) -> dict[str, object]:
    return build_routing_candidate(
        candidate_id=candidate_id,
        role_id=role_id,
        provider_id="provider.approved.v1",
        model_version_id="model.version.v1",
        prompt_version_id="prompt.version.v1",
        policy_identifier="FCF.POLICY.RUNTIME.ROUTING.V1",
        policy_version="1.0.0",
        policy_digest="sha256.testdigest",
        config_snapshot_id="config.snapshot.v1",
        registered_artifacts_status=(
            registered_artifacts_status
        ),
        privacy_policy_status=privacy_policy_status,
        licensing_policy_status=licensing_policy_status,
        health_status=health_status,
        cost_limit_status=cost_limit_status,
    )


def _contract(
    candidates: list[dict[str, object]],
) -> dict[str, object]:
    return build_routing_eligibility_contract(
        routing_contract_id="fcf.runtime.routing.v1",
        role_manifest=_role_manifest(),
        candidates=candidates,
    )


def test_eligible_candidate_passes_validation() -> None:
    candidate = _candidate()

    assert candidate["eligibility_status"] == (
        "ELIGIBLE_FOR_OPERATOR_REVIEW"
    )
    assert validate_routing_candidate(candidate) == []


def test_degraded_candidate_is_not_selected() -> None:
    candidate = _candidate(
        health_status="DEGRADED",
        cost_limit_status="UNKNOWN",
    )

    assert candidate["eligibility_status"] == "DEGRADED"
    assert candidate["automatic_routing_allowed"] is False
    assert candidate["route_execution_status"] == "NOT_ALLOWED"


def test_blocked_candidate_fails_closed() -> None:
    candidate = _candidate(
        privacy_policy_status="BLOCKED",
        cost_limit_status="EXCEEDED",
    )

    assert candidate["eligibility_status"] == "BLOCKED"
    assert "privacy_policy_blocked" in (
        candidate["blocking_reasons"]
    )
    assert "cost_limit_exceeded" in (
        candidate["blocking_reasons"]
    )


def test_valid_contract_passes_validation() -> None:
    contract = _contract([_candidate()])

    assert validate_routing_eligibility_contract(
        contract
    ) == []


def test_contract_has_no_automatic_selection() -> None:
    contract = _contract([_candidate()])

    assert contract["automatic_routing_status"] == "NOT_ALLOWED"
    assert contract["route_selection_status"] == "NOT_ALLOWED"
    assert contract["winner_selection_status"] == "NOT_ALLOWED"


def test_contract_has_no_model_or_prompt_execution() -> None:
    contract = _contract([_candidate()])

    assert contract["model_invocation_status"] == "NOT_ALLOWED"
    assert contract["prompt_execution_status"] == "NOT_ALLOWED"
    assert contract["runtime_execution_status"] == "NOT_ALLOWED"


def test_mixed_candidates_make_contract_degraded() -> None:
    contract = _contract(
        [
            _candidate(),
            _candidate(
                candidate_id="candidate.degraded.v1",
                health_status="DEGRADED",
            ),
        ]
    )

    assert contract["routing_contract_status"] == "DEGRADED"
    assert contract["eligible_candidate_count"] == 1
    assert contract["degraded_candidate_count"] == 1


def test_all_blocked_candidates_block_contract() -> None:
    contract = _contract(
        [
            _candidate(
                privacy_policy_status="BLOCKED",
            )
        ]
    )

    assert contract["routing_contract_status"] == "BLOCKED"
    assert contract["blocked_candidate_count"] == 1


def test_empty_candidates_block_contract() -> None:
    contract = _contract([])

    assert contract["routing_contract_status"] == "BLOCKED"
    assert contract["candidate_count"] == 0


def test_human_operator_is_not_routable() -> None:
    with pytest.raises(RoutingEligibilityViolation):
        _contract(
            [
                _candidate(
                    role_id="human_operator",
                )
            ]
        )


def test_unregistered_candidate_is_blocked() -> None:
    candidate = _candidate(
        registered_artifacts_status="MISSING",
    )

    assert candidate["eligibility_status"] == "BLOCKED"
    assert "registered_artifacts_not_verified" in (
        candidate["blocking_reasons"]
    )


def test_validation_rejects_automatic_routing() -> None:
    candidate = _candidate()
    candidate["automatic_routing_allowed"] = True

    assert (
        "automatic_routing_allowed_must_be_false"
        in validate_routing_candidate(candidate)
    )


def test_validation_rejects_state_tampering() -> None:
    candidate = _candidate(
        privacy_policy_status="BLOCKED",
    )
    candidate["eligibility_status"] = (
        "ELIGIBLE_FOR_OPERATOR_REVIEW"
    )

    assert "eligibility_status_mismatch" in (
        validate_routing_candidate(candidate)
    )


def test_duplicate_candidate_ids_are_rejected() -> None:
    candidate = _candidate()

    with pytest.raises(RoutingEligibilityViolation):
        _contract([candidate, deepcopy(candidate)])


def test_builder_returns_fresh_nested_containers() -> None:
    first = _contract([_candidate()])
    second = _contract([_candidate()])
    mutated = deepcopy(first)

    mutated["candidates"][0]["blocking_reasons"].append(
        "tampered"
    )

    assert second == _contract([_candidate()])
    assert mutated != second


def test_non_mapping_contract_is_rejected() -> None:
    assert validate_routing_eligibility_contract(
        []
    ) == ["routing_contract_must_be_mapping"]
