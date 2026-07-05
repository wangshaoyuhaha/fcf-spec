"""Archive item index records for REPORT-ARCHIVE-D3."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .source_discovery import (
    ArchiveSourceCandidate,
    validate_archive_source_candidate,
)


ARCHIVE_ITEM_INDEX_STAGE_ID = "REPORT-ARCHIVE-D3"
ARCHIVE_ITEM_RECORD_TYPE = "archive_item_index_record"
ARCHIVE_ITEM_INDEX_TYPE = "archive_item_index"
ARCHIVE_ITEM_INDEX_STATUS = "INDEXED_LOCAL_ARTIFACT"


@dataclass(frozen=True)
class ArchiveItemIndexRecord:
    """Read-only archive item index record.

    This record indexes metadata only. It does not read or mutate source content.
    """

    archive_item_id: str
    record_type: str
    source_app_id: str
    source_type: str
    source_path: str
    source_exists: bool
    file_extension: str
    file_size_bytes: int
    index_status: str = ARCHIVE_ITEM_INDEX_STATUS

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True

    source_content_read_for_index: bool = False
    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    checksum_generated: bool = False
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
class ArchiveItemIndex:
    """Read-only collection of archive item index records."""

    index_id: str
    index_type: str
    stage_id: str
    records: tuple[ArchiveItemIndexRecord, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    source_content_read_for_index: bool = False
    source_content_mutation_allowed: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "index_id": self.index_id,
            "index_type": self.index_type,
            "stage_id": self.stage_id,
            "records": [record.to_dict() for record in self.records],
            "created_at_utc": self.created_at_utc,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "sidecar_only": self.sidecar_only,
            "source_content_read_for_index": self.source_content_read_for_index,
            "source_content_mutation_allowed": self.source_content_mutation_allowed,
            "trade_action_enabled": self.trade_action_enabled,
            "real_execution_allowed": self.real_execution_allowed,
        }


def build_archive_item_index_record(
    candidate: ArchiveSourceCandidate,
    *,
    archive_item_id: str,
) -> ArchiveItemIndexRecord:
    """Build one archive item index record from a D2 source candidate."""

    candidate_errors = validate_archive_source_candidate(candidate)
    if candidate_errors:
        raise ValueError("; ".join(candidate_errors))

    return ArchiveItemIndexRecord(
        archive_item_id=archive_item_id,
        record_type=ARCHIVE_ITEM_RECORD_TYPE,
        source_app_id=candidate.source_app_id,
        source_type=candidate.source_type,
        source_path=candidate.source_path,
        source_exists=candidate.source_exists,
        file_extension=candidate.file_extension,
        file_size_bytes=candidate.file_size_bytes,
    )


def validate_archive_item_index_record(record: ArchiveItemIndexRecord) -> list[str]:
    """Validate one archive item index record."""

    errors: list[str] = []

    if not record.archive_item_id:
        errors.append("archive_item_id is required")
    if record.record_type != ARCHIVE_ITEM_RECORD_TYPE:
        errors.append("record_type mismatch")
    if not record.source_app_id:
        errors.append("source_app_id is required")
    if not record.source_type:
        errors.append("source_type is required")
    if not record.source_path:
        errors.append("source_path is required")
    if record.file_size_bytes < 0:
        errors.append("file_size_bytes must be non-negative")
    if record.index_status != ARCHIVE_ITEM_INDEX_STATUS:
        errors.append("index_status mismatch")

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
        "source_content_read_for_index",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "checksum_generated",
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


def build_archive_item_index(
    *,
    index_id: str,
    candidates: tuple[ArchiveSourceCandidate, ...] | list[ArchiveSourceCandidate],
) -> ArchiveItemIndex:
    """Build an archive item index from discovered source candidates."""

    records: list[ArchiveItemIndexRecord] = []
    for ordinal, candidate in enumerate(candidates, start=1):
        records.append(
            build_archive_item_index_record(
                candidate,
                archive_item_id=f"{index_id}-ITEM-{ordinal:04d}",
            )
        )

    return ArchiveItemIndex(
        index_id=index_id,
        index_type=ARCHIVE_ITEM_INDEX_TYPE,
        stage_id=ARCHIVE_ITEM_INDEX_STAGE_ID,
        records=tuple(records),
    )


def validate_archive_item_index(index: ArchiveItemIndex) -> list[str]:
    """Validate an archive item index and all nested records."""

    errors: list[str] = []

    if not index.index_id:
        errors.append("index_id is required")
    if index.index_type != ARCHIVE_ITEM_INDEX_TYPE:
        errors.append("index_type mismatch")
    if index.stage_id != ARCHIVE_ITEM_INDEX_STAGE_ID:
        errors.append("stage_id mismatch")

    for record in index.records:
        errors.extend(validate_archive_item_index_record(record))

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
    )
    for flag_name in required_true_flags:
        if getattr(index, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_read_for_index",
        "source_content_mutation_allowed",
        "trade_action_enabled",
        "real_execution_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(index, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def summarize_archive_item_index(index: ArchiveItemIndex) -> dict[str, Any]:
    """Return a compact summary of the archive item index."""

    by_app: dict[str, int] = {}
    by_type: dict[str, int] = {}

    for record in index.records:
        by_app[record.source_app_id] = by_app.get(record.source_app_id, 0) + 1
        by_type[record.source_type] = by_type.get(record.source_type, 0) + 1

    return {
        "index_id": index.index_id,
        "stage_id": index.stage_id,
        "record_count": len(index.records),
        "by_source_app_id": by_app,
        "by_source_type": by_type,
        "paper_only": index.paper_only,
        "local_only": index.local_only,
        "read_only": index.read_only,
        "sidecar_only": index.sidecar_only,
        "source_content_read_for_index": index.source_content_read_for_index,
        "source_content_mutation_allowed": index.source_content_mutation_allowed,
        "trade_action_enabled": index.trade_action_enabled,
        "real_execution_allowed": index.real_execution_allowed,
    }
