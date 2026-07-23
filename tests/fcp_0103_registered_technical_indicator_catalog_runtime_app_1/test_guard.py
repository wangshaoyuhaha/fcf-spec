from scripts.control_center_fcp_0103_registered_technical_indicator_catalog_runtime_guard import (
    build_fcp_0103_guard_report,
    main,
)


def test_fcp_0103_guard_passes_repository():
    report = build_fcp_0103_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0103_guard_main_passes():
    assert main() == 0
