from scripts.control_center_fcp_0038_a_share_registered_same_calendar_cross_source_coverage_reconciliation_guard import (
    build_fcp_0038_guard_report,
    main,
)


def test_fcp_0038_guard_passes_repository() -> None:
    report = build_fcp_0038_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0038_guard_main_passes() -> None:
    assert main() == 0
