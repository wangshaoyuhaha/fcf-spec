from pathlib import Path

from scripts.control_center_fcp_0003_correlated_evidence_confidence_budget_guard import (
    AUTHORITIES,
    FINAL_END,
    FINAL_START,
    LOCK_END,
    LOCK_START,
    build_fcp_0003_guard_report,
)
from scripts.run_all_checks import COMMANDS


ROOT = Path(__file__).resolve().parents[2]


def test_fcp_0003_guard_passes_repository() -> None:
    report = build_fcp_0003_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_lock_is_exact_across_authorities() -> None:
    blocks = []
    for path in AUTHORITIES:
        text = (ROOT / path).read_text(encoding="ascii")
        blocks.append(text[text.index(LOCK_START) : text.index(LOCK_END) + len(LOCK_END)])
    assert len(set(blocks)) == 1
    assert "FCF-FCP-0003 remains NEEDS_RESEARCH" in " ".join(blocks[0].split())


def test_guard_is_in_all_checks() -> None:
    assert ["python", "scripts/control_center_fcp_0003_correlated_evidence_confidence_budget_guard.py"] in COMMANDS


def test_final_is_exact_across_authorities() -> None:
    blocks = []
    for path in AUTHORITIES:
        text = (ROOT / path).read_text(encoding="ascii")
        blocks.append(text[text.index(FINAL_START) : text.index(FINAL_END) + len(FINAL_END)])
    assert len(set(blocks)) == 1
    assert "GOVERNANCE_FOUNDATION_COMPLETED_MERGED_VALIDATED" in blocks[0]
