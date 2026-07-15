import shutil
import socket
from pathlib import Path

from apps.browser_product_console_runtime_app_1 import (
    DIAGNOSTIC_STAGE_ID,
    OperatorLaunchDiagnosticCode,
    OperatorLaunchProfile,
    build_default_operator_launch_profile,
    build_operator_launch_preflight,
)
from scripts.run_browser_product_console_runtime import main


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_d4_default_preflight_is_ready() -> None:
    profile = build_default_operator_launch_profile(project_root=PROJECT_ROOT)
    result = build_operator_launch_preflight(profile)

    assert DIAGNOSTIC_STAGE_ID == "D4"
    assert result.status == "READY"
    assert result.code is OperatorLaunchDiagnosticCode.READY
    assert result.session is not None
    assert result.session.artifact_count == 14


def test_d4_missing_package_has_deterministic_guidance(tmp_path: Path) -> None:
    profile = OperatorLaunchProfile(
        allowed_root=tmp_path / "missing",
        index_path=tmp_path / "missing" / "index.json",
    )
    result = build_operator_launch_preflight(profile)

    assert result.status == "BLOCKED"
    assert result.code is OperatorLaunchDiagnosticCode.ARTIFACT_MISSING
    assert "missing" in result.message.lower()
    assert "registered package" in result.remediation.lower()


def test_d4_tampered_package_has_integrity_code(tmp_path: Path) -> None:
    source = build_default_operator_launch_profile(
        project_root=PROJECT_ROOT
    ).allowed_root
    copied = tmp_path / "starter"
    shutil.copytree(source, copied)
    (copied / "registered" / "data-quality.json").write_text(
        "{}",
        encoding="utf-8",
    )
    profile = OperatorLaunchProfile(
        allowed_root=copied,
        index_path=copied / "index.json",
    )
    result = build_operator_launch_preflight(profile)

    assert result.status == "BLOCKED"
    assert result.code is (
        OperatorLaunchDiagnosticCode.ARTIFACT_INTEGRITY_FAILURE
    )
    assert "bypass" in result.remediation


def test_d4_busy_port_has_deterministic_guidance() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as occupied:
        occupied.bind(("127.0.0.1", 0))
        occupied.listen(1)
        port = int(occupied.getsockname()[1])
        profile = build_default_operator_launch_profile(
            project_root=PROJECT_ROOT,
            port=port,
        )
        result = build_operator_launch_preflight(profile)

    assert result.status == "BLOCKED"
    assert result.code is OperatorLaunchDiagnosticCode.PORT_UNAVAILABLE
    assert "--port" in result.remediation


def test_d4_cli_reports_missing_custom_package_without_traceback(
    tmp_path: Path,
    capsys,
) -> None:
    missing = tmp_path / "missing"

    exit_code = main(
        [
            "--allowed-root",
            str(missing),
            "--index",
            "index.json",
            "--check",
        ]
    )
    output = capsys.readouterr()

    assert exit_code == 2
    assert "FCF-LAUNCH-ARTIFACT-MISSING" in output.err
    assert "Guidance:" in output.err
    assert "Traceback" not in output.err
