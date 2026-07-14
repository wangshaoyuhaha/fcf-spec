from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .read_model import ConsoleArtifactRecord, ConsoleReadModel
from .research_workspace import RESEARCH_WORKSPACE_ROUTE_REGISTRY


_D2_IMPLEMENTED_PATHS = frozenset(
    {
        "/",
        "/data",
        "/stocks",
        "/risk",
        "/validation",
        "/review",
        "/reports",
    }
)
_DATA_ARTIFACT_TYPES = frozenset({"data_snapshot", "data_quality"})


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
        if route.path in _D2_IMPLEMENTED_PATHS
    )
    planned = tuple(
        route.path
        for route in RESEARCH_WORKSPACE_ROUTE_REGISTRY.routes
        if route.path not in _D2_IMPLEMENTED_PATHS
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
