import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_result_registry.contract import (
    APP_ID,
    CONTRACT_VERSION,
    FORBIDDEN_RESULT_STATUSES,
    IMPORTED_RESULT_STATUSES,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_FORBIDDEN_CAPABILITIES,
    REQUIRED_TRUE_FLAGS,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)


def test_boundary_contract_identity() -> None:
    contract = build_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["contract_version"] == CONTRACT_VERSION


def test_boundary_contract_validation_passes() -> None:
    contract = build_boundary_contract()

    assert validate_boundary_contract(contract) == []


def test_boundary_contract_requires_imported_artifacts_only() -> None:
    contract = build_boundary_contract()

    assert contract["imported_artifacts_only"] is True
    assert (
        "operator_imported_evaluation_output_reference"
        in contract["allowed_inputs"]
    )


def test_boundary_contract_declares_expected_outputs() -> None:
    contract = build_boundary_contract()

    assert (
        "evaluation_result_record_metadata"
        in contract["allowed_outputs"]
    )
    assert (
        "result_registry_handoff_metadata"
        in contract["allowed_outputs"]
    )


def test_boundary_contract_required_true_flags() -> None:
    contract = build_boundary_contract()

    for field in REQUIRED_TRUE_FLAGS:
        assert contract[field] is True


def test_boundary_contract_required_false_flags() -> None:
    contract = build_boundary_contract()

    for field in REQUIRED_FALSE_FLAGS:
        assert contract[field] is False


def test_boundary_contract_status_model() -> None:
    contract = build_boundary_contract()

    assert contract["imported_result_statuses"] == list(
        IMPORTED_RESULT_STATUSES
    )
    assert contract["forbidden_result_statuses"] == list(
        FORBIDDEN_RESULT_STATUSES
    )

    for forbidden_status in FORBIDDEN_RESULT_STATUSES:
        assert (
            forbidden_status
            not in contract["imported_result_statuses"]
        )


def test_boundary_contract_forbidden_capabilities() -> None:
    contract = build_boundary_contract()

    for capability in REQUIRED_FORBIDDEN_CAPABILITIES:
        assert capability in contract["forbidden_capabilities"]


def test_validation_detects_model_and_prompt_execution() -> None:
    contract = build_boundary_contract()
    contract["model_invocation_allowed"] = True
    contract["prompt_execution_allowed"] = True

    errors = validate_boundary_contract(contract)

    assert "model_invocation_allowed_must_be_false" in errors
    assert "prompt_execution_allowed_must_be_false" in errors


def test_validation_detects_operator_review_bypass() -> None:
    contract = build_boundary_contract()
    contract["operator_review_bypass_allowed"] = True
    contract["automatic_evaluation_acceptance_allowed"] = True

    errors = validate_boundary_contract(contract)

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert (
        "automatic_evaluation_acceptance_allowed_must_be_false"
        in errors
    )


def test_validation_detects_forbidden_status_enabled() -> None:
    contract = build_boundary_contract()
    contract["imported_result_statuses"].append(
        "AUTO_APPROVED"
    )

    errors = validate_boundary_contract(contract)

    assert "imported_result_statuses_mismatch" in errors
    assert "forbidden_status_enabled:AUTO_APPROVED" in errors


def test_validation_detects_missing_forbidden_capability() -> None:
    contract = build_boundary_contract()
    contract["forbidden_capabilities"].remove(
        "real_execution"
    )

    errors = validate_boundary_contract(contract)

    assert (
        "missing_forbidden_capability:real_execution"
        in errors
    )


def test_builder_returns_fresh_lists() -> None:
    first = build_boundary_contract()
    second = build_boundary_contract()
    changed = deepcopy(first)

    changed["allowed_inputs"].append("unexpected-input")
    changed["imported_result_statuses"].clear()

    assert "unexpected-input" not in second["allowed_inputs"]
    assert second["imported_result_statuses"] == list(
        IMPORTED_RESULT_STATUSES
    )


def test_validation_rejects_non_mapping() -> None:
    assert validate_boundary_contract([]) == [
        "contract_not_mapping"
    ]