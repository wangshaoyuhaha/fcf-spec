from __future__ import annotations

from app.ui_risk_flag_visibility.visibility_review_packet import build_visibility_review_packet


def build_final_handoff() -> dict[str, object]:
    packet = build_visibility_review_packet()
    return {
        "app_id": "UI-RISK-FLAG-VISIBILITY-APP-1",
        "stage": "D6_FINAL_HANDOFF_CLOSEOUT",
        "final_status": "COMPLETED" if packet["review_status"] == "VISIBILITY_REVIEW_PASS" else "BLOCKED",
        "source_packet_id": packet["packet_id"],
        "risk_flags_visible": packet["risk_flags_visible"],
        "reason_codes_visible": packet["reason_codes_visible"],
        "blocked_response_state_visible": packet["blocked_response_state_visible"],
        "operator_review_required_visible": packet["operator_review_required_visible"],
        "risk_flag_downgrade_allowed": False,
        "risk_flag_deletion_allowed": False,
        "reason_code_deletion_allowed": False,
        "operator_review_bypass_allowed": False,
        "ui_approval_override_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "next_step": "merge review on main after operator confirmation",
    }
