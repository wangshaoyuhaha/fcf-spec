from scripts.control_center_fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_guard import (
    build_fcp_0084_guard_report,
    main,
)


def test_fcp_0084_guard_passes_repository():
    report = build_fcp_0084_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0084_guard_main_passes():
    assert main() == 0
