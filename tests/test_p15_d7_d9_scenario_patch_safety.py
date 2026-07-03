from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_doc(name: str) -> str:
    return (ROOT / "docs" / name).read_text(encoding="utf-8")


def test_p15_d7_scenario_report_browser_is_read_only_and_paper_only():
    text = read_doc("p15_scenario_report_browser_plan.md")
    assert "read-only index" in text
    assert "scenario engine outputs" in text
    assert "paper-only simulations" in text
    assert "no real execution" in text


def test_p15_d8_patch_review_queue_blocks_auto_mutation():
    text = read_doc("p15_patch_proposal_review_queue.md")
    assert "patch proposal is not patch application" in text
    assert "no auto-merge" in text
    assert "no parameter auto-update" in text
    assert "operator approval is required" in text


def test_p15_d9_safety_regression_report_preserves_release_boundary():
    text = read_doc("p15_safety_boundary_regression_report.md")
    assert "real_exchange_api" in text
    assert "real_money_impact" in text
    assert "operator_review_required" in text
    assert "GitHub Release is not deploy" in text
