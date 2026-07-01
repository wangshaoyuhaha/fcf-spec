import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_http_adapter import ROUTE_BATCH, route_dify_http_request
from fcf.api.dify_response_templates import render_dify_user_response

RUNNER_NAME = "multi_asset_error_dify_smoke"
FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "raw_market_data_multi_asset.json"


def load_multi_asset_fixture() -> List[Dict[str, Any]]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _call_batch(rows: List[Dict[str, Any]], case_name: str) -> Dict[str, Any]:
    return route_dify_http_request(
        "POST",
        ROUTE_BATCH,
        {
            "correlation_id": f"p4-d11-{case_name}",
            "rows": rows,
        },
    )


def _case_summary(
    name: str,
    rows: List[Dict[str, Any]],
    expected_text: str,
) -> Dict[str, Any]:
    adapter_response = _call_batch(rows, name)
    body = adapter_response.get("body", {})
    error = body.get("error") or {}
    user_response = render_dify_user_response(adapter_response)

    return {
        "name": name,
        "expected_text": expected_text,
        "adapter_http_status": adapter_response.get("http_status"),
        "adapter_ok": body.get("ok"),
        "adapter_error_type": error.get("type"),
        "adapter_error_message": error.get("message"),
        "user_response_type": user_response.get("response_type"),
        "user_title": user_response.get("title"),
        "user_error_type": user_response.get("fields", {}).get("error_type"),
        "user_error_message": user_response.get("fields", {}).get("error_message"),
    }


def _mutate_equities_bad_market_type(rows: List[Dict[str, Any]]) -> None:
    rows[1]["market_type"] = "not-real"


def _mutate_fx_bad_spread(rows: List[Dict[str, Any]]) -> None:
    rows[2]["best_bid"] = "1.0810"
    rows[2]["best_ask"] = "1.0800"


def _mutate_commodities_missing_last_price(rows: List[Dict[str, Any]]) -> None:
    del rows[3]["last_price"]


def _build_error_case(
    name: str,
    mutator: Callable[[List[Dict[str, Any]]], None],
    expected_text: str,
) -> Dict[str, Any]:
    rows = copy.deepcopy(load_multi_asset_fixture())
    mutator(rows)
    return _case_summary(
        name=name,
        rows=rows,
        expected_text=expected_text,
    )


def run_multi_asset_error_dify_smoke() -> Dict[str, Any]:
    cases = [
        _build_error_case(
            name="equities_bad_market_type",
            mutator=_mutate_equities_bad_market_type,
            expected_text="market_type",
        ),
        _build_error_case(
            name="fx_bad_spread",
            mutator=_mutate_fx_bad_spread,
            expected_text="best_bid",
        ),
        _build_error_case(
            name="commodities_missing_last_price",
            mutator=_mutate_commodities_missing_last_price,
            expected_text="last_price",
        ),
    ]

    return {
        "status": "completed",
        "runner": RUNNER_NAME,
        "fixture_path": FIXTURE_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "case_count": len(cases),
        "cases": cases,
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_exchange_api_key_storage": True,
            "only_calls_controlled_wrappers": True,
            "does_not_claim_real_trade_success": True,
        },
    }


def main() -> None:
    print(json.dumps(run_multi_asset_error_dify_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
