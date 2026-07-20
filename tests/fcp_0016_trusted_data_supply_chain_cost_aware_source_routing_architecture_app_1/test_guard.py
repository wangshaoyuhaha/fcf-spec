from scripts.control_center_fcp_0016_trusted_data_supply_chain_cost_aware_source_routing_architecture_guard import (
    build_fcp_0016_guard_report,
    main,
)


def test_fcp_0016_guard_passes_repository() -> None:
    report = build_fcp_0016_guard_report()
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0016_guard_main_passes() -> None:
    assert main() == 0
