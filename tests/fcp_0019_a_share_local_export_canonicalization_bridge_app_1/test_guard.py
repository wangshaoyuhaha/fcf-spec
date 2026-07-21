from scripts.control_center_fcp_0019_a_share_local_export_canonicalization_bridge_guard import (
    build_fcp_0019_guard_report,
    main,
)


def test_fcp_0019_guard_passes_repository() -> None:
    report = build_fcp_0019_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0019_guard_main_passes() -> None:
    assert main() == 0
