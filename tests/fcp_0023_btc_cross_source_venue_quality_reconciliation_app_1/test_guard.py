from scripts.control_center_fcp_0023_btc_cross_source_venue_quality_reconciliation_guard import (
    build_fcp_0023_guard_report,
    main,
)


def test_fcp_0023_guard_passes_repository() -> None:
    report = build_fcp_0023_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0023_guard_main_passes() -> None:
    assert main() == 0
