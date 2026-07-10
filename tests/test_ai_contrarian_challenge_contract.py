import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_contrarian_challenge import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    CHALLENGE_CATEGORIES,
    CHALLENGE_STATUSES,
    CONTRACT_VERSION,
    FORBIDDEN_OUTCOMES,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)


def test_boundary_contract_is_valid() -> None:
    contract = build_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["contract_version"] == CONTRACT_VERSION
    assert validate_boundary_contract(contract) == []


def test_boundary_contract_is_deterministic() -> None:
    first = build_boundary_contract()
    second = build_boundary_contract()

    assert first == second
    assert first is not second


def test_boundary_contract_exports_registered_inputs() -> None:
    contract = build_boundary_contract()

    assert contract["allowed_inputs"] == list(ALLOWED_INPUTS)
    assert "registered_ai_context_artifact" in ALLOWED_INPUTS
    assert "registered_drift_review_artifact" in ALLOWED_INPUTS


def test_boundary_contract_exports_review_outputs() -> None:
    contract = build_boundary_contract()

    assert contract["allowed_outputs"] == list(ALLOWED_OUTPUTS)
    assert "contradiction_summary" in ALLOWED_OUTPUTS
    assert "challenge_operator_handoff" in ALLOWED_OUTPUTS


def test_boundary_contract_defines_challenge_categories() -> None:
    contract = build_boundary_contract()

    assert contract["challenge_categories"] == list(
        CHALLENGE_CATEGORIES
    )
    assert "UNSUPPORTED_CLAIM" in CHALLENGE_CATEGORIES
    assert "CROSS_ARTIFACT_CONTRADICTION" in (
        CHALLENGE_CATEGORIES
    )


def test_boundary_contract_defines_review_statuses() -> None:
    contract = build_boundary_contract()

    assert contract["challenge_statuses"] == list(
        CHALLENGE_STATUSES
    )
    assert "REVIEW_REQUIRED" in CHALLENGE_STATUSES


def test_boundary_contract_rejects_missing_input() -> None:
    contract = build_boundary_contract()
    contract["allowed_inputs"].remove(
        "registered_evidence_references"
    )

    assert (
        "allowed_inputs_missing:registered_evidence_references"
        in validate_boundary_contract(contract)
    )


def test_boundary_contract_rejects_unexpected_output() -> None:
    contract = build_boundary_contract()
    contract["allowed_outputs"].append(
        "automatic_truth_decision"
    )

    assert (
        "allowed_outputs_unexpected:automatic_truth_decision"
        in validate_boundary_contract(contract)
    )


def test_boundary_contract_rejects_category_mutation() -> None:
    contract = build_boundary_contract()
    contract["challenge_categories"].append(
        "AUTOMATIC_WINNER"
    )

    assert (
        "challenge_categories_unexpected:AUTOMATIC_WINNER"
        in validate_boundary_contract(contract)
    )


def test_boundary_contract_rejects_forbidden_overlap() -> None:
    contract = build_boundary_contract()
    contract["challenge_statuses"].append("AUTO_WINNER")

    errors = validate_boundary_contract(contract)

    assert "challenge_statuses_unexpected:AUTO_WINNER" in errors
    assert "status_outcome_boundary_overlap" in errors


def test_boundary_contract_preserves_original_conclusion() -> None:
    contract = build_boundary_contract()

    assert contract["original_conclusion_preserved"] is True
    assert (
        contract["automatic_conclusion_replacement_allowed"]
        is False
    )


def test_boundary_contract_rejects_safety_mutation() -> None:
    contract = build_boundary_contract()
    contract["operator_review_required"] = False
    contract["model_invocation_allowed"] = True
    contract["automatic_truth_decision_allowed"] = True
    contract["trade_action_allowed"] = True

    errors = validate_boundary_contract(contract)

    assert "operator_review_required_must_be_true" in errors
    assert "model_invocation_allowed_must_be_false" in errors
    assert (
        "automatic_truth_decision_allowed_must_be_false"
        in errors
    )
    assert "trade_action_allowed_must_be_false" in errors


def test_boundary_contract_has_no_execution_capability() -> None:
    contract = build_boundary_contract()

    assert contract["model_invocation_allowed"] is False
    assert contract["prompt_execution_allowed"] is False
    assert contract["orchestrator_execution_allowed"] is False
    assert contract["real_execution_allowed"] is False


def test_boundary_contract_does_not_mutate_input() -> None:
    contract = build_boundary_contract()
    before = deepcopy(contract)

    validate_boundary_contract(contract)

    assert contract == before


def test_boundary_contract_rejects_non_mapping() -> None:
    assert validate_boundary_contract([]) == [
        "contract_not_mapping"
    ]