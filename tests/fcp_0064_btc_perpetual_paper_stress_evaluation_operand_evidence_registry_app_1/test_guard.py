from scripts.control_center_fcp_0064_btc_perpetual_paper_stress_evaluation_operand_evidence_registry_guard import (
    build_fcp_0064_guard_report,
    main,
)


def test_fcp_0064_guard_passes_repository():
    report = build_fcp_0064_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0064_guard_main_passes():
    assert main() == 0
