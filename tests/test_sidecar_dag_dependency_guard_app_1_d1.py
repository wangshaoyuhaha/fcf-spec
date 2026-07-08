from sidecars.sidecar_dag_dependency_guard_app_1 import (
    SidecarDependencyEdge,
    build_adjacency,
    has_cycle,
    validate_dependency_dag,
    validate_dependency_edge,
)


def test_d1_accepts_valid_dependency_edge():
    edge = SidecarDependencyEdge(
        source="DATA-APP-1",
        target="STOCK-APP-1",
        reason="stock app reads clean universe from data app",
    )

    valid, issues = validate_dependency_edge(edge)

    assert valid is True
    assert issues == ()


def test_d1_rejects_self_dependency():
    edge = SidecarDependencyEdge(
        source="DATA-APP-1",
        target="DATA-APP-1",
        reason="invalid self dependency",
    )

    valid, issues = validate_dependency_edge(edge)

    assert valid is False
    assert "self_dependency" in issues


def test_d1_rejects_forbidden_core_mutation_target():
    edge = SidecarDependencyEdge(
        source="STOCK-APP-1",
        target="core_mutation",
        reason="invalid core mutation",
    )

    valid, issues = validate_dependency_edge(edge)

    assert valid is False
    assert "forbidden_dependency_target" in issues


def test_d1_builds_adjacency():
    edges = [
        SidecarDependencyEdge(
            source="DATA-APP-1",
            target="STOCK-APP-1",
            reason="data to stock",
        ),
        SidecarDependencyEdge(
            source="STOCK-APP-1",
            target="AI-CONTEXT-1",
            reason="stock to context",
        ),
    ]

    adjacency = build_adjacency(edges)

    assert adjacency["DATA-APP-1"] == ("STOCK-APP-1",)
    assert adjacency["STOCK-APP-1"] == ("AI-CONTEXT-1",)
    assert adjacency["AI-CONTEXT-1"] == ()


def test_d1_detects_cycle():
    edges = [
        SidecarDependencyEdge(
            source="DATA-APP-1",
            target="STOCK-APP-1",
            reason="data to stock",
        ),
        SidecarDependencyEdge(
            source="STOCK-APP-1",
            target="DATA-APP-1",
            reason="invalid reverse dependency",
        ),
    ]

    assert has_cycle(edges) is True


def test_d1_validates_acyclic_dag():
    edges = [
        SidecarDependencyEdge(
            source="DATA-APP-1",
            target="STOCK-APP-1",
            reason="data to stock",
        ),
        SidecarDependencyEdge(
            source="STOCK-APP-1",
            target="AI-CONTEXT-1",
            reason="stock to context",
        ),
        SidecarDependencyEdge(
            source="AI-CONTEXT-1",
            target="UI-APP-1",
            reason="context to ui",
        ),
    ]

    valid, issues = validate_dependency_dag(edges)

    assert valid is True
    assert issues == ()


def test_d1_rejects_cyclic_dag():
    edges = [
        SidecarDependencyEdge(
            source="DATA-APP-1",
            target="STOCK-APP-1",
            reason="data to stock",
        ),
        SidecarDependencyEdge(
            source="STOCK-APP-1",
            target="DATA-APP-1",
            reason="invalid reverse dependency",
        ),
    ]

    valid, issues = validate_dependency_dag(edges)

    assert valid is False
    assert "cycle_detected" in issues
