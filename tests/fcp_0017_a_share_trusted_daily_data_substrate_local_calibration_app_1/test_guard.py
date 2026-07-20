from scripts.control_center_fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_guard import (
    build_fcp_0017_guard_report,
    main,
)


def test_fcp_0017_guard_passes_repository() -> None:
    report = build_fcp_0017_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0017_guard_main_passes() -> None:
    assert main() == 0
