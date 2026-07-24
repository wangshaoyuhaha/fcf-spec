from __future__ import annotations

from .contracts import (
    BRIDGE_ID,
    DEFAULT_REGISTRATION,
    SCHEMA_VERSION,
    SOURCE_KIND,
    QmtQuoteEvent,
    canonical_bytes,
    digest,
)
from .receiver import ingest_registered_events


REFERENCE_NOW_MS = 1_775_000_001_000


def build_reference_event_payload(
    *,
    sequence: int = 1,
    received_at_ms: int = 1_775_000_000_500,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "amount_cny": "120000000",
        "bridge_id": BRIDGE_ID,
        "event_time_ms": 1_775_000_000_000,
        "high": "10.2",
        "last": "10.1",
        "low": "9.9",
        "open": "10",
        "previous_close": "9.95",
        "received_at_ms": received_at_ms,
        "schema_version": SCHEMA_VERSION,
        "sequence": sequence,
        "source_kind": SOURCE_KIND,
        "symbol": "600000.SH",
        "volume_native": "120000",
        "volume_unit": "QMT_NATIVE_UNCALIBRATED",
    }
    payload["event_hash"] = digest(payload)
    return payload


def build_reference_event_bytes() -> bytes:
    return canonical_bytes(build_reference_event_payload())


def build_reference_event() -> QmtQuoteEvent:
    return QmtQuoteEvent(**build_reference_event_payload())


def build_reference_snapshot():
    return ingest_registered_events(
        (build_reference_event_bytes(),),
        now_ms=REFERENCE_NOW_MS,
        registration=DEFAULT_REGISTRATION,
    )


def render_reference_snapshot_json() -> str:
    return canonical_bytes(build_reference_snapshot().payload()).decode("ascii")

