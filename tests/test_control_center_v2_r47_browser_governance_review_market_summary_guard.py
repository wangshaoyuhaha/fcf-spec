from scripts.control_center_v2_r47_browser_governance_review_market_summary_guard import ROOT, build_v2_r47_guard_report, main


def test_v2_r47_guard_passes_repository():
    report = build_v2_r47_guard_report(ROOT)
    assert report["ok"] is True and all(report["checks"].values())


def test_v2_r47_guard_main_returns_zero():
    assert main() == 0


def test_v2_r47_guard_surface_is_closed():
    checks = build_v2_r47_guard_report(ROOT)["checks"]
    assert checks["surface_exact"] is True and checks["boundary_closed"] is True
