from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCRegisteredArtifact,
)
from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    BTCBookDelta,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCObservation,
    BTCReferencePriceObservation,
    BTCTradeObservation,
    decimal_text,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


COMMON_FIELDS = (
    "observation_id",
    "venue_id",
    "instrument_id",
    "instrument_kind",
    "observation_kind",
    "source_sequence",
    "event_at_utc",
    "received_at_utc",
    "ingested_at_utc",
)
KIND_FIELDS = {
    "TRADE": ("price", "quantity", "aggressor_side"),
    "BOOK_SNAPSHOT": ("bids", "asks"),
    "BOOK_DELTA": ("previous_sequence", "bid_updates", "ask_updates"),
    "REFERENCE_PRICE": ("mark_price", "index_price"),
    "FUNDING": ("funding_rate", "interval_start_utc", "interval_end_utc"),
}
BTC_OBSERVATION_TYPES = (
    BTCTradeObservation,
    BTCBookSnapshot,
    BTCBookDelta,
    BTCReferencePriceObservation,
    BTCFundingObservation,
)


def _canonical_observation_row(observation: BTCObservation) -> dict[str, object]:
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
            bids=[
                [decimal_text(item.price), decimal_text(item.quantity)]
                for item in observation.bids
            ],
            asks=[
                [decimal_text(item.price), decimal_text(item.quantity)]
                for item in observation.asks
            ],
        )
    elif isinstance(observation, BTCBookDelta):
        result.update(
            previous_sequence=observation.previous_sequence,
            bid_updates=[
                [decimal_text(item.price), decimal_text(item.quantity)]
                for item in observation.bid_updates
            ],
            ask_updates=[
                [decimal_text(item.price), decimal_text(item.quantity)]
                for item in observation.ask_updates
            ],
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


def canonical_observations_ndjson(observations: tuple[BTCObservation, ...]) -> bytes:
    return b"".join(
        json.dumps(
            _canonical_observation_row(item),
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        + b"\n"
        for item in observations
    )
CANONICAL_EXPORT_FIELDS = COMMON_FIELDS + tuple(
    field_name for fields in KIND_FIELDS.values() for field_name in fields
)


def _sha256(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be lowercase SHA-256")
    result = value
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return result


def _canonical_sha256(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
            "ascii"
        )
    ).hexdigest()


def _source_field(value: object) -> str:
    result = str(value).strip()
    if not result or len(result) > 160 or any(ord(character) < 33 or ord(character) > 126 for character in result):
        raise ValueError("source field names must be visible ASCII")
    return result


@dataclass(frozen=True)
class RegisteredBTCLocalExport:
    artifact_id: str
    source_id: str
    content_sha256: str
    byte_length: int
    registered_at_utc: str
    rights: LocalEventRights
    media_type: str = "application/x-ndjson"
    operator_registered: bool = True
    local_only: bool = True
    raw_repository_storage_allowed: bool = False
    provider_selected: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(self, "content_sha256", _sha256(self.content_sha256, "content_sha256"))
        if (
            isinstance(self.byte_length, bool)
            or not isinstance(self.byte_length, int)
            or not 1 <= self.byte_length <= 25_000_000
        ):
            raise ValueError("byte_length exceeds the bounded local export limit")
        object.__setattr__(
            self, "registered_at_utc", utc(self.registered_at_utc, "registered_at_utc")
        )
        if not isinstance(self.rights, LocalEventRights):
            raise ValueError("local export requires typed rights")
        if self.media_type != "application/x-ndjson":
            raise ValueError("local export must use registered NDJSON")
        if (
            self.operator_registered is not True
            or self.local_only is not True
            or self.raw_repository_storage_allowed is not False
            or self.provider_selected is not False
        ):
            raise ValueError("local export must remain registered-local and provider-unselected")


@dataclass(frozen=True)
class BTCLocalExportProfile:
    profile_id: str
    source_id: str
    canonical_to_source: Mapping[str, str]
    profile_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", identifier(self.profile_id, "profile_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        mapping = {
            identifier(key, "canonical field"): _source_field(value)
            for key, value in self.canonical_to_source.items()
        }
        if set(mapping) != set(CANONICAL_EXPORT_FIELDS):
            raise ValueError("profile must map the closed BTC local-export schema")
        if len(set(mapping.values())) != len(mapping):
            raise ValueError("source fields must map uniquely")
        object.__setattr__(self, "canonical_to_source", MappingProxyType(mapping))
        object.__setattr__(self, "profile_hash", _canonical_sha256(mapping))


@dataclass(frozen=True)
class BTCLocalExportBridgeManifest:
    source_artifact_id: str
    source_artifact_sha256: str
    canonical_artifact_id: str
    canonical_artifact_sha256: str
    profile_hash: str
    observation_hashes: tuple[str, ...]
    as_of_utc: str
    schema_version: str = "btc-market-ndjson-v1"
    operator_review_required: bool = True
    provider_selected: bool = False
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("source_artifact_id", "canonical_artifact_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in (
            "source_artifact_sha256",
            "canonical_artifact_sha256",
            "profile_hash",
        ):
            object.__setattr__(self, name, _sha256(getattr(self, name), name))
        hashes = tuple(_sha256(item, "observation_hash") for item in self.observation_hashes)
        if not hashes or len(hashes) != len(set(hashes)):
            raise ValueError("manifest requires unique observation hashes")
        if self.schema_version != "btc-market-ndjson-v1":
            raise ValueError("manifest schema is not registered")
        if (
            self.operator_review_required is not True
            or self.provider_selected is not False
        ):
            raise ValueError("manifest cannot bypass review or select a provider")
        object.__setattr__(self, "observation_hashes", hashes)
        object.__setattr__(self, "as_of_utc", utc(self.as_of_utc, "as_of_utc"))
        object.__setattr__(
            self,
            "manifest_hash",
            _canonical_sha256(
                {
                    "as_of_utc": self.as_of_utc,
                    "canonical_artifact_id": self.canonical_artifact_id,
                    "canonical_artifact_sha256": self.canonical_artifact_sha256,
                    "observation_hashes": hashes,
                    "profile_hash": self.profile_hash,
                    "schema_version": self.schema_version,
                    "source_artifact_id": self.source_artifact_id,
                    "source_artifact_sha256": self.source_artifact_sha256,
                }
            ),
        )


@dataclass(frozen=True)
class BTCLocalExportBridgeResult:
    canonical_ndjson: bytes
    canonical_registration: BTCRegisteredArtifact
    observations: tuple[BTCObservation, ...]
    manifest: BTCLocalExportBridgeManifest
    quality_state: str = "READY_FOR_REPLAY"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        if not isinstance(self.canonical_ndjson, bytes) or not self.canonical_ndjson:
            raise ValueError("bridge result requires canonical bytes")
        if not isinstance(self.canonical_registration, BTCRegisteredArtifact):
            raise ValueError("bridge result requires canonical registration")
        if not observations or not all(
            isinstance(item, BTC_OBSERVATION_TYPES) for item in observations
        ):
            raise ValueError("bridge result requires typed observations")
        if not isinstance(self.manifest, BTCLocalExportBridgeManifest):
            raise ValueError("bridge result requires a typed manifest")
        if self.quality_state != "READY_FOR_REPLAY" or self.operator_review_required is not True:
            raise ValueError("bridge result cannot bypass replay or Operator review")
        canonical_hash = hashlib.sha256(self.canonical_ndjson).hexdigest()
        if self.canonical_registration.content_sha256 != canonical_hash:
            raise ValueError("canonical registration digest disagrees with bytes")
        if self.canonical_registration.byte_length != len(self.canonical_ndjson):
            raise ValueError("canonical registration byte length disagrees with bytes")
        if self.manifest.canonical_artifact_id != self.canonical_registration.artifact_id:
            raise ValueError("bridge manifest canonical artifact identity disagrees")
        if self.manifest.canonical_artifact_sha256 != canonical_hash:
            raise ValueError("bridge manifest digest disagrees with canonical bytes")
        observation_hashes = tuple(item.observation_hash for item in observations)
        if self.manifest.observation_hashes != observation_hashes:
            raise ValueError("bridge manifest observation hashes disagree")
        if any(
            item.header.artifact_id != self.canonical_registration.artifact_id
            for item in observations
        ):
            raise ValueError("observation artifact lineage disagrees with registration")
        if canonical_observations_ndjson(observations) != self.canonical_ndjson:
            raise ValueError("canonical bytes disagree with typed observations")
        object.__setattr__(self, "observations", observations)
