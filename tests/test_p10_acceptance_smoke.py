import json
import subprocess
import sys
from pathlib import Path

from scripts.run_p10_acceptance_smoke import run_smoke


DOC = Path("docs/96_p10_acceptance_smoke.md")


def test_p10_acceptance_doc_exists_and_mentions_scope():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P10-D7" in text
    assert "Phase 10 acceptance smoke" in text
    assert "P9 global regression summary" in text
    assert "Dify global regression adapter" in text
    assert "operator review response templates" in text


def test_p10_acceptance_doc_mentions_phase10_days():
    text = DOC.read_text(encoding="utf-8")

    for day in ["P10-D1", "P10-D2", "P10-D3", "P10-D4", "P10-D5", "P10-D6", "P10-D7"]:
        assert day in text


def test_p10_acceptance_doc_mentions_command_and_outputs():
    text = DOC.read_text(encoding="utf-8")

    assert "python scripts/run_p10_acceptance_smoke.py" in text

    for item in [
        "status",
        "runner",
        "runner_version",
        "acceptance_summary",
        "components",
        "safe_boundary",
    ]:
        assert item in text


def test_p10_acceptance_smoke_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p10_acceptance_smoke"
    assert result["runner_version"] == "0.1.0"


def test_p10_acceptance_summary_ready_for_closeout():
    result = run_smoke()
    summary = result["acceptance_summary"]

    assert summary["phase"] == "P10"
    assert summary["phase_name"] == "Dify-safe paper operations packaging and operator review readiness"
    assert summary["accepted_days"] == ["P10-D1", "P10-D2", "P10-D3", "P10-D4", "P10-D5", "P10-D6", "P10-D7"]
    assert summary["p9_global_regression_completed"] is True
    assert summary["ready_for_phase10_planning"] is True
    assert summary["dify_global_regression_ok"] is True
    assert summary["operator_response_type"] == "global_regression_passed"
    assert summary["operator_response_passed"] is True
    assert summary["operator_review_required"] is True
    assert summary["ready_for_operator_review"] is True
    assert summary["p10_docs_ready"] is True
    assert summary["safe_boundary_ok"] is True
    assert summary["ready_for_p10_d8_closeout"] is True


def test_p10_acceptance_components():
    result = run_smoke()
    components = result["components"]

    assert components["p9_global_regression_summary"]["status"] == "completed"
    assert components["p9_global_regression_summary"]["ready_for_phase10_planning"] is True

    assert components["dify_global_regression_adapter"]["ok"] is True
    assert components["dify_global_regression_adapter"]["api"] == "dify_global_regression_api"
    assert components["dify_global_regression_adapter"]["api_version"] == "0.1.0"
    assert components["dify_global_regression_adapter"]["operator_review_required"] is True
    assert components["dify_global_regression_adapter"]["ready_for_operator_review"] is True

    assert components["operator_review_response"]["response_type"] == "global_regression_passed"
    assert components["operator_review_response"]["template"] == "operator_review_response_templates"
    assert components["operator_review_response"]["template_version"] == "0.1.0"


def test_p10_acceptance_docs_readiness():
    result = run_smoke()
    docs = result["components"]["p10_docs_readiness"]

    assert docs["all_docs_present"] is True
    assert docs["doc_count"] == 7

    for path, exists in docs["docs"].items():
        assert path.startswith("docs/")
        assert exists is True


def test_p10_acceptance_safe_boundary():
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


def test_p10_acceptance_doc_mentions_safety_boundaries():
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
    ]:
        assert item in text


def test_p10_acceptance_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_p10_acceptance_smoke.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["acceptance_summary"]["ready_for_p10_d8_closeout"] is True
