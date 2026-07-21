from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCMarketReplay,
)
from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1 import (
    BTCLocalExportProfile,
    RegisteredBTCLocalExport,
    canonicalize_registered_btc_local_export,
)
from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1.contracts import (
    CANONICAL_EXPORT_FIELDS,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


AS_OF = "2026-07-21T00:00:20Z"


def _common(observation_id: str, kind: str, sequence: int) -> dict[str, object]:
    return {
        "observation_id": observation_id,
        "venue_id": "venue-a",
        "instrument_id": "BTC-USDT",
        "instrument_kind": "PERPETUAL",
        "observation_kind": kind,
        "source_sequence": sequence,
        "event_at_utc": "2026-07-21T00:00:09Z",
        "received_at_utc": "2026-07-21T00:00:10Z",
        "ingested_at_utc": "2026-07-21T00:00:10Z",
    }


def _rows() -> list[dict[str, object]]:
    snapshot = _common("book-100", "BOOK_SNAPSHOT", 100)
    snapshot.update(
        bids=[["65000", "1.2"], ["64999", "2"]],
        asks=[["65001", "1.1"], ["65002", "3"]],
    )
    delta = _common("book-101", "BOOK_DELTA", 101)
    delta.update(
        previous_sequence=100,
        bid_updates=[["65000", "1.4"]],
        ask_updates=[["65001", "0"], ["65003", "4"]],
    )
    trade = _common("trade-1", "TRADE", 1)
    trade.update(price="65000.5", quantity="0.01", aggressor_side="BUY")
    reference = _common("reference-1", "REFERENCE_PRICE", 1)
    reference.update(mark_price="65000", index_price="64999")
    funding = _common("funding-1", "FUNDING", 1)
    funding.update(
        funding_rate="-0.0001",
        interval_start_utc="2026-07-20T16:00:00Z",
        interval_end_utc="2026-07-21T00:00:10Z",
    )
    return [snapshot, delta, trade, reference, funding]


def _bytes(rows: list[dict[str, object]] | None = None) -> bytes:
    return b"".join(
        json.dumps(row, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
            "ascii"
        )
        + b"\n"
        for row in (rows or _rows())
    )


def _rights() -> LocalEventRights:
    return LocalEventRights(
        license_id="synthetic-local-test-v1",
        permitted_use="local-paper-research",
        retention_days=30,
    )


def _registration(raw: bytes, **changes: object) -> RegisteredBTCLocalExport:
    values: dict[str, object] = {
        "artifact_id": "btc-source-export-v1",
        "source_id": "local-btc-export",
        "content_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "registered_at_utc": "2026-07-21T00:00:15Z",
        "rights": _rights(),
    }
    values.update(changes)
    return RegisteredBTCLocalExport(**values)


def _profile(**changes: object) -> BTCLocalExportProfile:
    values: dict[str, object] = {
        "profile_id": "btc-identity-export-v1",
        "source_id": "local-btc-export",
        "canonical_to_source": {item: item for item in CANONICAL_EXPORT_FIELDS},
    }
    values.update(changes)
    return BTCLocalExportProfile(**values)


def _bridge(path: Path, raw: bytes, **changes: object):
    values: dict[str, object] = {
        "file_path": path,
        "registration": _registration(raw),
        "profile": _profile(),
        "output_artifact_id": "btc-canonical-v1",
        "as_of_utc": AS_OF,
    }
    values.update(changes)
    return canonicalize_registered_btc_local_export(**values)


def test_complete_export_is_canonical_and_fcp_0018_replay_compatible(tmp_path: Path) -> None:
    raw = _bytes()
    path = tmp_path / "btc.ndjson"
    path.write_bytes(raw)

    result = _bridge(path, raw)
    replay = BTCMarketReplay().replay(
        result.canonical_registration,
        result.canonical_ndjson,
        result.observations,
        as_of_utc=AS_OF,
    )

    assert result.quality_state == "READY_FOR_REPLAY"
    assert result.operator_review_required is True
    assert result.manifest.canonical_artifact_sha256 == hashlib.sha256(
        result.canonical_ndjson
    ).hexdigest()
    assert replay.ready is True
    assert replay.book_state.last_sequence == 101
    assert replay.latest_funding.funding_rate.as_tuple().exponent == -4


def test_provider_field_names_are_isolated_by_profile(tmp_path: Path) -> None:
    mapping = {name: f"src_{name}" for name in CANONICAL_EXPORT_FIELDS}
    renamed = [
        {mapping[key]: value for key, value in row.items()}
        for row in _rows()
    ]
    raw = _bytes(renamed)
    path = tmp_path / "renamed.ndjson"
    path.write_bytes(raw)
    result = _bridge(
        path,
        raw,
        profile=_profile(canonical_to_source=mapping),
    )
    assert len(result.observations) == 5
    assert b"src_observation_id" not in result.canonical_ndjson


def test_json_decimal_lexeme_is_preserved_without_binary_float(tmp_path: Path) -> None:
    rows = _rows()
    rows[2]["price"] = 65000.125
    raw = _bytes(rows)
    path = tmp_path / "decimal.ndjson"
    path.write_bytes(raw)
    result = _bridge(path, raw)
    assert result.observations[2].price.as_tuple().exponent == -3
    assert b'"price":"65000.125"' in result.canonical_ndjson


@pytest.mark.parametrize(
    ("change", "match"),
    [
        ({"content_sha256": "0" * 64}, "SHA-256 mismatch"),
        ({"byte_length": 1}, "byte length mismatch"),
    ],
)
def test_exact_registered_bytes_are_enforced(
    tmp_path: Path, change: dict[str, object], match: str
) -> None:
    raw = _bytes()
    path = tmp_path / "btc.ndjson"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match=match):
        _bridge(path, raw, registration=_registration(raw, **change))


@pytest.mark.parametrize(
    ("raw", "match"),
    [
        (b"not-json\n", "invalid NDJSON"),
        (b"\xef\xbb\xbf{}\n", "BOM"),
        (b"{}\n\n", "row count"),
        (b"[]\n", "JSON objects"),
    ],
)
def test_malformed_source_fails_closed(tmp_path: Path, raw: bytes, match: str) -> None:
    path = tmp_path / "bad.ndjson"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match=match):
        _bridge(path, raw)


def test_missing_field_and_unknown_kind_fail_closed(tmp_path: Path) -> None:
    rows = _rows()
    rows[2].pop("price")
    raw = _bytes(rows)
    path = tmp_path / "missing.ndjson"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="lacks required field"):
        _bridge(path, raw)

    rows = _rows()
    rows[2]["observation_kind"] = "ORDER"
    raw = _bytes(rows)
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="observation_kind"):
        _bridge(path, raw)


def test_duplicate_observation_and_future_ingestion_fail_closed(tmp_path: Path) -> None:
    rows = _rows()
    rows[1]["observation_id"] = rows[0]["observation_id"]
    raw = _bytes(rows)
    path = tmp_path / "duplicate.ndjson"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="duplicate observation_id"):
        _bridge(path, raw)

    rows = _rows()
    rows[2]["event_at_utc"] = "2026-07-21T00:00:21Z"
    rows[2]["received_at_utc"] = "2026-07-21T00:00:21Z"
    rows[2]["ingested_at_utc"] = "2026-07-21T00:00:21Z"
    raw = _bytes(rows)
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="future ingestion"):
        _bridge(path, raw)


def test_clock_and_book_contracts_are_not_weakened(tmp_path: Path) -> None:
    rows = _rows()
    rows[2]["event_at_utc"] = "2026-07-21T00:00:11Z"
    raw = _bytes(rows)
    path = tmp_path / "clock.ndjson"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="clocks must be ordered"):
        _bridge(path, raw)

    rows = _rows()
    rows[0]["bids"] = [["65002", "1"]]
    raw = _bytes(rows)
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="crossed or locked"):
        _bridge(path, raw)


def test_delta_and_instrument_kind_contracts_are_not_weakened(tmp_path: Path) -> None:
    rows = _rows()
    rows[1]["previous_sequence"] = 101
    raw = _bytes(rows)
    path = tmp_path / "delta.ndjson"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="follow previous_sequence"):
        _bridge(path, raw)

    rows = _rows()
    rows[3]["instrument_kind"] = "SPOT"
    raw = _bytes(rows)
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="perpetual"):
        _bridge(path, raw)


def test_profile_is_closed_unique_and_source_bound() -> None:
    incomplete = {item: item for item in CANONICAL_EXPORT_FIELDS[:-1]}
    with pytest.raises(ValueError, match="closed BTC local-export schema"):
        _profile(canonical_to_source=incomplete)
    duplicate = {item: "same" for item in CANONICAL_EXPORT_FIELDS}
    with pytest.raises(ValueError, match="uniquely"):
        _profile(canonical_to_source=duplicate)


def test_registration_remains_local_and_provider_unselected() -> None:
    raw = _bytes()
    with pytest.raises(ValueError, match="registered-local"):
        _registration(raw, provider_selected=True)
    with pytest.raises(ValueError, match="registered-local"):
        _registration(raw, raw_repository_storage_allowed=True)
    with pytest.raises(ValueError, match="registered-local"):
        _registration(raw, local_only=False)


def test_source_lineage_must_match_profile(tmp_path: Path) -> None:
    raw = _bytes()
    path = tmp_path / "btc.ndjson"
    path.write_bytes(raw)
    with pytest.raises(ValueError, match="source lineage disagree"):
        _bridge(path, raw, profile=_profile(source_id="other-source"))


def test_result_and_profile_are_immutable_and_deterministic(tmp_path: Path) -> None:
    raw = _bytes()
    path = tmp_path / "btc.ndjson"
    path.write_bytes(raw)
    first = _bridge(path, raw)
    second = _bridge(path, raw)
    assert first.canonical_ndjson == second.canonical_ndjson
    assert first.manifest.manifest_hash == second.manifest.manifest_hash
    with pytest.raises(TypeError):
        _profile().canonical_to_source["price"] = "other"
    with pytest.raises(FrozenInstanceError):
        first.quality_state = "OTHER"
