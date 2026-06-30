from typing import Any, Dict, Optional

from fcf.api.local_market_input_api import (
    describe_api_contract,
    handle_batch_market_input,
    handle_single_market_input,
)

API_NAME = "dify_http_adapter"
API_VERSION = "0.1.0"

ROUTE_CONTRACT = "/api/v1/contract"
ROUTE_SINGLE = "/api/v1/market-input/single"
ROUTE_BATCH = "/api/v1/market-input/batch"

SUPPORTED_ROUTES = {
    "GET /api/v1/contract": "describe_api_contract",
    "POST /api/v1/market-input/single": "handle_single_market_input",
    "POST /api/v1/market-input/batch": "handle_batch_market_input",
}


def _http_response(http_status: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "http_status": http_status,
        "headers": {
            "content-type": "application/json",
        },
        "body": body,
    }


def _adapter_error(http_status: int, error_type: str, message: str) -> Dict[str, Any]:
    return _http_response(
        http_status=http_status,
        body={
            "ok": False,
            "api": API_NAME,
            "api_version": API_VERSION,
            "error": {
                "type": error_type,
                "message": message,
            },
            "data": None,
        },
    )


def describe_routes() -> Dict[str, Any]:
    return {
        "api": API_NAME,
        "api_version": API_VERSION,
        "routes": SUPPORTED_ROUTES,
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_exchange_api_key_storage": True,
            "only_calls_controlled_wrappers": True,
        },
    }


def _is_known_path(path: str) -> bool:
    return path in {
        ROUTE_CONTRACT,
        ROUTE_SINGLE,
        ROUTE_BATCH,
    }


def _require_body_object(body: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None
    return body


def route_dify_http_request(
    method: str,
    path: str,
    body: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    method = method.upper().strip()
    path = path.strip()

    if not _is_known_path(path):
        return _adapter_error(404, "NotFound", "route not found")

    if path == ROUTE_CONTRACT:
        if method != "GET":
            return _adapter_error(405, "MethodNotAllowed", "method not allowed")
        return _http_response(
            200,
            {
                "ok": True,
                "api": API_NAME,
                "api_version": API_VERSION,
                "error": None,
                "data": describe_api_contract(),
            },
        )

    if method != "POST":
        return _adapter_error(405, "MethodNotAllowed", "method not allowed")

    body_object = _require_body_object(body)
    if body_object is None:
        return _adapter_error(400, "BadRequest", "body must be provided as object")

    correlation_id = body_object.get("correlation_id")
    output_path = body_object.get("output_path")

    if not isinstance(correlation_id, str) or not correlation_id.strip():
        return _adapter_error(400, "BadRequest", "correlation_id must be provided as string")

    if path == ROUTE_SINGLE:
        raw = body_object.get("raw")
        if not isinstance(raw, dict):
            return _adapter_error(400, "BadRequest", "raw must be provided as object")
        wrapper_response = handle_single_market_input(
            raw=raw,
            correlation_id=correlation_id,
            output_path=output_path,
        )
        return _http_response(200 if wrapper_response["ok"] else 422, wrapper_response)

    if path == ROUTE_BATCH:
        rows = body_object.get("rows")
        if not isinstance(rows, list):
            return _adapter_error(400, "BadRequest", "rows must be provided as list")
        wrapper_response = handle_batch_market_input(
            rows=rows,
            correlation_id=correlation_id,
            output_path=output_path,
        )
        return _http_response(200 if wrapper_response["ok"] else 422, wrapper_response)

    return _adapter_error(404, "NotFound", "route not found")
