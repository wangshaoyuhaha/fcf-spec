from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from apps.v2_r7_local_market_session_registry_foundation_app_1 import (
    V2_R7_LOCAL_MARKET_SESSION_BOUNDARY,
    LocalMarketSessionRegistry,
    MarketSessionDefinition,
    RegisteredSessionInterval,
    V2R7LocalMarketSessionBoundary,
    build_operator_acceptance,
    build_read_model,
    resolve_market_session,
)


def _interval(
    interval_id: str,
    sequence: int,
    phase: str,
    start: str,
    end: str,
    *,
    available: str = "2026-01-01T00:00:00Z",
) -> RegisteredSessionInterval:
    return RegisteredSessionInterval(
        interval_id=interval_id,
        sequence=sequence,
        phase=phase,
        start_at_utc=start,
        end_at_utc=end,
        available_at_utc=available,
        source_artifact_hash=f"{sequence}" * 64,
    )


def _definition(
    *,
    available: str = "2026-01-01T00:00:00Z",
    intervals: tuple[RegisteredSessionInterval, ...] | None = None,
    continuous: bool = False,
) -> MarketSessionDefinition:
    registered = intervals or (
        _interval(
            "registered-call-auction",
            1,
            "CALL_AUCTION",
            "2026-01-01T00:30:00Z",
            "2026-01-01T01:00:00Z",
        ),
        _interval(
            "registered-continuous-session",
            2,
            "CONTINUOUS_SESSION",
            "2026-01-01T01:00:00Z",
            "2026-01-01T03:00:00Z",
        ),
        _interval(
            "registered-late-session",
            3,
            "LATE_SESSION",
            "2026-01-01T03:00:00Z",
            "2026-01-01T03:30:00Z",
        ),
    )
    return MarketSessionDefinition(
        registry_id="registered-market-session",
        venue="registered-venue",
        market="registered-market",
        trade_date="2026-01-01",
        timezone="asia-shanghai",
        calendar_version="calendar-v1",
        rule_version="rules-v1",
        available_at_utc=available,
        effective_from_utc="2026-01-01T00:00:00Z",
        expires_at_utc="2026-01-02T00:00:00Z",
        intervals=registered,
        continuous_market=continuous,
    )


def test_d1_boundary_is_closed_and_immutable() -> None:
    boundary = V2_R7_LOCAL_MARKET_SESSION_BOUNDARY

    assert boundary.local_only is True
    assert boundary.system_clock_authority_allowed is False
    assert boundary.hardcoded_venue_schedule_allowed is False
    assert boundary.order_or_execution_allowed is False
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R7LocalMarketSessionBoundary(network_access_allowed=True)
    with pytest.raises(FrozenInstanceError):
        boundary.network_access_allowed = True  # type: ignore[misc]


def test_d2_contract_rejects_inferred_interval_and_unknown_phase() -> None:
    with pytest.raises(ValueError, match="not inferred"):
        replace(
            _definition().intervals[0],
            observed_not_inferred=False,
        )
    with pytest.raises(ValueError, match="phase is not registered"):
        replace(_definition().intervals[0], phase="UNREGISTERED_PHASE")


def test_d2_definition_rejects_overlap_and_noncontiguous_sequence() -> None:
    overlapping = (
        _interval("first-window", 1, "PRE_OPEN", "2026-01-01T00:00:00Z", "2026-01-01T01:00:00Z"),
        _interval("second-window", 2, "CALL_AUCTION", "2026-01-01T00:59:00Z", "2026-01-01T01:30:00Z"),
    )
    with pytest.raises(ValueError, match="overlap"):
        _definition(intervals=overlapping)
    with pytest.raises(ValueError, match="sequence must be contiguous"):
        _definition(
            intervals=(
                _interval("first-window", 2, "PRE_OPEN", "2026-01-01T00:00:00Z", "2026-01-01T00:30:00Z"),
            )
        )


def test_d3_resolution_is_deterministic_and_uses_half_open_intervals() -> None:
    definition = _definition()
    auction = resolve_market_session(
        definition,
        observed_at_utc="2026-01-01T00:45:00Z",
        as_of_utc="2026-01-01T01:05:00Z",
    )
    boundary = resolve_market_session(
        definition,
        observed_at_utc="2026-01-01T01:00:00Z",
        as_of_utc="2026-01-01T01:05:00Z",
    )
    repeated = resolve_market_session(
        definition,
        observed_at_utc="2026-01-01T00:45:00Z",
        as_of_utc="2026-01-01T01:05:00Z",
    )

    assert auction.state == "RESOLVED"
    assert auction.phase == "CALL_AUCTION"
    assert boundary.phase == "CONTINUOUS_SESSION"
    assert auction.evidence_hash == repeated.evidence_hash


def test_d3_continuous_market_uses_registered_analysis_window() -> None:
    window = _interval(
        "btc-analysis-window",
        1,
        "CONTINUOUS_SESSION",
        "2026-01-01T00:00:00Z",
        "2026-01-02T00:00:00Z",
    )
    evidence = resolve_market_session(
        _definition(intervals=(window,), continuous=True),
        observed_at_utc="2026-01-01T12:00:00Z",
        as_of_utc="2026-01-01T12:00:01Z",
    )

    assert evidence.phase == "CONTINUOUS_SESSION"
    assert evidence.interval_id == "btc-analysis-window"


def test_d4_unavailable_definition_and_interval_fail_closed() -> None:
    definition_blocked = resolve_market_session(
        _definition(available="2026-01-01T02:00:00Z"),
        observed_at_utc="2026-01-01T00:45:00Z",
        as_of_utc="2026-01-01T01:00:00Z",
    )
    late_interval = (
        _interval(
            "late-registration",
            1,
            "CALL_AUCTION",
            "2026-01-01T00:30:00Z",
            "2026-01-01T01:00:00Z",
            available="2026-01-01T02:00:00Z",
        ),
    )
    interval_blocked = resolve_market_session(
        _definition(intervals=late_interval),
        observed_at_utc="2026-01-01T00:45:00Z",
        as_of_utc="2026-01-01T01:00:00Z",
    )

    assert definition_blocked.state == "BLOCKED"
    assert definition_blocked.reason_codes == ("DEFINITION_NOT_AVAILABLE_AT_AS_OF",)
    assert interval_blocked.reason_codes == ("INTERVAL_NOT_AVAILABLE_AT_AS_OF",)


def test_d4_future_observation_and_outside_session_fail_closed() -> None:
    with pytest.raises(ValueError, match="future observation"):
        resolve_market_session(
            _definition(),
            observed_at_utc="2026-01-01T02:00:00Z",
            as_of_utc="2026-01-01T01:00:00Z",
        )
    outside = resolve_market_session(
        _definition(),
        observed_at_utc="2026-01-01T00:10:00Z",
        as_of_utc="2026-01-01T00:10:01Z",
    )

    assert outside.state == "BLOCKED"
    assert outside.reason_codes == ("OUTSIDE_REGISTERED_SESSION",)


def test_d4_expired_definition_is_blocked() -> None:
    expired = resolve_market_session(
        _definition(),
        observed_at_utc="2026-01-02T00:00:00Z",
        as_of_utc="2026-01-02T00:00:01Z",
    )

    assert expired.state == "BLOCKED"
    assert expired.reason_codes == ("DEFINITION_NOT_EFFECTIVE",)


def test_d5_registry_is_append_only_and_rejects_duplicates() -> None:
    definition = _definition()
    registry = LocalMarketSessionRegistry().append(definition)

    assert registry.resolve(
        definition.registry_id,
        observed_at_utc="2026-01-01T00:45:00Z",
        as_of_utc="2026-01-01T01:00:00Z",
    ).state == "RESOLVED"
    with pytest.raises(ValueError, match="duplicate market session"):
        registry.append(definition)


def test_d6_read_model_and_acceptance_are_read_only() -> None:
    definition = _definition()
    registry = LocalMarketSessionRegistry().append(definition)
    evidence = registry.resolve(
        definition.registry_id,
        observed_at_utc="2026-01-01T00:45:00Z",
        as_of_utc="2026-01-01T01:00:00Z",
    )
    model = build_read_model(registry)
    acceptance = build_operator_acceptance(evidence)

    assert isinstance(model.payload, MappingProxyType)
    assert model.payload["network_source"] is False
    assert model.payload["system_clock_authority"] is False
    assert model.payload["order_or_execution"] is False
    assert acceptance.status == "WAITING_FOR_OPERATOR_REVIEW"
    assert acceptance.action_created is False
    with pytest.raises(TypeError):
        model.payload["network_source"] = True  # type: ignore[index]
