from scripts.control_center_fcp_0088_a_share_guojin_qmt_registered_local_dual_export_offline_sdk_compatibility_evidence_guard import (
    build_fcp_0088_guard_report,
    main,
)


def test_fcp_0088_guard_passes_repository():
    report = build_fcp_0088_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0088_guard_main_passes():
    assert main() == 0
