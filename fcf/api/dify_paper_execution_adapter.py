from typing import Any, Dict, Optional

from fcf.api.paper_execution_api import (
    describe_paper_execution_api,
    handle_paper_execution,
)

API_NAME = "dify_paper_execution_adapter"
API_VERSION = "0.1.0"

ROUTE_CONTRACT = "/api/v1/paper-execution/contract"
ROUTE_EXECUTE = "/api/v1/paper-execution/execute"

SUPPORTED_ROUTES = {
    "GET /api/v1/paper-execution/contract": "describe_paper_execution_api",
    "POST /api/v1/paper-execution/execute": "handle_paper_execution",
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
        "paper_execution_contract": describe_paper_execution_api(),
        "safe_boundary": {
            "execution_mode": "paper",
            "real_order": False,
            "real_execution": False,
            "real_exchange_api": False,
            "real_money_impact": False,
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_secret_storage": True,
            "only_calls_paper_execution_api": True,
        },
    }


def _is_known_path(path: str) -> bool:
    return path in {
        ROUTE_CONTRACT,
        ROUTE_EXECUTE,
    }


def _require_body_object(body: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not isinstance(body, dict):
        return None
    return body


def route_dify_paper_execution_request(
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
                "data": describe_routes(),
            },
        )

    if method != "POST":
        return _adapter_error(405, "MethodNotAllowed", "method not allowed")

    body_object = _require_body_object(body)
    if body_object is None:
        return _adapter_error(400, "BadRequest", "body must be provided as object")

    raw_order = body_object.get("raw_order")
    if not isinstance(raw_order, dict):
        return _adapter_error(400, "BadRequest", "raw_order must be provided as object")

    paper_response = handle_paper_execution(
        raw_order=raw_order,
        simulation_mode=body_object.get("simulation_mode", "simulated_fill"),
        fill_price=body_object.get("fill_price"),
        filled_quantity=body_object.get("filled_quantity"),
        reject_reason=body_object.get("reject_reason"),
        output_path=body_object.get("output_path"),
        policy_context=body_object,
    )

    return _http_response(
        200 if paper_response["ok"] else 422,
        paper_response,
    )
