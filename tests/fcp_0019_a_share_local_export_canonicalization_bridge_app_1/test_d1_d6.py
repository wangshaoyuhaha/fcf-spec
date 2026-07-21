from __future__ import annotations

import hashlib
from decimal import Decimal
from pathlib import Path

import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1 import (
    CANONICAL_COLUMNS,
    calibrate_registered_a_share_daily_csv,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    AShareDailyRowSupplement,
    LocalDailyExportProfile,
    RegisteredLocalDailyExport,
    canonicalize_registered_local_daily_export,
)


RQ_COLUMNS = (
    "order_book_id",
    "date",
    "low",
    "open",
    "high",
    "limit_down",
    "num_trades",
    "close",
    "limit_up",
    "volume",
    "total_turnover",
)
RQ_MAPPING = {
    "instrument_id": "order_book_id",
    "trade_date": "date",
    "raw_open": "open",
    "raw_high": "high",
    "raw_low": "low",
    "raw_close": "close",
    "volume": "volume",
    "amount": "total_turnover",
}
AS_OF = "2026-07-21T02:00:00Z"


def _bytes(*, bom: bool = False, duplicate: bool = False) -> bytes:
    header = ",".join(RQ_COLUMNS)
    rows = [
        "600036.XSHG,2026-07-18,40.1,40.2,41.0,36.0,2500,40.8,44.0,100000,4050000.25",
        "000001.XSHE,2026-07-18,11.8,12.0,12.4,10.8,1800,12.2,13.2,200000,2420000.5",
    ]
    if duplicate:
        rows.append(rows[0])
    text = header + "\n" + "\n".join(rows) + "\n"
    return (("\ufeff" if bom else "") + text).encode("utf-8")


def _registration(raw: bytes, **changes: object) -> RegisteredLocalDailyExport:
    values: dict[str, object] = {
        "artifact_id": "rq-local-export-v1",
        "source_id": "rqdata-trial-local-export",
        "artifact_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "registered_at_utc": "2026-07-21T01:00:00Z",
        "rights_state": "DECLARED_LOCAL_RESEARCH",
        "retention_state": "LOCAL_DERIVED_ONLY",
    }
    values.update(changes)
    return RegisteredLocalDailyExport(**values)


def _profile(**changes: object) -> LocalDailyExportProfile:
    values: dict[str, object] = {
        "profile_id": "rq-daily-export-v1",
        "source_id": "rqdata-trial-local-export",
        "source_columns": RQ_COLUMNS,
        "canonical_to_source": RQ_MAPPING,
    }
    values.update(changes)
    return LocalDailyExportProfile(**values)


def _supplement(instrument_id: str, **changes: object) -> AShareDailyRowSupplement:
    values: dict[str, object] = {
        "instrument_id": instrument_id,
        "trade_date": "2026-07-18",
        "event_at_utc": "2026-07-18T07:00:00Z",
        "available_at_utc": "2026-07-18T07:05:00Z",
        "first_tradable_at_utc": "2026-07-21T01:30:00Z",
        "ingested_at_utc": "2026-07-18T08:00:00Z",
        "revision_at_utc": "2026-07-18T08:00:00Z",
        "trading_status": "OBSERVED_TRADING",
        "adjustment_factor": Decimal("1.25"),
        "factor_version": "rq-export-factor-v1",
        "factor_available_at_utc": "2026-07-18T07:05:00Z",
    }
    values.update(changes)
    return AShareDailyRowSupplement(**values)


def _supplements() -> tuple[AShareDailyRowSupplement, ...]:
    return (_supplement("600036.XSHG"), _supplement("000001.XSHE"))


def _write(path: Path, raw: bytes) -> Path:
    path.write_bytes(raw)
    return path


def _bridge(path: Path, raw: bytes, **changes: object):
    values: dict[str, object] = {
        "file_path": path,
        "registration": _registration(raw),
        "profile": _profile(),
        "supplements": _supplements(),
        "output_artifact_id": "canonical-a-share-daily-v1",
        "as_of_utc": AS_OF,
    }
    values.update(changes)
    return canonicalize_registered_local_daily_export(**values)


def test_bridge_emits_exact_fcp_0017_input_and_calibrates(tmp_path: Path) -> None:
    raw = _bytes()
    source = _write(tmp_path / "rq.csv", raw)

    result = _bridge(source, raw)

    assert result.quality_state == "READY_FOR_CALIBRATION"
    assert result.finding_codes == ()
    assert result.operator_review_required is True
    assert result.manifest.row_count == 2
    assert result.manifest.source_artifact_sha256 == hashlib.sha256(raw).hexdigest()
    assert result.manifest.canonical_artifact_sha256 == hashlib.sha256(
        result.canonical_csv
    ).hexdigest()
    lines = result.canonical_csv.decode("ascii").splitlines()
    assert tuple(lines[0].split(",")) == CANONICAL_COLUMNS
    assert lines[1].startswith("000001.XSHE,2026-07-18,")
    assert lines[2].startswith("600036.XSHG,2026-07-18,")

    canonical = _write(tmp_path / "canonical.csv", result.canonical_csv)
    calibrated = calibrate_registered_a_share_daily_csv(
        canonical, result.canonical_registration, as_of_utc=AS_OF
    )
    assert calibrated.quality_state == "READY_FOR_RESEARCH"
    assert [item.instrument_id for item in calibrated.observations] == [
        "000001.XSHE",
        "600036.XSHG",
    ]
    assert calibrated.observations[0].research_payload()["close"] == "15.25"


def test_code_exchange_profile_normalizes_instruments(tmp_path: Path) -> None:
    raw = (
        "code,exchange,date,open,high,low,close,volume,amount\n"
        "600036,SSE,2026-07-18,40.2,41.0,40.1,40.8,100000,4050000.25\n"
    ).encode("ascii")
    path = _write(tmp_path / "code-exchange.csv", raw)
    profile = LocalDailyExportProfile(
        profile_id="code-exchange-v1",
        source_id="local-provider-export",
        source_columns=(
            "code",
            "exchange",
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "amount",
        ),
        canonical_to_source={
            "instrument_code": "code",
            "exchange": "exchange",
            "trade_date": "date",
            "raw_open": "open",
            "raw_high": "high",
            "raw_low": "low",
            "raw_close": "close",
            "volume": "volume",
            "amount": "amount",
        },
        instrument_format="CODE_EXCHANGE",
    )
    result = canonicalize_registered_local_daily_export(
        path,
        _registration(raw, source_id="local-provider-export"),
        profile,
        (_supplement("600036.XSHG"),),
        output_artifact_id="canonical-code-exchange-v1",
        as_of_utc=AS_OF,
    )
    assert b"600036.XSHG" in result.canonical_csv


@pytest.mark.parametrize(
    ("registration_change", "match"),
    [
        ({"byte_length": 1}, "byte length mismatch"),
        ({"artifact_sha256": "0" * 64}, "SHA-256 mismatch"),
    ],
)
def test_exact_registered_bytes_are_enforced(
    tmp_path: Path, registration_change: dict[str, object], match: str
) -> None:
    raw = _bytes()
    path = _write(tmp_path / "rq.csv", raw)
    with pytest.raises(ValueError, match=match):
        _bridge(path, raw, registration=_registration(raw, **registration_change))


def test_source_columns_must_match_registered_profile(tmp_path: Path) -> None:
    raw = _bytes().replace(b"order_book_id", b"unexpected", 1)
    path = _write(tmp_path / "rq.csv", raw)
    with pytest.raises(ValueError, match="columns do not match profile"):
        _bridge(path, raw)


def test_duplicate_source_keys_are_rejected(tmp_path: Path) -> None:
    raw = _bytes(duplicate=True)
    path = _write(tmp_path / "rq.csv", raw)
    with pytest.raises(ValueError, match="duplicate keys"):
        _bridge(path, raw)


@pytest.mark.parametrize(
    ("supplements", "match"),
    [
        ((_supplement("600036.XSHG"),), "lacks point-in-time supplement"),
        (
            (
                _supplement("600036.XSHG"),
                _supplement("000001.XSHE"),
                _supplement("300001.XSHE"),
            ),
            "unobserved export keys",
        ),
        (
            (_supplement("600036.XSHG"), _supplement("600036.XSHG")),
            "supplement keys must be unique",
        ),
    ],
)
def test_supplements_must_match_export_exactly(
    tmp_path: Path,
    supplements: tuple[AShareDailyRowSupplement, ...],
    match: str,
) -> None:
    raw = _bytes()
    path = _write(tmp_path / "rq.csv", raw)
    with pytest.raises(ValueError, match=match):
        _bridge(path, raw, supplements=supplements)


@pytest.mark.parametrize(
    ("change", "match"),
    [
        ({"revision_at_utc": "2026-07-22T08:00:00Z"}, "future revision"),
        (
            {
                "revision_at_utc": "2026-07-22T08:00:00Z",
                "factor_available_at_utc": "2026-07-22T07:00:00Z",
            },
            "future revision",
        ),
    ],
)
def test_future_lineage_is_rejected(
    tmp_path: Path, change: dict[str, object], match: str
) -> None:
    raw = _bytes()
    path = _write(tmp_path / "rq.csv", raw)
    supplements = (_supplement("600036.XSHG", **change), _supplement("000001.XSHE"))
    with pytest.raises(ValueError, match=match):
        _bridge(path, raw, supplements=supplements)


def test_missing_factor_and_unknown_status_block_without_guessing(tmp_path: Path) -> None:
    raw = _bytes()
    path = _write(tmp_path / "rq.csv", raw)
    supplements = (
        _supplement(
            "600036.XSHG",
            adjustment_factor=None,
            factor_version=None,
            factor_available_at_utc=None,
            trading_status="UNKNOWN",
        ),
        _supplement("000001.XSHE"),
    )
    result = _bridge(path, raw, supplements=supplements)
    assert result.quality_state == "BLOCKED"
    assert result.finding_codes == (
        "ADJUSTMENT_FACTOR_MISSING",
        "TRADING_STATUS_UNKNOWN",
    )
    canonical = _write(tmp_path / "blocked.csv", result.canonical_csv)
    calibrated = calibrate_registered_a_share_daily_csv(
        canonical, result.canonical_registration, as_of_utc=AS_OF
    )
    assert calibrated.quality_state == "BLOCKED"
    assert calibrated.finding_codes == result.finding_codes


def test_unresolved_rights_and_retention_are_visible_blockers(tmp_path: Path) -> None:
    raw = _bytes()
    path = _write(tmp_path / "rq.csv", raw)
    result = _bridge(
        path,
        raw,
        registration=_registration(
            raw, rights_state="UNRESOLVED", retention_state="UNRESOLVED"
        ),
    )
    assert result.quality_state == "BLOCKED"
    assert result.finding_codes == (
        "COMMERCIAL_RIGHTS_UNRESOLVED",
        "RETENTION_RIGHTS_UNRESOLVED",
    )


def test_bom_is_normalized_and_hashes_are_deterministic(tmp_path: Path) -> None:
    raw = _bytes(bom=True)
    path = _write(tmp_path / "rq.csv", raw)
    first = _bridge(path, raw)
    second = _bridge(path, raw)
    assert first.manifest.warning_codes == ("SOURCE_UTF8_BOM_NORMALIZED",)
    assert first.canonical_csv == second.canonical_csv
    assert first.manifest.manifest_hash == second.manifest.manifest_hash


def test_embedded_bom_is_rejected(tmp_path: Path) -> None:
    raw = _bytes().replace(b"40.2", "\ufeff40.2".encode("utf-8"), 1)
    path = _write(tmp_path / "rq.csv", raw)
    with pytest.raises(ValueError, match="embedded BOM"):
        _bridge(path, raw)


def test_profile_remains_closed_and_provider_unselected() -> None:
    incomplete = dict(RQ_MAPPING)
    incomplete.pop("amount")
    with pytest.raises(ValueError, match="closed local-export semantic schema"):
        _profile(canonical_to_source=incomplete)
    with pytest.raises(ValueError, match="provider-unselected"):
        _profile(provider_selected=True)


def test_supplement_rejects_invalid_trade_date() -> None:
    with pytest.raises(ValueError, match="trade_date must be an ISO date"):
        _supplement("600036.XSHG", trade_date="2026-02-30")


def test_source_lineage_must_match_profile(tmp_path: Path) -> None:
    raw = _bytes()
    path = _write(tmp_path / "rq.csv", raw)
    with pytest.raises(ValueError, match="source lineage disagree"):
        _bridge(path, raw, profile=_profile(source_id="different-local-export"))
