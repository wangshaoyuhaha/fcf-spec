from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCBookDelta,
    BTCBookLevel,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCMarketReplay,
    BTCObservationHeader,
    BTCReferencePriceObservation,
    BTCRegisteredArtifact,
    BTCTradeObservation,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


CONTENT = b'{"fixture":"btc-local-replay-v1"}\n'
AS_OF = "2026-07-21T00:00:20Z"


def artifact(content: bytes = CONTENT) -> BTCRegisteredArtifact:
    return BTCRegisteredArtifact(
        artifact_id="btc-local-replay-v1",
        content_sha256=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights=LocalEventRights(
            license_id="synthetic-local-test-v1",
            permitted_use="local-paper-research",
            retention_days=30,
        ),
    )


def header(
    observation_id: str,
    kind: str,
    sequence: int,
    *,
    instrument_kind: str = "PERPETUAL",
    artifact_id: str = "btc-local-replay-v1",
    venue_id: str = "venue-a",
    received_at: str = "2026-07-21T00:00:10Z",
    event_at: str = "2026-07-21T00:00:09Z",
) -> BTCObservationHeader:
    return BTCObservationHeader(
        observation_id=observation_id,
        artifact_id=artifact_id,
        venue_id=venue_id,
        instrument_id="BTC-USDT",
        instrument_kind=instrument_kind,
        observation_kind=kind,
        source_sequence=sequence,
        event_at_utc=event_at,
        received_at_utc=received_at,
        ingested_at_utc=received_at,
    )


def level(price: str, quantity: str) -> BTCBookLevel:
    return BTCBookLevel(Decimal(price), Decimal(quantity))


def snapshot(sequence: int = 100, observation_id: str = "book-100") -> BTCBookSnapshot:
    return BTCBookSnapshot(
        header(observation_id, "BOOK_SNAPSHOT", sequence),
        bids=(level("65000", "1.2"), level("64999", "2")),
        asks=(level("65001", "1.1"), level("65002", "3")),
    )


def delta(
    sequence: int = 101,
    previous: int = 100,
    observation_id: str = "book-101",
) -> BTCBookDelta:
    return BTCBookDelta(
        header(observation_id, "BOOK_DELTA", sequence),
        previous_sequence=previous,
        bid_updates=(level("65000", "1.4"),),
        ask_updates=(level("65001", "0"), level("65003", "4")),
    )


def trade(*, instrument_kind: str = "PERPETUAL") -> BTCTradeObservation:
    return BTCTradeObservation(
        header("trade-1", "TRADE", 1, instrument_kind=instrument_kind),
        Decimal("65000.5"),
        Decimal("0.01"),
        "BUY",
    )


def reference(mark: str = "65000", index: str = "64999") -> BTCReferencePriceObservation:
    return BTCReferencePriceObservation(
        header("reference-1", "REFERENCE_PRICE", 1),
        Decimal(mark),
        Decimal(index),
    )


def funding(rate: str = "-0.0001") -> BTCFundingObservation:
    return BTCFundingObservation(
        header("funding-1", "FUNDING", 1),
        Decimal(rate),
        "2026-07-20T16:00:00Z",
        "2026-07-21T00:00:10Z",
    )


def complete_events() -> tuple[object, ...]:
    return (snapshot(), delta(), trade(), reference(), funding())


def test_complete_perpetual_replay_is_ready_and_exact() -> None:
    report = BTCMarketReplay().replay(
        artifact(), CONTENT, complete_events(), as_of_utc=AS_OF
    )

    assert report.ready is True
    assert report.book_state.sync_state == "SYNCED"
    assert report.book_state.last_sequence == 101
    assert report.book_state.asks[0].price == Decimal("65002")
    assert report.latest_funding.funding_rate == Decimal("-0.0001")
    assert report.calculation_authority == "DETERMINISTIC_ENGINE"
    assert report.evidence_authority == "REGISTERED_EVIDENCE"
    assert report.ai_role == "ADVISORY_ONLY"
    assert report.operator_review_required is True


def test_contracts_are_immutable_and_reject_binary_float() -> None:
    item = level("1", "2")
    with pytest.raises(FrozenInstanceError):
        item.price = Decimal("2")
    with pytest.raises(ValueError, match="exact decimal"):
        BTCBookLevel(1.5, Decimal("1"))


def test_header_rejects_future_event_and_wrong_market_kind() -> None:
    with pytest.raises(ValueError, match="clocks must be ordered"):
        BTCObservationHeader(
            "obs-1",
            "artifact-1",
            "venue-a",
            "BTC-USDT",
            "SPOT",
            "TRADE",
            1,
            "2026-07-21T00:00:02Z",
            "2026-07-21T00:00:01Z",
            "2026-07-21T00:00:03Z",
        )
    with pytest.raises(ValueError, match="instrument_kind"):
        header("obs-2", "TRADE", 1, instrument_kind="A_SHARE")


def test_snapshot_rejects_crossed_book_and_unsorted_depth() -> None:
    with pytest.raises(ValueError, match="crossed or locked"):
        BTCBookSnapshot(
            header("crossed", "BOOK_SNAPSHOT", 1),
            bids=(level("10", "1"),),
            asks=(level("9", "1"),),
        )
    with pytest.raises(ValueError, match="price-descending"):
        BTCBookSnapshot(
            header("unsorted", "BOOK_SNAPSHOT", 1),
            bids=(level("9", "1"), level("10", "1")),
            asks=(level("11", "1"),),
        )


def test_sequence_gap_freezes_deltas_until_registered_snapshot() -> None:
    gap = delta(sequence=102, previous=101, observation_id="gap-102")
    ignored = delta(sequence=103, previous=102, observation_id="ignored-103")
    resync = snapshot(sequence=200, observation_id="resync-200")
    report = BTCMarketReplay().replay(
        artifact(),
        CONTENT,
        (snapshot(), gap, ignored, resync, trade(), reference(), funding()),
        as_of_utc=AS_OF,
    )

    assert report.book_state.sync_state == "SYNCED"
    assert report.book_state.last_sequence == 200
    assert report.book_state.generation == 2
    assert "gap-102" not in report.accepted_observation_ids
    assert "ignored-103" not in report.accepted_observation_ids
    assert {item.code for item in report.findings} >= {
        "SEQUENCE_GAP_RESYNC_REQUIRED",
        "BOOK_DELTA_WITHOUT_SYNCED_SNAPSHOT",
    }
    assert report.ready is False


def test_crossing_delta_is_ignored_and_requires_resync() -> None:
    crossing = BTCBookDelta(
        header("crossing", "BOOK_DELTA", 101),
        100,
        (level("65002", "1"),),
        (),
    )
    report = BTCMarketReplay().replay(
        artifact(),
        CONTENT,
        (snapshot(), crossing, trade(), reference(), funding()),
        as_of_utc=AS_OF,
    )

    assert report.book_state.sync_state == "RESYNC_REQUIRED"
    assert report.book_state.last_sequence == 100
    assert report.findings[0].code == "CROSSED_OR_EMPTY_BOOK_RESYNC_REQUIRED"


def test_artifact_digest_and_byte_length_are_verified() -> None:
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        BTCMarketReplay().replay(
            artifact(b'{"fixture":"btc-local-replay-v2"}\n'),
            CONTENT,
            complete_events(),
            as_of_utc=AS_OF,
        )
    bad_length = BTCRegisteredArtifact(
        artifact_id="btc-local-replay-v1",
        content_sha256=hashlib.sha256(CONTENT).hexdigest(),
        byte_length=len(CONTENT) + 1,
        rights=artifact().rights,
    )
    with pytest.raises(ValueError, match="byte length mismatch"):
        BTCMarketReplay().replay(
            bad_length, CONTENT, complete_events(), as_of_utc=AS_OF
        )


def test_observation_artifact_and_venue_lineage_are_isolated() -> None:
    wrong_artifact_trade = BTCTradeObservation(
        header("wrong-artifact", "TRADE", 1, artifact_id="other-artifact"),
        Decimal("1"),
        Decimal("1"),
        "UNKNOWN",
    )
    with pytest.raises(ValueError, match="artifact lineage mismatch"):
        BTCMarketReplay().replay(
            artifact(), CONTENT, (wrong_artifact_trade,), as_of_utc=AS_OF
        )
    other_venue = BTCTradeObservation(
        header("other-venue", "TRADE", 1, venue_id="venue-b"),
        Decimal("1"),
        Decimal("1"),
        "UNKNOWN",
    )
    with pytest.raises(ValueError, match="isolate one venue"):
        BTCMarketReplay().replay(
            artifact(), CONTENT, (snapshot(), other_venue), as_of_utc=AS_OF
        )


def test_perpetual_missing_reference_and_funding_fail_closed() -> None:
    report = BTCMarketReplay().replay(
        artifact(), CONTENT, (snapshot(), trade()), as_of_utc=AS_OF
    )

    assert report.ready is False
    assert {item.code for item in report.findings} == {
        "REFERENCE_PRICE_STREAM_MISSING",
        "FUNDING_STREAM_MISSING",
    }


def test_spot_does_not_inherit_perpetual_funding_semantics() -> None:
    spot_snapshot = BTCBookSnapshot(
        header("spot-book", "BOOK_SNAPSHOT", 1, instrument_kind="SPOT"),
        bids=(level("10", "1"),),
        asks=(level("11", "1"),),
    )
    report = BTCMarketReplay().replay(
        artifact(), CONTENT, (spot_snapshot, trade(instrument_kind="SPOT")), as_of_utc=AS_OF
    )

    assert report.ready is True
    assert not any("FUNDING" in item.code for item in report.findings)


def test_24x7_staleness_fails_closed_without_session_calendar() -> None:
    stale_trade = BTCTradeObservation(
        header(
            "stale-trade",
            "TRADE",
            1,
            received_at="2026-07-20T23:58:00Z",
            event_at="2026-07-20T23:57:59Z",
        ),
        Decimal("65000"),
        Decimal("1"),
        "SELL",
    )
    report = BTCMarketReplay(max_age_seconds=30).replay(
        artifact(),
        CONTENT,
        (snapshot(), stale_trade, reference(), funding()),
        as_of_utc=AS_OF,
    )

    assert "TRADE_STREAM_STALE" in {item.code for item in report.findings}
    assert report.ready is False


def test_mark_index_divergence_fails_closed() -> None:
    report = BTCMarketReplay(mark_index_divergence_bps=50).replay(
        artifact(),
        CONTENT,
        (snapshot(), trade(), reference("66000", "65000"), funding()),
        as_of_utc=AS_OF,
    )

    assert "MARK_INDEX_DIVERGENCE" in {item.code for item in report.findings}
    assert report.ready is False


def test_reference_and_funding_are_perpetual_only() -> None:
    with pytest.raises(ValueError, match="perpetual"):
        BTCReferencePriceObservation(
            header("spot-reference", "REFERENCE_PRICE", 1, instrument_kind="SPOT"),
            Decimal("1"),
            Decimal("1"),
        )
    with pytest.raises(ValueError, match="perpetual"):
        BTCFundingObservation(
            header("spot-funding", "FUNDING", 1, instrument_kind="SPOT"),
            Decimal("0"),
            "2026-07-20T16:00:00Z",
            "2026-07-21T00:00:10Z",
        )


def test_replay_manifest_is_deterministic_and_contains_only_accepted_events() -> None:
    engine = BTCMarketReplay()
    first = engine.replay(artifact(), CONTENT, complete_events(), as_of_utc=AS_OF)
    second = engine.replay(artifact(), CONTENT, complete_events(), as_of_utc=AS_OF)

    assert first.manifest.manifest_hash == second.manifest.manifest_hash
    assert first.manifest.observation_hashes == second.manifest.observation_hashes
    assert first.manifest.artifact_sha256 == hashlib.sha256(CONTENT).hexdigest()
