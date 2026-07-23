from scripts.control_center_fcp_0102_registered_factor_normalization_missing_state_runtime_guard import (
    build_fcp_0102_guard_report,
    main,
)


def test_fcp_0102_guard_passes_repository():
    report = build_fcp_0102_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0102_guard_main_passes():
    assert main() == 0
