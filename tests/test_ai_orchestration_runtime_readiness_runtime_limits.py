"""Tests for AI orchestration runtime readiness D4 limits."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    RuntimeLimitContractViolation,
    build_cost_contract,
    build_fallback_contract,
    build_machine_readable_role_contract_manifest,
    build_retry_contract,
    build_routing_candidate,
    build_routing_eligibility_contract,
    build_runtime_limit_contract_bundle,
    build_runtime_readiness_boundary_contract,
    build_timeout_contract,
    validate_cost_contract,
    validate_fallback_contract,
    validate_retry_contract,
    validate_runtime_limit_contract_bundle,
    validate_timeout_contract,
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
    candidate_id: str = "candidate.primary.v1",
    health_status: str = "HEALTHY",
) -> dict[str, object]:
    return build_routing_candidate(
        candidate_id=candidate_id,
        role_id="market_narrative_context_analyst",
        provider_id="provider.approved.v1",
        model_version_id="model.version.v1",
        prompt_version_id="prompt.version.v1",
        policy_identifier="FCF.POLICY.RUNTIME.ROUTING.V1",
        policy_version="1.0.0",
        policy_digest="sha256.testdigest",
        config_snapshot_id="config.snapshot.v1",
        registered_artifacts_status="VERIFIED",
        privacy_policy_status="ALLOWED",
        licensing_policy_status="ALLOWED",
        health_status=health_status,
        cost_limit_status="WITHIN_LIMIT",
    )


def _routing_contract(
    *,
    health_status: str = "HEALTHY",
) -> dict[str, object]:
    return build_routing_eligibility_contract(
        routing_contract_id="fcf.runtime.routing.v1",
        role_manifest=_role_manifest(),
        candidates=[
            _candidate(health_status=health_status),
            _candidate(
                candidate_id="candidate.fallback.v1",
            ),
        ],
    )


def _timeout() -> dict[str, object]:
    return build_timeout_contract(
        connect_timeout_ms=1000,
        response_timeout_ms=4000,
        total_timeout_ms=5000,
    )


def _retry() -> dict[str, object]:
    return build_retry_contract(
        max_attempts=2,
        backoff_ms=[500, 1000],
        retryable_failure_classes=[
            "PROVIDER_TRANSIENT_FAILURE",
            "RATE_LIMIT_TRANSIENT_FAILURE",
        ],
    )


def _fallback() -> dict[str, object]:
    return build_fallback_contract(
        fallback_candidate_ids=[
            "candidate.fallback.v1",
        ]
    )


def _cost() -> dict[str, object]:
    return build_cost_contract(
        currency="USD",
        per_request_limit_microunits=1_000_000,
        workflow_limit_microunits=5_000_000,
        daily_limit_microunits=20_000_000,
    )


def _bundle(
    *,
    health_status: str = "HEALTHY",
) -> dict[str, object]:
    return build_runtime_limit_contract_bundle(
        runtime_limit_bundle_id="fcf.runtime.limits.v1",
        routing_contract=_routing_contract(
            health_status=health_status
        ),
        timeout_contract=_timeout(),
        retry_contract=_retry(),
        fallback_contract=_fallback(),
        cost_contract=_cost(),
    )


def test_individual_contracts_pass_validation() -> None:
    assert validate_timeout_contract(_timeout()) == []
    assert validate_retry_contract(_retry()) == []
    assert validate_fallback_contract(_fallback()) == []
    assert validate_cost_contract(_cost()) == []


def test_valid_bundle_passes_validation() -> None:
    assert validate_runtime_limit_contract_bundle(
        _bundle()
    ) == []


def test_bundle_is_ready_for_policy_config_linkage() -> None:
    bundle = _bundle()

    assert bundle["bundle_status"] == (
        "READY_FOR_POLICY_CONFIG_LINKAGE"
    )


def test_degraded_routing_degrades_bundle() -> None:
    bundle = _bundle(health_status="DEGRADED")

    assert bundle["bundle_status"] == "DEGRADED"


def test_timeout_requires_total_budget() -> None:
    with pytest.raises(RuntimeLimitContractViolation):
        build_timeout_contract(
            connect_timeout_ms=1000,
            response_timeout_ms=4000,
            total_timeout_ms=4999,
        )


def test_retry_attempts_are_bounded() -> None:
    with pytest.raises(RuntimeLimitContractViolation):
        build_retry_contract(
            max_attempts=4,
            backoff_ms=[100, 200, 300, 400],
            retryable_failure_classes=[
                "PROVIDER_TRANSIENT_FAILURE"
            ],
        )


def test_retry_backoff_count_matches_attempts() -> None:
    with pytest.raises(RuntimeLimitContractViolation):
        build_retry_contract(
            max_attempts=2,
            backoff_ms=[500],
            retryable_failure_classes=[
                "PROVIDER_TRANSIENT_FAILURE"
            ],
        )


def test_fallback_is_operator_only() -> None:
    fallback = _fallback()

    assert fallback["operator_review_required"] is True
    assert fallback["automatic_fallback_status"] == "NOT_ALLOWED"
    assert fallback["automatic_switching_status"] == "NOT_ALLOWED"


def test_unknown_cost_and_exceeded_cost_block() -> None:
    cost = _cost()

    assert cost["unknown_cost_action"] == "BLOCK"
    assert cost["limit_exceeded_action"] == "BLOCK"
    assert cost["automatic_cost_override_status"] == (
        "NOT_ALLOWED"
    )


def test_cost_limit_order_is_required() -> None:
    with pytest.raises(RuntimeLimitContractViolation):
        build_cost_contract(
            currency="USD",
            per_request_limit_microunits=10_000_000,
            workflow_limit_microunits=5_000_000,
            daily_limit_microunits=20_000_000,
        )


def test_fallback_candidate_must_exist_in_routing() -> None:
    with pytest.raises(RuntimeLimitContractViolation):
        build_runtime_limit_contract_bundle(
            runtime_limit_bundle_id="fcf.runtime.limits.v1",
            routing_contract=_routing_contract(),
            timeout_contract=_timeout(),
            retry_contract=_retry(),
            fallback_contract=build_fallback_contract(
                fallback_candidate_ids=[
                    "candidate.unknown.v1"
                ]
            ),
            cost_contract=_cost(),
        )


def test_bundle_forbids_runtime_actions() -> None:
    bundle = _bundle()

    assert bundle["model_invocation_status"] == "NOT_ALLOWED"
    assert bundle["prompt_execution_status"] == "NOT_ALLOWED"
    assert bundle["automatic_routing_status"] == "NOT_ALLOWED"
    assert bundle["automatic_fallback_status"] == "NOT_ALLOWED"
    assert bundle["automatic_retry_status"] == "NOT_ALLOWED"
    assert bundle["runtime_execution_status"] == "NOT_ALLOWED"


def test_validation_rejects_automatic_retry() -> None:
    bundle = _bundle()
    bundle["automatic_retry_status"] = "ALLOWED"

    assert "automatic_retry_status_invalid" in (
        validate_runtime_limit_contract_bundle(bundle)
    )


def test_validation_rejects_cost_override() -> None:
    cost = _cost()
    cost["automatic_cost_override_status"] = "ALLOWED"

    assert "automatic_cost_override_status_invalid" in (
        validate_cost_contract(cost)
    )


def test_builder_returns_fresh_nested_contracts() -> None:
    first = _bundle()
    second = _bundle()
    mutated = deepcopy(first)

    mutated["retry_contract"]["backoff_ms"].append(2000)

    assert second == _bundle()
    assert mutated != second


def test_non_mapping_bundle_is_rejected() -> None:
    assert validate_runtime_limit_contract_bundle(
        []
    ) == ["runtime_limit_bundle_must_be_mapping"]
