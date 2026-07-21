from __future__ import annotations

from copy import deepcopy

import pytest

from scripts.fcp_governance_sequence import (
    fcp_delivery_sequence,
    is_historical_delivery_state_safe,
)


FCP_0019 = "FCF-FCP-0019-A-SHARE-LOCAL-EXPORT-CANONICALIZATION-BRIDGE-APP-1"
FCP_0020 = "FCF-FCP-0020-GOVERNANCE-SUCCESSOR-STATE-SCALABILITY-HARDENING-APP-1"
FCP_0021 = "FCF-FCP-0021-A-SHARE-CROSS-SOURCE-QUALITY-RECONCILIATION-APP-1"


def _truth(**changes: object) -> dict[str, object]:
    values: dict[str, object] = {
        "current_governance_phase_id": FCP_0020,
        "current_governance_phase_status": "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "current_product_implementation_phase": "NONE",
        "latest_completed_governance_delivery": FCP_0019,
        "next_product_implementation_phase": "NOT_SELECTED",
        "next_product_phase_approval": "NOT_APPROVED",
    }
    values.update(changes)
    return values


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (FCP_0019, 19),
        (FCP_0020, 20),
        ("FCF-FCP-0000-INVALID", None),
        ("FCF-FCP-20-INVALID", None),
        ("FCF-FCP-0020-invalid", None),
        ("FCF-FCP-0020-INVALID_", None),
        (None, None),
    ],
)
def test_delivery_sequence_is_strict(value: object, expected: int | None) -> None:
    assert fcp_delivery_sequence(value) == expected


def test_active_contiguous_successor_is_safe_for_history() -> None:
    truth = _truth()
    assert is_historical_delivery_state_safe(truth, FCP_0019) is True
    assert is_historical_delivery_state_safe(truth, FCP_0020) is True


def test_closed_later_delivery_is_safe_for_history() -> None:
    truth = _truth(
        current_governance_phase_id="NONE",
        current_governance_phase_status="NONE",
        latest_completed_governance_delivery=FCP_0020,
    )
    assert is_historical_delivery_state_safe(truth, FCP_0019) is True
    assert is_historical_delivery_state_safe(truth, FCP_0020) is True


def test_next_contiguous_active_phase_is_safe() -> None:
    truth = _truth(
        current_governance_phase_id=FCP_0021,
        latest_completed_governance_delivery=FCP_0020,
    )
    assert is_historical_delivery_state_safe(truth, FCP_0019) is True


@pytest.mark.parametrize(
    "changes",
    [
        {"current_governance_phase_id": "FCF-FCP-0022-SKIPPED"},
        {
            "current_governance_phase_id": FCP_0021,
            "latest_completed_governance_delivery": FCP_0019,
        },
        {"current_governance_phase_id": "malformed"},
        {"current_governance_phase_status": "UNKNOWN"},
        {"latest_completed_governance_delivery": "malformed"},
        {"current_product_implementation_phase": "V2-R48"},
        {"next_product_implementation_phase": "V2-R48"},
        {"next_product_phase_approval": "APPROVED"},
    ],
)
def test_unsafe_successor_states_fail_closed(changes: dict[str, object]) -> None:
    assert is_historical_delivery_state_safe(_truth(**changes), FCP_0019) is False


def test_regressive_active_or_closed_state_fails() -> None:
    assert is_historical_delivery_state_safe(_truth(), FCP_0021) is False
    closed = _truth(
        current_governance_phase_id="NONE",
        current_governance_phase_status="NONE",
        latest_completed_governance_delivery=FCP_0019,
    )
    assert is_historical_delivery_state_safe(closed, FCP_0020) is False


def test_input_mapping_is_not_mutated() -> None:
    truth = _truth()
    original = deepcopy(truth)
    assert is_historical_delivery_state_safe(truth, FCP_0019) is True
    assert truth == original
