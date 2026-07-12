"""Tests for AI orchestration runtime readiness D1."""

from copy import deepcopy

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    APP_ID,
    READINESS_MODE,
    REQUIRED_POLICY_IDENTIFIERS,
    RUNTIME_READINESS_STATES,
    STAGE_ID,
    build_runtime_readiness_boundary_contract,
    validate_runtime_readiness_boundary_contract,
)


def test_contract_identity() -> None:
    contract = build_runtime_readiness_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["readiness_mode"] == READINESS_MODE


def test_valid_contract_passes_validation() -> None:
    contract = build_runtime_readiness_boundary_contract()

    assert validate_runtime_readiness_boundary_contract(
        contract
    ) == []


def test_contract_is_readiness_only() -> None:
    contract = build_runtime_readiness_boundary_contract()
    flags = contract["safety_flags"]

    assert flags["readiness_only"] is True
    assert flags["paper_only"] is True
    assert flags["sidecar_only"] is True


def test_blocked_and_degraded_states_are_required() -> None:
    contract = build_runtime_readiness_boundary_contract()

    assert contract["runtime_readiness_states"] == list(
        RUNTIME_READINESS_STATES
    )
    assert "BLOCKED" in contract["runtime_readiness_states"]
    assert "DEGRADED" in contract["runtime_readiness_states"]


def test_policy_identifiers_are_machine_readable() -> None:
    contract = build_runtime_readiness_boundary_contract()

    assert contract["required_policy_identifiers"] == list(
        REQUIRED_POLICY_IDENTIFIERS
    )
    assert (
        "FCF.POLICY.RUNTIME.NO_MODEL_INVOCATION"
        in contract["required_policy_identifiers"]
    )
    assert (
        "FCF.POLICY.RUNTIME.CONFIG_SNAPSHOT_REQUIRED"
        in contract["required_policy_identifiers"]
    )


def test_policy_and_config_linkage_is_required() -> None:
    contract = build_runtime_readiness_boundary_contract()
    linkage = contract["policy_config_linkage"]

    assert linkage["policy_identifier_required"] is True
    assert linkage["policy_version_required"] is True
    assert linkage["policy_digest_required"] is True
    assert linkage["config_snapshot_id_required"] is True
    assert linkage["fail_closed_behavior_required"] is True
    assert linkage["runtime_policy_enforcement_active"] is False


def test_model_prompt_and_routing_are_forbidden() -> None:
    contract = build_runtime_readiness_boundary_contract()
    flags = contract["safety_flags"]

    assert flags["actual_model_invocation_allowed"] is False
    assert flags["prompt_execution_allowed"] is False
    assert flags["automatic_routing_allowed"] is False


def test_archive_and_learning_activation_are_forbidden() -> None:
    contract = build_runtime_readiness_boundary_contract()
    flags = contract["safety_flags"]

    assert flags["automatic_archive_allowed"] is False
    assert flags["archive_writing_allowed"] is False
    assert flags["automatic_learning_activation_allowed"] is False
    assert (
        flags["automatic_champion_promotion_allowed"]
        is False
    )


def test_execution_and_core_mutation_are_forbidden() -> None:
    contract = build_runtime_readiness_boundary_contract()
    flags = contract["safety_flags"]

    assert flags["real_execution_allowed"] is False
    assert flags["trade_action_allowed"] is False
    assert flags["trading_api_allowed"] is False
    assert flags["trading_credentials_allowed"] is False
    assert flags["core_mutation_allowed"] is False
    assert flags["p48_expansion_allowed"] is False


def test_existing_authority_is_preserved() -> None:
    contract = build_runtime_readiness_boundary_contract()
    overlap = contract["overlap_policy"]

    assert overlap["frozen_core_remains_authoritative"] is True
    assert overlap["existing_sidecars_remain_authoritative"] is True
    assert overlap["runtime_orchestrator_created"] is False
    assert overlap["runtime_workflow_execution_added"] is False


def test_validation_rejects_model_invocation() -> None:
    contract = build_runtime_readiness_boundary_contract()
    contract["safety_flags"][
        "actual_model_invocation_allowed"
    ] = True

    assert (
        "actual_model_invocation_allowed_must_be_false"
        in validate_runtime_readiness_boundary_contract(contract)
    )


def test_validation_rejects_policy_activation() -> None:
    contract = build_runtime_readiness_boundary_contract()
    contract["policy_config_linkage"][
        "automatic_policy_activation_allowed"
    ] = True

    assert "policy_config_linkage_invalid" in (
        validate_runtime_readiness_boundary_contract(contract)
    )


def test_builder_returns_fresh_containers() -> None:
    first = build_runtime_readiness_boundary_contract()
    second = build_runtime_readiness_boundary_contract()
    mutated = deepcopy(first)

    mutated["allowed_inputs"].append("UNREGISTERED_INPUT")
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == build_runtime_readiness_boundary_contract()
    assert mutated != second


def test_non_mapping_contract_is_rejected() -> None:
    assert validate_runtime_readiness_boundary_contract(
        []
    ) == ["contract_must_be_mapping"]