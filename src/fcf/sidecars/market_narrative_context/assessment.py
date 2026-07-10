"""Deterministic narrative risk and evidence assessment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class NarrativeAssessmentViolation(ValueError):
    """Raised when narrative assessment input is invalid."""


class NarrativeClaimPolarity(str, Enum):
    """Normalized claim polarity used only for comparison."""

    SUPPORTS = "SUPPORTS"
    OPPOSES = "OPPOSES"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class NarrativeFreshnessState(str, Enum):
    """Deterministic freshness classification."""

    FRESH = "FRESH"
    STALE = "STALE"


class NarrativeAssessmentDisposition(str, Enum):
    """Deterministic assessment disposition."""

    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class NarrativeAssessmentInput:
    """Immutable input for deterministic narrative assessment."""

    narrative_artifact_id: str
    target_artifact_id: str
    narrative_polarity: NarrativeClaimPolarity
    target_polarity: NarrativeClaimPolarity
    narrative_observed_at_utc: str
    target_observed_at_utc: str
    reference_time_utc: str
    max_age_hours: int
    narrative_evidence_reference_ids: tuple[str, ...] = ()
    target_evidence_reference_ids: tuple[str, ...] = ()
    narrative_uncertainty_flags: tuple[str, ...] = ()
    target_uncertainty_flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class NarrativeAssessmentResult:
    """Deterministic assessment result without truth inference."""

    narrative_artifact_id: str
    target_artifact_id: str
    disposition: NarrativeAssessmentDisposition
    contradiction_detected: bool
    uncertainty_detected: bool
    narrative_freshness_state: NarrativeFreshnessState
    target_freshness_state: NarrativeFreshnessState
    evidence_gap_detected: bool
    shared_evidence_reference_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    risk_flags: tuple[str, ...]
    truth_status: str = "UNDETERMINED"
    operator_review_required: bool = True
    original_conclusions_preserved: bool = True
    automatic_truth_decision_allowed: bool = False
    automatic_conclusion_replacement_allowed: bool = False
    trade_action_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic serialized result."""

        return {
            "narrative_artifact_id": self.narrative_artifact_id,
            "target_artifact_id": self.target_artifact_id,
            "disposition": self.disposition.value,
            "contradiction_detected": self.contradiction_detected,
            "uncertainty_detected": self.uncertainty_detected,
            "narrative_freshness_state": (
                self.narrative_freshness_state.value
            ),
            "target_freshness_state": (
                self.target_freshness_state.value
            ),
            "evidence_gap_detected": self.evidence_gap_detected,
            "shared_evidence_reference_ids": list(
                self.shared_evidence_reference_ids
            ),
            "reason_codes": list(self.reason_codes),
            "risk_flags": list(self.risk_flags),
            "truth_status": self.truth_status,
            "operator_review_required": (
                self.operator_review_required
            ),
            "original_conclusions_preserved": (
                self.original_conclusions_preserved
            ),
            "automatic_truth_decision_allowed": (
                self.automatic_truth_decision_allowed
            ),
            "automatic_conclusion_replacement_allowed": (
                self.automatic_conclusion_replacement_allowed
            ),
            "trade_action_allowed": self.trade_action_allowed,
        }


def _parse_utc(value: str) -> datetime | None:
    if not value.endswith("Z"):
        return None

    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return None

    if parsed.utcoffset() is None:
        return None

    return parsed


def _valid_identifier(value: str) -> bool:
    return bool(_ID_PATTERN.fullmatch(value))


def validate_assessment_input(
    assessment: NarrativeAssessmentInput,
) -> tuple[str, ...]:
    """Return deterministic input violations."""

    violations: list[str] = []

    if not _valid_identifier(assessment.narrative_artifact_id):
        violations.append("INVALID_NARRATIVE_ARTIFACT_ID")

    if not _valid_identifier(assessment.target_artifact_id):
        violations.append("INVALID_TARGET_ARTIFACT_ID")

    if not isinstance(
        assessment.narrative_polarity,
        NarrativeClaimPolarity,
    ):
        violations.append("INVALID_NARRATIVE_POLARITY")

    if not isinstance(
        assessment.target_polarity,
        NarrativeClaimPolarity,
    ):
        violations.append("INVALID_TARGET_POLARITY")

    narrative_time = _parse_utc(
        assessment.narrative_observed_at_utc
    )
    target_time = _parse_utc(
        assessment.target_observed_at_utc
    )
    reference_time = _parse_utc(assessment.reference_time_utc)

    if narrative_time is None:
        violations.append("INVALID_NARRATIVE_OBSERVED_AT_UTC")

    if target_time is None:
        violations.append("INVALID_TARGET_OBSERVED_AT_UTC")

    if reference_time is None:
        violations.append("INVALID_REFERENCE_TIME_UTC")

    if (
        not isinstance(assessment.max_age_hours, int)
        or isinstance(assessment.max_age_hours, bool)
        or assessment.max_age_hours <= 0
    ):
        violations.append("INVALID_MAX_AGE_HOURS")

    if narrative_time is not None and reference_time is not None:
        if narrative_time > reference_time:
            violations.append(
                "NARRATIVE_OBSERVED_AFTER_REFERENCE"
            )

    if target_time is not None and reference_time is not None:
        if target_time > reference_time:
            violations.append("TARGET_OBSERVED_AFTER_REFERENCE")

    evidence_groups = (
        (
            "NARRATIVE",
            assessment.narrative_evidence_reference_ids,
        ),
        (
            "TARGET",
            assessment.target_evidence_reference_ids,
        ),
    )

    for label, evidence_ids in evidence_groups:
        if len(set(evidence_ids)) != len(evidence_ids):
            violations.append(
                f"DUPLICATE_{label}_EVIDENCE_REFERENCE"
            )

        for evidence_id in evidence_ids:
            if not _valid_identifier(evidence_id):
                violations.append(
                    f"INVALID_{label}_EVIDENCE_REFERENCE"
                )
                break

    uncertainty_groups = (
        (
            "NARRATIVE",
            assessment.narrative_uncertainty_flags,
        ),
        (
            "TARGET",
            assessment.target_uncertainty_flags,
        ),
    )

    for label, uncertainty_flags in uncertainty_groups:
        if len(set(uncertainty_flags)) != len(
            uncertainty_flags
        ):
            violations.append(
                f"DUPLICATE_{label}_UNCERTAINTY_FLAG"
            )

        for uncertainty_flag in uncertainty_flags:
            if not _valid_identifier(uncertainty_flag):
                violations.append(
                    f"INVALID_{label}_UNCERTAINTY_FLAG"
                )
                break

    return tuple(violations)


def assert_valid_assessment_input(
    assessment: NarrativeAssessmentInput,
) -> None:
    """Raise when deterministic assessment input is invalid."""

    violations = validate_assessment_input(assessment)

    if violations:
        raise NarrativeAssessmentViolation(
            ";".join(violations)
        )


def assess_narrative_context(
    assessment: NarrativeAssessmentInput,
) -> NarrativeAssessmentResult:
    """Assess contradiction, uncertainty, freshness, and evidence gaps."""

    assert_valid_assessment_input(assessment)

    narrative_time = _parse_utc(
        assessment.narrative_observed_at_utc
    )
    target_time = _parse_utc(
        assessment.target_observed_at_utc
    )
    reference_time = _parse_utc(assessment.reference_time_utc)

    if (
        narrative_time is None
        or target_time is None
        or reference_time is None
    ):
        raise NarrativeAssessmentViolation(
            "UNEXPECTED_TIMESTAMP_PARSE_FAILURE"
        )

    max_age_seconds = assessment.max_age_hours * 3600

    narrative_age_seconds = (
        reference_time - narrative_time
    ).total_seconds()
    target_age_seconds = (
        reference_time - target_time
    ).total_seconds()

    narrative_freshness = NarrativeFreshnessState.FRESH
    target_freshness = NarrativeFreshnessState.FRESH

    reason_codes: list[str] = []
    risk_flags: list[str] = []

    if narrative_age_seconds > max_age_seconds:
        narrative_freshness = NarrativeFreshnessState.STALE
        risk_flags.append("NARRATIVE_STALE")
    else:
        reason_codes.append("NARRATIVE_FRESH")

    if target_age_seconds > max_age_seconds:
        target_freshness = NarrativeFreshnessState.STALE
        risk_flags.append("TARGET_STALE")
    else:
        reason_codes.append("TARGET_FRESH")

    polarity_pair = {
        assessment.narrative_polarity,
        assessment.target_polarity,
    }

    contradiction_detected = polarity_pair == {
        NarrativeClaimPolarity.SUPPORTS,
        NarrativeClaimPolarity.OPPOSES,
    }

    if contradiction_detected:
        risk_flags.append("CONTRADICTION_DETECTED")
    elif (
        assessment.narrative_polarity
        == assessment.target_polarity
        and assessment.narrative_polarity
        is not NarrativeClaimPolarity.UNKNOWN
    ):
        reason_codes.append("POLARITY_ALIGNED")

    uncertainty_detected = (
        assessment.narrative_polarity
        is NarrativeClaimPolarity.UNKNOWN
        or assessment.target_polarity
        is NarrativeClaimPolarity.UNKNOWN
        or bool(assessment.narrative_uncertainty_flags)
        or bool(assessment.target_uncertainty_flags)
    )

    if uncertainty_detected:
        risk_flags.append("UNCERTAINTY_PRESENT")
    else:
        reason_codes.append("NO_EXPLICIT_UNCERTAINTY")

    narrative_evidence = set(
        assessment.narrative_evidence_reference_ids
    )
    target_evidence = set(
        assessment.target_evidence_reference_ids
    )

    shared_evidence = tuple(
        sorted(narrative_evidence & target_evidence)
    )

    evidence_gap_detected = False

    if not narrative_evidence:
        evidence_gap_detected = True
        risk_flags.append("NARRATIVE_EVIDENCE_MISSING")

    if not target_evidence:
        evidence_gap_detected = True
        risk_flags.append("TARGET_EVIDENCE_MISSING")

    if narrative_evidence and target_evidence:
        if shared_evidence:
            reason_codes.append("EVIDENCE_REFERENCE_OVERLAP")
        else:
            evidence_gap_detected = True
            risk_flags.append("NO_SHARED_EVIDENCE_REFERENCE")

    stale_detected = (
        narrative_freshness is NarrativeFreshnessState.STALE
        or target_freshness is NarrativeFreshnessState.STALE
    )

    if stale_detected or evidence_gap_detected:
        disposition = NarrativeAssessmentDisposition.BLOCKED
    elif contradiction_detected or uncertainty_detected:
        disposition = (
            NarrativeAssessmentDisposition.REVIEW_REQUIRED
        )
    else:
        disposition = (
            NarrativeAssessmentDisposition.READY_FOR_REVIEW
        )

    reason_codes.append("OPERATOR_REVIEW_REQUIRED")

    return NarrativeAssessmentResult(
        narrative_artifact_id=assessment.narrative_artifact_id,
        target_artifact_id=assessment.target_artifact_id,
        disposition=disposition,
        contradiction_detected=contradiction_detected,
        uncertainty_detected=uncertainty_detected,
        narrative_freshness_state=narrative_freshness,
        target_freshness_state=target_freshness,
        evidence_gap_detected=evidence_gap_detected,
        shared_evidence_reference_ids=shared_evidence,
        reason_codes=tuple(reason_codes),
        risk_flags=tuple(risk_flags),
    )
