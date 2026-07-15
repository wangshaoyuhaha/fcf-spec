from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "docs" / "FCF_EXECUTION_SAFETY_PROTOCOL.md"
RUNNER = ROOT / "scripts" / "fcf_safe_runner.ps1"


def test_d3_protocol_requires_native_exit_guard_and_checkpoint_resume():
    text = PROTOCOL.read_text(encoding="utf-8")

    required = (
        "Native command sequence guard",
        "$LASTEXITCODE",
        "stat-only",
        "content hash",
        "last verified checkpoint",
        "tool-access failure",
        "active authority files",
    )
    for marker in required:
        assert marker in text


def test_d3_safe_runner_exposes_required_process_guard():
    text = RUNNER.read_text(encoding="utf-8")

    assert "function Assert-FcfProcessSucceeded" in text
    assert "function Invoke-FcfRequiredProcess" in text
    assert "REQUIRED_PROCESS_GUARD=PASSED" in text
