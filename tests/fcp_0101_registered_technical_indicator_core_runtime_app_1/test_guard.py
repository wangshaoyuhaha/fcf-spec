from pathlib import Path

from scripts.control_center_fcp_0101_registered_technical_indicator_core_runtime_guard import (
    build_fcp_0101_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[2]


def test_fcp_0101_guard_passes_repository() -> None:
    report = build_fcp_0101_guard_report(ROOT)

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0101_guard_main_passes() -> None:
    assert main() == 0
