import json
import subprocess
import sys
from pathlib import Path

from scripts.run_p11_acceptance_smoke import run_smoke


DOC = Path("docs/106_p11_acceptance_smoke.md")


def test_p11_acceptance_doc_exists_and_mentions_scope():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P11-D7" in text
    assert "Phase 11 acceptance smoke" in text
    assert "P10 Dify-safe package summary" in text
    assert "P11 regression stability gate" in text
    assert "Dify-safe global regression adapter" in text
    assert "operator review response templates" in text


def test_p11_acceptance_doc_mentions_phase11_days():
    text = DOC.read_text(encoding="utf-8")

    for day in ["P11-D1", "P11-D2", "P11-D3", "P11-D4", "P11-D5", "P11-D6", "P11-D7"]:
        assert day in text


def test_p11_acceptance_doc_mentions_command_outputs_and_targets():
    text = DOC.read_text(encoding="utf-8")

    assert "python scripts/run_p11_acceptance_smoke.py" in text

    for item in [
        "status",
        "runner",
        "runner_version",
        "acceptance_summary",
        "components",
        "safe_boundary",
        "ready_for_p11_d8_closeout true",
    ]:
        assert item in text


def test_p11_acceptance_smoke_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p11_acceptance_smoke"
    assert result["runner_version"] == "0.1.0"


def test_p11_acceptance_summary_ready_for_closeout():
    result = run_smoke()
    summary = result["acceptance_summary"]

    assert summary["phase"] == "P11"
    assert summary["phase_name"] == "Release readiness, operator handoff package, and long-term maintainability"
    assert summary["accepted_days"] == ["P11-D1", "P11-D2", "P11-D3", "P11-D4", "P11-D5", "P11-D6", "P11-D7"]
    assert summary["p10_package_completed"] is True
    assert summary["p10_package_ready_for_bridge"] is True
    assert summary["regression_stability_gate_completed"] is True
    assert summary["regression_stability_gate_ok"] is True
    assert summary["ready_for_p11_d7_acceptance_smoke"] is True
    assert summary["dify_global_regression_ok"] is True
    assert summary["operator_response_type"] == "global_regression_passed"
    assert summary["operator_response_passed"] is True
    assert summary["operator_review_required"] is True
    assert summary["ready_for_operator_review"] is True
    assert summary["p11_docs_ready"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_p11_d8_closeout"] is True


def test_p11_acceptance_components():
    result = run_smoke()
    components = result["components"]

    assert components["p10_package_summary"]["status"] == "completed"
    assert components["p10_package_summary"]["ready_for_p10_d10_bridge_plan"] is True

    assert components["regression_stability_gate"]["status"] == "completed"
    assert components["regression_stability_gate"]["ok"] is True
    assert components["regression_stability_gate"]["ready_for_p11_d7_acceptance_smoke"] is True
    assert components["regression_stability_gate"]["violation_count"] == 0

    assert components["dify_global_regression_adapter"]["ok"] is True
    assert components["dify_global_regression_adapter"]["api"] == "dify_global_regression_api"
    assert components["dify_global_regression_adapter"]["operator_review_required"] is True
    assert components["dify_global_regression_adapter"]["ready_for_operator_review"] is True

    assert components["operator_review_response"]["response_type"] == "global_regression_passed"
    assert components["operator_review_response"]["template"] == "operator_review_response_templates"


def test_p11_acceptance_docs_readiness():
    result = run_smoke()
    docs = result["components"]["p11_docs_readiness"]

    assert docs["all_docs_present"] is True
    assert docs["doc_count"] == 7
    assert docs["present_count"] == 7

    for path, exists in docs["docs"].items():
        assert path.startswith("docs/")
        assert exists is True


def test_p11_acceptance_safe_boundary():
    result = run_smoke()
    boundary = result["safe_boundary"]

    assert boundary["paper_only"] is True
    assert boundary["execution_mode"] == "paper"
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["no_real_exchange_api"] is True
    assert boundary["no_real_order_placement"] is True
    assert boundary["no_exchange_api_key_storage"] is True
    assert boundary["no_wallet_private_key_access"] is True
    assert boundary["no_real_account_balance_read"] is True
    assert boundary["no_real_position_read"] is True
    assert boundary["does_not_claim_real_trade_success"] is True
    assert boundary["operator_review_required"] is True
    assert boundary["auto_live_trading"] is False
    assert boundary["bypass_operator_review"] is False
    assert boundary["bypass_policy_risk_safe_boundary"] is False


def test_p11_acceptance_doc_mentions_safety_boundaries():
    text = DOC.read_text(encoding="utf-8")

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
    ]:
        assert item in text


def test_p11_acceptance_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_p11_acceptance_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["acceptance_summary"]["ready_for_p11_d8_closeout"] is True
