from scripts.control_center_fcp_0087_btc_registered_local_export_operator_review_receipt_guard import (
    build_fcp_0087_guard_report,
    main,
)


def test_fcp_0087_guard_passes_repository():
    report = build_fcp_0087_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0087_guard_main_passes():
    assert main() == 0
