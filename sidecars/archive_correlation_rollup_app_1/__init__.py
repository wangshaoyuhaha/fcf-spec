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

@dataclass(frozen=True)
class CorrelationTraceSummary:
    correlation_id: str
    record_count: int
    artifact_types: tuple[str, ...]
    source_apps: tuple[str, ...]
    rollup_scopes: tuple[str, ...]
    trace_states: tuple[str, ...]
    has_blocked_trace: bool
    has_partial_trace: bool
    operator_review_required: bool
    summary_state: str


def _unique_sorted(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(dict.fromkeys(values)))


def infer_summary_state(trace_states: Iterable[str]) -> str:
    states = set(trace_states)
    if "trace_blocked" in states:
        return "blocked"
    if "trace_partial" in states:
        return "partial"
    return "complete"


def build_trace_summary(
    correlation_id: str,
    records: Iterable[CorrelationRollupRecord],
) -> CorrelationTraceSummary:
    record_tuple = tuple(records)
    if not record_tuple:
        raise ValueError("empty_rollup_records")

    for record in record_tuple:
        valid, issues = validate_rollup_record(record)
        if not valid:
            raise ValueError(",".join(issues))
        if record.correlation_id != correlation_id:
            raise ValueError("correlation_id_mismatch")

    trace_states = _unique_sorted(record.trace_state for record in record_tuple)

    return CorrelationTraceSummary(
        correlation_id=correlation_id,
        record_count=len(record_tuple),
        artifact_types=_unique_sorted(record.artifact_type for record in record_tuple),
        source_apps=_unique_sorted(record.source_app for record in record_tuple),
        rollup_scopes=_unique_sorted(record.rollup_scope for record in record_tuple),
        trace_states=trace_states,
        has_blocked_trace="trace_blocked" in trace_states,
        has_partial_trace="trace_partial" in trace_states,
        operator_review_required=any(
            record.operator_review_state == "review_required"
            for record in record_tuple
        ),
        summary_state=infer_summary_state(trace_states),
    )


def build_trace_summaries(
    records: Iterable[CorrelationRollupRecord],
) -> dict[str, CorrelationTraceSummary]:
    grouped: dict[str, list[CorrelationRollupRecord]] = {}

    for record in records:
        valid, issues = validate_rollup_record(record)
        if not valid:
            raise ValueError(",".join(issues))
        grouped.setdefault(record.correlation_id, []).append(record)

    return {
        correlation_id: build_trace_summary(correlation_id, grouped_records)
        for correlation_id, grouped_records in sorted(grouped.items())
    }

@dataclass(frozen=True)
class CorrelationRollupPacket:
    packet_id: str
    created_at_utc: str
    source_app: str
    summary_count: int
    record_count: int
    summaries: tuple[CorrelationTraceSummary, ...]
    safety_state: str
    operator_review_required: bool
    no_execution_statement: str
    release_allowed: bool
    deploy_allowed: bool


def build_rollup_packet(
    packet_id: str,
    records: Iterable[CorrelationRollupRecord],
    created_at_utc: str,
    source_app: str = "ARCHIVE-CORRELATION-ROLLUP-APP-1",
) -> CorrelationRollupPacket:
    record_tuple = tuple(records)
    if not record_tuple:
        raise ValueError("empty_rollup_packet_records")

    summaries = tuple(build_trace_summaries(record_tuple).values())
    record_count = sum(summary.record_count for summary in summaries)

    packet = CorrelationRollupPacket(
        packet_id=packet_id,
        created_at_utc=created_at_utc,
        source_app=source_app,
        summary_count=len(summaries),
        record_count=record_count,
        summaries=summaries,
        safety_state="paper_only_local_read_only_sidecar_only",
        operator_review_required=True,
        no_execution_statement="This packet is paper-only and cannot execute trades.",
        release_allowed=False,
        deploy_allowed=False,
    )

    valid, issues = validate_rollup_packet(packet)
    if not valid:
        raise ValueError(",".join(issues))

    return packet


def validate_rollup_packet(packet: CorrelationRollupPacket) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    if not packet.packet_id.strip():
        issues.append("missing_packet_id")

    if not packet.created_at_utc.strip():
        issues.append("missing_created_at_utc")

    if packet.summary_count != len(packet.summaries):
        issues.append("summary_count_mismatch")

    if packet.record_count != sum(summary.record_count for summary in packet.summaries):
        issues.append("record_count_mismatch")

    if packet.safety_state != "paper_only_local_read_only_sidecar_only":
        issues.append("invalid_packet_safety_state")

    if packet.operator_review_required is not True:
        issues.append("operator_review_not_required")

    if packet.release_allowed is not False:
        issues.append("release_allowed_must_be_false")

    if packet.deploy_allowed is not False:
        issues.append("deploy_allowed_must_be_false")

    if "cannot execute trades" not in packet.no_execution_statement:
        issues.append("missing_no_execution_statement")

    return (not issues, tuple(issues))


def packet_has_blocked_trace(packet: CorrelationRollupPacket) -> bool:
    return any(summary.has_blocked_trace for summary in packet.summaries)


def packet_has_partial_trace(packet: CorrelationRollupPacket) -> bool:
    return any(summary.has_partial_trace for summary in packet.summaries)
