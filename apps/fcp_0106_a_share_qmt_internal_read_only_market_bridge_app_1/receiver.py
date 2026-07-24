from __future__ import annotations

import json
from pathlib import Path
import re
import stat

from .contracts import (
    DEFAULT_REGISTRATION,
    EMPTY_INGEST_STATE,
    EVENT_FIELDS,
    QmtBridgeBatchSnapshot,
    QmtBridgeIngestState,
    QmtInternalBridgeRegistration,
    QmtQuoteEvent,
    canonical_bytes,
    digest,
)

SPOOL_FILE = re.compile(
    r"^quote-(?P<code>[0-9]{6})-(?P<market>SH|SZ|BJ)-"
    r"(?P<received_at_ms>[0-9]{13})-(?P<sequence>[0-9]{12})\.json$"
)


def _is_reparse_point(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def parse_registered_event(
    raw: bytes,
    registration: QmtInternalBridgeRegistration = DEFAULT_REGISTRATION,
) -> QmtQuoteEvent:
    if type(raw) is not bytes:
        raise TypeError("raw event must be exact bytes")
    if not raw or len(raw) > registration.max_event_bytes:
        raise ValueError("raw event size is outside the registered limit")
    try:
        payload = json.loads(raw.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("raw event must be ASCII JSON") from exc
    if not isinstance(payload, dict) or tuple(sorted(payload)) != EVENT_FIELDS:
        raise ValueError("raw event does not match the closed schema")
    if raw != canonical_bytes(payload):
        raise ValueError("raw event must use canonical ASCII JSON")
    event = QmtQuoteEvent(**payload)
    if event.bridge_id != registration.bridge_id:
        raise ValueError("bridge_id is not registered")
    if event.schema_version != registration.schema_version:
        raise ValueError("schema_version is not registered")
    if event.source_kind != registration.source_kind:
        raise ValueError("source_kind is not registered")
    if event.symbol not in registration.allowed_symbols:
        raise ValueError("symbol is not registered")
    return event


def ingest_registered_events(
    raw_events: tuple[bytes, ...],
    *,
    now_ms: int,
    prior_state: QmtBridgeIngestState = EMPTY_INGEST_STATE,
    registration: QmtInternalBridgeRegistration = DEFAULT_REGISTRATION,
) -> QmtBridgeBatchSnapshot:
    if not isinstance(raw_events, tuple) or not raw_events:
        raise ValueError("raw_events must be a non-empty tuple")
    if len(raw_events) > registration.max_batch_files:
        raise ValueError("raw event batch exceeds the registered limit")
    if type(now_ms) is not int or now_ms <= 0:
        raise ValueError("now_ms must be a positive integer")
    if not isinstance(prior_state, QmtBridgeIngestState):
        raise TypeError("prior_state must be exact ingest state")
    events = tuple(parse_registered_event(raw, registration) for raw in raw_events)
    ordered = tuple(
        sorted(events, key=lambda item: (item.received_at_ms, item.symbol, item.sequence))
    )
    if events != ordered:
        raise ValueError("events must use canonical chronological order")
    sequences = dict(prior_state.last_sequences)
    hashes = list(prior_state.event_hashes)
    known_hashes = set(hashes)
    for event in events:
        if event.event_hash in known_hashes:
            raise ValueError("duplicate event hash")
        if event.received_at_ms > now_ms + registration.max_future_skew_ms:
            raise ValueError("event received time is in the future")
        if event.event_time_ms > event.received_at_ms + registration.max_future_skew_ms:
            raise ValueError("market event time is in the future")
        if now_ms - event.received_at_ms > registration.max_event_age_ms:
            raise ValueError("event receive time is stale")
        if now_ms - event.event_time_ms > registration.max_event_age_ms:
            raise ValueError("market event time is stale")
        previous = sequences.get(event.symbol, 0)
        if event.sequence <= previous:
            raise ValueError("event sequence is duplicate or out of order")
        sequences[event.symbol] = event.sequence
        hashes.append(event.event_hash)
        known_hashes.add(event.event_hash)
    state = QmtBridgeIngestState(
        last_sequences={key: sequences[key] for key in sorted(sequences)},
        event_hashes=tuple(hashes[-registration.max_batch_files :]),
    )
    payload = {
        "accepted_event_hashes": [item.event_hash for item in events],
        "account_authority": False,
        "bridge_state": "CANDIDATE_REALTIME_OBSERVED",
        "data_promotion_authority": False,
        "execution_authority": False,
        "latest_received_at_ms": max(item.received_at_ms for item in events),
        "market_data_authority": False,
        "operator_review_required": True,
        "read_only": True,
        "registration_hash": registration.registration_hash,
        "state_event_hashes": list(state.event_hashes),
        "state_last_sequences": dict(state.last_sequences),
    }
    return QmtBridgeBatchSnapshot(
        registration_hash=registration.registration_hash,
        accepted_events=events,
        state=state,
        latest_received_at_ms=payload["latest_received_at_ms"],
        bridge_state="CANDIDATE_REALTIME_OBSERVED",
        operator_review_required=True,
        read_only=True,
        market_data_authority=False,
        data_promotion_authority=False,
        account_authority=False,
        execution_authority=False,
        snapshot_hash=digest(payload),
    )


def read_registered_spool(
    spool_root: Path,
    *,
    now_ms: int,
    prior_state: QmtBridgeIngestState = EMPTY_INGEST_STATE,
    registration: QmtInternalBridgeRegistration = DEFAULT_REGISTRATION,
) -> QmtBridgeBatchSnapshot:
    root = spool_root.resolve(strict=True)
    if not root.is_dir() or root.is_symlink() or _is_reparse_point(root):
        raise ValueError("spool_root must be a regular local directory")
    if str(root).startswith("\\\\"):
        raise ValueError("spool_root must not be a network path")
    entries = tuple(sorted(root.iterdir(), key=lambda item: item.name))
    if not entries:
        raise ValueError("spool_root contains no registered events")
    if len(entries) > registration.max_batch_files:
        raise ValueError("spool_root exceeds the registered file limit")
    raw_events: list[bytes] = []
    for path in entries:
        name_match = SPOOL_FILE.fullmatch(path.name)
        if (
            name_match is None
            or path.is_symlink()
            or _is_reparse_point(path)
            or not path.is_file()
        ):
            raise ValueError("spool_root contains an unregistered entry")
        if path.stat().st_size > registration.max_event_bytes:
            raise ValueError("spool event exceeds the registered size")
        raw = path.read_bytes()
        event = parse_registered_event(raw, registration)
        filename_identity = (
            f"{name_match.group('code')}.{name_match.group('market')}",
            int(name_match.group("received_at_ms")),
            int(name_match.group("sequence")),
        )
        event_identity = (
            event.symbol,
            event.received_at_ms,
            event.sequence,
        )
        if filename_identity != event_identity:
            raise ValueError("spool filename does not match the event identity")
        raw_events.append(raw)
    return ingest_registered_events(
        tuple(raw_events),
        now_ms=now_ms,
        prior_state=prior_state,
        registration=registration,
    )
