from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "sidecars" / "correlation_id_traceability_app_1" / "D5_trace_review_packet.md"


def test_correlation_id_traceability_d5_trace_review_packet_exists():
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    required = [
        "D5 Trace Review Packet",
        "trace_packet_id",
        "packet_schema_version",
        "correlation_id",
        "chain_complete",
        "trace_integrity_state",
        "broken_chain_reasons",
        "data_reference",
        "validation_reference",
        "operator_review_reference",
        "ui_reference",
        "archive_reference",
        "dify_handoff_reference",
        "risk_flags_visible",
        "reason_codes_visible",
        "validation_failure_visible",
        "operator_review_required",
        "operator_review_bypass_allowed",
        "no_execution_receipt",
        "real_execution_allowed",
        "trade_action_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "trace_integrity_failed",
        "must not become",
        "Dify deployment request",
        "read-only, sidecar-only, non-executable",
    ]
    for item in required:
        assert item in text

