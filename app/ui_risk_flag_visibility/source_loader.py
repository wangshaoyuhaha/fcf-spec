from __future__ import annotations


def load_ui_visibility_sources() -> tuple[dict[str, object], ...]:
    safety = {
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "risk_flag_downgrade_allowed": False,
        "risk_flag_deletion_allowed": False,
        "reason_code_deletion_allowed": False,
        "operator_review_bypass_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "buy_button_enabled": False,
        "sell_button_enabled": False,
        "order_button_enabled": False,
    }
    rows = (
        ("UI-APP-1", "ranked_watchlist_view_model", ("risk_flags", "reason_codes", "operator_review_required")),
        ("AI-CONTEXT-1", "explanation_report", ("risk_flags", "reason_codes", "confidence_level")),
        ("OPERATOR-REVIEW-APP-1", "operator_review_packet", ("review_status", "risk_acknowledgement", "no_execution_receipt")),
        ("CORRELATION-ID-TRACEABILITY-APP-1", "traceability_packet", ("Correlation_ID", "artifact_chain", "review_chain")),
    )
    result = []
    for source_app, artifact_type, required_fields in rows:
        item = dict(safety)
        item.update({
            "source_app": source_app,
            "artifact_type": artifact_type,
            "required_visible_fields": required_fields,
        })
        result.append(item)
    return tuple(result)


def load_required_visibility_fields() -> tuple[str, ...]:
    fields = []
    for row in load_ui_visibility_sources():
        fields.extend(str(item) for item in row["required_visible_fields"])
    return tuple(sorted(set(fields)))
