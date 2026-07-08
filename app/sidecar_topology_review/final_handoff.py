from __future__ import annotations

from app.sidecar_topology_review.review_packet import build_topology_review_packet


def build_final_handoff() -> dict[str, object]:
    packet = build_topology_review_packet()
    return {
        "app_id": "SIDECAR-TOPOLOGY-REVIEW-APP-1",
        "stage": "D6_FINAL_HANDOFF_CLOSEOUT",
        "final_status": "COMPLETED" if packet["review_status"] == "TOPOLOGY_REVIEW_PASS" else "BLOCKED",
        "source_packet_id": packet["packet_id"],
        "sidecar_count": packet["sidecar_count"],
        "edge_count": packet["edge_count"],
        "dag_valid": packet["dag_valid"],
        "isolation_zone_valid": packet["isolation_zone_valid"],
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
        "next_step": "merge review on main after operator confirmation",
    }
