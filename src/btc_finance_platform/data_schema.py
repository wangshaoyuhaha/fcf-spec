from typing import Any


REQUIRED_PAPER_INPUT_FIELDS = {
    "symbol": str,
    "price": (int, float),
    "reference_price": (int, float),
}


def validate_paper_input_schema(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    missing = [key for key in REQUIRED_PAPER_INPUT_FIELDS if key not in payload]
    if missing:
        raise ValueError(f"missing required fields: {missing}")

    for key, expected_type in REQUIRED_PAPER_INPUT_FIELDS.items():
        if not isinstance(payload[key], expected_type):
            raise ValueError(f"invalid field type: {key}")

    if not payload["symbol"]:
        raise ValueError("symbol is required")

    if float(payload["price"]) <= 0:
        raise ValueError("price must be positive")

    if float(payload["reference_price"]) <= 0:
        raise ValueError("reference_price must be positive")

    return {
        "ok": True,
        "type": "paper_input_schema_validation",
        "symbol": str(payload["symbol"]).upper(),
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }


def validate_paper_batch_schema(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(payloads, list):
        raise ValueError("payloads must be a list")

    if not payloads:
        raise ValueError("payloads must not be empty")

    validations = [validate_paper_input_schema(payload) for payload in payloads]

    return {
        "ok": True,
        "type": "paper_batch_schema_validation",
        "count": len(validations),
        "symbols": [item["symbol"] for item in validations],
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
