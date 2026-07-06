"""MARKET-SCENARIO-D5 paper-only scenario review packet.

The packet is a local review artifact. It must not become a trade instruction,
order ticket, position sizing instruction, portfolio action, or execution request.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


STAGE_ID = "MARKET-SCENARIO-D5"

ALLOWED_PACKET_STATUS = {
    "DRAFT",
    "READY_FOR_OPERATOR_REVIEW",
    "OPERATOR_REVIEW_REQUIRED",
    "REJECTED_FOR_REVIEW",
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
    "POSITION SIZE",
}


@dataclass(frozen=True)
class NoExecutionReceipt:
    receipt_id: str
    packet_id: str
    no_execution_statement: str
    operator_review_required: bool
    trade_action_enabled: bool
    buy_button_enabled: bool
    sell_button_enabled: bool
    order_button_enabled: bool
    broker_connection_allowed: bool
    exchange_connection_allowed: bool
    real_execution_allowed: bool
    automatic_position_sizing_allowed: bool
    automatic_portfolio_action_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ScenarioReviewPacket:
    packet_id: str
    stage_id: str
    scenario_id: str
    scenario_summary: str
    scenario_definitions: List[Dict[str, object]]
    assumptions: List[Dict[str, object]]
    risk_contexts: List[Dict[str, object]]
    source_metadata_records: List[Dict[str, object]]
    data_sources: List[str]
    packet_status: str
    operator_review_required: bool
    no_execution_receipt: Dict[str, object]
    safety_flags: Dict[str, bool]
    generated_at_utc: str
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_no_execution_receipt(packet_id: str, receipt_id: Optional[str] = None) -> NoExecutionReceipt:
    selected_receipt_id = receipt_id or f"{packet_id}-no-execution"
    return NoExecutionReceipt(
        receipt_id=selected_receipt_id,
        packet_id=packet_id,
        no_execution_statement=(
            "This packet is paper-only and local-only. It is not an order ticket, "
            "trade instruction, execution request, position sizing instruction, "
            "or portfolio action."
        ),
        operator_review_required=True,
        trade_action_enabled=False,
        buy_button_enabled=False,
        sell_button_enabled=False,
        order_button_enabled=False,
        broker_connection_allowed=False,
        exchange_connection_allowed=False,
        real_execution_allowed=False,
        automatic_position_sizing_allowed=False,
        automatic_portfolio_action_allowed=False,
    )


def build_scenario_review_packet(
    packet_id: str,
    scenario_id: str,
    scenario_summary: str,
    scenario_definitions: List[Dict[str, object]],
    assumptions: List[Dict[str, object]],
    risk_contexts: List[Dict[str, object]],
    source_metadata_records: List[Dict[str, object]],
    data_sources: List[str],
    packet_status: str = "OPERATOR_REVIEW_REQUIRED",
    notes: str = "",
    generated_at_utc: Optional[str] = None,
) -> ScenarioReviewPacket:
    receipt = build_no_execution_receipt(packet_id)
    return ScenarioReviewPacket(
        packet_id=packet_id,
        stage_id=STAGE_ID,
        scenario_id=scenario_id,
        scenario_summary=scenario_summary,
        scenario_definitions=list(scenario_definitions),
        assumptions=list(assumptions),
        risk_contexts=list(risk_contexts),
        source_metadata_records=list(source_metadata_records),
        data_sources=list(data_sources),
        packet_status=packet_status,
        operator_review_required=True,
        no_execution_receipt=receipt.to_dict(),
        safety_flags={
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "scenario_packet_as_order_ticket": False,
            "trade_instruction_allowed": False,
            "real_execution_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "broker_connection_allowed": False,
            "exchange_connection_allowed": False,
        },
        generated_at_utc=generated_at_utc or _now_utc_iso(),
        notes=notes,
    )


def _contains_forbidden_action_text(value: str) -> bool:
    upper_value = value.upper()
    return any(term in upper_value for term in _FORBIDDEN_ACTION_TERMS)


def validate_no_execution_receipt(receipt: Dict[str, object]) -> List[str]:
    errors: List[str] = []

    if not receipt.get("receipt_id"):
        errors.append("receipt_id_required")
    if receipt.get("operator_review_required") is not True:
        errors.append("operator_review_required_must_be_true")
    for key in [
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "real_execution_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
    ]:
        if receipt.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    statement = str(receipt.get("no_execution_statement", ""))
    if not statement.strip():
        errors.append("no_execution_statement_required")

    return errors


def validate_scenario_review_packet(packet: ScenarioReviewPacket) -> List[str]:
    errors: List[str] = []

    if not packet.packet_id.strip():
        errors.append("packet_id_required")
    if packet.stage_id != STAGE_ID:
        errors.append("invalid_stage_id")
    if not packet.scenario_id.strip():
        errors.append("scenario_id_required")
    if not packet.scenario_summary.strip():
        errors.append("scenario_summary_required")
    if not packet.scenario_definitions:
        errors.append("scenario_definitions_required")
    if not packet.assumptions:
        errors.append("assumptions_required")
    if not packet.risk_contexts:
        errors.append("risk_contexts_required")
    if not packet.source_metadata_records:
        errors.append("source_metadata_records_required")
    if not packet.data_sources:
        errors.append("data_sources_required")
    if packet.packet_status not in ALLOWED_PACKET_STATUS:
        errors.append("invalid_packet_status")
    if packet.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")

    flags = packet.safety_flags
    for key in ["paper_only", "local_only", "read_only", "sidecar_only", "operator_review_required"]:
        if flags.get(key) is not True:
            errors.append(f"{key}_must_be_true")
    for key in [
        "scenario_packet_as_order_ticket",
        "trade_instruction_allowed",
        "real_execution_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
    ]:
        if flags.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    errors.extend(validate_no_execution_receipt(packet.no_execution_receipt))

    if _contains_forbidden_action_text(packet.scenario_summary):
        errors.append("scenario_summary_must_not_be_trade_instruction")
    if _contains_forbidden_action_text(packet.notes):
        errors.append("notes_must_not_be_trade_instruction")

    return errors


def is_valid_scenario_review_packet(packet: ScenarioReviewPacket) -> bool:
    return validate_scenario_review_packet(packet) == []
