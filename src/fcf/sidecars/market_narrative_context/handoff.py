"""Operator-review and archive handoff for narrative context."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .review_packet import NarrativeReviewPacket
from .review_packet import NarrativeReviewPacketState
from .review_packet import assert_valid_narrative_review_packet


_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class NarrativeHandoffViolation(ValueError):
    """Raised when narrative handoff metadata is invalid."""


class NarrativeHandoffState(str, Enum):
    """Deterministic operator and archive handoff state."""

    READY_FOR_ARCHIVE_REVIEW = "READY_FOR_ARCHIVE_REVIEW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED_PENDING_EVIDENCE = "BLOCKED_PENDING_EVIDENCE"


@dataclass(frozen=True)
class NarrativeReviewHandoff:
    """Immutable paper-only operator and archive handoff."""

    handoff_id: str
    packet_id: str
    correlation_id: str
    research_run_id: str
    narrative_artifact_id: str
    target_artifact_id: str
    source_packet_state: str
    handoff_state: NarrativeHandoffState
    reason_codes: tuple[str, ...]
    risk_flags: tuple[str, ...]
    review_status: str
    truth_status: str
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False
    archive_required: bool = True
    source_packet_preserved: bool = True
    original_conclusions_preserved: bool = True
    no_execution_receipt: bool = True
    automatic_truth_decision_allowed: bool = False
    automatic_conclusion_replacement_allowed: bool = False
    trade_action_allowed: bool = False
    real_execution_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic handoff representation."""

        return {
            "handoff_id": self.handoff_id,
            "packet_id": self.packet_id,
            "correlation_id": self.correlation_id,
            "research_run_id": self.research_run_id,
            "narrative_artifact_id": self.narrative_artifact_id,
            "target_artifact_id": self.target_artifact_id,
            "source_packet_state": self.source_packet_state,
            "handoff_state": self.handoff_state.value,
            "reason_codes": list(self.reason_codes),
            "risk_flags": list(self.risk_flags),
            "review_status": self.review_status,
            "truth_status": self.truth_status,
            "operator_review_required": (
                self.operator_review_required
            ),
            "operator_review_bypass_allowed": (
                self.operator_review_bypass_allowed
            ),
            "archive_required": self.archive_required,
            "source_packet_preserved": self.source_packet_preserved,
            "original_conclusions_preserved": (
                self.original_conclusions_preserved
            ),
            "no_execution_receipt": self.no_execution_receipt,
            "automatic_truth_decision_allowed": (
                self.automatic_truth_decision_allowed
            ),
            "automatic_conclusion_replacement_allowed": (
                self.automatic_conclusion_replacement_allowed
            ),
            "trade_action_allowed": self.trade_action_allowed,
            "real_execution_allowed": self.real_execution_allowed,
        }


def _valid_identifier(value: str) -> bool:
    return bool(_ID_PATTERN.fullmatch(value))


def _expected_handoff_state(
    packet_state: NarrativeReviewPacketState,
) -> NarrativeHandoffState:
    if (
        packet_state
        is NarrativeReviewPacketState.BLOCKED_PENDING_EVIDENCE
    ):
        return NarrativeHandoffState.BLOCKED_PENDING_EVIDENCE

    if packet_state is NarrativeReviewPacketState.REVIEW_REQUIRED:
        return NarrativeHandoffState.REVIEW_REQUIRED

    return NarrativeHandoffState.READY_FOR_ARCHIVE_REVIEW


def build_narrative_review_handoff(
    handoff_id: str,
    packet: NarrativeReviewPacket,
) -> NarrativeReviewHandoff:
    """Build a deterministic handoff from a valid D5 packet."""

    assert_valid_narrative_review_packet(packet)

    handoff = NarrativeReviewHandoff(
        handoff_id=handoff_id,
        packet_id=packet.packet_id,
        correlation_id=packet.correlation_id,
        research_run_id=packet.research_run_id,
        narrative_artifact_id=packet.narrative_artifact_id,
        target_artifact_id=packet.target_artifact_id,
        source_packet_state=packet.packet_state.value,
        handoff_state=_expected_handoff_state(packet.packet_state),
        reason_codes=packet.reason_codes,
        risk_flags=packet.risk_flags,
        review_status=packet.review_status,
        truth_status=packet.truth_status,
    )

    assert_valid_narrative_review_handoff(handoff)
    return handoff


def validate_narrative_review_handoff(
    handoff: NarrativeReviewHandoff,
) -> tuple[str, ...]:
    """Return deterministic handoff violations."""

    violations: list[str] = []

    identifier_fields = (
        ("handoff_id", handoff.handoff_id),
        ("packet_id", handoff.packet_id),
        ("correlation_id", handoff.correlation_id),
        ("research_run_id", handoff.research_run_id),
        ("narrative_artifact_id", handoff.narrative_artifact_id),
        ("target_artifact_id", handoff.target_artifact_id),
    )

    for field_name, value in identifier_fields:
        if not _valid_identifier(value):
            violations.append(f"INVALID_IDENTIFIER:{field_name}")

    valid_packet_states = {
        state.value for state in NarrativeReviewPacketState
    }

    if handoff.source_packet_state not in valid_packet_states:
        violations.append("INVALID_SOURCE_PACKET_STATE")

    if not isinstance(handoff.handoff_state, NarrativeHandoffState):
        violations.append("INVALID_HANDOFF_STATE")

    expected_mapping = {
        NarrativeReviewPacketState.READY_FOR_OPERATOR_REVIEW.value: (
            NarrativeHandoffState.READY_FOR_ARCHIVE_REVIEW
        ),
        NarrativeReviewPacketState.REVIEW_REQUIRED.value: (
            NarrativeHandoffState.REVIEW_REQUIRED
        ),
        NarrativeReviewPacketState.BLOCKED_PENDING_EVIDENCE.value: (
            NarrativeHandoffState.BLOCKED_PENDING_EVIDENCE
        ),
    }

    expected_state = expected_mapping.get(
        handoff.source_packet_state
    )

    if (
        expected_state is not None
        and handoff.handoff_state is not expected_state
    ):
        violations.append("HANDOFF_STATE_MAPPING_MISMATCH")

    if handoff.review_status != "PENDING_OPERATOR_REVIEW":
        violations.append("INVALID_REVIEW_STATUS")

    if handoff.truth_status != "UNDETERMINED":
        violations.append("INVALID_TRUTH_STATUS")

    required_true = (
        "operator_review_required",
        "archive_required",
        "source_packet_preserved",
        "original_conclusions_preserved",
        "no_execution_receipt",
    )

    required_false = (
        "operator_review_bypass_allowed",
        "automatic_truth_decision_allowed",
        "automatic_conclusion_replacement_allowed",
        "trade_action_allowed",
        "real_execution_allowed",
    )

    for field_name in required_true:
        if getattr(handoff, field_name) is not True:
            violations.append(f"REQUIRED_TRUE:{field_name}")

    for field_name in required_false:
        if getattr(handoff, field_name) is not False:
            violations.append(f"REQUIRED_FALSE:{field_name}")

    if len(set(handoff.reason_codes)) != len(
        handoff.reason_codes
    ):
        violations.append("DUPLICATE_REASON_CODE")

    if len(set(handoff.risk_flags)) != len(handoff.risk_flags):
        violations.append("DUPLICATE_RISK_FLAG")

    if (
        handoff.handoff_state
        in {
            NarrativeHandoffState.REVIEW_REQUIRED,
            NarrativeHandoffState.BLOCKED_PENDING_EVIDENCE,
        }
        and not handoff.risk_flags
    ):
        violations.append("NON_READY_HANDOFF_REQUIRES_RISK_FLAG")

    return tuple(violations)


def assert_valid_narrative_review_handoff(
    handoff: NarrativeReviewHandoff,
) -> None:
    """Raise when narrative handoff metadata is invalid."""

    violations = validate_narrative_review_handoff(handoff)

    if violations:
        raise NarrativeHandoffViolation(";".join(violations))
