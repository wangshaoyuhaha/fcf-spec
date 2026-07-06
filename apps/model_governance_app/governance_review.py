"""D5 governance review packet for MODEL-GOVERNANCE-APP-1.

This module builds a paper-only governance review packet by combining
source manifest, rule registry, and coverage report summaries.

It does not mutate scores, reason codes, risk flags, source artifacts,
or core modules. It does not enable trading, execution, position sizing,
portfolio actions, future return predictions, or guaranteed performance claims.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


REVIEW_PACKET_STATUS_VALUES: List[str] = [
    "GOVERNANCE_READY_FOR_OPERATOR_REVIEW",
    "GOVERNANCE_REVIEW_REQUIRED",
    "GOVERNANCE_BLOCKED",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def infer_governance_review_status(
    *,
    source_manifest_summary: Mapping[str, Any],
    rule_registry_summary: Mapping[str, Any],
    coverage_summary: Mapping[str, Any],
) -> str:
    """Infer paper-only governance review packet status."""

    source_status = source_manifest_summary.get("loader_status", "")
    registry_status = rule_registry_summary.get("registry_status", "")
    coverage_status = coverage_summary.get("packet_status", "")

    blocking_values = {
        "BLOCKED_MISSING_REQUIRED_SOURCE",
        "GOVERNANCE_BLOCKED",
        "GOVERNANCE_COVERAGE_BLOCKED",
    }
    review_values = {
        "PARTIAL_SOURCE_AVAILABLE",
        "NO_SOURCE_AVAILABLE",
        "GOVERNANCE_REVIEW_REQUIRED",
        "GOVERNANCE_COVERAGE_PARTIAL",
        "GOVERNANCE_COVERAGE_REVIEW_REQUIRED",
    }

    if source_status in blocking_values or registry_status in blocking_values or coverage_status in blocking_values:
        return "GOVERNANCE_BLOCKED"

    if source_status in review_values or registry_status in review_values or coverage_status in review_values:
        return "GOVERNANCE_REVIEW_REQUIRED"

    return "GOVERNANCE_READY_FOR_OPERATOR_REVIEW"


def build_governance_review_packet(
    *,
    packet_id: str,
    source_manifest_summary: Mapping[str, Any],
    rule_registry_summary: Mapping[str, Any],
    coverage_summary: Mapping[str, Any],
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build a paper-only model governance review packet."""

    packet_status = infer_governance_review_status(
        source_manifest_summary=source_manifest_summary,
        rule_registry_summary=rule_registry_summary,
        coverage_summary=coverage_summary,
    )

    return {
        "app_id": "MODEL-GOVERNANCE-APP-1",
        "stage_id": "MODEL-GOVERNANCE-D5",
        "packet_id": packet_id,
        "packet_status": packet_status,
        "created_at_utc": _utc_now_iso(),
        "source_manifest_summary": dict(source_manifest_summary),
        "rule_registry_summary": dict(rule_registry_summary),
        "coverage_summary": dict(coverage_summary),
        "operator_review_packet": {
            "operator_review_required": True,
            "operator_review_bypass_allowed": False,
            "required_action": "HUMAN_REVIEW_REQUIRED_FOR_MODEL_GOVERNANCE",
            "no_execution_receipt_required": True,
        },
        "limitations": [
            "paper_only_governance_review",
            "governance_packet_is_not_a_trade_instruction",
            "rule_registry_is_not_a_trading_rule_engine",
            "coverage_report_does_not_mutate_reason_codes_or_risk_flags",
            "operator_review_required",
        ],
        "notes": list(notes or []),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "trade_action_enabled": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
        "real_trading_allowed": False,
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
    }


def summarize_governance_review_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Return compact D5 governance review packet summary."""

    return {
        "app_id": packet["app_id"],
        "stage_id": packet["stage_id"],
        "packet_id": packet["packet_id"],
        "packet_status": packet["packet_status"],
        "operator_review_required": packet["operator_review_required"],
        "score_mutation_allowed": packet["score_mutation_allowed"],
        "reason_code_mutation_allowed": packet["reason_code_mutation_allowed"],
        "risk_flag_deletion_allowed": packet["risk_flag_deletion_allowed"],
        "trade_action_enabled": packet["trade_action_enabled"],
        "real_execution_allowed": packet["real_execution_allowed"],
        "future_return_prediction_allowed": packet["future_return_prediction_allowed"],
        "guaranteed_performance_claim_allowed": packet["guaranteed_performance_claim_allowed"],
    }


def validate_governance_review_packet(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate D5 governance review packet safety boundary."""

    required_fields = [
        "app_id",
        "stage_id",
        "packet_id",
        "packet_status",
        "source_manifest_summary",
        "rule_registry_summary",
        "coverage_summary",
        "operator_review_packet",
        "operator_review_required",
        "trade_action_enabled",
        "real_execution_allowed",
    ]

    missing_fields = [field for field in required_fields if field not in packet]

    unsafe_true_fields = [
        field
        for field in [
            "score_mutation_allowed",
            "reason_code_mutation_allowed",
            "risk_flag_deletion_allowed",
            "source_content_mutation_allowed",
            "source_deletion_allowed",
            "source_overwrite_allowed",
            "trade_action_enabled",
            "buy_button_enabled",
            "sell_button_enabled",
            "order_button_enabled",
            "real_trading_allowed",
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
        ]
        if packet.get(field) is True
    ]

    return {
        "schema_id": "MODEL-GOVERNANCE-D5-REVIEW-PACKET",
        "is_valid": not missing_fields and not unsafe_true_fields,
        "missing_fields": missing_fields,
        "unsafe_true_fields": unsafe_true_fields,
        "operator_review_required": packet.get("operator_review_required") is True,
        "trade_action_enabled": packet.get("trade_action_enabled") is True,
        "real_execution_allowed": packet.get("real_execution_allowed") is True,
    }
