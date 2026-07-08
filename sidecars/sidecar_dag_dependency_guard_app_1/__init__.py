"""SIDECAR-DAG-DEPENDENCY-GUARD-APP-1.

Read-only dependency guard helpers for sidecar DAG validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


FORBIDDEN_TARGETS = frozenset(
    {
        "core_mutation",
        "p48_core_expansion",
        "source_mutation",
        "source_deletion",
        "source_overwrite",
        "score_mutation",
        "reason_code_mutation",
        "risk_flag_deletion",
        "risk_flag_downgrade",
        "real_trading",
        "real_execution",
        "broker_api",
        "exchange_api",
        "api_key",
        "buy_button",
        "sell_button",
        "order_button",
        "tag",
        "release",
        "deploy",
    }
)

ALLOWED_SIDECAR_ZONES = frozenset(
    {
        "data_foundation",
        "research_intelligence",
        "governance_review",
        "presentation_handoff",
        "archive_audit",
    }
)

ZONE_ORDER = {
    "data_foundation": 1,
    "research_intelligence": 2,
    "governance_review": 3,
    "presentation_handoff": 4,
    "archive_audit": 5,
}

EXPLICIT_ALLOWED_DEPENDENCY_EDGES = frozenset(
    {
        ("UI-APP-1", "OPERATOR-REVIEW-APP-1"),
        ("OPERATOR-REVIEW-APP-1", "REPORT-ARCHIVE-APP-1"),
    }
)

FORBIDDEN_IMPORT_PATTERNS = frozenset(
    {
        "from sidecars import",
        "import sidecars",
        "core_mutation",
        "p48_core_expansion",
        "real_trading",
        "real_execution",
        "broker_api",
        "exchange_api",
        "api_key",
        "wallet_private_key",
        "buy_button",
        "sell_button",
        "order_button",
    }
)


@dataclass(frozen=True)
class SidecarDependencyEdge:
    source: str
    target: str
    reason: str


@dataclass(frozen=True)
class SidecarDependencyNode:
    name: str
    zone: str
    status: str
    read_only: bool
    operator_review_required: bool


@dataclass(frozen=True)
class DependencyPolicyDecision:
    source_zone: str
    target_zone: str
    allowed: bool
    reason: str


@dataclass(frozen=True)
class DependencyViolation:
    source: str
    target: str
    violation_type: str
    reason: str


@dataclass(frozen=True)
class DependencyGraphReport:
    node_count: int
    edge_count: int
    violation_count: int
    has_cycle: bool
    valid: bool
    violations: tuple[DependencyViolation, ...]


@dataclass(frozen=True)
class ImportBoundaryFinding:
    path: str
    line_number: int
    pattern: str
    finding_type: str


@dataclass(frozen=True)
class ImportBoundaryScanReport:
    scanned_file_count: int
    finding_count: int
    findings: tuple[ImportBoundaryFinding, ...]
    valid: bool


def validate_dependency_edge(edge: SidecarDependencyEdge) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    if not edge.source.strip():
        issues.append("missing_source")

    if not edge.target.strip():
        issues.append("missing_target")

    if not edge.reason.strip():
        issues.append("missing_reason")

    if edge.source == edge.target:
        issues.append("self_dependency")

    if edge.target in FORBIDDEN_TARGETS:
        issues.append("forbidden_dependency_target")

    return (not issues, tuple(issues))


def build_adjacency(edges: Iterable[SidecarDependencyEdge]) -> dict[str, tuple[str, ...]]:
    adjacency: dict[str, list[str]] = {}

    for edge in edges:
        valid, issues = validate_dependency_edge(edge)
        if not valid:
            raise ValueError(",".join(issues))

        adjacency.setdefault(edge.source, []).append(edge.target)
        adjacency.setdefault(edge.target, [])

    return {
        node: tuple(sorted(dict.fromkeys(targets)))
        for node, targets in sorted(adjacency.items())
    }


def has_cycle(edges: Iterable[SidecarDependencyEdge]) -> bool:
    adjacency = build_adjacency(edges)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False

        visiting.add(node)

        for target in adjacency.get(node, ()):
            if visit(target):
                return True

        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in adjacency)


def validate_dependency_dag(edges: Iterable[SidecarDependencyEdge]) -> tuple[bool, tuple[str, ...]]:
    edge_tuple = tuple(edges)
    issues: list[str] = []

    for edge in edge_tuple:
        valid, edge_issues = validate_dependency_edge(edge)
        if not valid:
            issues.extend(edge_issues)

    if not issues and has_cycle(edge_tuple):
        issues.append("cycle_detected")

    return (not issues, tuple(sorted(dict.fromkeys(issues))))


def validate_sidecar_node(node: SidecarDependencyNode) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    if not node.name.strip():
        issues.append("missing_node_name")

    if node.zone not in ALLOWED_SIDECAR_ZONES:
        issues.append("invalid_zone")

    if not node.status.strip():
        issues.append("missing_status")

    if node.read_only is not True:
        issues.append("node_must_be_read_only")

    if node.operator_review_required is not True:
        issues.append("operator_review_not_required")

    return (not issues, tuple(issues))


def build_node_index(nodes: Iterable[SidecarDependencyNode]) -> dict[str, SidecarDependencyNode]:
    index: dict[str, SidecarDependencyNode] = {}

    for node in nodes:
        valid, issues = validate_sidecar_node(node)
        if not valid:
            raise ValueError(",".join(issues))

        if node.name in index:
            raise ValueError("duplicate_node")

        index[node.name] = node

    return dict(sorted(index.items()))


def evaluate_zone_policy(source_zone: str, target_zone: str) -> DependencyPolicyDecision:
    if source_zone not in ZONE_ORDER:
        return DependencyPolicyDecision(source_zone, target_zone, False, "unknown_source_zone")

    if target_zone not in ZONE_ORDER:
        return DependencyPolicyDecision(source_zone, target_zone, False, "unknown_target_zone")

    if ZONE_ORDER[source_zone] > ZONE_ORDER[target_zone]:
        return DependencyPolicyDecision(source_zone, target_zone, False, "reverse_dependency")

    return DependencyPolicyDecision(
        source_zone,
        target_zone,
        True,
        "allowed_forward_or_same_zone_dependency",
    )


def validate_dependency_direction(
    edge: SidecarDependencyEdge,
    node_index: dict[str, SidecarDependencyNode],
) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    valid_edge, edge_issues = validate_dependency_edge(edge)
    if not valid_edge:
        issues.extend(edge_issues)
        return (False, tuple(issues))

    if edge.source not in node_index:
        issues.append("unknown_source_node")

    if edge.target not in node_index:
        issues.append("unknown_target_node")

    if issues:
        return (False, tuple(issues))

    if (edge.source, edge.target) in EXPLICIT_ALLOWED_DEPENDENCY_EDGES:
        return (True, ())

    decision = evaluate_zone_policy(
        node_index[edge.source].zone,
        node_index[edge.target].zone,
    )

    if not decision.allowed:
        issues.append(decision.reason)

    return (not issues, tuple(issues))


def validate_dependency_graph(
    nodes: Iterable[SidecarDependencyNode],
    edges: Iterable[SidecarDependencyEdge],
) -> tuple[bool, tuple[str, ...]]:
    issues: list[str] = []

    try:
        node_index = build_node_index(nodes)
    except ValueError as exc:
        return (False, tuple(str(exc).split(",")))

    edge_tuple = tuple(edges)

    for edge in edge_tuple:
        valid, edge_issues = validate_dependency_direction(edge, node_index)
        if not valid:
            issues.extend(edge_issues)

    if not issues and has_cycle(edge_tuple):
        issues.append("cycle_detected")

    return (not issues, tuple(sorted(dict.fromkeys(issues))))


def collect_dependency_violations(
    nodes: Iterable[SidecarDependencyNode],
    edges: Iterable[SidecarDependencyEdge],
) -> tuple[DependencyViolation, ...]:
    violations: list[DependencyViolation] = []

    try:
        node_index = build_node_index(nodes)
    except ValueError as exc:
        return (
            DependencyViolation(
                source="node_registry",
                target="node_registry",
                violation_type="invalid_node_registry",
                reason=str(exc),
            ),
        )

    edge_tuple = tuple(edges)

    for edge in edge_tuple:
        valid, issues = validate_dependency_direction(edge, node_index)
        if not valid:
            violations.extend(
                DependencyViolation(edge.source, edge.target, issue, edge.reason)
                for issue in issues
            )

    if not violations and has_cycle(edge_tuple):
        violations.append(
            DependencyViolation(
                source="dependency_graph",
                target="dependency_graph",
                violation_type="cycle_detected",
                reason="dependency graph must be acyclic",
            )
        )

    return tuple(violations)


def build_dependency_graph_report(
    nodes: Iterable[SidecarDependencyNode],
    edges: Iterable[SidecarDependencyEdge],
) -> DependencyGraphReport:
    node_tuple = tuple(nodes)
    edge_tuple = tuple(edges)
    violations = collect_dependency_violations(node_tuple, edge_tuple)
    graph_has_cycle = False if violations else has_cycle(edge_tuple)

    return DependencyGraphReport(
        node_count=len(node_tuple),
        edge_count=len(edge_tuple),
        violation_count=len(violations),
        has_cycle=graph_has_cycle,
        valid=not violations and not graph_has_cycle,
        violations=violations,
    )


def classify_import_boundary_path(path: str) -> str:
    normalized = path.replace("\\", "/")

    if normalized.startswith("core/") or "/core/" in normalized:
        return "core"

    if normalized.startswith("sidecars/") or "/sidecars/" in normalized:
        return "sidecar"

    if normalized.startswith("tests/") or "/tests/" in normalized:
        return "test"

    return "other"


def _is_enabled_forbidden_pattern(pattern: str, normalized_line: str) -> bool:
    return (
        f"{pattern} = true" in normalized_line
        or f"{pattern}=true" in normalized_line
        or f"{pattern} = 'forbidden'" in normalized_line
        or f'{pattern} = "forbidden"' in normalized_line
        or f"{pattern}()" in normalized_line
    )


def scan_import_boundary_text(path: str, text: str) -> tuple[ImportBoundaryFinding, ...]:
    path_type = classify_import_boundary_path(path)
    findings: list[ImportBoundaryFinding] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized_line = line.strip().lower()

        if not normalized_line:
            continue

        if path_type == "core" and (
            normalized_line.startswith("from sidecars")
            or normalized_line.startswith("import sidecars")
        ):
            findings.append(
                ImportBoundaryFinding(
                    path=path,
                    line_number=line_number,
                    pattern="core_imports_sidecars",
                    finding_type="core_sidecar_import_violation",
                )
            )

        for pattern in FORBIDDEN_IMPORT_PATTERNS:
            if pattern not in normalized_line:
                continue

            if pattern in {"from sidecars import", "import sidecars"} and path_type != "core":
                continue

            if pattern not in {"from sidecars import", "import sidecars"}:
                if not _is_enabled_forbidden_pattern(pattern, normalized_line):
                    continue

            findings.append(
                ImportBoundaryFinding(
                    path=path,
                    line_number=line_number,
                    pattern=pattern,
                    finding_type="forbidden_pattern",
                )
            )

    return tuple(findings)


def build_import_boundary_scan_report(
    file_text_by_path: dict[str, str],
) -> ImportBoundaryScanReport:
    findings: list[ImportBoundaryFinding] = []

    for path, text in sorted(file_text_by_path.items()):
        findings.extend(scan_import_boundary_text(path, text))

    finding_tuple = tuple(findings)

    return ImportBoundaryScanReport(
        scanned_file_count=len(file_text_by_path),
        finding_count=len(finding_tuple),
        findings=finding_tuple,
        valid=len(finding_tuple) == 0,
    )


def default_sidecar_nodes() -> tuple[SidecarDependencyNode, ...]:
    return (
        SidecarDependencyNode("DATA-APP-1", "data_foundation", "completed", True, True),
        SidecarDependencyNode("DATA-QUALITY-OPS-APP-1", "data_foundation", "completed", True, True),
        SidecarDependencyNode("STOCK-APP-1", "research_intelligence", "completed", True, True),
        SidecarDependencyNode("AI-CONTEXT-1", "research_intelligence", "completed", True, True),
        SidecarDependencyNode("MARKET-SCENARIO-APP-1", "research_intelligence", "completed", True, True),
        SidecarDependencyNode("BACKTEST-REVIEW-APP-1", "research_intelligence", "completed", True, True),
        SidecarDependencyNode("SIGNAL-VALIDATION-APP-1", "governance_review", "completed", True, True),
        SidecarDependencyNode("MODEL-GOVERNANCE-APP-1", "governance_review", "completed", True, True),
        SidecarDependencyNode("OPERATOR-REVIEW-APP-1", "governance_review", "completed", True, True),
        SidecarDependencyNode("UI-APP-1", "presentation_handoff", "completed", True, True),
        SidecarDependencyNode("UI-RISK-FLAG-VISIBILITY-APP-1", "presentation_handoff", "completed", True, True),
        SidecarDependencyNode("REPORT-ARCHIVE-APP-1", "archive_audit", "completed", True, True),
        SidecarDependencyNode("ARCHIVE-CORRELATION-ROLLUP-APP-1", "archive_audit", "completed", True, True),
        SidecarDependencyNode("SIDECAR-DAG-DEPENDENCY-GUARD-APP-1", "archive_audit", "active", True, True),
    )


def default_dependency_edges() -> tuple[SidecarDependencyEdge, ...]:
    return (
        SidecarDependencyEdge("DATA-APP-1", "STOCK-APP-1", "clean universe to stock ranking"),
        SidecarDependencyEdge("STOCK-APP-1", "AI-CONTEXT-1", "ranked watchlist to explanation"),
        SidecarDependencyEdge("AI-CONTEXT-1", "UI-APP-1", "explanation to read-only UI"),
        SidecarDependencyEdge("UI-APP-1", "OPERATOR-REVIEW-APP-1", "UI report to operator review"),
        SidecarDependencyEdge("OPERATOR-REVIEW-APP-1", "REPORT-ARCHIVE-APP-1", "operator review to archive"),
        SidecarDependencyEdge("REPORT-ARCHIVE-APP-1", "ARCHIVE-CORRELATION-ROLLUP-APP-1", "archive to correlation rollup"),
        SidecarDependencyEdge("ARCHIVE-CORRELATION-ROLLUP-APP-1", "SIDECAR-DAG-DEPENDENCY-GUARD-APP-1", "rollup to dag guard"),
    )
