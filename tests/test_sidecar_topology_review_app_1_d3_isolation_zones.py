from pathlib import Path


def test_sidecar_topology_review_d3_isolation_zone_mapping_exists():
    path = Path("docs/sidecar_topology_review_app_1/D3_ISOLATION_ZONE_MAPPING.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "D3 Isolation Zone Mapping" in text
    assert "Data Ingestion and Quarantine" in text
    assert "Context and Interpretation" in text
    assert "Governance and Review Gate" in text
    assert "Presentation and Immutable Archive" in text


def test_sidecar_topology_review_d3_zone_membership():
    text = Path("docs/sidecar_topology_review_app_1/D3_ISOLATION_ZONE_MAPPING.md").read_text(
        encoding="utf-8"
    )
    required_sidecars = [
        "DATA-QUALITY-OPS-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
        "MARKET-SCENARIO-APP-1",
        "MODEL-GOVERNANCE-APP-1",
        "SIGNAL-VALIDATION-APP-1",
        "OPERATOR-REVIEW-APP-1",
        "BACKTEST-REVIEW-APP-1",
        "UI-APP-1",
        "REPORT-ARCHIVE-APP-1",
        "DIFY-UI-HANDOFF-APP-1",
    ]
    for sidecar in required_sidecars:
        assert sidecar in text


def test_sidecar_topology_review_d3_direction_rules():
    text = Path("docs/sidecar_topology_review_app_1/D3_ISOLATION_ZONE_MAPPING.md").read_text(
        encoding="utf-8"
    )
    assert "Allowed direction" in text
    assert "Disallowed direction" in text
    assert "later zones must not mutate earlier-zone source artifacts" in text


def test_sidecar_topology_review_d3_safety_boundary():
    text = Path("docs/sidecar_topology_review_app_1/D3_ISOLATION_ZONE_MAPPING.md").read_text(
        encoding="utf-8"
    )
    required = [
        "paper-only",
        "local-only",
        "read-only",
        "governance-only",
        "operator-review-only",
        "no real order",
        "no real execution",
        "no Dify API write",
        "no deploy",
        "no release",
        "no tag",
    ]
    for item in required:
        assert item in text