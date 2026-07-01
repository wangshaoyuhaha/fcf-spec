from typing import Any, Dict, Optional

from fcf.policy.paper_execution_policy import evaluate_paper_execution_policy
from fcf.risk.paper_execution_risk_guardian import evaluate_paper_execution_risk
from fcf.paper.sandbox_execution_engine import (
    MODE_SIMULATED_FILL,
    MODE_SIMULATED_REJECT,
    execute_sandbox_order_with_eventstore,
)

API_NAME = "paper_execution_api"
API_VERSION = "0.1.0"


def _stable_response(
    ok: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "api": API_NAME,
        "api_version": API_VERSION,
        "error": error,
        "data": data,
    }


def describe_paper_execution_api() -> Dict[str, Any]:
    return {
        "api": API_NAME,
        "api_version": API_VERSION,
        "supported_handlers": [
            "handle_paper_execution",
        ],
        "supported_simulation_modes": [
            MODE_SIMULATED_FILL,
            MODE_SIMULATED_REJECT,
        ],
        "stable_response_fields": [
            "ok",
            "api",
            "api_version",
            "error",
            "data",
        ],
        "safe_boundary": {
            "execution_mode": "paper",
            "real_order": False,
            "real_execution": False,
            "real_exchange_api": False,
            "real_money_impact": False,
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_secret_storage": True,
            "only_calls_sandbox_execution_engine": True,
        },
    }


def handle_paper_execution(
    raw_order: Dict[str, Any],
    simulation_mode: str = MODE_SIMULATED_FILL,
    fill_price: Optional[float] = None,
    filled_quantity: Optional[float] = None,
    reject_reason: Optional[str] = None,
    output_path: Optional[str] = None,
    policy_context: Optional[Dict[str, Any]] = None,
    risk_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    policy_request: Dict[str, Any] = {
        "raw_order": raw_order,
        "simulation_mode": simulation_mode,
    }
    if isinstance(policy_context, dict):
        policy_request.update(policy_context)
        policy_request["raw_order"] = raw_order

    policy_decision = evaluate_paper_execution_policy(policy_request)
    if policy_decision["ok"] is not True:
        return _stable_response(
            ok=False,
            data=None,
            error=policy_decision["error"],
        )

    risk_request: Dict[str, Any] = {
        "raw_order": raw_order,
    }
    if isinstance(policy_context, dict):
        risk_request.update(policy_context)
        risk_request["raw_order"] = raw_order

    if isinstance(risk_context, dict):
        risk_request["risk_context"] = risk_context
    elif "risk_context" not in risk_request:
        risk_request["allow_missing_risk_context"] = True

    risk_decision = evaluate_paper_execution_risk(risk_request)
    if risk_decision["ok"] is not True:
        return _stable_response(
            ok=False,
            data=None,
            error=risk_decision["error"],
        )

    engine_response = execute_sandbox_order_with_eventstore(
        raw_order=raw_order,
        simulation_mode=simulation_mode,
        fill_price=fill_price,
        filled_quantity=filled_quantity,
        reject_reason=reject_reason,
        output_path=output_path,
    )

    if engine_response["ok"] is True:
        return _stable_response(
            ok=True,
            data=engine_response["data"],
            error=None,
        )

    return _stable_response(
        ok=False,
        data=None,
        error=engine_response["error"],
    )
