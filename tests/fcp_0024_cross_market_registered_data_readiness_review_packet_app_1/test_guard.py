from scripts.control_center_fcp_0024_cross_market_registered_data_readiness_review_packet_guard import build_fcp_0024_guard_report, main


def test_fcp_0024_guard_passes_repository():
    report = build_fcp_0024_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0024_guard_main_passes():
    assert main() == 0
