from pathlib import Path

from scripts.run_p9_global_regression_summary import run_smoke


PLAN_DOC = Path("docs/90_p10_dify_safe_paper_operations_plan.md")


def test_p10_dify_safe_paper_operations_plan_doc_exists():
    assert PLAN_DOC.exists()


def test_p10_dify_safe_paper_operations_plan_mentions_phase10_theme():
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "P10-D1" in text
    assert "Phase 10" in text
    assert "Dify-safe paper operations packaging and operator review readiness" in text
    assert "Dify 安全纸面操作封装与人工复核准备" in text


def test_p10_dify_safe_paper_operations_plan_mentions_core_targets():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "Dify-safe global regression adapter",
        "operator review response templates",
        "paper-only operator runbook",
        "failure triage guide",
        "Dify workflow node contract document",
        "handoff package for non-production paper-only use",
        "Phase 10 acceptance smoke",
    ]:
        assert item in text


def test_p10_dify_safe_paper_operations_plan_mentions_entrypoints_and_contracts():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for item in [
        "fcf/api/dify_global_regression_api.py",
        "handle_dify_global_regression_request",
        "fcf/api/operator_review_response_templates.py",
        "docs/91_p10_paper_only_operator_runbook.md",
        "docs/92_p10_failure_triage_guide.md",
        "docs/93_p10_dify_workflow_node_contract.md",
    ]:
        assert item in text


def test_p10_dify_safe_paper_operations_plan_mentions_route_and_safety():
    text = PLAN_DOC.read_text(encoding="utf-8")

    for day in ["P10-D1", "P10-D2", "P10-D3", "P10-D4", "P10-D5", "P10-D6", "P10-D7", "P10-D8"]:
        assert day in text

    for item in [
        "不接真实交易所 API",
        "不保存真实 API key",
        "不读取钱包私钥",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不声明真实成交",
        "不声明真实资金影响",
        "不配置 CI secret",
        "不做 production deployment",
        "不自动实盘交易",
        "不自动绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
    ]:
        assert item in text


def test_p10_dify_safe_paper_operations_plan_p9_summary_still_ready():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["global_summary"]["ready_for_phase10_planning"] is True
    assert result["global_summary"]["run_all_smokes_completed"] is True
    assert result["global_summary"]["p9_acceptance_completed"] is True
    assert result["global_summary"]["global_safe_boundary_ok"] is True
    assert result["global_summary"]["project_state_consistency_ok"] is True
