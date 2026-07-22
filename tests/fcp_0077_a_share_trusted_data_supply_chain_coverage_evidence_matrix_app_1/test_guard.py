from scripts.control_center_fcp_0077_a_share_trusted_data_supply_chain_coverage_evidence_matrix_guard import (
    build_fcp_0077_guard_report,
    main,
)


def test_fcp_0077_guard_passes_repository():
    report = build_fcp_0077_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0077_guard_main_passes():
    assert main() == 0
