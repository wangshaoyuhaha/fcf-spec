import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fcf.api.paper_execution_api import handle_paper_execution


API_NAME = "portfolio_paper_execution_api"
API_VERSION = "0.1.0"

PORTFOLIO_POLICY_DENY_FLAGS = [
    "real_execution_requested",
    "real_order_requested",
    "real_order",
    "real_execution",
    "real_exchange_api",
    "place_real_order_requested",
    "connect_exchange_requested",
    "save_api_key_requested",
    "read_private_key_requested",
    "bypass_risk_requested",
    "force_execute_requested",
]


def _stable_response(
    *,
    ok: bool,
    error: Optional[Dict[str, Any]],
    data: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "api": API_NAME,
        "api_version": API_VERSION,
        "error": error,
        "data": data,
    }


def _normalize_asset_class(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().lower()


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def _order_notional(order: Dict[str, Any]) -> Decimal:
    raw_order = order.get("raw_order") or {}
    quantity = _to_decimal(raw_order.get("quantity"))
    price = _to_decimal(raw_order.get("price"))
    return abs(quantity * price)


def _count_assets(orders: List[Dict[str, Any]]) -> Dict[str, int]:
    counter = Counter(
        _normalize_asset_class((order.get("raw_order") or {}).get("asset_class"))
        for order in orders
    )
    return dict(sorted(counter.items()))


def _notional_by_asset_class(orders: List[Dict[str, Any]]) -> Dict[str, float]:
    totals: Dict[str, Decimal] = {}

    for order in orders:
        asset_class = _normalize_asset_class((order.get("raw_order") or {}).get("asset_class"))
        totals[asset_class] = totals.get(asset_class, Decimal("0")) + _order_notional(order)

    return {
        asset_class: float(notional)
        for asset_class, notional in sorted(totals.items())
    }


def _safe_boundary() -> Dict[str, Any]:
    return {
        "execution_mode": "paper",
        "real_order": False,
        "real_execution": False,
        "real_exchange_api": False,
        "real_money_impact": False,
        "no_real_exchange_api": True,
        "no_real_order_placement": True,
        "no_exchange_api_key_storage": True,
        "no_wallet_private_key_access": True,
        "policy_risk_cannot_be_bypassed": True,
        "does_not_claim_real_trade_success": True,
        "sandbox_fill_is_not_real_fill": True,
        "sandbox_reject_is_not_exchange_reject": True,
        "policy_deny_is_not_exchange_reject": True,
        "risk_deny_is_not_exchange_reject": True,
        "portfolio_policy_deny_is_not_exchange_reject": True,
        "portfolio_risk_deny_is_not_exchange_reject": True,
    }


def _validate_portfolio_request(portfolio_request: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(portfolio_request, dict):
        return {
            "type": "PortfolioSchemaError",
            "message": "portfolio_request must be a dict",
        }

    if not isinstance(portfolio_request.get("orders"), list):
        return {
            "type": "PortfolioSchemaError",
            "message": "portfolio_request.orders must be a list",
        }

    if len(portfolio_request.get("orders") or []) == 0:
        return {
            "type": "PortfolioSchemaError",
            "message": "portfolio_request.orders must not be empty",
        }

    return None


def _portfolio_policy_deny_reasons(policy_context: Dict[str, Any]) -> List[str]:
    reasons = []

    for flag in PORTFOLIO_POLICY_DENY_FLAGS:
        if policy_context.get(flag) is True:
            reasons.append(flag)

    return reasons


def _portfolio_risk_deny_reasons(
    orders: List[Dict[str, Any]],
    risk_context: Dict[str, Any],
) -> List[str]:
    reasons: List[str] = []

    max_order_count = risk_context.get("max_order_count")
    if isinstance(max_order_count, int) and len(orders) > max_order_count:
        reasons.append("max_order_count_exceeded")

    blocked_asset_classes = {
        _normalize_asset_class(item)
        for item in risk_context.get("blocked_asset_classes", [])
    }
    order_asset_classes = {
        _normalize_asset_class((order.get("raw_order") or {}).get("asset_class"))
        for order in orders
    }
    if blocked_asset_classes.intersection(order_asset_classes):
        reasons.append("blocked_asset_class")

    blocked_symbols = {
        _normalize_symbol(item)
        for item in risk_context.get("blocked_symbols", [])
    }
    order_symbols = {
        _normalize_symbol((order.get("raw_order") or {}).get("symbol"))
        for order in orders
    }
    if blocked_symbols.intersection(order_symbols):
        reasons.append("blocked_symbol")

    total_notional = sum((_order_notional(order) for order in orders), Decimal("0"))
    max_total_notional = risk_context.get("max_total_notional")
    if max_total_notional is not None and total_notional > _to_decimal(max_total_notional):
        reasons.append("max_total_notional_exceeded")

    max_single_order_notional = risk_context.get("max_single_order_notional")
    if max_single_order_notional is not None:
        max_single_order_notional_decimal = _to_decimal(max_single_order_notional)
        if any(_order_notional(order) > max_single_order_notional_decimal for order in orders):
            reasons.append("max_single_order_notional_exceeded")

    max_asset_class_notional = risk_context.get("max_asset_class_notional") or {}
    if isinstance(max_asset_class_notional, dict):
        notional_by_asset = _notional_by_asset_class(orders)
        for asset_class, notional in notional_by_asset.items():
            limit = max_asset_class_notional.get(asset_class)
            if limit is not None and _to_decimal(notional) > _to_decimal(limit):
                reasons.append("max_asset_class_notional_exceeded")
                break

    max_same_side_count = risk_context.get("max_same_side_count")
    if isinstance(max_same_side_count, int):
        side_counts = Counter(
            str((order.get("raw_order") or {}).get("side") or "").strip().lower()
            for order in orders
        )
        if any(count > max_same_side_count for count in side_counts.values()):
            reasons.append("max_same_side_count_exceeded")

    return reasons


def _blocked_portfolio_data(
    *,
    portfolio_request: Dict[str, Any],
    portfolio_status: str,
    blocked_branch: str,
    policy_denied_count: int,
    risk_denied_count: int,
) -> Dict[str, Any]:
    orders = portfolio_request.get("orders") or {}
    if not isinstance(orders, list):
        orders = []

    results = []
    for order in orders:
        raw_order = order.get("raw_order") or {}
        results.append(
            {
                "order_id": order.get("order_id"),
                "asset_class": _normalize_asset_class(raw_order.get("asset_class")),
                "symbol": _normalize_symbol(raw_order.get("symbol")),
                "expected_branch": order.get("expected_branch"),
                "actual_branch": blocked_branch,
                "ok": False,
                "execution_status": None,
                "error_type": (
                    "PortfolioPolicyDeny"
                    if blocked_branch == "blocked_by_portfolio_policy"
                    else "PortfolioRiskDeny"
                ),
                "sandbox_event_written": False,
                "real_execution": False,
            }
        )

    branch_counts = Counter(result["actual_branch"] for result in results)

    return {
        "portfolio_id": portfolio_request.get("portfolio_id"),
        "correlation_id": portfolio_request.get("correlation_id"),
        "source": portfolio_request.get("source"),
        "execution_mode": "paper",
        "portfolio_status": portfolio_status,
        "order_count": len(orders),
        "filled_count": 0,
        "sandbox_rejected_count": 0,
        "policy_denied_count": policy_denied_count,
        "risk_denied_count": risk_denied_count,
        "asset_class_counts": _count_assets(orders),
        "branch_counts": dict(sorted(branch_counts.items())),
        "total_notional": float(sum((_order_notional(order) for order in orders), Decimal("0"))),
        "notional_by_asset_class": _notional_by_asset_class(orders),
        "results": results,
        "safe_boundary": _safe_boundary(),
    }


def _classify_order_response(response: Dict[str, Any]) -> str:
    if response.get("ok") is True:
        data = response.get("data") or {}
        execution_status = data.get("execution_status")
        if execution_status == "filled":
            return "fill_success"
        if execution_status == "rejected":
            return "sandbox_reject"
        return "unknown_success"

    error = response.get("error") or {}
    error_type = error.get("type")
    if error_type == "PolicyDeny":
        return "policy_deny"
    if error_type == "RiskDeny":
        return "risk_deny"

    return "unknown_error"


def _execute_order(
    *,
    order: Dict[str, Any],
    output_root: Path,
) -> Dict[str, Any]:
    output_path = output_root / f"{order.get('order_id', 'order')}.jsonl"

    response = handle_paper_execution(
        raw_order=order.get("raw_order"),
        simulation_mode=order.get("simulation_mode", "simulated_fill"),
        fill_price=order.get("fill_price"),
        filled_quantity=order.get("filled_quantity"),
        reject_reason=order.get("reject_reason"),
        output_path=str(output_path),
        policy_context=order.get("policy_context"),
        risk_context=order.get("risk_context"),
    )

    raw_order = order.get("raw_order") or {}
    data = response.get("data") or {}
    error = response.get("error") or {}
    actual_branch = _classify_order_response(response)

    return {
        "order_id": order.get("order_id"),
        "asset_class": _normalize_asset_class(raw_order.get("asset_class")),
        "symbol": _normalize_symbol(raw_order.get("symbol")),
        "expected_branch": order.get("expected_branch"),
        "actual_branch": actual_branch,
        "ok": response.get("ok"),
        "execution_status": data.get("execution_status"),
        "error_type": error.get("type"),
        "sandbox_event_written": output_path.exists(),
        "real_execution": data.get("real_execution", False) is True,
    }


def _summarize_order_results(
    *,
    portfolio_request: Dict[str, Any],
    results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    branch_counts = Counter(result["actual_branch"] for result in results)

    filled_count = branch_counts.get("fill_success", 0)
    sandbox_rejected_count = branch_counts.get("sandbox_reject", 0)
    policy_denied_count = branch_counts.get("policy_deny", 0)
    risk_denied_count = branch_counts.get("risk_deny", 0)

    portfolio_status = "completed"
    if sandbox_rejected_count or policy_denied_count or risk_denied_count:
        portfolio_status = "partial"

    orders = portfolio_request.get("orders") or []

    return {
        "portfolio_id": portfolio_request.get("portfolio_id"),
        "correlation_id": portfolio_request.get("correlation_id"),
        "source": portfolio_request.get("source"),
        "execution_mode": "paper",
        "portfolio_status": portfolio_status,
        "order_count": len(orders),
        "filled_count": filled_count,
        "sandbox_rejected_count": sandbox_rejected_count,
        "policy_denied_count": policy_denied_count,
        "risk_denied_count": risk_denied_count,
        "asset_class_counts": _count_assets(orders),
        "branch_counts": dict(sorted(branch_counts.items())),
        "total_notional": float(sum((_order_notional(order) for order in orders), Decimal("0"))),
        "notional_by_asset_class": _notional_by_asset_class(orders),
        "results": results,
        "safe_boundary": _safe_boundary(),
    }


def _handle_with_output_root(
    portfolio_request: Dict[str, Any],
    output_root: Path,
) -> Dict[str, Any]:
    schema_error = _validate_portfolio_request(portfolio_request)
    if schema_error is not None:
        return _stable_response(ok=False, error=schema_error, data=None)

    orders = portfolio_request["orders"]

    policy_context = portfolio_request.get("portfolio_policy_context") or {}
    policy_deny_reasons = _portfolio_policy_deny_reasons(policy_context)
    if policy_deny_reasons:
        data = _blocked_portfolio_data(
            portfolio_request=portfolio_request,
            portfolio_status="portfolio_policy_deny",
            blocked_branch="blocked_by_portfolio_policy",
            policy_denied_count=len(orders),
            risk_denied_count=0,
        )
        return _stable_response(
            ok=False,
            error={
                "type": "PortfolioPolicyDeny",
                "message": "portfolio policy denied paper execution",
                "deny_reasons": policy_deny_reasons,
                "not_exchange_reject": True,
            },
            data=data,
        )

    risk_context = portfolio_request.get("portfolio_risk_context") or {}
    risk_deny_reasons = _portfolio_risk_deny_reasons(orders, risk_context)
    if risk_deny_reasons:
        data = _blocked_portfolio_data(
            portfolio_request=portfolio_request,
            portfolio_status="portfolio_risk_deny",
            blocked_branch="blocked_by_portfolio_risk",
            policy_denied_count=0,
            risk_denied_count=len(orders),
        )
        return _stable_response(
            ok=False,
            error={
                "type": "PortfolioRiskDeny",
                "message": "portfolio risk denied paper execution",
                "deny_reasons": risk_deny_reasons,
                "not_exchange_reject": True,
            },
            data=data,
        )

    results = [
        _execute_order(order=order, output_root=output_root)
        for order in orders
    ]

    data = _summarize_order_results(
        portfolio_request=portfolio_request,
        results=results,
    )

    return _stable_response(ok=True, error=None, data=data)


def handle_portfolio_paper_execution(
    portfolio_request: Dict[str, Any],
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    if output_dir is None:
        with tempfile.TemporaryDirectory(prefix="fcf_p8_portfolio_") as tmp_dir:
            return _handle_with_output_root(
                portfolio_request=portfolio_request,
                output_root=Path(tmp_dir),
            )

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    return _handle_with_output_root(
        portfolio_request=portfolio_request,
        output_root=output_root,
    )
