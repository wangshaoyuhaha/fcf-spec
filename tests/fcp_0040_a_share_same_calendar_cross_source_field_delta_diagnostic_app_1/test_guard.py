from scripts.control_center_fcp_0040_a_share_same_calendar_cross_source_field_delta_diagnostic_guard import (
    build_fcp_0040_guard_report,
    main,
)


def test_fcp_0040_guard_passes_repository() -> None:
    report = build_fcp_0040_guard_report()

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0040_guard_main_passes() -> None:
    assert main() == 0
