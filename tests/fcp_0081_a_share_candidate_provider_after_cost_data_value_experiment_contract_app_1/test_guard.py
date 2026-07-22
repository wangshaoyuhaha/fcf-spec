from scripts.control_center_fcp_0081_a_share_candidate_provider_after_cost_data_value_experiment_contract_guard import (
    build_fcp_0081_guard_report,
    main,
)


def test_fcp_0081_guard_passes_repository():
    report = build_fcp_0081_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0081_guard_main_passes():
    assert main() == 0
