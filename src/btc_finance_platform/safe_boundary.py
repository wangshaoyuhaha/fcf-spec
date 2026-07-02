SAFE_BOUNDARY = {
    "paper_only": True,
    "execution_mode": "paper",
    "real_order": False,
    "real_execution": False,
    "real_exchange_api": False,
    "real_money_impact": False,
    "no_real_exchange_api": True,
    "no_real_order_placement": True,
    "no_exchange_api_key_storage": True,
    "no_wallet_private_key_access": True,
    "no_real_account_balance_read": True,
    "no_real_position_read": True,
    "does_not_claim_real_trade_success": True,
    "ci_secret_required": False,
    "production_deployment": False,
    "operator_review_required": True,
    "auto_live_trading": False,
    "bypass_operator_review": False,
    "bypass_policy_risk_safe_boundary": False,
}


def get_safe_boundary() -> dict:
    return dict(SAFE_BOUNDARY)


def assert_safe_boundary() -> bool:
    required_true = [
        "paper_only",
        "no_real_exchange_api",
        "no_real_order_placement",
        "no_exchange_api_key_storage",
        "no_wallet_private_key_access",
        "no_real_account_balance_read",
        "no_real_position_read",
        "does_not_claim_real_trade_success",
        "operator_review_required",
    ]

    required_false = [
        "real_order",
        "real_execution",
        "real_exchange_api",
        "real_money_impact",
        "ci_secret_required",
        "production_deployment",
        "auto_live_trading",
        "bypass_operator_review",
        "bypass_policy_risk_safe_boundary",
    ]

    for key in required_true:
        if SAFE_BOUNDARY.get(key) is not True:
            raise AssertionError(f"safe boundary key must be true: {key}")

    for key in required_false:
        if SAFE_BOUNDARY.get(key) is not False:
            raise AssertionError(f"safe boundary key must be false: {key}")

    return True
