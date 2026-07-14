from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Tuple

from .evidence_audit_explorer import EvidenceRelation
from .evidence_audit_graph import EvidenceArtifactGraph
from .read_model import ConsoleArtifactRecord, ConsoleReadModel


_SAFE_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$"
)
_SAFE_PAYLOAD_KEY_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$"
)

_LIFECYCLE_STAGE_BY_ARTIFACT_TYPE = MappingProxyType(
    {
        "paper_validation": "PAPER_VALIDATION",
        "shadow_observation": "SHADOW_OBSERVATION",
        "operator_review": "OPERATOR_REVIEW",
        "report_archive": "REPORT_ARCHIVE",
    }
)
_STAGE_ORDER = MappingProxyType(
    {
        "PAPER_VALIDATION": 1,
        "SHADOW_OBSERVATION": 2,
        "OPERATOR_REVIEW": 3,
        "REPORT_ARCHIVE": 4,
    }
)
_LIFECYCLE_RELATIONS = frozenset(
    {
        EvidenceRelation.DERIVED_FROM,
        EvidenceRelation.VALIDATES,
        EvidenceRelation.REVIEWS,
        EvidenceRelation.ARCHIVES,
    }
)


def _require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _safe_id(value: object, field_name: str) -> str:
    normalized = _require_text(value, field_name)
    if not _SAFE_ID_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{field_name} contains a prohibited character"
        )
    return normalized


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


def _payload_keys(
    payload: Mapping[str, Any],
) -> Tuple[str, ...]:
    return tuple(
        sorted(
            key
            for key in (
                str(item).strip()
                for item in payload.keys()
            )
            if _SAFE_PAYLOAD_KEY_PATTERN.fullmatch(key)
        )
    )


def _digest(value: object) -> str:
    digest = _require_text(
        value,
        "content_sha256",
    ).lower()
    if len(digest) != 64 or any(
        character not in "0123456789abcdef"
        for character in digest
    ):
        raise ValueError(
            "content_sha256 must be a SHA-256 digest"
        )
    return digest


@dataclass(frozen=True)
class EvidenceLifecycleItem:
    artifact_id: str
    artifact_type: str
    stage: str
    status: str
    observed_at: str
    evidence_keys: Tuple[str, ...]
    relative_path: str
    content_sha256: str
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True

    def __post_init__(self) -> None:
        artifact_id = _safe_id(
            self.artifact_id,
            "artifact_id",
        )
        artifact_type = _safe_id(
            self.artifact_type,
            "artifact_type",
        )
        expected_stage = (
            _LIFECYCLE_STAGE_BY_ARTIFACT_TYPE.get(
                artifact_type
            )
        )
        if expected_stage is None:
            raise ValueError(
                "unsupported lifecycle evidence artifact type"
            )
        if self.stage != expected_stage:
            raise ValueError(
                "lifecycle stage does not match artifact type"
            )

        status = _require_text(self.status, "status")
        observed_at = _require_text(
            self.observed_at,
            "observed_at",
        )
        evidence_keys = tuple(
            sorted(set(self.evidence_keys))
        )
        if any(
            not _SAFE_PAYLOAD_KEY_PATTERN.fullmatch(item)
            for item in evidence_keys
        ):
            raise ValueError(
                "evidence key contains a prohibited character"
            )
        relative_path = _require_text(
            self.relative_path,
            "relative_path",
        )
        digest = _digest(self.content_sha256)

        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "lifecycle evidence must remain "
                "registered-artifact-only and read-only"
            )
        if not self.operator_review_required:
            raise ValueError(
                "Operator review must remain required"
            )
        if not self.deterministic_authority:
            raise ValueError(
                "Deterministic Engine authority must remain enabled"
            )

        object.__setattr__(
            self,
            "artifact_id",
            artifact_id,
        )
        object.__setattr__(
            self,
            "artifact_type",
            artifact_type,
        )
        object.__setattr__(self, "status", status)
        object.__setattr__(
            self,
            "observed_at",
            observed_at,
        )
        object.__setattr__(
            self,
            "evidence_keys",
            evidence_keys,
        )
        object.__setattr__(
            self,
            "relative_path",
            relative_path,
        )
        object.__setattr__(
            self,
            "content_sha256",
            digest,
        )


@dataclass(frozen=True)
class EvidenceLifecycleLink:
    source_artifact_id: str
    source_stage: str
    relation: EvidenceRelation
    target_artifact_id: str
    target_stage: str
    correlation_id: str
    registered_artifact_only: bool = True
    read_only: bool = True

    def __post_init__(self) -> None:
        source_artifact_id = _safe_id(
            self.source_artifact_id,
            "source_artifact_id",
        )
        target_artifact_id = _safe_id(
            self.target_artifact_id,
            "target_artifact_id",
        )
        correlation_id = _safe_id(
            self.correlation_id,
            "correlation_id",
        )
        if self.source_stage not in _STAGE_ORDER:
            raise ValueError(
                "unsupported source lifecycle stage"
            )
        if self.target_stage not in _STAGE_ORDER:
            raise ValueError(
                "unsupported target lifecycle stage"
            )

        relation = self.relation
        if not isinstance(relation, EvidenceRelation):
            relation = EvidenceRelation(str(relation))
        if relation not in _LIFECYCLE_RELATIONS:
            raise ValueError(
                "unsupported lifecycle evidence relation"
            )
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "lifecycle link must remain "
                "registered-artifact-only and read-only"
            )

        object.__setattr__(
            self,
            "source_artifact_id",
            source_artifact_id,
        )
        object.__setattr__(
            self,
            "target_artifact_id",
            target_artifact_id,
        )
        object.__setattr__(
            self,
            "correlation_id",
            correlation_id,
        )
        object.__setattr__(
            self,
            "relation",
            relation,
        )


@dataclass(frozen=True)
class EvidenceLifecycleDossier:
    correlation_id: str
    state: str
    items: Tuple[EvidenceLifecycleItem, ...]
    links: Tuple[EvidenceLifecycleLink, ...]
    stage_counts: Mapping[str, int]
    relation_counts: Mapping[str, int]
    missing_artifact_types: Tuple[str, ...]
    unresolved_artifact_ids: Tuple[str, ...]
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True
    paper_only: bool = True

    def __post_init__(self) -> None:
        correlation_id = _safe_id(
            self.correlation_id,
            "correlation_id",
        )
        if self.state not in {
            "AVAILABLE",
            "INCOMPLETE",
            "NO_REGISTERED_LIFECYCLE_EVIDENCE",
        }:
            raise ValueError(
                "unsupported lifecycle dossier state"
            )

        items = tuple(self.items)
        links = tuple(self.links)
        item_ids = tuple(
            item.artifact_id for item in items
        )
        if len(set(item_ids)) != len(item_ids):
            raise ValueError(
                "lifecycle item ids must be unique"
            )

        expected_item_order = tuple(
            sorted(
                items,
                key=lambda item: (
                    _STAGE_ORDER[item.stage],
                    item.artifact_id,
                ),
            )
        )
        if items != expected_item_order:
            raise ValueError(
                "lifecycle items must be deterministically ordered"
            )

        link_keys = tuple(
            (
                link.source_artifact_id,
                link.relation.value,
                link.target_artifact_id,
            )
            for link in links
        )
        if len(set(link_keys)) != len(link_keys):
            raise ValueError(
                "lifecycle links must be unique"
            )
        if any(
            link.correlation_id != correlation_id
            for link in links
        ):
            raise ValueError(
                "lifecycle link correlation mismatch"
            )

        item_id_set = set(item_ids)
        if any(
            link.source_artifact_id not in item_id_set
            or link.target_artifact_id not in item_id_set
            for link in links
        ):
            raise ValueError(
                "lifecycle link endpoints must be lifecycle items"
            )

        missing = tuple(
            sorted(set(self.missing_artifact_types))
        )
        unresolved = tuple(
            sorted(set(self.unresolved_artifact_ids))
        )
        if set(unresolved) & item_id_set:
            raise ValueError(
                "unresolved artifact ids must not be registered"
            )

        expected_state = (
            "NO_REGISTERED_LIFECYCLE_EVIDENCE"
            if not items
            else "INCOMPLETE"
            if missing or unresolved
            else "AVAILABLE"
        )
        if self.state != expected_state:
            raise ValueError(
                "lifecycle dossier state mismatch"
            )

        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "lifecycle dossier must remain "
                "registered-artifact-only and read-only"
            )
        if not self.operator_review_required:
            raise ValueError(
                "Operator review must remain required"
            )
        if not self.deterministic_authority:
            raise ValueError(
                "Deterministic Engine authority must remain enabled"
            )
        if not self.paper_only:
            raise ValueError(
                "lifecycle dossier must remain paper-only"
            )

        object.__setattr__(
            self,
            "correlation_id",
            correlation_id,
        )
        object.__setattr__(self, "items", items)
        object.__setattr__(self, "links", links)
        object.__setattr__(
            self,
            "stage_counts",
            MappingProxyType(
                dict(sorted(self.stage_counts.items()))
            ),
        )
        object.__setattr__(
            self,
            "relation_counts",
            MappingProxyType(
                dict(sorted(self.relation_counts.items()))
            ),
        )
        object.__setattr__(
            self,
            "missing_artifact_types",
            missing,
        )
        object.__setattr__(
            self,
            "unresolved_artifact_ids",
            unresolved,
        )


def _lifecycle_item(
    record: ConsoleArtifactRecord,
) -> EvidenceLifecycleItem:
    stage = _LIFECYCLE_STAGE_BY_ARTIFACT_TYPE[
        record.artifact_type
    ]
    return EvidenceLifecycleItem(
        artifact_id=record.artifact_id,
        artifact_type=record.artifact_type,
        stage=stage,
        status=_payload_label(
            record.payload,
            (
                "validation_status",
                "observation_status",
                "review_status",
                "archive_status",
                "status",
                "state",
                "decision",
                "result",
                "outcome",
            ),
            "UNSPECIFIED",
        ),
        observed_at=_payload_label(
            record.payload,
            (
                "timestamp_utc",
                "observed_at_utc",
                "validated_at_utc",
                "reviewed_at_utc",
                "archived_at_utc",
                "created_at_utc",
                "recorded_at_utc",
                "as_of",
            ),
            "UNSPECIFIED",
        ),
        evidence_keys=_payload_keys(record.payload),
        relative_path=record.relative_path,
        content_sha256=record.content_sha256,
    )


def _count_stages(
    items: Tuple[EvidenceLifecycleItem, ...],
) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.stage] = (
            counts.get(item.stage, 0) + 1
        )
    return MappingProxyType(dict(sorted(counts.items())))


def _count_relations(
    links: Tuple[EvidenceLifecycleLink, ...],
) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for link in links:
        name = link.relation.value
        counts[name] = counts.get(name, 0) + 1
    return MappingProxyType(dict(sorted(counts.items())))


def build_evidence_lifecycle_dossier(
    read_model: ConsoleReadModel,
    graph: EvidenceArtifactGraph,
) -> EvidenceLifecycleDossier:
    if graph.correlation_id != read_model.correlation_id:
        raise ValueError(
            "evidence graph and read model correlation mismatch"
        )

    graph_node_ids = {
        node.artifact_id for node in graph.nodes
    }
    record_ids = {
        record.artifact_id
        for record in read_model.artifact_records
    }
    if graph_node_ids != record_ids:
        raise ValueError(
            "evidence graph and read model artifact mismatch"
        )

    lifecycle_records = tuple(
        sorted(
            (
                record
                for record in read_model.artifact_records
                if record.artifact_type
                in _LIFECYCLE_STAGE_BY_ARTIFACT_TYPE
            ),
            key=lambda record: (
                _STAGE_ORDER[
                    _LIFECYCLE_STAGE_BY_ARTIFACT_TYPE[
                        record.artifact_type
                    ]
                ],
                record.artifact_id,
            ),
        )
    )
    items = tuple(
        _lifecycle_item(record)
        for record in lifecycle_records
    )

    item_by_id = {
        item.artifact_id: item for item in items
    }
    lifecycle_ids = set(item_by_id)

    links = tuple(
        sorted(
            (
                EvidenceLifecycleLink(
                    source_artifact_id=relationship.source_artifact_id,
                    source_stage=item_by_id[
                        relationship.source_artifact_id
                    ].stage,
                    relation=relationship.relation,
                    target_artifact_id=relationship.target_artifact_id,
                    target_stage=item_by_id[
                        relationship.target_artifact_id
                    ].stage,
                    correlation_id=relationship.correlation_id,
                )
                for relationship in graph.relationships
                if (
                    relationship.relation
                    in _LIFECYCLE_RELATIONS
                    and relationship.source_artifact_id
                    in lifecycle_ids
                    and relationship.target_artifact_id
                    in lifecycle_ids
                )
            ),
            key=lambda link: (
                _STAGE_ORDER[link.source_stage],
                link.source_artifact_id,
                link.relation.value,
                _STAGE_ORDER[link.target_stage],
                link.target_artifact_id,
            ),
        )
    )

    present_types = {
        item.artifact_type for item in items
    }
    missing_types = tuple(
        sorted(
            set(_LIFECYCLE_STAGE_BY_ARTIFACT_TYPE)
            - present_types
        )
    )
    unresolved = tuple(
        sorted(graph.unresolved_artifact_ids)
    )

    state = (
        "NO_REGISTERED_LIFECYCLE_EVIDENCE"
        if not items
        else "INCOMPLETE"
        if missing_types or unresolved
        else "AVAILABLE"
    )

    return EvidenceLifecycleDossier(
        correlation_id=read_model.correlation_id,
        state=state,
        items=items,
        links=links,
        stage_counts=_count_stages(items),
        relation_counts=_count_relations(links),
        missing_artifact_types=missing_types,
        unresolved_artifact_ids=unresolved,
    )
