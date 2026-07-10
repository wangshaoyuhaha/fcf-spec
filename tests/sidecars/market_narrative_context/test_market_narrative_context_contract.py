"""D1 tests for the market narrative context contract."""

from dataclasses import replace

import pytest

from fcf.sidecars.market_narrative_context.contract import (
    ALLOWED_INPUT_ARTIFACT_TYPES,
    ALLOWED_OUTPUT_ARTIFACT_TYPES,
    APP_ID,
    CONTRACT_VERSION,
    NarrativeBoundaryViolation,
    assert_valid_contract,
    build_default_contract,
    validate_contract,
)


def test_default_contract_is_valid() -> None:
    contract = build_default_contract()

    assert validate_contract(contract) == ()
    assert_valid_contract(contract)


def test_contract_identity_is_stable() -> None:
    contract = build_default_contract()

    assert contract.app_id == APP_ID
    assert contract.contract_version == CONTRACT_VERSION


def test_permanent_safety_boundaries_are_enabled() -> None:
    contract = build_default_contract()

    assert contract.paper_only is True
    assert contract.local_only is True
    assert contract.read_only is True
    assert contract.sidecar_only is True
    assert contract.deterministic_only is True
    assert contract.registered_artifacts_only is True
    assert contract.operator_review_required is True
    assert contract.original_conclusions_preserved is True


def test_automatic_and_execution_capabilities_are_disabled() -> None:
    contract = build_default_contract()

    assert contract.live_model_invocation_allowed is False
    assert contract.prompt_execution_allowed is False
    assert contract.ai_orchestrator_execution_allowed is False
    assert contract.automatic_truth_decision_allowed is False
    assert contract.automatic_winner_selection_allowed is False
    assert contract.automatic_conclusion_replacement_allowed is False
    assert contract.operator_review_bypass_allowed is False
    assert contract.trade_action_allowed is False
    assert contract.real_execution_allowed is False


def test_registered_input_types_are_fixed() -> None:
    assert ALLOWED_INPUT_ARTIFACT_TYPES == (
        "REGISTERED_MARKET_NARRATIVE",
        "REGISTERED_MACRO_CONTEXT",
        "REGISTERED_INDUSTRY_CONTEXT",
        "REGISTERED_RESEARCH_ARTIFACT",
        "REGISTERED_RISK_FLAG",
        "REGISTERED_EVIDENCE_REFERENCE",
    )


def test_output_types_are_review_artifacts() -> None:
    assert ALLOWED_OUTPUT_ARTIFACT_TYPES == (
        "NARRATIVE_CONTEXT_RECORD",
        "NARRATIVE_LINKAGE_REPORT",
        "NARRATIVE_REVIEW_PACKET",
        "OPERATOR_REVIEW_HANDOFF",
    )


def test_validation_detects_review_bypass() -> None:
    contract = replace(
        build_default_contract(),
        operator_review_bypass_allowed=True,
    )

    assert validate_contract(contract) == (
        "REQUIRED_FALSE:operator_review_bypass_allowed",
    )


def test_validation_detects_truth_decision_permission() -> None:
    contract = replace(
        build_default_contract(),
        automatic_truth_decision_allowed=True,
    )

    assert validate_contract(contract) == (
        "REQUIRED_FALSE:automatic_truth_decision_allowed",
    )


def test_assert_valid_contract_rejects_execution_permission() -> None:
    contract = replace(
        build_default_contract(),
        real_execution_allowed=True,
    )

    with pytest.raises(
        NarrativeBoundaryViolation,
        match="REQUIRED_FALSE:real_execution_allowed",
    ):
        assert_valid_contract(contract)


def test_contract_serialization_is_deterministic() -> None:
    first = build_default_contract().to_dict()
    second = build_default_contract().to_dict()

    assert first == second
    assert first["allowed_input_artifact_types"] == list(
        ALLOWED_INPUT_ARTIFACT_TYPES
    )
    assert first["allowed_output_artifact_types"] == list(
        ALLOWED_OUTPUT_ARTIFACT_TYPES
    )
