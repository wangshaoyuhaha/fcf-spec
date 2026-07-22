from scripts.control_center_fcp_0067_btc_perpetual_paper_stress_evaluation_measure_formula_semantics_registry_guard import (
    build_fcp_0067_guard_report,
    main,
)


def test_fcp_0067_governance_guard_passes():
    report = build_fcp_0067_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0067_governance_guard_main_passes():
    assert main() == 0
