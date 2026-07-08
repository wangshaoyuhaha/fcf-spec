from sidecars.sidecar_dag_dependency_guard_app_1 import (
    default_dependency_edges,
    default_sidecar_nodes,
    validate_dependency_graph,
)


def test_d3_report_archive_is_archive_audit():
    nodes = {node.name: node for node in default_sidecar_nodes()}

    assert nodes["REPORT-ARCHIVE-APP-1"].zone == "archive_audit"


def test_d3_repaired_default_dependency_graph_is_valid():
    valid, issues = validate_dependency_graph(
        default_sidecar_nodes(),
        default_dependency_edges(),
    )

    assert valid is True
    assert issues == ()
