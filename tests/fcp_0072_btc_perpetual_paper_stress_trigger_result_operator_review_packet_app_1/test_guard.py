from scripts.control_center_fcp_0072_btc_perpetual_paper_stress_trigger_result_operator_review_packet_guard import (
    build_fcp_0072_guard_report,
    main,
)


def test_fcp_0072_guard_passes_repository():
    report = build_fcp_0072_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0072_guard_main_passes():
    assert main() == 0
