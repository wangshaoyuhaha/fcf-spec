from pathlib import Path

from scripts.control_center_fcp_0093_btc_coin_metrics_reference_rate_local_csv_validation_guard import (
    build_fcp_0093_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[2]


def test_fcp_0093_guard_passes_repository() -> None:
    report = build_fcp_0093_guard_report(ROOT)

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0093_guard_main_passes() -> None:
    assert main() == 0
