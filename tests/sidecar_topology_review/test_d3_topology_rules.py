from app.sidecar_topology_review.topology_rules import build_dependency_edges, validate_dag


def test_d3_topology_edges_and_dag_validation():
    edges = build_dependency_edges()
    result = validate_dag()
    assert len(edges) >= 18
    assert ("DIFY-UI-HANDOFF-APP-1", "CORRELATION-ID-TRACEABILITY-APP-1") in edges
    assert result["dag_required"] is True
    assert result["circular_dependency_allowed"] is False
    assert result["sidecar_count"] >= 18
    assert result["edge_count"] >= 18
    assert result["missing_upstream_sidecars"] == ()
    assert result["forward_order_violations"] == ()
    assert result["dag_valid"] is True
