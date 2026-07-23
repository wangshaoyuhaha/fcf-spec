from scripts.control_center_fcp_0091_a_share_guojin_qmt_registered_local_cache_loopback_read_only_probe_guard import (
    build_fcp_0091_guard_report,
    main,
)


def test_fcp_0091_guard_passes_repository():
    report = build_fcp_0091_guard_report()
    assert report["ok"] is True, report


def test_fcp_0091_guard_main_passes():
    assert main() == 0
