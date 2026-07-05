"""Paper-only repair queue and local ops packet for DATA-QUALITY-OPS-D5."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .issue_list import (
    DataQualityIssue,
    DataQualityIssueList,
    summarize_data_quality_issue_list,
    validate_data_quality_issue,
    validate_data_quality_issue_list,
)


DATA_REPAIR_QUEUE_STAGE_ID = "DATA-QUALITY-OPS-D5"
DATA_REPAIR_QUEUE_ITEM_TYPE = "data_repair_queue_item"
DATA_REPAIR_QUEUE_TYPE = "data_repair_queue"
DATA_QUALITY_OPS_PACKET_TYPE = "data_quality_ops_local_packet"

REPAIR_STATUS_PAPER_REVIEW_REQUIRED = "PAPER_REPAIR_REVIEW_REQUIRED"
REPAIR_STATUS_NO_AUTO_REPAIR = "NO_AUTO_REPAIR"

REPAIR_PRIORITY_HIGH = "HIGH"
REPAIR_PRIORITY_MEDIUM = "MEDIUM"


@dataclass(frozen=True)
class DataRepairQueueItem:
    """Paper-only repair queue item.

    This is a documentation item only and cannot mutate data or execute repair actions.
    """

    repair_item_id: str
    record_type: str
    stage_id: str
    source_issue_id: str
    source_app_id: str
    source_type: str
    source_path: str
    issue_code: str
    issue_message: str
    severity: str
    repair_status: str
    repair_priority: str
    suggested_paper_action: str
    evidence: dict[str, Any]

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True

    repair_queue_is_execution_instruction: bool = False
    suggested_action_is_execution_instruction: bool = False
    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False

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
class DataRepairQueue:
    """Paper-only repair queue built from D4 issue list."""

    queue_id: str
    queue_type: str
    stage_id: str
    source_issue_list_id: str
    repair_items: tuple[DataRepairQueueItem, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True

    repair_queue_is_execution_instruction: bool = False
    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "queue_id": self.queue_id,
            "queue_type": self.queue_type,
            "stage_id": self.stage_id,
            "source_issue_list_id": self.source_issue_list_id,
            "repair_items": [item.to_dict() for item in self.repair_items],
            "created_at_utc": self.created_at_utc,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "sidecar_only": self.sidecar_only,
            "operator_review_required": self.operator_review_required,
            "repair_queue_is_execution_instruction": self.repair_queue_is_execution_instruction,
            "source_content_mutation_allowed": self.source_content_mutation_allowed,
            "source_deletion_allowed": self.source_deletion_allowed,
            "source_overwrite_allowed": self.source_overwrite_allowed,
            "trade_action_enabled": self.trade_action_enabled,
            "real_execution_allowed": self.real_execution_allowed,
        }


@dataclass(frozen=True)
class DataQualityOpsPacket:
    """Local paper-only data quality ops packet."""

    packet_id: str
    packet_type: str
    stage_id: str
    issue_list: DataQualityIssueList
    repair_queue: DataRepairQueue
    issue_summary: dict[str, Any]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True

    repair_queue_is_execution_instruction: bool = False
    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False
    tag_created: bool = False
    release_created: bool = False
    deployed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "packet_type": self.packet_type,
            "stage_id": self.stage_id,
            "issue_list": self.issue_list.to_dict(),
            "repair_queue": self.repair_queue.to_dict(),
            "issue_summary": self.issue_summary,
            "created_at_utc": self.created_at_utc,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "sidecar_only": self.sidecar_only,
            "operator_review_required": self.operator_review_required,
            "repair_queue_is_execution_instruction": self.repair_queue_is_execution_instruction,
            "source_content_mutation_allowed": self.source_content_mutation_allowed,
            "source_deletion_allowed": self.source_deletion_allowed,
            "source_overwrite_allowed": self.source_overwrite_allowed,
            "trade_action_enabled": self.trade_action_enabled,
            "real_execution_allowed": self.real_execution_allowed,
            "tag_created": self.tag_created,
            "release_created": self.release_created,
            "deployed": self.deployed,
        }


def _suggest_paper_action(issue: DataQualityIssue) -> str:
    if issue.severity == "ERROR":
        return "OPEN_MANUAL_SOURCE_REVIEW_AND_PREPARE_REPAIR_NOTE"
    return "OPEN_MANUAL_DATA_QUALITY_REVIEW_NOTE"


def build_data_repair_queue_item(
    issue: DataQualityIssue,
    *,
    repair_item_id: str,
) -> DataRepairQueueItem:
    """Build one paper-only repair queue item from a D4 issue."""

    issue_errors = validate_data_quality_issue(issue)
    if issue_errors:
        raise ValueError("; ".join(issue_errors))

    priority = REPAIR_PRIORITY_HIGH if issue.severity == "ERROR" else REPAIR_PRIORITY_MEDIUM

    return DataRepairQueueItem(
        repair_item_id=repair_item_id,
        record_type=DATA_REPAIR_QUEUE_ITEM_TYPE,
        stage_id=DATA_REPAIR_QUEUE_STAGE_ID,
        source_issue_id=issue.issue_id,
        source_app_id=issue.source_app_id,
        source_type=issue.source_type,
        source_path=issue.source_path,
        issue_code=issue.issue_code,
        issue_message=issue.issue_message,
        severity=issue.severity,
        repair_status=REPAIR_STATUS_PAPER_REVIEW_REQUIRED,
        repair_priority=priority,
        suggested_paper_action=_suggest_paper_action(issue),
        evidence=issue.evidence,
    )


def validate_data_repair_queue_item(item: DataRepairQueueItem) -> list[str]:
    """Validate one repair queue item."""

    errors: list[str] = []

    if not item.repair_item_id:
        errors.append("repair_item_id is required")
    if item.record_type != DATA_REPAIR_QUEUE_ITEM_TYPE:
        errors.append("record_type mismatch")
    if item.stage_id != DATA_REPAIR_QUEUE_STAGE_ID:
        errors.append("stage_id mismatch")
    if not item.source_issue_id:
        errors.append("source_issue_id is required")
    if item.repair_status not in {REPAIR_STATUS_PAPER_REVIEW_REQUIRED, REPAIR_STATUS_NO_AUTO_REPAIR}:
        errors.append("repair_status is not allowed")
    if item.repair_priority not in {REPAIR_PRIORITY_HIGH, REPAIR_PRIORITY_MEDIUM}:
        errors.append("repair_priority is not allowed")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(item, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "repair_queue_is_execution_instruction",
        "suggested_action_is_execution_instruction",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
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
        if getattr(item, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def build_data_repair_queue(
    *,
    queue_id: str,
    issue_list: DataQualityIssueList,
) -> DataRepairQueue:
    """Build a paper-only repair queue from D4 issue list."""

    issue_list_errors = validate_data_quality_issue_list(issue_list)
    if issue_list_errors:
        raise ValueError("; ".join(issue_list_errors))

    repair_items = tuple(
        build_data_repair_queue_item(
            issue,
            repair_item_id=f"{queue_id}-REPAIR-{ordinal:04d}",
        )
        for ordinal, issue in enumerate(issue_list.issues, start=1)
    )

    return DataRepairQueue(
        queue_id=queue_id,
        queue_type=DATA_REPAIR_QUEUE_TYPE,
        stage_id=DATA_REPAIR_QUEUE_STAGE_ID,
        source_issue_list_id=issue_list.issue_list_id,
        repair_items=repair_items,
    )


def validate_data_repair_queue(queue: DataRepairQueue) -> list[str]:
    """Validate repair queue and nested items."""

    errors: list[str] = []

    if not queue.queue_id:
        errors.append("queue_id is required")
    if queue.queue_type != DATA_REPAIR_QUEUE_TYPE:
        errors.append("queue_type mismatch")
    if queue.stage_id != DATA_REPAIR_QUEUE_STAGE_ID:
        errors.append("stage_id mismatch")
    if not queue.source_issue_list_id:
        errors.append("source_issue_list_id is required")

    for item in queue.repair_items:
        errors.extend(validate_data_repair_queue_item(item))

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(queue, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "repair_queue_is_execution_instruction",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "trade_action_enabled",
        "real_execution_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(queue, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def build_data_quality_ops_packet(
    *,
    packet_id: str,
    issue_list: DataQualityIssueList,
    repair_queue: DataRepairQueue,
) -> DataQualityOpsPacket:
    """Build local paper-only data quality ops packet."""

    issue_errors = validate_data_quality_issue_list(issue_list)
    queue_errors = validate_data_repair_queue(repair_queue)
    errors = issue_errors + queue_errors
    if errors:
        raise ValueError("; ".join(errors))

    return DataQualityOpsPacket(
        packet_id=packet_id,
        packet_type=DATA_QUALITY_OPS_PACKET_TYPE,
        stage_id=DATA_REPAIR_QUEUE_STAGE_ID,
        issue_list=issue_list,
        repair_queue=repair_queue,
        issue_summary=summarize_data_quality_issue_list(issue_list),
    )


def validate_data_quality_ops_packet(packet: DataQualityOpsPacket) -> list[str]:
    """Validate local data quality ops packet."""

    errors: list[str] = []

    if not packet.packet_id:
        errors.append("packet_id is required")
    if packet.packet_type != DATA_QUALITY_OPS_PACKET_TYPE:
        errors.append("packet_type mismatch")
    if packet.stage_id != DATA_REPAIR_QUEUE_STAGE_ID:
        errors.append("stage_id mismatch")

    errors.extend(validate_data_quality_issue_list(packet.issue_list))
    errors.extend(validate_data_repair_queue(packet.repair_queue))

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(packet, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "repair_queue_is_execution_instruction",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
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


def write_data_quality_ops_packet(packet: DataQualityOpsPacket, output_path: str | Path) -> Path:
    """Write local paper-only data quality ops packet JSON."""

    errors = validate_data_quality_ops_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(packet.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path
