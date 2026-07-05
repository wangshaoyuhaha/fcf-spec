"""Archive contract for REPORT-ARCHIVE-D1."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


REPORT_ARCHIVE_APP_ID = "REPORT-ARCHIVE-APP-1"
REPORT_ARCHIVE_STAGE_ID = "REPORT-ARCHIVE-D1"

ALLOWED_SOURCE_APP_IDS = (
    "DATA-APP-1",
    "STOCK-APP-1",
    "AI-CONTEXT-1",
    "UI-APP-1",
    "OPERATOR-REVIEW-APP-1",
)

ALLOWED_SOURCE_TYPES = (
    "local_report_artifact",
    "workflow_handoff",
    "final_handoff",
    "closeout_summary",
)

ARCHIVE_OUTPUT_TYPES = (
    "archive_manifest",
    "archive_item_index",
    "archive_integrity_summary",
    "paper_archive_packet",
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
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
    "operator_review_bypass_allowed",
    "tag_created",
    "release_created",
    "deployed",
)


@dataclass(frozen=True)
class ReportArchiveContract:
    """Static safety contract for the report archive sidecar."""

    app_id: str = REPORT_ARCHIVE_APP_ID
    stage_id: str = REPORT_ARCHIVE_STAGE_ID
    contract_version: str = "1.0.0"

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False

    allowed_source_app_ids: tuple[str, ...] = ALLOWED_SOURCE_APP_IDS
    allowed_source_types: tuple[str, ...] = ALLOWED_SOURCE_TYPES
    archive_output_types: tuple[str, ...] = ARCHIVE_OUTPUT_TYPES

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

    notes: tuple[str, ...] = field(
        default_factory=lambda: (
            "Archive local report and handoff artifacts only.",
            "Never mutate source report contents.",
            "Never convert archive packets into trade instructions.",
            "Never mutate P1-P47 core modules.",
            "Never tag, release, or deploy from this sidecar.",
        )
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["allowed_source_app_ids"] = list(self.allowed_source_app_ids)
        data["allowed_source_types"] = list(self.allowed_source_types)
        data["archive_output_types"] = list(self.archive_output_types)
        data["notes"] = list(self.notes)
        return data


def build_report_archive_contract() -> ReportArchiveContract:
    """Build the static REPORT-ARCHIVE-D1 contract."""
    return ReportArchiveContract()


def validate_report_archive_contract(contract: ReportArchiveContract) -> list[str]:
    """Validate the D1 archive safety contract."""

    errors: list[str] = []

    if contract.app_id != REPORT_ARCHIVE_APP_ID:
        errors.append("app_id mismatch")
    if contract.stage_id != REPORT_ARCHIVE_STAGE_ID:
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

    source_mutation_forbidden_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "archive_packet_is_trade_instruction",
    )
    for flag_name in source_mutation_forbidden_flags:
        if getattr(contract, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    if tuple(contract.allowed_source_app_ids) != ALLOWED_SOURCE_APP_IDS:
        errors.append("allowed_source_app_ids mismatch")
    if tuple(contract.allowed_source_types) != ALLOWED_SOURCE_TYPES:
        errors.append("allowed_source_types mismatch")
    if tuple(contract.archive_output_types) != ARCHIVE_OUTPUT_TYPES:
        errors.append("archive_output_types mismatch")

    return errors
