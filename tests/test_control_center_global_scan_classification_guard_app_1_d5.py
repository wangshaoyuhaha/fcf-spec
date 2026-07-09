from sidecars.control_center_global_scan_classification_guard_app_1.classification_packet import (
    RawScanHit,
)
from sidecars.control_center_global_scan_classification_guard_app_1.classification_rules import (
    ACTIONABLE_STRUCTURE_GAP,
    ACTIONABLE_UNSAFE_PERMISSION,
    EXPECTED_GOVERNANCE_TEXT,
    EXPECTED_SAFETY_BOUNDARY,
)
from sidecars.control_center_global_scan_classification_guard_app_1.review_gate import (
    ACTIONABLE_REVIEW_REQUIRED,
    EXPECTED_ONLY_VISIBLE,
    UNSAFE_PERMISSION_BLOCKED,
)
from sidecars.control_center_global_scan_classification_guard_app_1.review_packet import (
    PHASE_ID,
    build_review_packet,
    review_packet_blocks_unsafe_permission,
    review_packet_preserves_visibility,
    review_packet_queue_size_matches_actionable_count,
    review_packet_requires_operator_review,
)


def test_d5_expected_only_packet_preserves_visibility_without_queue():
    packet = build_review_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real trading and no broker connection",
            ),
            RawScanHit(
                source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
                matched_text="governance policy approved",
            ),
        ],
        packet_id="D5-PACKET-001",
    )

    assert packet.packet_id == "D5-PACKET-001"
    assert packet.phase_id == PHASE_ID
    assert packet.gate_status == EXPECTED_ONLY_VISIBLE
    assert packet.total_hit_count == 2
    assert packet.expected_hit_count == 2
    assert packet.actionable_hit_count == 0
    assert packet.review_required_count == 0
    assert len(packet.remediation_queue) == 0
    assert review_packet_preserves_visibility(packet) is True


def test_d5_actionable_structure_gap_enters_review_queue():
    packet = build_review_packet(
        [
            RawScanHit(
                source_path="docs/architecture.md",
                matched_text="missing provenance and unclear ownership",
                line_number=88,
                correlation_id="CID-D5-STRUCTURE",
            ),
        ],
        packet_id="D5-PACKET-002",
    )

    assert packet.gate_status == ACTIONABLE_REVIEW_REQUIRED
    assert packet.actionable_hit_count == 1
    assert len(packet.remediation_queue) == 1
    item = packet.remediation_queue[0]
    assert item.classification_label == ACTIONABLE_STRUCTURE_GAP
    assert item.review_required is True
    assert item.blocked_until_review is False
    assert item.line_number == 88
    assert item.correlation_id == "CID-D5-STRUCTURE"
    assert review_packet_requires_operator_review(packet) is True


def test_d5_unsafe_permission_is_blocked_until_review():
    packet = build_review_packet(
        [
            RawScanHit(
                source_path="docs/example.md",
                matched_text="broker connection allowed for real trading",
                line_number=12,
                correlation_id="CID-D5-UNSAFE",
            ),
        ],
        packet_id="D5-PACKET-003",
    )

    assert packet.gate_status == UNSAFE_PERMISSION_BLOCKED
    assert packet.blocked_until_review is True
    assert packet.operator_review_required is True
    assert len(packet.remediation_queue) == 1
    item = packet.remediation_queue[0]
    assert item.classification_label == ACTIONABLE_UNSAFE_PERMISSION
    assert item.blocked_until_review is True
    assert item.review_required is True
    assert item.correlation_id == "CID-D5-UNSAFE"
    assert review_packet_blocks_unsafe_permission(packet) is True


def test_d5_expected_labels_do_not_enter_remediation_queue():
    packet = build_review_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no API key and no wallet private key",
            ),
            RawScanHit(
                source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
                matched_text="governance policy approved",
            ),
        ],
        packet_id="D5-PACKET-004",
    )

    labels = {item.classification_label for item in packet.remediation_queue}
    assert EXPECTED_SAFETY_BOUNDARY not in labels
    assert EXPECTED_GOVERNANCE_TEXT not in labels
    assert len(packet.remediation_queue) == 0


def test_d5_mixed_packet_preserves_all_records_and_routes_actionable_only():
    packet = build_review_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real execution",
            ),
            RawScanHit(
                source_path="docs/architecture.md",
                matched_text="missing audit trail",
            ),
            RawScanHit(
                source_path="docs/example.md",
                matched_text="buy button enabled",
            ),
        ],
        packet_id="D5-PACKET-005",
    )

    assert packet.total_hit_count == 3
    assert packet.records_visible_count == 3
    assert packet.expected_hit_count == 1
    assert packet.actionable_hit_count == 2
    assert len(packet.remediation_queue) == 2
    assert packet.gate_status == UNSAFE_PERMISSION_BLOCKED
    assert review_packet_preserves_visibility(packet) is True
    assert review_packet_queue_size_matches_actionable_count(packet) is True


def test_d5_packet_preserves_safety_boundary_flags():
    packet = build_review_packet([], packet_id="D5-PACKET-006")

    assert packet.safety_boundary_preserved is True
    assert packet.sidecar_only is True


def test_d5_empty_packet_is_visible_expected_only():
    packet = build_review_packet([], packet_id="D5-PACKET-007")

    assert packet.gate_status == EXPECTED_ONLY_VISIBLE
    assert packet.total_hit_count == 0
    assert packet.records_visible_count == 0
    assert packet.operator_review_required is False
    assert packet.blocked_until_review is False
    assert review_packet_preserves_visibility(packet) is True


def test_d5_queue_size_matches_actionable_count_for_multiple_actionable_hits():
    packet = build_review_packet(
        [
            RawScanHit(
                source_path="docs/architecture.md",
                matched_text="missing provenance",
            ),
            RawScanHit(
                source_path="FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
                matched_text="obsolete validation count conflicts with current control center",
            ),
            RawScanHit(
                source_path="docs/example.md",
                matched_text="exchange API enabled",
            ),
        ],
        packet_id="D5-PACKET-008",
    )

    assert packet.actionable_hit_count == 3
    assert len(packet.remediation_queue) == 3
    assert review_packet_queue_size_matches_actionable_count(packet) is True
