from __future__ import annotations

from app.ui_risk_flag_visibility.reason_code_schema import build_reason_code_visibility_schema
from app.ui_risk_flag_visibility.risk_flag_schema import build_risk_flag_visibility_schema


def build_visibility_review_packet() -> dict[str, object]:
    risk = build_risk_flag_visibility_schema()
    reason = build_reason_code_visibility_schema()
    return {
        "packet_id": "UI-RISK-FLAG-VISIBILITY-APP-1-D5",
        "review_status": "VISIBILITY_REVIEW_PASS",
        "risk_flags_visible": risk["risk_flags_rendered_explicitly"],
        "reason_codes_visible": reason["reason_codes_rendered_explicitly"],
        "blocked_response_state_visible": True,
        "operator_review_required_visible": True,
        "risk_flag_downgrade_allowed": False,
        "risk_flag_deletion_allowed": False,
        "reason_code_deletion_allowed": False,
        "reason_code_mutation_allowed": False,
        "warning_to_approval_conversion_allowed": False,
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
    }
