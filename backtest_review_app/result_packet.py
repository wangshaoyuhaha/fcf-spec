"""BACKTEST-REVIEW-D4 backtest result packet.

A backtest result packet is paper-only and review-only.
It is not a profit guarantee, trade instruction, order ticket, future return
prediction, real account analysis, position sizing instruction, or execution request.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


STAGE_ID = "BACKTEST-REVIEW-D4"

ALLOWED_RESULT_STATUS = {
    "DRAFT",
    "READY_FOR_OPERATOR_REVIEW",
    "OPERATOR_REVIEW_REQUIRED",
    "REJECTED_FOR_REVIEW",
}

ALLOWED_RESULT_TYPES = {
    "paper_replay_result",
    "scenario_outcome_result",
    "quality_gated_result",
    "operator_decision_result",
    "archive_replay_result",
    "risk_flag_replay_result",
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
}


@dataclass(frozen=True)
class BacktestResultMetric:
    metric_id: str
    metric_name: str
    metric_value: Optional[float]
    metric_unit: str
    sample_size: int
    interpretation_note: str
    metric_as_trade_instruction: bool
    metric_as_profit_guarantee: bool
    future_return_prediction_allowed: bool
    operator_review_required: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BacktestResultPacket:
    packet_id: str
    stage_id: str
    review_id: str
    result_type: str
    result_status: str
    replay_window: str
    source_metadata_ids: List[str]
    scenario_ids: List[str]
    metrics: List[Dict[str, object]]
    findings: List[str]
    limitations: List[str]
    data_sources: List[str]
    operator_review_required: bool
    safety_flags: Dict[str, bool]
    generated_at_utc: str
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_backtest_result_metric(
    metric_id: str,
    metric_name: str,
    metric_value: Optional[float],
    metric_unit: str,
    sample_size: int,
    interpretation_note: str,
) -> BacktestResultMetric:
    return BacktestResultMetric(
        metric_id=metric_id,
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        sample_size=sample_size,
        interpretation_note=interpretation_note,
        metric_as_trade_instruction=False,
        metric_as_profit_guarantee=False,
        future_return_prediction_allowed=False,
        operator_review_required=True,
    )


def build_backtest_result_packet(
    packet_id: str,
    review_id: str,
    result_type: str,
    replay_window: str,
    source_metadata_ids: List[str],
    metrics: List[Dict[str, object]],
    findings: List[str],
    limitations: List[str],
    data_sources: List[str],
    scenario_ids: Optional[List[str]] = None,
    result_status: str = "OPERATOR_REVIEW_REQUIRED",
    generated_at_utc: Optional[str] = None,
    notes: str = "",
) -> BacktestResultPacket:
    return BacktestResultPacket(
        packet_id=packet_id,
        stage_id=STAGE_ID,
        review_id=review_id,
        result_type=result_type,
        result_status=result_status,
        replay_window=replay_window,
        source_metadata_ids=list(source_metadata_ids),
        scenario_ids=list(scenario_ids or []),
        metrics=list(metrics),
        findings=list(findings),
        limitations=list(limitations),
        data_sources=list(data_sources),
        operator_review_required=True,
        safety_flags={
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
            "real_position_access_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
        },
        generated_at_utc=generated_at_utc or _now_utc_iso(),
        notes=notes,
    )


def _contains_forbidden_text(value: str) -> bool:
    upper_value = value.upper()
    return any(term in upper_value for term in _FORBIDDEN_TEXT_TERMS)


def validate_backtest_result_metric(metric: BacktestResultMetric) -> List[str]:
    errors: List[str] = []

    if not metric.metric_id.strip():
        errors.append("metric_id_required")
    if not metric.metric_name.strip():
        errors.append("metric_name_required")
    if metric.sample_size < 0:
        errors.append("sample_size_must_not_be_negative")
    if metric.metric_as_trade_instruction is not False:
        errors.append("metric_must_not_be_trade_instruction")
    if metric.metric_as_profit_guarantee is not False:
        errors.append("metric_must_not_be_profit_guarantee")
    if metric.future_return_prediction_allowed is not False:
        errors.append("future_return_prediction_must_not_be_allowed")
    if metric.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if _contains_forbidden_text(metric.interpretation_note):
        errors.append("interpretation_note_must_not_be_trade_or_guarantee_text")

    return errors


def validate_backtest_result_packet(packet: BacktestResultPacket) -> List[str]:
    errors: List[str] = []

    if not packet.packet_id.strip():
        errors.append("packet_id_required")
    if packet.stage_id != STAGE_ID:
        errors.append("invalid_stage_id")
    if not packet.review_id.strip():
        errors.append("review_id_required")
    if packet.result_type not in ALLOWED_RESULT_TYPES:
        errors.append("invalid_result_type")
    if packet.result_status not in ALLOWED_RESULT_STATUS:
        errors.append("invalid_result_status")
    if not packet.replay_window.strip():
        errors.append("replay_window_required")
    if not packet.source_metadata_ids:
        errors.append("source_metadata_ids_required")
    if not packet.metrics:
        errors.append("metrics_required")
    if not packet.findings:
        errors.append("findings_required")
    if not packet.limitations:
        errors.append("limitations_required")
    if not packet.data_sources:
        errors.append("data_sources_required")
    if packet.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")

    flags = packet.safety_flags
    for key in ["paper_only", "local_only", "read_only", "sidecar_only", "operator_review_required"]:
        if flags.get(key) is not True:
            errors.append(f"{key}_must_be_true")

    for key in [
        "trade_instruction_allowed",
        "profit_guarantee_allowed",
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

    for metric_payload in packet.metrics:
        metric = BacktestResultMetric(**metric_payload)
        errors.extend(validate_backtest_result_metric(metric))

    for value in list(packet.findings) + list(packet.limitations) + [packet.notes]:
        if _contains_forbidden_text(value):
            errors.append("packet_text_must_not_be_trade_or_guarantee_text")
            break

    return errors


def is_valid_backtest_result_metric(metric: BacktestResultMetric) -> bool:
    return validate_backtest_result_metric(metric) == []


def is_valid_backtest_result_packet(packet: BacktestResultPacket) -> bool:
    return validate_backtest_result_packet(packet) == []
