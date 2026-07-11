"""Boundary contract for deterministic AI scenario simulation governance."""

from typing import Any, Mapping


APP_ID = "AI-SCENARIO-SIMULATION-APP-1"
STAGE_ID = "AI-SCENARIO-SIMULATION-D1"
CONTRACT_VERSION = "1.0.0"

ALLOWED_INPUTS = (
    "registered_market_scenario_definition",
    "registered_market_scenario_assumption",
    "registered_market_scenario_risk_context",
    "registered_market_narrative_assessment",
    "registered_ai_context_artifact",
    "registered_contrarian_challenge_artifact",
    "registered_risk_flags",
    "registered_evidence_references",
)

ALLOWED_OUTPUTS = (
    "scenario_simulation_boundary_contract",
    "scenario_simulation_input_record",
    "scenario_assumption_bundle",
    "scenario_branch_record",
    "cross_scenario_consequence_matrix",
    "scenario_simulation_assessment",
    "scenario_simulation_review_packet",
    "scenario_simulation_operator_handoff",
)

REQUIRED_TRUE_FLAGS = (
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "deterministic_only",
    "registered_artifacts_only",
    "operator_review_required",
    "original_conclusions_preserved",
    "source_artifacts_preserved",
)

REQUIRED_FALSE_FLAGS = (
    "p48_core_expansion_allowed",
    "core_mutation_allowed",
    "source_mutation_allowed",
    "source_deletion_allowed",
    "source_overwrite_allowed",
    "live_model_invocation_allowed",
    "prompt_execution_allowed",
    "ai_orchestrator_execution_allowed",
    "automatic_truth_decision_allowed",
    "automatic_winner_selection_allowed",
    "automatic_conclusion_replacement_allowed",
    "automatic_scenario_probability_generation_allowed",
    "automatic_scenario_ranking_allowed",
    "automatic_model_switching_allowed",
    "automatic_prompt_switching_allowed",
    "operator_review_bypass_allowed",
    "trade_action_allowed",
    "real_execution_allowed",
    "broker_connection_allowed",
    "exchange_connection_allowed",
    "credential_storage_allowed",
    "wallet_private_key_access_allowed",
    "real_account_access_allowed",
    "real_position_access_allowed",
    "automatic_position_sizing_allowed",
    "automatic_portfolio_action_allowed",
    "price_target_prediction_allowed",
    "black_box_monte_carlo_prediction_allowed",
)

FORBIDDEN_CAPABILITIES = (
    "live_model_invocation",
    "prompt_execution",
    "ai_orchestrator_execution",
    "automatic_truth_decision",
    "automatic_winner_selection",
    "automatic_conclusion_replacement",
    "automatic_scenario_probability_generation",
    "automatic_scenario_ranking",
    "automatic_model_switching",
    "automatic_prompt_switching",
    "operator_review_bypass",
    "trade_action",
    "real_execution",
    "broker_connection",
    "exchange_connection",
    "credential_storage",
    "wallet_private_key_access",
    "real_account_access",
    "real_position_access",
    "automatic_position_sizing",
    "automatic_portfolio_action",
    "price_target_prediction",
    "black_box_monte_carlo_prediction",
)

OVERLAP_POLICY = {
    "market_scenario_app_role": (
        "authoritative_registered_scenario_source"
    ),
    "ai_scenario_simulation_role": (
        "read_only_governance_simulation"
    ),
    "creates_scenario_registry": False,
    "mutates_registered_scenarios": False,
    "replaces_market_scenario_app": False,
    "simulation_result_is_truth": False,
    "simulation_result_is_forecast": False,
    "simulation_result_is_trade_instruction": False,
}


def build_boundary_contract() -> dict[str, Any]:
    """Build a fresh immutable-intent D1 boundary contract."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "purpose": (
            "Build deterministic read-only scenario branches from "
            "registered artifacts without creating or mutating the "
            "authoritative market scenario registry."
        ),
        "allowed_inputs": list(ALLOWED_INPUTS),
        "allowed_outputs": list(ALLOWED_OUTPUTS),
        "truth_status": "UNDETERMINED",
        "interpretation_boundary": (
            "Simulation outputs are additional governance evidence only."
        ),
        "safety_flags": {
            **{name: True for name in REQUIRED_TRUE_FLAGS},
            **{name: False for name in REQUIRED_FALSE_FLAGS},
        },
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "overlap_policy": dict(OVERLAP_POLICY),
    }


def _validate_exact_string_list(
    value: Any,
    expected: tuple[str, ...],
    field_name: str,
) -> list[str]:
    """Validate an exact deterministic string list."""
    if not isinstance(value, list):
        return [f"{field_name}_must_be_list"]

    if any(not isinstance(item, str) or not item for item in value):
        return [f"{field_name}_must_contain_non_empty_strings"]

    if value != list(expected):
        return [f"{field_name}_must_match_contract"]

    return []


def validate_boundary_contract(contract: object) -> list[str]:
    """Return deterministic D1 boundary validation errors."""
    if not isinstance(contract, Mapping):
        return ["contract_must_be_mapping"]

    errors: list[str] = []

    if contract.get("app_id") != APP_ID:
        errors.append("app_id_invalid")

    if contract.get("stage_id") != STAGE_ID:
        errors.append("stage_id_invalid")

    if contract.get("contract_version") != CONTRACT_VERSION:
        errors.append("contract_version_invalid")

    errors.extend(
        _validate_exact_string_list(
            contract.get("allowed_inputs"),
            ALLOWED_INPUTS,
            "allowed_inputs",
        )
    )
    errors.extend(
        _validate_exact_string_list(
            contract.get("allowed_outputs"),
            ALLOWED_OUTPUTS,
            "allowed_outputs",
        )
    )
    errors.extend(
        _validate_exact_string_list(
            contract.get("forbidden_capabilities"),
            FORBIDDEN_CAPABILITIES,
            "forbidden_capabilities",
        )
    )

    if contract.get("truth_status") != "UNDETERMINED":
        errors.append("truth_status_must_remain_undetermined")

    safety_flags = contract.get("safety_flags")
    if not isinstance(safety_flags, Mapping):
        errors.append("safety_flags_must_be_mapping")
    else:
        for name in REQUIRED_TRUE_FLAGS:
            if safety_flags.get(name) is not True:
                errors.append(f"{name}_must_be_true")

        for name in REQUIRED_FALSE_FLAGS:
            if safety_flags.get(name) is not False:
                errors.append(f"{name}_must_be_false")

        expected_flag_names = set(
            REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
        )
        if set(safety_flags.keys()) != expected_flag_names:
            errors.append("safety_flag_names_must_match_contract")

    overlap_policy = contract.get("overlap_policy")
    if not isinstance(overlap_policy, Mapping):
        errors.append("overlap_policy_must_be_mapping")
    else:
        if dict(overlap_policy) != OVERLAP_POLICY:
            errors.append("overlap_policy_must_match_contract")

    return errors
