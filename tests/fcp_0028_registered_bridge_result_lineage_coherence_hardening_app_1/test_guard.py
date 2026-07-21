from scripts.control_center_fcp_0028_registered_bridge_result_lineage_coherence_hardening_guard import (
    build_fcp_0028_guard_report,
    main,
)


def test_fcp_0028_guard_passes_repository():
    assert build_fcp_0028_guard_report()["ok"] is True


def test_fcp_0028_guard_main_passes():
    assert main() == 0
