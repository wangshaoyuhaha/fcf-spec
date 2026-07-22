from scripts.control_center_fcp_0076_a_share_candidate_daily_promotion_readiness_gate_guard import (
    build_fcp_0076_guard_report,
    main,
)


def test_fcp_0076_guard_passes_repository():
    report = build_fcp_0076_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0076_guard_main_passes():
    assert main() == 0
