from copy import deepcopy
from pathlib import Path

from fcf.api.dify_global_regression_api import handle_dify_global_regression_request
from fcf.api.operator_review_response_templates import render_operator_review_response


DOC = Path("docs/92_p10_operator_review_response_templates.md")


def _valid_request():
    return {
        "request_id": "p10-d3-review",
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


def _valid_response():
    return handle_dify_global_regression_request(_valid_request())


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
    assert response["template"] == "operator_review_response_templates"
    assert response["template_version"] == "0.1.0"
    assert "paper-only / non-production" in response["safety_notice"]
    assert "不是真实交易信号" in response["safety_notice"]
    assert "不是真实下单结果" in response["safety_notice"]
    assert "不是真实成交结果" in response["safety_notice"]
    assert "需要人工复核" in response["safety_notice"]


def _assert_no_real_claims(response):
    fields = response["fields"]

    assert fields["paper_only"] is True
    assert fields["real_order"] is False
    assert fields["real_execution"] is False
    assert fields["real_exchange_api"] is False
    assert fields["real_money_impact"] is False
    assert fields["no_real_exchange_api"] is True
    assert fields["no_real_order_placement"] is True
    assert fields["no_exchange_api_key_storage"] is True
    assert fields["no_wallet_private_key_access"] is True
    assert fields["no_real_account_balance_read"] is True
    assert fields["no_real_position_read"] is True
    assert fields["does_not_claim_real_trade_success"] is True
    assert fields["ci_secret_required"] is False
    assert fields["production_deployment"] is False
    assert fields["auto_live_trading"] is False
    assert fields["bypass_operator_review"] is False
    assert fields["bypass_policy_risk_safe_boundary"] is False


def test_p10_operator_review_response_doc_exists_and_mentions_scope():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P10-D3" in text
    assert "operator review response templates" in text
    assert "render_operator_review_response" in text


def test_p10_operator_review_response_global_regression_passed():
    response = render_operator_review_response(_valid_response())

    _assert_base(response)
    _assert_no_real_claims(response)

    assert response["response_type"] == "global_regression_passed"
    assert response["title"] == "Global paper regression passed"
    assert response["fields"]["request_id"] == "p10-d3-review"
    assert response["fields"]["operator_review_required"] is True
    assert response["fields"]["ready_for_operator_review"] is True
    assert "可以进入人工复核" in response["message"]


def test_p10_operator_review_response_global_regression_failed():
    api_response = deepcopy(_valid_response())
    api_response["data"]["run_all_smokes"]["status"] = "failed"

    response = render_operator_review_response(api_response)

    _assert_base(response)
    _assert_no_real_claims(response)

    assert response["response_type"] == "global_regression_failed"
    assert response["title"] == "Global paper regression failed"
    assert "需要人工复核" in response["message"]


def test_p10_operator_review_response_safe_boundary_failed():
    api_response = deepcopy(_valid_response())
    api_response["data"]["global_safe_boundary_check"]["ok"] = False
    api_response["data"]["global_safe_boundary_check"]["status"] = "failed"

    response = render_operator_review_response(api_response)

    _assert_base(response)
    _assert_no_real_claims(response)

    assert response["response_type"] == "safe_boundary_failed"
    assert response["title"] == "Safe boundary check failed"
    assert "必须停止并人工复核" in response["message"]


def test_p10_operator_review_response_project_state_inconsistent():
    api_response = deepcopy(_valid_response())
    api_response["data"]["project_state_consistency_check"]["ok"] = False
    api_response["data"]["project_state_consistency_check"]["status"] = "failed"

    response = render_operator_review_response(api_response)

    _assert_base(response)
    _assert_no_real_claims(response)

    assert response["response_type"] == "project_state_inconsistent"
    assert response["title"] == "Project state consistency failed"
    assert "需要人工复核" in response["message"]


def test_p10_operator_review_response_operator_review_required_for_partial_checks():
    api_response = handle_dify_global_regression_request(
        {
            "request_id": "partial-review",
            "operator_id": "operator-paper-review",
            "review_mode": "operator_review",
            "requested_checks": ["all_smokes"],
            "output_format": "json",
        }
    )

    response = render_operator_review_response(api_response)

    _assert_base(response)
    _assert_no_real_claims(response)

    assert response["response_type"] == "operator_review_required"
    assert response["title"] == "Operator review required"
    assert response["fields"]["requested_checks"] == ["all_smokes"]


def test_p10_operator_review_response_schema_error_maps_to_global_regression_failed():
    api_response = handle_dify_global_regression_request(
        {
            "review_mode": "live_trading",
        }
    )

    response = render_operator_review_response(api_response)

    _assert_base(response)
    _assert_no_real_claims(response)

    assert response["response_type"] == "global_regression_failed"
    assert "不是真实交易信号" in response["message"]


def test_p10_operator_review_response_invalid_input_requires_review():
    response = render_operator_review_response(None)

    _assert_base(response)
    _assert_no_real_claims(response)

    assert response["response_type"] == "operator_review_required"
    assert response["title"] == "Operator review required"


def test_p10_operator_review_response_doc_mentions_all_response_types_and_safety():
    text = DOC.read_text(encoding="utf-8")

    for item in [
        "global_regression_passed",
        "global_regression_failed",
        "safe_boundary_failed",
        "project_state_inconsistent",
        "operator_review_required",
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
    ]:
        assert item in text
