"""Paper review record schema for OPERATOR-REVIEW-D3."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .ui_app_source_loader import UiAppSourcePayload, summarize_ui_app_source_payload


REVIEW_STATUS_PENDING = "PENDING_OPERATOR_REVIEW"
PAPER_DECISION_LABEL_UNDECIDED = "PAPER_UNDECIDED"

ALLOWED_REVIEW_STATUSES = {
    REVIEW_STATUS_PENDING,
    "REVIEWED_ON_PAPER",
    "NEEDS_MORE_DATA",
    "REJECTED_ON_PAPER",
}

ALLOWED_PAPER_DECISION_LABELS = {
    PAPER_DECISION_LABEL_UNDECIDED,
    "PAPER_WATCH_ONLY",
    "PAPER_REJECT",
    "PAPER_REVIEW_LATER",
}


@dataclass(frozen=True)
class PaperReviewRecord:
    """Paper-only review record.

    This schema cannot represent a real trade, order, or execution.
    """

    review_record_id: str
    source_report_id: str
    source_stage_id: str
    candidate_count: int
    review_status: str = REVIEW_STATUS_PENDING
    paper_decision_label: str = PAPER_DECISION_LABEL_UNDECIDED

    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False
    review_status_is_trade_action: bool = False
    paper_decision_label_is_trade_action: bool = False

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

    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    data_sources: tuple[str, ...] = ()
    handoff_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["data_sources"] = list(self.data_sources)
        return data


def build_paper_review_record_from_ui_source(
    source: UiAppSourcePayload,
    *,
    review_record_id: str,
    review_status: str = REVIEW_STATUS_PENDING,
    paper_decision_label: str = PAPER_DECISION_LABEL_UNDECIDED,
) -> PaperReviewRecord:
    """Create a paper review record from a loaded UI-APP source payload."""

    summary = summarize_ui_app_source_payload(source)

    return PaperReviewRecord(
        review_record_id=review_record_id,
        source_report_id=str(summary.get("source_report_id") or ""),
        source_stage_id=str(summary.get("source_stage_id") or ""),
        candidate_count=int(summary.get("candidate_count") or 0),
        review_status=review_status,
        paper_decision_label=paper_decision_label,
        operator_review_required=bool(summary.get("operator_review_required", True)),
        data_sources=(source.source_path,),
        handoff_summary=summary,
    )


def validate_paper_review_record(record: PaperReviewRecord) -> list[str]:
    """Validate paper review record safety and schema constraints."""

    errors: list[str] = []

    if not record.review_record_id:
        errors.append("review_record_id is required")
    if record.candidate_count < 0:
        errors.append("candidate_count must be non-negative")
    if record.review_status not in ALLOWED_REVIEW_STATUSES:
        errors.append("review_status is not allowed")
    if record.paper_decision_label not in ALLOWED_PAPER_DECISION_LABELS:
        errors.append("paper_decision_label is not allowed")

    required_true_flags = (
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(record, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "operator_review_bypass_allowed",
        "review_status_is_trade_action",
        "paper_decision_label_is_trade_action",
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
    )
    for flag_name in forbidden_true_flags:
        if getattr(record, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors
