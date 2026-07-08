from __future__ import annotations

from app.sidecar_topology_review.source_loader import load_completed_sidecar_inventory
from app.sidecar_topology_review.topology_rules import validate_dag
from app.sidecar_topology_review.zone_model import validate_zone_contract


def build_topology_review_packet() -> dict[str, object]:
    rows = load_completed_sidecar_inventory()
    dag = validate_dag()
    zone = validate_zone_contract()
    sidecar_ids = [str(row["sidecar_id"]) for row in rows]
    duplicate_ids = tuple(sorted({item for item in sidecar_ids if sidecar_ids.count(item) > 1}))
    packet_valid = (
        dag["dag_valid"] is True
        and zone["isolation_zone_valid"] is True
        and not duplicate_ids
    )
    return {
        "packet_id": "SIDECAR-TOPOLOGY-REVIEW-APP-1-D5",
        "review_status": "TOPOLOGY_REVIEW_PASS" if packet_valid else "TOPOLOGY_REVIEW_BLOCKED",
        "sidecar_count": len(rows),
        "edge_count": dag["edge_count"],
        "duplicate_sidecar_ids": duplicate_ids,
        "dag_required": True,
        "dag_valid": dag["dag_valid"],
        "isolation_zone_valid": zone["isolation_zone_valid"],
        "missing_upstream_sidecars": dag["missing_upstream_sidecars"],
        "forward_order_violations": dag["forward_order_violations"],
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "core_mutation_allowed": False,
        "p48_core_expansion_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
    }
