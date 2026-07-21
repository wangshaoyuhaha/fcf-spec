from scripts.control_center_fcp_0034_btc_perpetual_leverage_paper_research_architecture_guard import (
    build_fcp_0034_guard_report,
    main,
)


def test_fcp_0034_guard_passes():
    report = build_fcp_0034_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0034_guard_main_passes():
    assert main() == 0
