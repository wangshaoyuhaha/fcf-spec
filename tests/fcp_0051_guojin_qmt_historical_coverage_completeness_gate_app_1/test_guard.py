from scripts.control_center_fcp_0051_guojin_qmt_historical_coverage_completeness_gate_guard import (
    build_fcp_0051_guard_report,
    main,
)


def test_fcp_0051_guard_passes_repository() -> None:
    report = build_fcp_0051_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0051_guard_main_passes() -> None:
    assert main() == 0
