from scripts.control_center_fcp_0062_btc_perpetual_paper_stress_evaluation_readiness_parameter_domain_coherence_hardening_guard import build_fcp_0062_guard_report, main


def test_fcp_0062_guard_passes_repository():
    report = build_fcp_0062_guard_report(); assert report["ok"] is True; assert all(report["checks"].values())


def test_fcp_0062_guard_main_passes():
    assert main() == 0
