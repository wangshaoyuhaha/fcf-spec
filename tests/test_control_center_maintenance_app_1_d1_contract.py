from pathlib import Path


def test_control_center_maintenance_d1_contract_exists():
    path = Path("docs/control_center_maintenance_app_1/D1_CONTROL_CENTER_MAINTENANCE_CONTRACT.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "CONTROL-CENTER-MAINTENANCE-APP-1" in text
    assert "governance-only" in text
    assert "mandatory maintenance rules" in text
    assert "source of truth" in text


def test_control_center_maintenance_d1_required_fields():
    text = Path("docs/control_center_maintenance_app_1/D1_CONTROL_CENTER_MAINTENANCE_CONTRACT.md").read_text(
        encoding="utf-8"
    )
    required = [
        "sidecar name",
        "branch name",
        "main merge commit",
        "final branch commit",
        "validation result",
        "pytest count",
        "final git status",
        "no tag confirmation",
        "no release confirmation",
        "no deploy confirmation",
        "deferred backlog changes",
    ]
    for item in required:
        assert item in text


def test_control_center_maintenance_d1_safety_boundary():
    text = Path("docs/control_center_maintenance_app_1/D1_CONTROL_CENTER_MAINTENANCE_CONTRACT.md").read_text(
        encoding="utf-8"
    )
    required = [
        "paper-only",
        "local-only",
        "read-only",
        "governance-only",
        "operator-review-only",
        "sidecar-only",
        "mutate frozen core P1-P47",
        "create P48",
        "deploy anything",
        "create a release",
        "create a tag",
    ]
    for item in required:
        assert item in text