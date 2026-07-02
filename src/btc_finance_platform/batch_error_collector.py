from typing import Any

from btc_finance_platform.paper_input import validate_paper_input


def collect_batch_input_errors(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(payloads, list):
        raise ValueError("payloads must be a list")

    valid_items: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for index, payload in enumerate(payloads):
        try:
            valid_items.append(validate_paper_input(payload))
        except Exception as exc:
            errors.append({
                "index": index,
                "error": str(exc),
                "paper_only": True,
                "real_order": False,
                "real_execution": False,
                "real_money_impact": False,
            })

    return {
        "ok": True,
        "type": "paper_batch_input_error_collection",
        "total_count": len(payloads),
        "valid_count": len(valid_items),
        "error_count": len(errors),
        "valid_items": valid_items,
        "errors": errors,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
    }
