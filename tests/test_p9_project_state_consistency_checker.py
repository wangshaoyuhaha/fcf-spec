from pathlib import Path

from fcf.regression.project_state_consistency_checker import (
    REQUIRED_NEXT_MARKERS,
    REQUIRED_PHASE_MARKERS,
    REQUIRED_SAFETY_MARKERS,
    check_project_state_consistency,
)


DOC = Path("docs/84_p9_project_state_consistency_checker.md")


def test_p9_project_state_consistency_doc_exists():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P9-D5" in text
    assert "PROJECT_STATE / README consistency checker" in text
    assert "check_project_state_consistency" in text


def test_p9_project_state_consistency_valid_repo_passes():
    result = check_project_state_consistency()

    assert result["status"] == "completed"
    assert result["checker"] == "project_state_consistency_checker"
    assert result["checker_version"] == "0.1.0"
    assert result["ok"] is True
    assert result["violations"] == []
    assert result["ready_for_p9_d6_ci_safe_command_doc"] is True


def test_p9_project_state_consistency_checks_required_markers():
    result = check_project_state_consistency()
    check_names = {check["name"] for check in result["checks"]}

    assert "README.md:exists" in check_names
    assert "PROJECT_STATE.md:exists" in check_names

    for marker in REQUIRED_PHASE_MARKERS:
        assert f"README.md:phase_markers:{marker}" in check_names
        assert f"PROJECT_STATE.md:phase_markers:{marker}" in check_names

    for marker in REQUIRED_SAFETY_MARKERS:
        assert f"README.md:safety_markers:{marker}" in check_names
        assert f"PROJECT_STATE.md:safety_markers:{marker}" in check_names

    for marker in REQUIRED_NEXT_MARKERS:
        assert f"README.md:next_markers:{marker}" in check_names
        assert f"PROJECT_STATE.md:next_markers:{marker}" in check_names


def test_p9_project_state_consistency_all_checks_pass_for_repo():
    result = check_project_state_consistency()

    assert len(result["checks"]) > 0
    for check in result["checks"]:
        assert check["passed"] is True


def test_p9_project_state_consistency_fails_missing_files(tmp_path):
    result = check_project_state_consistency(
        readme_path=str(tmp_path / "README.md"),
        project_state_path=str(tmp_path / "PROJECT_STATE.md"),
    )

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert result["ready_for_p9_d6_ci_safe_command_doc"] is False
    assert len(result["violations"]) > 0


def test_p9_project_state_consistency_fails_stale_project_state(tmp_path):
    readme = tmp_path / "README.md"
    project_state = tmp_path / "PROJECT_STATE.md"

    complete_text = "\n".join(
        REQUIRED_PHASE_MARKERS
        + REQUIRED_SAFETY_MARKERS
        + REQUIRED_NEXT_MARKERS
    )

    readme.write_text(complete_text, encoding="utf-8")
    project_state.write_text("P9-D1\n不接真实交易所 API\n", encoding="utf-8")

    result = check_project_state_consistency(
        readme_path=str(readme),
        project_state_path=str(project_state),
    )

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert any(
        violation["file"] == "PROJECT_STATE.md"
        and violation["marker"] == "P9-D5"
        for violation in result["violations"]
    )


def test_p9_project_state_consistency_fails_stale_readme(tmp_path):
    readme = tmp_path / "README.md"
    project_state = tmp_path / "PROJECT_STATE.md"

    complete_text = "\n".join(
        REQUIRED_PHASE_MARKERS
        + REQUIRED_SAFETY_MARKERS
        + REQUIRED_NEXT_MARKERS
    )

    readme.write_text("P9-D1\n不真实下单\n", encoding="utf-8")
    project_state.write_text(complete_text, encoding="utf-8")

    result = check_project_state_consistency(
        readme_path=str(readme),
        project_state_path=str(project_state),
    )

    assert result["status"] == "failed"
    assert result["ok"] is False
    assert any(
        violation["file"] == "README.md"
        and violation["marker"] == "P9-D5"
        for violation in result["violations"]
    )


def test_p9_project_state_consistency_doc_mentions_safety_and_next_step():
    text = DOC.read_text(encoding="utf-8")

    for marker in REQUIRED_SAFETY_MARKERS:
        assert marker in text

    assert "P9-D6" in text
    assert "CI-safe regression command document" in text
