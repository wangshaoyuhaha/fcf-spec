from scripts.control_center_fcp_0086_btc_registered_local_export_operator_review_packet_guard import (
    build_fcp_0086_guard_report,
    main,
)


def test_fcp_0086_guard_passes_repository() -> None:
    report = build_fcp_0086_guard_report()

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0086_guard_main_passes() -> None:
    assert main() == 0
