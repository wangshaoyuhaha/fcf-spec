from pathlib import Path

from scripts.control_center_fcp_0001_data_entitlement_provenance_readiness_guard import (
    AUTHORITY_PATHS,
    LOCK_END,
    LOCK_START,
    FINAL_END,
    FINAL_START,
    build_fcp_0001_guard_report,
)


ROOT = Path(__file__).resolve().parents[2]


def _lock_block(text: str) -> str:
    start = text.index(LOCK_START)
    end = text.index(LOCK_END) + len(LOCK_END)
    return text[start:end]


def test_lock_is_exact_across_all_active_authorities() -> None:
    texts = tuple((ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS)
    blocks = tuple(_lock_block(text) for text in texts)
    assert len(set(blocks)) == 1
    assert "Status: DELIVERY_IMPLEMENTED_VALIDATION_PENDING" in blocks[0]
    assert "FCF-FCP-0001 remains NEEDS_RESEARCH" in " ".join(blocks[0].split())
    assert "No P48 is created." in blocks[0]


def test_d6_guard_passes_locked_repository() -> None:
    report = build_fcp_0001_guard_report(ROOT)
    assert report["ok"] is True
    assert all(report["checks"].values())


def test_final_sync_is_exact_across_all_active_authorities() -> None:
    texts = tuple((ROOT / path).read_text(encoding="ascii") for path in AUTHORITY_PATHS)
    blocks = []
    for text in texts:
        start = text.index(FINAL_START)
        end = text.index(FINAL_END) + len(FINAL_END)
        blocks.append(text[start:end])
    assert len(set(blocks)) == 1
    assert "Status: GOVERNANCE_FOUNDATION_COMPLETED_MERGED_VALIDATED" in blocks[0]
    assert "315ca4dba01e53448e39131418c153fa73ad2aa0" in blocks[0]
    assert "4a0c29cc4b7ab8d2d9b78b0a014be967f7ef485e" in blocks[0]


def test_d6_document_preserves_validation_order_and_boundary() -> None:
    text = (
        ROOT
        / "docs/FCF_FCP_0001_DATA_ENTITLEMENT_PROVENANCE_READINESS_FOUNDATION_APP_1_D6.md"
    ).read_text(encoding="ascii")
    assert "Status: COMPLETE_VALIDATED_READY_FOR_MANUAL_MERGE" in text
    assert "full pytest" in text
    assert "python scripts/run_all_checks.py" in text
    assert "5370 passed" in text
    assert "ALL CHECKS PASSED" in text
    assert "FCF-FCP-0001 from NEEDS_RESEARCH" in text
    assert "no P48 is created" in text
