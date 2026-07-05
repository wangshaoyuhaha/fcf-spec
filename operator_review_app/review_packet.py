"""No-execution receipt and local review packet for OPERATOR-REVIEW-D5."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paper_review_record import PaperReviewRecord, validate_paper_review_record
from .reviewer_risk_models import (
    ReviewerNoteRecord,
    RiskAcknowledgementRecord,
    validate_reviewer_note_record,
    validate_risk_acknowledgement_record,
)


NO_EXECUTION_RECEIPT_TYPE = "no_execution_receipt"
LOCAL_REVIEW_PACKET_TYPE = "local_operator_review_packet"


@dataclass(frozen=True)
class NoExecutionReceipt:
    """Receipt proving this review packet cannot execute trades."""

    review_record_id: str
    receipt_type: str = NO_EXECUTION_RECEIPT_TYPE
    no_execution_receipt: bool = True

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True

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
    operator_review_bypass_allowed: bool = False
    core_mutation_allowed: bool = False
    p48_core_expansion_allowed: bool = False

    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LocalReviewPacket:
    """Local paper-only operator review packet."""

    packet_id: str
    packet_type: str
    review_record: PaperReviewRecord
    reviewer_note: ReviewerNoteRecord
    risk_acknowledgement: RiskAcknowledgementRecord
    no_execution_receipt: NoExecutionReceipt
    created_at_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    real_execution_allowed: bool = False
    trade_action_enabled: bool = False
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "packet_type": self.packet_type,
            "review_record": self.review_record.to_dict(),
            "reviewer_note": self.reviewer_note.to_dict(),
            "risk_acknowledgement": self.risk_acknowledgement.to_dict(),
            "no_execution_receipt": self.no_execution_receipt.to_dict(),
            "created_at_utc": self.created_at_utc,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "real_execution_allowed": self.real_execution_allowed,
            "trade_action_enabled": self.trade_action_enabled,
            "operator_review_required": self.operator_review_required,
            "operator_review_bypass_allowed": self.operator_review_bypass_allowed,
        }


def build_no_execution_receipt(review_record: PaperReviewRecord) -> NoExecutionReceipt:
    """Create a no-execution receipt for a paper review record."""
    return NoExecutionReceipt(review_record_id=review_record.review_record_id)


def validate_no_execution_receipt(receipt: NoExecutionReceipt) -> list[str]:
    """Validate no-execution receipt safety constraints."""

    errors: list[str] = []

    if not receipt.review_record_id:
        errors.append("review_record_id is required")
    if receipt.receipt_type != NO_EXECUTION_RECEIPT_TYPE:
        errors.append("receipt_type mismatch")
    if receipt.no_execution_receipt is not True:
        errors.append("no_execution_receipt must be true")

    required_true_flags = ("paper_only", "local_only", "read_only")
    for flag_name in required_true_flags:
        if getattr(receipt, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
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
        "operator_review_bypass_allowed",
        "core_mutation_allowed",
        "p48_core_expansion_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(receipt, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def build_local_review_packet(
    *,
    packet_id: str,
    review_record: PaperReviewRecord,
    reviewer_note: ReviewerNoteRecord,
    risk_acknowledgement: RiskAcknowledgementRecord,
    no_execution_receipt: NoExecutionReceipt | None = None,
) -> LocalReviewPacket:
    """Build a local paper-only operator review packet."""

    receipt = no_execution_receipt or build_no_execution_receipt(review_record)

    return LocalReviewPacket(
        packet_id=packet_id,
        packet_type=LOCAL_REVIEW_PACKET_TYPE,
        review_record=review_record,
        reviewer_note=reviewer_note,
        risk_acknowledgement=risk_acknowledgement,
        no_execution_receipt=receipt,
    )


def validate_local_review_packet(packet: LocalReviewPacket) -> list[str]:
    """Validate local review packet and nested safety records."""

    errors: list[str] = []

    if not packet.packet_id:
        errors.append("packet_id is required")
    if packet.packet_type != LOCAL_REVIEW_PACKET_TYPE:
        errors.append("packet_type mismatch")

    errors.extend(validate_paper_review_record(packet.review_record))
    errors.extend(validate_reviewer_note_record(packet.reviewer_note))
    errors.extend(validate_risk_acknowledgement_record(packet.risk_acknowledgement))
    errors.extend(validate_no_execution_receipt(packet.no_execution_receipt))

    review_record_id = packet.review_record.review_record_id
    nested_ids = {
        packet.reviewer_note.review_record_id,
        packet.risk_acknowledgement.review_record_id,
        packet.no_execution_receipt.review_record_id,
    }
    if nested_ids != {review_record_id}:
        errors.append("nested review_record_id values must match")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(packet, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    forbidden_true_flags = (
        "real_execution_allowed",
        "trade_action_enabled",
        "operator_review_bypass_allowed",
    )
    for flag_name in forbidden_true_flags:
        if getattr(packet, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    return errors


def write_local_review_packet(
    packet: LocalReviewPacket,
    output_path: str | Path,
) -> Path:
    """Write the local packet to disk as JSON.

    This writes only local paper-only artifacts and never executes trades.
    """

    errors = validate_local_review_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(packet.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path
