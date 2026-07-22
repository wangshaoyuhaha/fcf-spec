from scripts.control_center_fcp_0069_btc_perpetual_paper_stress_evaluation_input_binding_registry_guard import (
    build_fcp_0069_guard_report,
    main,
)


def test_fcp_0069_governance_guard_passes():
    report = build_fcp_0069_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0069_governance_guard_main_passes():
    assert main() == 0
