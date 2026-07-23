from pathlib import Path

from scripts.control_center_fcp_0100_registered_multi_horizon_conflict_resolver_runtime_guard import (
    build_fcp_0100_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[2]


def test_fcp_0100_guard_passes_repository() -> None:
    report = build_fcp_0100_guard_report(ROOT)

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0100_guard_main_passes() -> None:
    assert main() == 0
