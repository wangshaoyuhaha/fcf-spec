from scripts.control_center_fcp_0079_a_share_corporate_action_query_policy_lineage_contract_guard import (
    build_fcp_0079_guard_report,
    main,
)


def test_fcp_0079_guard_passes_repository():
    report = build_fcp_0079_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0079_guard_main_passes():
    assert main() == 0
