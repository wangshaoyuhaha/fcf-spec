from scripts.control_center_fcp_0047_btc_perpetual_margin_risk_tier_evidence_registry_guard import (
    build_fcp_0047_guard_report,
    main,
)


def test_fcp_0047_guard_passes_repository() -> None:
    report = build_fcp_0047_guard_report()

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0047_guard_main_passes() -> None:
    assert main() == 0
