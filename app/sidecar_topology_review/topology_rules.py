from __future__ import annotations

from app.sidecar_topology_review.source_loader import load_completed_sidecar_inventory


def build_dependency_edges() -> tuple[tuple[str, str], ...]:
    edges = []
    for row in load_completed_sidecar_inventory():
        target = str(row["sidecar_id"])
        for upstream in row["allowed_upstream_sidecars"]:
            edges.append((str(upstream), target))
    return tuple(edges)


def validate_dag() -> dict[str, object]:
    rows = load_completed_sidecar_inventory()
    ids = {str(row["sidecar_id"]) for row in rows}
    edges = build_dependency_edges()
    missing = sorted({src for src, _ in edges if src not in ids})
    forward_violations = []
    index = {str(row["sidecar_id"]): int(row["phase_index"]) for row in rows}
    for src, dst in edges:
        if src in index and index[src] >= index[dst]:
            forward_violations.append((src, dst))
    return {
        "dag_required": True,
        "circular_dependency_allowed": False,
        "sidecar_count": len(rows),
        "edge_count": len(edges),
        "missing_upstream_sidecars": tuple(missing),
        "forward_order_violations": tuple(forward_violations),
        "dag_valid": not missing and not forward_violations,
    }
