"""ARCHIVE-CORRELATION-ROLLUP-APP-1 D1.

Read-only Correlation_ID rollup contract helpers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


REQUIRED_FIELDS = (
    "correlation_id",
    "artifact_path",
    "artifact_type",
    "source_app",
    "source_phase",
    "validation_state",
    "safety_state",
    "operator_review_state",
)

ALLOWED_SAFETY_STATES = frozenset(
    {
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
    }
)

ALLOWED_OPERATOR_REVIEW_STATES = frozenset(
    {
        "review_required",
        "review_pending",
        "review_completed",
        "blocked",
    }
)


@dataclass(frozen=True)
class CorrelationRollupItem:
    correlation_id: str
    artifact_path: str
    artifact_type: str
    source_app: str
    source_phase: str
    validation_state: str
    safety_state: str
    operator_review_state: str


def validate_rollup_item(item: CorrelationRollupItem) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    for field_name in REQUIRED_FIELDS:
        value = getattr(item, field_name)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"missing_or_empty:{field_name}")

    if item.safety_state not in ALLOWED_SAFETY_STATES:
        issues.append("invalid_safety_state")

    if item.operator_review_state not in ALLOWED_OPERATOR_REVIEW_STATES:
        issues.append("invalid_operator_review_state")

    return (not issues, tuple(issues))


def build_rollup_index(items: Iterable[CorrelationRollupItem]) -> dict[str, tuple[CorrelationRollupItem, ...]]:
    index: dict[str, list[CorrelationRollupItem]] = {}

    for item in items:
        valid, issues = validate_rollup_item(item)
        if not valid:
            raise ValueError(",".join(issues))

        index.setdefault(item.correlation_id, []).append(item)

    return {key: tuple(value) for key, value in index.items()}
