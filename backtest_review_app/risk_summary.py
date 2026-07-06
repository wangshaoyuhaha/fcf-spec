"""BACKTEST-REVIEW-D5 backtest risk summary.

A backtest risk summary is paper-only and review-only.
It is not a trade instruction, profit guarantee, order ticket, future return
prediction, real account analysis, position sizing instruction, or execution request.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


STAGE_ID = "BACKTEST-REVIEW-D5"

ALLOWED_RISK_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
    "UNKNOWN",
}

ALLOWED_RISK_CATEGORIES = {
    "sample_size",
    "data_quality",
    "scenario_dependency",
    "operator_decision",
    "metric_instability",
    "market_regime",
    "survivorship_bias",
    "lookahead_bias",
    "liquidity_assumption",
    "execution_assumption",
}

ALLOWED_SUMMARY_STATUS = {
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
    "POSITION SIZE",
    "AUTO REBALANCE",
}


@dataclass(frozen=True)
class BacktestRiskItem:
    risk_id: str
    review_id: str
    result_packet_id: str
    risk_category: str
    risk_level: str
    description: str
    evidence_metric_ids: List[str]
    mitigation_note: str
    operator_review_required: bool
    risk_item_as_trade_instruction: bool
    risk_item_as_profit_guarantee: bool
    automatic_position_sizing_allowed: bool
    automatic_portfolio_action_allowed: bool
    real_execution_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BacktestRiskSummary:
    summary_id: str
    stage_id: str
    review_id: str
    result_packet_id: str
    overall_risk_level: str
    risk_items: List[Dict[str, object]]
    risk_flags: List[str]
    limitations: List[str]
    summary_status: str
    operator_review_required: bool
    safety_flags: Dict[str, bool]
    generated_at_utc: str
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_backtest_risk_item(
    risk_id: str,
    review_id: str,
    result_packet_id: str,
    risk_category: str,
    risk_level: str,
    description: str,
    evidence_metric_ids: List[str],
    mitigation_note: str,
) -> BacktestRiskItem:
    return BacktestRiskItem(
        risk_id=risk_id,
        review_id=review_id,
        result_packet_id=result_packet_id,
        risk_category=risk_category,
        risk_level=risk_level,
        description=description,
        evidence_metric_ids=list(evidence_metric_ids),
        mitigation_note=mitigation_note,
        operator_review_required=True,
        risk_item_as_trade_instruction=False,
        risk_item_as_profit_guarantee=False,
        automatic_position_sizing_allowed=False,
        automatic_portfolio_action_allowed=False,
        real_execution_allowed=False,
    )


def build_backtest_risk_summary(
    summary_id: str,
    review_id: str,
    result_packet_id: str,
    overall_risk_level: str,
    risk_items: List[Dict[str, object]],
    risk_flags: List[str],
    limitations: List[str],
    summary_status: str = "OPERATOR_REVIEW_REQUIRED",
    generated_at_utc: Optional[str] = None,
    notes: str = "",
) -> BacktestRiskSummary:
    return BacktestRiskSummary(
        summary_id=summary_id,
        stage_id=STAGE_ID,
        review_id=review_id,
        result_packet_id=result_packet_id,
        overall_risk_level=overall_risk_level,
        risk_items=list(risk_items),
        risk_flags=list(risk_flags),
        limitations=list(limitations),
        summary_status=summary_status,
        operator_review_required=True,
        safety_flags={
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "risk_summary_as_trade_instruction": False,
            "risk_summary_as_profit_guarantee": False,
            "order_ticket_allowed": False,
            "real_execution_allowed": False,
            "real_account_access_allowed": False,
            "real_position_access_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
        },
        generated_at_utc=generated_at_utc or _now_utc_iso(),
        notes=notes,
    )


def backtest_risk_summary_schema() -> Dict[str, object]:
    return {
        "stage_id": STAGE_ID,
        "schema_name": "backtest_risk_summary",
        "allowed_risk_levels": sorted(ALLOWED_RISK_LEVELS),
        "allowed_risk_categories": sorted(ALLOWED_RISK_CATEGORIES),
        "allowed_summary_status": sorted(ALLOWED_SUMMARY_STATUS),
        "required_fields": [
            "summary_id",
            "review_id",
            "result_packet_id",
            "overall_risk_level",
            "risk_items",
            "risk_flags",
            "limitations",
            "summary_status",
            "operator_review_required",
        ],
        "safety_flags": {
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "risk_summary_as_trade_instruction": False,
            "risk_summary_as_profit_guarantee": False,
            "real_execution_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
        },
    }


def _contains_forbidden_text(value: str) -> bool:
    upper_value = value.upper()
    return any(term in upper_value for term in _FORBIDDEN_TEXT_TERMS)


def validate_backtest_risk_item(item: BacktestRiskItem) -> List[str]:
    errors: List[str] = []

    if not item.risk_id.strip():
        errors.append("risk_id_required")
    if not item.review_id.strip():
        errors.append("review_id_required")
    if not item.result_packet_id.strip():
        errors.append("result_packet_id_required")
    if item.risk_category not in ALLOWED_RISK_CATEGORIES:
        errors.append("invalid_risk_category")
    if item.risk_level not in ALLOWED_RISK_LEVELS:
        errors.append("invalid_risk_level")
    if not item.description.strip():
        errors.append("description_required")
    if not item.evidence_metric_ids:
        errors.append("evidence_metric_ids_required")
    if not item.mitigation_note.strip():
        errors.append("mitigation_note_required")
    if item.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if item.risk_item_as_trade_instruction is not False:
        errors.append("risk_item_must_not_be_trade_instruction")
    if item.risk_item_as_profit_guarantee is not False:
        errors.append("risk_item_must_not_be_profit_guarantee")
    if item.automatic_position_sizing_allowed is not False:
        errors.append("automatic_position_sizing_must_not_be_allowed")
    if item.automatic_portfolio_action_allowed is not False:
        errors.append("automatic_portfolio_action_must_not_be_allowed")
    if item.real_execution_allowed is not False:
        errors.append("real_execution_must_not_be_allowed")
    if _contains_forbidden_text(item.description):
        errors.append("description_must_not_be_trade_or_guarantee_text")
    if _contains_forbidden_text(item.mitigation_note):
        errors.append("mitigation_note_must_not_be_trade_or_guarantee_text")

    return errors


def validate_backtest_risk_summary(summary: BacktestRiskSummary) -> List[str]:
    errors: List[str] = []

    if not summary.summary_id.strip():
        errors.append("summary_id_required")
    if summary.stage_id != STAGE_ID:
        errors.append("invalid_stage_id")
    if not summary.review_id.strip():
        errors.append("review_id_required")
    if not summary.result_packet_id.strip():
        errors.append("result_packet_id_required")
    if summary.overall_risk_level not in ALLOWED_RISK_LEVELS:
        errors.append("invalid_overall_risk_level")
    if not summary.risk_items:
        errors.append("risk_items_required")
    if not summary.risk_flags:
        errors.append("risk_flags_required")
    if not summary.limitations:
        errors.append("limitations_required")
    if summary.summary_status not in ALLOWED_SUMMARY_STATUS:
        errors.append("invalid_summary_status")
    if summary.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")

    flags = summary.safety_flags
    for key in ["paper_only", "local_only", "read_only", "sidecar_only", "operator_review_required"]:
        if flags.get(key) is not True:
            errors.append(f"{key}_must_be_true")

    for key in [
        "risk_summary_as_trade_instruction",
        "risk_summary_as_profit_guarantee",
        "order_ticket_allowed",
        "real_execution_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
    ]:
        if flags.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    for item_payload in summary.risk_items:
        item = BacktestRiskItem(**item_payload)
        errors.extend(validate_backtest_risk_item(item))

    for value in list(summary.risk_flags) + list(summary.limitations) + [summary.notes]:
        if _contains_forbidden_text(value):
            errors.append("summary_text_must_not_be_trade_or_guarantee_text")
            break

    return errors


def is_valid_backtest_risk_item(item: BacktestRiskItem) -> bool:
    return validate_backtest_risk_item(item) == []


def is_valid_backtest_risk_summary(summary: BacktestRiskSummary) -> bool:
    return validate_backtest_risk_summary(summary) == []
