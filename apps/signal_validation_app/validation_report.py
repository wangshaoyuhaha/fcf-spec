"""D5 paper-only validation report packet for SIGNAL-VALIDATION-APP-1."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping

from .conflict_detector import detect_signal_conflicts, summarize_conflict_detection
from .evidence_matrix import EvidenceMatrix


REPORT_STATUS_VALUES: List[str] = [
    "VALIDATION_READY_FOR_OPERATOR_REVIEW",
    "VALIDATION_REVIEW_REQUIRED",
    "VALIDATION_CONFLICT_DETECTED",
    "VALIDATION_BLOCKED",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_validation_report_status(conflict_report: Mapping[str, Any]) -> str:
    """Infer paper-only report status from D4 conflict detection."""

    detection_status = conflict_report.get("detection_status", "REVIEW_REQUIRED")

    if detection_status == "VALIDATION_BLOCKED":
        return "VALIDATION_BLOCKED"
    if detection_status == "CONFLICT_DETECTED":
        return "VALIDATION_CONFLICT_DETECTED"
    if detection_status == "NO_CONFLICT_DETECTED":
        return "VALIDATION_READY_FOR_OPERATOR_REVIEW"

    return "VALIDATION_REVIEW_REQUIRED"


def build_validation_report_packet(
    *,
    matrix: EvidenceMatrix,
    report_id: str,
    source_manifest_summary: Mapping[str, Any] | None = None,
    notes: List[str] | None = None,
) -> Dict[str, Any]:
    """Build a paper-only signal validation report packet."""

    matrix_payload = matrix.to_dict()
    conflict_report = detect_signal_conflicts(matrix)
    conflict_summary = summarize_conflict_detection(conflict_report)
    report_status = infer_validation_report_status(conflict_report)

    return {
        "app_id": "SIGNAL-VALIDATION-APP-1",
        "stage_id": "SIGNAL-VALIDATION-D5",
        "report_id": report_id,
        "candidate_id": matrix.candidate_id,
        "matrix_id": matrix.matrix_id,
        "report_status": report_status,
        "created_at_utc": _utc_now_iso(),
        "source_manifest_summary": dict(source_manifest_summary or {}),
        "evidence_matrix_summary": {
            "overall_validation_status": matrix_payload["overall_validation_status"],
            "evidence_row_count": len(matrix_payload["evidence_rows"]),
            "operator_review_required": matrix_payload["operator_review_required"],
        },
        "conflict_summary": conflict_summary,
        "conflict_report": conflict_report,
        "operator_review_packet": {
            "operator_review_required": True,
            "operator_review_bypass_allowed": False,
            "required_action": "HUMAN_REVIEW_REQUIRED_BEFORE_ANY_DOWNSTREAM_USE",
            "no_execution_receipt_required": True,
        },
        "limitations": [
            "paper_only_validation_report",
            "historical_and_local_sources_may_be_incomplete",
            "validation_status_is_not_a_trade_instruction",
            "conflict_report_is_not_an_order_ticket",
            "operator_review_required",
        ],
        "notes": list(notes or []),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "trade_action_enabled": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
        "real_execution_allowed": False,
        "broker_connection_allowed": False,
        "exchange_connection_allowed": False,
        "api_key_storage_allowed": False,
        "wallet_private_key_access_allowed": False,
        "real_account_access_allowed": False,
        "real_position_access_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
        "p1_p47_core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
    }


def summarize_validation_report_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Return compact D5 validation report summary."""

    return {
        "app_id": packet["app_id"],
        "stage_id": packet["stage_id"],
        "report_id": packet["report_id"],
        "candidate_id": packet["candidate_id"],
        "matrix_id": packet["matrix_id"],
        "report_status": packet["report_status"],
        "conflict_count": packet["conflict_summary"]["conflict_count"],
        "blocking_conflict_count": packet["conflict_summary"]["blocking_conflict_count"],
        "operator_review_required": packet["operator_review_required"],
        "trade_action_enabled": packet["trade_action_enabled"],
        "real_execution_allowed": packet["real_execution_allowed"],
        "future_return_prediction_allowed": packet["future_return_prediction_allowed"],
        "guaranteed_performance_claim_allowed": packet["guaranteed_performance_claim_allowed"],
    }


def validate_validation_report_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate that D5 packet keeps the safety boundary closed."""

    required_fields = [
        "app_id",
        "stage_id",
        "report_id",
        "candidate_id",
        "matrix_id",
        "report_status",
        "operator_review_packet",
        "paper_only",
        "read_only",
        "sidecar_only",
        "trade_action_enabled",
        "real_execution_allowed",
    ]

    missing_fields = [field for field in required_fields if field not in packet]

    forbidden_true_fields = [
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "p1_p47_core_mutation_allowed",
        "p48_core_expansion_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
    ]

    unsafe_fields = [field for field in forbidden_true_fields if packet.get(field) is True]

    return {
        "schema_id": "SIGNAL-VALIDATION-D5-REPORT-PACKET",
        "is_valid": not missing_fields and not unsafe_fields,
        "missing_fields": missing_fields,
        "unsafe_fields": unsafe_fields,
        "operator_review_required": packet.get("operator_review_required") is True,
        "paper_only": packet.get("paper_only") is True,
        "read_only": packet.get("read_only") is True,
        "sidecar_only": packet.get("sidecar_only") is True,
    }
