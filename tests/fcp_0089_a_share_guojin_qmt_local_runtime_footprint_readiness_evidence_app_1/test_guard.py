from scripts.control_center_fcp_0089_a_share_guojin_qmt_local_runtime_footprint_readiness_evidence_guard import (
    build_fcp_0089_guard_report,
    main,
)


def test_fcp_0089_guard_passes_repository():
    report = build_fcp_0089_guard_report()
    assert report["ok"] is True


def test_fcp_0089_guard_main_passes():
    assert main() == 0
