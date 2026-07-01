import json
import subprocess
import sys
from pathlib import Path

from scripts.run_all_smokes import run_all_smokes


DOC = Path("docs/81_p9_run_all_smokes_entrypoint.md")


def test_p9_run_all_smokes_doc_exists_and_mentions_entrypoint():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P9-D2" in text
    assert "scripts/run_all_smokes.py" in text
    assert "python scripts/run_all_smokes.py" in text
    assert "P7 guarded paper execution regression summary" in text
    assert "P8 portfolio guarded paper regression summary" in text


def test_p9_run_all_smokes_function_completes():
    result = run_all_smokes()

    assert result["status"] == "completed"
    assert result["runner"] == "run_all_smokes"
    assert result["runner_version"] == "0.1.0"


def test_p9_run_all_smokes_counts():
    result = run_all_smokes()

    assert result["counts"] == {
        "total_smoke_count": 2,
        "completed_count": 2,
        "failed_count": 0,
        "ready_count": 2,
    }


def test_p9_run_all_smokes_suites():
    result = run_all_smokes()
    suites = {suite["name"]: suite for suite in result["suites"]}

    assert set(suites.keys()) == {
        "p7_guarded_paper_execution_regression",
        "p8_portfolio_guarded_paper_regression",
    }

    assert suites["p7_guarded_paper_execution_regression"]["phase"] == "P7"
    assert suites["p7_guarded_paper_execution_regression"]["status"] == "completed"
    assert suites["p7_guarded_paper_execution_regression"]["ready"] is True

    assert suites["p8_portfolio_guarded_paper_regression"]["phase"] == "P8"
    assert suites["p8_portfolio_guarded_paper_regression"]["status"] == "completed"
    assert suites["p8_portfolio_guarded_paper_regression"]["ready"] is True


def test_p9_run_all_smokes_readiness():
    result = run_all_smokes()

    assert result["readiness"]["phase"] == "P9"
    assert result["readiness"]["global_regression_suite_ready"] is True
    assert result["readiness"]["ready_for_p9_d3_report_schema"] is True


def test_p9_run_all_smokes_safe_boundary():
    result = run_all_smokes()
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


def test_p9_run_all_smokes_cli_outputs_json_completed():
    completed = subprocess.run(
        [sys.executable, "scripts/run_all_smokes.py"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["status"] == "completed"
    assert payload["counts"]["total_smoke_count"] == 2
    assert payload["readiness"]["global_regression_suite_ready"] is True
