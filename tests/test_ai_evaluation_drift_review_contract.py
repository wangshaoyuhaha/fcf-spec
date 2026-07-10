import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_drift_review import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    CONTRACT_VERSION,
    DRIFT_STATUSES,
    FORBIDDEN_DRIFT_STATUSES,
    REQUIRED_DRIFT_DIMENSIONS,
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
    assert "registered_comparison_record" in ALLOWED_INPUTS
    assert "comparison_operator_handoff" in ALLOWED_INPUTS


def test_boundary_contract_exports_review_only_outputs() -> None:
    contract = build_boundary_contract()

    assert contract["allowed_outputs"] == list(ALLOWED_OUTPUTS)
    assert "drift_review_packet" in ALLOWED_OUTPUTS
    assert "drift_operator_handoff" in ALLOWED_OUTPUTS


def test_boundary_contract_requires_drift_dimensions() -> None:
    contract = build_boundary_contract()

    assert contract["required_drift_dimensions"] == list(
        REQUIRED_DRIFT_DIMENSIONS
    )
    assert "baseline_reference" in REQUIRED_DRIFT_DIMENSIONS
    assert "candidate_reference" in REQUIRED_DRIFT_DIMENSIONS


def test_boundary_contract_rejects_app_id_mutation() -> None:
    contract = build_boundary_contract()
    contract["app_id"] = "OTHER-APP"

    assert "app_id_mismatch" in validate_boundary_contract(
        contract
    )


def test_boundary_contract_rejects_missing_input() -> None:
    contract = build_boundary_contract()
    contract["allowed_inputs"].remove(
        "registered_comparison_record"
    )

    errors = validate_boundary_contract(contract)

    assert (
        "allowed_inputs_missing:registered_comparison_record"
        in errors
    )


def test_boundary_contract_rejects_unexpected_output() -> None:
    contract = build_boundary_contract()
    contract["allowed_outputs"].append(
        "automatic_model_switch"
    )

    errors = validate_boundary_contract(contract)

    assert (
        "allowed_outputs_unexpected:automatic_model_switch"
        in errors
    )


def test_boundary_contract_rejects_missing_dimension() -> None:
    contract = build_boundary_contract()
    contract["required_drift_dimensions"].remove(
        "baseline_created_at_utc"
    )

    errors = validate_boundary_contract(contract)

    assert (
        "required_drift_dimensions_missing:"
        "baseline_created_at_utc"
        in errors
    )


def test_boundary_contract_rejects_status_mutation() -> None:
    contract = build_boundary_contract()
    contract["drift_statuses"].append("AUTO_APPROVED")

    errors = validate_boundary_contract(contract)

    assert "drift_statuses_unexpected:AUTO_APPROVED" in errors
    assert "drift_status_boundary_overlap" in errors


def test_boundary_contract_keeps_forbidden_statuses_separate() -> None:
    assert not (
        set(DRIFT_STATUSES)
        & set(FORBIDDEN_DRIFT_STATUSES)
    )


def test_boundary_contract_rejects_safety_mutation() -> None:
    contract = build_boundary_contract()
    contract["operator_review_required"] = False
    contract["model_invocation_allowed"] = True
    contract["automatic_rollback_allowed"] = True
    contract["trade_action_allowed"] = True

    errors = validate_boundary_contract(contract)

    assert "operator_review_required_must_be_true" in errors
    assert "model_invocation_allowed_must_be_false" in errors
    assert "automatic_rollback_allowed_must_be_false" in errors
    assert "trade_action_allowed_must_be_false" in errors


def test_boundary_contract_has_no_execution_capability() -> None:
    contract = build_boundary_contract()

    assert contract["model_invocation_allowed"] is False
    assert contract["prompt_execution_allowed"] is False
    assert contract["orchestrator_execution_allowed"] is False
    assert contract["automatic_model_switch_allowed"] is False
    assert contract["automatic_prompt_switch_allowed"] is False
    assert contract["real_execution_allowed"] is False


def test_boundary_contract_does_not_mutate_copy() -> None:
    contract = build_boundary_contract()
    before = deepcopy(contract)

    validate_boundary_contract(contract)

    assert contract == before


def test_boundary_contract_rejects_non_mapping() -> None:
    assert validate_boundary_contract([]) == [
        "contract_not_mapping"
    ]