from scripts.control_center_fcp_0032_a_share_cross_source_reconciliation_dataset_lineage_authority_integrity_hardening_guard import (
    build_fcp_0032_guard_report,
    main,
)


def test_fcp_0032_guard_passes_repository():
    assert build_fcp_0032_guard_report()["ok"] is True


def test_fcp_0032_guard_main_passes():
    assert main() == 0
