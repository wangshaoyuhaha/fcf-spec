from sidecars.sidecar_dag_dependency_guard_app_1 import (
    SidecarDependencyEdge,
    SidecarDependencyNode,
    build_node_index,
    default_dependency_edges,
    default_sidecar_nodes,
    validate_dependency_direction,
    validate_dependency_graph,
    validate_sidecar_node,
)


def test_d2_accepts_valid_sidecar_node():
    node = SidecarDependencyNode(
        name="DATA-APP-1",
        zone="data_foundation",
        status="completed",
        read_only=True,
        operator_review_required=True,
    )

    valid, issues = validate_sidecar_node(node)

    assert valid is True
    assert issues == ()


def test_d2_rejects_non_read_only_node():
    node = SidecarDependencyNode(
        name="DATA-APP-1",
        zone="data_foundation",
        status="completed",
        read_only=False,
        operator_review_required=True,
    )

    valid, issues = validate_sidecar_node(node)

    assert valid is False
    assert "node_must_be_read_only" in issues


def test_d2_builds_node_index():
    nodes = (
        SidecarDependencyNode("DATA-APP-1", "data_foundation", "completed", True, True),
        SidecarDependencyNode("STOCK-APP-1", "research_intelligence", "completed", True, True),
    )

    index = build_node_index(nodes)

    assert tuple(index.keys()) == ("DATA-APP-1", "STOCK-APP-1")
    assert index["DATA-APP-1"].zone == "data_foundation"


def test_d2_accepts_forward_dependency_direction():
    nodes = (
        SidecarDependencyNode("DATA-APP-1", "data_foundation", "completed", True, True),
        SidecarDependencyNode("STOCK-APP-1", "research_intelligence", "completed", True, True),
    )
    edge = SidecarDependencyEdge(
        source="DATA-APP-1",
        target="STOCK-APP-1",
        reason="data to stock",
    )

    valid, issues = validate_dependency_direction(edge, build_node_index(nodes))

    assert valid is True
    assert issues == ()


def test_d2_rejects_reverse_dependency_direction():
    nodes = (
        SidecarDependencyNode("DATA-APP-1", "data_foundation", "completed", True, True),
        SidecarDependencyNode("STOCK-APP-1", "research_intelligence", "completed", True, True),
    )
    edge = SidecarDependencyEdge(
        source="STOCK-APP-1",
        target="DATA-APP-1",
        reason="invalid reverse dependency",
    )

    valid, issues = validate_dependency_direction(edge, build_node_index(nodes))

    assert valid is False
    assert "reverse_dependency" in issues


def test_d2_rejects_unknown_target_node():
    nodes = (
        SidecarDependencyNode("DATA-APP-1", "data_foundation", "completed", True, True),
    )
    edge = SidecarDependencyEdge(
        source="DATA-APP-1",
        target="UNKNOWN-APP-1",
        reason="invalid unknown target",
    )

    valid, issues = validate_dependency_direction(edge, build_node_index(nodes))

    assert valid is False
    assert "unknown_target_node" in issues


def test_d2_default_dependency_graph_is_valid():
    valid, issues = validate_dependency_graph(
        default_sidecar_nodes(),
        default_dependency_edges(),
    )

    assert valid is True
    assert issues == ()


def test_d2_dependency_graph_rejects_reverse_edge():
    nodes = (
        SidecarDependencyNode("DATA-APP-1", "data_foundation", "completed", True, True),
        SidecarDependencyNode("UI-APP-1", "presentation_handoff", "completed", True, True),
    )
    edges = (
        SidecarDependencyEdge(
            source="UI-APP-1",
            target="DATA-APP-1",
            reason="invalid ui reverse dependency",
        ),
    )

    valid, issues = validate_dependency_graph(nodes, edges)

    assert valid is False
    assert "reverse_dependency" in issues
