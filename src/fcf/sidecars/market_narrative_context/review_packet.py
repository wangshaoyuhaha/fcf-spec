"""Paper-only market narrative review packet."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .assessment import NarrativeAssessmentDisposition
from .assessment import NarrativeAssessmentResult


_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class NarrativeReviewPacketViolation(ValueError):
    """Raised when a narrative review packet is invalid."""


class NarrativeReviewPacketState(str, Enum):
    """Paper-only operator review packet state."""

    READY_FOR_OPERATOR_REVIEW = "READY_FOR_OPERATOR_REVIEW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED_PENDING_EVIDENCE = "BLOCKED_PENDING_EVIDENCE"


@dataclass(frozen=True)
class NarrativeReviewPacket:
    """Immutable paper-only narrative review packet."""

    packet_id: str
    correlation_id: str
    research_run_id: str
    narrative_artifact_id: str
    target_artifact_id: str
    packet_state: NarrativeReviewPacketState
    assessment_disposition: str
    contradiction_detected: bool
    uncertainty_detected: bool
    narrative_freshness_state: str
    target_freshness_state: str
    evidence_gap_detected: bool
    shared_evidence_reference_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    risk_flags: tuple[str, ...]
    review_status: str = "PENDING_OPERATOR_REVIEW"
    truth_status: str = "UNDETERMINED"
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False
    original_conclusions_preserved: bool = True
    no_execution_receipt: bool = True
    automatic_truth_decision_allowed: bool = False
    automatic_conclusion_replacement_allowed: bool = False
    trade_action_allowed: bool = False
    real_execution_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic packet representation."""

        return {
            "packet_id": self.packet_id,
            "correlation_id": self.correlation_id,
            "research_run_id": self.research_run_id,
            "narrative_artifact_id": self.narrative_artifact_id,
            "target_artifact_id": self.target_artifact_id,
            "packet_state": self.packet_state.value,
            "assessment_disposition": self.assessment_disposition,
            "contradiction_detected": self.contradiction_detected,
            "uncertainty_detected": self.uncertainty_detected,
            "narrative_freshness_state": (
                self.narrative_freshness_state
            ),
            "target_freshness_state": self.target_freshness_state,
            "evidence_gap_detected": self.evidence_gap_detected,
            "shared_evidence_reference_ids": list(
                self.shared_evidence_reference_ids
            ),
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


def build_narrative_review_packet(
    packet_id: str,
    correlation_id: str,
    research_run_id: str,
    assessment: NarrativeAssessmentResult,
) -> NarrativeReviewPacket:
    """Build a paper-only packet from a deterministic assessment."""

    if assessment.disposition is NarrativeAssessmentDisposition.BLOCKED:
        packet_state = (
            NarrativeReviewPacketState.BLOCKED_PENDING_EVIDENCE
        )
    elif (
        assessment.disposition
        is NarrativeAssessmentDisposition.REVIEW_REQUIRED
    ):
        packet_state = NarrativeReviewPacketState.REVIEW_REQUIRED
    else:
        packet_state = (
            NarrativeReviewPacketState.READY_FOR_OPERATOR_REVIEW
        )

    packet = NarrativeReviewPacket(
        packet_id=packet_id,
        correlation_id=correlation_id,
        research_run_id=research_run_id,
        narrative_artifact_id=assessment.narrative_artifact_id,
        target_artifact_id=assessment.target_artifact_id,
        packet_state=packet_state,
        assessment_disposition=assessment.disposition.value,
        contradiction_detected=assessment.contradiction_detected,
        uncertainty_detected=assessment.uncertainty_detected,
        narrative_freshness_state=(
            assessment.narrative_freshness_state.value
        ),
        target_freshness_state=(
            assessment.target_freshness_state.value
        ),
        evidence_gap_detected=assessment.evidence_gap_detected,
        shared_evidence_reference_ids=(
            assessment.shared_evidence_reference_ids
        ),
        reason_codes=assessment.reason_codes,
        risk_flags=assessment.risk_flags,
    )

    assert_valid_narrative_review_packet(packet)
    return packet


def validate_narrative_review_packet(
    packet: NarrativeReviewPacket,
) -> tuple[str, ...]:
    """Return deterministic packet violations."""

    violations: list[str] = []

    identifier_fields = (
        ("packet_id", packet.packet_id),
        ("correlation_id", packet.correlation_id),
        ("research_run_id", packet.research_run_id),
        ("narrative_artifact_id", packet.narrative_artifact_id),
        ("target_artifact_id", packet.target_artifact_id),
    )

    for field_name, value in identifier_fields:
        if not _valid_identifier(value):
            violations.append(f"INVALID_IDENTIFIER:{field_name}")

    if not isinstance(packet.packet_state, NarrativeReviewPacketState):
        violations.append("INVALID_PACKET_STATE")

    if packet.review_status != "PENDING_OPERATOR_REVIEW":
        violations.append("INVALID_REVIEW_STATUS")

    if packet.truth_status != "UNDETERMINED":
        violations.append("INVALID_TRUTH_STATUS")

    required_true = (
        "operator_review_required",
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
        if getattr(packet, field_name) is not True:
            violations.append(f"REQUIRED_TRUE:{field_name}")

    for field_name in required_false:
        if getattr(packet, field_name) is not False:
            violations.append(f"REQUIRED_FALSE:{field_name}")

    if len(set(packet.reason_codes)) != len(packet.reason_codes):
        violations.append("DUPLICATE_REASON_CODE")

    if len(set(packet.risk_flags)) != len(packet.risk_flags):
        violations.append("DUPLICATE_RISK_FLAG")

    if (
        packet.packet_state
        is NarrativeReviewPacketState.BLOCKED_PENDING_EVIDENCE
        and not packet.risk_flags
    ):
        violations.append("BLOCKED_PACKET_REQUIRES_RISK_FLAG")

    return tuple(violations)


def assert_valid_narrative_review_packet(
    packet: NarrativeReviewPacket,
) -> None:
    """Raise when a paper-only review packet is invalid."""

    violations = validate_narrative_review_packet(packet)

    if violations:
        raise NarrativeReviewPacketViolation(
            ";".join(violations)
        )
