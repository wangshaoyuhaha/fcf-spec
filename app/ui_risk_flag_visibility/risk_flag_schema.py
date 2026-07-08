from __future__ import annotations


def build_risk_flag_visibility_schema() -> dict[str, object]:
    return {
        "schema_id": "UI-RISK-FLAG-VISIBILITY-APP-1-D3",
        "risk_flags_required": True,
        "risk_flags_rendered_explicitly": True,
        "risk_flag_severity_visible": True,
        "risk_flag_source_visible": True,
        "risk_flag_count_visible": True,
        "risk_flag_downgrade_allowed": False,
        "risk_flag_deletion_allowed": False,
        "warning_to_approval_conversion_allowed": False,
        "operator_review_required_visible": True,
        "operator_review_bypass_allowed": False,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
    }
