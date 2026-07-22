from scripts.control_center_fcp_0055_btc_perpetual_complete_rule_bundle_coherence_hardening_guard import (
    build_fcp_0055_guard_report,
    main,
)


def test_fcp_0055_guard_passes_repository() -> None:
    report = build_fcp_0055_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0055_guard_main_passes() -> None:
    assert main() == 0
