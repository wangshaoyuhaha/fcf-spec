import pytest

from sidecars.archive_correlation_rollup_app_1 import (
    CorrelationRollupPacket,
    CorrelationRollupRecord,
    build_rollup_packet,
    packet_has_blocked_trace,
    packet_has_partial_trace,
    validate_rollup_packet,
)


def _record(correlation_id, trace_state="trace_ready"):
    return CorrelationRollupRecord(
        correlation_id=correlation_id,
        artifact_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        artifact_type="control_center",
        source_app="ARCHIVE-CORRELATION-ROLLUP-APP-1",
        source_phase="D5",
        validation_state="passed",
        safety_state="read_only",
        operator_review_state="review_required",
        rollup_scope="control_center",
        trace_state=trace_state,
    )


def test_d5_builds_rollup_packet():
    packet = build_rollup_packet(
        packet_id="PACKET-ARCHIVE-ROLLUP-D5",
        records=[
            _record("CORR-D5-A"),
            _record("CORR-D5-B"),
        ],
        created_at_utc="2026-07-08T00:00:00Z",
    )

    assert packet.packet_id == "PACKET-ARCHIVE-ROLLUP-D5"
    assert packet.summary_count == 2
    assert packet.record_count == 2
    assert packet.operator_review_required is True
    assert packet.release_allowed is False
    assert packet.deploy_allowed is False
    assert packet.safety_state == "paper_only_local_read_only_sidecar_only"


def test_d5_validates_packet():
    packet = build_rollup_packet(
        packet_id="PACKET-ARCHIVE-ROLLUP-D5",
        records=[_record("CORR-D5-A")],
        created_at_utc="2026-07-08T00:00:00Z",
    )

    valid, issues = validate_rollup_packet(packet)

    assert valid is True
    assert issues == ()


def test_d5_rejects_empty_packet_records():
    with pytest.raises(ValueError, match="empty_rollup_packet_records"):
        build_rollup_packet(
            packet_id="PACKET-EMPTY",
            records=[],
            created_at_utc="2026-07-08T00:00:00Z",
        )


def test_d5_detects_blocked_trace_in_packet():
    packet = build_rollup_packet(
        packet_id="PACKET-BLOCKED",
        records=[_record("CORR-D5-BLOCKED", "trace_blocked")],
        created_at_utc="2026-07-08T00:00:00Z",
    )

    assert packet_has_blocked_trace(packet) is True
    assert packet_has_partial_trace(packet) is False


def test_d5_detects_partial_trace_in_packet():
    packet = build_rollup_packet(
        packet_id="PACKET-PARTIAL",
        records=[_record("CORR-D5-PARTIAL", "trace_partial")],
        created_at_utc="2026-07-08T00:00:00Z",
    )

    assert packet_has_partial_trace(packet) is True
    assert packet_has_blocked_trace(packet) is False


def test_d5_rejects_release_enabled_packet():
    valid_packet = build_rollup_packet(
        packet_id="PACKET-ARCHIVE-ROLLUP-D5",
        records=[_record("CORR-D5-A")],
        created_at_utc="2026-07-08T00:00:00Z",
    )
    invalid_packet = CorrelationRollupPacket(
        packet_id=valid_packet.packet_id,
        created_at_utc=valid_packet.created_at_utc,
        source_app=valid_packet.source_app,
        summary_count=valid_packet.summary_count,
        record_count=valid_packet.record_count,
        summaries=valid_packet.summaries,
        safety_state=valid_packet.safety_state,
        operator_review_required=valid_packet.operator_review_required,
        no_execution_statement=valid_packet.no_execution_statement,
        release_allowed=True,
        deploy_allowed=valid_packet.deploy_allowed,
    )

    valid, issues = validate_rollup_packet(invalid_packet)

    assert valid is False
    assert "release_allowed_must_be_false" in issues
