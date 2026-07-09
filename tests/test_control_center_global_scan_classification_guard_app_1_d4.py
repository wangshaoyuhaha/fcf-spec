from sidecars.control_center_global_scan_classification_guard_app_1.classification_packet import (
    RawScanHit,
    build_classification_packet,
)
from sidecars.control_center_global_scan_classification_guard_app_1.review_gate import (
    ACTIONABLE_REVIEW_REQUIRED,
    EXPECTED_ONLY_VISIBLE,
    UNSAFE_PERMISSION_BLOCKED,
    evaluate_review_gate,
    gate_blocks_unsafe_permission,
    gate_is_expected_only,
    gate_preserves_visibility,
    gate_requires_review_for_actionable,
)


def test_d4_expected_only_packet_remains_visible():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no real trading and no broker connection",
            ),
            RawScanHit(
                source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
                matched_text="governance policy approved",
            ),
        ]
    )

    result = evaluate_review_gate(packet)

    assert result.gate_status == EXPECTED_ONLY_VISIBLE
    assert result.total_hit_count == 2
    assert result.records_visible_count == 2
    assert result.operator_review_required is False
    assert result.blocked_until_review is False
    assert gate_is_expected_only(result) is True
    assert gate_preserves_visibility(packet, result) is True


def test_d4_actionable_structure_gap_requires_review():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/architecture.md",
                matched_text="missing provenance and unclear ownership",
            ),
        ]
    )

    result = evaluate_review_gate(packet)

    assert result.gate_status == ACTIONABLE_REVIEW_REQUIRED
    assert result.actionable_hit_count == 1
    assert result.structure_gap_count == 1
    assert result.operator_review_required is True
    assert result.blocked_until_review is False
    assert gate_requires_review_for_actionable(result) is True
    assert gate_preserves_visibility(packet, result) is True


def test_d4_actionable_stale_state_requires_review():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
                matched_text="obsolete validation count conflicts with current control center",
            ),
        ]
    )

    result = evaluate_review_gate(packet)

    assert result.gate_status == ACTIONABLE_REVIEW_REQUIRED
    assert result.stale_state_count == 1
    assert result.operator_review_required is True
    assert result.blocked_until_review is False


def test_d4_unsafe_permission_is_blocked_until_review():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/example.md",
                matched_text="broker connection allowed for real trading",
            ),
        ]
    )

    result = evaluate_review_gate(packet)

    assert result.gate_status == UNSAFE_PERMISSION_BLOCKED
    assert result.unsafe_permission_count == 1
    assert result.operator_review_required is True
    assert result.blocked_until_review is True
    assert gate_blocks_unsafe_permission(result) is True


def test_d4_expected_label_does_not_downgrade_unsafe_permission():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
                matched_text="governance policy approved",
            ),
            RawScanHit(
                source_path="docs/FCF_PROJECT_CONTROL_CENTER.md",
                matched_text="exchange API enabled for real trading",
                context="governance docs",
            ),
        ]
    )

    result = evaluate_review_gate(packet)

    assert result.gate_status == UNSAFE_PERMISSION_BLOCKED
    assert result.expected_hit_count == 1
    assert result.actionable_hit_count == 1
    assert result.unsafe_permission_count == 1
    assert result.blocked_until_review is True


def test_d4_empty_packet_is_expected_only_visible():
    packet = build_classification_packet([])
    result = evaluate_review_gate(packet)

    assert result.gate_status == EXPECTED_ONLY_VISIBLE
    assert result.total_hit_count == 0
    assert result.records_visible_count == 0
    assert result.operator_review_required is False
    assert gate_preserves_visibility(packet, result) is True


def test_d4_review_gate_preserves_boundary_flags():
    packet = build_classification_packet(
        [
            RawScanHit(
                source_path="docs/HANDOFF_PROMPT.md",
                matched_text="no API key and no wallet private key",
            ),
        ]
    )

    result = evaluate_review_gate(packet)

    assert result.safety_boundary_preserved is True
    assert result.sidecar_only is True


def test_d4_review_gate_never_hides_mixed_records():
    packet = build_classification_packet(
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
        ]
    )

    result = evaluate_review_gate(packet)

    assert packet.total_hit_count == 3
    assert result.records_visible_count == 3
    assert result.gate_status == UNSAFE_PERMISSION_BLOCKED
    assert gate_preserves_visibility(packet, result) is True
