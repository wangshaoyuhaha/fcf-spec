from scripts.control_center_fcp_0037_a_share_registered_expected_trading_date_artifact_profile_guard import (
    build_fcp_0037_guard_report,
    main,
)


def test_fcp_0037_guard_passes_repository() -> None:
    report = build_fcp_0037_guard_report()

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0037_guard_main_passes() -> None:
    assert main() == 0
