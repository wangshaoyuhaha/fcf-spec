import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
from fcf.sidecars.ai_evaluation_comparison import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    COMPARISON_MODES,
    COMPARISON_STATUSES,
    CONTRACT_VERSION,
    FORBIDDEN_COMPARISON_STATUSES,
    REQUIRED_COMPARISON_DIMENSIONS,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)


def test_build_boundary_contract_is_valid() -> None:
    contract = build_boundary_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert contract["contract_version"] == CONTRACT_VERSION
    assert contract["allowed_inputs"] == list(ALLOWED_INPUTS)
    assert contract["allowed_outputs"] == list(ALLOWED_OUTPUTS)
    assert contract["comparison_modes"] == list(COMPARISON_MODES)
    assert contract["comparison_statuses"] == list(
        COMPARISON_STATUSES
    )
    assert contract["required_comparison_dimensions"] == list(
        REQUIRED_COMPARISON_DIMENSIONS
    )
    assert contract["forbidden_comparison_statuses"] == list(
        FORBIDDEN_COMPARISON_STATUSES
    )
    assert validate_boundary_contract(contract) == []


def test_contract_supports_registered_multi_model_comparison() -> None:
    contract = build_boundary_contract()

    assert "expected_vs_observed" in contract["comparison_modes"]
    assert "cross_model" in contract["comparison_modes"]
    assert "cross_model_version" in contract["comparison_modes"]
    assert "cross_prompt_version" in contract["comparison_modes"]

    dimensions = contract["required_comparison_dimensions"]

    assert "model_id" in dimensions
    assert "model_version" in dimensions
    assert "prompt_id" in dimensions
    assert "prompt_version" in dimensions
    assert "expected_result_reference" in dimensions
    assert "observed_result_reference" in dimensions


def test_contract_enforces_permanent_safety_boundary() -> None:
    contract = build_boundary_contract()

    required_true = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
        "deterministic_comparison_only",
        "registered_artifacts_only",
    )

    required_false = (
        "operator_review_bypass_allowed",
        "automatic_evaluation_acceptance_allowed",
        "source_artifact_mutation_allowed",
        "model_invocation_allowed",
        "prompt_execution_allowed",
        "orchestrator_execution_allowed",
        "news_feed_connection_allowed",
        "trade_instruction_generation_allowed",
        "trade_action_allowed",
        "real_trading_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
    )

    for field in required_true:
        assert contract[field] is True

    for field in required_false:
        assert contract[field] is False


def test_contract_rejects_safety_flag_mutation() -> None:
    contract = build_boundary_contract()
    contract["operator_review_required"] = False
    contract["model_invocation_allowed"] = True
    contract["core_mutation_allowed"] = True

    errors = validate_boundary_contract(contract)

    assert "operator_review_required_must_be_true" in errors
    assert "model_invocation_allowed_must_be_false" in errors
    assert "core_mutation_allowed_must_be_false" in errors


def test_contract_rejects_forbidden_status_activation() -> None:
    contract = build_boundary_contract()
    contract["comparison_statuses"].append("AUTO_APPROVED")

    errors = validate_boundary_contract(contract)

    assert "comparison_statuses_mismatch" in errors
    assert "forbidden_status_enabled:AUTO_APPROVED" in errors


def test_contract_requires_all_forbidden_capabilities() -> None:
    contract = build_boundary_contract()
    contract["forbidden_capabilities"].remove(
        "live_model_invocation"
    )

    errors = validate_boundary_contract(contract)

    assert (
        "missing_forbidden_capability:live_model_invocation"
        in errors
    )


def test_contract_requires_exact_comparison_dimensions() -> None:
    contract = build_boundary_contract()
    contract["required_comparison_dimensions"].remove(
        "operator_review_status"
    )

    errors = validate_boundary_contract(contract)

    assert "required_comparison_dimensions_mismatch" in errors


def test_boundary_contract_returns_fresh_lists() -> None:
    first = build_boundary_contract()
    second = build_boundary_contract()

    first["allowed_inputs"].append("unexpected_input")
    first["comparison_modes"].append("unexpected_mode")

    assert first["allowed_inputs"] != second["allowed_inputs"]
    assert first["comparison_modes"] != second["comparison_modes"]


def test_validate_boundary_contract_rejects_non_mapping() -> None:
    assert validate_boundary_contract([]) == [
        "contract_not_mapping"
    ]


def test_validate_boundary_contract_is_deterministic() -> None:
    contract = build_boundary_contract()
    mutated = deepcopy(contract)
    mutated["app_id"] = "WRONG"
    mutated["paper_only"] = False

    first = validate_boundary_contract(mutated)
    second = validate_boundary_contract(mutated)

    assert first == second
    assert first == sorted(first)