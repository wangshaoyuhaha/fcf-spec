"""Deterministic narrative-to-research linkage rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class NarrativeLinkageViolation(ValueError):
    """Raised when narrative linkage metadata is invalid."""


class NarrativeLinkageDisposition(str, Enum):
    """Deterministic metadata-linkage disposition."""

    LINKED = "LINKED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class NarrativeLinkageRequest:
    """Immutable narrative and target artifact linkage request."""

    narrative_artifact_id: str
    target_artifact_id: str
    narrative_correlation_id: str
    target_correlation_id: str
    narrative_research_run_id: str
    target_research_run_id: str
    narrative_asset_type: str
    target_asset_type: str
    narrative_symbol: str
    target_symbol: str
    narrative_evidence_reference_ids: tuple[str, ...] = ()
    target_evidence_reference_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic request representation."""

        return {
            "narrative_artifact_id": self.narrative_artifact_id,
            "target_artifact_id": self.target_artifact_id,
            "narrative_correlation_id": (
                self.narrative_correlation_id
            ),
            "target_correlation_id": self.target_correlation_id,
            "narrative_research_run_id": (
                self.narrative_research_run_id
            ),
            "target_research_run_id": self.target_research_run_id,
            "narrative_asset_type": self.narrative_asset_type,
            "target_asset_type": self.target_asset_type,
            "narrative_symbol": self.narrative_symbol,
            "target_symbol": self.target_symbol,
            "narrative_evidence_reference_ids": list(
                self.narrative_evidence_reference_ids
            ),
            "target_evidence_reference_ids": list(
                self.target_evidence_reference_ids
            ),
        }


@dataclass(frozen=True)
class NarrativeLinkageResult:
    """Deterministic narrative linkage result."""

    narrative_artifact_id: str
    target_artifact_id: str
    disposition: NarrativeLinkageDisposition
    reason_codes: tuple[str, ...]
    risk_flags: tuple[str, ...]
    shared_evidence_reference_ids: tuple[str, ...]
    truth_status: str = "UNDETERMINED"
    operator_review_required: bool = True
    original_conclusions_preserved: bool = True
    automatic_truth_decision_allowed: bool = False
    automatic_conclusion_replacement_allowed: bool = False
    trade_action_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic result representation."""

        return {
            "narrative_artifact_id": self.narrative_artifact_id,
            "target_artifact_id": self.target_artifact_id,
            "disposition": self.disposition.value,
            "reason_codes": list(self.reason_codes),
            "risk_flags": list(self.risk_flags),
            "shared_evidence_reference_ids": list(
                self.shared_evidence_reference_ids
            ),
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


def _is_valid_identifier(value: str) -> bool:
    return bool(_ID_PATTERN.fullmatch(value))


def validate_linkage_request(
    request: NarrativeLinkageRequest,
) -> tuple[str, ...]:
    """Return deterministic linkage-request violations."""

    violations: list[str] = []

    identifier_fields = (
        ("narrative_artifact_id", request.narrative_artifact_id),
        ("target_artifact_id", request.target_artifact_id),
        (
            "narrative_correlation_id",
            request.narrative_correlation_id,
        ),
        ("target_correlation_id", request.target_correlation_id),
        (
            "narrative_research_run_id",
            request.narrative_research_run_id,
        ),
        (
            "target_research_run_id",
            request.target_research_run_id,
        ),
    )

    for field_name, value in identifier_fields:
        if not _is_valid_identifier(value):
            violations.append(
                f"INVALID_IDENTIFIER:{field_name}"
            )

    text_fields = (
        ("narrative_asset_type", request.narrative_asset_type),
        ("target_asset_type", request.target_asset_type),
        ("narrative_symbol", request.narrative_symbol),
        ("target_symbol", request.target_symbol),
    )

    for field_name, value in text_fields:
        if not value or not value.strip():
            violations.append(f"EMPTY_FIELD:{field_name}")

    if len(set(request.narrative_evidence_reference_ids)) != len(
        request.narrative_evidence_reference_ids
    ):
        violations.append(
            "DUPLICATE_NARRATIVE_EVIDENCE_REFERENCE"
        )

    if len(set(request.target_evidence_reference_ids)) != len(
        request.target_evidence_reference_ids
    ):
        violations.append(
            "DUPLICATE_TARGET_EVIDENCE_REFERENCE"
        )

    all_evidence_ids = (
        request.narrative_evidence_reference_ids
        + request.target_evidence_reference_ids
    )

    for evidence_id in all_evidence_ids:
        if not _is_valid_identifier(evidence_id):
            violations.append("INVALID_EVIDENCE_REFERENCE_ID")
            break

    return tuple(violations)


def assert_valid_linkage_request(
    request: NarrativeLinkageRequest,
) -> None:
    """Raise when linkage metadata is invalid."""

    violations = validate_linkage_request(request)

    if violations:
        raise NarrativeLinkageViolation(";".join(violations))


def evaluate_narrative_linkage(
    request: NarrativeLinkageRequest,
) -> NarrativeLinkageResult:
    """Evaluate deterministic metadata linkage without truth inference."""

    assert_valid_linkage_request(request)

    reason_codes: list[str] = []
    risk_flags: list[str] = []
    identity_match = True

    if (
        request.narrative_correlation_id
        == request.target_correlation_id
    ):
        reason_codes.append("CORRELATION_ID_MATCH")
    else:
        identity_match = False
        risk_flags.append("CORRELATION_ID_MISMATCH")

    if (
        request.narrative_research_run_id
        == request.target_research_run_id
    ):
        reason_codes.append("RESEARCH_RUN_ID_MATCH")
    else:
        identity_match = False
        risk_flags.append("RESEARCH_RUN_ID_MISMATCH")

    if (
        request.narrative_asset_type.strip().upper()
        == request.target_asset_type.strip().upper()
    ):
        reason_codes.append("ASSET_TYPE_MATCH")
    else:
        identity_match = False
        risk_flags.append("ASSET_TYPE_MISMATCH")

    if (
        request.narrative_symbol.strip().upper()
        == request.target_symbol.strip().upper()
    ):
        reason_codes.append("SYMBOL_MATCH")
    else:
        identity_match = False
        risk_flags.append("SYMBOL_MISMATCH")

    shared_evidence = tuple(
        sorted(
            set(request.narrative_evidence_reference_ids)
            & set(request.target_evidence_reference_ids)
        )
    )

    if shared_evidence:
        reason_codes.append("EVIDENCE_REFERENCE_OVERLAP")
    else:
        risk_flags.append("NO_SHARED_EVIDENCE_REFERENCE")

    reason_codes.append("OPERATOR_REVIEW_REQUIRED")

    if not identity_match:
        disposition = NarrativeLinkageDisposition.BLOCKED
    elif not shared_evidence:
        disposition = NarrativeLinkageDisposition.REVIEW_REQUIRED
    else:
        disposition = NarrativeLinkageDisposition.LINKED

    return NarrativeLinkageResult(
        narrative_artifact_id=request.narrative_artifact_id,
        target_artifact_id=request.target_artifact_id,
        disposition=disposition,
        reason_codes=tuple(reason_codes),
        risk_flags=tuple(risk_flags),
        shared_evidence_reference_ids=shared_evidence,
    )
