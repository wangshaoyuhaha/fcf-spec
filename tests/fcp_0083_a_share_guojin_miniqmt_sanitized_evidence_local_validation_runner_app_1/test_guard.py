from scripts.control_center_fcp_0083_a_share_guojin_miniqmt_sanitized_evidence_local_validation_runner_guard import (
    build_fcp_0083_guard_report,
    main,
)


def test_fcp_0083_guard_passes_repository():
    report = build_fcp_0083_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0083_guard_main_passes():
    assert main() == 0
