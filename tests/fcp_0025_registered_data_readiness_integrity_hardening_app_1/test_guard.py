from scripts.control_center_fcp_0025_registered_data_readiness_integrity_hardening_guard import build_fcp_0025_guard_report, main


def test_fcp_0025_guard_passes_repository():
    report = build_fcp_0025_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0025_guard_main_passes():
    assert main() == 0
