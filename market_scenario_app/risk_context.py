"""MARKET-SCENARIO-D4 scenario assumption and risk context model.

Paper-only model for scenario assumptions and risk context.
This module does not create trade instructions, order tickets, position sizing,
portfolio actions, real execution, or broker/exchange connectivity.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from market_scenario_app.schema import (
    ALLOWED_CONFIDENCE_LEVELS,
    ALLOWED_DATA_QUALITY_STATES,
)


STAGE_ID = "MARKET-SCENARIO-D4"

ALLOWED_ASSUMPTION_TYPES = {
    "liquidity",
    "volatility",
    "policy_event",
    "data_quality",
    "cross_asset",
    "sector_rotation",
    "crypto_flow",
    "futures_basis",
    "operator_note",
}

ALLOWED_RISK_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
    "UNKNOWN",
}

_FORBIDDEN_ACTION_TERMS = {
    "BUY NOW",
    "SELL NOW",
    "PLACE ORDER",
    "EXECUTE ORDER",
    "SEND ORDER",
    "LIVE ORDER",
    "AUTO POSITION",
    "AUTO REBALANCE",
}


@dataclass(frozen=True)
class ScenarioAssumption:
    assumption_id: str
    scenario_id: str
    assumption_type: str
    description: str
    evidence_source_ids: List[str]
    confidence_level: str
    data_quality_state: str
    operator_review_required: bool
    trade_instruction_allowed: bool
    real_execution_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RiskContext:
    risk_context_id: str
    scenario_id: str
    risk_level: str
    risk_factors: List[str]
    risk_flags: List[str]
    source_metadata_ids: List[str]
    scenario_score_adjustment: Optional[float]
    mitigation_notes: str
    operator_review_required: bool
    scenario_score_as_trade_instruction: bool
    automatic_position_sizing_allowed: bool
    automatic_portfolio_action_allowed: bool
    order_ticket_allowed: bool
    real_execution_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def build_scenario_assumption(
    assumption_id: str,
    scenario_id: str,
    assumption_type: str,
    description: str,
    evidence_source_ids: List[str],
    confidence_level: str,
    data_quality_state: str,
) -> ScenarioAssumption:
    return ScenarioAssumption(
        assumption_id=assumption_id,
        scenario_id=scenario_id,
        assumption_type=assumption_type,
        description=description,
        evidence_source_ids=list(evidence_source_ids),
        confidence_level=confidence_level,
        data_quality_state=data_quality_state,
        operator_review_required=True,
        trade_instruction_allowed=False,
        real_execution_allowed=False,
    )


def build_risk_context(
    risk_context_id: str,
    scenario_id: str,
    risk_level: str,
    risk_factors: List[str],
    risk_flags: List[str],
    source_metadata_ids: List[str],
    mitigation_notes: str,
    scenario_score_adjustment: Optional[float] = None,
) -> RiskContext:
    return RiskContext(
        risk_context_id=risk_context_id,
        scenario_id=scenario_id,
        risk_level=risk_level,
        risk_factors=list(risk_factors),
        risk_flags=list(risk_flags),
        source_metadata_ids=list(source_metadata_ids),
        scenario_score_adjustment=scenario_score_adjustment,
        mitigation_notes=mitigation_notes,
        operator_review_required=True,
        scenario_score_as_trade_instruction=False,
        automatic_position_sizing_allowed=False,
        automatic_portfolio_action_allowed=False,
        order_ticket_allowed=False,
        real_execution_allowed=False,
    )


def assumption_risk_context_schema() -> Dict[str, object]:
    return {
        "stage_id": STAGE_ID,
        "schema_name": "scenario_assumption_and_risk_context",
        "allowed_assumption_types": sorted(ALLOWED_ASSUMPTION_TYPES),
        "allowed_risk_levels": sorted(ALLOWED_RISK_LEVELS),
        "safety_flags": {
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "trade_instruction_allowed": False,
            "scenario_score_as_trade_instruction": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "order_ticket_allowed": False,
            "real_execution_allowed": False,
        },
    }


def _contains_forbidden_action_text(value: str) -> bool:
    upper_value = value.upper()
    return any(term in upper_value for term in _FORBIDDEN_ACTION_TERMS)


def validate_scenario_assumption(assumption: ScenarioAssumption) -> List[str]:
    errors: List[str] = []

    if not assumption.assumption_id.strip():
        errors.append("assumption_id_required")
    if not assumption.scenario_id.strip():
        errors.append("scenario_id_required")
    if assumption.assumption_type not in ALLOWED_ASSUMPTION_TYPES:
        errors.append("invalid_assumption_type")
    if not assumption.description.strip():
        errors.append("description_required")
    if not assumption.evidence_source_ids:
        errors.append("evidence_source_ids_required")
    if assumption.confidence_level not in ALLOWED_CONFIDENCE_LEVELS:
        errors.append("invalid_confidence_level")
    if assumption.data_quality_state not in ALLOWED_DATA_QUALITY_STATES:
        errors.append("invalid_data_quality_state")
    if assumption.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if assumption.trade_instruction_allowed is not False:
        errors.append("trade_instruction_must_not_be_allowed")
    if assumption.real_execution_allowed is not False:
        errors.append("real_execution_must_not_be_allowed")
    if _contains_forbidden_action_text(assumption.description):
        errors.append("assumption_description_must_not_be_trade_instruction")

    return errors


def validate_risk_context(risk_context: RiskContext) -> List[str]:
    errors: List[str] = []

    if not risk_context.risk_context_id.strip():
        errors.append("risk_context_id_required")
    if not risk_context.scenario_id.strip():
        errors.append("scenario_id_required")
    if risk_context.risk_level not in ALLOWED_RISK_LEVELS:
        errors.append("invalid_risk_level")
    if not risk_context.risk_factors:
        errors.append("risk_factors_required")
    if not risk_context.risk_flags:
        errors.append("risk_flags_required")
    if not risk_context.source_metadata_ids:
        errors.append("source_metadata_ids_required")
    if risk_context.scenario_score_adjustment is not None:
        if risk_context.scenario_score_adjustment < -100 or risk_context.scenario_score_adjustment > 100:
            errors.append("scenario_score_adjustment_out_of_range")
    if risk_context.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if risk_context.scenario_score_as_trade_instruction is not False:
        errors.append("scenario_score_must_not_be_trade_instruction")
    if risk_context.automatic_position_sizing_allowed is not False:
        errors.append("automatic_position_sizing_must_not_be_allowed")
    if risk_context.automatic_portfolio_action_allowed is not False:
        errors.append("automatic_portfolio_action_must_not_be_allowed")
    if risk_context.order_ticket_allowed is not False:
        errors.append("order_ticket_must_not_be_allowed")
    if risk_context.real_execution_allowed is not False:
        errors.append("real_execution_must_not_be_allowed")
    if _contains_forbidden_action_text(risk_context.mitigation_notes):
        errors.append("mitigation_notes_must_not_be_trade_instruction")

    return errors


def is_valid_scenario_assumption(assumption: ScenarioAssumption) -> bool:
    return validate_scenario_assumption(assumption) == []


def is_valid_risk_context(risk_context: RiskContext) -> bool:
    return validate_risk_context(risk_context) == []
