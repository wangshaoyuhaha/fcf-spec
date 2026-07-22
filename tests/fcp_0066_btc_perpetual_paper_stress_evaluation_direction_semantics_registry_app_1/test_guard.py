from scripts.control_center_fcp_0066_btc_perpetual_paper_stress_evaluation_direction_semantics_registry_guard import (
    build_fcp_0066_guard_report,
)


def test_fcp_0066_governance_guard_passes():
    report = build_fcp_0066_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0066_preserves_permanent_boundary():
    report = build_fcp_0066_guard_report()
    assert report["checks"]["gaps_preserved"] is True
    assert report["checks"]["no_product_phase"] is True
