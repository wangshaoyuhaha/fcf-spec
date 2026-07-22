from scripts.control_center_fcp_0053_btc_perpetual_rule_bundle_point_in_time_coherence_gate_guard import (
    build_fcp_0053_guard_report,
    main,
)


def test_fcp_0053_guard_passes_repository() -> None:
    report = build_fcp_0053_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0053_guard_main_passes() -> None:
    assert main() == 0
