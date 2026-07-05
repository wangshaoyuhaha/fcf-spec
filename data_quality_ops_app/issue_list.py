"""Paper-only data quality issue list for DATA-QUALITY-OPS-D4."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .quality_checks import (
    CHECK_SEVERITY_ERROR,
    CHECK_SEVERITY_WARN,
    CHECK_STATUS_FAIL,
    CHECK_STATUS_REVIEW_REQUIRED,
    DataQualityOpsCheck,
    validate_data_quality_ops_check,
)


DATA_QUALITY_ISSUE_STAGE_ID = "DATA-QUALITY-OPS-D4"
DATA_QUALITY_ISSUE_RECORD_TYPE = "data_quality_issue"
DATA_QUALITY_ISSUE_LIST_TYPE = "data_quality_issue_list"

ISSUE_STATUS_OPEN = "OPEN_FOR_PAPER_REVIEW"
ISSUE_STATUS_NO_ACTION_REQUIRED = "NO_ACTION_REQUIRED"


@dataclass(frozen=True)
class DataQualityIssue:
    """Paper-only data quality issue derived from a quality check."""

    issue_id: str
    record_type: str
    stage_id: str
    source_check_id: str
    source_app_id: str
    source_type: str
    source_path: str
    issue_status: str
    severity: str
    issue_code: str
    issue_message: str
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
    issue_is_trade_instruction: bool = False

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
class DataQualityIssueList:
    """Paper-only issue list built from D3 checks."""

    issue_list_id: str
    list_type: str
    stage_id: str
    issues: tuple[DataQualityIssue, ...]
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    operator_review_required: bool = True

    source_content_mutation_allowed: bool = False
    source_deletion_allowed: bool = False
    source_overwrite_allowed: bool = False
    repair_queue_is_execution_instruction: bool = False
    issue_list_is_trade_instruction: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_list_id": self.issue_list_id,
            "list_type": self.list_type,
            "stage_id": self.stage_id,
            "issues": [issue.to_dict() for issue in self.issues],
            "created_at_utc": self.created_at_utc,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "sidecar_only": self.sidecar_only,
            "operator_review_required": self.operator_review_required,
            "source_content_mutation_allowed": self.source_content_mutation_allowed,
            "source_deletion_allowed": self.source_deletion_allowed,
            "source_overwrite_allowed": self.source_overwrite_allowed,
            "repair_queue_is_execution_instruction": self.repair_queue_is_execution_instruction,
            "issue_list_is_trade_instruction": self.issue_list_is_trade_instruction,
            "trade_action_enabled": self.trade_action_enabled,
            "real_execution_allowed": self.real_execution_allowed,
        }


def build_data_quality_issue_from_check(
    check: DataQualityOpsCheck,
    *,
    issue_id: str,
) -> DataQualityIssue | None:
    """Build one paper-only issue from a D3 check if review is required."""

    check_errors = validate_data_quality_ops_check(check)
    if check_errors:
        raise ValueError("; ".join(check_errors))

    if check.check_status not in {CHECK_STATUS_REVIEW_REQUIRED, CHECK_STATUS_FAIL}:
        return None

    issue_status = ISSUE_STATUS_OPEN
    severity = check.severity
    if check.check_status == CHECK_STATUS_FAIL:
        severity = CHECK_SEVERITY_ERROR
    elif check.severity not in {CHECK_SEVERITY_WARN, CHECK_SEVERITY_ERROR}:
        severity = CHECK_SEVERITY_WARN

    return DataQualityIssue(
        issue_id=issue_id,
        record_type=DATA_QUALITY_ISSUE_RECORD_TYPE,
        stage_id=DATA_QUALITY_ISSUE_STAGE_ID,
        source_check_id=check.check_id,
        source_app_id=check.source_app_id,
        source_type=check.source_type,
        source_path=check.source_path,
        issue_status=issue_status,
        severity=severity,
        issue_code=check.finding_code,
        issue_message=check.finding_message,
        evidence=check.evidence,
    )


def validate_data_quality_issue(issue: DataQualityIssue) -> list[str]:
    """Validate one data quality issue."""

    errors: list[str] = []

    if not issue.issue_id:
        errors.append("issue_id is required")
    if issue.record_type != DATA_QUALITY_ISSUE_RECORD_TYPE:
        errors.append("record_type mismatch")
    if issue.stage_id != DATA_QUALITY_ISSUE_STAGE_ID:
        errors.append("stage_id mismatch")
    if issue.issue_status not in {ISSUE_STATUS_OPEN, ISSUE_STATUS_NO_ACTION_REQUIRED}:
        errors.append("issue_status is not allowed")
    if issue.severity not in {"INFO", "WARN", "ERROR"}:
        errors.append("severity is not allowed")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(issue, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "repair_queue_is_execution_instruction",
        "issue_is_trade_instruction",
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
        if getattr(issue, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def build_data_quality_issue_list(
    *,
    issue_list_id: str,
    checks: tuple[DataQualityOpsCheck, ...] | list[DataQualityOpsCheck],
) -> DataQualityIssueList:
    """Build paper-only issue list from D3 checks."""

    issues: list[DataQualityIssue] = []
    for ordinal, check in enumerate(checks, start=1):
        issue = build_data_quality_issue_from_check(
            check,
            issue_id=f"{issue_list_id}-ISSUE-{ordinal:04d}",
        )
        if issue is not None:
            issues.append(issue)

    return DataQualityIssueList(
        issue_list_id=issue_list_id,
        list_type=DATA_QUALITY_ISSUE_LIST_TYPE,
        stage_id=DATA_QUALITY_ISSUE_STAGE_ID,
        issues=tuple(issues),
    )


def validate_data_quality_issue_list(issue_list: DataQualityIssueList) -> list[str]:
    """Validate issue list and nested issues."""

    errors: list[str] = []

    if not issue_list.issue_list_id:
        errors.append("issue_list_id is required")
    if issue_list.list_type != DATA_QUALITY_ISSUE_LIST_TYPE:
        errors.append("list_type mismatch")
    if issue_list.stage_id != DATA_QUALITY_ISSUE_STAGE_ID:
        errors.append("stage_id mismatch")

    for issue in issue_list.issues:
        errors.extend(validate_data_quality_issue(issue))

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(issue_list, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "repair_queue_is_execution_instruction",
        "issue_list_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(issue_list, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def summarize_data_quality_issue_list(issue_list: DataQualityIssueList) -> dict[str, Any]:
    """Summarize paper-only data quality issue list."""

    by_severity: dict[str, int] = {}
    by_code: dict[str, int] = {}
    by_status: dict[str, int] = {}

    for issue in issue_list.issues:
        by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
        by_code[issue.issue_code] = by_code.get(issue.issue_code, 0) + 1
        by_status[issue.issue_status] = by_status.get(issue.issue_status, 0) + 1

    return {
        "issue_list_id": issue_list.issue_list_id,
        "issue_count": len(issue_list.issues),
        "by_severity": by_severity,
        "by_issue_code": by_code,
        "by_issue_status": by_status,
        "operator_review_required": issue_list.operator_review_required,
        "paper_only": issue_list.paper_only,
        "local_only": issue_list.local_only,
        "read_only": issue_list.read_only,
        "sidecar_only": issue_list.sidecar_only,
        "source_content_mutation_allowed": issue_list.source_content_mutation_allowed,
        "trade_action_enabled": issue_list.trade_action_enabled,
        "real_execution_allowed": issue_list.real_execution_allowed,
    }
