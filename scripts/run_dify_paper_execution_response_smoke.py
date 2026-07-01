import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fcf.api.dify_paper_execution_adapter import (
    ROUTE_EXECUTE,
    route_dify_paper_execution_request,
)
from fcf.api.paper_execution_response_templates import (
    render_paper_execution_user_response,
)

RUNNER_NAME = "dify_paper_execution_response_smoke"


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
        "source": "dify_paper_execution_response_smoke",
        "correlation_id": "p6-d10-dify-paper-execution-response-smoke",
        "metadata": {
            "note": "paper only response smoke",
        },
    }


def _safe_risk_context() -> Dict[str, Any]:
    return {
        "max_quantity": 1.0,
        "max_notional": 100000.0,
        "allow_leverage": False,
        "allow_margin": False,
        "duplicate_order_keys": [],
        "blocked_symbols": [],
        "blocked_asset_classes": [],
        "high_risk_flags": [],
    }


def _call_execute(body: Dict[str, Any]) -> Dict[str, Any]:
    return route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        body,
    )


def _summarize_case(
    name: str,
    adapter_response: Optional[Dict[str, Any]],
    user_response: Dict[str, Any],
) -> Dict[str, Any]:
    body = {}
    error = {}
    if adapter_response is not None:
        body = adapter_response.get("body", {})
        error = body.get("error") or {}

    safety_notice = user_response.get("safety_notice", "")
    fields = user_response.get("fields") or {}

    return {
        "name": name,
        "adapter_http_status": None if adapter_response is None else adapter_response.get("http_status"),
        "adapter_ok": body.get("ok"),
        "adapter_api": body.get("api"),
        "adapter_error_type": error.get("type"),
        "user_response_type": user_response.get("response_type"),
        "user_title": user_response.get("title"),
        "user_error_type": fields.get("error_type"),
        "policy_denied": fields.get("policy_denied"),
        "risk_denied": fields.get("risk_denied"),
        "not_exchange_reject": fields.get("not_exchange_reject"),
        "user_safety_notice_present": "没有真实下单" in safety_notice,
    }


def run_dify_paper_execution_response_smoke() -> Dict[str, Any]:
    fill_adapter_response = _call_execute(
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "risk_context": _safe_risk_context(),
        }
    )
    fill_user_response = render_paper_execution_user_response(fill_adapter_response)

    reject_adapter_response = _call_execute(
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_reject",
            "reject_reason": "policy and risk allowed then sandbox reject in response smoke",
            "risk_context": _safe_risk_context(),
        }
    )
    reject_user_response = render_paper_execution_user_response(reject_adapter_response)

    policy_deny_adapter_response = _call_execute(
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "bypass_risk_requested": True,
            "risk_context": _safe_risk_context(),
        }
    )
    policy_deny_user_response = render_paper_execution_user_response(
        policy_deny_adapter_response
    )

    risk_context = _safe_risk_context()
    risk_context["max_quantity"] = 0.1
    risk_deny_adapter_response = _call_execute(
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "risk_context": risk_context,
        }
    )
    risk_deny_user_response = render_paper_execution_user_response(
        risk_deny_adapter_response
    )

    bad_order = _sample_paper_order()
    bad_order["quantity"] = "-1"
    error_adapter_response = _call_execute(
        {
            "raw_order": bad_order,
            "simulation_mode": "simulated_fill",
            "risk_context": _safe_risk_context(),
        }
    )
    error_user_response = render_paper_execution_user_response(error_adapter_response)

    safety_user_response = render_paper_execution_user_response(intent="real_execution")

    cases = [
        _summarize_case(
            "fill_to_user_paper_fill_success",
            fill_adapter_response,
            fill_user_response,
        ),
        _summarize_case(
            "reject_to_user_paper_reject_success",
            reject_adapter_response,
            reject_user_response,
        ),
        _summarize_case(
            "policy_deny_to_user_paper_policy_deny",
            policy_deny_adapter_response,
            policy_deny_user_response,
        ),
        _summarize_case(
            "risk_deny_to_user_paper_risk_deny",
            risk_deny_adapter_response,
            risk_deny_user_response,
        ),
        _summarize_case(
            "bad_order_to_user_paper_execution_error",
            error_adapter_response,
            error_user_response,
        ),
        _summarize_case(
            "real_execution_intent_to_safety_refusal",
            None,
            safety_user_response,
        ),
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
            "only_renders_paper_user_responses": True,
            "does_not_claim_real_trade_success": True,
            "does_not_claim_policy_deny_as_exchange_reject": True,
            "does_not_claim_risk_deny_as_exchange_reject": True,
        },
    }


def main() -> None:
    print(json.dumps(run_dify_paper_execution_response_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
