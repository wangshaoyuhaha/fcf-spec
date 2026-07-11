from __future__ import annotations

from copy import deepcopy

from apps.ai_comprehensive_report_integration_app_1 import (
    APP_ID,
    CONTRACT_VERSION,
    build_integration_boundary_contract,
    validate_integration_boundary_contract,
)


def test_d1_contract_identity() -> None:
    contract = build_integration_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["contract_version"] == CONTRACT_VERSION
    assert contract["stage"] == "D1"
    assert contract["mode"] == "READ_ONLY_INTEGRATION"


def test_d1_contract_source_authority() -> None:
    contract = build_integration_boundary_contract()

    assert (
        contract["source_app_id"]
        == "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
    )
    assert (
        contract["source_artifact_type"]
        == "comprehensive_report_synthesis_packet"
    )


def test_d1_contract_allowed_consumers_are_exact() -> None:
    contract = build_integration_boundary_contract()

    assert contract["allowed_consumers"] == [
        "OPERATOR-REVIEW-APP-1",
        "UI-APP-1",
        "REPORT-ARCHIVE-APP-1",
    ]


def test_d1_contract_requires_all_preservation_fields() -> None:
    contract = build_integration_boundary_contract()
    fields = set(contract["required_preservation_fields"])

    assert {
        "correlation_id",
        "source_artifact_ref",
        "source_artifact_version",
        "source_statements",
        "original_conclusions",
        "risk_flags",
        "counterevidence",
        "alternative_explanations",
        "uncertainty_states",
        "operator_review_required",
    } == fields


def test_d1_contract_blocks_unsafe_operations() -> None:
    contract = build_integration_boundary_contract()
    forbidden = set(contract["forbidden_operations"])

    assert {
        "mutate_source_artifact",
        "replace_original_conclusion",
        "assign_probability",
        "select_winner",
        "auto_approve",
        "bypass_operator_review",
        "execute_archive",
        "invoke_live_model",
        "execute_prompt",
        "route_runtime",
        "place_order",
        "connect_broker_or_exchange",
        "create_tag",
        "create_release",
        "deploy",
    }.issubset(forbidden)


def test_d1_contract_preserves_interpretation_state() -> None:
    contract = build_integration_boundary_contract()

    assert contract["interpretation_state"] == {
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "operator_decision": "PENDING",
        "archive_execution": "NOT_PERFORMED",
    }


def test_d1_contract_preserves_safety_boundary() -> None:
    contract = build_integration_boundary_contract()
    boundary = contract["safety_boundary"]

    assert boundary["core_frozen"] is True
    assert boundary["p48_allowed"] is False
    assert boundary["core_mutation_allowed"] is False
    assert boundary["paper_only"] is True
    assert boundary["local_only"] is True
    assert boundary["read_only"] is True
    assert boundary["sidecar_only"] is True
    assert boundary["operator_review_required"] is True
    assert boundary["automatic_approval_allowed"] is False
    assert boundary["automatic_archive_execution_allowed"] is False
    assert boundary["runtime_orchestration_allowed"] is False
    assert boundary["live_model_invocation_allowed"] is False
    assert boundary["prompt_execution_allowed"] is False
    assert boundary["real_execution_allowed"] is False


def test_d1_valid_contract_passes_validation() -> None:
    contract = build_integration_boundary_contract()
    result = validate_integration_boundary_contract(contract)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["operator_review_required"] is True
    assert result["source_mutation_performed"] is False
    assert result["archive_execution_performed"] is False
    assert result["runtime_execution_performed"] is False
    assert result["real_execution_performed"] is False


def test_d1_validator_rejects_source_mutation_boundary_change() -> None:
    contract = build_integration_boundary_contract()
    unsafe_contract = deepcopy(contract)
    unsafe_contract["safety_boundary"]["read_only"] = False

    result = validate_integration_boundary_contract(unsafe_contract)

    assert result["ok"] is False
    assert "UNSAFE_BOUNDARY_READ_ONLY" in result["errors"]


def test_d1_validator_rejects_automatic_approval() -> None:
    contract = build_integration_boundary_contract()
    unsafe_contract = deepcopy(contract)
    unsafe_contract["safety_boundary"]["automatic_approval_allowed"] = True

    result = validate_integration_boundary_contract(unsafe_contract)

    assert result["ok"] is False
    assert (
        "UNSAFE_BOUNDARY_AUTOMATIC_APPROVAL_ALLOWED"
        in result["errors"]
    )


def test_d1_validator_does_not_mutate_input() -> None:
    contract = build_integration_boundary_contract()
    original = deepcopy(contract)

    validate_integration_boundary_contract(contract)

    assert contract == original
