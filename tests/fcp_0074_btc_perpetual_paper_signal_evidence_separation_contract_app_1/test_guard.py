from scripts.control_center_fcp_0074_btc_perpetual_paper_signal_evidence_separation_contract_guard import (
    build_fcp_0074_guard_report,
    main,
)


def test_fcp_0074_guard_passes_repository():
    report = build_fcp_0074_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0074_guard_main_passes():
    assert main() == 0
