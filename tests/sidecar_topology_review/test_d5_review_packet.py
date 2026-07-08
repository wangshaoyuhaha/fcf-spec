from app.sidecar_topology_review.review_packet import build_topology_review_packet


def test_d5_topology_review_packet():
    packet = build_topology_review_packet()
    assert packet["packet_id"] == "SIDECAR-TOPOLOGY-REVIEW-APP-1-D5"
    assert packet["review_status"] == "TOPOLOGY_REVIEW_PASS"
    assert packet["sidecar_count"] >= 18
    assert packet["edge_count"] >= 18
    assert packet["duplicate_sidecar_ids"] == ()
    assert packet["dag_required"] is True
    assert packet["dag_valid"] is True
    assert packet["isolation_zone_valid"] is True
    assert packet["missing_upstream_sidecars"] == ()
    assert packet["forward_order_violations"] == ()
    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["core_mutation_allowed"] is False
    assert packet["p48_core_expansion_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False
    assert packet["tag_allowed"] is False
    assert packet["release_allowed"] is False
    assert packet["deploy_allowed"] is False
