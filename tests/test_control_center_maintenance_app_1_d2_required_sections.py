from pathlib import Path


def test_control_center_maintenance_d2_required_section_model_exists():
    path = Path("docs/control_center_maintenance_app_1/D2_REQUIRED_SECTION_MODEL.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "D2 Required Section Model" in text
    assert "Project identity" in text
    assert "Current mainline state" in text
    assert "Completed sidecar registry" in text
    assert "Mainline sync records" in text


def test_control_center_maintenance_d2_required_sections():
    text = Path("docs/control_center_maintenance_app_1/D2_REQUIRED_SECTION_MODEL.md").read_text(
        encoding="utf-8"
    )
    required = [
        "Validation baseline",
        "Safety boundary",
        "Deferred backlog",
        "Candidate sidecar queue",
        "Architecture governance notes",
        "Final clean status records",
    ]
    for item in required:
        assert item in text


def test_control_center_maintenance_d2_safety_boundary():
    text = Path("docs/control_center_maintenance_app_1/D2_REQUIRED_SECTION_MODEL.md").read_text(
        encoding="utf-8"
    )
    required = [
        "paper-only",
        "local-only",
        "read-only",
        "sidecar-only",
        "operator-review-only",
        "no P48",
        "no core mutation",
        "no real trading",
        "no real execution",
        "no deploy",
        "no release",
        "no tag",
    ]
    for item in required:
        assert item in text


def test_control_center_maintenance_d2_backlog_and_queue_rules():
    text = Path("docs/control_center_maintenance_app_1/D2_REQUIRED_SECTION_MODEL.md").read_text(
        encoding="utf-8"
    )
    required = [
        "deferred reason",
        "start condition",
        "explicit operator approval requirement",
        "candidate name",
        "priority",
        "dependency",
        "safety gate",
    ]
    for item in required:
        assert item in text