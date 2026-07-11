"""Boundary and anti-hallucination contract for causal reasoning."""

from typing import Any, Mapping


APP_ID = "AI-CAUSAL-REASONING-CHAIN-APP-1"
STAGE_ID = "AI-CAUSAL-REASONING-CHAIN-D1"
CONTRACT_VERSION = "1.0.0"
REASONING_MODE = "DETERMINISTIC_REGISTERED_EVIDENCE_ONLY"

ALLOWED_INPUT_ARTIFACT_TYPES = (
    "REGISTERED_AI_CONTEXT_ARTIFACT",
    "REGISTERED_AI_EVALUATION_ARTIFACT",
    "REGISTERED_AI_CHALLENGE_ARTIFACT",
    "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
    "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
    "REGISTERED_CAUSAL_CLAIM_ARTIFACT",
    "REGISTERED_PREMISE_ARTIFACT",
    "REGISTERED_SUPPORTING_EVIDENCE_ARTIFACT",
    "REGISTERED_COUNTEREVIDENCE_ARTIFACT",
    "REGISTERED_ALTERNATIVE_EXPLANATION_ARTIFACT",
    "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
    "REGISTERED_VALIDATION_BASELINE_ARTIFACT",
    "REGISTERED_OPERATOR_REVIEW_ARTIFACT",
)

ALLOWED_OUTPUT_ARTIFACT_TYPES = (
    "CAUSAL_REASONING_BOUNDARY_CONTRACT",
    "REGISTERED_CAUSAL_CLAIM_RECORD",
    "DETERMINISTIC_CAUSAL_CHAIN_RECORD",
    "CAUSAL_CHAIN_GAP_REPORT",
    "CAUSAL_CONTRADICTION_REPORT",
    "ALTERNATIVE_EXPLANATION_REPORT",
    "CAUSAL_REASONING_REVIEW_PACKET",
    "OPERATOR_REVIEW_HANDOFF",
)

FORBIDDEN_CAPABILITIES = (
    "AUTOMATIC_CAUSAL_TRUTH_DECISION",
    "AUTOMATIC_CAUSALITY_INFERENCE_FROM_CORRELATION",
    "AUTOMATIC_CLAIM_CREATION",
    "AUTOMATIC_EVIDENCE_CREATION",
    "AUTOMATIC_MODEL_SELECTION",
    "AUTOMATIC_MODEL_SWITCHING",
    "AUTOMATIC_PROBABILITY_ASSIGNMENT",
    "AUTOMATIC_PROMPT_SELECTION",
    "AUTOMATIC_PROMPT_SWITCHING",
    "AUTOMATIC_ROLE_SWITCHING",
    "AUTOMATIC_ROUTE_SELECTION",
    "AUTOMATIC_WINNER_SELECTION",
    "CONCLUSION_REPLACEMENT",
    "CORE_MUTATION",
    "LIVE_MODEL_INVOCATION",
    "OPERATOR_REVIEW_BYPASS",
    "PROMPT_EXECUTION",
    "REAL_EXECUTION",
    "RUNTIME_ORCHESTRATOR_EXECUTION",
    "SOURCE_ARTIFACT_MUTATION",
    "TRADE_ACTION",
)

REQUIRED_TRUE_FLAGS = (
    "correlation_is_not_causation",
    "deterministic_only",
    "explicit_counterevidence_required",
    "explicit_evidence_references_required",
    "explicit_premises_required",
    "local_only",
    "operator_review_required",
    "original_conclusions_preserved",
    "paper_only",
    "read_only",
    "registered_artifacts_only",
    "sidecar_only",
    "source_artifacts_preserved",
    "truth_status_remains_undetermined",
)

REQUIRED_FALSE_FLAGS = (
    "automatic_causal_truth_decision_allowed",
    "automatic_causality_inference_allowed",
    "automatic_claim_creation_allowed",
    "automatic_evidence_creation_allowed",
    "automatic_model_selection_allowed",
    "automatic_model_switching_allowed",
    "automatic_probability_assignment_allowed",
    "automatic_prompt_selection_allowed",
    "automatic_prompt_switching_allowed",
    "automatic_role_switching_allowed",
    "automatic_route_selection_allowed",
    "automatic_winner_selection_allowed",
    "conclusion_replacement_allowed",
    "core_mutation_allowed",
    "live_model_invocation_allowed",
    "operator_review_bypass_allowed",
    "prompt_execution_allowed",
    "real_execution_allowed",
    "runtime_orchestrator_execution_allowed",
    "source_artifact_mutation_allowed",
    "trade_action_allowed",
)

ANTI_OVERLAP_POLICY = {
    "ai_context_sidecar_remains_authoritative": True,
    "ai_challenge_sidecar_remains_authoritative": True,
    "market_narrative_sidecar_remains_authoritative": True,
    "scenario_simulation_sidecar_remains_authoritative": True,
    "correlation_rollup_remains_authoritative": True,
    "causal_reasoning_is_additional_governance_evidence": True,
    "missing_claims_are_not_created": True,
    "missing_evidence_is_not_created": True,
    "correlation_is_not_promoted_to_causation": True,
    "source_artifacts_are_not_mutated": True,
    "original_conclusions_are_not_replaced": True,
    "runtime_orchestrator_created": False,
    "core_mutation_allowed": False,
}

REQUIRED_CONTRACT_FIELDS = (
    "app_id",
    "stage_id",
    "contract_version",
    "reasoning_mode",
    "allowed_input_artifact_types",
    "allowed_output_artifact_types",
    "forbidden_capabilities",
    "anti_overlap_policy",
    "interpretation_state",
    "safety_flags",
)


def _safety_flags() -> dict[str, bool]:
    return {
        **{
            name: True
            for name in REQUIRED_TRUE_FLAGS
        },
        **{
            name: False
            for name in REQUIRED_FALSE_FLAGS
        },
    }


def build_causal_reasoning_boundary_contract() -> dict[str, Any]:
    """Build the deterministic D1 causal reasoning contract."""
    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "reasoning_mode": REASONING_MODE,
        "allowed_input_artifact_types": list(
            ALLOWED_INPUT_ARTIFACT_TYPES
        ),
        "allowed_output_artifact_types": list(
            ALLOWED_OUTPUT_ARTIFACT_TYPES
        ),
        "forbidden_capabilities": list(
            FORBIDDEN_CAPABILITIES
        ),
        "anti_overlap_policy": dict(
            ANTI_OVERLAP_POLICY
        ),
        "interpretation_state": {
            "causal_truth_status": "UNDETERMINED",
            "probability_status": "NOT_ASSIGNED",
            "winner_status": "NOT_SELECTED",
            "operator_review_status": "REQUIRED",
            "source_artifact_status": "PRESERVED",
            "original_conclusion_status": "PRESERVED",
        },
        "safety_flags": _safety_flags(),
    }


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(
                f"{name}_must_be_true"
            )

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(
                f"{name}_must_be_false"
            )

    return errors


def validate_causal_reasoning_boundary_contract(
    contract: object,
) -> list[str]:
    """Return deterministic D1 boundary validation errors."""
    if not isinstance(contract, Mapping):
        return ["contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(
        REQUIRED_CONTRACT_FIELDS
    ):
        errors.append(
            "contract_fields_must_match_schema"
        )

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "reasoning_mode": REASONING_MODE,
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    expected_lists = {
        "allowed_input_artifact_types": list(
            ALLOWED_INPUT_ARTIFACT_TYPES
        ),
        "allowed_output_artifact_types": list(
            ALLOWED_OUTPUT_ARTIFACT_TYPES
        ),
        "forbidden_capabilities": list(
            FORBIDDEN_CAPABILITIES
        ),
    }

    for field, expected in expected_lists.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    anti_overlap_policy = contract.get(
        "anti_overlap_policy"
    )

    if not isinstance(anti_overlap_policy, Mapping):
        errors.append(
            "anti_overlap_policy_must_be_mapping"
        )
    elif dict(anti_overlap_policy) != (
        ANTI_OVERLAP_POLICY
    ):
        errors.append(
            "anti_overlap_policy_invalid"
        )

    interpretation_state = contract.get(
        "interpretation_state"
    )

    expected_interpretation_state = {
        "causal_truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "winner_status": "NOT_SELECTED",
        "operator_review_status": "REQUIRED",
        "source_artifact_status": "PRESERVED",
        "original_conclusion_status": "PRESERVED",
    }

    if not isinstance(interpretation_state, Mapping):
        errors.append(
            "interpretation_state_must_be_mapping"
        )
    elif dict(interpretation_state) != (
        expected_interpretation_state
    ):
        errors.append(
            "interpretation_state_invalid"
        )

    errors.extend(
        _validate_safety_flags(
            contract.get("safety_flags")
        )
    )

    return errors
