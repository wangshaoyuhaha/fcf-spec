from typing import Any, Dict, Optional

from fcf.contracts.event import create_event
from fcf.core.event_store import EventStore
from fcf.replay.replay_engine import ReplayEngine

from fcf.paper.paper_order_schema import normalize_paper_order

ENGINE_NAME = "sandbox_execution_engine"
ENGINE_VERSION = "0.1.0"

MODE_SIMULATED_FILL = "simulated_fill"
MODE_SIMULATED_REJECT = "simulated_reject"

SUPPORTED_SIMULATION_MODES = {
    MODE_SIMULATED_FILL,
    MODE_SIMULATED_REJECT,
}

EVENT_SANDBOX_FILLED = "fcf.sandbox.execution.filled"
EVENT_SANDBOX_PARTIAL_FILLED = "fcf.sandbox.execution.partial_filled"
EVENT_SANDBOX_REJECTED = "fcf.sandbox.execution.rejected"


def describe_sandbox_execution_engine() -> Dict[str, Any]:
    return {
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "supported_simulation_modes": sorted(SUPPORTED_SIMULATION_MODES),
        "event_names": [
            EVENT_SANDBOX_FILLED,
            EVENT_SANDBOX_PARTIAL_FILLED,
            EVENT_SANDBOX_REJECTED,
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
        },
    }


def _stable_response(
    ok: bool,
    data: Optional[Dict[str, Any]] = None,
    error: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    return {
        "ok": ok,
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "error": error,
        "data": data,
    }


def _error_response(error: Exception) -> Dict[str, Any]:
    return _stable_response(
        ok=False,
        data=None,
        error={
            "type": error.__class__.__name__,
            "message": str(error),
        },
    )


def _require_positive_number(value: Optional[float], field: str) -> float:
    if value is None:
        raise ValueError(f"{field} must be a valid number")
    try:
        converted = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field} must be a valid number") from error
    if converted <= 0:
        raise ValueError(f"{field} must be greater than 0")
    return converted


def _normalize_simulation_mode(simulation_mode: str) -> str:
    if not isinstance(simulation_mode, str) or not simulation_mode.strip():
        raise ValueError("simulation_mode must be provided as non-empty string")

    normalized = simulation_mode.strip().lower()
    if normalized not in SUPPORTED_SIMULATION_MODES:
        raise ValueError(f"simulation_mode is not supported: {simulation_mode}")

    return normalized


def _base_execution_data(
    paper_order: Dict[str, Any],
    simulation_mode: str,
) -> Dict[str, Any]:
    return {
        "status": "completed",
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "simulation_mode": simulation_mode,
        "execution_mode": "paper",
        "real_order": False,
        "real_execution": False,
        "real_exchange_api": False,
        "real_money_impact": False,
        "correlation_id": paper_order["correlation_id"],
        "asset_class": paper_order["asset_class"],
        "symbol": paper_order["symbol"],
        "venue": paper_order["venue"],
        "market_type": paper_order["market_type"],
        "side": paper_order["side"],
        "order_type": paper_order["order_type"],
        "requested_quantity": paper_order["quantity"],
        "source": paper_order["source"],
        "paper_order": paper_order,
    }


def _simulate_fill(
    paper_order: Dict[str, Any],
    fill_price: Optional[float] = None,
    filled_quantity: Optional[float] = None,
) -> Dict[str, Any]:
    requested_quantity = paper_order["quantity"]

    if filled_quantity is None:
        normalized_filled_quantity = requested_quantity
    else:
        normalized_filled_quantity = _require_positive_number(
            filled_quantity,
            "filled_quantity",
        )

    if normalized_filled_quantity > requested_quantity:
        raise ValueError("filled_quantity must be less than or equal to requested quantity")

    if fill_price is None:
        if "price" not in paper_order:
            raise ValueError("fill_price must be provided when paper order has no price")
        normalized_fill_price = _require_positive_number(paper_order["price"], "fill_price")
    else:
        normalized_fill_price = _require_positive_number(fill_price, "fill_price")

    remaining_quantity = requested_quantity - normalized_filled_quantity

    execution_status = "filled"
    event_name = EVENT_SANDBOX_FILLED
    if remaining_quantity > 0:
        execution_status = "partial_filled"
        event_name = EVENT_SANDBOX_PARTIAL_FILLED

    data = _base_execution_data(
        paper_order=paper_order,
        simulation_mode=MODE_SIMULATED_FILL,
    )
    data.update(
        {
            "execution_status": execution_status,
            "event_name": event_name,
            "filled_quantity": normalized_filled_quantity,
            "remaining_quantity": remaining_quantity,
            "fill_price": normalized_fill_price,
            "notional": normalized_filled_quantity * normalized_fill_price,
            "message": "sandbox execution simulated fill; no real order was placed",
        }
    )
    return data


def _simulate_reject(
    paper_order: Dict[str, Any],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    reject_reason = reason or "sandbox rejection"

    data = _base_execution_data(
        paper_order=paper_order,
        simulation_mode=MODE_SIMULATED_REJECT,
    )
    data.update(
        {
            "execution_status": "rejected",
            "event_name": EVENT_SANDBOX_REJECTED,
            "filled_quantity": 0.0,
            "remaining_quantity": paper_order["quantity"],
            "fill_price": None,
            "notional": 0.0,
            "reject_reason": reject_reason,
            "message": "sandbox execution simulated reject; no real order was placed",
        }
    )
    return data


def execute_sandbox_order(
    raw_order: Dict[str, Any],
    simulation_mode: str = MODE_SIMULATED_FILL,
    fill_price: Optional[float] = None,
    filled_quantity: Optional[float] = None,
    reject_reason: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        mode = _normalize_simulation_mode(simulation_mode)
        paper_order = normalize_paper_order(raw_order)

        if mode == MODE_SIMULATED_FILL:
            data = _simulate_fill(
                paper_order=paper_order,
                fill_price=fill_price,
                filled_quantity=filled_quantity,
            )
        elif mode == MODE_SIMULATED_REJECT:
            data = _simulate_reject(
                paper_order=paper_order,
                reason=reject_reason,
            )
        else:
            raise ValueError(f"simulation_mode is not supported: {simulation_mode}")

        return _stable_response(
            ok=True,
            data=data,
            error=None,
        )
    except Exception as error:
        return _error_response(error)


def _build_sandbox_execution_event(execution_data: Dict[str, Any]) -> Any:
    return create_event(
        event_name=execution_data["event_name"],
        source_module=ENGINE_NAME,
        correlation_id=execution_data["correlation_id"],
        payload={
            "sandbox_execution": execution_data,
        },
        metadata={
            "execution_mode": "paper",
            "real_order": False,
            "real_execution": False,
            "real_exchange_api": False,
            "real_money_impact": False,
        },
    )


def _persist_execution_store_if_needed(
    store: EventStore,
    output_path: Optional[str],
) -> bool:
    if output_path:
        store.save_jsonl(output_path)
        return True
    return False


def _replay_execution_store(store: EventStore) -> Dict[str, Any]:
    replay_engine = ReplayEngine()
    return replay_engine.replay(store.all_events())


def execute_sandbox_order_with_eventstore(
    raw_order: Dict[str, Any],
    simulation_mode: str = MODE_SIMULATED_FILL,
    fill_price: Optional[float] = None,
    filled_quantity: Optional[float] = None,
    reject_reason: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    execution_response = execute_sandbox_order(
        raw_order=raw_order,
        simulation_mode=simulation_mode,
        fill_price=fill_price,
        filled_quantity=filled_quantity,
        reject_reason=reject_reason,
    )

    if execution_response["ok"] is not True:
        return execution_response

    execution_data = dict(execution_response["data"])

    store = EventStore()
    event = _build_sandbox_execution_event(execution_data)
    store.record(event)

    persisted = _persist_execution_store_if_needed(store, output_path)
    replay_result = _replay_execution_store(store)

    execution_data.update(
        {
            "event_count": store.count(),
            "event_names": replay_result.get(
                "event_names",
                [execution_data["event_name"]],
            ),
            "persisted": persisted,
            "output_path": output_path,
            "replay": replay_result,
        }
    )

    return _stable_response(
        ok=True,
        data=execution_data,
        error=None,
    )

