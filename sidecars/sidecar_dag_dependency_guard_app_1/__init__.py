"""SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D1.

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


@dataclass(frozen=True)
class SidecarDependencyEdge:
    source: str
    target: str
    reason: str


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
