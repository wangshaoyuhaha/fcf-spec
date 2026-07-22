from scripts.control_center_fcp_0073_btc_perpetual_paper_stress_trigger_result_operator_review_receipt_guard import (
    build_fcp_0073_guard_report,
    main,
)


def test_fcp_0073_guard_passes_repository():
    report = build_fcp_0073_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0073_guard_main_passes():
    assert main() == 0
