from scripts.control_center_fcp_0052_guojin_qmt_coverage_supplement_lineage_integrity_hardening_guard import (
    ROOT,
    build_fcp_0052_guard_report,
    main,
)


def test_fcp_0052_guard_passes_repository() -> None:
    report = build_fcp_0052_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0052_guard_main_passes() -> None:
    assert main() == 0
