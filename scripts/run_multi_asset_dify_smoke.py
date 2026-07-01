import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_http_adapter import ROUTE_BATCH, route_dify_http_request
from fcf.api.dify_response_templates import render_dify_user_response

RUNNER_NAME = "multi_asset_dify_response_smoke"
FIXTURE_PATH = PROJECT_ROOT / "fixtures" / "raw_market_data_multi_asset.json"


def load_multi_asset_fixture() -> List[Dict[str, Any]]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_multi_asset_dify_smoke() -> Dict[str, Any]:
    rows = load_multi_asset_fixture()

    adapter_response = route_dify_http_request(
        "POST",
        ROUTE_BATCH,
        {
            "correlation_id": "p4-d10-multi-asset-dify-smoke",
            "rows": rows,
        },
    )

    body = adapter_response.get("body", {})
    data = body.get("data") or {}

    user_response = render_dify_user_response(adapter_response)

    return {
        "status": "completed",
        "runner": RUNNER_NAME,
        "fixture_path": FIXTURE_PATH.relative_to(PROJECT_ROOT).as_posix(),
        "asset_classes": data.get("asset_classes", []),
        "symbols": data.get("symbols", []),
        "market_types": data.get("market_types", []),
        "adapter_http_status": adapter_response.get("http_status"),
        "adapter_ok": body.get("ok"),
        "event_count": data.get("event_count"),
        "replay_status": (data.get("replay") or {}).get("status"),
        "replay_event_count": (data.get("replay") or {}).get("event_count"),
        "user_response_type": user_response.get("response_type"),
        "user_title": user_response.get("title"),
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_exchange_api_key_storage": True,
            "only_calls_controlled_wrappers": True,
            "does_not_claim_real_trade_success": True,
        },
    }


def main() -> None:
    print(json.dumps(run_multi_asset_dify_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
