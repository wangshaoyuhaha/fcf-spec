from pathlib import Path

from fcf.api.dify_global_regression_api import (
    handle_dify_global_regression_request,
)


DOC = Path("docs/91_p10_global_regression_dify_adapter_contract.md")


def _valid_request():
    return {
        "request_id": "p10-d2-smoke",
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


def test_p10_global_regression_dify_adapter_contract_doc_exists():
    text = DOC.read_text(encoding="utf-8")

    assert DOC.exists()
    assert "P10-D2" in text
    assert "handle_dify_global_regression_request" in text
    assert "Dify-safe global regression adapter contract" in text


def test_p10_global_regression_dify_adapter_valid_request_passes():
    response = handle_dify_global_regression_request(_valid_request())

    assert response["ok"] is True
    assert response["api"] == "dify_global_regression_api"
    assert response["api_version"] == "0.1.0"
    assert response["error"] is None

    data = response["data"]
    assert data["request_id"] == "p10-d2-smoke"
    assert data["operator_id"] == "operator-paper-review"
    assert data["review_mode"] == "operator_review"
    assert data["output_format"] == "json"
    assert data["operator_review_required"] is True
    assert data["ready_for_operator_review"] is True


def test_p10_global_regression_dify_adapter_runs_requested_components():
    response = handle_dify_global_regression_request(_valid_request())
    data = response["data"]

    assert data["run_all_smokes"]["status"] == "completed"
    assert data["global_regression_report"]["status"] == "completed"
    assert data["global_safe_boundary_check"]["status"] == "completed"
    assert data["global_safe_boundary_check"]["ok"] is True
    assert data["project_state_consistency_check"]["status"] == "completed"
    assert data["project_state_consistency_check"]["ok"] is True


def test_p10_global_regression_dify_adapter_default_request_passes():
    response = handle_dify_global_regression_request({})

    assert response["ok"] is True
    assert response["data"]["review_mode"] == "operator_review"
    assert response["data"]["requested_checks"] == [
        "all_smokes",
        "global_report",
        "safe_boundary",
        "project_state_consistency",
    ]
    assert response["data"]["output_format"] == "json"


def test_p10_global_regression_dify_adapter_rejects_invalid_review_mode():
    response = handle_dify_global_regression_request(
        {
            "review_mode": "live_trading",
        }
    )

    assert response["ok"] is False
    assert response["error"]["type"] == "DifyGlobalRegressionSchemaError"
    assert response["error"]["details"]["review_mode"] == "live_trading"
    assert response["data"]["safe_boundary"]["real_execution"] is False


def test_p10_global_regression_dify_adapter_rejects_invalid_output_format():
    response = handle_dify_global_regression_request(
        {
            "output_format": "html",
        }
    )

    assert response["ok"] is False
    assert response["error"]["type"] == "DifyGlobalRegressionSchemaError"
    assert response["error"]["details"]["output_format"] == "html"


def test_p10_global_regression_dify_adapter_rejects_unknown_check():
    response = handle_dify_global_regression_request(
        {
            "requested_checks": ["all_smokes", "real_exchange_balance"],
        }
    )

    assert response["ok"] is False
    assert response["error"]["type"] == "DifyGlobalRegressionSchemaError"
    assert response["error"]["details"]["unknown_checks"] == ["real_exchange_balance"]


def test_p10_global_regression_dify_adapter_safe_boundary():
    response = handle_dify_global_regression_request(_valid_request())
    boundary = response["data"]["safe_boundary"]

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
    assert boundary["operator_review_required"] is True
    assert boundary["auto_live_trading"] is False
    assert boundary["bypass_operator_review"] is False
    assert boundary["bypass_policy_risk_safe_boundary"] is False


def test_p10_global_regression_dify_adapter_doc_mentions_safety_boundaries():
    text = DOC.read_text(encoding="utf-8")

    for item in [
        "真实交易所 API",
        "真实下单",
        "真实 API key 保存",
        "钱包私钥读取",
        "真实账户余额读取",
        "真实仓位读取",
        "自动实盘交易",
        "自动绕过人工复核",
        "绕过 policy / risk / safe_boundary",
    ]:
        assert item in text
