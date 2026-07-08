from app.sidecar_topology_review.final_handoff import build_final_handoff


def test_d6_final_handoff_closeout():
    handoff = build_final_handoff()
    assert handoff["app_id"] == "SIDECAR-TOPOLOGY-REVIEW-APP-1"
    assert handoff["stage"] == "D6_FINAL_HANDOFF_CLOSEOUT"
    assert handoff["final_status"] == "COMPLETED"
    assert handoff["source_packet_id"] == "SIDECAR-TOPOLOGY-REVIEW-APP-1-D5"
    assert handoff["sidecar_count"] >= 18
    assert handoff["edge_count"] >= 18
    assert handoff["dag_valid"] is True
    assert handoff["isolation_zone_valid"] is True
    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["operator_review_required"] is True
    assert handoff["core_mutation_allowed"] is False
    assert handoff["p48_core_expansion_allowed"] is False
    assert handoff["trade_action_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False
