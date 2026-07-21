from scripts.control_center_fcp_0035_guojin_qmt_registered_local_daily_export_profile_guard import (
    build_fcp_0035_guard_report,
    main,
)


def test_fcp_0035_guard_passes() -> None:
    report = build_fcp_0035_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0035_guard_main_passes() -> None:
    assert main() == 0
