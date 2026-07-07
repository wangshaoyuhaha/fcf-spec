from pathlib import Path


def test_sidecar_topology_review_d2_inventory_exists():
    path = Path("docs/sidecar_topology_review_app_1/D2_COMPLETED_SIDECAR_INVENTORY.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "D2 Completed Sidecar Inventory" in text
    assert "DIFY-UI-HANDOFF-APP-1" in text
    assert "STOCK-APP-1" in text
    assert "AI-CONTEXT-1" in text
    assert "UI-APP-1" in text


def test_sidecar_topology_review_d2_inventory_safety_boundary():
    text = Path("docs/sidecar_topology_review_app_1/D2_COMPLETED_SIDECAR_INVENTORY.md").read_text(
        encoding="utf-8"
    )
    required = [
        "paper-only",
        "local-only",
        "read-only",
        "governance-only",
        "operator-review-only",
        "no deploy",
        "no release",
        "no tag",
        "no real trading",
        "no Dify API write",
    ]
    for item in required:
        assert item in text