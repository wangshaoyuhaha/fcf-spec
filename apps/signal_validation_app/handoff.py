"""D6 final workflow handoff for SIGNAL-VALIDATION-APP-1."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping


COMPLETED_SIGNAL_VALIDATION_STAGES: List[str] = [
    "SIGNAL-VALIDATION-D1",
    "SIGNAL-VALIDATION-D2",
    "SIGNAL-VALIDATION-D3",
    "SIGNAL-VALIDATION-D4",
    "SIGNAL-VALIDATION-D5",
    "SIGNAL-VALIDATION-D6",
]

SIGNAL_VALIDATION_OUTPUTS: List[str] = [
    "signal_validation_contract",
    "source_packet_manifest",
    "signal_evidence_matrix",
    "signal_conflict_report",
    "signal_validation_report_packet",
    "final_workflow_handoff",
]

NEXT_RECOMMENDED_SIDECAR_SEQUENCE: List[str] = [
    "MODEL-GOVERNANCE-APP-1",
    "WATCHLIST-LIFECYCLE-APP-1",
]

FINAL_SAFETY_BOUNDARY: Dict[str, bool] = {
    "paper_only": True,
    "local_only": True,
    "read_only": True,
    "sidecar_only": True,
    "operator_review_required": True,
    "operator_review_bypass_allowed": False,
    "p1_p47_core_mutation_allowed": False,
    "p48_core_expansion_allowed": False,
    "source_content_mutation_allowed": False,
    "source_deletion_allowed": False,
    "source_overwrite_allowed": False,
    "real_trading_allowed": False,
    "real_execution_allowed": False,
    "broker_connection_allowed": False,
    "exchange_connection_allowed": False,
    "api_key_storage_allowed": False,
    "wallet_private_key_access_allowed": False,
    "real_account_access_allowed": False,
    "real_position_access_allowed": False,
    "trade_action_enabled": False,
    "buy_button_enabled": False,
    "sell_button_enabled": False,
    "order_button_enabled": False,
    "automatic_position_sizing_allowed": False,
    "automatic_portfolio_action_allowed": False,
    "future_return_prediction_allowed": False,
    "guaranteed_performance_claim_allowed": False,
    "tag_creation_allowed": False,
    "release_creation_allowed": False,
    "deploy_action_allowed": False,
}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_signal_validation_final_handoff(
    *,
    branch_name: str = "sidecar-signal-validation-app-1",
    validation_baseline: str = "1369 passed",
    notes: List[str] | None = None,
) -> Dict[str, Any]:
    """Build the final paper-only workflow handoff packet."""

    return {
        "app_id": "SIGNAL-VALIDATION-APP-1",
        "stage_id": "SIGNAL-VALIDATION-D6",
        "handoff_type": "final_workflow_handoff_and_closeout",
        "created_at_utc": _utc_now_iso(),
        "branch_name": branch_name,
        "validation_baseline": validation_baseline,
        "completed_stages": list(COMPLETED_SIGNAL_VALIDATION_STAGES),
        "outputs": list(SIGNAL_VALIDATION_OUTPUTS),
        "purpose": (
            "Validate paper-only signal evidence consistency across existing "
            "local sidecar outputs and produce operator-review-ready validation packets."
        ),
        "reads_from": [
            "STOCK-APP-1",
            "AI-CONTEXT-1",
            "OPERATOR-REVIEW-APP-1",
            "REPORT-ARCHIVE-APP-1",
            "DATA-QUALITY-OPS-APP-1",
            "MARKET-SCENARIO-APP-1",
            "BACKTEST-REVIEW-APP-1",
        ],
        "next_recommended_sidecar_sequence": list(NEXT_RECOMMENDED_SIDECAR_SEQUENCE),
        "merge_policy": {
            "auto_merge_allowed": False,
            "merge_requires_user_confirmation": True,
            "main_final_current_state_file_required_after_merge": True,
        },
        "release_policy": {
            "tag_allowed": False,
            "release_allowed": False,
            "deploy_allowed": False,
        },
        "safety_boundary": dict(FINAL_SAFETY_BOUNDARY),
        "closeout_summary": {
            "d1": "contract and safety boundary",
            "d2": "read-only source packet loader",
            "d3": "evidence matrix schema",
            "d4": "conflict and inconsistency detector",
            "d5": "paper-only validation report packet",
            "d6": "final workflow handoff and closeout",
        },
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "notes": list(notes or []),
    }


def validate_signal_validation_final_handoff(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate the final handoff packet safety boundary."""

    required_fields = [
        "app_id",
        "stage_id",
        "handoff_type",
        "branch_name",
        "validation_baseline",
        "completed_stages",
        "outputs",
        "merge_policy",
        "release_policy",
        "safety_boundary",
        "operator_review_required",
    ]
    missing_fields = [field for field in required_fields if field not in packet]

    boundary = packet.get("safety_boundary", {})
    unsafe_true_fields = [
        key
        for key in [
            "p1_p47_core_mutation_allowed",
            "p48_core_expansion_allowed",
            "source_content_mutation_allowed",
            "source_deletion_allowed",
            "source_overwrite_allowed",
            "real_trading_allowed",
            "real_execution_allowed",
            "broker_connection_allowed",
            "exchange_connection_allowed",
            "api_key_storage_allowed",
            "wallet_private_key_access_allowed",
            "real_account_access_allowed",
            "real_position_access_allowed",
            "trade_action_enabled",
            "buy_button_enabled",
            "sell_button_enabled",
            "order_button_enabled",
            "automatic_position_sizing_allowed",
            "automatic_portfolio_action_allowed",
            "future_return_prediction_allowed",
            "guaranteed_performance_claim_allowed",
            "tag_creation_allowed",
            "release_creation_allowed",
            "deploy_action_allowed",
        ]
        if boundary.get(key) is True
    ]

    completed = set(packet.get("completed_stages", []))
    missing_stages = [
        stage
        for stage in COMPLETED_SIGNAL_VALIDATION_STAGES
        if stage not in completed
    ]

    return {
        "schema_id": "SIGNAL-VALIDATION-D6-FINAL-HANDOFF",
        "is_valid": not missing_fields and not unsafe_true_fields and not missing_stages,
        "missing_fields": missing_fields,
        "unsafe_true_fields": unsafe_true_fields,
        "missing_stages": missing_stages,
        "operator_review_required": packet.get("operator_review_required") is True,
        "auto_merge_allowed": packet.get("merge_policy", {}).get("auto_merge_allowed") is True,
        "tag_allowed": packet.get("release_policy", {}).get("tag_allowed") is True,
        "release_allowed": packet.get("release_policy", {}).get("release_allowed") is True,
        "deploy_allowed": packet.get("release_policy", {}).get("deploy_allowed") is True,
    }


def summarize_signal_validation_final_handoff(packet: Mapping[str, Any]) -> Dict[str, Any]:
    """Return compact final handoff summary."""

    return {
        "app_id": packet["app_id"],
        "stage_id": packet["stage_id"],
        "branch_name": packet["branch_name"],
        "validation_baseline": packet["validation_baseline"],
        "completed_stage_count": len(packet["completed_stages"]),
        "output_count": len(packet["outputs"]),
        "next_recommended_sidecar_sequence": list(packet["next_recommended_sidecar_sequence"]),
        "operator_review_required": packet["operator_review_required"],
        "auto_merge_allowed": packet["merge_policy"]["auto_merge_allowed"],
        "tag_allowed": packet["release_policy"]["tag_allowed"],
        "release_allowed": packet["release_policy"]["release_allowed"],
        "deploy_allowed": packet["release_policy"]["deploy_allowed"],
        "real_execution_allowed": packet["safety_boundary"]["real_execution_allowed"],
        "trade_action_enabled": packet["safety_boundary"]["trade_action_enabled"],
    }
