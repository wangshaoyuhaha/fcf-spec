import sidecars.sidecar_dag_dependency_guard_app_1 as dag


def test_d3_explicit_allowed_dependency_edges_constant_exists():
    assert hasattr(dag, "EXPLICIT_ALLOWED_DEPENDENCY_EDGES")
    assert (
        "UI-APP-1",
        "OPERATOR-REVIEW-APP-1",
    ) in dag.EXPLICIT_ALLOWED_DEPENDENCY_EDGES
    assert (
        "OPERATOR-REVIEW-APP-1",
        "REPORT-ARCHIVE-APP-1",
    ) in dag.EXPLICIT_ALLOWED_DEPENDENCY_EDGES
