from scripts.control_center_fcp_0092_a_share_guojin_qmt_local_cache_probe_operator_review_packet_guard import (
    build_fcp_0092_guard_report,
    main,
)


def test_fcp_0092_guard_passes_repository():
    report = build_fcp_0092_guard_report()
    assert report["ok"] is True, report


def test_fcp_0092_guard_main_passes():
    assert main() == 0
