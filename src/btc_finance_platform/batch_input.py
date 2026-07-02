from typing import Any

from btc_finance_platform.paper_input import validate_paper_input


def validate_paper_input_batch(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(payloads, list):
        raise ValueError("payloads must be a list")

    if not payloads:
        raise ValueError("payloads must not be empty")

    validated_items = [validate_paper_input(payload) for payload in payloads]

    return {
        "ok": True,
        "type": "validated_paper_input_batch",
        "count": len(validated_items),
        "items": validated_items,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
