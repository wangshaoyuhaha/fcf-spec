from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from decimal import Decimal

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import (
    BTCBookDelta,
    BTCBookLevel,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCObservation,
    BTCReferencePriceObservation,
    BTCRegisteredArtifact,
    BTCTradeObservation,
    canonical_sha256,
    decimal_text,
)


@dataclass(frozen=True)
class BTCReplayFinding:
    code: str
    severity: str
    observation_id: str
    detail: str
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.severity not in {"INFO", "WARNING", "BLOCKING"}:
            raise ValueError("finding severity is not registered")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain required")


@dataclass(frozen=True)
class BTCBookState:
    venue_id: str
    instrument_id: str
    last_sequence: int
    bids: tuple[BTCBookLevel, ...]
    asks: tuple[BTCBookLevel, ...]
    sync_state: str
    generation: int
    state_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.sync_state not in {"SYNCED", "RESYNC_REQUIRED"}:
            raise ValueError("sync_state is not registered")
        if self.last_sequence < 0 or self.generation < 0:
            raise ValueError("book sequence and generation must be nonnegative")
        object.__setattr__(
            self,
            "state_hash",
            canonical_sha256(
                {
                    "asks": [(decimal_text(x.price), decimal_text(x.quantity)) for x in self.asks],
                    "bids": [(decimal_text(x.price), decimal_text(x.quantity)) for x in self.bids],
                    "generation": self.generation,
                    "instrument_id": self.instrument_id,
                    "last_sequence": self.last_sequence,
                    "sync_state": self.sync_state,
                    "venue_id": self.venue_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCReplayManifest:
    artifact_id: str
    artifact_sha256: str
    observation_hashes: tuple[str, ...]
    book_state_hash: str
    replayed_at_utc: str
    layer: str = "NORMALIZED_REPLAY"
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        replayed = utc(self.replayed_at_utc, "replayed_at_utc")
        object.__setattr__(self, "replayed_at_utc", replayed)
        object.__setattr__(
            self,
            "manifest_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact_id,
                    "artifact_sha256": self.artifact_sha256,
                    "book_state_hash": self.book_state_hash,
                    "layer": self.layer,
                    "observation_hashes": self.observation_hashes,
                    "replayed_at_utc": replayed,
                }
            ),
        )


@dataclass(frozen=True)
class BTCReplayReport:
    book_state: BTCBookState
    accepted_observation_ids: tuple[str, ...]
    findings: tuple[BTCReplayFinding, ...]
    manifest: BTCReplayManifest
    latest_trade: BTCTradeObservation | None
    latest_reference_price: BTCReferencePriceObservation | None
    latest_funding: BTCFundingObservation | None
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    operator_review_required: bool = True

    @property
    def ready(self) -> bool:
        return self.book_state.sync_state == "SYNCED" and not any(
            item.severity == "BLOCKING" for item in self.findings
        )


def _apply_updates(
    current: tuple[BTCBookLevel, ...],
    updates: tuple[BTCBookLevel, ...],
    *,
    reverse: bool,
) -> tuple[BTCBookLevel, ...]:
    values = {item.price: item.quantity for item in current}
    for item in updates:
        if item.quantity == 0:
            values.pop(item.price, None)
        else:
            values[item.price] = item.quantity
    return tuple(
        BTCBookLevel(price=price, quantity=quantity)
        for price, quantity in sorted(values.items(), reverse=reverse)
    )


def _blocked(code: str, observation_id: str, detail: str) -> BTCReplayFinding:
    return BTCReplayFinding(
        code=code,
        severity="BLOCKING",
        observation_id=observation_id,
        detail=detail,
    )


@dataclass(frozen=True)
class BTCMarketReplay:
    max_age_seconds: int = 30
    mark_index_divergence_bps: int = 100

    def __post_init__(self) -> None:
        if self.max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be positive")
        if not 0 < self.mark_index_divergence_bps <= 10000:
            raise ValueError("mark_index_divergence_bps must be in range")

    def replay(
        self,
        artifact: BTCRegisteredArtifact,
        artifact_content: bytes,
        observations: tuple[BTCObservation, ...],
        *,
        as_of_utc: str,
    ) -> BTCReplayReport:
        if not isinstance(artifact, BTCRegisteredArtifact):
            raise ValueError("artifact must be registered")
        if not isinstance(artifact_content, bytes):
            raise ValueError("artifact_content must be exact bytes")
        try:
            artifact_content.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError("registered BTC artifact must be ASCII") from exc
        if len(artifact_content) != artifact.byte_length:
            raise ValueError("registered artifact byte length mismatch")
        digest = hashlib.sha256(artifact_content).hexdigest()
        if digest != artifact.content_sha256:
            raise ValueError("registered artifact SHA-256 mismatch")
        events = tuple(observations)
        if not events:
            raise ValueError("at least one registered BTC observation is required")
        as_of = instant(utc(as_of_utc, "as_of_utc"))
        venue_ids = {item.header.venue_id for item in events}
        instrument_ids = {item.header.instrument_id for item in events}
        instrument_kinds = {item.header.instrument_kind for item in events}
        if len(venue_ids) != 1 or len(instrument_ids) != 1 or len(instrument_kinds) != 1:
            raise ValueError("one replay bundle must isolate one venue and instrument")
        if any(item.header.artifact_id != artifact.artifact_id for item in events):
            raise ValueError("observation artifact lineage mismatch")
        if len({item.header.observation_id for item in events}) != len(events):
            raise ValueError("duplicate observation_id is prohibited")
        if any(instant(item.header.ingested_at_utc) > as_of for item in events):
            raise ValueError("future ingestion is prohibited")

        venue_id = next(iter(venue_ids))
        instrument_id = next(iter(instrument_ids))
        instrument_kind = next(iter(instrument_kinds))
        book = BTCBookState(venue_id, instrument_id, 0, (), (), "RESYNC_REQUIRED", 0)
        findings: list[BTCReplayFinding] = []
        accepted: list[BTCObservation] = []
        latest_trade: BTCTradeObservation | None = None
        latest_reference: BTCReferencePriceObservation | None = None
        latest_funding: BTCFundingObservation | None = None

        for event in events:
            header = event.header
            if isinstance(event, BTCBookSnapshot):
                book = BTCBookState(
                    venue_id,
                    instrument_id,
                    header.source_sequence,
                    event.bids,
                    event.asks,
                    "SYNCED",
                    book.generation + 1,
                )
                accepted.append(event)
            elif isinstance(event, BTCBookDelta):
                if book.sync_state != "SYNCED":
                    findings.append(
                        _blocked(
                            "BOOK_DELTA_WITHOUT_SYNCED_SNAPSHOT",
                            header.observation_id,
                            "delta ignored until a registered snapshot resynchronizes the book",
                        )
                    )
                    continue
                if (
                    event.previous_sequence != book.last_sequence
                    or header.source_sequence != book.last_sequence + 1
                ):
                    findings.append(
                        _blocked(
                            "SEQUENCE_GAP_RESYNC_REQUIRED",
                            header.observation_id,
                            "book frozen until a later registered snapshot",
                        )
                    )
                    book = BTCBookState(
                        venue_id,
                        instrument_id,
                        book.last_sequence,
                        book.bids,
                        book.asks,
                        "RESYNC_REQUIRED",
                        book.generation,
                    )
                    continue
                bids = _apply_updates(book.bids, event.bid_updates, reverse=True)
                asks = _apply_updates(book.asks, event.ask_updates, reverse=False)
                if not bids or not asks or bids[0].price >= asks[0].price:
                    findings.append(
                        _blocked(
                            "CROSSED_OR_EMPTY_BOOK_RESYNC_REQUIRED",
                            header.observation_id,
                            "invalid delta ignored and book frozen for resynchronization",
                        )
                    )
                    book = BTCBookState(
                        venue_id,
                        instrument_id,
                        book.last_sequence,
                        book.bids,
                        book.asks,
                        "RESYNC_REQUIRED",
                        book.generation,
                    )
                    continue
                book = BTCBookState(
                    venue_id,
                    instrument_id,
                    header.source_sequence,
                    bids,
                    asks,
                    "SYNCED",
                    book.generation,
                )
                accepted.append(event)
            elif isinstance(event, BTCTradeObservation):
                latest_trade = event
                accepted.append(event)
            elif isinstance(event, BTCReferencePriceObservation):
                latest_reference = event
                accepted.append(event)
            elif isinstance(event, BTCFundingObservation):
                latest_funding = event
                accepted.append(event)
            else:
                raise ValueError("observation type is not registered")

        latest_by_kind = {
            "TRADE": latest_trade,
            "BOOK": next(
                (item for item in reversed(accepted) if isinstance(item, (BTCBookSnapshot, BTCBookDelta))),
                None,
            ),
            "REFERENCE_PRICE": latest_reference,
            "FUNDING": latest_funding,
        }
        required = ("TRADE", "BOOK")
        if instrument_kind == "PERPETUAL":
            required += ("REFERENCE_PRICE", "FUNDING")
        for kind in required:
            event = latest_by_kind[kind]
            if event is None:
                findings.append(_blocked(f"{kind}_STREAM_MISSING", "NONE", "required BTC stream is absent"))
                continue
            age = (as_of - instant(event.header.received_at_utc)).total_seconds()
            if age > self.max_age_seconds:
                findings.append(_blocked(f"{kind}_STREAM_STALE", event.header.observation_id, "stream exceeds the configured 24x7 freshness bound"))

        if latest_reference is not None:
            divergence = (
                abs(latest_reference.mark_price - latest_reference.index_price)
                / latest_reference.index_price
                * Decimal("10000")
            )
            if divergence > self.mark_index_divergence_bps:
                findings.append(
                    _blocked(
                        "MARK_INDEX_DIVERGENCE",
                        latest_reference.header.observation_id,
                        f"mark/index divergence is {decimal_text(divergence)} bps",
                    )
                )

        manifest = BTCReplayManifest(
            artifact_id=artifact.artifact_id,
            artifact_sha256=artifact.content_sha256,
            observation_hashes=tuple(item.observation_hash for item in accepted),
            book_state_hash=book.state_hash,
            replayed_at_utc=as_of_utc,
        )
        return BTCReplayReport(
            book_state=book,
            accepted_observation_ids=tuple(item.header.observation_id for item in accepted),
            findings=tuple(findings),
            manifest=manifest,
            latest_trade=latest_trade,
            latest_reference_price=latest_reference,
            latest_funding=latest_funding,
        )
