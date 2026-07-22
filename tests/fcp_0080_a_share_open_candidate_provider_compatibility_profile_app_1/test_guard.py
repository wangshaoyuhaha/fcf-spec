from scripts.control_center_fcp_0080_a_share_open_candidate_provider_compatibility_profile_guard import (
    build_fcp_0080_guard_report,
    main,
)


def test_fcp_0080_guard_passes_repository():
    report = build_fcp_0080_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0080_guard_main_passes():
    assert main() == 0
