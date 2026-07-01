import json
from pathlib import Path

from fcf.api.portfolio_paper_execution_api import handle_portfolio_paper_execution


FIXTURE_PATH = Path("fixtures/paper_order_portfolios_multi_asset.json")


def _load_cases():
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _case_by_id(case_id):
    return {
        case["case_id"]: case
        for case in _load_cases()
    }[case_id]


def _assert_counts_match_expected(response, expected):
    data = response["data"]

    assert response["ok"] is expected["ok"]
    assert data["portfolio_status"] == expected["portfolio_status"]
    assert data["order_count"] == expected["order_count"]
    assert data["filled_count"] == expected["filled_count"]
    assert data["sandbox_rejected_count"] == expected["sandbox_rejected_count"]
    assert data["policy_denied_count"] == expected["policy_denied_count"]
    assert data["risk_denied_count"] == expected["risk_denied_count"]
    assert data["asset_class_counts"] == expected["asset_class_counts"]
    assert data["branch_counts"] == expected["branch_counts"]


def test_portfolio_paper_execution_api_stable_response_schema(tmp_path):
    case = _case_by_id("portfolio_all_fill")

    response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(tmp_path / case["case_id"]),
    )

    assert set(response.keys()) == {
        "ok",
        "api",
        "api_version",
        "error",
        "data",
    }
    assert response["api"] == "portfolio_paper_execution_api"
    assert response["api_version"] == "0.1.0"
    assert response["error"] is None
    assert response["data"]["execution_mode"] == "paper"


def test_portfolio_paper_execution_all_fill_matches_fixture_expected(tmp_path):
    case = _case_by_id("portfolio_all_fill")

    response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(tmp_path / case["case_id"]),
    )

    _assert_counts_match_expected(response, case["expected"])

    data = response["data"]

    assert response["ok"] is True
    assert data["portfolio_status"] == "completed"
    assert len(data["results"]) == 4

    for result in data["results"]:
        assert result["actual_branch"] == "fill_success"
        assert result["ok"] is True
        assert result["execution_status"] == "filled"
        assert result["sandbox_event_written"] is True
        assert result["real_execution"] is False


def test_portfolio_paper_execution_mixed_results_matches_fixture_expected(tmp_path):
    case = _case_by_id("portfolio_mixed_results")

    response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(tmp_path / case["case_id"]),
    )

    _assert_counts_match_expected(response, case["expected"])

    data = response["data"]
    branches = {
        result["order_id"]: result["actual_branch"]
        for result in data["results"]
    }

    assert response["ok"] is True
    assert data["portfolio_status"] == "partial"
    assert set(branches.values()) == {
        "fill_success",
        "sandbox_reject",
        "policy_deny",
        "risk_deny",
    }

    for result in data["results"]:
        if result["actual_branch"] in {"fill_success", "sandbox_reject"}:
            assert result["sandbox_event_written"] is True
        if result["actual_branch"] in {"policy_deny", "risk_deny"}:
            assert result["sandbox_event_written"] is False


def test_portfolio_paper_execution_policy_deny_blocks_before_order_execution(tmp_path):
    case = _case_by_id("portfolio_policy_deny")

    response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(tmp_path / case["case_id"]),
    )

    _assert_counts_match_expected(response, case["expected"])

    assert response["ok"] is False
    assert response["error"]["type"] == "PortfolioPolicyDeny"
    assert response["error"]["not_exchange_reject"] is True

    for result in response["data"]["results"]:
        assert result["actual_branch"] == "blocked_by_portfolio_policy"
        assert result["sandbox_event_written"] is False
        assert result["real_execution"] is False


def test_portfolio_paper_execution_risk_deny_blocks_before_order_execution(tmp_path):
    case = _case_by_id("portfolio_risk_deny")

    response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(tmp_path / case["case_id"]),
    )

    _assert_counts_match_expected(response, case["expected"])

    assert response["ok"] is False
    assert response["error"]["type"] == "PortfolioRiskDeny"
    assert response["error"]["not_exchange_reject"] is True
    assert "max_order_count_exceeded" in response["error"]["deny_reasons"]

    for result in response["data"]["results"]:
        assert result["actual_branch"] == "blocked_by_portfolio_risk"
        assert result["sandbox_event_written"] is False
        assert result["real_execution"] is False


def test_portfolio_paper_execution_safe_boundary_for_all_cases(tmp_path):
    for case in _load_cases():
        response = handle_portfolio_paper_execution(
            case["request"],
            output_dir=str(tmp_path / case["case_id"]),
        )

        boundary = response["data"]["safe_boundary"]

        assert boundary["execution_mode"] == "paper"
        assert boundary["real_order"] is False
        assert boundary["real_execution"] is False
        assert boundary["real_exchange_api"] is False
        assert boundary["real_money_impact"] is False
        assert boundary["no_real_exchange_api"] is True
        assert boundary["no_real_order_placement"] is True
        assert boundary["no_exchange_api_key_storage"] is True
        assert boundary["no_wallet_private_key_access"] is True
        assert boundary["policy_risk_cannot_be_bypassed"] is True


def test_portfolio_paper_execution_notional_summary_is_present(tmp_path):
    case = _case_by_id("portfolio_all_fill")

    response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(tmp_path / case["case_id"]),
    )

    data = response["data"]

    assert data["total_notional"] > 0
    assert set(data["notional_by_asset_class"].keys()) == {
        "commodities",
        "crypto",
        "equities",
        "fx",
    }
    assert all(value > 0 for value in data["notional_by_asset_class"].values())
