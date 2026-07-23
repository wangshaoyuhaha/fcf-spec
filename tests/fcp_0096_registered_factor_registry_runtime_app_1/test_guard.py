from scripts.control_center_fcp_0096_registered_factor_registry_runtime_guard import (
    build_fcp_0096_guard_report,
    main,
)


def test_guard_report_passes() -> None:
    report = build_fcp_0096_guard_report()
    assert report["ok"], report


def test_guard_main_passes() -> None:
    assert main() == 0
