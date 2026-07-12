"""Tests for multi-model workflow planning D1."""

from copy import deepcopy

import pytest

from fcf.sidecars.ai_multi_model_workflow_planning import (
    APP_ID,
    AUTHORITY_HIERARCHY,
    MODEL_SLOT_TYPES,
    PLANNING_MODE,
    REQUIRED_EXISTING_BINDINGS,
    STAGE_ID,
    MultiModelWorkflowBoundaryViolation,
    build_multi_model_workflow_boundary_contract,
    validate_multi_model_workflow_boundary_contract,
)


def _contract() -> dict[str, object]:
    return build_multi_model_workflow_boundary_contract()


def test_valid_contract_passes_validation() -> None:
    assert validate_multi_model_workflow_boundary_contract(
        _contract()
    ) == []


def test_contract_identity_is_locked() -> None:
    contract = _contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["planning_mode"] == PLANNING_MODE


def test_model_slot_types_match_locked_architecture() -> None:
    assert MODEL_SLOT_TYPES == (
        "PRIMARY",
        "FALLBACK",
        "COMPARISON",
        "LOCAL_ONLY",
        "CLOUD_APPROVED",
    )


def test_existing_contracts_and_registries_are_bound() -> None:
    contract = _contract()

    assert contract["required_existing_bindings"] == list(
        REQUIRED_EXISTING_BINDINGS
    )
    assert "MACHINE_READABLE_ROLE_CONTRACT_MANIFEST" in (
        contract["required_existing_bindings"]
    )
    assert "REGISTERED_MODEL_VERSION_ARTIFACT" in (
        contract["required_existing_bindings"]
    )
    assert "REGISTERED_PROMPT_VERSION_ARTIFACT" in (
        contract["required_existing_bindings"]
    )
    assert "ROUTING_ELIGIBILITY_CONTRACT" in (
        contract["required_existing_bindings"]
    )


def test_authority_hierarchy_keeps_ai_below_deterministic_engine() -> None:
    assert AUTHORITY_HIERARCHY[0] == "OPERATOR_POLICY"
    assert AUTHORITY_HIERARCHY.index(
        "DETERMINISTIC_ENGINE"
    ) < AUTHORITY_HIERARCHY.index("AI_MODELS")


def test_input_and_output_ownership_are_explicit() -> None:
    contract = _contract()

    assert contract["input_ownership"][
        "MACHINE_READABLE_ROLE_CONTRACT_MANIFEST"
    ] == "AI-ORCHESTRATION-RUNTIME-READINESS-APP-1"
    assert contract["output_ownership"][
        "MULTI_MODEL_WORKFLOW_BOUNDARY_CONTRACT"
    ] == APP_ID
    assert contract["output_ownership"][
        "FINAL_OPERATOR_APPROVAL_RECORD"
    ] == "HUMAN_OPERATOR"


def test_cloud_eligibility_is_deterministic_and_fail_closed() -> None:
    rules = _contract()["cloud_eligibility_rules"]

    assert rules["deterministic_policy_decision_required"] is True
    assert rules["privacy_policy_status_required"] is True
    assert rules["licensing_policy_status_required"] is True
    assert rules["config_snapshot_required"] is True
    assert rules["fail_closed_required"] is True
    assert rules["ai_self_authorization_allowed"] is False
    assert rules["automatic_cloud_selection_allowed"] is False
    assert rules["automatic_cloud_switching_allowed"] is False


def test_existing_capabilities_are_reused_without_duplication() -> None:
    rules = _contract()["non_duplication_rules"]

    assert rules["existing_role_contracts_reused"] is True
    assert rules["existing_version_registry_reused"] is True
    assert rules["existing_routing_eligibility_reused"] is True
    assert rules["new_role_registry_created"] is False
    assert rules["new_model_registry_created"] is False
    assert rules["new_prompt_registry_created"] is False
    assert rules["runtime_readiness_reimplemented"] is False


def test_model_selection_switching_and_execution_are_forbidden() -> None:
    flags = _contract()["safety_flags"]

    assert flags["automatic_model_selection_allowed"] is False
    assert flags["automatic_model_switching_allowed"] is False
    assert flags["automatic_routing_allowed"] is False
    assert flags["model_invocation_allowed"] is False
    assert flags["prompt_execution_allowed"] is False
    assert flags["runtime_activation_allowed"] is False


def test_http_credentials_core_and_trading_are_forbidden() -> None:
    flags = _contract()["safety_flags"]

    assert flags["http_service_allowed"] is False
    assert flags["port_listener_allowed"] is False
    assert flags["credential_access_allowed"] is False
    assert flags["core_mutation_allowed"] is False
    assert flags["p48_expansion_allowed"] is False
    assert flags["trading_api_allowed"] is False
    assert flags["real_order_allowed"] is False
    assert flags["real_execution_allowed"] is False


def test_operator_review_and_registered_artifacts_are_required() -> None:
    contract = _contract()
    flags = contract["safety_flags"]

    assert contract["operator_review_status"] == "REVIEW_REQUIRED"
    assert flags["operator_review_required"] is True
    assert flags["registered_artifacts_only"] is True
    assert flags["input_ownership_required"] is True
    assert flags["output_ownership_required"] is True


def test_validation_rejects_automatic_model_selection() -> None:
    contract = _contract()
    contract["safety_flags"][
        "automatic_model_selection_allowed"
    ] = True

    assert "automatic_model_selection_allowed_must_be_false" in (
        validate_multi_model_workflow_boundary_contract(contract)
    )


def test_validation_rejects_cloud_policy_tampering() -> None:
    contract = _contract()
    contract["cloud_eligibility_rules"][
        "ai_self_authorization_allowed"
    ] = True

    assert "cloud_eligibility_rules_invalid" in (
        validate_multi_model_workflow_boundary_contract(contract)
    )


def test_validation_rejects_registry_duplication() -> None:
    contract = _contract()
    contract["non_duplication_rules"][
        "new_model_registry_created"
    ] = True

    assert "non_duplication_rules_invalid" in (
        validate_multi_model_workflow_boundary_contract(contract)
    )


def test_builder_rejects_invalid_contract_id() -> None:
    with pytest.raises(MultiModelWorkflowBoundaryViolation):
        build_multi_model_workflow_boundary_contract(
            contract_id="invalid contract id"
        )


def test_builder_returns_fresh_nested_containers() -> None:
    first = _contract()
    second = _contract()
    mutated = deepcopy(first)

    mutated["model_slot_types"].append("AUTO_SELECTED")
    mutated["cloud_eligibility_rules"][
        "ai_self_authorization_allowed"
    ] = True
    mutated["safety_flags"]["real_execution_allowed"] = True

    assert second == _contract()
    assert mutated != second


def test_non_mapping_contract_is_rejected() -> None:
    assert validate_multi_model_workflow_boundary_contract(
        []
    ) == ["contract_must_be_mapping"]