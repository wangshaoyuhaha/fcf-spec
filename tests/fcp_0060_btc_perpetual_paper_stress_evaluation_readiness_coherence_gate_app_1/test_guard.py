from scripts.control_center_fcp_0060_btc_perpetual_paper_stress_evaluation_readiness_coherence_gate_guard import (
    build_fcp_0060_guard_report,
    main,
)


def test_fcp_0060_guard_passes_repository() -> None:
    report = build_fcp_0060_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0060_guard_main_passes() -> None:
    assert main() == 0
