from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Mapping, Tuple
from urllib.parse import parse_qsl

from .evidence_audit_explorer import (
    EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY,
    EvidenceArtifactNode,
    EvidenceAuditQuery,
)
from .evidence_audit_graph import (
    EvidenceArtifactGraph,
    build_evidence_artifact_graph,
    build_evidence_correlation_lineage,
)
from .evidence_audit_lifecycle import (
    EvidenceLifecycleDossier,
    EvidenceLifecycleItem,
    build_evidence_lifecycle_dossier,
)
from .evidence_audit_risk_ai import (
    EvidenceRiskAIDossier,
    build_evidence_risk_ai_dossier,
)
from .read_model import ConsoleReadModel


_MULTI_VALUE_PARAMETERS = frozenset(
    {
        "artifact_ids",
        "artifact_types",
        "integrity_states",
        "risk_flags",
        "contradiction_codes",
    }
)
_SCALAR_PARAMETERS = frozenset(
    {
        "correlation_id",
        "offset",
        "limit",
        "sort_order",
    }
)
_ALLOWED_PARAMETERS = (
    _MULTI_VALUE_PARAMETERS | _SCALAR_PARAMETERS
)
_MAX_QUERY_LENGTH = 2048
_MAX_QUERY_PAIRS = 100


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _validate_percent_encoding(raw_query: str) -> None:
    index = 0
    while index < len(raw_query):
        if raw_query[index] != "%":
            index += 1
            continue
        if index + 2 >= len(raw_query):
            raise ValueError("query contains invalid percent encoding")
        pair = raw_query[index + 1 : index + 3]
        if any(
            character not in "0123456789abcdefABCDEF"
            for character in pair
        ):
            raise ValueError("query contains invalid percent encoding")
        index += 3


def parse_evidence_audit_query(
    raw_query: str,
) -> EvidenceAuditQuery:
    normalized = str(raw_query)
    if len(normalized) > _MAX_QUERY_LENGTH:
        raise ValueError("query exceeds the maximum length")
    if not normalized:
        return EvidenceAuditQuery()

    _validate_percent_encoding(normalized)
    try:
        pairs = parse_qsl(
            normalized,
            keep_blank_values=True,
            strict_parsing=True,
        )
    except ValueError as exc:
        raise ValueError("query string is malformed") from exc

    if len(pairs) > _MAX_QUERY_PAIRS:
        raise ValueError("query contains too many parameters")

    values: dict[str, object] = {}
    multi_values: dict[str, list[str]] = {
        name: [] for name in _MULTI_VALUE_PARAMETERS
    }

    for key, value in pairs:
        if key not in _ALLOWED_PARAMETERS:
            raise ValueError(
                f"unsupported query parameter: {key}"
            )
        if not value.strip():
            raise ValueError(
                f"query parameter {key} must not be blank"
            )
        if key in _SCALAR_PARAMETERS:
            if key in values:
                raise ValueError(
                    f"query parameter {key} must not be repeated"
                )
            values[key] = value
        else:
            multi_values[key].append(value)

    for key, items in multi_values.items():
        if items:
            values[key] = items

    return EvidenceAuditQuery.from_mapping(values)


@dataclass(frozen=True)
class EvidenceAuditExplorerPageModel:
    path: str
    title: str
    state: str
    query: EvidenceAuditQuery
    selected_artifact_ids: Tuple[str, ...]
    total_registered_artifacts: int
    body_html: str
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True

    def __post_init__(self) -> None:
        EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.by_path(
            self.path
        )
        if self.state not in {
            "AVAILABLE",
            "INCOMPLETE",
            "NO_REGISTERED_EVIDENCE",
            "FILTERED_EMPTY",
        }:
            raise ValueError(
                "unsupported Evidence Audit Explorer page state"
            )
        selected = tuple(self.selected_artifact_ids)
        if len(set(selected)) != len(selected):
            raise ValueError(
                "selected artifact ids must be unique"
            )
        if self.total_registered_artifacts < 0:
            raise ValueError(
                "total_registered_artifacts must be non-negative"
            )
        if not self.title.strip() or not self.body_html.strip():
            raise ValueError("page title and body are required")
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "Evidence Audit Explorer page must remain "
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
        if not self.ai_advisory_only:
            raise ValueError("AI must remain advisory-only")

        object.__setattr__(
            self,
            "selected_artifact_ids",
            selected,
        )


def _has_active_filter(query: EvidenceAuditQuery) -> bool:
    return any(
        (
            query.correlation_id is not None,
            bool(query.artifact_ids),
            bool(query.artifact_types),
            bool(query.integrity_states),
            bool(query.risk_flags),
            bool(query.contradiction_codes),
            query.offset != 0,
            query.limit != 100,
            query.sort_order != "ASC",
        )
    )


def _risk_map(
    dossier: EvidenceRiskAIDossier,
) -> Mapping[str, frozenset[str]]:
    values: dict[str, set[str]] = {}
    for finding in dossier.risk_findings:
        values.setdefault(
            finding.artifact_id,
            set(),
        ).update(finding.risk_flags)
    return {
        artifact_id: frozenset(flags)
        for artifact_id, flags in values.items()
    }


def _contradiction_map(
    dossier: EvidenceRiskAIDossier,
) -> Mapping[str, frozenset[str]]:
    values: dict[str, set[str]] = {}
    for finding in dossier.contradiction_findings:
        values.setdefault(
            finding.artifact_id,
            set(),
        ).update(finding.contradiction_codes)
    return {
        artifact_id: frozenset(codes)
        for artifact_id, codes in values.items()
    }


def _select_nodes(
    graph: EvidenceArtifactGraph,
    dossier: EvidenceRiskAIDossier,
    query: EvidenceAuditQuery,
) -> Tuple[EvidenceArtifactNode, ...]:
    if (
        query.correlation_id is not None
        and query.correlation_id != graph.correlation_id
    ):
        return ()

    risk_by_artifact = _risk_map(dossier)
    contradiction_by_artifact = _contradiction_map(dossier)
    required_risks = set(query.risk_flags)
    required_contradictions = set(
        query.contradiction_codes
    )
    required_states = set(query.integrity_states)

    selected = []
    for node in graph.nodes:
        if (
            query.artifact_ids
            and node.artifact_id not in query.artifact_ids
        ):
            continue
        if (
            query.artifact_types
            and node.artifact_type not in query.artifact_types
        ):
            continue
        if (
            required_states
            and node.integrity_state not in required_states
        ):
            continue
        if (
            required_risks
            and not required_risks.issubset(
                risk_by_artifact.get(
                    node.artifact_id,
                    frozenset(),
                )
            )
        ):
            continue
        if (
            required_contradictions
            and not required_contradictions.issubset(
                contradiction_by_artifact.get(
                    node.artifact_id,
                    frozenset(),
                )
            )
        ):
            continue
        selected.append(node)

    selected.sort(
        key=lambda node: (
            node.artifact_id,
            node.artifact_type,
        ),
        reverse=query.sort_order == "DESC",
    )
    return tuple(
        selected[
            query.offset : query.offset + query.limit
        ]
    )


def _page_state(
    graph: EvidenceArtifactGraph,
    selected_nodes: Tuple[EvidenceArtifactNode, ...],
    query: EvidenceAuditQuery,
) -> str:
    if not graph.nodes:
        return "NO_REGISTERED_EVIDENCE"
    if not selected_nodes and _has_active_filter(query):
        return "FILTERED_EMPTY"
    if graph.state == "INCOMPLETE":
        return "INCOMPLETE"
    return "AVAILABLE"


def _badges(values: Tuple[str, ...]) -> str:
    if not values:
        return "-"
    return "".join(
        f'<span class="badge">{_escape(value)}</span>'
        for value in values
    )


def _table(
    headers: Tuple[str, ...],
    rows: Tuple[Tuple[str, ...], ...],
    empty_message: str,
) -> str:
    if not rows:
        return (
            '<section class="card">'
            f"{_escape(empty_message)}"
            "</section>"
        )
    header_html = "".join(
        f"<th>{_escape(header)}</th>"
        for header in headers
    )
    row_html = "".join(
        "<tr>"
        + "".join(f"<td>{cell}</td>" for cell in row)
        + "</tr>"
        for row in rows
    )
    return f"""
<section class="card">
<table>
<thead><tr>{header_html}</tr></thead>
<tbody>{row_html}</tbody>
</table>
</section>
"""


def _query_summary(query: EvidenceAuditQuery) -> str:
    items = (
        ("correlation_id", query.correlation_id or "-"),
        ("artifact_ids", ",".join(query.artifact_ids) or "-"),
        ("artifact_types", ",".join(query.artifact_types) or "-"),
        (
            "integrity_states",
            ",".join(
                state.value
                for state in query.integrity_states
            )
            or "-",
        ),
        ("risk_flags", ",".join(query.risk_flags) or "-"),
        (
            "contradiction_codes",
            ",".join(query.contradiction_codes) or "-",
        ),
        ("offset", str(query.offset)),
        ("limit", str(query.limit)),
        ("sort_order", query.sort_order),
    )
    rows = "".join(
        f"<li><strong>{_escape(name)}</strong>: "
        f"<code>{_escape(value)}</code></li>"
        for name, value in items
    )
    return (
        '<section class="card">'
        "<h2>Deterministic query</h2>"
        f"<ul>{rows}</ul>"
        "</section>"
    )


def _common_header(
    title: str,
    correlation_id: str,
    state: str,
    selected_count: int,
    total_count: int,
) -> str:
    return f"""
<section class="card">
<h1>{_escape(title)}</h1>
<p>Correlation ID: <code>{_escape(correlation_id)}</code></p>
<p>State: <span class="state">{_escape(state)}</span></p>
<p>Selected registered artifacts: {selected_count} / {total_count}</p>
</section>
"""


def _overview_body(
    graph: EvidenceArtifactGraph,
    dossier: EvidenceRiskAIDossier,
    lifecycle: EvidenceLifecycleDossier,
    query: EvidenceAuditQuery,
    selected_nodes: Tuple[EvidenceArtifactNode, ...],
    state: str,
) -> str:
    lineage = build_evidence_correlation_lineage(graph)
    counts = (
        ("Graph state", graph.state),
        ("Lineage state", lineage.state),
        ("Risk and AI state", dossier.state),
        ("Lifecycle state", lifecycle.state),
        ("Registered nodes", str(len(graph.nodes))),
        ("Registered relationships", str(len(graph.relationships))),
        ("Risk findings", str(len(dossier.risk_findings))),
        (
            "Contradiction findings",
            str(len(dossier.contradiction_findings)),
        ),
        ("AI evidence", str(len(dossier.ai_evidence))),
        ("Lifecycle items", str(len(lifecycle.items))),
        (
            "Unresolved artifact references",
            str(len(graph.unresolved_artifact_ids)),
        ),
    )
    cards = "".join(
        (
            '<section class="card">'
            f"<h2>{_escape(label)}</h2>"
            f"<p>{_escape(value)}</p>"
            "</section>"
        )
        for label, value in counts
    )
    return (
        _common_header(
            "Evidence Overview",
            graph.correlation_id,
            state,
            len(selected_nodes),
            len(graph.nodes),
        )
        + f'<section class="grid">{cards}</section>'
        + _query_summary(query)
    )


def _artifacts_body(
    graph: EvidenceArtifactGraph,
    dossier: EvidenceRiskAIDossier,
    query: EvidenceAuditQuery,
    selected_nodes: Tuple[EvidenceArtifactNode, ...],
    state: str,
) -> str:
    risk_by_artifact = _risk_map(dossier)
    contradiction_by_artifact = _contradiction_map(
        dossier
    )
    rows = tuple(
        (
            _escape(node.artifact_id),
            _escape(node.artifact_type),
            _escape(node.integrity_state.value),
            _escape(node.relative_path),
            f"<code>{_escape(node.content_sha256)}</code>",
            _badges(
                tuple(
                    sorted(
                        risk_by_artifact.get(
                            node.artifact_id,
                            frozenset(),
                        )
                    )
                )
            ),
            _badges(
                tuple(
                    sorted(
                        contradiction_by_artifact.get(
                            node.artifact_id,
                            frozenset(),
                        )
                    )
                )
            ),
        )
        for node in selected_nodes
    )
    return (
        _common_header(
            "Registered Artifacts",
            graph.correlation_id,
            state,
            len(selected_nodes),
            len(graph.nodes),
        )
        + _table(
            (
                "Artifact ID",
                "Type",
                "Integrity",
                "Registered path",
                "SHA-256",
                "Risk flags",
                "Contradictions",
            ),
            rows,
            "No registered artifact matches the query.",
        )
        + _query_summary(query)
    )


def _lineage_body(
    graph: EvidenceArtifactGraph,
    query: EvidenceAuditQuery,
    selected_nodes: Tuple[EvidenceArtifactNode, ...],
    state: str,
) -> str:
    selected_ids = {
        node.artifact_id for node in selected_nodes
    }
    relationships = tuple(
        relationship
        for relationship in graph.relationships
        if (
            relationship.source_artifact_id in selected_ids
            or relationship.target_artifact_id in selected_ids
        )
    )
    rows = tuple(
        (
            _escape(item.source_artifact_id),
            _escape(item.relation.value),
            _escape(item.target_artifact_id),
            _escape(item.correlation_id),
        )
        for item in relationships
    )
    unresolved = _badges(
        graph.unresolved_artifact_ids
    )
    return (
        _common_header(
            "Correlation Lineage",
            graph.correlation_id,
            state,
            len(selected_nodes),
            len(graph.nodes),
        )
        + (
            '<section class="card">'
            "<h2>Unresolved registered references</h2>"
            f"<p>{unresolved}</p>"
            "</section>"
        )
        + _table(
            (
                "Source artifact",
                "Relation",
                "Target artifact",
                "Correlation ID",
            ),
            rows,
            "No registered relationship matches the query.",
        )
        + _query_summary(query)
    )


def _risk_body(
    graph: EvidenceArtifactGraph,
    dossier: EvidenceRiskAIDossier,
    query: EvidenceAuditQuery,
    selected_nodes: Tuple[EvidenceArtifactNode, ...],
    state: str,
) -> str:
    selected_ids = {
        node.artifact_id for node in selected_nodes
    }
    risk_rows = tuple(
        (
            _escape(item.artifact_id),
            _escape(item.artifact_type),
            _escape(item.subject),
            _badges(item.risk_flags),
            _escape(item.severity),
            _escape(item.relative_path),
        )
        for item in dossier.risk_findings
        if item.artifact_id in selected_ids
    )
    contradiction_rows = tuple(
        (
            _escape(item.artifact_id),
            _escape(item.artifact_type),
            _badges(item.contradiction_codes),
            _badges(item.target_artifact_ids),
            _escape(item.status),
        )
        for item in dossier.contradiction_findings
        if item.artifact_id in selected_ids
    )
    ai_rows = tuple(
        (
            _escape(item.artifact_id),
            _escape(item.artifact_type),
            _escape(item.model_label),
            _escape(item.prompt_version),
            _escape(item.evaluation_state),
            _badges(item.evidence_keys),
        )
        for item in dossier.ai_evidence
        if item.artifact_id in selected_ids
    )
    return (
        _common_header(
            "Risk and Contradictions",
            graph.correlation_id,
            state,
            len(selected_nodes),
            len(graph.nodes),
        )
        + _table(
            (
                "Artifact ID",
                "Type",
                "Subject",
                "Risk flags",
                "Severity",
                "Registered path",
            ),
            risk_rows,
            "No explicit registered risk finding matches the query.",
        )
        + _table(
            (
                "Artifact ID",
                "Type",
                "Contradiction codes",
                "Registered targets",
                "Status",
            ),
            contradiction_rows,
            "No explicit registered contradiction matches the query.",
        )
        + _table(
            (
                "Artifact ID",
                "Type",
                "Model",
                "Prompt version",
                "Evaluation state",
                "Evidence keys",
            ),
            ai_rows,
            "No registered AI evidence matches the query.",
        )
        + _query_summary(query)
    )


def _lifecycle_rows(
    lifecycle: EvidenceLifecycleDossier,
    selected_ids: set[str],
    stages: frozenset[str],
) -> Tuple[Tuple[str, ...], ...]:
    return tuple(
        (
            _escape(item.artifact_id),
            _escape(item.artifact_type),
            _escape(item.stage),
            _escape(item.status),
            _escape(item.observed_at),
            _escape(item.relative_path),
            f"<code>{_escape(item.content_sha256)}</code>",
            _badges(item.evidence_keys),
        )
        for item in lifecycle.items
        if (
            item.artifact_id in selected_ids
            and item.stage in stages
        )
    )


def _lifecycle_body(
    title: str,
    graph: EvidenceArtifactGraph,
    lifecycle: EvidenceLifecycleDossier,
    query: EvidenceAuditQuery,
    selected_nodes: Tuple[EvidenceArtifactNode, ...],
    state: str,
    stages: frozenset[str],
    empty_message: str,
) -> str:
    selected_ids = {
        node.artifact_id for node in selected_nodes
    }
    rows = _lifecycle_rows(
        lifecycle,
        selected_ids,
        stages,
    )
    return (
        _common_header(
            title,
            graph.correlation_id,
            state,
            len(selected_nodes),
            len(graph.nodes),
        )
        + _table(
            (
                "Artifact ID",
                "Type",
                "Stage",
                "Status",
                "Observed at",
                "Registered path",
                "SHA-256",
                "Evidence keys",
            ),
            rows,
            empty_message,
        )
        + _query_summary(query)
    )


def build_evidence_audit_explorer_page(
    read_model: ConsoleReadModel,
    path: str,
    raw_query: str = "",
) -> EvidenceAuditExplorerPageModel:
    route = EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.by_path(
        path
    )
    query = parse_evidence_audit_query(raw_query)
    graph = build_evidence_artifact_graph(read_model)
    dossier = build_evidence_risk_ai_dossier(
        read_model,
        graph,
    )
    lifecycle = build_evidence_lifecycle_dossier(
        read_model,
        graph,
    )
    selected_nodes = _select_nodes(
        graph,
        dossier,
        query,
    )
    state = _page_state(
        graph,
        selected_nodes,
        query,
    )

    if path == "/evidence":
        body = _overview_body(
            graph,
            dossier,
            lifecycle,
            query,
            selected_nodes,
            state,
        )
    elif path == "/evidence/artifacts":
        body = _artifacts_body(
            graph,
            dossier,
            query,
            selected_nodes,
            state,
        )
    elif path == "/evidence/lineage":
        body = _lineage_body(
            graph,
            query,
            selected_nodes,
            state,
        )
    elif path == "/evidence/risk":
        body = _risk_body(
            graph,
            dossier,
            query,
            selected_nodes,
            state,
        )
    elif path == "/evidence/validation":
        body = _lifecycle_body(
            "Validation Evidence",
            graph,
            lifecycle,
            query,
            selected_nodes,
            state,
            frozenset(
                {
                    "PAPER_VALIDATION",
                    "SHADOW_OBSERVATION",
                }
            ),
            "No registered validation evidence matches the query.",
        )
    elif path == "/evidence/review":
        body = _lifecycle_body(
            "Operator Review Evidence",
            graph,
            lifecycle,
            query,
            selected_nodes,
            state,
            frozenset({"OPERATOR_REVIEW"}),
            "No registered Operator review evidence matches the query.",
        )
    elif path == "/evidence/archive":
        body = _lifecycle_body(
            "Archive Evidence",
            graph,
            lifecycle,
            query,
            selected_nodes,
            state,
            frozenset({"REPORT_ARCHIVE"}),
            "No registered archive evidence matches the query.",
        )
    else:
        raise KeyError(path)

    body += """
<section class="notice">
Registered-artifact-only and read-only. The explorer cannot mutate evidence,
dispatch workflows, approve, promote, replace baselines, activate AI or
learning, archive automatically, place orders, or execute financial actions.
</section>
"""

    return EvidenceAuditExplorerPageModel(
        path=path,
        title=f"FCF {route.title}",
        state=state,
        query=query,
        selected_artifact_ids=tuple(
            node.artifact_id
            for node in selected_nodes
        ),
        total_registered_artifacts=len(graph.nodes),
        body_html=body,
    )
