from pathlib import Path


def test_sidecar_topology_review_d1_contract_exists():
    path = Path("docs/sidecar_topology_review_app_1/D1_TOPOLOGY_REVIEW_CONTRACT.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "SIDECAR-TOPOLOGY-REVIEW-APP-1" in text
    assert "governance-only" in text
    assert "Data Ingestion and Quarantine" in text
    assert "Context and Interpretation" in text
    assert "Governance and Review Gate" in text
    assert "Presentation and Immutable Archive" in text


def test_sidecar_topology_review_d1_safety_boundary():
    text = Path("docs/sidecar_topology_review_app_1/D1_TOPOLOGY_REVIEW_CONTRACT.md").read_text(
        encoding="utf-8"
    )
    forbidden_markers = [
        "broker APIs",
        "exchange APIs",
        "wallet APIs",
        "real orders",
        "real trades",
        "deploy anything",
        "create a release",
        "create a tag",
    ]
    for marker in forbidden_markers:
        assert marker in text