from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    LocalEventRights,
    identifier,
    instant,
    utc,
)


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
INSTRUMENT_KINDS = ("SPOT", "PERPETUAL")
OBSERVATION_KINDS = (
    "TRADE",
    "BOOK_SNAPSHOT",
    "BOOK_DELTA",
    "REFERENCE_PRICE",
    "FUNDING",
)


def exact_decimal(value: object, name: str, *, allow_zero: bool = True) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must use an exact decimal value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite() or result < 0 or (not allow_zero and result == 0):
        qualifier = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{name} must be finite and {qualifier}")
    return result


def decimal_text(value: Decimal) -> str:
    normalized = value.normalize()
    if normalized == 0:
        return "0"
    return format(normalized, "f")


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class BTCRegisteredArtifact:
    artifact_id: str
    content_sha256: str
    byte_length: int
    rights: LocalEventRights
    media_type: str = "application/x-ndjson"
    market: str = "BTC"
    operator_registered: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        digest = str(self.content_sha256).strip().lower()
        if _SHA256.fullmatch(digest) is None:
            raise ValueError("content_sha256 must be lowercase SHA-256")
        object.__setattr__(self, "content_sha256", digest)
        if isinstance(self.byte_length, bool) or self.byte_length <= 0:
            raise ValueError("byte_length must be positive")
        if not isinstance(self.rights, LocalEventRights):
            raise ValueError("artifact requires explicit registered local rights")
        if self.media_type != "application/x-ndjson" or self.market != "BTC":
            raise ValueError("artifact must use the closed BTC NDJSON contract")
        if self.operator_registered is not True:
            raise ValueError("artifact requires Operator registration")


@dataclass(frozen=True)
class BTCObservationHeader:
    observation_id: str
    artifact_id: str
    venue_id: str
    instrument_id: str
    instrument_kind: str
    observation_kind: str
    source_sequence: int
    event_at_utc: str
    received_at_utc: str
    ingested_at_utc: str
    schema_version: int = 1
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("observation_id", "artifact_id", "venue_id", "instrument_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        instrument_kind = str(self.instrument_kind).strip().upper()
        observation_kind = str(self.observation_kind).strip().upper()
        if instrument_kind not in INSTRUMENT_KINDS:
            raise ValueError("instrument_kind is not registered")
        if observation_kind not in OBSERVATION_KINDS:
            raise ValueError("observation_kind is not registered")
        object.__setattr__(self, "instrument_kind", instrument_kind)
        object.__setattr__(self, "observation_kind", observation_kind)
        if isinstance(self.source_sequence, bool) or self.source_sequence <= 0:
            raise ValueError("source_sequence must be positive")
        if isinstance(self.schema_version, bool) or self.schema_version <= 0:
            raise ValueError("schema_version must be positive")
        for name in ("event_at_utc", "received_at_utc", "ingested_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if not (
            instant(self.event_at_utc)
            <= instant(self.received_at_utc)
            <= instant(self.ingested_at_utc)
        ):
            raise ValueError("event, receive, and ingest clocks must be ordered")
        object.__setattr__(
            self,
            "record_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact_id,
                    "event_at_utc": self.event_at_utc,
                    "ingested_at_utc": self.ingested_at_utc,
                    "instrument_id": self.instrument_id,
                    "instrument_kind": self.instrument_kind,
                    "observation_id": self.observation_id,
                    "observation_kind": self.observation_kind,
                    "received_at_utc": self.received_at_utc,
                    "schema_version": self.schema_version,
                    "source_sequence": self.source_sequence,
                    "venue_id": self.venue_id,
                }
            ),
        )


def _require_kind(header: BTCObservationHeader, expected: str) -> None:
    if not isinstance(header, BTCObservationHeader) or header.observation_kind != expected:
        raise ValueError(f"header must declare {expected}")


@dataclass(frozen=True)
class BTCBookLevel:
    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        object.__setattr__(self, "price", exact_decimal(self.price, "price", allow_zero=False))
        object.__setattr__(self, "quantity", exact_decimal(self.quantity, "quantity"))


def _levels(
    values: tuple[BTCBookLevel, ...],
    name: str,
    *,
    allow_zero: bool,
    allow_empty: bool = False,
) -> tuple[BTCBookLevel, ...]:
    levels = tuple(values)
    if not levels and allow_empty:
        return ()
    if not levels or not all(isinstance(level, BTCBookLevel) for level in levels):
        raise ValueError(f"{name} must contain typed book levels")
    if len({level.price for level in levels}) != len(levels):
        raise ValueError(f"{name} prices must be unique")
    if not allow_zero and any(level.quantity == 0 for level in levels):
        raise ValueError(f"{name} snapshot quantity must be positive")
    return levels


@dataclass(frozen=True)
class BTCTradeObservation:
    header: BTCObservationHeader
    price: Decimal
    quantity: Decimal
    aggressor_side: str
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        _require_kind(self.header, "TRADE")
        object.__setattr__(self, "price", exact_decimal(self.price, "price", allow_zero=False))
        object.__setattr__(
            self, "quantity", exact_decimal(self.quantity, "quantity", allow_zero=False)
        )
        side = str(self.aggressor_side).strip().upper()
        if side not in {"BUY", "SELL", "UNKNOWN"}:
            raise ValueError("aggressor_side is not registered")
        object.__setattr__(self, "aggressor_side", side)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "aggressor_side": side,
                    "header_hash": self.header.record_hash,
                    "price": decimal_text(self.price),
                    "quantity": decimal_text(self.quantity),
                }
            ),
        )


@dataclass(frozen=True)
class BTCBookSnapshot:
    header: BTCObservationHeader
    bids: tuple[BTCBookLevel, ...]
    asks: tuple[BTCBookLevel, ...]
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        _require_kind(self.header, "BOOK_SNAPSHOT")
        bids = _levels(self.bids, "bids", allow_zero=False)
        asks = _levels(self.asks, "asks", allow_zero=False)
        if tuple(sorted(bids, key=lambda item: item.price, reverse=True)) != bids:
            raise ValueError("snapshot bids must be strictly price-descending")
        if tuple(sorted(asks, key=lambda item: item.price)) != asks:
            raise ValueError("snapshot asks must be strictly price-ascending")
        if bids[0].price >= asks[0].price:
            raise ValueError("snapshot order book is crossed or locked")
        object.__setattr__(self, "bids", bids)
        object.__setattr__(self, "asks", asks)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "asks": [(decimal_text(x.price), decimal_text(x.quantity)) for x in asks],
                    "bids": [(decimal_text(x.price), decimal_text(x.quantity)) for x in bids],
                    "header_hash": self.header.record_hash,
                }
            ),
        )


@dataclass(frozen=True)
class BTCBookDelta:
    header: BTCObservationHeader
    previous_sequence: int
    bid_updates: tuple[BTCBookLevel, ...]
    ask_updates: tuple[BTCBookLevel, ...]
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        _require_kind(self.header, "BOOK_DELTA")
        if isinstance(self.previous_sequence, bool) or self.previous_sequence <= 0:
            raise ValueError("previous_sequence must be positive")
        if self.previous_sequence >= self.header.source_sequence:
            raise ValueError("delta sequence must follow previous_sequence")
        bids = _levels(
            self.bid_updates, "bid_updates", allow_zero=True, allow_empty=True
        )
        asks = _levels(
            self.ask_updates, "ask_updates", allow_zero=True, allow_empty=True
        )
        if not bids and not asks:
            raise ValueError("book delta must update at least one side")
        object.__setattr__(self, "bid_updates", bids)
        object.__setattr__(self, "ask_updates", asks)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "ask_updates": [(decimal_text(x.price), decimal_text(x.quantity)) for x in asks],
                    "bid_updates": [(decimal_text(x.price), decimal_text(x.quantity)) for x in bids],
                    "header_hash": self.header.record_hash,
                    "previous_sequence": self.previous_sequence,
                }
            ),
        )


@dataclass(frozen=True)
class BTCReferencePriceObservation:
    header: BTCObservationHeader
    mark_price: Decimal
    index_price: Decimal
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        _require_kind(self.header, "REFERENCE_PRICE")
        if self.header.instrument_kind != "PERPETUAL":
            raise ValueError("reference prices require a perpetual instrument")
        object.__setattr__(
            self, "mark_price", exact_decimal(self.mark_price, "mark_price", allow_zero=False)
        )
        object.__setattr__(
            self, "index_price", exact_decimal(self.index_price, "index_price", allow_zero=False)
        )
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "header_hash": self.header.record_hash,
                    "index_price": decimal_text(self.index_price),
                    "mark_price": decimal_text(self.mark_price),
                }
            ),
        )


@dataclass(frozen=True)
class BTCFundingObservation:
    header: BTCObservationHeader
    funding_rate: Decimal
    interval_start_utc: str
    interval_end_utc: str
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        _require_kind(self.header, "FUNDING")
        if self.header.instrument_kind != "PERPETUAL":
            raise ValueError("funding requires a perpetual instrument")
        if isinstance(self.funding_rate, bool) or isinstance(self.funding_rate, float):
            raise ValueError("funding_rate must use an exact decimal value")
        try:
            rate = Decimal(str(self.funding_rate))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("funding_rate must be decimal-compatible") from exc
        if not rate.is_finite():
            raise ValueError("funding_rate must be finite")
        object.__setattr__(self, "funding_rate", rate)
        start = utc(self.interval_start_utc, "interval_start_utc")
        end = utc(self.interval_end_utc, "interval_end_utc")
        if instant(end) <= instant(start):
            raise ValueError("funding interval end must follow start")
        if not instant(start) <= instant(self.header.event_at_utc) <= instant(end):
            raise ValueError("funding event must fall inside its declared interval")
        object.__setattr__(self, "interval_start_utc", start)
        object.__setattr__(self, "interval_end_utc", end)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "funding_rate": decimal_text(rate),
                    "header_hash": self.header.record_hash,
                    "interval_end_utc": end,
                    "interval_start_utc": start,
                }
            ),
        )


BTCObservation = (
    BTCTradeObservation
    | BTCBookSnapshot
    | BTCBookDelta
    | BTCReferencePriceObservation
    | BTCFundingObservation
)
