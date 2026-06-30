from typing import Any, Dict, List, Optional

from fcf.pipelines.market_input_pipeline import (
    process_raw_market_batch,
    process_raw_market_input,
)


API_NAME = "local_market_input_api"
API_VERSION = "0.1.0"


def _success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "api": API_NAME,
        "api_version": API_VERSION,
        "error": None,
        "data": data,
    }


def _error_response(error: Exception) -> Dict[str, Any]:
    return {
        "ok": False,
        "api": API_NAME,
        "api_version": API_VERSION,
        "error": {
            "type": error.__class__.__name__,
            "message": str(error),
        },
        "data": None,
    }


def handle_single_market_input(
    raw: Dict[str, Any],
    correlation_id: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        result = process_raw_market_input(
            raw=raw,
            correlation_id=correlation_id,
            output_path=output_path,
        )
        return _success_response(result)
    except Exception as error:
        return _error_response(error)


def handle_batch_market_input(
    rows: List[Dict[str, Any]],
    correlation_id: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        result = process_raw_market_batch(
            rows=rows,
            correlation_id=correlation_id,
            output_path=output_path,
        )
        return _success_response(result)
    except Exception as error:
        return _error_response(error)


def describe_api_contract() -> Dict[str, Any]:
    return {
        "api": API_NAME,
        "api_version": API_VERSION,
        "purpose": "local wrapper for controlled market input pipeline",
        "external_systems": [
            "Dify workflow",
            "local scripts",
            "future HTTP wrapper",
        ],
        "allowed_actions": [
            "validate raw market input",
            "build raw market event",
            "persist event when output_path is provided",
            "replay persisted or in-memory events",
            "return summary dict",
        ],
        "forbidden_actions": [
            "no real exchange API key",
            "no real order placement",
            "no secret storage",
            "no direct trading execution",
            "no bypassing EventStore",
            "no bypassing ReplayEngine",
        ],
        "single_input_handler": "handle_single_market_input",
        "batch_input_handler": "handle_batch_market_input",
    }
