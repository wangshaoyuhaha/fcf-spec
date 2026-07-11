"""Deterministic boundary contract for market narrative context."""

from __future__ import annotations

from dataclasses import dataclass


APP_ID = "MARKET-NARRATIVE-CONTEXT-APP-1"
CONTRACT_VERSION = "1.0.0"

ALLOWED_INPUT_ARTIFACT_TYPES = (
    "REGISTERED_MARKET_NARRATIVE",
    "REGISTERED_MACRO_CONTEXT",
    "REGISTERED_INDUSTRY_CONTEXT",
    "REGISTERED_RESEARCH_ARTIFACT",
    "REGISTERED_RISK_FLAG",
    "REGISTERED_EVIDENCE_REFERENCE",
)

ALLOWED_OUTPUT_ARTIFACT_TYPES = (
    "NARRATIVE_CONTEXT_RECORD",
    "NARRATIVE_LINKAGE_REPORT",
    "NARRATIVE_REVIEW_PACKET",
    "OPERATOR_REVIEW_HANDOFF",
)


class NarrativeBoundaryViolation(ValueError):
    """Raised when the permanent sidecar boundary is violated."""


@dataclass(frozen=True)
class MarketNarrativeContextContract:
    """Immutable D1 contract for deterministic narrative review."""

    app_id: str = APP_ID
    contract_version: str = CONTRACT_VERSION

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    deterministic_only: bool = True
    registered_artifacts_only: bool = True
    operator_review_required: bool = True
    original_conclusions_preserved: bool = True

    live_model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    ai_orchestrator_execution_allowed: bool = False
    automatic_truth_decision_allowed: bool = False
    automatic_winner_selection_allowed: bool = False
    automatic_conclusion_replacement_allowed: bool = False
    automatic_model_ranking_allowed: bool = False
    automatic_prompt_selection_allowed: bool = False
    automatic_model_switching_allowed: bool = False
    automatic_prompt_switching_allowed: bool = False
    operator_review_bypass_allowed: bool = False

    trade_action_allowed: bool = False
    real_execution_allowed: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    api_key_access_allowed: bool = False
    wallet_key_access_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic contract representation."""

        return {
            "app_id": self.app_id,
            "contract_version": self.contract_version,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "sidecar_only": self.sidecar_only,
            "deterministic_only": self.deterministic_only,
            "registered_artifacts_only": self.registered_artifacts_only,
            "operator_review_required": self.operator_review_required,
            "original_conclusions_preserved": (
                self.original_conclusions_preserved
            ),
            "live_model_invocation_allowed": (
                self.live_model_invocation_allowed
            ),
            "prompt_execution_allowed": self.prompt_execution_allowed,
            "ai_orchestrator_execution_allowed": (
                self.ai_orchestrator_execution_allowed
            ),
            "automatic_truth_decision_allowed": (
                self.automatic_truth_decision_allowed
            ),
            "automatic_winner_selection_allowed": (
                self.automatic_winner_selection_allowed
            ),
            "automatic_conclusion_replacement_allowed": (
                self.automatic_conclusion_replacement_allowed
            ),
            "automatic_model_ranking_allowed": (
                self.automatic_model_ranking_allowed
            ),
            "automatic_prompt_selection_allowed": (
                self.automatic_prompt_selection_allowed
            ),
            "automatic_model_switching_allowed": (
                self.automatic_model_switching_allowed
            ),
            "automatic_prompt_switching_allowed": (
                self.automatic_prompt_switching_allowed
            ),
            "operator_review_bypass_allowed": (
                self.operator_review_bypass_allowed
            ),
            "trade_action_allowed": self.trade_action_allowed,
            "real_execution_allowed": self.real_execution_allowed,
            "broker_connection_allowed": self.broker_connection_allowed,
            "exchange_connection_allowed": self.exchange_connection_allowed,
            "api_key_access_allowed": self.api_key_access_allowed,
            "wallet_key_access_allowed": self.wallet_key_access_allowed,
            "allowed_input_artifact_types": list(
                ALLOWED_INPUT_ARTIFACT_TYPES
            ),
            "allowed_output_artifact_types": list(
                ALLOWED_OUTPUT_ARTIFACT_TYPES
            ),
        }


def build_default_contract() -> MarketNarrativeContextContract:
    """Build the canonical immutable D1 contract."""

    return MarketNarrativeContextContract()


def validate_contract(
    contract: MarketNarrativeContextContract,
) -> tuple[str, ...]:
    """Return deterministic boundary violations."""

    violations: list[str] = []

    if contract.app_id != APP_ID:
        violations.append("INVALID_APP_ID")

    if contract.contract_version != CONTRACT_VERSION:
        violations.append("INVALID_CONTRACT_VERSION")

    required_true = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "deterministic_only",
        "registered_artifacts_only",
        "operator_review_required",
        "original_conclusions_preserved",
    )

    required_false = (
        "live_model_invocation_allowed",
        "prompt_execution_allowed",
        "ai_orchestrator_execution_allowed",
        "automatic_truth_decision_allowed",
        "automatic_winner_selection_allowed",
        "automatic_conclusion_replacement_allowed",
        "automatic_model_ranking_allowed",
        "automatic_prompt_selection_allowed",
        "automatic_model_switching_allowed",
        "automatic_prompt_switching_allowed",
        "operator_review_bypass_allowed",
        "trade_action_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_access_allowed",
        "wallet_key_access_allowed",
    )

    for field_name in required_true:
        if getattr(contract, field_name) is not True:
            violations.append(f"REQUIRED_TRUE:{field_name}")

    for field_name in required_false:
        if getattr(contract, field_name) is not False:
            violations.append(f"REQUIRED_FALSE:{field_name}")

    return tuple(violations)


def assert_valid_contract(
    contract: MarketNarrativeContextContract,
) -> None:
    """Raise when any permanent boundary is violated."""

    violations = validate_contract(contract)

    if violations:
        raise NarrativeBoundaryViolation(";".join(violations))
