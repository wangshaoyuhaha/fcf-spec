from sidecars.sidecar_dag_dependency_guard_app_1 import (
    SidecarDependencyEdge,
    SidecarDependencyNode,
    build_node_index,
    default_dependency_edges,
    default_sidecar_nodes,
    validate_dependency_direction,
    validate_dependency_graph,
)


def test_d3_report_archive_is_archive_audit():
    nodes = {node.name: node for node in default_sidecar_nodes()}

    assert nodes["REPORT-ARCHIVE-APP-1"].zone == "archive_audit"


def test_d3_allows_ui_to_operator_review_handoff():
    nodes = {node.name: node for node in default_sidecar_nodes()}
    edge = SidecarDependencyEdge(
        source="UI-APP-1",
        target="OPERATOR-REVIEW-APP-1",
        reason="read-only UI artifact to paper review",
    )

    valid, issues = validate_dependency_direction(edge, nodes)

    assert valid is True
    assert issues == ()


def test_d3_allows_operator_review_to_report_archive_handoff():
    nodes = {node.name: node for node in default_sidecar_nodes()}
    edge = SidecarDependencyEdge(
        source="OPERATOR-REVIEW-APP-1",
        target="REPORT-ARCHIVE-APP-1",
        reason="paper review to archive",
    )

    valid, issues = validate_dependency_direction(edge, nodes)

    assert valid is True
    assert issues == ()


def test_d3_still_rejects_ui_to_data_reverse_dependency():
    nodes = (
        SidecarDependencyNode("DATA-APP-1", "data_foundation", "completed", True, True),
        SidecarDependencyNode("UI-APP-1", "presentation_handoff", "completed", True, True),
    )
    edge = SidecarDependencyEdge(
        source="UI-APP-1",
        target="DATA-APP-1",
        reason="invalid reverse dependency",
    )

    valid, issues = validate_dependency_direction(edge, build_node_index(nodes))

    assert valid is False
    assert "reverse_dependency" in issues


def test_d3_repaired_default_dependency_graph_is_valid():
    valid, issues = validate_dependency_graph(
        default_sidecar_nodes(),
        default_dependency_edges(),
    )

    assert valid is True
    assert issues == ()
