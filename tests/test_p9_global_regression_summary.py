import json
import subprocess
import sys
from pathlib import Path

from scripts.run_p9_global_regression_summary import run_smoke


DOC = Path("docs/88_p9_post_closeout_global_regression_summary.md")


def test_p9_global_regression_summary_doc_exists_and_mentions_scope():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P9-D9" in text
    assert "Post-closeout Global Regression Summary" in text
    assert "run_all_smokes" in text
    assert "run_p9_acceptance_smoke" in text
    assert "build_global_regression_report" in text
    assert "check_global_safe_boundary" in text
    assert "check_project_state_consistency" in text


def test_p9_global_regression_summary_completes():
    result = run_smoke()

    assert result["status"] == "completed"
    assert result["runner"] == "p9_global_regression_summary"
    assert result["runner_version"] == "0.1.0"


def test_p9_global_regression_summary_ready_for_phase10():
    result = run_smoke()
    summary = result["global_summary"]

    assert summary["phase"] == "P9"
    assert summary["phase_name"] == "Global paper-only regression suite and CI-safe operational readiness"
    assert summary["post_closeout_global_regression"] is True
    assert summary["run_all_smokes_completed"] is True
    assert summary["p9_acceptance_completed"] is True
    assert summary["global_report_completed"] is True
    assert summary["global_safe_boundary_ok"] is True
    assert summary["project_state_consistency_ok"] is True
    assert summary["closeout_doc_exists"] is True
    assert summary["ready_for_phase10_planning"] is True


def test_p9_global_regression_summary_components():
    result = run_smoke()
    components = result["components"]

    assert components["run_all_smokes"]["status"] == "completed"
    assert components["run_all_smokes"]["counts"] == {
        "total_smoke_count": 2,
        "completed_count": 2,
        "failed_count": 0,
        "ready_count": 2,
    }

    assert components["p9_acceptance_smoke"]["status"] == "completed"
    assert components["p9_acceptance_smoke"]["ready_for_p9_d8_closeout"] is True

    assert components["global_regression_report"]["status"] == "completed"
    assert components["global_regression_report"]["report_version"] == "0.1.0"

    assert components["global_safe_boundary_checker"]["status"] == "completed"
    assert components["global_safe_boundary_checker"]["ok"] is True
    assert components["global_safe_boundary_checker"]["violation_count"] == 0

    assert components["project_state_consistency_checker"]["status"] == "completed"
    assert components["project_state_consistency_checker"]["ok"] is True
    assert components["project_state_consistency_checker"]["violation_count"] == 0

    assert components["p9_closeout_doc"]["path"] == "docs/87_p9_closeout_project_state.md"
    assert components["p9_closeout_doc"]["exists"] is True


def test_p9_global_regression_summary_safe_boundary():
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
    assert boundary["ci_secret_required"] is False
    assert boundary["production_deployment"] is False


def test_p9_global_regression_summary_doc_mentions_safety_boundaries():
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
        "不把 paper execution 伪装成 real execution",
    ]:
        assert item in text


def test_p9_global_regression_summary_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_p9_global_regression_summary.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["global_summary"]["ready_for_phase10_planning"] is True
