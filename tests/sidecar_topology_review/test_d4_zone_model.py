from app.sidecar_topology_review.zone_model import build_zone_summary, validate_zone_contract


def test_d4_zone_summary_and_contract():
    summary = build_zone_summary()
    result = validate_zone_contract()
    assert set(summary) == {
        "data_ingestion_and_quarantine",
        "context_and_interpretation",
        "governance_and_review_gate",
        "presentation_and_immutable_archive",
    }
    assert "DATA-APP-1" in summary["data_ingestion_and_quarantine"]
    assert "AI-CONTEXT-1" in summary["context_and_interpretation"]
    assert "OPERATOR-REVIEW-APP-1" in summary["governance_and_review_gate"]
    assert "REPORT-ARCHIVE-APP-1" in summary["presentation_and_immutable_archive"]
    assert result["zone_contract_required"] is True
    assert result["isolation_zone_valid"] is True
    assert result["risk_flag_downgrade_allowed"] is False
    assert result["reason_code_deletion_allowed"] is False
    assert result["operator_review_bypass_allowed"] is False
