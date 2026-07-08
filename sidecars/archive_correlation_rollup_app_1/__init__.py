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

ELIGIBLE_ARTIFACT_TYPES = frozenset(
    {
        "final_current_state",
        "control_center",
        "archive_report",
        "backend_handoff",
        "validation_summary",
        "project_prompt",
    }
)


def classify_artifact_path(path: str) -> str:
    normalized = path.replace("\\", "/")

    if normalized.endswith("docs/FCF_PROJECT_CONTROL_CENTER.md"):
        return "control_center"

    name = normalized.rsplit("/", 1)[-1]

    if name.startswith("FCF_CURRENT_STATE_") and name.endswith(".md"):
        return "final_current_state"

    if "ARCHITECTURE_GAP_AUDIT_REPORT" in name or "AUDIT_REPORT" in name:
        return "archive_report"

    if "BACKEND_HANDOFF" in name or "HANDOFF" in name:
        return "backend_handoff"

    if "VALIDATION" in name and name.endswith(".md"):
        return "validation_summary"

    if "NEW_WINDOW_CHAT_PROMPT" in name:
        return "project_prompt"

    return "unknown"


def is_rollup_source_path(path: str) -> bool:
    return classify_artifact_path(path) in ELIGIBLE_ARTIFACT_TYPES


def discover_rollup_source_paths(paths: Iterable[str]) -> tuple[str, ...]:
    eligible = [path for path in paths if is_rollup_source_path(path)]
    return tuple(sorted(dict.fromkeys(eligible)))

ALLOWED_ROLLUP_SCOPES = frozenset(
    {
        "archive",
        "report",
        "final_current_state",
        "control_center",
        "handoff",
        "validation",
    }
)

ALLOWED_TRACE_STATES = frozenset(
    {
        "trace_ready",
        "trace_partial",
        "trace_blocked",
    }
)


@dataclass(frozen=True)
class CorrelationRollupRecord:
    correlation_id: str
    artifact_path: str
    artifact_type: str
    source_app: str
    source_phase: str
    validation_state: str
    safety_state: str
    operator_review_state: str
    rollup_scope: str
    trace_state: str


def infer_rollup_scope(artifact_type: str) -> str:
    mapping = {
        "archive_report": "archive",
        "final_current_state": "final_current_state",
        "control_center": "control_center",
        "backend_handoff": "handoff",
        "validation_summary": "validation",
        "project_prompt": "handoff",
    }
    return mapping.get(artifact_type, "report")


def build_correlation_id(source_app: str, source_phase: str, artifact_type: str) -> str:
    parts = (source_app, source_phase, artifact_type)
    normalized = "-".join(part.strip().upper().replace("_", "-") for part in parts if part.strip())
    return f"CORR-{normalized}"


def build_rollup_record(
    artifact_path: str,
    source_app: str,
    source_phase: str,
    validation_state: str = "passed",
    safety_state: str = "read_only",
    operator_review_state: str = "review_required",
    trace_state: str = "trace_ready",
) -> CorrelationRollupRecord:
    artifact_type = classify_artifact_path(artifact_path)
    rollup_scope = infer_rollup_scope(artifact_type)
    correlation_id = build_correlation_id(source_app, source_phase, artifact_type)

    record = CorrelationRollupRecord(
        correlation_id=correlation_id,
        artifact_path=artifact_path,
        artifact_type=artifact_type,
        source_app=source_app,
        source_phase=source_phase,
        validation_state=validation_state,
        safety_state=safety_state,
        operator_review_state=operator_review_state,
        rollup_scope=rollup_scope,
        trace_state=trace_state,
    )

    valid, issues = validate_rollup_record(record)
    if not valid:
        raise ValueError(",".join(issues))

    return record


def validate_rollup_record(record: CorrelationRollupRecord) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    base_item = CorrelationRollupItem(
        correlation_id=record.correlation_id,
        artifact_path=record.artifact_path,
        artifact_type=record.artifact_type,
        source_app=record.source_app,
        source_phase=record.source_phase,
        validation_state=record.validation_state,
        safety_state=record.safety_state,
        operator_review_state=record.operator_review_state,
    )

    base_valid, base_issues = validate_rollup_item(base_item)
    if not base_valid:
        issues.extend(base_issues)

    if record.artifact_type == "unknown":
        issues.append("unknown_artifact_type")

    if record.rollup_scope not in ALLOWED_ROLLUP_SCOPES:
        issues.append("invalid_rollup_scope")

    if record.trace_state not in ALLOWED_TRACE_STATES:
        issues.append("invalid_trace_state")

    return (not issues, tuple(issues))
