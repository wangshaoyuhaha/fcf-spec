from dataclasses import replace
from decimal import Decimal

import pytest

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCBookLevel,
    BTCBookState,
    BTCMarketReplay,
)
from tests.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.test_d1_d6 import (
    AS_OF,
    CONTENT,
    artifact,
    complete_events,
)


def replay_report():
    return BTCMarketReplay().replay(
        artifact(),
        CONTENT,
        complete_events(),
        as_of_utc=AS_OF,
    )


def test_exact_replay_report_remains_valid_and_deterministic():
    first = replay_report()
    second = replay_report()

    assert first.ready is True
    assert first.manifest.observation_ids == first.accepted_observation_ids
    assert first.report_hash == second.report_hash


@pytest.mark.parametrize(
    "field,value",
    [
        ("calculation_authority", "BROKER"),
        ("evidence_authority", "UNREGISTERED"),
        ("ai_role", "DECISION_AUTHORITY"),
        ("operator_review_required", False),
    ],
)
def test_report_rejects_authority_substitution(field, value):
    report = replay_report()

    with pytest.raises(ValueError, match="authority identities are immutable"):
        replace(report, **{field: value})


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("artifact_sha256", "NOT-A-DIGEST", "lowercase SHA-256"),
        ("book_state_hash", "NOT-A-DIGEST", "lowercase SHA-256"),
        ("layer", "RAW", "layer is not registered"),
    ],
)
def test_manifest_rejects_invalid_registered_fields(field, value, match):
    manifest = replay_report().manifest

    with pytest.raises(ValueError, match=match):
        replace(manifest, **{field: value})


def test_manifest_rejects_incomplete_or_duplicate_lineage_pairs():
    manifest = replay_report().manifest

    with pytest.raises(ValueError, match="lineage pairs must be complete"):
        replace(manifest, observation_ids=manifest.observation_ids[:-1])
    with pytest.raises(ValueError, match="observation ids must be unique"):
        replace(
            manifest,
            observation_ids=(
                manifest.observation_ids[0],
                manifest.observation_ids[0],
                *manifest.observation_ids[2:],
            ),
        )


@pytest.mark.parametrize("field,value", [("last_sequence", True), ("generation", Decimal("1.5"))])
def test_book_state_rejects_non_integer_sequence_fields(field, value):
    book = replay_report().book_state

    with pytest.raises(ValueError, match="sequence and generation"):
        replace(book, **{field: value})


def test_book_state_rejects_untyped_unsorted_and_crossed_depth():
    book = replay_report().book_state

    with pytest.raises(ValueError, match="typed levels"):
        replace(book, bids=((Decimal("1"), Decimal("1")),))
    with pytest.raises(ValueError, match="descending"):
        replace(book, bids=tuple(reversed(book.bids)))
    with pytest.raises(ValueError, match="noncrossed"):
        replace(
            book,
            bids=(BTCBookLevel(book.asks[0].price, Decimal("1")),),
        )


def test_report_rejects_book_manifest_state_disagreement():
    report = replay_report()
    changed_book = replace(report.book_state, generation=report.book_state.generation + 1)

    with pytest.raises(ValueError, match="book state hash disagrees"):
        replace(report, book_state=changed_book)


class FakeFinding:
    severity = "INFO"


def test_report_rejects_structural_finding_impersonation():
    report = replay_report()

    with pytest.raises(ValueError, match="findings must be typed"):
        replace(report, findings=(FakeFinding(),))


def test_report_rejects_accepted_id_manifest_disagreement():
    report = replay_report()

    with pytest.raises(ValueError, match="accepted observation ids disagree"):
        replace(
            report,
            accepted_observation_ids=("fake-id", *report.accepted_observation_ids[1:]),
        )


def test_report_rejects_latest_observation_digest_disagreement():
    report = replay_report()
    index = report.manifest.observation_ids.index(
        report.latest_trade.header.observation_id
    )
    hashes = list(report.manifest.observation_hashes)
    hashes[index] = "f" * 64
    changed_manifest = replace(report.manifest, observation_hashes=tuple(hashes))

    with pytest.raises(ValueError, match="latest observation digest lineage disagrees"):
        replace(report, manifest=changed_manifest)


def test_report_rejects_wrong_latest_observation_type():
    report = replay_report()

    with pytest.raises(ValueError, match="latest_trade has an unregistered"):
        replace(report, latest_trade=report.latest_reference_price)


def test_report_rejects_latest_observation_absent_from_accepted_ids():
    report = replay_report()
    latest_id = report.latest_trade.header.observation_id
    index = report.manifest.observation_ids.index(latest_id)
    ids = list(report.manifest.observation_ids)
    ids[index] = "substitute-id"
    changed_manifest = replace(report.manifest, observation_ids=tuple(ids))

    with pytest.raises(ValueError, match="latest observations are absent"):
        replace(
            report,
            accepted_observation_ids=tuple(ids),
            manifest=changed_manifest,
        )
