"""Final workflow handoff and closeout for REPORT-ARCHIVE-D6."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .archive_contract import REPORT_ARCHIVE_APP_ID
from .archive_packet import PaperArchivePacket, validate_paper_archive_packet


REPORT_ARCHIVE_FINAL_STAGE_ID = "REPORT-ARCHIVE-D6"
FINAL_ARCHIVE_HANDOFF_PACKET_TYPE = "report_archive_final_workflow_handoff"
FINAL_ARCHIVE_CLOSEOUT_STATUS = "REPORT_ARCHIVE_APP_1_CLOSED_ON_BRANCH"


@dataclass(frozen=True)
class FinalReportArchiveHandoff:
    """Final paper-only handoff packet for REPORT-ARCHIVE-APP-1."""

    handoff_id: str
    app_id: str
    stage_id: str
    packet_type: str
    source_packet_id: str
    closeout_status: str
    paper_archive_packet: dict[str, Any]

    completed_stages: tuple[str, ...] = (
        "REPORT-ARCHIVE-D1",
        "REPORT-ARCHIVE-D2",
        "REPORT-ARCHIVE-D3",
        "REPORT-ARCHIVE-D4",
        "REPORT-ARCHIVE-D5",
        "REPORT-ARCHIVE-D6",
    )

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False

    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    archive_packet_is_trade_instruction: bool = False

    real_execution_allowed: bool = False
    trade_action_enabled: bool = False
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
        data = asdict(self)
        data["completed_stages"] = list(self.completed_stages)
        return data


def build_final_report_archive_handoff(
    *,
    handoff_id: str,
    paper_archive_packet: PaperArchivePacket,
) -> FinalReportArchiveHandoff:
    """Build final REPORT-ARCHIVE-APP-1 handoff packet."""

    packet_errors = validate_paper_archive_packet(paper_archive_packet)
    if packet_errors:
        raise ValueError("; ".join(packet_errors))

    return FinalReportArchiveHandoff(
        handoff_id=handoff_id,
        app_id=REPORT_ARCHIVE_APP_ID,
        stage_id=REPORT_ARCHIVE_FINAL_STAGE_ID,
        packet_type=FINAL_ARCHIVE_HANDOFF_PACKET_TYPE,
        source_packet_id=paper_archive_packet.packet_id,
        closeout_status=FINAL_ARCHIVE_CLOSEOUT_STATUS,
        paper_archive_packet=paper_archive_packet.to_dict(),
    )


def validate_final_report_archive_handoff(
    handoff: FinalReportArchiveHandoff,
) -> list[str]:
    """Validate final archive handoff safety and closeout constraints."""

    errors: list[str] = []

    if not handoff.handoff_id:
        errors.append("handoff_id is required")
    if handoff.app_id != REPORT_ARCHIVE_APP_ID:
        errors.append("app_id mismatch")
    if handoff.stage_id != REPORT_ARCHIVE_FINAL_STAGE_ID:
        errors.append("stage_id mismatch")
    if handoff.packet_type != FINAL_ARCHIVE_HANDOFF_PACKET_TYPE:
        errors.append("packet_type mismatch")
    if handoff.closeout_status != FINAL_ARCHIVE_CLOSEOUT_STATUS:
        errors.append("closeout_status mismatch")
    if not handoff.source_packet_id:
        errors.append("source_packet_id is required")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(handoff, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "operator_review_bypass_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "archive_packet_is_trade_instruction",
        "real_execution_allowed",
        "trade_action_enabled",
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
        if getattr(handoff, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    if tuple(handoff.completed_stages) != (
        "REPORT-ARCHIVE-D1",
        "REPORT-ARCHIVE-D2",
        "REPORT-ARCHIVE-D3",
        "REPORT-ARCHIVE-D4",
        "REPORT-ARCHIVE-D5",
        "REPORT-ARCHIVE-D6",
    ):
        errors.append("completed_stages mismatch")

    return errors


def build_report_archive_closeout_summary(
    handoff: FinalReportArchiveHandoff,
) -> dict[str, Any]:
    """Build compact REPORT-ARCHIVE-APP-1 closeout summary."""

    return {
        "app_id": handoff.app_id,
        "stage_id": handoff.stage_id,
        "handoff_id": handoff.handoff_id,
        "source_packet_id": handoff.source_packet_id,
        "closeout_status": handoff.closeout_status,
        "completed_stages": list(handoff.completed_stages),
        "paper_only": handoff.paper_only,
        "local_only": handoff.local_only,
        "read_only": handoff.read_only,
        "sidecar_only": handoff.sidecar_only,
        "operator_review_required": handoff.operator_review_required,
        "operator_review_bypass_allowed": handoff.operator_review_bypass_allowed,
        "source_content_mutation_allowed": handoff.source_content_mutation_allowed,
        "source_deletion_allowed": handoff.source_deletion_allowed,
        "source_overwrite_allowed": handoff.source_overwrite_allowed,
        "archive_packet_is_trade_instruction": handoff.archive_packet_is_trade_instruction,
        "real_execution_allowed": handoff.real_execution_allowed,
        "trade_action_enabled": handoff.trade_action_enabled,
        "buy_button_enabled": handoff.buy_button_enabled,
        "sell_button_enabled": handoff.sell_button_enabled,
        "order_button_enabled": handoff.order_button_enabled,
        "broker_connection_allowed": handoff.broker_connection_allowed,
        "exchange_connection_allowed": handoff.exchange_connection_allowed,
        "credential_storage_allowed": handoff.credential_storage_allowed,
        "wallet_private_key_access_allowed": handoff.wallet_private_key_access_allowed,
        "real_account_access_allowed": handoff.real_account_access_allowed,
        "real_position_access_allowed": handoff.real_position_access_allowed,
        "core_mutation_allowed": handoff.core_mutation_allowed,
        "p48_core_expansion_allowed": handoff.p48_core_expansion_allowed,
        "tag_created": handoff.tag_created,
        "release_created": handoff.release_created,
        "deployed": handoff.deployed,
        "created_at_utc": handoff.created_at_utc,
    }


def write_final_report_archive_handoff(
    handoff: FinalReportArchiveHandoff,
    output_path: str | Path,
) -> Path:
    """Write final archive handoff JSON as a local paper-only artifact."""

    errors = validate_final_report_archive_handoff(handoff)
    if errors:
        raise ValueError("; ".join(errors))

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(handoff.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path
