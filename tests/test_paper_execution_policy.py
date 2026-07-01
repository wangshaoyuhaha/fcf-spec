from fcf.policy.paper_execution_policy import (
    DENY_RULES,
    describe_paper_execution_policy,
    evaluate_paper_execution_policy,
)


def _sample_policy_request():
    return {
        "raw_order": {
            "asset_class": "crypto",
            "symbol": "BTCUSDT",
            "venue": "binance",
            "market_type": "perp",
            "side": "buy",
            "order_type": "limit",
            "quantity": "0.25",
            "price": "60050.5",
            "source": "unit_test_policy",
            "correlation_id": "p6-d2-policy",
            "metadata": {
                "note": "paper only",
            },
        },
        "simulation_mode": "simulated_fill",
        "metadata": {
            "workflow": "unit_test",
        },
    }


def test_describe_paper_execution_policy_declares_rules_and_boundary():
    description = describe_paper_execution_policy()

    assert description["gate"] == "paper_execution_policy"
    assert description["gate_version"] == "0.1.0"
    assert "real_execution_requested" in description["deny_rules"]
    assert "save_api_key_requested" in description["deny_rules"]
    assert "read_private_key_requested" in description["deny_rules"]
    assert description["decision_values"] == ["allowed", "denied"]
    assert description["safe_boundary"]["execution_mode"] == "paper"
    assert description["safe_boundary"]["real_order"] is False
    assert description["safe_boundary"]["real_execution"] is False
    assert description["safe_boundary"]["no_real_exchange_api"] is True


def test_policy_allows_safe_paper_request():
    result = evaluate_paper_execution_policy(_sample_policy_request())

    assert result["ok"] is True
    assert result["gate"] == "paper_execution_policy"
    assert result["gate_version"] == "0.1.0"
    assert result["decision"] == "allowed"
    assert result["error"] is None
    assert result["data"]["policy_allowed"] is True
    assert "real_execution_requested" in result["data"]["checked_fields"]
    assert result["data"]["safe_boundary"]["real_order"] is False


def test_policy_rejects_non_dict_request():
    result = evaluate_paper_execution_policy(None)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["error"]["type"] == "PolicyDeny"
    assert "dict" in result["error"]["message"]
    assert result["policy_violation"]["field"] == "request"


def test_policy_rejects_top_level_real_execution_requested():
    request = _sample_policy_request()
    request["real_execution_requested"] = True

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["error"]["type"] == "PolicyDeny"
    assert "real execution" in result["error"]["message"]
    assert result["policy_violation"]["field"] == "real_execution_requested"
    assert result["policy_violation"]["location"] == "request"


def test_policy_rejects_raw_order_real_order():
    request = _sample_policy_request()
    request["raw_order"]["real_order"] = True

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["policy_violation"]["field"] == "real_order"
    assert result["policy_violation"]["location"] == "raw_order"
    assert "real order" in result["error"]["message"]


def test_policy_rejects_request_metadata_save_api_key():
    request = _sample_policy_request()
    request["metadata"]["save_api_key_requested"] = "true"

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["policy_violation"]["field"] == "save_api_key_requested"
    assert result["policy_violation"]["location"] == "request.metadata"
    assert "API keys" in result["error"]["message"]


def test_policy_rejects_raw_order_metadata_read_private_key():
    request = _sample_policy_request()
    request["raw_order"]["metadata"]["read_private_key_requested"] = "yes"

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["policy_violation"]["field"] == "read_private_key_requested"
    assert result["policy_violation"]["location"] == "raw_order.metadata"
    assert "private keys" in result["error"]["message"]


def test_policy_rejects_bypass_risk_requested():
    request = _sample_policy_request()
    request["bypass_risk_requested"] = 1

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["policy_violation"]["field"] == "bypass_risk_requested"
    assert "risk" in result["error"]["message"]


def test_policy_rejects_force_execute_requested():
    request = _sample_policy_request()
    request["force_execute_requested"] = True

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["policy_violation"]["field"] == "force_execute_requested"
    assert "force execution" in result["error"]["message"]


def test_policy_rejects_convert_paper_to_real_requested():
    request = _sample_policy_request()
    request["convert_paper_to_real_requested"] = True

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["policy_violation"]["field"] == "convert_paper_to_real_requested"
    assert "paper order to real order" in result["error"]["message"]


def test_policy_rejects_place_real_order_requested():
    request = _sample_policy_request()
    request["place_real_order_requested"] = True

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["policy_violation"]["field"] == "place_real_order_requested"
    assert "real orders" in result["error"]["message"]


def test_policy_rejects_connect_exchange_requested():
    request = _sample_policy_request()
    request["connect_exchange_requested"] = True

    result = evaluate_paper_execution_policy(request)

    assert result["ok"] is False
    assert result["policy_violation"]["field"] == "connect_exchange_requested"
    assert "exchange" in result["error"]["message"]


def test_policy_rejects_all_defined_deny_rules_when_true():
    for field in DENY_RULES:
        request = _sample_policy_request()
        request[field] = True

        result = evaluate_paper_execution_policy(request)

        assert result["ok"] is False
        assert result["decision"] == "denied"
        assert result["policy_violation"]["field"] == field
        assert result["error"]["type"] == "PolicyDeny"
