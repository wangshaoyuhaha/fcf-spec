from scripts.control_center_fcp_0106_a_share_qmt_internal_read_only_market_bridge_guard import (
    build_fcp_0106_guard_report,
    main,
)


def test_fcp_0106_guard_passes_repository():
    report = build_fcp_0106_guard_report()
    assert report["ok"] is True, report


def test_fcp_0106_guard_main_passes():
    assert main() == 0
