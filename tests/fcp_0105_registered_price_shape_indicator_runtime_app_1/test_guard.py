from scripts.control_center_fcp_0105_registered_price_shape_indicator_runtime_guard import (
    build_fcp_0105_guard_report,
    main,
)


def test_fcp_0105_guard_passes_repository():
    report = build_fcp_0105_guard_report()
    assert report["ok"] is True, report


def test_fcp_0105_guard_main_passes():
    assert main() == 0
