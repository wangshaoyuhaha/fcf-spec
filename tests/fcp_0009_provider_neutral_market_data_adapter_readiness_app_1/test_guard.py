from scripts.control_center_fcp_0009_provider_neutral_market_data_adapter_readiness_guard import (
    build_fcp_0009_guard_report,
)


def test_fcp_0009_control_guard_passes() -> None:
    report = build_fcp_0009_guard_report()
    assert report["ok"] is True, report
