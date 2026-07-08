import sidecars.sidecar_dag_dependency_guard_app_1 as dag


def test_d4_syntax_repair_module_imports():
    assert dag.default_sidecar_nodes()
    assert dag.default_dependency_edges()


def test_d4_syntax_repair_default_graph_valid():
    valid, issues = dag.validate_dependency_graph(
        dag.default_sidecar_nodes(),
        dag.default_dependency_edges(),
    )

    assert valid is True
    assert issues == ()


def test_d4_syntax_repair_scanner_allows_boundary_text():
    findings = dag.scan_import_boundary_text(
        "docs/example.md",
        "- no real trading\n- no api key\n- no exchange api\n",
    )

    assert findings == ()


def test_d4_syntax_repair_scanner_blocks_enabled_keyword():
    findings = dag.scan_import_boundary_text(
        "sidecars/example_app/__init__.py",
        "real_trading = True\n",
    )

    assert len(findings) == 1
    assert findings[0].pattern == "real_trading"
