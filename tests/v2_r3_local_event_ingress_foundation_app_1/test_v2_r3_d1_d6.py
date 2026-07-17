from dataclasses import FrozenInstanceError, replace
from decimal import Decimal

import pytest

from apps.v2_r3_local_event_ingress_foundation_app_1 import (
    V2_R3_LOCAL_EVENT_INGRESS_BOUNDARY,
    BoundedLocalEventIngress,
    LocalEventEnvelope,
    LocalEventRights,
    ReplayCheckpoint,
    build_checkpoint,
    build_operator_acceptance,
    build_read_model,
    replay_local_events,
    restore_checkpoint,
)


def _rights(**overrides: object) -> LocalEventRights:
    values = {
        "license_id": "operator-local-license-v1",
        "permitted_use": "local-paper-research",
        "retention_days": 30,
    }
    values.update(overrides)
    return LocalEventRights(**values)


def _event(
    sequence: int = 1,
    *,
    stream_id: str = "registered-stream-a",
    event_id: str | None = None,
    minute: int | None = None,
    payload: dict[str, object] | None = None,
    **overrides: object,
) -> LocalEventEnvelope:
    offset = sequence if minute is None else minute
    values = {
        "event_id": event_id or f"registered-event-{stream_id}-{sequence}",
        "stream_id": stream_id,
        "source_id": "operator-local-source",
        "registered_artifact_id": "registered-artifact-events-v1",
        "event_type": "field-observation",
        "source_sequence": sequence,
        "event_at_utc": f"2026-07-17T00:{offset:02d}:00Z",
        "received_at_utc": f"2026-07-17T00:{offset:02d}:01Z",
        "processed_at_utc": f"2026-07-17T00:{offset:02d}:02Z",
        "payload": payload or {"field": "price", "value": Decimal("101.25")},
        "rights": _rights(),
    }
    values.update(overrides)
    return LocalEventEnvelope(**values)


def test_d1_boundary_and_local_rights_are_closed() -> None:
    boundary = V2_R3_LOCAL_EVENT_INGRESS_BOUNDARY

    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.operator_review_required is True
    assert boundary.network_access_allowed is False
    assert boundary.external_source_allowed is False
    assert boundary.daemon_allowed is False
    assert boundary.external_queue_allowed is False
    assert boundary.market_selection_allowed is False
    assert boundary.order_path_allowed is False
    assert boundary.real_execution_allowed is False
    with pytest.raises(ValueError, match="local-only scope"):
        _rights(network_retrieval_allowed=True)


def test_d2_event_is_immutable_and_hashes_are_deterministic() -> None:
    first = _event(payload={"count": 3, "field": "price", "value": Decimal("1.20")})
    second = _event(payload={"value": Decimal("1.2"), "field": "price", "count": 3})

    assert first.payload_sha256 == second.payload_sha256
    assert first.event_hash == second.event_hash
    assert first.payload["value"] == Decimal("1.20")
    with pytest.raises(TypeError):
        first.payload["field"] = "changed"
    with pytest.raises(FrozenInstanceError):
        first.event_id = "changed"


def test_d2_rejects_time_inversion_checksum_mismatch_and_binary_float() -> None:
    with pytest.raises(ValueError, match="time must be ordered"):
        _event(received_at_utc="2026-07-16T23:59:59Z")
    with pytest.raises(ValueError, match="does not match"):
        _event(declared_payload_sha256="0" * 64)
    with pytest.raises(ValueError, match="binary float"):
        _event(payload={"value": 1.25})


def test_d3_ingress_accepts_contiguous_events_and_independent_streams() -> None:
    ingress = BoundedLocalEventIngress(capacity=4, ttl_seconds=600)
    ingress, first = ingress.accept(
        _event(1), as_of_utc="2026-07-17T00:02:00Z"
    )
    ingress, second = ingress.accept(
        _event(1, stream_id="registered-stream-b", minute=2),
        as_of_utc="2026-07-17T00:03:00Z",
    )
    ingress, third = ingress.accept(
        _event(2), as_of_utc="2026-07-17T00:03:00Z"
    )

    assert (first.queue_size, second.queue_size, third.queue_size) == (1, 2, 3)
    assert dict(ingress.last_sequences) == {
        "registered-stream-a": 2,
        "registered-stream-b": 1,
    }


def test_d3_ingress_rejects_duplicate_gap_expiry_and_capacity_overflow() -> None:
    ingress = BoundedLocalEventIngress(capacity=1, ttl_seconds=600)
    event = _event(1)
    accepted, _ = ingress.accept(event, as_of_utc="2026-07-17T00:02:00Z")

    with pytest.raises(ValueError, match="capacity exceeded"):
        accepted.accept(_event(2), as_of_utc="2026-07-17T00:03:00Z")
    with pytest.raises(ValueError, match="duplicate event_id"):
        BoundedLocalEventIngress(capacity=2, ttl_seconds=600).accept(
            event, as_of_utc="2026-07-17T00:02:00Z"
        )[0].accept(event, as_of_utc="2026-07-17T00:02:00Z")
    with pytest.raises(ValueError, match="out-of-order sequence"):
        BoundedLocalEventIngress(capacity=2, ttl_seconds=600).accept(
            _event(2), as_of_utc="2026-07-17T00:03:00Z"
        )
    with pytest.raises(ValueError, match="expired"):
        BoundedLocalEventIngress(capacity=2, ttl_seconds=10).accept(
            event, as_of_utc="2026-07-17T00:02:00Z"
        )


def test_d4_replay_checkpoint_and_restore_are_deterministic() -> None:
    events = (_event(1), _event(2), _event(3))
    first, receipts = replay_local_events(
        events,
        capacity=4,
        ttl_seconds=600,
        as_of_utc="2026-07-17T00:04:00Z",
    )
    second, repeated = replay_local_events(
        events,
        capacity=4,
        ttl_seconds=600,
        as_of_utc="2026-07-17T00:04:00Z",
    )
    checkpoint = build_checkpoint(
        first,
        checkpoint_id="registered-checkpoint-1",
        created_at_utc="2026-07-17T00:04:01Z",
    )
    restored = restore_checkpoint(
        events,
        checkpoint,
        capacity=4,
        ttl_seconds=600,
    )

    assert first == second == restored
    assert receipts == repeated
    assert checkpoint.event_count == 3
    assert len(checkpoint.events_hash) == 64


def test_d4_restore_rejects_checkpoint_mismatch() -> None:
    events = (_event(1),)
    ingress, _ = replay_local_events(
        events,
        capacity=2,
        ttl_seconds=600,
        as_of_utc="2026-07-17T00:02:00Z",
    )
    checkpoint = build_checkpoint(
        ingress,
        checkpoint_id="registered-checkpoint-1",
        created_at_utc="2026-07-17T00:02:01Z",
    )
    unsafe = replace(checkpoint, events_hash="0" * 64)

    with pytest.raises(ValueError, match="event hash mismatch"):
        restore_checkpoint(
            events,
            unsafe,
            capacity=2,
            ttl_seconds=600,
        )


def test_d5_read_model_is_immutable_metadata_only() -> None:
    ingress, _ = replay_local_events(
        (_event(1),),
        capacity=2,
        ttl_seconds=600,
        as_of_utc="2026-07-17T00:02:00Z",
    )
    checkpoint = build_checkpoint(
        ingress,
        checkpoint_id="registered-checkpoint-1",
        created_at_utc="2026-07-17T00:02:01Z",
    )
    model = build_read_model(ingress, checkpoint)

    assert model.payload["read_only"] is True
    assert model.payload["event_count"] == 1
    assert model.payload["external_source_allowed"] is False
    assert model.payload["market_selection_allowed"] is False
    assert model.payload["order_path_allowed"] is False
    assert "payload" not in model.payload
    with pytest.raises(TypeError):
        model.payload["status"] = "changed"


def test_d6_operator_acceptance_cannot_auto_approve() -> None:
    ingress, _ = replay_local_events(
        (_event(1),),
        capacity=2,
        ttl_seconds=600,
        as_of_utc="2026-07-17T00:02:00Z",
    )
    checkpoint = build_checkpoint(
        ingress,
        checkpoint_id="registered-checkpoint-1",
        created_at_utc="2026-07-17T00:02:01Z",
    )
    acceptance = build_operator_acceptance(ingress, checkpoint)

    assert acceptance.status == "READY_FOR_OPERATOR_REVIEW"
    assert acceptance.operator_review_required is True
    assert acceptance.automatic_approval_allowed is False

    unsafe = replace(checkpoint, events_hash="0" * 64)
    blocked = build_operator_acceptance(ingress, unsafe)
    blocked_model = build_read_model(ingress, unsafe)
    assert blocked.status == "BLOCKED"
    assert blocked_model.payload["status"] == "BLOCKED"


def test_checkpoint_mapping_is_immutable() -> None:
    checkpoint = ReplayCheckpoint(
        checkpoint_id="registered-checkpoint-1",
        created_at_utc="2026-07-17T00:02:01Z",
        event_count=1,
        last_sequences={"registered-stream-a": 1},
        events_hash="0" * 64,
    )

    with pytest.raises(TypeError):
        checkpoint.last_sequences["registered-stream-a"] = 2
