"""Final workflow handoff and closeout for DATA-QUALITY-OPS-D6."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ops_contract import DATA_QUALITY_OPS_APP_ID
from .repair_queue import DataQualityOpsPacket, validate_data_quality_ops_packet


DATA_QUALITY_OPS_FINAL_STAGE_ID = "DATA-QUALITY-OPS-D6"
FINAL_DATA_QUALITY_OPS_HANDOFF_TYPE = "data_quality_ops_final_workflow_handoff"
FINAL_DATA_QUALITY_OPS_CLOSEOUT_STATUS = "DATA_QUALITY_OPS_APP_1_CLOSED_ON_BRANCH"


@dataclass(frozen=True)
class FinalDataQualityOpsHandoff:
    """Final paper-only handoff packet for DATA-QUALITY-OPS-APP-1."""

    handoff_id: str
    app_id: str
    stage_id: str
    packet_type: str
    source_packet_id: str
    closeout_status: str
    data_quality_ops_packet: dict[str, Any]

    completed_stages: tuple[str, ...] = (
        "DATA-QUALITY-OPS-D1",
        "DATA-QUALITY-OPS-D2",
        "DATA-QUALITY-OPS-D3",
        "DATA-QUALITY-OPS-D4",
        "DATA-QUALITY-OPS-D5",
        "DATA-QUALITY-OPS-D6",
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
    repair_queue_is_execution_instruction: bool = False
    ops_check_is_trade_instruction: bool = False

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


def build_final_data_quality_ops_handoff(
    *,
    handoff_id: str,
    data_quality_ops_packet: DataQualityOpsPacket,
) -> FinalDataQualityOpsHandoff:
    """Build final DATA-QUALITY-OPS-APP-1 handoff packet."""

    packet_errors = validate_data_quality_ops_packet(data_quality_ops_packet)
    if packet_errors:
        raise ValueError("; ".join(packet_errors))

    return FinalDataQualityOpsHandoff(
        handoff_id=handoff_id,
        app_id=DATA_QUALITY_OPS_APP_ID,
        stage_id=DATA_QUALITY_OPS_FINAL_STAGE_ID,
        packet_type=FINAL_DATA_QUALITY_OPS_HANDOFF_TYPE,
        source_packet_id=data_quality_ops_packet.packet_id,
        closeout_status=FINAL_DATA_QUALITY_OPS_CLOSEOUT_STATUS,
        data_quality_ops_packet=data_quality_ops_packet.to_dict(),
    )


def validate_final_data_quality_ops_handoff(
    handoff: FinalDataQualityOpsHandoff,
) -> list[str]:
    """Validate final data quality ops handoff safety constraints."""

    errors: list[str] = []

    if not handoff.handoff_id:
        errors.append("handoff_id is required")
    if handoff.app_id != DATA_QUALITY_OPS_APP_ID:
        errors.append("app_id mismatch")
    if handoff.stage_id != DATA_QUALITY_OPS_FINAL_STAGE_ID:
        errors.append("stage_id mismatch")
    if handoff.packet_type != FINAL_DATA_QUALITY_OPS_HANDOFF_TYPE:
        errors.append("packet_type mismatch")
    if handoff.closeout_status != FINAL_DATA_QUALITY_OPS_CLOSEOUT_STATUS:
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
        "repair_queue_is_execution_instruction",
        "ops_check_is_trade_instruction",
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
        "DATA-QUALITY-OPS-D1",
        "DATA-QUALITY-OPS-D2",
        "DATA-QUALITY-OPS-D3",
        "DATA-QUALITY-OPS-D4",
        "DATA-QUALITY-OPS-D5",
        "DATA-QUALITY-OPS-D6",
    ):
        errors.append("completed_stages mismatch")

    return errors


def build_data_quality_ops_closeout_summary(
    handoff: FinalDataQualityOpsHandoff,
) -> dict[str, Any]:
    """Build compact DATA-QUALITY-OPS-APP-1 closeout summary."""

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
        "repair_queue_is_execution_instruction": handoff.repair_queue_is_execution_instruction,
        "ops_check_is_trade_instruction": handoff.ops_check_is_trade_instruction,
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


def write_final_data_quality_ops_handoff(
    handoff: FinalDataQualityOpsHandoff,
    output_path: str | Path,
) -> Path:
    """Write final handoff JSON as a local paper-only artifact."""

    errors = validate_final_data_quality_ops_handoff(handoff)
    if errors:
        raise ValueError("; ".join(errors))

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(handoff.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path
