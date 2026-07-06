"""BACKTEST-REVIEW-D3 backtest review schema.

The schema is paper-only and review-only.
A backtest review is not a trade instruction, profit guarantee, order ticket,
execution request, future return prediction, or real account analysis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional


STAGE_ID = "BACKTEST-REVIEW-D3"

ALLOWED_BACKTEST_REVIEW_TYPES = {
    "paper_signal_replay",
    "scenario_outcome_review",
    "quality_gated_replay",
    "operator_decision_review",
    "archive_replay",
    "risk_flag_replay",
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

_FORBIDDEN_TEXT_TERMS = {
    "BUY NOW",
    "SELL NOW",
    "PLACE ORDER",
    "EXECUTE ORDER",
    "SEND ORDER",
    "LIVE ORDER",
    "GUARANTEED PROFIT",
    "GUARANTEED RETURN",
    "RISK FREE",
    "FUTURE RETURN",
}


@dataclass(frozen=True)
class BacktestReviewDefinition:
    review_id: str
    review_label: str
    review_type: str
    market_scope: str
    asset_classes: List[str]
    replay_window: str
    source_metadata_ids: List[str]
    scenario_ids: List[str]
    data_quality_state: str
    confidence_level: str
    review_status: str
    operator_review_required: bool
    trade_instruction_allowed: bool
    profit_guarantee_allowed: bool
    order_ticket_allowed: bool
    real_execution_allowed: bool
    real_account_access_allowed: bool
    future_return_prediction_allowed: bool
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BacktestMetricDefinition:
    metric_id: str
    review_id: str
    metric_name: str
    metric_value: Optional[float]
    metric_unit: str
    sample_size: int
    interpretation_note: str
    metric_as_trade_instruction: bool
    metric_as_profit_guarantee: bool
    operator_review_required: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def backtest_review_schema() -> Dict[str, object]:
    return {
        "stage_id": STAGE_ID,
        "schema_name": "backtest_review_definition",
        "required_fields": [
            "review_id",
            "review_label",
            "review_type",
            "market_scope",
            "asset_classes",
            "replay_window",
            "source_metadata_ids",
            "data_quality_state",
            "confidence_level",
            "review_status",
            "operator_review_required",
        ],
        "allowed_backtest_review_types": sorted(ALLOWED_BACKTEST_REVIEW_TYPES),
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
            "trade_instruction_allowed": False,
            "profit_guarantee_allowed": False,
            "order_ticket_allowed": False,
            "real_execution_allowed": False,
            "real_account_access_allowed": False,
            "future_return_prediction_allowed": False,
        },
    }


def build_backtest_review_definition(
    review_id: str,
    review_label: str,
    review_type: str,
    market_scope: str,
    asset_classes: List[str],
    replay_window: str,
    source_metadata_ids: List[str],
    data_quality_state: str,
    confidence_level: str,
    scenario_ids: Optional[List[str]] = None,
    review_status: str = "OPERATOR_REVIEW_REQUIRED",
    notes: str = "",
) -> BacktestReviewDefinition:
    return BacktestReviewDefinition(
        review_id=review_id,
        review_label=review_label,
        review_type=review_type,
        market_scope=market_scope,
        asset_classes=list(asset_classes),
        replay_window=replay_window,
        source_metadata_ids=list(source_metadata_ids),
        scenario_ids=list(scenario_ids or []),
        data_quality_state=data_quality_state,
        confidence_level=confidence_level,
        review_status=review_status,
        operator_review_required=True,
        trade_instruction_allowed=False,
        profit_guarantee_allowed=False,
        order_ticket_allowed=False,
        real_execution_allowed=False,
        real_account_access_allowed=False,
        future_return_prediction_allowed=False,
        notes=notes,
    )


def build_backtest_metric_definition(
    metric_id: str,
    review_id: str,
    metric_name: str,
    metric_value: Optional[float],
    metric_unit: str,
    sample_size: int,
    interpretation_note: str,
) -> BacktestMetricDefinition:
    return BacktestMetricDefinition(
        metric_id=metric_id,
        review_id=review_id,
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        sample_size=sample_size,
        interpretation_note=interpretation_note,
        metric_as_trade_instruction=False,
        metric_as_profit_guarantee=False,
        operator_review_required=True,
    )


def _contains_forbidden_text(value: str) -> bool:
    upper_value = value.upper()
    return any(term in upper_value for term in _FORBIDDEN_TEXT_TERMS)


def validate_backtest_review_definition(definition: BacktestReviewDefinition) -> List[str]:
    errors: List[str] = []

    if not definition.review_id.strip():
        errors.append("review_id_required")
    if not definition.review_label.strip():
        errors.append("review_label_required")
    if definition.review_type not in ALLOWED_BACKTEST_REVIEW_TYPES:
        errors.append("invalid_review_type")
    if definition.market_scope not in ALLOWED_MARKET_SCOPES:
        errors.append("invalid_market_scope")
    if not definition.asset_classes:
        errors.append("asset_classes_required")
    if not definition.replay_window.strip():
        errors.append("replay_window_required")
    if not definition.source_metadata_ids:
        errors.append("source_metadata_ids_required")
    if definition.data_quality_state not in ALLOWED_DATA_QUALITY_STATES:
        errors.append("invalid_data_quality_state")
    if definition.confidence_level not in ALLOWED_CONFIDENCE_LEVELS:
        errors.append("invalid_confidence_level")
    if definition.review_status not in ALLOWED_REVIEW_STATUS:
        errors.append("invalid_review_status")
    if definition.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if definition.trade_instruction_allowed is not False:
        errors.append("trade_instruction_must_not_be_allowed")
    if definition.profit_guarantee_allowed is not False:
        errors.append("profit_guarantee_must_not_be_allowed")
    if definition.order_ticket_allowed is not False:
        errors.append("order_ticket_must_not_be_allowed")
    if definition.real_execution_allowed is not False:
        errors.append("real_execution_must_not_be_allowed")
    if definition.real_account_access_allowed is not False:
        errors.append("real_account_access_must_not_be_allowed")
    if definition.future_return_prediction_allowed is not False:
        errors.append("future_return_prediction_must_not_be_allowed")
    if _contains_forbidden_text(definition.review_label):
        errors.append("review_label_must_not_be_trade_or_guarantee_text")
    if _contains_forbidden_text(definition.notes):
        errors.append("notes_must_not_be_trade_or_guarantee_text")

    return errors


def validate_backtest_metric_definition(metric: BacktestMetricDefinition) -> List[str]:
    errors: List[str] = []

    if not metric.metric_id.strip():
        errors.append("metric_id_required")
    if not metric.review_id.strip():
        errors.append("review_id_required")
    if not metric.metric_name.strip():
        errors.append("metric_name_required")
    if metric.sample_size < 0:
        errors.append("sample_size_must_not_be_negative")
    if metric.metric_as_trade_instruction is not False:
        errors.append("metric_must_not_be_trade_instruction")
    if metric.metric_as_profit_guarantee is not False:
        errors.append("metric_must_not_be_profit_guarantee")
    if metric.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if _contains_forbidden_text(metric.interpretation_note):
        errors.append("interpretation_note_must_not_be_trade_or_guarantee_text")

    return errors


def is_valid_backtest_review_definition(definition: BacktestReviewDefinition) -> bool:
    return validate_backtest_review_definition(definition) == []


def is_valid_backtest_metric_definition(metric: BacktestMetricDefinition) -> bool:
    return validate_backtest_metric_definition(metric) == []
