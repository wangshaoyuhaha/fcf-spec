from sidecars.control_center_global_scan_classification_guard_app_1.classification_packet import (
    RawScanHit,
    build_classification_packet,
    build_classification_record,
    packet_has_hidden_records,
    packet_requires_review,
)
from sidecars.control_center_global_scan_classification_guard_app_1.classification_rules import (
    ACTIONABLE_STRUCTURE_GAP,
    ACTIONABLE_UNSAFE_PERMISSION,
    EXPECTED_GOVERNANCE_TEXT,
    EXPECTED_SAFETY_BOUNDARY,
)


def test_d3_build_classification_record_preserves_source_metadata():
    hit = RawScanHit(
        source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        line_number=42,
        matched_text="governance policy approved",
        context="control center text",
        scan_family="safety_scan",
        correlation_id="CID-001",
    )

    record = build_classification_record(hit)

    assert record.source_path == "docs/FCF_PROJECT_CONTROL_CENTER.md"
    assert record.line_number == 42
    assert record.matched_text == "governance policy approved"
    assert record.context == "control center text"
    assert record.scan_family == "safety_scan"
    assert record.correlation_id == "CID-001"
    assert record.classification_label == EXPECTED_GOVERNANCE_TEXT
    assert record.review_required is False


def test_d3_packet_counts_expected_and_actionable_hits():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real trading and no broker connection",
            ),
            RawScanHit(
                source_path="docs/example.md",
                matched_text="broker connection allowed for real trading",
            ),
        ]
    )

    assert packet.total_hit_count == 2
    assert packet.expected_hit_count == 1
    assert packet.actionable_hit_count == 1
    assert packet.review_required_count == 1
    assert packet.count_by_label[EXPECTED_SAFETY_BOUNDARY] == 1
    assert packet.count_by_label[ACTIONABLE_UNSAFE_PERMISSION] == 1


def test_d3_packet_keeps_expected_hits_visible():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real trading",
            ),
            RawScanHit(
                source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
                matched_text="governance policy",
            ),
        ]
    )

    assert packet.total_hit_count == 2
    assert len(packet.records) == 2
    assert packet_has_hidden_records(packet) is False


def test_d3_packet_requires_review_when_actionable_exists():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/architecture.md",
                matched_text="missing provenance and unclear ownership",
            ),
        ]
    )

    assert packet.count_by_label[ACTIONABLE_STRUCTURE_GAP] == 1
    assert packet.review_required_count == 1
    assert packet_requires_review(packet) is True


def test_d3_packet_does_not_require_review_for_expected_only():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no API key and no wallet private key",
            ),
        ]
    )

    assert packet.review_required_count == 0
    assert packet_requires_review(packet) is False


def test_d3_packet_summary_preserves_safety_boundary_flags():
    packet = build_classification_packet([])

    assert packet.safety_boundary_preserved is True
    assert packet.operator_review_required is True
    assert packet.sidecar_only is True


def test_d3_packet_count_by_label_contains_all_labels():
    packet = build_classification_packet([])

    assert set(packet.count_by_label) == {
        "EXPECTED_GOVERNANCE_TEXT",
        "EXPECTED_TEST_ASSERTION",
        "EXPECTED_FINAL_STATE_HISTORY",
        "EXPECTED_SAFETY_BOUNDARY",
        "ACTIONABLE_STALE_STATE",
        "ACTIONABLE_UNSAFE_PERMISSION",
        "ACTIONABLE_STRUCTURE_GAP",
    }


def test_d3_packet_no_hidden_records_after_mixed_classification():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real execution",
            ),
            RawScanHit(
                source_path="docs/example.md",
                matched_text="exchange API enabled",
            ),
            RawScanHit(
                source_path="docs/architecture.md",
                matched_text="missing audit trail",
            ),
        ]
    )

    assert packet.total_hit_count == 3
    assert len(packet.records) == 3
    assert sum(packet.count_by_label.values()) == 3
    assert packet_has_hidden_records(packet) is False
