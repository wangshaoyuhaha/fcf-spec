"""Reviewer note and risk acknowledgement models for OPERATOR-REVIEW-D4."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .paper_review_record import PaperReviewRecord


REVIEWER_NOTE_RECORD_TYPE = "reviewer_note_record"
RISK_ACKNOWLEDGEMENT_RECORD_TYPE = "risk_acknowledgement_record"
RISK_ACKNOWLEDGEMENT_STATUS = "RISK_ACKNOWLEDGED_ON_PAPER"
RISK_ACKNOWLEDGEMENT_PENDING = "RISK_ACKNOWLEDGEMENT_PENDING"


@dataclass(frozen=True)
class ReviewerNoteRecord:
    """Paper-only reviewer note.

    The note is local documentation only and cannot become a trade instruction.
    """

    review_record_id: str
    record_type: str = REVIEWER_NOTE_RECORD_TYPE
    reviewer_note: str = ""
    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    note_is_trade_instruction: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False
    operator_review_required: bool = True
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RiskAcknowledgementRecord:
    """Paper-only risk acknowledgement.

    This record documents that risk flags were reviewed on paper.
    """

    review_record_id: str
    record_type: str = RISK_ACKNOWLEDGEMENT_RECORD_TYPE
    risk_acknowledgement: bool = False
    acknowledgement_status: str = RISK_ACKNOWLEDGEMENT_PENDING
    acknowledged_risk_flags: tuple[str, ...] = ()
    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    acknowledgement_is_trade_instruction: bool = False
    trade_action_enabled: bool = False
    real_execution_allowed: bool = False
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["acknowledged_risk_flags"] = list(self.acknowledged_risk_flags)
        return data


def build_reviewer_note_record(
    review_record: PaperReviewRecord,
    *,
    reviewer_note: str,
) -> ReviewerNoteRecord:
    """Create a paper-only reviewer note from a paper review record."""

    return ReviewerNoteRecord(
        review_record_id=review_record.review_record_id,
        reviewer_note=reviewer_note.strip(),
    )


def build_risk_acknowledgement_record(
    review_record: PaperReviewRecord,
    *,
    acknowledged_risk_flags: tuple[str, ...] | list[str] = (),
    risk_acknowledgement: bool = False,
) -> RiskAcknowledgementRecord:
    """Create a paper-only risk acknowledgement from a paper review record."""

    normalized_flags = tuple(str(item).strip() for item in acknowledged_risk_flags if str(item).strip())
    status = (
        RISK_ACKNOWLEDGEMENT_STATUS
        if risk_acknowledgement
        else RISK_ACKNOWLEDGEMENT_PENDING
    )

    return RiskAcknowledgementRecord(
        review_record_id=review_record.review_record_id,
        risk_acknowledgement=risk_acknowledgement,
        acknowledgement_status=status,
        acknowledged_risk_flags=normalized_flags,
    )


def validate_reviewer_note_record(note: ReviewerNoteRecord) -> list[str]:
    """Validate reviewer note safety and schema constraints."""

    errors: list[str] = []

    if not note.review_record_id:
        errors.append("review_record_id is required")
    if note.record_type != REVIEWER_NOTE_RECORD_TYPE:
        errors.append("record_type mismatch")
    if len(note.reviewer_note) > 2000:
        errors.append("reviewer_note is too long")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(note, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "note_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(note, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def validate_risk_acknowledgement_record(
    acknowledgement: RiskAcknowledgementRecord,
) -> list[str]:
    """Validate risk acknowledgement safety and schema constraints."""

    errors: list[str] = []

    if not acknowledgement.review_record_id:
        errors.append("review_record_id is required")
    if acknowledgement.record_type != RISK_ACKNOWLEDGEMENT_RECORD_TYPE:
        errors.append("record_type mismatch")
    if acknowledgement.acknowledgement_status not in {
        RISK_ACKNOWLEDGEMENT_STATUS,
        RISK_ACKNOWLEDGEMENT_PENDING,
    }:
        errors.append("acknowledgement_status is not allowed")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(acknowledgement, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "acknowledgement_is_trade_instruction",
        "trade_action_enabled",
        "real_execution_allowed",
        "operator_review_bypass_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(acknowledgement, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors
