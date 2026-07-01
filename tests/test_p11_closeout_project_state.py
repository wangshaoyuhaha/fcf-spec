from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response
from fcf.regression.regression_stability_gate import evaluate_regression_stability_gate
from scripts.run_p10_dify_safe_package_summary import run_smoke as run_p10_package_summary
from scripts.run_p11_acceptance_smoke import run_smoke as run_p11_acceptance_smoke


CLOSEOUT_DOC = Path("docs/107_p11_closeout_project_state.md")


def _text():
    return CLOSEOUT_DOC.read_text(encoding="utf-8")


def test_p11_closeout_doc_exists():
    assert CLOSEOUT_DOC.exists()


def test_p11_closeout_doc_mentions_phase11_days():
    text = _text()

    for day in ["P11-D1", "P11-D2", "P11-D3", "P11-D4", "P11-D5", "P11-D6", "P11-D7", "P11-D8"]:
        assert day in text


def test_p11_closeout_doc_mentions_key_artifacts():
    text = _text()

    for artifact in [
        "docs/100_p11_release_readiness_plan.md",
        "docs/101_p11_operator_handoff_package.md",
        "docs/102_p11_versioned_run_commands.md",
        "docs/103_p11_artifact_inventory.md",
        "docs/104_p11_maintenance_checklist.md",
        "docs/105_p11_regression_stability_gate.md",
        "docs/106_p11_acceptance_smoke.md",
        "docs/107_p11_closeout_project_state.md",
        "fcf/regression/regression_stability_gate.py",
        "scripts/run_p11_acceptance_smoke.py",
    ]:
        assert artifact in text


def test_p11_closeout_doc_mentions_completed_capabilities():
    text = _text()

    for item in [
        "release readiness plan",
        "operator handoff package",
        "versioned run commands document",
        "artifact inventory and ownership map",
        "maintenance checklist",
        "regression stability gate",
        "Phase 11 acceptance smoke",
        "ready_for_p11_d8_closeout=true",
    ]:
        assert item in text


def test_p11_closeout_acceptance_smoke_still_completed():
    result = run_p11_acceptance_smoke()
    summary = result["acceptance_summary"]

    assert result["status"] == "completed"
    assert summary["phase"] == "P11"
    assert summary["ready_for_p11_d8_closeout"] is True
    assert summary["regression_stability_gate_ok"] is True
    assert summary["dify_global_regression_ok"] is True
    assert summary["operator_response_passed"] is True
    assert summary["safe_boundary_ok"] is True


def test_p11_closeout_regression_gate_still_completed():
    package = run_p10_package_summary()
    result = evaluate_regression_stability_gate(package)

    assert result["status"] == "completed"
    assert result["ok"] is True
    assert result["violations"] == []
    assert result["ready_for_p11_d7_acceptance_smoke"] is True


def test_p11_closeout_adapter_and_template_still_pass():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "p11-d8-closeout",
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
    assert api_response["data"]["operator_review_required"] is True
    assert api_response["data"]["ready_for_operator_review"] is True
    assert api_response["data"]["safe_boundary"]["real_execution"] is False
    assert api_response["data"]["safe_boundary"]["bypass_operator_review"] is False
    assert user_response["response_type"] == "global_regression_passed"
    assert user_response["fields"]["real_execution"] is False
    assert user_response["fields"]["bypass_policy_risk_safe_boundary"] is False


def test_p11_closeout_doc_keeps_safety_boundaries_and_next_stage():
    text = _text()

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
        "P11-D9",
        "P11-D10",
        "Phase 12",
        "Documentation hardening, archive readiness, and final non-production delivery package",
    ]:
        assert item in text
