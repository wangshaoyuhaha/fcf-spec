from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    AShareDailyRowSupplement,
    RegisteredLocalDailyExport,
    canonicalize_registered_local_daily_export,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QMT_SOURCE_COLUMNS,
    QmtLocalDailyExportProfile,
    compare_registered_qmt_front_adjustment,
    normalize_registered_qmt_daily_export,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1.contracts import (
    QmtLocalDailyNormalizationResult,
)


AS_OF = "2026-07-23T02:00:00Z"


def _bytes(*, first_date: str = "20260720", second_date: str = "20260721") -> bytes:
    return (
        "timetag,open,high,low,close,volumn,amount\n"
        f"{first_date},5.05,5.24,5.04,5.24,5358812.0,2770032847.00\n"
        f"{second_date},5.19,5.22,5.09,5.12,4026139.0,2073781911.00\n"
    ).encode("ascii")


def _registration(raw: bytes, *, artifact_id: str = "qmt-raw-v1", **changes: object):
    values: dict[str, object] = {
        "artifact_id": artifact_id,
        "source_id": "guojin-qmt-local-export",
        "artifact_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "registered_at_utc": "2026-07-21T11:20:00Z",
        "rights_state": "DECLARED_LOCAL_RESEARCH",
        "retention_state": "SESSION_ONLY",
    }
    values.update(changes)
    return RegisteredLocalDailyExport(**values)


def _profile(**changes: object) -> QmtLocalDailyExportProfile:
    values: dict[str, object] = {
        "profile_id": "guojin-qmt-daily-export-v1",
        "source_id": "guojin-qmt-local-export",
        "instrument_id": "600028.XSHG",
        "requested_start_date": "2021-01-01",
        "requested_end_date": "2026-07-21",
    }
    values.update(changes)
    return QmtLocalDailyExportProfile(**values)


def _write(path: Path, raw: bytes) -> Path:
    path.write_bytes(raw)
    return path


def _normalize(path: Path, raw: bytes, **changes: object):
    values: dict[str, object] = {
        "file_path": path,
        "registration": _registration(raw),
        "profile": _profile(),
        "output_artifact_id": "qmt-normalized-v1",
        "as_of_utc": AS_OF,
    }
    values.update(changes)
    return normalize_registered_qmt_daily_export(**values)


def test_qmt_profile_records_exact_source_contract() -> None:
    profile = _profile()

    assert QMT_SOURCE_COLUMNS == (
        "timetag",
        "open",
        "high",
        "low",
        "close",
        "volumn",
        "amount",
    )
    assert profile.code == "600028"
    assert profile.exchange == "XSHG"
    assert profile.volume_lot_size == 100
    assert profile.provider_selected is False


def test_normalizer_emits_deterministic_fcp_0019_bridge_bytes(tmp_path: Path) -> None:
    raw = _bytes()
    result = _normalize(_write(tmp_path / "qmt.txt", raw), raw)

    assert result.quality_state == "BLOCKED_PENDING_SUPPLEMENTS"
    assert result.operator_review_required is True
    assert result.manifest.row_count == 2
    assert result.manifest.actual_start_date == "2026-07-20"
    assert result.manifest.actual_end_date == "2026-07-21"
    assert result.finding_codes == (
        "ADJUSTMENT_FACTOR_MISSING",
        "POINT_IN_TIME_SUPPLEMENTS_MISSING",
        "REQUESTED_RANGE_START_MISMATCH",
        "TRADING_STATUS_UNKNOWN",
    )
    lines = result.normalized_csv.decode("ascii").splitlines()
    assert lines[0] == "code,exchange,date,open,high,low,close,volume,amount"
    assert lines[1] == (
        "600028,XSHG,2026-07-20,5.05,5.24,5.04,5.24,535881200,2770032847"
    )
    assert lines[2] == (
        "600028,XSHG,2026-07-21,5.19,5.22,5.09,5.12,402613900,2073781911"
    )
    assert result.normalized_registration.artifact_sha256 == hashlib.sha256(
        result.normalized_csv
    ).hexdigest()


def test_normalizer_is_deterministic(tmp_path: Path) -> None:
    raw = _bytes()
    path = _write(tmp_path / "qmt.txt", raw)

    first = _normalize(path, raw)
    second = _normalize(path, raw)

    assert first.normalized_csv == second.normalized_csv
    assert first.manifest.manifest_hash == second.manifest.manifest_hash


def test_result_rejects_normalized_byte_lineage_mismatch(tmp_path: Path) -> None:
    raw = _bytes()
    result = _normalize(_write(tmp_path / "qmt.txt", raw), raw)

    with pytest.raises(ValueError, match="registration SHA-256 mismatch"):
        QmtLocalDailyNormalizationResult(
            normalized_csv=result.normalized_csv + b"\n",
            normalized_registration=result.normalized_registration,
            bridge_profile=result.bridge_profile,
            manifest=result.manifest,
            quality_state=result.quality_state,
            finding_codes=result.finding_codes,
        )


@pytest.mark.parametrize(
    ("registration_change", "match"),
    [
        ({"byte_length": 1}, "byte length mismatch"),
        ({"artifact_sha256": "0" * 64}, "SHA-256 mismatch"),
    ],
)
def test_registered_bytes_are_exact(
    tmp_path: Path, registration_change: dict[str, object], match: str
) -> None:
    raw = _bytes()
    path = _write(tmp_path / "qmt.txt", raw)
    with pytest.raises(ValueError, match=match):
        _normalize(path, raw, registration=_registration(raw, **registration_change))


def test_header_is_closed(tmp_path: Path) -> None:
    raw = _bytes().replace(b"volumn", b"volume", 1)
    path = _write(tmp_path / "qmt.txt", raw)
    with pytest.raises(ValueError, match="columns are not exact"):
        _normalize(path, raw)


@pytest.mark.parametrize(
    ("old", "new", "match"),
    [
        (b"20260720", b"20260230", "valid YYYYMMDD"),
        (b"5358812.0", b"5358812.5", "integral lots"),
        (b"5.24,5.04,5.24", b"5.00,5.04,5.24", "high price"),
        (b"5.05,5.24,5.04,5.24", b"5.05,5.40,5.30,5.24", "low price"),
    ],
)
def test_invalid_source_values_fail_closed(
    tmp_path: Path, old: bytes, new: bytes, match: str
) -> None:
    raw = _bytes().replace(old, new, 1)
    path = _write(tmp_path / "qmt.txt", raw)
    with pytest.raises(ValueError, match=match):
        _normalize(path, raw)


def test_duplicate_and_unordered_dates_are_rejected(tmp_path: Path) -> None:
    duplicate = _bytes(second_date="20260720")
    with pytest.raises(ValueError, match="duplicate dates"):
        _normalize(_write(tmp_path / "duplicate.txt", duplicate), duplicate)

    unordered = _bytes(first_date="20260721", second_date="20260720")
    with pytest.raises(ValueError, match="not ordered"):
        _normalize(_write(tmp_path / "unordered.txt", unordered), unordered)


def test_profile_rejects_unsafe_identity_and_adjustment_claims() -> None:
    with pytest.raises(ValueError, match="A-share exchange identifier"):
        _profile(instrument_id="price_600028.txt")
    with pytest.raises(ValueError, match="100 shares"):
        _profile(volume_lot_size=1)
    with pytest.raises(ValueError, match="RAW prices only"):
        _profile(adjustment_mode="FRONT")
    with pytest.raises(ValueError, match="unselected"):
        _profile(provider_selected=True)


def test_front_adjustment_is_recorded_as_additive_reference_only(
    tmp_path: Path,
) -> None:
    raw = _bytes()
    front = (
        "timetag,open,high,low,close,volumn,amount\n"
        "20260720,4.85,5.04,4.84,5.04,5358812.0,2770032847.00\n"
        "20260721,5.19,5.22,5.09,5.12,4026139.0,2073781911.00\n"
    ).encode("ascii")
    reference = compare_registered_qmt_front_adjustment(
        _write(tmp_path / "raw.txt", raw),
        _registration(raw),
        _write(tmp_path / "front.txt", front),
        _registration(front, artifact_id="qmt-front-v1"),
        _profile(),
    )

    assert reference.adjustment_semantics == "ADDITIVE_PRICE_REFERENCE_ONLY"
    assert reference.factor_authority is False
    assert reference.boundary_dates == ("2026-07-21",)
    assert str(reference.latest_cash_offset) == "0.00"


def test_front_adjustment_cannot_change_volume_or_amount(tmp_path: Path) -> None:
    raw = _bytes()
    front = raw.replace(b"5358812.0", b"5358813.0", 1)
    with pytest.raises(ValueError, match="changed volume or amount"):
        compare_registered_qmt_front_adjustment(
            _write(tmp_path / "raw.txt", raw),
            _registration(raw),
            _write(tmp_path / "front.txt", front),
            _registration(front, artifact_id="qmt-front-v1"),
            _profile(),
        )


def _supplement(trade_date: str) -> AShareDailyRowSupplement:
    return AShareDailyRowSupplement(
        instrument_id="600028.XSHG",
        trade_date=trade_date,
        event_at_utc=f"{trade_date}T07:00:00Z",
        available_at_utc=f"{trade_date}T07:05:00Z",
        first_tradable_at_utc=f"{trade_date}T07:05:00Z",
        ingested_at_utc=f"{trade_date}T08:00:00Z",
        revision_at_utc=f"{trade_date}T08:00:00Z",
        trading_status="UNKNOWN",
        adjustment_factor=None,
        factor_version=None,
        factor_available_at_utc=None,
    )


def test_normalized_bytes_enter_fcp_0019_without_weakening_blockers(
    tmp_path: Path,
) -> None:
    raw = _bytes()
    result = _normalize(_write(tmp_path / "qmt.txt", raw), raw)
    normalized = _write(tmp_path / "normalized.csv", result.normalized_csv)

    bridged = canonicalize_registered_local_daily_export(
        normalized,
        result.normalized_registration,
        result.bridge_profile,
        (_supplement("2026-07-20"), _supplement("2026-07-21")),
        output_artifact_id="qmt-canonical-v1",
        as_of_utc=AS_OF,
    )

    assert bridged.quality_state == "BLOCKED"
    assert bridged.finding_codes == (
        "ADJUSTMENT_FACTOR_MISSING",
        "TRADING_STATUS_UNKNOWN",
    )
    assert b"600028.XSHG,2026-07-20" in bridged.canonical_csv
