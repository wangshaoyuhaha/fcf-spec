from app.ui_risk_flag_visibility.source_loader import (
    load_required_visibility_fields,
    load_ui_visibility_sources,
)


def test_d2_source_loader_visibility_sources():
    rows = load_ui_visibility_sources()
    sources = {row["source_app"] for row in rows}
    fields = set(load_required_visibility_fields())
    assert len(rows) >= 4
    assert "UI-APP-1" in sources
    assert "AI-CONTEXT-1" in sources
    assert "OPERATOR-REVIEW-APP-1" in sources
    assert "CORRELATION-ID-TRACEABILITY-APP-1" in sources
    assert "risk_flags" in fields
    assert "reason_codes" in fields
    assert "operator_review_required" in fields
    assert "Correlation_ID" in fields
    for row in rows:
        assert row["paper_only"] is True
        assert row["local_only"] is True
        assert row["read_only"] is True
        assert row["sidecar_only"] is True
        assert row["operator_review_required"] is True
        assert row["risk_flag_downgrade_allowed"] is False
        assert row["risk_flag_deletion_allowed"] is False
        assert row["reason_code_deletion_allowed"] is False
        assert row["operator_review_bypass_allowed"] is False
        assert row["trade_action_allowed"] is False
        assert row["real_execution_allowed"] is False
        assert row["buy_button_enabled"] is False
        assert row["sell_button_enabled"] is False
        assert row["order_button_enabled"] is False
