from scripts.control_center_fcp_0070_btc_perpetual_paper_stress_deterministic_trigger_evaluation_guard import (
    build_fcp_0070_guard_report,
    main,
)


def test_fcp_0070_governance_guard_passes():
    report = build_fcp_0070_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0070_governance_guard_main_passes():
    assert main() == 0
