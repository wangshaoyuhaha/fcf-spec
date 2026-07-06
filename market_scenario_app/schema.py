"""MARKET-SCENARIO-D3 scenario definition schema.

The schema is paper-only and review-only.
A scenario definition is not a trade instruction, order ticket, or execution request.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


STAGE_ID = "MARKET-SCENARIO-D3"

ALLOWED_SCENARIO_TYPES = {
    "base_case",
    "risk_off",
    "risk_on",
    "liquidity_stress",
    "data_quality_degraded",
    "policy_event",
    "earnings_event",
    "crypto_volatility",
    "futures_basis_shift",
}

ALLOWED_MARKET_SCOPES = {
    "single_asset",
    "sector",
    "theme",
    "cross_asset",
    "portfolio_context",
    "macro_context",
}

ALLOWED_DATA_QUALITY_STATES = {
    "PASS_STRICT",
    "PASS_LIMITED",
    "FAIL_QUARANTINE",
    "UNKNOWN",
}

ALLOWED_CONFIDENCE_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
}

ALLOWED_REVIEW_STATUS = {
    "DRAFT",
    "READY_FOR_OPERATOR_REVIEW",
    "OPERATOR_REVIEW_REQUIRED",
    "REJECTED_FOR_REVIEW",
}

_FORBIDDEN_LABEL_TERMS = {
    "BUY",
    "SELL",
    "ORDER",
    "EXECUTE",
    "EXECUTION",
    "TRADE NOW",
    "PLACE ORDER",
}


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    scenario_label: str
    scenario_type: str
    market_scope: str
    asset_classes: List[str]
    time_horizon: str
    source_metadata_ids: List[str]
    data_quality_state: str
    confidence_level: str
    scenario_score: Optional[float]
    scenario_review_status: str
    operator_review_required: bool
    trade_instruction_allowed: bool
    order_ticket_allowed: bool
    real_execution_allowed: bool
    automatic_position_sizing_allowed: bool
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def scenario_definition_schema() -> Dict[str, object]:
    return {
        "stage_id": STAGE_ID,
        "schema_name": "market_scenario_definition",
        "required_fields": [
            "scenario_id",
            "scenario_label",
            "scenario_type",
            "market_scope",
            "asset_classes",
            "time_horizon",
            "source_metadata_ids",
            "data_quality_state",
            "confidence_level",
            "scenario_review_status",
            "operator_review_required",
        ],
        "allowed_scenario_types": sorted(ALLOWED_SCENARIO_TYPES),
        "allowed_market_scopes": sorted(ALLOWED_MARKET_SCOPES),
        "allowed_data_quality_states": sorted(ALLOWED_DATA_QUALITY_STATES),
        "allowed_confidence_levels": sorted(ALLOWED_CONFIDENCE_LEVELS),
        "allowed_review_status": sorted(ALLOWED_REVIEW_STATUS),
        "safety_flags": {
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "scenario_label_as_trade_instruction": False,
            "scenario_score_as_trade_instruction": False,
            "scenario_review_status_bypass_operator_review": False,
            "scenario_packet_as_order_ticket": False,
            "automatic_position_sizing_allowed": False,
            "real_execution_allowed": False,
        },
    }


def build_scenario_definition(
    scenario_id: str,
    scenario_label: str,
    scenario_type: str,
    market_scope: str,
    asset_classes: List[str],
    time_horizon: str,
    source_metadata_ids: List[str],
    data_quality_state: str,
    confidence_level: str,
    scenario_review_status: str = "OPERATOR_REVIEW_REQUIRED",
    scenario_score: Optional[float] = None,
    notes: str = "",
) -> ScenarioDefinition:
    return ScenarioDefinition(
        scenario_id=scenario_id,
        scenario_label=scenario_label,
        scenario_type=scenario_type,
        market_scope=market_scope,
        asset_classes=list(asset_classes),
        time_horizon=time_horizon,
        source_metadata_ids=list(source_metadata_ids),
        data_quality_state=data_quality_state,
        confidence_level=confidence_level,
        scenario_score=scenario_score,
        scenario_review_status=scenario_review_status,
        operator_review_required=True,
        trade_instruction_allowed=False,
        order_ticket_allowed=False,
        real_execution_allowed=False,
        automatic_position_sizing_allowed=False,
        notes=notes,
    )


def validate_scenario_definition(definition: ScenarioDefinition) -> List[str]:
    errors: List[str] = []

    if not definition.scenario_id.strip():
        errors.append("scenario_id_required")
    if not definition.scenario_label.strip():
        errors.append("scenario_label_required")
    if definition.scenario_type not in ALLOWED_SCENARIO_TYPES:
        errors.append("invalid_scenario_type")
    if definition.market_scope not in ALLOWED_MARKET_SCOPES:
        errors.append("invalid_market_scope")
    if not definition.asset_classes:
        errors.append("asset_classes_required")
    if not definition.time_horizon.strip():
        errors.append("time_horizon_required")
    if not definition.source_metadata_ids:
        errors.append("source_metadata_ids_required")
    if definition.data_quality_state not in ALLOWED_DATA_QUALITY_STATES:
        errors.append("invalid_data_quality_state")
    if definition.confidence_level not in ALLOWED_CONFIDENCE_LEVELS:
        errors.append("invalid_confidence_level")
    if definition.scenario_review_status not in ALLOWED_REVIEW_STATUS:
        errors.append("invalid_scenario_review_status")
    if definition.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if definition.trade_instruction_allowed is not False:
        errors.append("trade_instruction_must_not_be_allowed")
    if definition.order_ticket_allowed is not False:
        errors.append("order_ticket_must_not_be_allowed")
    if definition.real_execution_allowed is not False:
        errors.append("real_execution_must_not_be_allowed")
    if definition.automatic_position_sizing_allowed is not False:
        errors.append("automatic_position_sizing_must_not_be_allowed")
    if definition.scenario_score is not None:
        if definition.scenario_score < 0 or definition.scenario_score > 100:
            errors.append("scenario_score_out_of_range")
    label_upper = definition.scenario_label.upper()
    if any(term in label_upper for term in _FORBIDDEN_LABEL_TERMS):
        errors.append("scenario_label_must_not_be_trade_instruction")

    return errors


def is_valid_scenario_definition(definition: ScenarioDefinition) -> bool:
    return validate_scenario_definition(definition) == []
