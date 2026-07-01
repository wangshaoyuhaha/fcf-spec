from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from scripts.run_p10_acceptance_smoke import run_smoke


CLOSEOUT_DOC = Path("docs/97_p10_closeout_project_state.md")


def test_p10_closeout_doc_exists():
    assert CLOSEOUT_DOC.exists()


def test_p10_closeout_doc_mentions_phase10_days():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for day in ["P10-D1", "P10-D2", "P10-D3", "P10-D4", "P10-D5", "P10-D6", "P10-D7", "P10-D8"]:
        assert day in text


def test_p10_closeout_doc_mentions_key_artifacts():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for artifact in [
        "docs/90_p10_dify_safe_paper_operations_plan.md",
        "docs/91_p10_global_regression_dify_adapter_contract.md",
        "docs/92_p10_operator_review_response_templates.md",
        "docs/93_p10_paper_only_operator_runbook.md",
        "docs/94_p10_failure_triage_guide.md",
        "docs/95_p10_dify_workflow_node_contract.md",
        "docs/96_p10_acceptance_smoke.md",
        "fcf/api/dify_global_regression_api.py",
        "fcf/api/operator_review_response_templates.py",
        "scripts/run_p10_acceptance_smoke.py",
    ]:
        assert artifact in text


def test_p10_closeout_doc_mentions_completed_capabilities():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

    for item in [
        "Dify-safe global regression adapter",
        "operator review response templates",
        "paper-only operator runbook",
        "failure triage guide",
        "Dify workflow node contract document",
        "Phase 10 acceptance smoke",
        "ready_for_p10_d8_closeout=true",
    ]:
        assert item in text


def test_p10_closeout_acceptance_smoke_still_completed():
    result = run_smoke()
    summary = result["acceptance_summary"]

    assert result["status"] == "completed"
    assert summary["phase"] == "P10"
    assert summary["ready_for_p10_d8_closeout"] is True
    assert summary["dify_global_regression_ok"] is True
    assert summary["operator_response_passed"] is True
    assert summary["operator_review_required"] is True
    assert summary["ready_for_operator_review"] is True
    assert summary["safe_boundary_ok"] is True


def test_p10_closeout_adapter_and_template_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p10-d8-closeout",
            "operator_id": "operator-paper-review",
            "review_mode": "operator_review",
            "requested_checks": [
                "all_smokes",
                "global_report",
                "safe_boundary",
                "project_state_consistency",
            ],
            "output_format": "json",
        }
    )
    user_response = render_operator_review_response(api_response)

    assert api_response["ok"] is True
    assert api_response["data"]["ready_for_operator_review"] is True
    assert api_response["data"]["safe_boundary"]["real_execution"] is False
    assert api_response["data"]["safe_boundary"]["bypass_operator_review"] is False
    assert user_response["response_type"] == "global_regression_passed"
    assert user_response["fields"]["operator_review_required"] is True
    assert user_response["fields"]["real_execution"] is False
    assert user_response["fields"]["bypass_policy_risk_safe_boundary"] is False


def test_p10_closeout_doc_keeps_safety_boundaries_and_next_stage():
    text = CLOSEOUT_DOC.read_text(encoding="utf-8")

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
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
        "P10-D9",
        "P10-D10",
        "Phase 11",
        "Release readiness, operator handoff package, and long-term maintainability",
    ]:
        assert item in text
