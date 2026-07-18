from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .read_model import ConsoleArtifactRecord, ConsoleReadModel
from .research_workspace import RESEARCH_WORKSPACE_ROUTE_REGISTRY


_D4_IMPLEMENTED_PATHS = frozenset(
    {
        "/",
        "/data",
        "/stocks",
        "/runs",
        "/ai-comparison",
        "/risk",
        "/validation",
        "/review",
        "/reports",
        "/governance",
        "/audit",
    }
)
_DATA_ARTIFACT_TYPES = frozenset({"data_snapshot", "data_quality"})
_RESEARCH_RUN_ARTIFACT_TYPES = frozenset(
    {"research_run", "workflow_status"}
)
_AI_COMPARISON_ARTIFACT_TYPES = frozenset(
    {"ai_explanation", "ai_evaluation"}
)
_GOVERNANCE_ARTIFACT_TYPES = frozenset(
    {"factor_governance_projection", "model_governance", "policy_snapshot"}
)
_REQUIRED_GOVERNANCE_ARTIFACT_TYPES = frozenset(
    {"model_governance", "policy_snapshot"}
)
_AUDIT_ARTIFACT_TYPES = frozenset(
    {"audit_receipt", "manifest"}
)


@dataclass(frozen=True)
class OverviewWorkspaceModel:
    correlation_id: str
    registered_artifact_count: int
    stock_candidate_count: int
    artifact_type_counts: Mapping[str, int]
    available_workspace_paths: Tuple[str, ...]
    planned_workspace_paths: Tuple[str, ...]
    paper_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if not self.correlation_id.strip():
            raise ValueError("correlation_id is required")
        if self.registered_artifact_count < 0:
            raise ValueError("registered_artifact_count must be non-negative")
        if self.stock_candidate_count < 0:
            raise ValueError("stock_candidate_count must be non-negative")
        if not self.paper_only:
            raise ValueError("overview must remain paper-only")
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")
        object.__setattr__(
            self,
            "artifact_type_counts",
            MappingProxyType(dict(self.artifact_type_counts)),
        )
        object.__setattr__(
            self,
            "available_workspace_paths",
            tuple(self.available_workspace_paths),
        )
        object.__setattr__(
            self,
            "planned_workspace_paths",
            tuple(self.planned_workspace_paths),
        )


@dataclass(frozen=True)
class DataWorkspaceItem:
    artifact_id: str
    artifact_type: str
    relative_path: str
    content_sha256: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.artifact_type not in _DATA_ARTIFACT_TYPES:
            raise ValueError("unsupported Data Workspace artifact type")
        if not self.artifact_id.strip():
            raise ValueError("artifact_id is required")
        if not self.relative_path.strip():
            raise ValueError("relative_path is required")
        if len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a SHA-256 digest")
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


@dataclass(frozen=True)
class DataWorkspaceModel:
    correlation_id: str
    state: str
    items: Tuple[DataWorkspaceItem, ...]
    artifact_type_counts: Mapping[str, int]
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "AVAILABLE",
            "INCOMPLETE",
            "NO_REGISTERED_DATA",
        }:
            raise ValueError("unsupported Data Workspace state")
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "Data Workspace must remain registered-artifact-only "
                "and read-only"
            )
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(
            self,
            "artifact_type_counts",
            MappingProxyType(dict(self.artifact_type_counts)),
        )


def _payload_label(
    payload: Mapping[str, Any],
    keys: Tuple[str, ...],
    default: str,
) -> str:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, (str, int, float, bool)):
            normalized = str(value).strip()
            if normalized:
                return normalized
    return default


@dataclass(frozen=True)
class ResearchRunWorkspaceItem:
    artifact_id: str
    artifact_type: str
    relative_path: str
    content_sha256: str
    run_id: str
    workflow_state: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.artifact_type not in _RESEARCH_RUN_ARTIFACT_TYPES:
            raise ValueError("unsupported Research Runs artifact type")
        if not self.artifact_id.strip():
            raise ValueError("artifact_id is required")
        if not self.relative_path.strip():
            raise ValueError("relative_path is required")
        if len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a SHA-256 digest")
        if not self.run_id.strip():
            raise ValueError("run_id is required")
        if not self.workflow_state.strip():
            raise ValueError("workflow_state is required")
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


@dataclass(frozen=True)
class ResearchRunsWorkspaceModel:
    correlation_id: str
    state: str
    items: Tuple[ResearchRunWorkspaceItem, ...]
    artifact_type_counts: Mapping[str, int]
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "AVAILABLE",
            "INCOMPLETE",
            "NO_REGISTERED_RUNS",
        }:
            raise ValueError("unsupported Research Runs state")
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "Research Runs must remain registered-artifact-only "
                "and read-only"
            )
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(
            self,
            "artifact_type_counts",
            MappingProxyType(dict(self.artifact_type_counts)),
        )


@dataclass(frozen=True)
class AIComparisonItem:
    artifact_id: str
    artifact_type: str
    relative_path: str
    content_sha256: str
    model_label: str
    prompt_version: str
    evaluation_state: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.artifact_type not in _AI_COMPARISON_ARTIFACT_TYPES:
            raise ValueError("unsupported AI Comparison artifact type")
        for field_name in (
            "artifact_id",
            "relative_path",
            "model_label",
            "prompt_version",
            "evaluation_state",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")
        if len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a SHA-256 digest")
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


@dataclass(frozen=True)
class AIComparisonWorkspaceModel:
    correlation_id: str
    state: str
    items: Tuple[AIComparisonItem, ...]
    artifact_type_counts: Mapping[str, int]
    registered_artifact_only: bool = True
    read_only: bool = True
    ai_advisory_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "COMPARISON_READY",
            "INCOMPLETE",
            "NO_REGISTERED_AI_ARTIFACTS",
        }:
            raise ValueError("unsupported AI Comparison state")
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "AI Comparison must remain registered-artifact-only "
                "and read-only"
            )
        if not self.ai_advisory_only:
            raise ValueError("AI must remain advisory-only")
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(
            self,
            "artifact_type_counts",
            MappingProxyType(dict(self.artifact_type_counts)),
        )


@dataclass(frozen=True)
class GovernanceWorkspaceItem:
    artifact_id: str
    artifact_type: str
    relative_path: str
    content_sha256: str
    subject: str
    version: str
    decision: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.artifact_type not in _GOVERNANCE_ARTIFACT_TYPES:
            raise ValueError("unsupported Governance artifact type")
        for field_name in (
            "artifact_id",
            "relative_path",
            "subject",
            "version",
            "decision",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")
        if len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a SHA-256 digest")
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


@dataclass(frozen=True)
class GovernanceWorkspaceModel:
    correlation_id: str
    state: str
    items: Tuple[GovernanceWorkspaceItem, ...]
    artifact_type_counts: Mapping[str, int]
    registered_artifact_only: bool = True
    read_only: bool = True
    deterministic_authority: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "AVAILABLE",
            "INCOMPLETE",
            "NO_REGISTERED_GOVERNANCE",
        }:
            raise ValueError("unsupported Governance state")
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "Governance must remain registered-artifact-only "
                "and read-only"
            )
        if not self.deterministic_authority:
            raise ValueError(
                "Deterministic Engine authority must remain enabled"
            )
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(
            self,
            "artifact_type_counts",
            MappingProxyType(dict(self.artifact_type_counts)),
        )


@dataclass(frozen=True)
class AuditHistoryItem:
    artifact_id: str
    artifact_type: str
    relative_path: str
    content_sha256: str
    event_id: str
    event_time: str
    action: str
    actor: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.artifact_type not in _AUDIT_ARTIFACT_TYPES:
            raise ValueError("unsupported Audit History artifact type")
        for field_name in (
            "artifact_id",
            "relative_path",
            "event_id",
            "event_time",
            "action",
            "actor",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")
        if len(self.content_sha256) != 64:
            raise ValueError("content_sha256 must be a SHA-256 digest")
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )


@dataclass(frozen=True)
class AuditHistoryWorkspaceModel:
    correlation_id: str
    state: str
    items: Tuple[AuditHistoryItem, ...]
    artifact_type_counts: Mapping[str, int]
    registered_artifact_only: bool = True
    read_only: bool = True
    append_only_evidence: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "AVAILABLE",
            "INCOMPLETE",
            "NO_REGISTERED_AUDIT_HISTORY",
        }:
            raise ValueError("unsupported Audit History state")
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "Audit History must remain registered-artifact-only "
                "and read-only"
            )
        if not self.append_only_evidence:
            raise ValueError("audit evidence must remain append-only")
        if not self.operator_review_required:
            raise ValueError("Operator review must remain required")
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(
            self,
            "artifact_type_counts",
            MappingProxyType(dict(self.artifact_type_counts)),
        )


def _type_counts(
    records: Tuple[ConsoleArtifactRecord, ...],
) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.artifact_type] = (
            counts.get(record.artifact_type, 0) + 1
        )
    return MappingProxyType(dict(sorted(counts.items())))


def build_overview_workspace_model(
    read_model: ConsoleReadModel,
) -> OverviewWorkspaceModel:
    available = tuple(
        route.path
        for route in RESEARCH_WORKSPACE_ROUTE_REGISTRY.routes
        if route.path in _D4_IMPLEMENTED_PATHS
    )
    planned = tuple(
        route.path
        for route in RESEARCH_WORKSPACE_ROUTE_REGISTRY.routes
        if route.path not in _D4_IMPLEMENTED_PATHS
    )
    return OverviewWorkspaceModel(
        correlation_id=read_model.correlation_id,
        registered_artifact_count=len(
            read_model.source_artifact_ids
        ),
        stock_candidate_count=len(read_model.candidates),
        artifact_type_counts=_type_counts(
            read_model.artifact_records
        ),
        available_workspace_paths=available,
        planned_workspace_paths=planned,
    )


def build_data_workspace_model(
    read_model: ConsoleReadModel,
) -> DataWorkspaceModel:
    records = tuple(
        record
        for record in read_model.artifact_records
        if record.artifact_type in _DATA_ARTIFACT_TYPES
    )
    items = tuple(
        DataWorkspaceItem(
            artifact_id=record.artifact_id,
            artifact_type=record.artifact_type,
            relative_path=record.relative_path,
            content_sha256=record.content_sha256,
            payload=record.payload,
        )
        for record in records
    )
    counts = _type_counts(records)
    present_types = frozenset(counts)

    if not items:
        state = "NO_REGISTERED_DATA"
    elif present_types == _DATA_ARTIFACT_TYPES:
        state = "AVAILABLE"
    else:
        state = "INCOMPLETE"

    return DataWorkspaceModel(
        correlation_id=read_model.correlation_id,
        state=state,
        items=items,
        artifact_type_counts=counts,
    )


def build_research_runs_workspace_model(
    read_model: ConsoleReadModel,
) -> ResearchRunsWorkspaceModel:
    records = tuple(
        sorted(
            (
                record
                for record in read_model.artifact_records
                if record.artifact_type
                in _RESEARCH_RUN_ARTIFACT_TYPES
            ),
            key=lambda item: (item.artifact_type, item.artifact_id),
        )
    )
    items = tuple(
        ResearchRunWorkspaceItem(
            artifact_id=record.artifact_id,
            artifact_type=record.artifact_type,
            relative_path=record.relative_path,
            content_sha256=record.content_sha256,
            run_id=_payload_label(
                record.payload,
                (
                    "run_id",
                    "research_run_id",
                    "workflow_id",
                    "correlation_id",
                ),
                record.artifact_id,
            ),
            workflow_state=_payload_label(
                record.payload,
                (
                    "workflow_status",
                    "status",
                    "state",
                    "decision",
                ),
                "UNSPECIFIED",
            ),
            payload=record.payload,
        )
        for record in records
    )
    counts = _type_counts(records)
    present_types = frozenset(counts)

    if not items:
        state = "NO_REGISTERED_RUNS"
    elif present_types == _RESEARCH_RUN_ARTIFACT_TYPES:
        state = "AVAILABLE"
    else:
        state = "INCOMPLETE"

    return ResearchRunsWorkspaceModel(
        correlation_id=read_model.correlation_id,
        state=state,
        items=items,
        artifact_type_counts=counts,
    )


def build_ai_comparison_workspace_model(
    read_model: ConsoleReadModel,
) -> AIComparisonWorkspaceModel:
    records = tuple(
        sorted(
            (
                record
                for record in read_model.artifact_records
                if record.artifact_type
                in _AI_COMPARISON_ARTIFACT_TYPES
            ),
            key=lambda item: (item.artifact_type, item.artifact_id),
        )
    )
    items = tuple(
        AIComparisonItem(
            artifact_id=record.artifact_id,
            artifact_type=record.artifact_type,
            relative_path=record.relative_path,
            content_sha256=record.content_sha256,
            model_label=_payload_label(
                record.payload,
                (
                    "model_name",
                    "model_id",
                    "provider",
                    "model",
                    "evaluator_model",
                ),
                "UNSPECIFIED",
            ),
            prompt_version=_payload_label(
                record.payload,
                (
                    "prompt_version",
                    "prompt_id",
                    "prompt_model_version",
                    "schema_version",
                ),
                "UNSPECIFIED",
            ),
            evaluation_state=_payload_label(
                record.payload,
                (
                    "evaluation_status",
                    "status",
                    "result",
                    "decision",
                    "outcome",
                ),
                "UNSPECIFIED",
            ),
            payload=record.payload,
        )
        for record in records
    )
    counts = _type_counts(records)
    present_types = frozenset(counts)

    if not items:
        state = "NO_REGISTERED_AI_ARTIFACTS"
    elif present_types == _AI_COMPARISON_ARTIFACT_TYPES:
        state = "COMPARISON_READY"
    else:
        state = "INCOMPLETE"

    return AIComparisonWorkspaceModel(
        correlation_id=read_model.correlation_id,
        state=state,
        items=items,
        artifact_type_counts=counts,
    )


def build_governance_workspace_model(
    read_model: ConsoleReadModel,
) -> GovernanceWorkspaceModel:
    records = tuple(
        sorted(
            (
                record
                for record in read_model.artifact_records
                if record.artifact_type
                in _GOVERNANCE_ARTIFACT_TYPES
            ),
            key=lambda item: (item.artifact_type, item.artifact_id),
        )
    )
    items = tuple(
        GovernanceWorkspaceItem(
            artifact_id=record.artifact_id,
            artifact_type=record.artifact_type,
            relative_path=record.relative_path,
            content_sha256=record.content_sha256,
            subject=_payload_label(
                record.payload,
                (
                    "model_name",
                    "model_id",
                    "policy_name",
                    "policy_id",
                    "candidate_id",
                    "factor_id",
                    "subject",
                ),
                record.artifact_id,
            ),
            version=_payload_label(
                record.payload,
                (
                    "model_version",
                    "policy_version",
                    "version",
                    "schema_version",
                ),
                "UNSPECIFIED",
            ),
            decision=_payload_label(
                record.payload,
                (
                    "governance_status",
                    "policy_status",
                    "decision",
                    "status",
                    "state",
                ),
                "UNSPECIFIED",
            ),
            payload=record.payload,
        )
        for record in records
    )
    counts = _type_counts(records)
    present_types = frozenset(counts)

    if not items:
        state = "NO_REGISTERED_GOVERNANCE"
    elif _REQUIRED_GOVERNANCE_ARTIFACT_TYPES <= present_types:
        state = "AVAILABLE"
    else:
        state = "INCOMPLETE"

    return GovernanceWorkspaceModel(
        correlation_id=read_model.correlation_id,
        state=state,
        items=items,
        artifact_type_counts=counts,
    )


def build_audit_history_workspace_model(
    read_model: ConsoleReadModel,
) -> AuditHistoryWorkspaceModel:
    records = tuple(
        sorted(
            (
                record
                for record in read_model.artifact_records
                if record.artifact_type in _AUDIT_ARTIFACT_TYPES
            ),
            key=lambda item: (item.artifact_type, item.artifact_id),
        )
    )
    items = tuple(
        AuditHistoryItem(
            artifact_id=record.artifact_id,
            artifact_type=record.artifact_type,
            relative_path=record.relative_path,
            content_sha256=record.content_sha256,
            event_id=_payload_label(
                record.payload,
                (
                    "event_id",
                    "receipt_id",
                    "manifest_id",
                    "audit_id",
                    "correlation_id",
                ),
                record.artifact_id,
            ),
            event_time=_payload_label(
                record.payload,
                (
                    "timestamp_utc",
                    "created_at_utc",
                    "recorded_at_utc",
                    "event_time",
                    "as_of",
                ),
                "UNSPECIFIED",
            ),
            action=_payload_label(
                record.payload,
                (
                    "action",
                    "decision",
                    "event_type",
                    "status",
                    "state",
                ),
                "UNSPECIFIED",
            ),
            actor=_payload_label(
                record.payload,
                (
                    "actor",
                    "operator_id",
                    "source",
                    "producer",
                    "component",
                ),
                "UNSPECIFIED",
            ),
            payload=record.payload,
        )
        for record in records
    )
    counts = _type_counts(records)
    present_types = frozenset(counts)

    if not items:
        state = "NO_REGISTERED_AUDIT_HISTORY"
    elif present_types == _AUDIT_ARTIFACT_TYPES:
        state = "AVAILABLE"
    else:
        state = "INCOMPLETE"

    return AuditHistoryWorkspaceModel(
        correlation_id=read_model.correlation_id,
        state=state,
        items=items,
        artifact_type_counts=counts,
    )
