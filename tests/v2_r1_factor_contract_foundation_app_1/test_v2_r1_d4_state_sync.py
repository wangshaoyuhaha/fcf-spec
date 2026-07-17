from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.v2_r1_factor_contract_foundation_app_1 import evaluate_state_sync

from .fixtures import state_sync_anchor


def test_d4_state_sync_hash_is_deterministic_and_payload_is_immutable():
    first = state_sync_anchor(payload={"volume": "12345", "close": "100.00"})
    second = state_sync_anchor(payload={"close": "100.00", "volume": "12345"})

    assert first.state_hash == second.state_hash
    assert isinstance(first.payload, MappingProxyType)
    with pytest.raises(TypeError):
        first.payload["close"] = "101.00"
    with pytest.raises(ValueError, match="does not match"):
        replace(first, payload={"close": "999.00"})


def test_d4_state_sync_enforces_time_order_and_expiry():
    anchor = state_sync_anchor()

    assert evaluate_state_sync(anchor, "2026-07-17T01:01:04Z").status == "ACTIVE"
    assert (
        evaluate_state_sync(anchor, "2026-07-17T01:01:05Z").status
        == "STATE_EXPIRED"
    )
    with pytest.raises(ValueError, match="out of order"):
        state_sync_anchor(ingest_time_utc="2026-07-17T00:59:00Z")
    with pytest.raises(ValueError, match="cannot precede"):
        evaluate_state_sync(anchor, "2026-07-17T00:59:00Z")


def test_d4_state_sync_requires_registered_artifact_metadata():
    with pytest.raises(ValueError, match="safe identifier"):
        state_sync_anchor(registered_artifact_id="unsafe artifact id")


def test_d4_state_sync_normalizes_equivalent_utc_timestamps_before_hashing():
    normalized = state_sync_anchor()
    offset_form = state_sync_anchor(
        event_time_utc="2026-07-17T01:00:00+00:00",
        source_time_utc="2026-07-17T01:00:01+00:00",
        ingest_time_utc="2026-07-17T01:00:02+00:00",
        processing_time_utc="2026-07-17T01:00:03+00:00",
        snapshot_time_utc="2026-07-17T01:00:04+00:00",
    )

    assert offset_form.state_hash == normalized.state_hash
    assert offset_form.snapshot_time_utc == "2026-07-17T01:00:04Z"
