import json
from pathlib import Path

from fcf.api.portfolio_paper_execution_api import handle_portfolio_paper_execution
from fcf.api.portfolio_paper_execution_response_templates import (
    render_portfolio_paper_execution_user_response,
)


FIXTURE_PATH = Path("fixtures/paper_order_portfolios_multi_asset.json")


def _load_cases():
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _case(case_id):
    return {case["case_id"]: case for case in _load_cases()}[case_id]


def _render(case_id, tmp_path):
    case = _case(case_id)
    api_response = handle_portfolio_paper_execution(
        case["request"],
        output_dir=str(tmp_path / case_id),
    )
    return render_portfolio_paper_execution_user_response(api_response)


def _assert_base(response):
    assert set(response.keys()) == {
        "response_type",
        "template",
        "template_version",
        "title",
        "message",
        "fields",
        "safety_notice",
    }
    assert response["template"] == "portfolio_paper_execution_response_templates"
    assert response["template_version"] == "0.1.0"
    assert "没有真实下单" in response["safety_notice"]
    assert "没有连接真实交易所" in response["safety_notice"]
    assert "没有保存真实 API key" in response["safety_notice"]
    assert "没有读取钱包私钥" in response["safety_notice"]
    assert "没有真实成交" in response["safety_notice"]
    assert "没有真实资金影响" in response["safety_notice"]

    fields = response["fields"]
    assert fields["real_order"] is False
    assert fields["real_execution"] is False
    assert fields["real_exchange_api"] is False
    assert fields["real_money_impact"] is False


def test_portfolio_response_success(tmp_path):
    response = _render("portfolio_all_fill", tmp_path)
    _assert_base(response)

    assert response["response_type"] == "portfolio_paper_success"
    assert response["fields"]["portfolio_status"] == "completed"
    assert response["fields"]["filled_count"] == 4
    assert "没有真实成交" in response["message"]


def test_portfolio_response_partial_success(tmp_path):
    response = _render("portfolio_mixed_results", tmp_path)
    _assert_base(response)

    assert response["response_type"] == "portfolio_paper_partial_success"
    assert response["fields"]["portfolio_status"] == "partial"
    assert response["fields"]["filled_count"] == 1
    assert response["fields"]["sandbox_rejected_count"] == 1
    assert response["fields"]["policy_denied_count"] == 1
    assert response["fields"]["risk_denied_count"] == 1
    assert "sandbox reject 不是交易所真实拒单" in response["message"]


def test_portfolio_response_policy_deny(tmp_path):
    response = _render("portfolio_policy_deny", tmp_path)
    _assert_base(response)

    assert response["response_type"] == "portfolio_policy_deny"
    assert response["fields"]["portfolio_policy_denied"] is True
    assert response["fields"]["portfolio_risk_denied"] is False
    assert response["fields"]["not_exchange_reject"] is True
    assert "不是交易所真实拒单" in response["message"]


def test_portfolio_response_risk_deny(tmp_path):
    response = _render("portfolio_risk_deny", tmp_path)
    _assert_base(response)

    assert response["response_type"] == "portfolio_risk_deny"
    assert response["fields"]["portfolio_policy_denied"] is False
    assert response["fields"]["portfolio_risk_denied"] is True
    assert response["fields"]["not_exchange_reject"] is True
    assert "不是交易所真实拒单" in response["message"]


def test_portfolio_response_schema_error():
    api_response = handle_portfolio_paper_execution(
        {
            "portfolio_id": "bad-portfolio",
            "orders": [],
        }
    )
    response = render_portfolio_paper_execution_user_response(api_response)
    _assert_base(response)

    assert response["response_type"] == "portfolio_schema_error"
    assert response["fields"]["portfolio_schema_error"] is True
    assert response["fields"]["not_exchange_reject"] is True


def test_portfolio_response_exposure_fields(tmp_path):
    response = _render("portfolio_all_fill", tmp_path)
    fields = response["fields"]

    assert fields["asset_class_counts"] == {
        "commodities": 1,
        "crypto": 1,
        "equities": 1,
        "fx": 1,
    }
    assert fields["branch_counts"] == {"fill_success": 4}
    assert fields["total_notional"] > 0
    assert set(fields["notional_by_asset_class"].keys()) == {
        "commodities",
        "crypto",
        "equities",
        "fx",
    }
