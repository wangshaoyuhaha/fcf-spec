from scripts.control_center_fcp_0045_btc_cross_source_exact_observation_delta_evidence_ledger_guard import (
    build_fcp_0045_guard_report,
    main,
)


def test_fcp_0045_guard_passes_repository() -> None:
    report = build_fcp_0045_guard_report()

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0045_guard_main_passes() -> None:
    assert main() == 0
