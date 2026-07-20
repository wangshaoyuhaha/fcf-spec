from pathlib import Path

from scripts.control_center_fcp_0005_mvp_product_readiness_decision_gate_guard import (
    build_fcp_0005_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[2]


def test_fcp_0005_guard_passes_repository() -> None:
    report = build_fcp_0005_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_fcp_0005_guard_main_passes() -> None:
    assert main() == 0
