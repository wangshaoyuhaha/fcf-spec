from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCBookDelta,
    BTCBookLevel,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCObservationHeader,
    BTCReferencePriceObservation,
    BTCRegisteredArtifact,
    BTCTradeObservation,
)
from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    BTCObservation,
    decimal_text,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import (
    BTCLocalExportBridgeManifest,
    BTCLocalExportBridgeResult,
    BTCLocalExportProfile,
    RegisteredBTCLocalExport,
)


def _value(row: Mapping[str, object], profile: BTCLocalExportProfile, name: str) -> object:
    source_name = profile.canonical_to_source[name]
    if source_name not in row:
        raise ValueError(f"source row lacks required field {source_name}")
    return row[source_name]


def _integer(value: object, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        result = int(str(value))
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if str(result) != str(value).strip() or result <= 0:
        raise ValueError(f"{name} must be a positive canonical integer")
    return result


def _levels(value: object, name: str) -> tuple[BTCBookLevel, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array of price-quantity pairs")
    levels: list[BTCBookLevel] = []
    for item in value:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"{name} must contain price-quantity pairs")
        levels.append(BTCBookLevel(price=item[0], quantity=item[1]))
    return tuple(levels)


def _header(
    row: Mapping[str, object],
    profile: BTCLocalExportProfile,
    artifact_id: str,
) -> BTCObservationHeader:
    return BTCObservationHeader(
        observation_id=str(_value(row, profile, "observation_id")),
        artifact_id=artifact_id,
        venue_id=str(_value(row, profile, "venue_id")),
        instrument_id=str(_value(row, profile, "instrument_id")),
        instrument_kind=str(_value(row, profile, "instrument_kind")),
        observation_kind=str(_value(row, profile, "observation_kind")),
        source_sequence=_integer(_value(row, profile, "source_sequence"), "source_sequence"),
        event_at_utc=str(_value(row, profile, "event_at_utc")),
        received_at_utc=str(_value(row, profile, "received_at_utc")),
        ingested_at_utc=str(_value(row, profile, "ingested_at_utc")),
    )


def _observation(
    row: Mapping[str, object],
    profile: BTCLocalExportProfile,
    artifact_id: str,
) -> BTCObservation:
    header = _header(row, profile, artifact_id)
    kind = header.observation_kind
    if kind == "TRADE":
        return BTCTradeObservation(
            header=header,
            price=_value(row, profile, "price"),
            quantity=_value(row, profile, "quantity"),
            aggressor_side=str(_value(row, profile, "aggressor_side")),
        )
    if kind == "BOOK_SNAPSHOT":
        return BTCBookSnapshot(
            header=header,
            bids=_levels(_value(row, profile, "bids"), "bids"),
            asks=_levels(_value(row, profile, "asks"), "asks"),
        )
    if kind == "BOOK_DELTA":
        return BTCBookDelta(
            header=header,
            previous_sequence=_integer(
                _value(row, profile, "previous_sequence"), "previous_sequence"
            ),
            bid_updates=_levels(_value(row, profile, "bid_updates"), "bid_updates"),
            ask_updates=_levels(_value(row, profile, "ask_updates"), "ask_updates"),
        )
    if kind == "REFERENCE_PRICE":
        return BTCReferencePriceObservation(
            header=header,
            mark_price=_value(row, profile, "mark_price"),
            index_price=_value(row, profile, "index_price"),
        )
    if kind == "FUNDING":
        return BTCFundingObservation(
            header=header,
            funding_rate=_value(row, profile, "funding_rate"),
            interval_start_utc=str(_value(row, profile, "interval_start_utc")),
            interval_end_utc=str(_value(row, profile, "interval_end_utc")),
        )
    raise ValueError("source observation kind is not registered")


def _canonical_row(observation: BTCObservation) -> dict[str, object]:
    header = observation.header
    result: dict[str, object] = {
        "artifact_id": header.artifact_id,
        "event_at_utc": header.event_at_utc,
        "ingested_at_utc": header.ingested_at_utc,
        "instrument_id": header.instrument_id,
        "instrument_kind": header.instrument_kind,
        "observation_id": header.observation_id,
        "observation_kind": header.observation_kind,
        "received_at_utc": header.received_at_utc,
        "schema_version": header.schema_version,
        "source_sequence": header.source_sequence,
        "venue_id": header.venue_id,
    }
    if isinstance(observation, BTCTradeObservation):
        result.update(
            price=decimal_text(observation.price),
            quantity=decimal_text(observation.quantity),
            aggressor_side=observation.aggressor_side,
        )
    elif isinstance(observation, BTCBookSnapshot):
        result.update(
            bids=[[decimal_text(item.price), decimal_text(item.quantity)] for item in observation.bids],
            asks=[[decimal_text(item.price), decimal_text(item.quantity)] for item in observation.asks],
        )
    elif isinstance(observation, BTCBookDelta):
        result.update(
            previous_sequence=observation.previous_sequence,
            bid_updates=[[decimal_text(item.price), decimal_text(item.quantity)] for item in observation.bid_updates],
            ask_updates=[[decimal_text(item.price), decimal_text(item.quantity)] for item in observation.ask_updates],
        )
    elif isinstance(observation, BTCReferencePriceObservation):
        result.update(
            mark_price=decimal_text(observation.mark_price),
            index_price=decimal_text(observation.index_price),
        )
    elif isinstance(observation, BTCFundingObservation):
        result.update(
            funding_rate=decimal_text(observation.funding_rate),
            interval_start_utc=observation.interval_start_utc,
            interval_end_utc=observation.interval_end_utc,
        )
    return result


def canonicalize_registered_btc_local_export(
    file_path: Path,
    registration: RegisteredBTCLocalExport,
    profile: BTCLocalExportProfile,
    *,
    output_artifact_id: str,
    as_of_utc: str,
) -> BTCLocalExportBridgeResult:
    if not isinstance(registration, RegisteredBTCLocalExport):
        raise TypeError("registration must be RegisteredBTCLocalExport")
    if not isinstance(profile, BTCLocalExportProfile):
        raise TypeError("profile must be BTCLocalExportProfile")
    if registration.source_id != profile.source_id:
        raise ValueError("registration and profile source lineage disagree")
    raw = Path(file_path).read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered local export byte length mismatch")
    if hashlib.sha256(raw).hexdigest() != registration.content_sha256:
        raise ValueError("registered local export SHA-256 mismatch")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("registered local export must be UTF-8") from exc
    if text.startswith("\ufeff") or "\ufeff" in text:
        raise ValueError("registered local export cannot contain BOM markers")
    lines = text.splitlines()
    if not 1 <= len(lines) <= 10_000 or any(not line.strip() for line in lines):
        raise ValueError("registered local export row count is outside its bounded domain")
    rows: list[Mapping[str, object]] = []
    for line in lines:
        try:
            row = json.loads(line, parse_float=str)
        except json.JSONDecodeError as exc:
            raise ValueError("registered local export contains invalid NDJSON") from exc
        if not isinstance(row, dict):
            raise ValueError("registered local export rows must be JSON objects")
        rows.append(row)
    observations = tuple(
        _observation(row, profile, output_artifact_id) for row in rows
    )
    observation_ids = tuple(item.header.observation_id for item in observations)
    if len(observation_ids) != len(set(observation_ids)):
        raise ValueError("registered local export contains duplicate observation_id")
    as_of = instant(utc(as_of_utc, "as_of_utc"))
    if any(instant(item.header.ingested_at_utc) > as_of for item in observations):
        raise ValueError("registered local export contains future ingestion")
    canonical = b"".join(
        json.dumps(
            _canonical_row(item), ensure_ascii=True, separators=(",", ":"), sort_keys=True
        ).encode("ascii")
        + b"\n"
        for item in observations
    )
    canonical_hash = hashlib.sha256(canonical).hexdigest()
    canonical_registration = BTCRegisteredArtifact(
        artifact_id=output_artifact_id,
        content_sha256=canonical_hash,
        byte_length=len(canonical),
        rights=registration.rights,
    )
    manifest = BTCLocalExportBridgeManifest(
        source_artifact_id=registration.artifact_id,
        source_artifact_sha256=registration.content_sha256,
        canonical_artifact_id=output_artifact_id,
        canonical_artifact_sha256=canonical_hash,
        profile_hash=profile.profile_hash,
        observation_hashes=tuple(item.observation_hash for item in observations),
        as_of_utc=as_of_utc,
    )
    return BTCLocalExportBridgeResult(
        canonical_ndjson=canonical,
        canonical_registration=canonical_registration,
        observations=observations,
        manifest=manifest,
    )
