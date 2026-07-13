"""Contract tests for the FCF safe PowerShell process runner."""

from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "fcf_safe_runner.ps1"


def test_required_safe_runner_functions_exist() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    required = (
        "function Invoke-FcfProcess",
        "function Invoke-FcfProcessWithRetry",
        "function Get-FcfRepositoryState",
        "function Assert-FcfRepositoryState",
        "function Assert-FcfChangedPaths",
        "function Write-FcfTextFile",
        "function Write-FcfCheckpoint",
        "function Read-FcfCheckpoint",
        "RedirectStandardOutput = $true",
        "RedirectStandardError = $true",
        "AllowedExitCodes",
        "AttemptCount",
        "[AllowEmptyString()]",
        '"<EMPTY>"',
    )

    for marker in required:
        assert marker in text


def test_forbidden_destructive_patterns_are_absent() -> None:
    text = RUNNER.read_text(encoding="utf-8").lower()

    forbidden = (
        "git clean -fd",
        "git clean -xdf",
        "git restore --worktree --staged -- .",
        "git reset --hard",
        "core.autocrlf",
        "git ls-remote",
        "remove-item $repositorypath -recurse",
    )

    for pattern in forbidden:
        assert pattern not in text


def test_safe_runner_self_test_passes() -> None:
    executable = (
        shutil.which("powershell.exe")
        or shutil.which("powershell")
        or shutil.which("pwsh")
    )

    if executable is None:
        pytest.skip("PowerShell is not installed.")

    command = [
        executable,
        "-NoProfile",
    ]

    if Path(executable).name.lower().startswith("powershell"):
        command.extend(
            [
                "-ExecutionPolicy",
                "Bypass",
            ]
        )

    command.extend(
        [
            "-File",
            str(RUNNER),
            "-SelfTest",
        ]
    )

    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, (
        completed.stdout + "\n" + completed.stderr
    )
    assert "SELF_TEST_RESULT=PASSED" in completed.stdout
    assert "STDERR_WARNING_EXIT_ZERO=PASSED" in completed.stdout
    assert "NONZERO_EXIT_FAILURE=PASSED" in completed.stdout
    assert "RETRY_RECOVERY=PASSED" in completed.stdout
    assert "LINE_ENDING_NORMALIZATION=PASSED" in completed.stdout
    assert "IDEMPOTENT_WRITE=PASSED" in completed.stdout
    assert "CHECKPOINT_RESUME=PASSED" in completed.stdout

def test_self_test_switch_uses_non_conflicting_variable() -> None:
    text = RUNNER.read_text(encoding="utf-8")

    assert '[Alias("SelfTest")]' in text
    assert "[switch]$RunSelfTest" in text
    assert "if ($RunSelfTest)" in text
    assert "[switch]$SelfTest" not in text
