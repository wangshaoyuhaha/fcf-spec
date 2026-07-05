"""Archive manifest and paper archive packet for REPORT-ARCHIVE-D5."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .integrity_summary import (
    ArchiveIntegritySummary,
    INTEGRITY_STATUS_READY,
    summarize_archive_integrity_summary,
    validate_archive_integrity_summary,
)


ARCHIVE_MANIFEST_STAGE_ID = "REPORT-ARCHIVE-D5"
ARCHIVE_MANIFEST_TYPE = "archive_manifest"
PAPER_ARCHIVE_PACKET_TYPE = "paper_archive_packet"


@dataclass(frozen=True)
class ArchiveManifest:
    """Paper-only archive manifest built from read-only integrity summary."""

    manifest_id: str
    manifest_type: str
    stage_id: str
    source_integrity_summary_id: str
    source_index_id: str
    archive_item_count: int
    checksum_ready_count: int
    checksum_missing_count: int
    checksum_unreadable_count: int
    integrity_summary: dict[str, Any]

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True

    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    archive_packet_is_trade_instruction: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False
    buy_button_enabled: bool = False
    sell_button_enabled: bool = False
    order_button_enabled: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    credential_storage_allowed: bool = False
    wallet_private_key_access_allowed: bool = False
    real_account_access_allowed: bool = False
    real_position_access_allowed: bool = False
    core_mutation_allowed: bool = False
    p48_core_expansion_allowed: bool = False
    tag_created: bool = False
    release_created: bool = False
    deployed: bool = False

    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PaperArchivePacket:
    """Local paper-only archive packet."""

    packet_id: str
    packet_type: str
    stage_id: str
    archive_manifest: ArchiveManifest
    integrity_summary: dict[str, Any]

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True

    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    archive_packet_is_trade_instruction: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False
    tag_created: bool = False
    release_created: bool = False
    deployed: bool = False

    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "packet_type": self.packet_type,
            "stage_id": self.stage_id,
            "archive_manifest": self.archive_manifest.to_dict(),
            "integrity_summary": self.integrity_summary,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "sidecar_only": self.sidecar_only,
            "source_content_mutation_allowed": self.source_content_mutation_allowed,
            "source_deletion_allowed": self.source_deletion_allowed,
            "source_overwrite_allowed": self.source_overwrite_allowed,
            "archive_packet_is_trade_instruction": self.archive_packet_is_trade_instruction,
            "trade_action_enabled": self.trade_action_enabled,
            "real_execution_allowed": self.real_execution_allowed,
            "tag_created": self.tag_created,
            "release_created": self.release_created,
            "deployed": self.deployed,
            "created_at_utc": self.created_at_utc,
        }


def build_archive_manifest(
    *,
    manifest_id: str,
    integrity_summary: ArchiveIntegritySummary,
) -> ArchiveManifest:
    """Build a local paper-only archive manifest."""

    errors = validate_archive_integrity_summary(integrity_summary)
    if errors:
        raise ValueError("; ".join(errors))

    compact = summarize_archive_integrity_summary(integrity_summary)
    status_counts = compact["status_counts"]

    return ArchiveManifest(
        manifest_id=manifest_id,
        manifest_type=ARCHIVE_MANIFEST_TYPE,
        stage_id=ARCHIVE_MANIFEST_STAGE_ID,
        source_integrity_summary_id=integrity_summary.summary_id,
        source_index_id=integrity_summary.source_index_id,
        archive_item_count=len(integrity_summary.records),
        checksum_ready_count=status_counts.get(INTEGRITY_STATUS_READY, 0),
        checksum_missing_count=status_counts.get("SOURCE_MISSING", 0),
        checksum_unreadable_count=status_counts.get("SOURCE_UNREADABLE", 0),
        integrity_summary=compact,
    )


def validate_archive_manifest(manifest: ArchiveManifest) -> list[str]:
    """Validate archive manifest safety and schema constraints."""

    errors: list[str] = []

    if not manifest.manifest_id:
        errors.append("manifest_id is required")
    if manifest.manifest_type != ARCHIVE_MANIFEST_TYPE:
        errors.append("manifest_type mismatch")
    if manifest.stage_id != ARCHIVE_MANIFEST_STAGE_ID:
        errors.append("stage_id mismatch")
    if not manifest.source_integrity_summary_id:
        errors.append("source_integrity_summary_id is required")
    if not manifest.source_index_id:
        errors.append("source_index_id is required")
    if manifest.archive_item_count < 0:
        errors.append("archive_item_count must be non-negative")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
    )
    for flag_name in required_true_flags:
        if getattr(manifest, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "archive_packet_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "credential_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
        "tag_created",
        "release_created",
        "deployed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(manifest, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def build_paper_archive_packet(
    *,
    packet_id: str,
    archive_manifest: ArchiveManifest,
    integrity_summary: ArchiveIntegritySummary,
) -> PaperArchivePacket:
    """Build a local paper-only archive packet."""

    manifest_errors = validate_archive_manifest(archive_manifest)
    if manifest_errors:
        raise ValueError("; ".join(manifest_errors))

    return PaperArchivePacket(
        packet_id=packet_id,
        packet_type=PAPER_ARCHIVE_PACKET_TYPE,
        stage_id=ARCHIVE_MANIFEST_STAGE_ID,
        archive_manifest=archive_manifest,
        integrity_summary=integrity_summary.to_dict(),
    )


def validate_paper_archive_packet(packet: PaperArchivePacket) -> list[str]:
    """Validate paper archive packet safety and schema constraints."""

    errors: list[str] = []

    if not packet.packet_id:
        errors.append("packet_id is required")
    if packet.packet_type != PAPER_ARCHIVE_PACKET_TYPE:
        errors.append("packet_type mismatch")
    if packet.stage_id != ARCHIVE_MANIFEST_STAGE_ID:
        errors.append("stage_id mismatch")

    errors.extend(validate_archive_manifest(packet.archive_manifest))

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
    )
    for flag_name in required_true_flags:
        if getattr(packet, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "archive_packet_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
        "tag_created",
        "release_created",
        "deployed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(packet, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def write_paper_archive_packet(packet: PaperArchivePacket, output_path: str | Path) -> Path:
    """Write local paper archive packet JSON."""

    errors = validate_paper_archive_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(packet.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path
