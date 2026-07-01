from pathlib import Path

from fcf.regression.global_regression_report_schema import (
    build_global_regression_report,
)
from scripts.run_all_smokes import run_all_smokes


DOC = Path("docs/82_p9_global_regression_report_schema.md")


def test_p9_global_regression_report_schema_doc_exists():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P9-D3" in text
    assert "machine-readable global regression report schema" in text
    assert "build_global_regression_report" in text


def test_p9_global_regression_report_schema_keys():
    report = build_global_regression_report(run_all_smokes())

    assert set(report.keys()) == {
        "report_version",
        "generated_by",
        "phase",
        "status",
        "source_runner",
        "suites",
        "counts",
        "readiness",
        "safe_boundary",
        "report_path",
        "next_action",
    }


def test_p9_global_regression_report_schema_values():
    report = build_global_regression_report(run_all_smokes())

    assert report["report_version"] == "0.1.0"
    assert report["generated_by"] == "global_regression_report_schema"
    assert report["phase"] == "P9"
    assert report["status"] == "completed"
    assert report["source_runner"] == "run_all_smokes"
    assert report["next_action"] == "P9-D4：global safe boundary checker"


def test_p9_global_regression_report_counts_and_readiness():
    report = build_global_regression_report(run_all_smokes())

    assert report["counts"] == {
        "total_smoke_count": 2,
        "completed_count": 2,
        "failed_count": 0,
        "ready_count": 2,
    }
    assert report["readiness"]["phase"] == "P9"
    assert report["readiness"]["global_regression_suite_ready"] is True
    assert report["readiness"]["ready_for_p9_d3_report_schema"] is True
    assert report["readiness"]["ready_for_p9_d4_safe_boundary_checker"] is True


def test_p9_global_regression_report_suites():
    report = build_global_regression_report(run_all_smokes())
    suites = {suite["name"]: suite for suite in report["suites"]}

    assert set(suites.keys()) == {
        "p7_guarded_paper_execution_regression",
        "p8_portfolio_guarded_paper_regression",
    }
    assert suites["p7_guarded_paper_execution_regression"]["completed"] is True
    assert suites["p8_portfolio_guarded_paper_regression"]["completed"] is True


def test_p9_global_regression_report_safe_boundary():
    report = build_global_regression_report(run_all_smokes())
    boundary = report["safe_boundary"]

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


def test_p9_global_regression_report_handles_invalid_input():
    report = build_global_regression_report(None)

    assert report["status"] == "failed"
    assert report["source_runner"] is None
    assert report["suites"] == []
    assert report["counts"]["total_smoke_count"] == 0
    assert report["readiness"]["global_regression_suite_ready"] is False
    assert report["next_action"] == "Fix failing smoke / regression suite before continuing"
