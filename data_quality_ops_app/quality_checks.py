"""Paper-only data quality checks for DATA-QUALITY-OPS-D3."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .source_loader import DataQualityOpsSource, validate_data_quality_ops_source


DATA_QUALITY_CHECK_STAGE_ID = "DATA-QUALITY-OPS-D3"
DATA_QUALITY_CHECK_RECORD_TYPE = "data_quality_ops_check"

CHECK_STATUS_PASS = "PASS"
CHECK_STATUS_REVIEW_REQUIRED = "REVIEW_REQUIRED"
CHECK_STATUS_FAIL = "FAIL"

CHECK_SEVERITY_INFO = "INFO"
CHECK_SEVERITY_WARN = "WARN"
CHECK_SEVERITY_ERROR = "ERROR"


@dataclass(frozen=True)
class DataQualityOpsCheck:
    """Paper-only data quality check result."""

    check_id: str
    record_type: str
    stage_id: str
    source_app_id: str
    source_type: str
    source_path: str
    check_status: str
    severity: str
    finding_code: str
    finding_message: str
    evidence: dict[str, Any]

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True

    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    repair_queue_is_execution_instruction: bool = False
    ops_check_is_trade_instruction: bool = False

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


def build_data_quality_ops_check(
    source: DataQualityOpsSource,
    *,
    check_id: str,
) -> DataQualityOpsCheck:
    """Build one paper-only data quality check from a loaded source."""

    source_errors = validate_data_quality_ops_source(source)

    if source.load_errors:
        return DataQualityOpsCheck(
            check_id=check_id,
            record_type=DATA_QUALITY_CHECK_RECORD_TYPE,
            stage_id=DATA_QUALITY_CHECK_STAGE_ID,
            source_app_id=source.source_app_id,
            source_type=source.source_type,
            source_path=source.source_path,
            check_status=CHECK_STATUS_REVIEW_REQUIRED,
            severity=CHECK_SEVERITY_WARN,
            finding_code="SOURCE_LOAD_ERRORS",
            finding_message="Source loaded with diagnostics and requires paper review.",
            evidence={"load_errors": list(source.load_errors)},
        )

    if source_errors:
        return DataQualityOpsCheck(
            check_id=check_id,
            record_type=DATA_QUALITY_CHECK_RECORD_TYPE,
            stage_id=DATA_QUALITY_CHECK_STAGE_ID,
            source_app_id=source.source_app_id,
            source_type=source.source_type,
            source_path=source.source_path,
            check_status=CHECK_STATUS_FAIL,
            severity=CHECK_SEVERITY_ERROR,
            finding_code="SOURCE_SCHEMA_INVALID",
            finding_message="Source metadata failed data quality ops validation.",
            evidence={"validation_errors": source_errors},
        )

    payload = source.payload
    if source.source_type == "health_check_report":
        state = str(payload.get("data_quality_state", "")).strip()
        if state in {"FAIL_QUARANTINE", "FAIL"}:
            return DataQualityOpsCheck(
                check_id=check_id,
                record_type=DATA_QUALITY_CHECK_RECORD_TYPE,
                stage_id=DATA_QUALITY_CHECK_STAGE_ID,
                source_app_id=source.source_app_id,
                source_type=source.source_type,
                source_path=source.source_path,
                check_status=CHECK_STATUS_FAIL,
                severity=CHECK_SEVERITY_ERROR,
                finding_code="HEALTH_CHECK_FAIL",
                finding_message="Health check indicates quarantine or failure.",
                evidence={"data_quality_state": state},
            )
        if state in {"PASS_LIMITED", "WATCHLIST_ONLY"}:
            return DataQualityOpsCheck(
                check_id=check_id,
                record_type=DATA_QUALITY_CHECK_RECORD_TYPE,
                stage_id=DATA_QUALITY_CHECK_STAGE_ID,
                source_app_id=source.source_app_id,
                source_type=source.source_type,
                source_path=source.source_path,
                check_status=CHECK_STATUS_REVIEW_REQUIRED,
                severity=CHECK_SEVERITY_WARN,
                finding_code="HEALTH_CHECK_LIMITED",
                finding_message="Health check is limited and requires paper review.",
                evidence={"data_quality_state": state},
            )

    issue_count = payload.get("issue_count")
    if isinstance(issue_count, int) and issue_count > 0:
        return DataQualityOpsCheck(
            check_id=check_id,
            record_type=DATA_QUALITY_CHECK_RECORD_TYPE,
            stage_id=DATA_QUALITY_CHECK_STAGE_ID,
            source_app_id=source.source_app_id,
            source_type=source.source_type,
            source_path=source.source_path,
            check_status=CHECK_STATUS_REVIEW_REQUIRED,
            severity=CHECK_SEVERITY_WARN,
            finding_code="ISSUES_PRESENT",
            finding_message="Source metadata reports one or more data quality issues.",
            evidence={"issue_count": issue_count},
        )

    return DataQualityOpsCheck(
        check_id=check_id,
        record_type=DATA_QUALITY_CHECK_RECORD_TYPE,
        stage_id=DATA_QUALITY_CHECK_STAGE_ID,
        source_app_id=source.source_app_id,
        source_type=source.source_type,
        source_path=source.source_path,
        check_status=CHECK_STATUS_PASS,
        severity=CHECK_SEVERITY_INFO,
        finding_code="NO_IMMEDIATE_ISSUE",
        finding_message="No immediate data quality issue detected in metadata.",
        evidence={"source_exists": source.source_exists, "file_size_bytes": source.file_size_bytes},
    )


def validate_data_quality_ops_check(check: DataQualityOpsCheck) -> list[str]:
    """Validate one data quality ops check."""

    errors: list[str] = []

    if not check.check_id:
        errors.append("check_id is required")
    if check.record_type != DATA_QUALITY_CHECK_RECORD_TYPE:
        errors.append("record_type mismatch")
    if check.stage_id != DATA_QUALITY_CHECK_STAGE_ID:
        errors.append("stage_id mismatch")
    if check.check_status not in {
        CHECK_STATUS_PASS,
        CHECK_STATUS_REVIEW_REQUIRED,
        CHECK_STATUS_FAIL,
    }:
        errors.append("check_status is not allowed")
    if check.severity not in {
        CHECK_SEVERITY_INFO,
        CHECK_SEVERITY_WARN,
        CHECK_SEVERITY_ERROR,
    }:
        errors.append("severity is not allowed")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(check, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "repair_queue_is_execution_instruction",
        "ops_check_is_trade_instruction",
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
        if getattr(check, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def build_data_quality_ops_checks(
    sources: tuple[DataQualityOpsSource, ...] | list[DataQualityOpsSource],
    *,
    check_set_id: str,
) -> tuple[DataQualityOpsCheck, ...]:
    """Build paper-only checks from loaded sources."""

    checks: list[DataQualityOpsCheck] = []
    for ordinal, source in enumerate(sources, start=1):
        checks.append(
            build_data_quality_ops_check(
                source,
                check_id=f"{check_set_id}-CHECK-{ordinal:04d}",
            )
        )
    return tuple(checks)


def summarize_data_quality_ops_checks(
    checks: tuple[DataQualityOpsCheck, ...] | list[DataQualityOpsCheck],
) -> dict[str, Any]:
    """Summarize data quality ops checks."""

    by_status: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    by_code: dict[str, int] = {}

    for check in checks:
        by_status[check.check_status] = by_status.get(check.check_status, 0) + 1
        by_severity[check.severity] = by_severity.get(check.severity, 0) + 1
        by_code[check.finding_code] = by_code.get(check.finding_code, 0) + 1

    return {
        "check_count": len(checks),
        "by_status": by_status,
        "by_severity": by_severity,
        "by_finding_code": by_code,
        "operator_review_required": True,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "source_content_mutation_allowed": False,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
    }
