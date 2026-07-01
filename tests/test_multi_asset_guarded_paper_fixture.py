import json
from pathlib import Path

import pytest

from fcf.api.paper_execution_api import handle_paper_execution


FIXTURE_PATH = Path("fixtures/paper_orders_multi_asset_guarded.json")

EXPECTED_ASSET_CLASSES = {
    "crypto",
    "equities",
    "fx",
    "commodities",
}

EXPECTED_BRANCHES = {
    "fill_success",
    "sandbox_reject",
    "policy_deny",
    "risk_deny",
}

REQUIRED_CASE_FIELDS = {
    "case_id",
    "asset_class",
    "branch",
    "description",
    "request",
    "expected",
}

REQUIRED_RAW_ORDER_FIELDS = {
    "asset_class",
    "symbol",
    "venue",
    "market_type",
    "side",
    "order_type",
    "quantity",
    "source",
    "correlation_id",
}

REQUIRED_EXPECTED_FIELDS = {
    "ok",
    "execution_status",
    "error_type",
    "sandbox_event_expected",
    "real_execution",
}


def _load_cases():
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _case_ids():
    return [case["case_id"] for case in _load_cases()]


def test_fixture_file_exists_and_is_list():
    assert FIXTURE_PATH.exists()

    cases = _load_cases()

    assert isinstance(cases, list)
    assert len(cases) == 16


def test_fixture_schema_has_required_fields():
    cases = _load_cases()

    for case in cases:
        assert REQUIRED_CASE_FIELDS.issubset(case.keys())

        request = case["request"]
        expected = case["expected"]
        raw_order = request["raw_order"]

        assert isinstance(case["case_id"], str)
        assert case["asset_class"] in EXPECTED_ASSET_CLASSES
        assert case["branch"] in EXPECTED_BRANCHES
        assert isinstance(case["description"], str)
        assert isinstance(request, dict)
        assert isinstance(expected, dict)
        assert isinstance(raw_order, dict)

        assert REQUIRED_RAW_ORDER_FIELDS.issubset(raw_order.keys())
        assert REQUIRED_EXPECTED_FIELDS.issubset(expected.keys())

        assert request["simulation_mode"] in {
            "simulated_fill",
            "simulated_reject",
        }

        assert "risk_context" in request
        assert isinstance(request["risk_context"], dict)

        assert raw_order["source"] == "p7_d2_multi_asset_guarded_fixture"
        assert raw_order.get("real_order") is not True
        assert raw_order.get("real_execution") is not True
        assert raw_order.get("real_exchange_api") is not True

        assert expected["real_execution"] is False


def test_fixture_covers_every_asset_class_and_branch_pair():
    cases = _load_cases()

    actual_pairs = {
        (case["asset_class"], case["branch"])
        for case in cases
    }

    expected_pairs = {
        (asset_class, branch)
        for asset_class in EXPECTED_ASSET_CLASSES
        for branch in EXPECTED_BRANCHES
    }

    assert actual_pairs == expected_pairs


def test_fixture_case_ids_are_unique():
    cases = _load_cases()
    case_ids = [case["case_id"] for case in cases]

    assert len(case_ids) == len(set(case_ids))


@pytest.mark.parametrize("case_id", _case_ids())
def test_guarded_paper_execution_fixture_case(case_id, tmp_path):
    cases = {
        case["case_id"]: case
        for case in _load_cases()
    }
    case = cases[case_id]

    request = case["request"]
    expected = case["expected"]

    output_path = tmp_path / f"{case_id}.jsonl"

    response = handle_paper_execution(
        raw_order=request["raw_order"],
        simulation_mode=request.get("simulation_mode", "simulated_fill"),
        fill_price=request.get("fill_price"),
        filled_quantity=request.get("filled_quantity"),
        reject_reason=request.get("reject_reason"),
        output_path=str(output_path),
        policy_context=request.get("policy_context"),
        risk_context=request.get("risk_context"),
    )

    assert response["ok"] is expected["ok"]
    assert response["api"] == "paper_execution_api"
    assert response["api_version"] == "0.1.0"

    if expected["ok"] is True:
        data = response["data"]

        assert response["error"] is None
        assert data["execution_status"] == expected["execution_status"]
        assert data["asset_class"] == case["asset_class"]
        assert data["event_count"] == 1
        assert data["persisted"] is True
        assert data["output_path"] == str(output_path)
        assert data["real_order"] is False
        assert data["real_execution"] is False
        assert data["real_exchange_api"] is False
        assert data["real_money_impact"] is False
        assert output_path.exists()

        if expected["execution_status"] == "filled":
            assert data["event_name"] == "fcf.sandbox.execution.filled"
            assert data["filled_quantity"] == data["requested_quantity"]
            assert data["remaining_quantity"] == 0.0

        if expected["execution_status"] == "rejected":
            assert data["event_name"] == "fcf.sandbox.execution.rejected"
            assert data["filled_quantity"] == 0.0
            assert "sandbox reject" in data["reject_reason"]

    else:
        assert response["data"] is None
        assert response["error"]["type"] == expected["error_type"]
        assert not output_path.exists()

        if expected["error_type"] == "PolicyDeny":
            assert case["branch"] == "policy_deny"

        if expected["error_type"] == "RiskDeny":
            assert case["branch"] == "risk_deny"
            assert "blocked" in response["error"]["message"]
