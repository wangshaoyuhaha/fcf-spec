from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from .evidence_audit_explorer import (
    EvidenceArtifactNode,
    EvidenceIntegrityState,
    EvidenceRelation,
    EvidenceRelationship,
)
from .read_model import ConsoleArtifactRecord, ConsoleReadModel


_SAFE_PAYLOAD_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")

_RELATION_FIELD_MAP = (
    ("archive_for_artifact_id", EvidenceRelation.ARCHIVES),
    ("archive_for_artifact_ids", EvidenceRelation.ARCHIVES),
    ("archived_artifact_id", EvidenceRelation.ARCHIVES),
    ("archived_artifact_ids", EvidenceRelation.ARCHIVES),
    ("contradicts_artifact_id", EvidenceRelation.CONTRADICTS),
    ("contradicts_artifact_ids", EvidenceRelation.CONTRADICTS),
    ("correlates_with_artifact_id", EvidenceRelation.CORRELATES_WITH),
    ("correlates_with_artifact_ids", EvidenceRelation.CORRELATES_WITH),
    ("derived_from_artifact_id", EvidenceRelation.DERIVED_FROM),
    ("derived_from_artifact_ids", EvidenceRelation.DERIVED_FROM),
    ("input_artifact_id", EvidenceRelation.DERIVED_FROM),
    ("input_artifact_ids", EvidenceRelation.DERIVED_FROM),
    ("parent_artifact_id", EvidenceRelation.DERIVED_FROM),
    ("parent_artifact_ids", EvidenceRelation.DERIVED_FROM),
    ("review_for_artifact_id", EvidenceRelation.REVIEWS),
    ("review_for_artifact_ids", EvidenceRelation.REVIEWS),
    ("reviewed_artifact_id", EvidenceRelation.REVIEWS),
    ("reviewed_artifact_ids", EvidenceRelation.REVIEWS),
    ("source_artifact_id", EvidenceRelation.DERIVED_FROM),
    ("source_artifact_ids", EvidenceRelation.DERIVED_FROM),
    ("validates_artifact_id", EvidenceRelation.VALIDATES),
    ("validates_artifact_ids", EvidenceRelation.VALIDATES),
    ("validation_for_artifact_id", EvidenceRelation.VALIDATES),
    ("validation_for_artifact_ids", EvidenceRelation.VALIDATES),
)

_PROVENANCE_CHAIN_RELATIONS = frozenset(
    {
        EvidenceRelation.DERIVED_FROM,
        EvidenceRelation.VALIDATES,
        EvidenceRelation.REVIEWS,
        EvidenceRelation.ARCHIVES,
    }
)


def _reference_values(
    value: object,
    field_name: str,
) -> Tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raw_values = (value,)
    elif isinstance(value, (tuple, list)):
        raw_values = tuple(value)
    else:
        raise ValueError(
            f"{field_name} must be text or an array"
        )

    normalized = tuple(
        str(item).strip()
        for item in raw_values
    )
    if any(not item for item in normalized):
        raise ValueError(
            f"{field_name} contains an empty artifact reference"
        )
    return tuple(sorted(set(normalized)))


def _payload_keys(
    record: ConsoleArtifactRecord,
) -> Tuple[str, ...]:
    return tuple(
        sorted(
            key
            for key in (
                str(item).strip()
                for item in record.payload.keys()
            )
            if _SAFE_PAYLOAD_KEY.fullmatch(key)
        )
    )


@dataclass(frozen=True)
class EvidenceArtifactGraph:
    correlation_id: str
    state: str
    nodes: Tuple[EvidenceArtifactNode, ...]
    relationships: Tuple[EvidenceRelationship, ...]
    unresolved_artifact_ids: Tuple[str, ...]
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "AVAILABLE",
            "EMPTY",
            "INCOMPLETE",
        }:
            raise ValueError(
                "unsupported evidence artifact graph state"
            )
        correlation_id = str(self.correlation_id).strip()
        if not correlation_id:
            raise ValueError("correlation_id is required")

        nodes = tuple(self.nodes)
        relationships = tuple(self.relationships)
        unresolved = tuple(
            sorted(set(self.unresolved_artifact_ids))
        )

        node_ids = tuple(node.artifact_id for node in nodes)
        if len(set(node_ids)) != len(node_ids):
            raise ValueError(
                "evidence graph node ids must be unique"
            )
        if any(
            node.correlation_id != correlation_id
            for node in nodes
        ):
            raise ValueError(
                "evidence graph node correlation mismatch"
            )

        node_id_set = set(node_ids)
        relationship_keys = tuple(
            (
                item.source_artifact_id,
                item.relation.value,
                item.target_artifact_id,
            )
            for item in relationships
        )
        if len(set(relationship_keys)) != len(
            relationship_keys
        ):
            raise ValueError(
                "evidence graph relationships must be unique"
            )
        for relationship in relationships:
            if relationship.correlation_id != correlation_id:
                raise ValueError(
                    "evidence graph relationship correlation mismatch"
                )
            if (
                relationship.source_artifact_id
                not in node_id_set
                or relationship.target_artifact_id
                not in node_id_set
            ):
                raise ValueError(
                    "evidence graph relationship endpoint "
                    "must be registered"
                )

        if set(unresolved) & node_id_set:
            raise ValueError(
                "unresolved artifact ids must not be registered"
            )

        expected_state = (
            "EMPTY"
            if not nodes
            else "INCOMPLETE"
            if unresolved
            else "AVAILABLE"
        )
        if self.state != expected_state:
            raise ValueError(
                "evidence artifact graph state mismatch"
            )

        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "evidence graph must remain registered-artifact-only "
                "and read-only"
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
            "correlation_id",
            correlation_id,
        )
        object.__setattr__(self, "nodes", nodes)
        object.__setattr__(
            self,
            "relationships",
            relationships,
        )
        object.__setattr__(
            self,
            "unresolved_artifact_ids",
            unresolved,
        )

    def by_artifact_id(
        self,
        artifact_id: str,
    ) -> EvidenceArtifactNode:
        normalized = str(artifact_id).strip()
        for node in self.nodes:
            if node.artifact_id == normalized:
                return node
        raise KeyError(normalized)

    def outgoing(
        self,
        artifact_id: str,
    ) -> Tuple[EvidenceRelationship, ...]:
        normalized = str(artifact_id).strip()
        self.by_artifact_id(normalized)
        return tuple(
            item
            for item in self.relationships
            if item.source_artifact_id == normalized
        )

    def incoming(
        self,
        artifact_id: str,
    ) -> Tuple[EvidenceRelationship, ...]:
        normalized = str(artifact_id).strip()
        self.by_artifact_id(normalized)
        return tuple(
            item
            for item in self.relationships
            if item.target_artifact_id == normalized
        )


@dataclass(frozen=True)
class EvidenceCorrelationLineage:
    correlation_id: str
    state: str
    artifact_ids: Tuple[str, ...]
    artifact_type_counts: Mapping[str, int]
    relationship_count: int
    unresolved_artifact_ids: Tuple[str, ...]
    registered_artifact_only: bool = True
    read_only: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "AVAILABLE",
            "EMPTY",
            "INCOMPLETE",
        }:
            raise ValueError(
                "unsupported correlation lineage state"
            )
        artifact_ids = tuple(self.artifact_ids)
        if len(set(artifact_ids)) != len(artifact_ids):
            raise ValueError(
                "correlation lineage artifact ids must be unique"
            )
        counts = dict(self.artifact_type_counts)
        if any(
            not str(key).strip() or int(value) < 1
            for key, value in counts.items()
        ):
            raise ValueError(
                "artifact type counts must be positive"
            )
        relationship_count = int(self.relationship_count)
        if relationship_count < 0:
            raise ValueError(
                "relationship_count must be non-negative"
            )
        unresolved = tuple(
            sorted(set(self.unresolved_artifact_ids))
        )
        expected_state = (
            "EMPTY"
            if not artifact_ids
            else "INCOMPLETE"
            if unresolved
            else "AVAILABLE"
        )
        if self.state != expected_state:
            raise ValueError(
                "correlation lineage state mismatch"
            )
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "correlation lineage must remain "
                "registered-artifact-only and read-only"
            )

        object.__setattr__(
            self,
            "artifact_ids",
            artifact_ids,
        )
        object.__setattr__(
            self,
            "artifact_type_counts",
            MappingProxyType(dict(sorted(counts.items()))),
        )
        object.__setattr__(
            self,
            "relationship_count",
            relationship_count,
        )
        object.__setattr__(
            self,
            "unresolved_artifact_ids",
            unresolved,
        )


@dataclass(frozen=True)
class EvidenceProvenanceStep:
    depth: int
    artifact_id: str
    from_artifact_id: str | None
    relation: EvidenceRelation | None

    def __post_init__(self) -> None:
        depth = int(self.depth)
        artifact_id = str(self.artifact_id).strip()
        if depth < 0:
            raise ValueError("depth must be non-negative")
        if not artifact_id:
            raise ValueError("artifact_id is required")

        from_artifact_id = self.from_artifact_id
        relation = self.relation
        if depth == 0:
            if from_artifact_id is not None or relation is not None:
                raise ValueError(
                    "root provenance step cannot have an incoming edge"
                )
        else:
            if from_artifact_id is None or relation is None:
                raise ValueError(
                    "non-root provenance step requires an incoming edge"
                )
            from_artifact_id = str(from_artifact_id).strip()
            if not from_artifact_id:
                raise ValueError(
                    "from_artifact_id is required"
                )
            if not isinstance(relation, EvidenceRelation):
                relation = EvidenceRelation(str(relation))
            if relation not in _PROVENANCE_CHAIN_RELATIONS:
                raise ValueError(
                    "unsupported provenance chain relation"
                )

        object.__setattr__(self, "depth", depth)
        object.__setattr__(
            self,
            "artifact_id",
            artifact_id,
        )
        object.__setattr__(
            self,
            "from_artifact_id",
            from_artifact_id,
        )
        object.__setattr__(self, "relation", relation)


@dataclass(frozen=True)
class EvidenceProvenanceChain:
    correlation_id: str
    root_artifact_id: str
    state: str
    steps: Tuple[EvidenceProvenanceStep, ...]
    cycle_detected: bool
    max_depth_reached: bool
    read_only: bool = True
    registered_artifact_only: bool = True

    def __post_init__(self) -> None:
        if self.state not in {
            "AVAILABLE",
            "INCOMPLETE",
        }:
            raise ValueError(
                "unsupported provenance chain state"
            )
        root = str(self.root_artifact_id).strip()
        steps = tuple(self.steps)
        if not root:
            raise ValueError("root_artifact_id is required")
        if not steps:
            raise ValueError(
                "provenance chain must contain the root step"
            )
        if (
            steps[0].depth != 0
            or steps[0].artifact_id != root
        ):
            raise ValueError(
                "provenance chain root step mismatch"
            )
        step_ids = tuple(step.artifact_id for step in steps)
        if len(set(step_ids)) != len(step_ids):
            raise ValueError(
                "provenance chain artifact ids must be unique"
            )
        if not self.read_only or not self.registered_artifact_only:
            raise ValueError(
                "provenance chain must remain read-only "
                "and registered-artifact-only"
            )

        object.__setattr__(
            self,
            "root_artifact_id",
            root,
        )
        object.__setattr__(self, "steps", steps)
        object.__setattr__(
            self,
            "cycle_detected",
            bool(self.cycle_detected),
        )
        object.__setattr__(
            self,
            "max_depth_reached",
            bool(self.max_depth_reached),
        )


def build_evidence_artifact_graph(
    read_model: ConsoleReadModel,
) -> EvidenceArtifactGraph:
    records = tuple(
        sorted(
            read_model.artifact_records,
            key=lambda item: (
                item.artifact_type,
                item.artifact_id,
            ),
        )
    )
    node_ids = {
        record.artifact_id
        for record in records
    }

    nodes = tuple(
        EvidenceArtifactNode(
            artifact_id=record.artifact_id,
            artifact_type=record.artifact_type,
            correlation_id=read_model.correlation_id,
            relative_path=record.relative_path,
            content_sha256=record.content_sha256,
            integrity_state=EvidenceIntegrityState.VERIFIED,
            payload_keys=_payload_keys(record),
        )
        for record in records
    )

    relationship_map = {}
    unresolved = set()

    for record in records:
        for field_name, relation in _RELATION_FIELD_MAP:
            references = _reference_values(
                record.payload.get(field_name),
                field_name,
            )
            for target_artifact_id in references:
                if target_artifact_id == record.artifact_id:
                    raise ValueError(
                        "self-referential evidence relationship: "
                        + record.artifact_id
                    )
                if target_artifact_id not in node_ids:
                    unresolved.add(target_artifact_id)
                    continue

                relationship = EvidenceRelationship(
                    source_artifact_id=record.artifact_id,
                    target_artifact_id=target_artifact_id,
                    relation=relation,
                    correlation_id=read_model.correlation_id,
                )
                key = (
                    relationship.source_artifact_id,
                    relationship.relation.value,
                    relationship.target_artifact_id,
                )
                relationship_map[key] = relationship

    relationships = tuple(
        relationship_map[key]
        for key in sorted(relationship_map)
    )
    unresolved_ids = tuple(sorted(unresolved))
    state = (
        "EMPTY"
        if not nodes
        else "INCOMPLETE"
        if unresolved_ids
        else "AVAILABLE"
    )

    return EvidenceArtifactGraph(
        correlation_id=read_model.correlation_id,
        state=state,
        nodes=nodes,
        relationships=relationships,
        unresolved_artifact_ids=unresolved_ids,
    )


def build_evidence_correlation_lineage(
    graph: EvidenceArtifactGraph,
) -> EvidenceCorrelationLineage:
    counts = {}
    for node in graph.nodes:
        counts[node.artifact_type] = (
            counts.get(node.artifact_type, 0) + 1
        )

    return EvidenceCorrelationLineage(
        correlation_id=graph.correlation_id,
        state=graph.state,
        artifact_ids=tuple(
            node.artifact_id
            for node in graph.nodes
        ),
        artifact_type_counts=counts,
        relationship_count=len(graph.relationships),
        unresolved_artifact_ids=(
            graph.unresolved_artifact_ids
        ),
    )


def build_evidence_provenance_chain(
    graph: EvidenceArtifactGraph,
    artifact_id: str,
    *,
    max_depth: int = 50,
) -> EvidenceProvenanceChain:
    root = graph.by_artifact_id(artifact_id)
    depth_limit = int(max_depth)
    if not 1 <= depth_limit <= 100:
        raise ValueError(
            "max_depth must be between 1 and 100"
        )

    steps = [
        EvidenceProvenanceStep(
            depth=0,
            artifact_id=root.artifact_id,
            from_artifact_id=None,
            relation=None,
        )
    ]
    visited = {root.artifact_id}
    frontier = [(root.artifact_id, 0)]
    cycle_detected = False
    max_depth_reached = False

    while frontier:
        current_artifact_id, depth = frontier.pop(0)
        outgoing = tuple(
            relationship
            for relationship in graph.outgoing(
                current_artifact_id
            )
            if relationship.relation
            in _PROVENANCE_CHAIN_RELATIONS
        )
        for relationship in outgoing:
            next_depth = depth + 1
            if next_depth > depth_limit:
                max_depth_reached = True
                continue

            target = relationship.target_artifact_id
            if target in visited:
                cycle_detected = True
                continue

            visited.add(target)
            steps.append(
                EvidenceProvenanceStep(
                    depth=next_depth,
                    artifact_id=target,
                    from_artifact_id=current_artifact_id,
                    relation=relationship.relation,
                )
            )
            frontier.append((target, next_depth))

    ordered_steps = tuple(
        sorted(
            steps,
            key=lambda item: (
                item.depth,
                item.artifact_id,
                ""
                if item.relation is None
                else item.relation.value,
            ),
        )
    )
    state = (
        "INCOMPLETE"
        if (
            graph.state == "INCOMPLETE"
            or cycle_detected
            or max_depth_reached
        )
        else "AVAILABLE"
    )

    return EvidenceProvenanceChain(
        correlation_id=graph.correlation_id,
        root_artifact_id=root.artifact_id,
        state=state,
        steps=ordered_steps,
        cycle_detected=cycle_detected,
        max_depth_reached=max_depth_reached,
    )
