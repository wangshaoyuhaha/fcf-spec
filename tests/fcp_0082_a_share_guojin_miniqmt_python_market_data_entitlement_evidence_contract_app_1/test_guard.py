from scripts.control_center_fcp_0082_a_share_guojin_miniqmt_python_market_data_entitlement_evidence_contract_guard import (
    build_fcp_0082_guard_report,
    main,
)


def test_fcp_0082_guard_passes_repository():
    report = build_fcp_0082_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0082_guard_main_passes():
    assert main() == 0
