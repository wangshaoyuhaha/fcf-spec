"""Data quality operations contract for DATA-QUALITY-OPS-D1."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


DATA_QUALITY_OPS_APP_ID = "DATA-QUALITY-OPS-APP-1"
DATA_QUALITY_OPS_STAGE_ID = "DATA-QUALITY-OPS-D1"

ALLOWED_SOURCE_APP_IDS = (
    "DATA-APP-1",
    "REPORT-ARCHIVE-APP-1",
    "OPERATOR-REVIEW-APP-1",
)

ALLOWED_SOURCE_TYPES = (
    "data_quality_summary",
    "health_check_report",
    "quarantine_report",
    "archive_manifest",
    "paper_archive_packet",
    "operator_review_handoff",
)

OPS_OUTPUT_TYPES = (
    "data_quality_ops_check",
    "data_quality_issue_list",
    "data_repair_queue",
    "data_quality_ops_handoff",
)

_FORBIDDEN_TRUE_FLAGS = (
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
    "source_content_mutation_allowed",
    "source_deletion_allowed",
    "source_overwrite_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
    "operator_review_bypass_allowed",
    "tag_created",
    "release_created",
    "deployed",
)


@dataclass(frozen=True)
class DataQualityOpsContract:
    """Static safety contract for the data quality operations sidecar."""

    app_id: str = DATA_QUALITY_OPS_APP_ID
    stage_id: str = DATA_QUALITY_OPS_STAGE_ID
    contract_version: str = "1.0.0"

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False

    allowed_source_app_ids: tuple[str, ...] = ALLOWED_SOURCE_APP_IDS
    allowed_source_types: tuple[str, ...] = ALLOWED_SOURCE_TYPES
    ops_output_types: tuple[str, ...] = OPS_OUTPUT_TYPES

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

    notes: tuple[str, ...] = field(
        default_factory=lambda: (
            "Inspect local data quality artifacts only.",
            "Create paper-only issue lists and repair queues only.",
            "Never mutate source data or reports.",
            "Never convert repair queues into execution instructions.",
            "Never mutate P1-P47 core modules.",
        )
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_source_app_ids"] = list(self.allowed_source_app_ids)
        data["allowed_source_types"] = list(self.allowed_source_types)
        data["ops_output_types"] = list(self.ops_output_types)
        data["notes"] = list(self.notes)
        return data


def build_data_quality_ops_contract() -> DataQualityOpsContract:
    """Build the static DATA-QUALITY-OPS-D1 contract."""
    return DataQualityOpsContract()


def validate_data_quality_ops_contract(contract: DataQualityOpsContract) -> list[str]:
    """Validate the DATA-QUALITY-OPS-D1 safety contract."""

    errors: list[str] = []

    if contract.app_id != DATA_QUALITY_OPS_APP_ID:
        errors.append("app_id mismatch")
    if contract.stage_id != DATA_QUALITY_OPS_STAGE_ID:
        errors.append("stage_id mismatch")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(contract, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    for flag_name in _FORBIDDEN_TRUE_FLAGS:
        if getattr(contract, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    if contract.repair_queue_is_execution_instruction is not False:
        errors.append("repair_queue_is_execution_instruction must be false")
    if contract.ops_check_is_trade_instruction is not False:
        errors.append("ops_check_is_trade_instruction must be false")

    if tuple(contract.allowed_source_app_ids) != ALLOWED_SOURCE_APP_IDS:
        errors.append("allowed_source_app_ids mismatch")
    if tuple(contract.allowed_source_types) != ALLOWED_SOURCE_TYPES:
        errors.append("allowed_source_types mismatch")
    if tuple(contract.ops_output_types) != OPS_OUTPUT_TYPES:
        errors.append("ops_output_types mismatch")

    return errors
