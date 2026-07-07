from pathlib import Path


def test_sidecar_topology_review_d4_dag_review_exists():
    path = Path("docs/sidecar_topology_review_app_1/D4_DEPENDENCY_DAG_REVIEW.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "D4 Dependency DAG Review" in text
    assert "dependency DAG" in text
    assert "Circular dependency rules" in text
    assert "Forbidden reverse edges" in text


def test_sidecar_topology_review_d4_required_edges():
    text = Path("docs/sidecar_topology_review_app_1/D4_DEPENDENCY_DAG_REVIEW.md").read_text(
        encoding="utf-8"
    )
    required_edges = [
        "DATA-QUALITY-OPS-APP-1 | STOCK-APP-1",
        "STOCK-APP-1 | AI-CONTEXT-1",
        "AI-CONTEXT-1 | MARKET-SCENARIO-APP-1",
        "SIGNAL-VALIDATION-APP-1 | BACKTEST-REVIEW-APP-1",
        "OPERATOR-REVIEW-APP-1 | UI-APP-1",
        "REPORT-ARCHIVE-APP-1 | DIFY-UI-HANDOFF-APP-1",
    ]
    for edge in required_edges:
        assert edge in text


def test_sidecar_topology_review_d4_forbidden_reverse_edges():
    text = Path("docs/sidecar_topology_review_app_1/D4_DEPENDENCY_DAG_REVIEW.md").read_text(
        encoding="utf-8"
    )
    required = [
        "UI-APP-1 | STOCK-APP-1",
        "DIFY-UI-HANDOFF-APP-1 | AI-CONTEXT-1",
        "REPORT-ARCHIVE-APP-1 | SIGNAL-VALIDATION-APP-1",
        "OPERATOR-REVIEW-APP-1 | DATA-QUALITY-OPS-APP-1",
        "SIDECAR-TOPOLOGY-REVIEW-APP-1 | core P1-P47",
    ]
    for item in required:
        assert item in text


def test_sidecar_topology_review_d4_safety_boundary():
    text = Path("docs/sidecar_topology_review_app_1/D4_DEPENDENCY_DAG_REVIEW.md").read_text(
        encoding="utf-8"
    )
    required = [
        "paper-only",
        "local-only",
        "read-only",
        "governance-only",
        "operator-review-only",
        "no P48",
        "no core mutation",
        "no real order",
        "no real execution",
        "no Dify API write",
        "no deploy",
        "no release",
        "no tag",
    ]
    for item in required:
        assert item in text