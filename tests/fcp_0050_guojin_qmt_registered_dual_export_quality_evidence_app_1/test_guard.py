from scripts.control_center_fcp_0050_guojin_qmt_registered_dual_export_quality_evidence_guard import (
    build_fcp_0050_guard_report,
    main,
)


def test_fcp_0050_guard_passes_repository() -> None:
    report = build_fcp_0050_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0050_guard_main_passes() -> None:
    assert main() == 0
