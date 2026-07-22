from scripts.control_center_fcp_0058_btc_perpetual_paper_stress_evaluation_input_evidence_registry_guard import (
    build_fcp_0058_guard_report,
    main,
)


def test_fcp_0058_guard_passes_repository() -> None:
    report = build_fcp_0058_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0058_guard_main_passes() -> None:
    assert main() == 0
