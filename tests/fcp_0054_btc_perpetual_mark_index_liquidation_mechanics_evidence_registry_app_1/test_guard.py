from scripts.control_center_fcp_0054_btc_perpetual_mark_index_liquidation_mechanics_evidence_registry_guard import (
    build_fcp_0054_guard_report,
    main,
)


def test_fcp_0054_guard_passes_repository() -> None:
    report = build_fcp_0054_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0054_guard_main_passes() -> None:
    assert main() == 0
