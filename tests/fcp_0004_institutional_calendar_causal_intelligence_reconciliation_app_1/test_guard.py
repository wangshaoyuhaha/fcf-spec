from pathlib import Path

from scripts.control_center_fcp_0004_institutional_calendar_causal_intelligence_reconciliation_guard import (
    APPROVAL_END,
    APPROVAL_START,
    AUTHORITIES,
    FINAL_END,
    FINAL_START,
    LOCK_END,
    LOCK_START,
    build_fcp_0004_guard_report,
)
from scripts.run_all_checks import COMMANDS


ROOT = Path(__file__).resolve().parents[2]


def _blocks(start: str, end: str) -> list[str]:
    blocks = []
    for path in AUTHORITIES:
        text = (ROOT / path).read_text(encoding="ascii")
        blocks.append(text[text.index(start) : text.index(end) + len(end)])
    return blocks


def test_guard_passes() -> None:
    report = build_fcp_0004_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_approval_is_exact_across_authorities() -> None:
    blocks = _blocks(APPROVAL_START, APPROVAL_END)
    assert len(set(blocks)) == 1


def test_lock_is_exact_across_authorities() -> None:
    blocks = _blocks(LOCK_START, LOCK_END)
    assert len(set(blocks)) == 1
    assert "DELIVERY_IMPLEMENTED_VALIDATION_PENDING" in blocks[0]


def test_guard_is_in_all_checks() -> None:
    assert [
        "python",
        "scripts/control_center_fcp_0004_institutional_calendar_causal_intelligence_reconciliation_guard.py",
    ] in COMMANDS


def test_guard_proves_historical_delivery_evidence() -> None:
    checks = build_fcp_0004_guard_report(ROOT)["checks"]
    assert checks["historical_delivery_evidence_exists"] is True
    assert checks["historical_stage_surfaces_unique"] is True


def test_final_is_exact_across_authorities() -> None:
    blocks = _blocks(FINAL_START, FINAL_END)
    assert len(set(blocks)) == 1
    assert "GOVERNANCE_RECONCILIATION_COMPLETED_MERGED_VALIDATED" in blocks[0]
