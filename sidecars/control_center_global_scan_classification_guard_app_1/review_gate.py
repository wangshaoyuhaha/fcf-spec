"""Review gate for global scan classification packets.

This module is paper-only, local-only, read-only, and sidecar-only.
It does not mutate scan records, core files, source files, runtime files, or handoff files.
"""

from __future__ import annotations

from dataclasses import dataclass

from sidecars.control_center_global_scan_classification_guard_app_1.classification_packet import (
    ClassificationPacket,
)
from sidecars.control_center_global_scan_classification_guard_app_1.classification_rules import (
    ACTIONABLE_STALE_STATE,
    ACTIONABLE_STRUCTURE_GAP,
    ACTIONABLE_UNSAFE_PERMISSION,
)


EXPECTED_ONLY_VISIBLE = "EXPECTED_ONLY_VISIBLE"
ACTIONABLE_REVIEW_REQUIRED = "ACTIONABLE_REVIEW_REQUIRED"
UNSAFE_PERMISSION_BLOCKED = "UNSAFE_PERMISSION_BLOCKED"

GATE_STATUSES = (
    EXPECTED_ONLY_VISIBLE,
    ACTIONABLE_REVIEW_REQUIRED,
    UNSAFE_PERMISSION_BLOCKED,
)


@dataclass(frozen=True)
class ReviewGateResult:
    gate_status: str
    total_hit_count: int
    expected_hit_count: int
    actionable_hit_count: int
    review_required_count: int
    unsafe_permission_count: int
    stale_state_count: int
    structure_gap_count: int
    records_visible_count: int
    operator_review_required: bool
    blocked_until_review: bool
    safety_boundary_preserved: bool
    sidecar_only: bool


def evaluate_review_gate(packet: ClassificationPacket) -> ReviewGateResult:
    unsafe_permission_count = packet.count_by_label[ACTIONABLE_UNSAFE_PERMISSION]
    stale_state_count = packet.count_by_label[ACTIONABLE_STALE_STATE]
    structure_gap_count = packet.count_by_label[ACTIONABLE_STRUCTURE_GAP]

    if unsafe_permission_count > 0:
        gate_status = UNSAFE_PERMISSION_BLOCKED
    elif packet.actionable_hit_count > 0:
        gate_status = ACTIONABLE_REVIEW_REQUIRED
    else:
        gate_status = EXPECTED_ONLY_VISIBLE

    return ReviewGateResult(
        gate_status=gate_status,
        total_hit_count=packet.total_hit_count,
        expected_hit_count=packet.expected_hit_count,
        actionable_hit_count=packet.actionable_hit_count,
        review_required_count=packet.review_required_count,
        unsafe_permission_count=unsafe_permission_count,
        stale_state_count=stale_state_count,
        structure_gap_count=structure_gap_count,
        records_visible_count=len(packet.records),
        operator_review_required=packet.actionable_hit_count > 0,
        blocked_until_review=unsafe_permission_count > 0,
        safety_boundary_preserved=packet.safety_boundary_preserved,
        sidecar_only=packet.sidecar_only,
    )


def gate_preserves_visibility(packet: ClassificationPacket, result: ReviewGateResult) -> bool:
    return (
        packet.total_hit_count == len(packet.records)
        and result.records_visible_count == packet.total_hit_count
    )


def gate_blocks_unsafe_permission(result: ReviewGateResult) -> bool:
    return (
        result.unsafe_permission_count > 0
        and result.gate_status == UNSAFE_PERMISSION_BLOCKED
        and result.blocked_until_review is True
        and result.operator_review_required is True
    )


def gate_requires_review_for_actionable(result: ReviewGateResult) -> bool:
    if result.actionable_hit_count <= 0:
        return False
    return result.operator_review_required is True


def gate_is_expected_only(result: ReviewGateResult) -> bool:
    return (
        result.gate_status == EXPECTED_ONLY_VISIBLE
        and result.actionable_hit_count == 0
        and result.review_required_count == 0
        and result.operator_review_required is False
        and result.blocked_until_review is False
    )
