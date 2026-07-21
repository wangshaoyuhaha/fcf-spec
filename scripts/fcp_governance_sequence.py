from __future__ import annotations

import re
from collections.abc import Mapping


_DELIVERY_ID = re.compile(r"^FCF-FCP-([0-9]{4})-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
_ACTIVE_STATUSES = frozenset(
    {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
)


def fcp_delivery_sequence(delivery_id: object) -> int | None:
    if not isinstance(delivery_id, str):
        return None
    match = _DELIVERY_ID.fullmatch(delivery_id)
    if match is None:
        return None
    sequence = int(match.group(1))
    return sequence if sequence > 0 else None


def is_historical_delivery_state_safe(
    truth: object,
    historical_delivery_id: str,
) -> bool:
    if not isinstance(truth, Mapping):
        return False
    historical_sequence = fcp_delivery_sequence(historical_delivery_id)
    if historical_sequence is None:
        return False
    if (
        truth.get("current_product_implementation_phase") != "NONE"
        or truth.get("next_product_implementation_phase") != "NOT_SELECTED"
        or truth.get("next_product_phase_approval") != "NOT_APPROVED"
    ):
        return False
    current_id = truth.get("current_governance_phase_id")
    current_status = truth.get("current_governance_phase_status")
    latest_id = truth.get("latest_completed_governance_delivery")
    latest_sequence = fcp_delivery_sequence(latest_id)
    if current_id == "NONE":
        return current_status == "NONE" and latest_sequence is not None and (
            latest_sequence >= historical_sequence
        )
    current_sequence = fcp_delivery_sequence(current_id)
    if current_sequence is None or current_status not in _ACTIVE_STATUSES:
        return False
    if current_sequence == historical_sequence:
        return latest_sequence is None or latest_sequence < historical_sequence
    return (
        current_sequence > historical_sequence
        and latest_sequence is not None
        and latest_sequence >= historical_sequence
        and current_sequence == latest_sequence + 1
    )
