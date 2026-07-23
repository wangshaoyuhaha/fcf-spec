from scripts.control_center_fcp_0097_registered_target_label_registry_runtime_guard import (
    build_fcp_0097_guard_report,
    main,
)


def test_guard_report_passes() -> None:
    report = build_fcp_0097_guard_report()
    assert report["ok"], report


def test_guard_main_passes() -> None:
    assert main() == 0
