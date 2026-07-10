"""Registered narrative source schema and source trust levels."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from enum import IntEnum
import re

from .contract import ALLOWED_INPUT_ARTIFACT_TYPES


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class NarrativeSourceSchemaViolation(ValueError):
    """Raised when a registered narrative source is invalid."""


class NarrativeSourceTrustLevel(IntEnum):
    """Deterministic trust classification for registered sources."""

    LEVEL_0_LOCAL_DETERMINISTIC = 0
    LEVEL_1_PROJECT_ARCHIVED = 1
    LEVEL_2_OPERATOR_PROVIDED = 2
    LEVEL_3_EXTERNAL_REGISTERED = 3


@dataclass(frozen=True)
class NarrativeSourceRecord:
    """Immutable registered narrative source metadata."""

    artifact_id: str
    artifact_type: str
    source_trust_level: NarrativeSourceTrustLevel
    content_sha256: str
    registered_at_utc: str
    correlation_id: str
    research_run_id: str
    evidence_reference_ids: tuple[str, ...] = ()
    local_snapshot_present: bool = True
    operator_review_required: bool = True
    original_content_preserved: bool = True
    live_fetch_allowed: bool = False
    automatic_truth_decision_allowed: bool = False

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic serialized source record."""

        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "source_trust_level": int(self.source_trust_level),
            "source_trust_level_name": self.source_trust_level.name,
            "content_sha256": self.content_sha256,
            "registered_at_utc": self.registered_at_utc,
            "correlation_id": self.correlation_id,
            "research_run_id": self.research_run_id,
            "evidence_reference_ids": list(
                self.evidence_reference_ids
            ),
            "local_snapshot_present": self.local_snapshot_present,
            "operator_review_required": self.operator_review_required,
            "original_content_preserved": (
                self.original_content_preserved
            ),
            "live_fetch_allowed": self.live_fetch_allowed,
            "automatic_truth_decision_allowed": (
                self.automatic_truth_decision_allowed
            ),
        }


def _is_valid_identifier(value: str) -> bool:
    return bool(_ID_PATTERN.fullmatch(value))


def _is_valid_utc_timestamp(value: str) -> bool:
    if not value.endswith("Z"):
        return False

    try:
        parsed = datetime.fromisoformat(
            value[:-1] + "+00:00"
        )
    except ValueError:
        return False

    return parsed.utcoffset() == timedelta(0)


def validate_source_record(
    record: NarrativeSourceRecord,
) -> tuple[str, ...]:
    """Return deterministic source-schema violations."""

    violations: list[str] = []

    if not _is_valid_identifier(record.artifact_id):
        violations.append("INVALID_ARTIFACT_ID")

    if record.artifact_type not in ALLOWED_INPUT_ARTIFACT_TYPES:
        violations.append("UNREGISTERED_ARTIFACT_TYPE")

    if not isinstance(
        record.source_trust_level,
        NarrativeSourceTrustLevel,
    ):
        violations.append("INVALID_SOURCE_TRUST_LEVEL")

    if not _SHA256_PATTERN.fullmatch(record.content_sha256):
        violations.append("INVALID_CONTENT_SHA256")

    if not _is_valid_utc_timestamp(record.registered_at_utc):
        violations.append("INVALID_REGISTERED_AT_UTC")

    if not _is_valid_identifier(record.correlation_id):
        violations.append("INVALID_CORRELATION_ID")

    if not _is_valid_identifier(record.research_run_id):
        violations.append("INVALID_RESEARCH_RUN_ID")

    if len(set(record.evidence_reference_ids)) != len(
        record.evidence_reference_ids
    ):
        violations.append("DUPLICATE_EVIDENCE_REFERENCE_ID")

    for evidence_id in record.evidence_reference_ids:
        if not _is_valid_identifier(evidence_id):
            violations.append("INVALID_EVIDENCE_REFERENCE_ID")
            break

    if record.local_snapshot_present is not True:
        violations.append("LOCAL_SNAPSHOT_REQUIRED")

    if record.operator_review_required is not True:
        violations.append("OPERATOR_REVIEW_REQUIRED")

    if record.original_content_preserved is not True:
        violations.append("ORIGINAL_CONTENT_MUST_BE_PRESERVED")

    if record.live_fetch_allowed is not False:
        violations.append("LIVE_FETCH_FORBIDDEN")

    if record.automatic_truth_decision_allowed is not False:
        violations.append("AUTOMATIC_TRUTH_DECISION_FORBIDDEN")

    if (
        record.source_trust_level
        is NarrativeSourceTrustLevel.LEVEL_3_EXTERNAL_REGISTERED
        and not record.evidence_reference_ids
    ):
        violations.append(
            "EXTERNAL_SOURCE_EVIDENCE_REFERENCE_REQUIRED"
        )

    return tuple(violations)


def assert_valid_source_record(
    record: NarrativeSourceRecord,
) -> None:
    """Raise when a registered narrative source is invalid."""

    violations = validate_source_record(record)

    if violations:
        raise NarrativeSourceSchemaViolation(
            ";".join(violations)
        )
