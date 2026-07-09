"""Classification packet builder for global scan classification results.

This module is paper-only, local-only, read-only, and sidecar-only.
It builds visible classification packets and does not mutate source files or core files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sidecars.control_center_global_scan_classification_guard_app_1.classification_rules import (
    ACTIONABLE_LABELS,
    EXPECTED_LABELS,
    LABELS,
    classify_scan_hit,
)


@dataclass(frozen=True)
class RawScanHit:
    source_path: str
    matched_text: str
    line_number: int | None = None
    context: str = ""
    scan_family: str = "global_scan"
    correlation_id: str | None = None


@dataclass(frozen=True)
class ClassificationRecord:
    source_path: str
    matched_text: str
    line_number: int | None
    context: str
    scan_family: str
    classification_label: str
    reason_code: str
    review_required: bool
    correlation_id: str | None


@dataclass(frozen=True)
class ClassificationPacket:
    records: tuple[ClassificationRecord, ...]
    total_hit_count: int
    count_by_label: dict[str, int]
    actionable_hit_count: int
    expected_hit_count: int
    review_required_count: int
    safety_boundary_preserved: bool
    operator_review_required: bool
    sidecar_only: bool


def build_classification_record(hit: RawScanHit) -> ClassificationRecord:
    classified = classify_scan_hit(
        source_path=hit.source_path,
        matched_text=hit.matched_text,
        context=hit.context,
        correlation_id=hit.correlation_id,
    )
    return ClassificationRecord(
        source_path=hit.source_path,
        matched_text=hit.matched_text,
        line_number=hit.line_number,
        context=hit.context,
        scan_family=hit.scan_family,
        classification_label=classified.classification_label,
        reason_code=classified.reason_code,
        review_required=classified.review_required,
        correlation_id=classified.correlation_id,
    )


def build_classification_packet(hits: Iterable[RawScanHit]) -> ClassificationPacket:
    records = tuple(build_classification_record(hit) for hit in hits)

    count_by_label = {label: 0 for label in LABELS}
    for record in records:
        count_by_label[record.classification_label] += 1

    actionable_hit_count = sum(count_by_label[label] for label in ACTIONABLE_LABELS)
    expected_hit_count = sum(count_by_label[label] for label in EXPECTED_LABELS)
    review_required_count = sum(1 for record in records if record.review_required)

    return ClassificationPacket(
        records=records,
        total_hit_count=len(records),
        count_by_label=count_by_label,
        actionable_hit_count=actionable_hit_count,
        expected_hit_count=expected_hit_count,
        review_required_count=review_required_count,
        safety_boundary_preserved=True,
        operator_review_required=True,
        sidecar_only=True,
    )


def packet_has_hidden_records(packet: ClassificationPacket) -> bool:
    counted = sum(packet.count_by_label.values())
    return counted != packet.total_hit_count or counted != len(packet.records)


def packet_requires_review(packet: ClassificationPacket) -> bool:
    return packet.review_required_count > 0
