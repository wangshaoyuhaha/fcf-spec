from __future__ import annotations


def build_reason_code_visibility_schema() -> dict[str, object]:
    return {
        "schema_id": "UI-RISK-FLAG-VISIBILITY-APP-1-D4",
        "reason_codes_required": True,
        "reason_codes_rendered_explicitly": True,
        "reason_code_source_visible": True,
        "reason_code_count_visible": True,
        "reason_code_meaning_visible": True,
        "reason_code_deletion_allowed": False,
        "reason_code_mutation_allowed": False,
        "reason_code_silencing_allowed": False,
        "risk_flag_downgrade_allowed": False,
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
