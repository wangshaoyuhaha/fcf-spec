from scripts.control_center_fcp_0033_cross_market_readiness_dataset_lineage_visibility_hardening_guard import (
    build_fcp_0033_guard_report,
    main,
)


def test_fcp_0033_guard_passes():
    report = build_fcp_0033_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0033_guard_main_passes():
    assert main() == 0
