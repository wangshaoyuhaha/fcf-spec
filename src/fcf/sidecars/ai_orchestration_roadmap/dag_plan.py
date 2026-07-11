"""Deterministic one-way governance DAG roadmap plan."""

import re
from collections import deque
from typing import Any, Mapping, Sequence

from .artifact_plan import (
    validate_registered_artifact_dependency_plan,
)
from .contract import (
    ALLOWED_INPUTS,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    ROADMAP_MODE,
)


STAGE_ID = "AI-ORCHESTRATION-ROADMAP-D3"
DAG_PLAN_VERSION = "1.0.0"

DEFAULT_ARTIFACT_TYPE_ORDER = (
    "REGISTERED_MODEL_VERSION_ARTIFACT",
    "REGISTERED_PROMPT_VERSION_ARTIFACT",
    "REGISTERED_VALIDATION_BASELINE_ARTIFACT",
    "REGISTERED_AI_CONTEXT_ARTIFACT",
    "REGISTERED_AI_EVALUATION_ARTIFACT",
    "REGISTERED_AI_CHALLENGE_ARTIFACT",
    "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
    "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
    "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
    "REGISTERED_OPERATOR_REVIEW_ARTIFACT",
)

EDGE_TYPES = (
    "DATA_DEPENDENCY",
    "GOVERNANCE_EVIDENCE",
    "VERSION_GUARD",
    "VALIDATION_GATE",
    "TRACEABILITY",
    "OPERATOR_GATE",
)

PLANNED_EDGE_DEFINITIONS = (
    (
        "REGISTERED_MODEL_VERSION_ARTIFACT",
        "REGISTERED_AI_EVALUATION_ARTIFACT",
        "VERSION_GUARD",
        True,
    ),
    (
        "REGISTERED_PROMPT_VERSION_ARTIFACT",
        "REGISTERED_AI_EVALUATION_ARTIFACT",
        "VERSION_GUARD",
        True,
    ),
    (
        "REGISTERED_VALIDATION_BASELINE_ARTIFACT",
        "REGISTERED_AI_EVALUATION_ARTIFACT",
        "VALIDATION_GATE",
        True,
    ),
    (
        "REGISTERED_AI_CONTEXT_ARTIFACT",
        "REGISTERED_AI_EVALUATION_ARTIFACT",
        "DATA_DEPENDENCY",
        True,
    ),
    (
        "REGISTERED_AI_EVALUATION_ARTIFACT",
        "REGISTERED_AI_CHALLENGE_ARTIFACT",
        "GOVERNANCE_EVIDENCE",
        True,
    ),
    (
        "REGISTERED_AI_CONTEXT_ARTIFACT",
        "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
        "DATA_DEPENDENCY",
        True,
    ),
    (
        "REGISTERED_AI_CHALLENGE_ARTIFACT",
        "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
        "GOVERNANCE_EVIDENCE",
        True,
    ),
    (
        "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
        "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
        "DATA_DEPENDENCY",
        True,
    ),
    (
        "REGISTERED_AI_CHALLENGE_ARTIFACT",
        "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
        "GOVERNANCE_EVIDENCE",
        True,
    ),
    (
        "REGISTERED_AI_EVALUATION_ARTIFACT",
        "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
        "TRACEABILITY",
        True,
    ),
    (
        "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
        "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
        "TRACEABILITY",
        True,
    ),
    (
        "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
        "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
        "TRACEABILITY",
        True,
    ),
    (
        "REGISTERED_AI_CHALLENGE_ARTIFACT",
        "REGISTERED_OPERATOR_REVIEW_ARTIFACT",
        "OPERATOR_GATE",
        True,
    ),
    (
        "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
        "REGISTERED_OPERATOR_REVIEW_ARTIFACT",
        "OPERATOR_GATE",
        True,
    ),
)

DAG_STATUSES = (
    "READY_FOR_GATE_PLANNING",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

REQUIRED_NODE_FIELDS = (
    "node_id",
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "correlation_id",
    "research_run_id",
    "topological_index",
    "node_status",
    "operator_review_status",
    "runtime_execution_status",
    "safety_flags",
)

REQUIRED_EDGE_FIELDS = (
    "edge_id",
    "source_node_id",
    "target_node_id",
    "edge_type",
    "operator_gate_required",
    "edge_status",
    "runtime_execution_status",
)

REQUIRED_DAG_PLAN_FIELDS = (
    "dag_plan_id",
    "artifact_plan_id",
    "source_artifact_plan_status",
    "nodes",
    "edges",
    "topological_order",
    "cycle_detected",
    "orphan_node_ids",
    "dag_status",
    "operator_review_status",
    "roadmap_mode",
    "runtime_execution_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class DagPlanViolation(ValueError):
    """Raised when a deterministic roadmap DAG cannot be built."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str) or not item
        for item in value
    ):
        return False

    return value == sorted(set(value))


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append("safety_flag_names_must_match_contract")

    return errors


def _clone_node(node: Mapping[str, Any]) -> dict[str, Any]:
    cloned = dict(node)
    cloned["safety_flags"] = dict(node["safety_flags"])
    return cloned


def _canonical_nodes(
    nodes: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [_clone_node(node) for node in nodes],
        key=lambda item: (
            int(item["topological_index"]),
            str(item["node_id"]),
        ),
    )


def _canonical_edges(
    edges: Sequence[Mapping[str, Any]],
    node_index: Mapping[str, int],
) -> list[dict[str, Any]]:
    return sorted(
        [dict(edge) for edge in edges],
        key=lambda item: (
            node_index[str(item["source_node_id"])],
            node_index[str(item["target_node_id"])],
            str(item["edge_id"]),
        ),
    )


def _has_cycle(
    node_ids: Sequence[str],
    edges: Sequence[Mapping[str, Any]],
) -> bool:
    adjacency = {
        node_id: []
        for node_id in node_ids
    }
    indegree = {
        node_id: 0
        for node_id in node_ids
    }

    for edge in edges:
        source = str(edge["source_node_id"])
        target = str(edge["target_node_id"])

        if source not in adjacency or target not in indegree:
            return True

        adjacency[source].append(target)
        indegree[target] += 1

    queue = deque(
        sorted(
            node_id
            for node_id, count in indegree.items()
            if count == 0
        )
    )
    visited = 0

    while queue:
        node_id = queue.popleft()
        visited += 1

        for target in sorted(adjacency[node_id]):
            indegree[target] -= 1

            if indegree[target] == 0:
                queue.append(target)

    return visited != len(node_ids)


def _orphan_node_ids(
    node_ids: Sequence[str],
    edges: Sequence[Mapping[str, Any]],
) -> list[str]:
    connected: set[str] = set()

    for edge in edges:
        connected.add(str(edge["source_node_id"]))
        connected.add(str(edge["target_node_id"]))

    return sorted(set(node_ids) - connected)


def _derive_dag_status(
    *,
    source_artifact_plan_status: str,
    cycle_detected: bool,
    orphan_node_ids: Sequence[str],
) -> str:
    if source_artifact_plan_status == "BLOCKED":
        return "BLOCKED"

    if cycle_detected:
        return "INVALID"

    if (
        source_artifact_plan_status
        != "READY_FOR_DAG_PLANNING"
        or orphan_node_ids
    ):
        return "REVIEW_REQUIRED"

    return "READY_FOR_GATE_PLANNING"


def build_deterministic_governance_dag_plan(
    *,
    dag_plan_id: str,
    artifact_plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-executable one-way governance DAG roadmap."""
    plan_errors = (
        validate_registered_artifact_dependency_plan(
            artifact_plan
        )
    )

    if plan_errors:
        raise DagPlanViolation(";".join(plan_errors))

    references = artifact_plan["artifact_references"]
    reference_by_type: dict[str, Mapping[str, Any]] = {}

    for reference in references:
        artifact_type = str(reference["artifact_type"])

        if artifact_type in reference_by_type:
            raise DagPlanViolation(
                f"multiple_artifacts_for_type:{artifact_type}"
            )

        reference_by_type[artifact_type] = reference

    nodes: list[dict[str, Any]] = []

    for index, artifact_type in enumerate(
        DEFAULT_ARTIFACT_TYPE_ORDER,
        start=1,
    ):
        reference = reference_by_type.get(artifact_type)

        if reference is None:
            continue

        nodes.append(
            {
                "node_id": (
                    "node:" + str(reference["artifact_id"])
                ),
                "artifact_id": str(reference["artifact_id"]),
                "artifact_type": artifact_type,
                "artifact_version": str(
                    reference["artifact_version"]
                ),
                "correlation_id": str(
                    reference["correlation_id"]
                ),
                "research_run_id": str(
                    reference["research_run_id"]
                ),
                "topological_index": index,
                "node_status": "PLANNED",
                "operator_review_status": "REVIEW_REQUIRED",
                "runtime_execution_status": "NOT_ALLOWED",
                "safety_flags": _safety_flags(),
            }
        )

    canonical_nodes = _canonical_nodes(nodes)
    node_by_type = {
        node["artifact_type"]: node
        for node in canonical_nodes
    }
    node_index = {
        str(node["node_id"]): int(
            node["topological_index"]
        )
        for node in canonical_nodes
    }

    edges: list[dict[str, Any]] = []

    for edge_number, definition in enumerate(
        PLANNED_EDGE_DEFINITIONS,
        start=1,
    ):
        (
            source_type,
            target_type,
            edge_type,
            operator_gate_required,
        ) = definition

        source_node = node_by_type.get(source_type)
        target_node = node_by_type.get(target_type)

        if source_node is None or target_node is None:
            continue

        edges.append(
            {
                "edge_id": f"edge-{edge_number:02d}",
                "source_node_id": source_node["node_id"],
                "target_node_id": target_node["node_id"],
                "edge_type": edge_type,
                "operator_gate_required": (
                    operator_gate_required
                ),
                "edge_status": "PLANNED",
                "runtime_execution_status": "NOT_ALLOWED",
            }
        )

    canonical_edges = _canonical_edges(edges, node_index)
    node_ids = [
        str(node["node_id"])
        for node in canonical_nodes
    ]
    cycle_detected = _has_cycle(
        node_ids,
        canonical_edges,
    )
    orphan_node_ids = _orphan_node_ids(
        node_ids,
        canonical_edges,
    )

    return {
        "dag_plan_id": dag_plan_id,
        "artifact_plan_id": artifact_plan["plan_id"],
        "source_artifact_plan_status": artifact_plan[
            "plan_status"
        ],
        "nodes": canonical_nodes,
        "edges": canonical_edges,
        "topological_order": node_ids,
        "cycle_detected": cycle_detected,
        "orphan_node_ids": orphan_node_ids,
        "dag_status": _derive_dag_status(
            source_artifact_plan_status=artifact_plan[
                "plan_status"
            ],
            cycle_detected=cycle_detected,
            orphan_node_ids=orphan_node_ids,
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "roadmap_mode": ROADMAP_MODE,
        "runtime_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def _validate_node(node: object) -> list[str]:
    if not isinstance(node, Mapping):
        return ["node_must_be_mapping"]

    errors: list[str] = []

    if set(node.keys()) != set(REQUIRED_NODE_FIELDS):
        errors.append("node_fields_must_match_schema")

    for field in (
        "node_id",
        "artifact_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(node.get(field)):
            errors.append(f"{field}_invalid")

    if node.get("artifact_type") not in ALLOWED_INPUTS:
        errors.append("artifact_type_invalid")

    if not _valid_non_empty_string(
        node.get("artifact_version")
    ):
        errors.append("artifact_version_invalid")

    topological_index = node.get("topological_index")

    if (
        not isinstance(topological_index, int)
        or isinstance(topological_index, bool)
        or topological_index < 1
    ):
        errors.append("topological_index_invalid")

    if node.get("node_status") != "PLANNED":
        errors.append("node_status_invalid")

    if node.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if node.get("runtime_execution_status") != "NOT_ALLOWED":
        errors.append("runtime_execution_must_not_be_allowed")

    errors.extend(
        _validate_safety_flags(node.get("safety_flags"))
    )

    return errors


def _validate_edge(
    edge: object,
    node_ids: set[str],
    node_index: Mapping[str, int],
) -> list[str]:
    if not isinstance(edge, Mapping):
        return ["edge_must_be_mapping"]

    errors: list[str] = []

    if set(edge.keys()) != set(REQUIRED_EDGE_FIELDS):
        errors.append("edge_fields_must_match_schema")

    if not _valid_identifier(edge.get("edge_id")):
        errors.append("edge_id_invalid")

    source = edge.get("source_node_id")
    target = edge.get("target_node_id")

    if source not in node_ids:
        errors.append("source_node_id_invalid")

    if target not in node_ids:
        errors.append("target_node_id_invalid")

    if source == target:
        errors.append("self_edge_forbidden")

    if (
        source in node_index
        and target in node_index
        and node_index[str(source)] >= node_index[str(target)]
    ):
        errors.append("edge_direction_must_be_forward")

    if edge.get("edge_type") not in EDGE_TYPES:
        errors.append("edge_type_invalid")

    if edge.get("operator_gate_required") is not True:
        errors.append(
            "operator_gate_required_must_be_true"
        )

    if edge.get("edge_status") != "PLANNED":
        errors.append("edge_status_invalid")

    if edge.get("runtime_execution_status") != "NOT_ALLOWED":
        errors.append("runtime_execution_must_not_be_allowed")

    return errors


def validate_deterministic_governance_dag_plan(
    plan: object,
) -> list[str]:
    """Return deterministic D3 roadmap DAG validation errors."""
    if not isinstance(plan, Mapping):
        return ["dag_plan_must_be_mapping"]

    errors: list[str] = []

    if set(plan.keys()) != set(REQUIRED_DAG_PLAN_FIELDS):
        errors.append("dag_plan_fields_must_match_schema")

    for field in (
        "dag_plan_id",
        "artifact_plan_id",
    ):
        if not _valid_identifier(plan.get(field)):
            errors.append(f"{field}_invalid")

    source_status = plan.get("source_artifact_plan_status")

    if source_status not in (
        "READY_FOR_DAG_PLANNING",
        "REVIEW_REQUIRED",
        "BLOCKED",
    ):
        errors.append("source_artifact_plan_status_invalid")

    nodes = plan.get("nodes")

    if not isinstance(nodes, list):
        errors.append("nodes_must_be_list")
        nodes = []
    else:
        for index, node in enumerate(nodes):
            for node_error in _validate_node(node):
                errors.append(
                    f"node:{index}:{node_error}"
                )

    valid_nodes = [
        node
        for node in nodes
        if isinstance(node, Mapping)
    ]

    node_ids = [
        str(node.get("node_id"))
        for node in valid_nodes
    ]
    artifact_ids = [
        str(node.get("artifact_id"))
        for node in valid_nodes
    ]
    artifact_types = [
        str(node.get("artifact_type"))
        for node in valid_nodes
    ]
    topological_indices = [
        node.get("topological_index")
        for node in valid_nodes
    ]

    if len(node_ids) != len(set(node_ids)):
        errors.append("node_ids_must_be_unique")

    if len(artifact_ids) != len(set(artifact_ids)):
        errors.append("artifact_ids_must_be_unique")

    if len(artifact_types) != len(set(artifact_types)):
        errors.append("artifact_types_must_be_unique")

    if len(topological_indices) != len(
        set(topological_indices)
    ):
        errors.append("topological_indices_must_be_unique")

    if valid_nodes:
        expected_nodes = _canonical_nodes(valid_nodes)

        if nodes != expected_nodes:
            errors.append("nodes_must_be_canonical")

    node_id_set = set(node_ids)
    node_index = {
        str(node.get("node_id")): int(
            node.get("topological_index")
        )
        for node in valid_nodes
        if isinstance(node.get("topological_index"), int)
        and not isinstance(
            node.get("topological_index"),
            bool,
        )
    }

    edges = plan.get("edges")

    if not isinstance(edges, list):
        errors.append("edges_must_be_list")
        edges = []
    else:
        for index, edge in enumerate(edges):
            for edge_error in _validate_edge(
                edge,
                node_id_set,
                node_index,
            ):
                errors.append(
                    f"edge:{index}:{edge_error}"
                )

    valid_edges = [
        edge
        for edge in edges
        if isinstance(edge, Mapping)
        and edge.get("source_node_id") in node_id_set
        and edge.get("target_node_id") in node_id_set
    ]

    edge_ids = [
        str(edge.get("edge_id"))
        for edge in valid_edges
    ]

    if len(edge_ids) != len(set(edge_ids)):
        errors.append("edge_ids_must_be_unique")

    if valid_edges and len(node_index) == len(valid_nodes):
        expected_edges = _canonical_edges(
            valid_edges,
            node_index,
        )

        if edges != expected_edges:
            errors.append("edges_must_be_canonical")

    expected_topological_order = [
        str(node["node_id"])
        for node in sorted(
            valid_nodes,
            key=lambda item: (
                int(item["topological_index"]),
                str(item["node_id"]),
            ),
        )
        if isinstance(node.get("topological_index"), int)
        and not isinstance(
            node.get("topological_index"),
            bool,
        )
    ]

    if plan.get("topological_order") != (
        expected_topological_order
    ):
        errors.append("topological_order_mismatch")

    computed_cycle = _has_cycle(
        node_ids,
        valid_edges,
    )

    if not isinstance(plan.get("cycle_detected"), bool):
        errors.append("cycle_detected_must_be_boolean")
    elif plan.get("cycle_detected") != computed_cycle:
        errors.append("cycle_detected_mismatch")

    computed_orphans = _orphan_node_ids(
        node_ids,
        valid_edges,
    )

    if not _valid_canonical_string_list(
        plan.get("orphan_node_ids")
    ):
        errors.append("orphan_node_ids_invalid")
    elif plan.get("orphan_node_ids") != computed_orphans:
        errors.append("orphan_node_ids_mismatch")

    expected_status = _derive_dag_status(
        source_artifact_plan_status=str(source_status),
        cycle_detected=computed_cycle,
        orphan_node_ids=computed_orphans,
    )

    if plan.get("dag_status") not in DAG_STATUSES:
        errors.append("dag_status_invalid")
    elif plan.get("dag_status") != expected_status:
        errors.append("dag_status_mismatch")

    if plan.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if plan.get("roadmap_mode") != ROADMAP_MODE:
        errors.append("roadmap_mode_invalid")

    if plan.get("runtime_execution_status") != "NOT_ALLOWED":
        errors.append("runtime_execution_must_not_be_allowed")

    errors.extend(
        _validate_safety_flags(plan.get("safety_flags"))
    )

    return errors
