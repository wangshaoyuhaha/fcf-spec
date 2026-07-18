from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import CLOCK_TYPES, EVIDENCE_GROUPS, RegisteredClockEventState
from .registry import LocalMultiClockEventStateRegistry


@dataclass(frozen=True)
class MultiClockEventStateSnapshot:
    market: str
    horizon: str
    observed_at_utc: str
    evaluated_at_utc: str
    state: str
    active_states: tuple[RegisteredClockEventState, ...]
    clock_groups: Mapping[str, tuple[str, ...]]
    evidence_groups: Mapping[str, tuple[str, ...]]
    missing_clocks: tuple[str, ...]
    overlap_codes: tuple[str, ...]
    conflict_policy: str
    winner_state_id: None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"MISSING", "RESOLVED"}:
            raise ValueError("invalid multi-clock snapshot state")
        if self.conflict_policy != "PRESERVE_ALL_NO_WINNER":
            raise ValueError("multi-clock conflict policy is not closed")
        if self.winner_state_id is not None:
            raise ValueError("multi-clock snapshot cannot select a winner")
        if self.operator_review_required is not True:
            raise ValueError("multi-clock snapshot requires Operator review")


def resolve_multi_clock_event_state(
    registry: LocalMultiClockEventStateRegistry,
    *,
    market: str,
    horizon: str,
    observed_at_utc: str,
    as_of_utc: str,
) -> MultiClockEventStateSnapshot:
    market_id = identifier(market, "market")
    horizon_id = identifier(horizon, "horizon")
    observed_text = utc(observed_at_utc, "observed_at_utc")
    evaluated_text = utc(as_of_utc, "as_of_utc")
    observed = instant(observed_text)
    as_of = instant(evaluated_text)
    if observed > as_of:
        raise ValueError("clock state resolution cannot use future observation")
    active = tuple(
        sorted(
            (
                state
                for state in registry.states
                if state.market == market_id
                and state.horizon == horizon_id
                and instant(state.available_at_utc) <= as_of
                and instant(state.effective_from_utc)
                <= observed
                < instant(state.effective_to_utc)
            ),
            key=lambda state: (
                CLOCK_TYPES.index(state.clock_type),
                state.effective_from_utc,
                state.state_id,
            ),
        )
    )
    clock_values = {
        clock: tuple(state.state_id for state in active if state.clock_type == clock)
        for clock in CLOCK_TYPES
    }
    evidence_values = {
        group: tuple(
            state.state_id for state in active if state.evidence_group == group
        )
        for group in EVIDENCE_GROUPS
    }
    missing_clocks = tuple(clock for clock, values in clock_values.items() if not values)
    overlap_codes = tuple(
        f"OVERLAP_PRESERVED_{clock}"
        for clock, values in clock_values.items()
        if len(values) > 1
    )
    state = "RESOLVED" if active else "MISSING"
    reasons = [
        "ACTIVE_CLOCK_STATE_STACK_RESOLVED"
        if active
        else "NO_ACTIVE_CLOCK_STATE_AT_AS_OF"
    ]
    if overlap_codes:
        reasons.append("CONFLICTS_PRESERVED_NO_WINNER")
    payload = {
        "active_state_hashes": [item.state_hash for item in active],
        "clock_groups": clock_values,
        "conflict_policy": "PRESERVE_ALL_NO_WINNER",
        "evaluated_at_utc": evaluated_text,
        "evidence_groups": evidence_values,
        "horizon": horizon_id,
        "market": market_id,
        "missing_clocks": missing_clocks,
        "observed_at_utc": observed_text,
        "overlap_codes": overlap_codes,
        "reason_codes": reasons,
        "state": state,
        "winner_state_id": None,
    }
    snapshot_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return MultiClockEventStateSnapshot(
        market=market_id,
        horizon=horizon_id,
        observed_at_utc=observed_text,
        evaluated_at_utc=evaluated_text,
        state=state,
        active_states=active,
        clock_groups=MappingProxyType(clock_values),
        evidence_groups=MappingProxyType(evidence_values),
        missing_clocks=missing_clocks,
        overlap_codes=overlap_codes,
        conflict_policy="PRESERVE_ALL_NO_WINNER",
        winner_state_id=None,
        reason_codes=tuple(reasons),
        operator_review_required=True,
        snapshot_hash=snapshot_hash,
    )
