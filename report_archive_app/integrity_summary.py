"""Read-only archive integrity summary for REPORT-ARCHIVE-D4."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .item_index import (
    ArchiveItemIndex,
    ArchiveItemIndexRecord,
    validate_archive_item_index,
    validate_archive_item_index_record,
)


ARCHIVE_INTEGRITY_STAGE_ID = "REPORT-ARCHIVE-D4"
ARCHIVE_INTEGRITY_RECORD_TYPE = "archive_integrity_record"
ARCHIVE_INTEGRITY_SUMMARY_TYPE = "archive_integrity_summary"
INTEGRITY_STATUS_READY = "CHECKSUM_READY"
INTEGRITY_STATUS_SOURCE_MISSING = "SOURCE_MISSING"
INTEGRITY_STATUS_SOURCE_UNREADABLE = "SOURCE_UNREADABLE"


@dataclass(frozen=True)
class ArchiveIntegrityRecord:
    """Read-only checksum record for one archive item."""

    archive_item_id: str
    record_type: str
    source_app_id: str
    source_type: str
    source_path: str
    source_exists: bool
    file_size_bytes: int
    checksum_sha256: str
    integrity_status: str

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True

    checksum_generated: bool = False
    source_content_read_for_checksum: bool = False
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

    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ArchiveIntegritySummary:
    """Read-only integrity summary for an archive item index."""

    summary_id: str
    summary_type: str
    stage_id: str
    source_index_id: str
    records: tuple[ArchiveIntegrityRecord, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

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

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "summary_type": self.summary_type,
            "stage_id": self.stage_id,
            "source_index_id": self.source_index_id,
            "records": [record.to_dict() for record in self.records],
            "created_at_utc": self.created_at_utc,
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
        }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_archive_integrity_record(
    index_record: ArchiveItemIndexRecord,
) -> ArchiveIntegrityRecord:
    """Build a read-only checksum record from one archive item index record."""

    record_errors = validate_archive_item_index_record(index_record)
    if record_errors:
        raise ValueError("; ".join(record_errors))

    path = Path(index_record.source_path)
    if not path.exists() or not path.is_file():
        return ArchiveIntegrityRecord(
            archive_item_id=index_record.archive_item_id,
            record_type=ARCHIVE_INTEGRITY_RECORD_TYPE,
            source_app_id=index_record.source_app_id,
            source_type=index_record.source_type,
            source_path=index_record.source_path,
            source_exists=False,
            file_size_bytes=0,
            checksum_sha256="",
            integrity_status=INTEGRITY_STATUS_SOURCE_MISSING,
            checksum_generated=False,
            source_content_read_for_checksum=False,
        )

    try:
        checksum = _sha256_file(path)
        file_size = path.stat().st_size
    except OSError:
        return ArchiveIntegrityRecord(
            archive_item_id=index_record.archive_item_id,
            record_type=ARCHIVE_INTEGRITY_RECORD_TYPE,
            source_app_id=index_record.source_app_id,
            source_type=index_record.source_type,
            source_path=index_record.source_path,
            source_exists=True,
            file_size_bytes=index_record.file_size_bytes,
            checksum_sha256="",
            integrity_status=INTEGRITY_STATUS_SOURCE_UNREADABLE,
            checksum_generated=False,
            source_content_read_for_checksum=False,
        )

    return ArchiveIntegrityRecord(
        archive_item_id=index_record.archive_item_id,
        record_type=ARCHIVE_INTEGRITY_RECORD_TYPE,
        source_app_id=index_record.source_app_id,
        source_type=index_record.source_type,
        source_path=index_record.source_path,
        source_exists=True,
        file_size_bytes=file_size,
        checksum_sha256=checksum,
        integrity_status=INTEGRITY_STATUS_READY,
        checksum_generated=True,
        source_content_read_for_checksum=True,
    )


def validate_archive_integrity_record(record: ArchiveIntegrityRecord) -> list[str]:
    """Validate one archive integrity record."""

    errors: list[str] = []

    if not record.archive_item_id:
        errors.append("archive_item_id is required")
    if record.record_type != ARCHIVE_INTEGRITY_RECORD_TYPE:
        errors.append("record_type mismatch")
    if not record.source_path:
        errors.append("source_path is required")
    if record.file_size_bytes < 0:
        errors.append("file_size_bytes must be non-negative")
    if record.integrity_status not in {
        INTEGRITY_STATUS_READY,
        INTEGRITY_STATUS_SOURCE_MISSING,
        INTEGRITY_STATUS_SOURCE_UNREADABLE,
    }:
        errors.append("integrity_status is not allowed")

    if record.integrity_status == INTEGRITY_STATUS_READY:
        if len(record.checksum_sha256) != 64:
            errors.append("checksum_sha256 must be a sha256 hex digest")
        if record.checksum_generated is not True:
            errors.append("checksum_generated must be true for ready records")
        if record.source_content_read_for_checksum is not True:
            errors.append("source_content_read_for_checksum must be true for ready records")

    if record.integrity_status != INTEGRITY_STATUS_READY:
        if record.checksum_sha256 != "":
            errors.append("checksum_sha256 must be empty for non-ready records")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
    )
    for flag_name in required_true_flags:
        if getattr(record, flag_name) is not True:
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
    )
    for flag_name in forbidden_true_flags:
        if getattr(record, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def build_archive_integrity_summary(
    *,
    summary_id: str,
    item_index: ArchiveItemIndex,
) -> ArchiveIntegritySummary:
    """Build a read-only integrity summary from an archive item index."""

    index_errors = validate_archive_item_index(item_index)
    if index_errors:
        raise ValueError("; ".join(index_errors))

    records = tuple(build_archive_integrity_record(record) for record in item_index.records)

    return ArchiveIntegritySummary(
        summary_id=summary_id,
        summary_type=ARCHIVE_INTEGRITY_SUMMARY_TYPE,
        stage_id=ARCHIVE_INTEGRITY_STAGE_ID,
        source_index_id=item_index.index_id,
        records=records,
    )


def validate_archive_integrity_summary(summary: ArchiveIntegritySummary) -> list[str]:
    """Validate archive integrity summary and nested records."""

    errors: list[str] = []

    if not summary.summary_id:
        errors.append("summary_id is required")
    if summary.summary_type != ARCHIVE_INTEGRITY_SUMMARY_TYPE:
        errors.append("summary_type mismatch")
    if summary.stage_id != ARCHIVE_INTEGRITY_STAGE_ID:
        errors.append("stage_id mismatch")
    if not summary.source_index_id:
        errors.append("source_index_id is required")

    for record in summary.records:
        errors.extend(validate_archive_integrity_record(record))

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
    )
    for flag_name in required_true_flags:
        if getattr(summary, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "archive_packet_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(summary, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def summarize_archive_integrity_summary(summary: ArchiveIntegritySummary) -> dict[str, Any]:
    """Return a compact integrity summary."""

    status_counts: dict[str, int] = {}
    for record in summary.records:
        status_counts[record.integrity_status] = status_counts.get(record.integrity_status, 0) + 1

    return {
        "summary_id": summary.summary_id,
        "stage_id": summary.stage_id,
        "source_index_id": summary.source_index_id,
        "record_count": len(summary.records),
        "status_counts": status_counts,
        "all_ready": status_counts.get(INTEGRITY_STATUS_READY, 0) == len(summary.records),
        "paper_only": summary.paper_only,
        "local_only": summary.local_only,
        "read_only": summary.read_only,
        "sidecar_only": summary.sidecar_only,
        "source_content_mutation_allowed": summary.source_content_mutation_allowed,
        "trade_action_enabled": summary.trade_action_enabled,
        "real_execution_allowed": summary.real_execution_allowed,
    }
