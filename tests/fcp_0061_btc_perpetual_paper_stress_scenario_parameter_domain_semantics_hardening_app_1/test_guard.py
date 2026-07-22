from scripts.control_center_fcp_0061_btc_perpetual_paper_stress_scenario_parameter_domain_semantics_hardening_guard import (
    build_fcp_0061_guard_report,
    main,
)


def test_fcp_0061_guard_passes_repository() -> None:
    report = build_fcp_0061_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0061_guard_main_passes() -> None:
    assert main() == 0
