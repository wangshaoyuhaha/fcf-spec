from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from types import MappingProxyType
from typing import Mapping


PHASE_ID = (
    "FCF-FCP-0106-A-SHARE-QMT-INTERNAL-READ-ONLY-MARKET-BRIDGE-APP-1"
)
BRIDGE_ID = "fcf-qmt-internal-read-only-market-bridge-v1"
SCHEMA_VERSION = "fcf-qmt-quote-v1"
SOURCE_KIND = "GUOJIN_QMT_INTERNAL_QUOTE"
SYMBOL = re.compile(r"^[0-9]{6}\.(?:SH|SZ|BJ)$")
DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EVENT_FIELDS = (
    "amount_cny",
    "bridge_id",
    "event_hash",
    "event_time_ms",
    "high",
    "last",
    "low",
    "open",
    "previous_close",
    "received_at_ms",
    "schema_version",
    "sequence",
    "source_kind",
    "symbol",
    "volume_native",
    "volume_unit",
)


def canonical_bytes(payload: Mapping[str, object]) -> bytes:
    return json.dumps(
        dict(payload),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def digest(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _decimal_text(
    value: str,
    name: str,
    *,
    positive: bool,
) -> str:
    if not isinstance(value, str) or not DECIMAL.fullmatch(value):
        raise ValueError(f"{name} must be canonical non-negative decimal text")
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{name} must be decimal text") from exc
    if not parsed.is_finite() or parsed < 0 or (positive and parsed <= 0):
        raise ValueError(f"{name} is outside the registered range")
    return value


@dataclass(frozen=True)
class QmtInternalBridgeRegistration:
    bridge_id: str = BRIDGE_ID
    schema_version: str = SCHEMA_VERSION
    source_kind: str = SOURCE_KIND
    allowed_symbols: tuple[str, ...] = ("600000.SH",)
    max_event_age_ms: int = 10_000
    max_future_skew_ms: int = 2_000
    max_event_bytes: int = 4096
    max_batch_files: int = 1024

    def __post_init__(self) -> None:
        if type(self.allowed_symbols) is not tuple:
            raise ValueError("allowed_symbols must be an exact tuple")
        if (
            not 1 <= len(self.allowed_symbols) <= 64
            or any(
                not isinstance(item, str) or not SYMBOL.fullmatch(item)
                for item in self.allowed_symbols
            )
        ):
            raise ValueError("allowed_symbols is outside the closed contract registry")
        exact = (
            self.bridge_id == BRIDGE_ID,
            self.schema_version == SCHEMA_VERSION,
            self.source_kind == SOURCE_KIND,
            self.allowed_symbols == tuple(sorted(set(self.allowed_symbols))),
            type(self.max_event_age_ms) is int,
            1_000 <= self.max_event_age_ms <= 60_000,
            type(self.max_future_skew_ms) is int,
            0 <= self.max_future_skew_ms <= 5_000,
            type(self.max_event_bytes) is int,
            512 <= self.max_event_bytes <= 16_384,
            type(self.max_batch_files) is int,
            1 <= self.max_batch_files <= 4096,
        )
        if not all(exact):
            raise ValueError("bridge registration is outside the closed contract")

    def payload(self) -> dict[str, object]:
        return {
            "allowed_symbols": list(self.allowed_symbols),
            "bridge_id": self.bridge_id,
            "max_batch_files": self.max_batch_files,
            "max_event_age_ms": self.max_event_age_ms,
            "max_event_bytes": self.max_event_bytes,
            "max_future_skew_ms": self.max_future_skew_ms,
            "schema_version": self.schema_version,
            "source_kind": self.source_kind,
        }

    @property
    def registration_hash(self) -> str:
        return digest(self.payload())


DEFAULT_REGISTRATION = QmtInternalBridgeRegistration()


@dataclass(frozen=True)
class QmtQuoteEvent:
    amount_cny: str
    bridge_id: str
    event_hash: str
    event_time_ms: int
    high: str
    last: str
    low: str
    open: str
    previous_close: str
    received_at_ms: int
    schema_version: str
    sequence: int
    source_kind: str
    symbol: str
    volume_native: str
    volume_unit: str

    def __post_init__(self) -> None:
        exact = (
            self.bridge_id == BRIDGE_ID,
            self.schema_version == SCHEMA_VERSION,
            self.source_kind == SOURCE_KIND,
            isinstance(self.symbol, str) and bool(SYMBOL.fullmatch(self.symbol)),
            type(self.event_time_ms) is int and self.event_time_ms > 0,
            type(self.received_at_ms) is int and self.received_at_ms > 0,
            type(self.sequence) is int and self.sequence > 0,
            self.volume_unit == "QMT_NATIVE_UNCALIBRATED",
            isinstance(self.event_hash, str)
            and bool(SHA256.fullmatch(self.event_hash)),
        )
        if not all(exact):
            raise ValueError("quote event identity is outside the closed contract")
        for name in ("open", "high", "low", "last", "previous_close"):
            _decimal_text(getattr(self, name), name, positive=True)
        _decimal_text(self.volume_native, "volume_native", positive=False)
        _decimal_text(self.amount_cny, "amount_cny", positive=False)
        prices = tuple(
            Decimal(value)
            for value in (
                self.open,
                self.high,
                self.low,
                self.last,
            )
        )
        if prices[2] > min(prices[0], prices[3]):
            raise ValueError("low exceeds open or last")
        if prices[1] < max(prices[0], prices[3]):
            raise ValueError("high is below open or last")
        if self.event_hash != digest(self.payload_without_hash()):
            raise ValueError("event_hash does not match the event payload")

    def payload_without_hash(self) -> dict[str, object]:
        return {
            "amount_cny": self.amount_cny,
            "bridge_id": self.bridge_id,
            "event_time_ms": self.event_time_ms,
            "high": self.high,
            "last": self.last,
            "low": self.low,
            "open": self.open,
            "previous_close": self.previous_close,
            "received_at_ms": self.received_at_ms,
            "schema_version": self.schema_version,
            "sequence": self.sequence,
            "source_kind": self.source_kind,
            "symbol": self.symbol,
            "volume_native": self.volume_native,
            "volume_unit": self.volume_unit,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_hash(), "event_hash": self.event_hash}


@dataclass(frozen=True)
class QmtBridgeIngestState:
    last_sequences: Mapping[str, int]
    event_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.last_sequences, Mapping):
            raise ValueError("last_sequences must be an exact mapping")
        sequences = dict(self.last_sequences)
        if type(self.event_hashes) is not tuple:
            raise ValueError("event_hashes must be an exact tuple")
        if any(
            not isinstance(symbol, str)
            or not SYMBOL.fullmatch(symbol)
            or type(sequence) is not int
            or sequence <= 0
            for symbol, sequence in sequences.items()
        ):
            raise ValueError("last_sequences is invalid")
        if tuple(sequences) != tuple(sorted(sequences)):
            raise ValueError("last_sequences must be sorted")
        if (
            len(set(self.event_hashes)) != len(self.event_hashes)
            or any(
                not isinstance(item, str) or not SHA256.fullmatch(item)
                for item in self.event_hashes
            )
        ):
            raise ValueError("event_hashes must be unique SHA-256 values")
        object.__setattr__(self, "last_sequences", MappingProxyType(sequences))


EMPTY_INGEST_STATE = QmtBridgeIngestState(
    last_sequences=MappingProxyType({}),
    event_hashes=(),
)


@dataclass(frozen=True)
class QmtBridgeBatchSnapshot:
    registration_hash: str
    accepted_events: tuple[QmtQuoteEvent, ...]
    state: QmtBridgeIngestState
    latest_received_at_ms: int
    bridge_state: str
    operator_review_required: bool
    read_only: bool
    market_data_authority: bool
    data_promotion_authority: bool
    account_authority: bool
    execution_authority: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        if not isinstance(self.registration_hash, str) or not SHA256.fullmatch(
            self.registration_hash
        ):
            raise ValueError("registration_hash must be SHA-256")
        if type(self.accepted_events) is not tuple or any(
            type(item) is not QmtQuoteEvent for item in self.accepted_events
        ):
            raise ValueError("accepted_events must be an exact event tuple")
        if not self.accepted_events:
            raise ValueError("accepted_events cannot be empty")
        if type(self.state) is not QmtBridgeIngestState:
            raise ValueError("state must be an exact ingest state")
        if type(self.latest_received_at_ms) is not int:
            raise ValueError("latest_received_at_ms must be an exact integer")
        if self.latest_received_at_ms != max(
            item.received_at_ms for item in self.accepted_events
        ):
            raise ValueError("latest_received_at_ms does not match the batch")
        if self.bridge_state != "CANDIDATE_REALTIME_OBSERVED":
            raise ValueError("bridge_state is not registered")
        authority_flags = (
            self.operator_review_required,
            self.read_only,
            self.market_data_authority,
            self.data_promotion_authority,
            self.account_authority,
            self.execution_authority,
        )
        if any(type(value) is not bool for value in authority_flags):
            raise ValueError("snapshot authority flags must be exact booleans")
        if not self.operator_review_required or not self.read_only:
            raise ValueError("Operator review and read-only state are mandatory")
        if any(
            (
                self.market_data_authority,
                self.data_promotion_authority,
                self.account_authority,
                self.execution_authority,
            )
        ):
            raise ValueError("bridge snapshot cannot grant authority")
        if not isinstance(self.snapshot_hash, str) or not SHA256.fullmatch(
            self.snapshot_hash
        ):
            raise ValueError("snapshot_hash must be SHA-256")
        if self.snapshot_hash != digest(self.payload_without_hash()):
            raise ValueError("snapshot_hash does not match the snapshot")

    def payload_without_hash(self) -> dict[str, object]:
        return {
            "accepted_event_hashes": [
                item.event_hash for item in self.accepted_events
            ],
            "account_authority": self.account_authority,
            "bridge_state": self.bridge_state,
            "data_promotion_authority": self.data_promotion_authority,
            "execution_authority": self.execution_authority,
            "latest_received_at_ms": self.latest_received_at_ms,
            "market_data_authority": self.market_data_authority,
            "operator_review_required": self.operator_review_required,
            "read_only": self.read_only,
            "registration_hash": self.registration_hash,
            "state_event_hashes": list(self.state.event_hashes),
            "state_last_sequences": dict(self.state.last_sequences),
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_hash(), "snapshot_hash": self.snapshot_hash}
