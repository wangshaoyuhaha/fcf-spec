from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from decimal import Decimal

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)

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


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


@dataclass(frozen=True)
class BTCReplayFinding:
    code: str
    severity: str
    observation_id: str
    detail: str
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", identifier(self.code, "finding code"))
        object.__setattr__(
            self,
            "observation_id",
            identifier(self.observation_id, "finding observation_id"),
        )
        if not isinstance(self.detail, str) or not self.detail.strip():
            raise ValueError("finding detail must be nonempty text")
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
        object.__setattr__(self, "venue_id", identifier(self.venue_id, "venue_id"))
        object.__setattr__(
            self, "instrument_id", identifier(self.instrument_id, "instrument_id")
        )
        if self.sync_state not in {"SYNCED", "RESYNC_REQUIRED"}:
            raise ValueError("sync_state is not registered")
        if any(
            isinstance(item, bool) or not isinstance(item, int) or item < 0
            for item in (self.last_sequence, self.generation)
        ):
            raise ValueError("book sequence and generation must be nonnegative")
        bids = tuple(self.bids)
        asks = tuple(self.asks)
        if not all(isinstance(item, BTCBookLevel) for item in (*bids, *asks)):
            raise ValueError("book state requires typed levels")
        if bids != tuple(sorted(bids, key=lambda item: item.price, reverse=True)):
            raise ValueError("book bids must be deterministically descending")
        if asks != tuple(sorted(asks, key=lambda item: item.price)):
            raise ValueError("book asks must be deterministically ascending")
        if (bids and asks and bids[0].price >= asks[0].price) or (
            self.sync_state == "SYNCED" and (not bids or not asks)
        ):
            raise ValueError("book state must be noncrossed and complete when synced")
        object.__setattr__(self, "bids", bids)
        object.__setattr__(self, "asks", asks)
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
    observation_ids: tuple[str, ...]
    observation_hashes: tuple[str, ...]
    book_state_hash: str
    replayed_at_utc: str
    layer: str = "NORMALIZED_REPLAY"
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(
            self,
            "artifact_sha256",
            _digest(self.artifact_sha256, "artifact_sha256"),
        )
        observation_ids = tuple(
            identifier(item, "manifest observation_id") for item in self.observation_ids
        )
        if len(observation_ids) != len(set(observation_ids)):
            raise ValueError("manifest observation ids must be unique")
        hashes = tuple(_digest(item, "observation_hash") for item in self.observation_hashes)
        if len(hashes) != len(set(hashes)):
            raise ValueError("manifest observation hashes must be unique")
        if len(observation_ids) != len(hashes):
            raise ValueError("manifest observation lineage pairs must be complete")
        object.__setattr__(self, "observation_ids", observation_ids)
        object.__setattr__(self, "observation_hashes", hashes)
        object.__setattr__(
            self,
            "book_state_hash",
            _digest(self.book_state_hash, "book_state_hash"),
        )
        if self.layer != "NORMALIZED_REPLAY":
            raise ValueError("replay manifest layer is not registered")
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
                    "observation_ids": self.observation_ids,
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
    report_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.book_state, BTCBookState):
            raise ValueError("replay report requires typed book state")
        if not isinstance(self.manifest, BTCReplayManifest):
            raise ValueError("replay report requires typed manifest")
        accepted = tuple(
            identifier(item, "accepted observation_id")
            for item in self.accepted_observation_ids
        )
        if len(accepted) != len(set(accepted)):
            raise ValueError("accepted observation ids must be unique")
        findings = tuple(self.findings)
        if not all(isinstance(item, BTCReplayFinding) for item in findings):
            raise ValueError("replay report findings must be typed")
        latest = (
            (self.latest_trade, BTCTradeObservation, "latest_trade"),
            (
                self.latest_reference_price,
                BTCReferencePriceObservation,
                "latest_reference_price",
            ),
            (self.latest_funding, BTCFundingObservation, "latest_funding"),
        )
        for item, expected_type, name in latest:
            if item is not None and not isinstance(item, expected_type):
                raise ValueError(f"{name} has an unregistered observation type")
        if self.manifest.book_state_hash != self.book_state.state_hash:
            raise ValueError("replay manifest book state hash disagrees")
        if self.manifest.observation_ids != accepted:
            raise ValueError("replay manifest accepted observation ids disagree")
        latest_ids = {
            item.header.observation_id for item, _, _ in latest if item is not None
        }
        if not latest_ids.issubset(set(accepted)):
            raise ValueError("latest observations are absent from accepted ids")
        lineage = dict(
            zip(
                self.manifest.observation_ids,
                self.manifest.observation_hashes,
                strict=True,
            )
        )
        if any(
            lineage[item.header.observation_id] != item.observation_hash
            for item, _, _ in latest
            if item is not None
        ):
            raise ValueError("latest observation digest lineage disagrees")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
            or self.operator_review_required is not True
        ):
            raise ValueError("replay report authority identities are immutable")
        object.__setattr__(self, "accepted_observation_ids", accepted)
        object.__setattr__(self, "findings", findings)
        object.__setattr__(
            self,
            "report_hash",
            canonical_sha256(
                {
                    "accepted_observation_ids": accepted,
                    "book_state_hash": self.book_state.state_hash,
                    "finding_rows": [
                        {
                            "code": item.code,
                            "detail": item.detail,
                            "observation_id": item.observation_id,
                            "severity": item.severity,
                        }
                        for item in findings
                    ],
                    "latest_funding_hash": (
                        self.latest_funding.observation_hash
                        if self.latest_funding is not None
                        else None
                    ),
                    "latest_reference_price_hash": (
                        self.latest_reference_price.observation_hash
                        if self.latest_reference_price is not None
                        else None
                    ),
                    "latest_trade_hash": (
                        self.latest_trade.observation_hash
                        if self.latest_trade is not None
                        else None
                    ),
                    "manifest_hash": self.manifest.manifest_hash,
                }
            ),
        )

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
            observation_ids=tuple(item.header.observation_id for item in accepted),
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
