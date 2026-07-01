import json
from collections import Counter
from pathlib import Path


FIXTURE_PATH = Path("fixtures/paper_order_portfolios_multi_asset.json")

EXPECTED_PORTFOLIO_BRANCHES = {
    "portfolio_all_fill",
    "portfolio_mixed_results",
    "portfolio_policy_deny",
    "portfolio_risk_deny",
}

EXPECTED_ASSET_CLASSES = {
    "crypto",
    "equities",
    "fx",
    "commodities",
}

EXPECTED_ORDER_BRANCHES = {
    "fill_success",
    "sandbox_reject",
    "policy_deny",
    "risk_deny",
    "blocked_by_portfolio_policy",
    "blocked_by_portfolio_risk",
}

REQUIRED_CASE_FIELDS = {
    "case_id",
    "portfolio_id",
    "branch",
    "description",
    "request",
    "expected",
}

REQUIRED_REQUEST_FIELDS = {
    "portfolio_id",
    "correlation_id",
    "source",
    "orders",
    "portfolio_policy_context",
    "portfolio_risk_context",
    "metadata",
}

REQUIRED_ORDER_FIELDS = {
    "order_id",
    "expected_branch",
    "simulation_mode",
    "raw_order",
    "risk_context",
}

REQUIRED_RAW_ORDER_FIELDS = {
    "asset_class",
    "symbol",
    "venue",
    "market_type",
    "side",
    "order_type",
    "quantity",
    "price",
    "source",
    "correlation_id",
    "metadata",
}

REQUIRED_EXPECTED_FIELDS = {
    "ok",
    "portfolio_status",
    "order_count",
    "filled_count",
    "sandbox_rejected_count",
    "policy_denied_count",
    "risk_denied_count",
    "asset_class_counts",
    "branch_counts",
    "real_execution",
    "safe_boundary",
}


def _normalize_asset_class(value):
    return str(value).strip().lower()


def _load_cases():
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_portfolio_fixture_file_exists_and_is_list():
    assert FIXTURE_PATH.exists()

    cases = _load_cases()

    assert isinstance(cases, list)
    assert len(cases) == 4


def test_portfolio_fixture_case_schema():
    cases = _load_cases()

    for case in cases:
        assert REQUIRED_CASE_FIELDS.issubset(case.keys())
        assert case["branch"] in EXPECTED_PORTFOLIO_BRANCHES
        assert case["portfolio_id"] == case["request"]["portfolio_id"]

        request = case["request"]
        expected = case["expected"]

        assert REQUIRED_REQUEST_FIELDS.issubset(request.keys())
        assert REQUIRED_EXPECTED_FIELDS.issubset(expected.keys())
        assert request["source"] == "p8_portfolio_fixture"
        assert isinstance(request["orders"], list)
        assert len(request["orders"]) == expected["order_count"]
        assert expected["real_execution"] is False
        assert expected["safe_boundary"]["paper_only"] is True
        assert expected["safe_boundary"]["no_real_exchange_api"] is True
        assert expected["safe_boundary"]["no_real_order_placement"] is True
        assert expected["safe_boundary"]["no_exchange_api_key_storage"] is True
        assert expected["safe_boundary"]["no_wallet_private_key_access"] is True


def test_portfolio_fixture_order_schema_and_safety_boundary():
    cases = _load_cases()

    for case in cases:
        for order in case["request"]["orders"]:
            assert REQUIRED_ORDER_FIELDS.issubset(order.keys())
            assert REQUIRED_RAW_ORDER_FIELDS.issubset(order["raw_order"].keys())

            raw_order = order["raw_order"]

            assert order["expected_branch"] in EXPECTED_ORDER_BRANCHES
            assert order["simulation_mode"] in {
                "simulated_fill",
                "simulated_reject",
            }
            assert raw_order["source"] == "p8_portfolio_fixture"
            assert raw_order["metadata"]["paper_only"] is True
            assert raw_order.get("real_order") is not True
            assert raw_order.get("real_execution") is not True
            assert raw_order.get("real_exchange_api") is not True


def test_portfolio_fixture_covers_expected_portfolio_branches():
    cases = _load_cases()
    branches = {case["branch"] for case in cases}

    assert branches == EXPECTED_PORTFOLIO_BRANCHES


def test_portfolio_fixture_covers_expected_asset_classes():
    cases = _load_cases()

    asset_classes = {
        _normalize_asset_class(order["raw_order"]["asset_class"])
        for case in cases
        for order in case["request"]["orders"]
    }

    assert asset_classes == EXPECTED_ASSET_CLASSES


def test_portfolio_fixture_covers_expected_order_branches():
    cases = _load_cases()

    order_branches = {
        order["expected_branch"]
        for case in cases
        for order in case["request"]["orders"]
    }

    assert EXPECTED_ORDER_BRANCHES.issubset(order_branches)


def test_portfolio_fixture_expected_counts_match_orders():
    cases = _load_cases()

    for case in cases:
        orders = case["request"]["orders"]
        expected = case["expected"]

        asset_counts = Counter(
            _normalize_asset_class(order["raw_order"]["asset_class"])
            for order in orders
        )
        branch_counts = Counter(order["expected_branch"] for order in orders)

        assert dict(sorted(asset_counts.items())) == expected["asset_class_counts"]
        assert dict(sorted(branch_counts.items())) == expected["branch_counts"]

        assert expected["order_count"] == len(orders)
        assert expected["filled_count"] >= 0
        assert expected["sandbox_rejected_count"] >= 0
        assert expected["policy_denied_count"] >= 0
        assert expected["risk_denied_count"] >= 0


def test_portfolio_fixture_specific_case_expectations():
    cases = {case["case_id"]: case for case in _load_cases()}

    all_fill = cases["portfolio_all_fill"]["expected"]
    assert all_fill["ok"] is True
    assert all_fill["portfolio_status"] == "completed"
    assert all_fill["filled_count"] == 4
    assert all_fill["sandbox_rejected_count"] == 0
    assert all_fill["policy_denied_count"] == 0
    assert all_fill["risk_denied_count"] == 0

    mixed = cases["portfolio_mixed_results"]["expected"]
    assert mixed["ok"] is True
    assert mixed["portfolio_status"] == "partial"
    assert mixed["filled_count"] == 1
    assert mixed["sandbox_rejected_count"] == 1
    assert mixed["policy_denied_count"] == 1
    assert mixed["risk_denied_count"] == 1

    policy_deny = cases["portfolio_policy_deny"]["expected"]
    assert policy_deny["ok"] is False
    assert policy_deny["portfolio_status"] == "portfolio_policy_deny"
    assert policy_deny["policy_denied_count"] == 2

    risk_deny = cases["portfolio_risk_deny"]["expected"]
    assert risk_deny["ok"] is False
    assert risk_deny["portfolio_status"] == "portfolio_risk_deny"
    assert risk_deny["risk_denied_count"] == 2
