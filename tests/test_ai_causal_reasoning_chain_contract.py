"""Tests for causal reasoning D1 boundary contract."""

from copy import deepcopy

from fcf.sidecars.ai_causal_reasoning_chain import (
    APP_ID,
    REASONING_MODE,
    STAGE_ID,
    build_causal_reasoning_boundary_contract,
    validate_causal_reasoning_boundary_contract,
)


def test_contract_identity() -> None:
    contract = build_causal_reasoning_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["reasoning_mode"] == REASONING_MODE


def test_valid_contract_passes_validation() -> None:
    contract = build_causal_reasoning_boundary_contract()

    assert (
        validate_causal_reasoning_boundary_contract(
            contract
        )
        == []
    )


def test_causal_truth_remains_undetermined() -> None:
    contract = build_causal_reasoning_boundary_contract()

    assert contract["interpretation_state"][
        "causal_truth_status"
    ] == "UNDETERMINED"


def test_correlation_is_not_causation() -> None:
    contract = build_causal_reasoning_boundary_contract()

    assert contract["safety_flags"][
        "correlation_is_not_causation"
    ] is True

    assert contract["anti_overlap_policy"][
        "correlation_is_not_promoted_to_causation"
    ] is True


def test_missing_claims_and_evidence_are_not_created() -> None:
    contract = build_causal_reasoning_boundary_contract()

    assert contract["anti_overlap_policy"][
        "missing_claims_are_not_created"
    ] is True

    assert contract["anti_overlap_policy"][
        "missing_evidence_is_not_created"
    ] is True


def test_source_artifacts_and_conclusions_are_preserved() -> None:
    contract = build_causal_reasoning_boundary_contract()

    assert contract["interpretation_state"][
        "source_artifact_status"
    ] == "PRESERVED"

    assert contract["interpretation_state"][
        "original_conclusion_status"
    ] == "PRESERVED"


def test_live_model_and_prompt_execution_are_forbidden() -> None:
    contract = build_causal_reasoning_boundary_contract()
    flags = contract["safety_flags"]

    assert flags[
        "live_model_invocation_allowed"
    ] is False

    assert flags[
        "prompt_execution_allowed"
    ] is False


def test_runtime_orchestration_is_forbidden() -> None:
    contract = build_causal_reasoning_boundary_contract()

    assert contract["anti_overlap_policy"][
        "runtime_orchestrator_created"
    ] is False

    assert contract["safety_flags"][
        "runtime_orchestrator_execution_allowed"
    ] is False


def test_automatic_causal_inference_is_forbidden() -> None:
    contract = build_causal_reasoning_boundary_contract()
    flags = contract["safety_flags"]

    assert flags[
        "automatic_causal_truth_decision_allowed"
    ] is False

    assert flags[
        "automatic_causality_inference_allowed"
    ] is False

    assert flags[
        "automatic_probability_assignment_allowed"
    ] is False


def test_validation_rejects_causal_truth_decision() -> None:
    contract = build_causal_reasoning_boundary_contract()

    contract["safety_flags"][
        "automatic_causal_truth_decision_allowed"
    ] = True

    errors = validate_causal_reasoning_boundary_contract(
        contract
    )

    assert (
        "automatic_causal_truth_decision_allowed_must_be_false"
        in errors
    )


def test_validation_rejects_source_mutation() -> None:
    contract = build_causal_reasoning_boundary_contract()

    contract["anti_overlap_policy"][
        "source_artifacts_are_not_mutated"
    ] = False

    assert "anti_overlap_policy_invalid" in (
        validate_causal_reasoning_boundary_contract(
            contract
        )
    )


def test_builder_returns_fresh_containers() -> None:
    first = build_causal_reasoning_boundary_contract()
    second = build_causal_reasoning_boundary_contract()
    mutated = deepcopy(first)

    mutated["allowed_input_artifact_types"].append(
        "UNREGISTERED_INPUT"
    )

    mutated["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert second == (
        build_causal_reasoning_boundary_contract()
    )

    assert mutated != second


def test_non_mapping_contract_is_rejected() -> None:
    assert (
        validate_causal_reasoning_boundary_contract(
            []
        )
        == ["contract_must_be_mapping"]
    )
