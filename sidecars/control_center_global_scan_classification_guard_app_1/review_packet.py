"""Operator review packet for global scan classification.

This module is paper-only, local-only, read-only, and sidecar-only.
It creates review summaries only and does not mutate source files, runtime files,
handoff files, or frozen core files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sidecars.control_center_global_scan_classification_guard_app_1.classification_packet import (
    ClassificationPacket,
    ClassificationRecord,
    RawScanHit,
    build_classification_packet,
)
from sidecars.control_center_global_scan_classification_guard_app_1.classification_rules import (
    ACTIONABLE_LABELS,
    ACTIONABLE_UNSAFE_PERMISSION,
)
from sidecars.control_center_global_scan_classification_guard_app_1.review_gate import (
    UNSAFE_PERMISSION_BLOCKED,
    ReviewGateResult,
    evaluate_review_gate,
)


PHASE_ID = "CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1"


@dataclass(frozen=True)
class ReviewQueueItem:
    source_path: str
    line_number: int | None
    matched_text: str
    classification_label: str
    reason_code: str
    review_required: bool
    blocked_until_review: bool
    correlation_id: str | None


@dataclass(frozen=True)
class ClassificationReviewPacket:
    packet_id: str
    phase_id: str
    gate_status: str
    total_hit_count: int
    expected_hit_count: int
    actionable_hit_count: int
    review_required_count: int
    records_visible_count: int
    remediation_queue: tuple[ReviewQueueItem, ...]
    blocked_until_review: bool
    operator_review_required: bool
    safety_boundary_preserved: bool
    sidecar_only: bool


def _queue_item_from_record(record: ClassificationRecord) -> ReviewQueueItem:
    return ReviewQueueItem(
        source_path=record.source_path,
        line_number=record.line_number,
        matched_text=record.matched_text,
        classification_label=record.classification_label,
        reason_code=record.reason_code,
        review_required=record.review_required,
        blocked_until_review=record.classification_label == ACTIONABLE_UNSAFE_PERMISSION,
        correlation_id=record.correlation_id,
    )


def build_review_packet_from_classification_packet(
    packet: ClassificationPacket,
    *,
    packet_id: str,
) -> ClassificationReviewPacket:
    gate = evaluate_review_gate(packet)
    remediation_queue = tuple(
        _queue_item_from_record(record)
        for record in packet.records
        if record.classification_label in ACTIONABLE_LABELS
    )

    return ClassificationReviewPacket(
        packet_id=packet_id,
        phase_id=PHASE_ID,
        gate_status=gate.gate_status,
        total_hit_count=packet.total_hit_count,
        expected_hit_count=packet.expected_hit_count,
        actionable_hit_count=packet.actionable_hit_count,
        review_required_count=packet.review_required_count,
        records_visible_count=len(packet.records),
        remediation_queue=remediation_queue,
        blocked_until_review=gate.blocked_until_review,
        operator_review_required=gate.operator_review_required,
        safety_boundary_preserved=gate.safety_boundary_preserved,
        sidecar_only=gate.sidecar_only,
    )


def build_review_packet(
    hits: Iterable[RawScanHit],
    *,
    packet_id: str,
) -> ClassificationReviewPacket:
    packet = build_classification_packet(hits)
    return build_review_packet_from_classification_packet(
        packet,
        packet_id=packet_id,
    )


def review_packet_preserves_visibility(packet: ClassificationReviewPacket) -> bool:
    return packet.records_visible_count == packet.total_hit_count


def review_packet_requires_operator_review(packet: ClassificationReviewPacket) -> bool:
    return packet.operator_review_required is True or packet.review_required_count > 0


def review_packet_blocks_unsafe_permission(packet: ClassificationReviewPacket) -> bool:
    has_blocked_item = any(
        item.classification_label == ACTIONABLE_UNSAFE_PERMISSION
        and item.blocked_until_review is True
        for item in packet.remediation_queue
    )
    return (
        packet.gate_status == UNSAFE_PERMISSION_BLOCKED
        and packet.blocked_until_review is True
        and has_blocked_item
    )


def review_packet_queue_size_matches_actionable_count(packet: ClassificationReviewPacket) -> bool:
    return len(packet.remediation_queue) == packet.actionable_hit_count
