from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path

import pytest

from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1 import (
    BTCLocalExportProfile,
    RegisteredBTCLocalExport,
)
from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1.contracts import (
    CANONICAL_EXPORT_FIELDS,
)
from apps.fcp_0085_btc_registered_local_export_validation_runner_app_1 import (
    BTCLocalExportValidationRequest,
    render_validation_json,
    validate_registered_btc_local_export,
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
    snapshot.update(bids=[["65000", "1.2"]], asks=[["65001", "1.1"]])
    delta = _common("book-101", "BOOK_DELTA", 101)
    delta.update(
        previous_sequence=100,
        bid_updates=[["65000", "1.4"]],
        ask_updates=[["65001", "0"]],
    )
    trade = _common("trade-1", "TRADE", 1)
    trade.update(price="65000.5", quantity="0.01", aggressor_side="BUY")
    reference = _common("reference-1", "REFERENCE_PRICE", 2)
    reference.update(mark_price="65000", index_price="64999")
    funding = _common("funding-1", "FUNDING", 3)
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


def _registration(raw: bytes, **changes: object) -> RegisteredBTCLocalExport:
    values: dict[str, object] = {
        "artifact_id": "btc-source-export-v1",
        "source_id": "local-btc-export",
        "content_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "registered_at_utc": "2026-07-21T00:00:15Z",
        "rights": LocalEventRights(
            license_id="synthetic-local-test-v1",
            permitted_use="local-paper-research",
            retention_days=30,
        ),
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


def _request(raw: bytes, **changes: object) -> BTCLocalExportValidationRequest:
    values: dict[str, object] = {
        "registration": _registration(raw),
        "profile": _profile(),
        "output_artifact_id": "btc-canonical-v1",
        "as_of_utc": AS_OF,
    }
    values.update(changes)
    return BTCLocalExportValidationRequest(**values)


def _run(tmp_path: Path, raw: bytes | None = None):
    payload = raw or _bytes()
    path = tmp_path / "btc.ndjson"
    path.write_bytes(payload)
    return validate_registered_btc_local_export(path, _request(payload))


def test_d1_request_is_typed_immutable_and_source_aligned() -> None:
    raw = _bytes()
    request = _request(raw)

    assert request.registration.source_id == request.profile.source_id
    with pytest.raises(FrozenInstanceError):
        request.output_artifact_id = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="source lineage disagree"):
        _request(raw, profile=_profile(source_id="other-source"))
    with pytest.raises(ValueError, match="cannot precede"):
        _request(raw, as_of_utc="2026-07-21T00:00:14Z")


def test_d2_requires_existing_regular_non_symlink_path(tmp_path: Path) -> None:
    raw = _bytes()
    target = tmp_path / "target.ndjson"
    target.write_bytes(raw)
    link = tmp_path / "link.ndjson"
    link.symlink_to(target)

    with pytest.raises(ValueError, match="must not be a symlink"):
        validate_registered_btc_local_export(link, _request(raw))
    with pytest.raises(FileNotFoundError, match="not a regular file"):
        validate_registered_btc_local_export(tmp_path / "missing.ndjson", _request(raw))
    with pytest.raises(FileNotFoundError, match="not a regular file"):
        validate_registered_btc_local_export(tmp_path, _request(raw))


def test_d3_delegates_all_five_typed_observation_kinds(tmp_path: Path) -> None:
    result = _run(tmp_path)

    assert result.observation_count == 5
    assert result.observation_kind_counts == (
        ("BOOK_DELTA", 1),
        ("BOOK_SNAPSHOT", 1),
        ("FUNDING", 1),
        ("REFERENCE_PRICE", 1),
        ("TRADE", 1),
    )
    assert (result.sequence_min, result.sequence_max) == (1, 101)
    assert result.quality_state == "READY_FOR_REPLAY"


def test_d4_output_is_ascii_path_free_and_value_free(tmp_path: Path) -> None:
    rendered = render_validation_json(_run(tmp_path))
    payload = json.loads(rendered)

    rendered.encode("ascii")
    assert payload["authority"]["operator_review_required"] is True
    assert payload["authority"]["raw_rows_retained"] is False
    assert payload["authority"]["canonical_rows_retained"] is False
    assert "btc.ndjson" not in rendered
    for prohibited in ("65000", "64999", "0.01", "-0.0001", "bids", "asks"):
        assert prohibited not in rendered


def test_d5_exact_registered_bytes_and_bridge_validation_fail_closed(tmp_path: Path) -> None:
    raw = _bytes()
    path = tmp_path / "btc.ndjson"
    path.write_bytes(raw)

    with pytest.raises(ValueError, match="byte length mismatch"):
        validate_registered_btc_local_export(
            path,
            _request(raw, registration=_registration(raw, byte_length=len(raw) - 1)),
        )
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        validate_registered_btc_local_export(
            path,
            _request(raw, registration=_registration(raw, content_sha256="0" * 64)),
        )
    with pytest.raises(ValueError, match="invalid NDJSON"):
        _run(tmp_path, b"not-json\n")


def test_d6_result_cannot_gain_runtime_or_action_authority(tmp_path: Path) -> None:
    result = _run(tmp_path)

    for changes in (
        {"operator_review_required": False},
        {"local_only": False},
        {"provider_selected": True},
        {"network_used": True},
        {"sdk_used": True},
        {"raw_rows_retained": True},
        {"canonical_rows_retained": True},
        {"local_paths_retained": True},
        {"gap_closed": True},
    ):
        with pytest.raises(ValueError, match="cannot gain runtime or action authority"):
            replace(result, **changes)


def test_result_and_rendering_are_deterministic(tmp_path: Path) -> None:
    first = _run(tmp_path)
    second = _run(tmp_path)

    assert first == second
    assert first.result_hash == second.result_hash
    assert render_validation_json(first) == render_validation_json(second)


def test_clock_and_lineage_metadata_are_preserved(tmp_path: Path) -> None:
    result = _run(tmp_path)

    assert result.source_artifact_sha256 == hashlib.sha256(_bytes()).hexdigest()
    assert result.event_start_utc == result.event_end_utc
    assert result.ingested_end_utc <= result.as_of_utc
    assert len(result.manifest_hash) == 64
    assert len(result.observation_hashes_sha256) == 64


def test_runner_and_renderer_require_typed_inputs(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="request must be"):
        validate_registered_btc_local_export(tmp_path, object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="result must be"):
        render_validation_json(object())  # type: ignore[arg-type]
