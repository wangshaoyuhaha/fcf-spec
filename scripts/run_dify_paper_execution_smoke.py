import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_paper_execution_adapter import (
    ROUTE_CONTRACT,
    ROUTE_EXECUTE,
    route_dify_paper_execution_request,
)

RUNNER_NAME = "dify_paper_execution_smoke"


def _sample_paper_order() -> Dict[str, Any]:
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "PERP",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": "0.25",
        "price": "60050.5",
        "time_in_force": "gtc",
        "source": "dify_paper_execution_smoke",
        "correlation_id": "p5-d8-dify-paper-execution-smoke",
        "metadata": {
            "note": "paper only smoke",
        },
        "real_order": True,
        "real_exchange_api": True,
        "real_money_impact": True,
    }


def _case_summary(name: str, response: Dict[str, Any]) -> Dict[str, Any]:
    body = response.get("body", {})
    data = body.get("data") or {}
    error = body.get("error") or {}

    return {
        "name": name,
        "http_status": response.get("http_status"),
        "ok": body.get("ok"),
        "api": body.get("api"),
        "error_type": error.get("type"),
        "error_message": error.get("message"),
        "execution_status": data.get("execution_status"),
        "event_name": data.get("event_name"),
        "event_count": data.get("event_count"),
        "replay_status": (data.get("replay") or {}).get("status"),
        "real_order": data.get("real_order"),
        "real_execution": data.get("real_execution"),
        "real_exchange_api": data.get("real_exchange_api"),
        "real_money_impact": data.get("real_money_impact"),
        "user_visible_safety": (
            "paper/sandbox only; no real exchange API; no real order placement"
        ),
    }


def run_dify_paper_execution_smoke() -> Dict[str, Any]:
    contract_response = route_dify_paper_execution_request(
        "GET",
        ROUTE_CONTRACT,
    )

    fill_response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
        },
    )

    reject_response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_reject",
            "reject_reason": "policy denied in smoke",
        },
    )

    bad_order = _sample_paper_order()
    bad_order["quantity"] = "-1"

    bad_order_response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": bad_order,
            "simulation_mode": "simulated_fill",
        },
    )

    bad_mode_response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "real_execution",
        },
    )

    missing_raw_order_response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "simulation_mode": "simulated_fill",
        },
    )

    cases: List[Dict[str, Any]] = [
        _case_summary("contract", contract_response),
        _case_summary("simulated_fill", fill_response),
        _case_summary("simulated_reject", reject_response),
        _case_summary("bad_order_error", bad_order_response),
        _case_summary("bad_simulation_mode_error", bad_mode_response),
        _case_summary("missing_raw_order_error", missing_raw_order_response),
    ]

    return {
        "status": "completed",
        "runner": RUNNER_NAME,
        "case_count": len(cases),
        "cases": cases,
        "safe_boundary": {
            "execution_mode": "paper",
            "real_order": False,
            "real_execution": False,
            "real_exchange_api": False,
            "real_money_impact": False,
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_secret_storage": True,
            "only_calls_dify_paper_execution_adapter": True,
            "does_not_claim_real_trade_success": True,
        },
    }


def main() -> None:
    print(json.dumps(run_dify_paper_execution_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
