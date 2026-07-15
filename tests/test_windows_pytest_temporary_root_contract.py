from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_execution_protocol_requires_safe_windows_pytest_scratch() -> None:
    protocol = (
        PROJECT_ROOT / "docs" / "FCF_EXECUTION_SAFETY_PROTOCOL.md"
    ).read_text(encoding="utf-8")

    assert "## Windows pytest temporary roots" in protocol
    assert "outside the repository" in protocol
    assert "direct process argument" in protocol
    assert "never pass an absolute Windows `--basetemp` value" in protocol
    assert "request an explicit UAC confirmation" in protocol
    assert "never hide the target" in protocol


def test_control_center_allows_recoverable_environment_repairs() -> None:
    control = (
        PROJECT_ROOT / "docs" / "FCF_PROJECT_CONTROL_CENTER.md"
    ).read_text(encoding="utf-8")

    assert "### 13. Windows pytest and recoverable environment operations" in control
    assert "must not be passed through" in control
    assert "resume from the last verified checkpoint" in control
    assert "Do not roll back verified project changes" in control
    assert "Commit and push remain blocked" in control
