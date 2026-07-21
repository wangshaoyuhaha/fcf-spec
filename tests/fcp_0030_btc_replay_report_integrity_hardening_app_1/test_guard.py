from scripts.control_center_fcp_0030_btc_replay_report_integrity_hardening_guard import (
    build_fcp_0030_guard_report,
    main,
)


def test_fcp_0030_guard_passes_repository():
    assert build_fcp_0030_guard_report()["ok"] is True


def test_fcp_0030_guard_main_passes():
    assert main() == 0
