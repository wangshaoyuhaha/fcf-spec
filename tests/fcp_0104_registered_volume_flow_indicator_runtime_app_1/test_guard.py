from scripts.control_center_fcp_0104_registered_volume_flow_indicator_runtime_guard import (
    build_fcp_0104_guard_report,
    main,
)


def test_fcp_0104_guard_passes_repository():
    report = build_fcp_0104_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0104_guard_main_passes():
    assert main() == 0
