import json
import subprocess
import sys
from pathlib import Path

from scripts.run_p10_dify_safe_package_summary import run_smoke


DOC = Path("docs/98_p10_post_closeout_dify_safe_package_summary.md")


def test_p10_dify_safe_package_summary_doc_exists_and_mentions_scope():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P10-D9" in text
    assert "Post-closeout Dify-safe Paper Operations Package Summary" in text
    assert "Dify-safe global regression adapter" in text
    assert "operator review response templates" in text
    assert "paper-only operator runbook" in text
    assert "failure triage guide" in text
    assert "Dify workflow node contract" in text


def test_p10_dify_safe_package_summary_command_and_outputs():
    text = DOC.read_text(encoding="utf-8")

    assert "python scripts/run_p10_dify_safe_package_summary.py" in text

    for item in [
        "status",
        "runner",
        "runner_version",
        "package_summary",
        "deliverables",
        "components",
        "safe_boundary",
    ]:
        assert item in text


def test_p10_dify_safe_package_summary_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p10_dify_safe_package_summary"
    assert result["runner_version"] == "0.1.0"


def test_p10_dify_safe_package_summary_ready_for_bridge_plan():
    result = run_smoke()
    summary = result["package_summary"]

    assert summary["phase"] == "P10"
    assert summary["post_closeout_package_summary"] is True
    assert summary["p10_acceptance_completed"] is True
    assert summary["ready_for_p10_d8_closeout"] is True
    assert summary["dify_global_regression_ok"] is True
    assert summary["operator_response_type"] == "global_regression_passed"
    assert summary["operator_response_passed"] is True
    assert summary["operator_review_required"] is True
    assert summary["ready_for_operator_review"] is True
    assert summary["deliverables_all_present"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_p10_d10_bridge_plan"] is True


def test_p10_dify_safe_package_summary_deliverables():
    result = run_smoke()
    deliverables = result["deliverables"]

    assert deliverables["deliverable_count"] == 11
    assert deliverables["present_count"] == 11
    assert deliverables["all_present"] is True

    for name, item in deliverables["items"].items():
        assert name
        assert item["path"]
        assert item["exists"] is True


def test_p10_dify_safe_package_summary_components():
    result = run_smoke()
    components = result["components"]

    assert components["p10_acceptance_smoke"]["status"] == "completed"
    assert components["p10_acceptance_smoke"]["ready_for_p10_d8_closeout"] is True

    assert components["dify_global_regression_adapter"]["ok"] is True
    assert components["dify_global_regression_adapter"]["api"] == "dify_global_regression_api"
    assert components["dify_global_regression_adapter"]["operator_review_required"] is True
    assert components["dify_global_regression_adapter"]["ready_for_operator_review"] is True

    assert components["operator_review_response"]["response_type"] == "global_regression_passed"
    assert components["operator_review_response"]["template"] == "operator_review_response_templates"


def test_p10_dify_safe_package_summary_safe_boundary_and_doc_safety():
    result = run_smoke()
    boundary = result["safe_boundary"]
    text = DOC.read_text(encoding="utf-8")

    assert boundary["paper_only"] is True
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["operator_review_required"] is True
    assert boundary["auto_live_trading"] is False
    assert boundary["bypass_operator_review"] is False
    assert boundary["bypass_policy_risk_safe_boundary"] is False

    for item in [
        "不接真实交易所 API",
        "不保存真实 API key",
        "不读取钱包私钥",
        "不真实下单",
        "不读取真实账户余额",
        "不读取真实仓位",
        "不声明真实成交",
        "不声明真实资金影响",
        "不自动绕过人工复核",
        "不绕过 policy / risk / safe_boundary",
        "不把 paper-only passed 解释成真实交易信号",
        "不把 paper-only passed 解释成真实成交",
    ]:
        assert item in text


def test_p10_dify_safe_package_summary_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_p10_dify_safe_package_summary.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["package_summary"]["ready_for_p10_d10_bridge_plan"] is True
