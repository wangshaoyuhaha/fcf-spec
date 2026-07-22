from scripts.control_center_fcp_0078_a_share_publication_availability_clock_contract_guard import (
    build_fcp_0078_guard_report,
    main,
)


def test_fcp_0078_guard_passes_repository():
    report = build_fcp_0078_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0078_guard_main_passes():
    assert main() == 0
