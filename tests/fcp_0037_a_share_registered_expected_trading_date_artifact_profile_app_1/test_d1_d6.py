from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from apps.fcp_0037_a_share_registered_expected_trading_date_artifact_profile_app_1 import (
    RegisteredExpectedTradingDateArtifact,
    RegisteredExpectedTradingDateProfile,
    load_registered_expected_trading_dates,
    to_fcp_0036_expected_date_set,
)


RAW = b"trade_date\n2026-07-17\n2026-07-20\n2026-07-21\n"


def _registration(
    raw: bytes = RAW,
    **updates: object,
) -> RegisteredExpectedTradingDateArtifact:
    values: dict[str, object] = {
        "artifact_id": "calendar-xshg-600036-v1",
        "source_id": "operator-local-calendar",
        "source_revision_id": "revision-2026-07-21",
        "artifact_sha256": hashlib.sha256(raw).hexdigest(),
        "byte_length": len(raw),
        "market_id": "XSHG",
        "instrument_id": "600036.XSHG",
        "declared_start_date": "2026-07-17",
        "declared_end_date": "2026-07-21",
        "observed_at_utc": "2026-07-21T07:00:00Z",
        "available_at_utc": "2026-07-21T07:05:00Z",
        "registered_at_utc": "2026-07-21T08:00:00Z",
        "revision_at_utc": "2026-07-21T08:30:00Z",
        "rights_state": "DECLARED_LOCAL_RESEARCH",
        "retention_state": "SESSION_ONLY",
    }
    values.update(updates)
    return RegisteredExpectedTradingDateArtifact(**values)


def _write(tmp_path: Path, raw: bytes = RAW) -> Path:
    path = tmp_path / "registered_dates.csv"
    path.write_bytes(raw)
    return path


def test_loads_exact_registered_artifact_deterministically(tmp_path: Path) -> None:
    path = _write(tmp_path)
    registration = _registration()

    first = load_registered_expected_trading_dates(
        path, registration, as_of_utc="2026-07-21T09:00:00Z"
    )
    second = load_registered_expected_trading_dates(
        path, registration, as_of_utc="2026-07-21T09:00:00Z"
    )

    assert first == second
    assert first.dates == ("2026-07-17", "2026-07-20", "2026-07-21")
    assert first.manifest.date_count == 3
    assert first.manifest.quality_state == "REGISTERED_EXPECTED_DATES_READY"
    assert first.manifest.finding_codes == ("EXACT_REGISTERED_TRADING_DATES",)
    assert first.operator_review_required is True
    assert first.provider_selected is False


def test_rejects_byte_tampering(tmp_path: Path) -> None:
    path = _write(tmp_path, RAW + b"2026-07-22\n")
    with pytest.raises(ValueError, match="byte length mismatch"):
        load_registered_expected_trading_dates(
            path, _registration(), as_of_utc="2026-07-21T09:00:00Z"
        )


def test_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        load_registered_expected_trading_dates(
            tmp_path / "missing.csv",
            _registration(),
            as_of_utc="2026-07-21T09:00:00Z",
        )


@pytest.mark.parametrize(
    "raw,message",
    (
        (b"date\n2026-07-17\n", "columns are not exact"),
        (b"trade_date\n", "must not be empty"),
        (
            b"trade_date\n2026-07-20\n2026-07-17\n",
            "ordered and unique",
        ),
        (
            b"trade_date\n2026-07-17\n2026-07-17\n",
            "ordered and unique",
        ),
        (b"trade_date\n2026-02-30\n", "must be an ISO date"),
        (b"trade_date\n 2026-07-17\n", "canonical ISO text"),
    ),
)
def test_rejects_unsafe_date_artifact_rows(
    tmp_path: Path,
    raw: bytes,
    message: str,
) -> None:
    path = _write(tmp_path, raw)
    registration = _registration(
        raw,
        declared_start_date="2026-07-17",
        declared_end_date="2026-07-20",
    )
    with pytest.raises(ValueError, match=message):
        load_registered_expected_trading_dates(
            path, registration, as_of_utc="2026-07-21T09:00:00Z"
        )


def test_rejects_non_ascii_artifact(tmp_path: Path) -> None:
    raw = "trade_date\n2026-07-17\ncalendar\u65e5\n".encode("utf-8")
    path = _write(tmp_path, raw)
    with pytest.raises(ValueError, match="must be ASCII"):
        load_registered_expected_trading_dates(
            path,
            _registration(raw, declared_end_date="2026-07-17"),
            as_of_utc="2026-07-21T09:00:00Z",
        )


def test_rejects_declared_range_mismatch(tmp_path: Path) -> None:
    path = _write(tmp_path)
    registration = _registration(declared_start_date="2026-07-16")
    with pytest.raises(ValueError, match="coverage range disagrees"):
        load_registered_expected_trading_dates(
            path, registration, as_of_utc="2026-07-21T09:00:00Z"
        )


def test_rejects_future_revision(tmp_path: Path) -> None:
    path = _write(tmp_path)
    with pytest.raises(ValueError, match="future revision"):
        load_registered_expected_trading_dates(
            path, _registration(), as_of_utc="2026-07-21T08:00:00Z"
        )


def test_rejects_inconsistent_time_lineage() -> None:
    with pytest.raises(ValueError, match="time lineage is inconsistent"):
        _registration(available_at_utc="2026-07-21T06:59:00Z")


def test_rejects_market_instrument_disagreement() -> None:
    with pytest.raises(ValueError, match="instrument_id and market_id disagree"):
        _registration(market_id="XSHE")


def test_rejects_natural_day_inference_authority() -> None:
    with pytest.raises(ValueError, match="natural-day inference"):
        _registration(natural_day_inference_allowed=True)


def test_unresolved_rights_remain_visible(tmp_path: Path) -> None:
    path = _write(tmp_path)
    profile = load_registered_expected_trading_dates(
        path,
        _registration(rights_state="UNRESOLVED"),
        as_of_utc="2026-07-21T09:00:00Z",
    )

    assert profile.manifest.quality_state == "REVIEW_REQUIRED_UNRESOLVED_RIGHTS"
    assert "RIGHTS_UNRESOLVED" in profile.manifest.finding_codes


def test_source_revision_changes_registration_and_date_set_hash(tmp_path: Path) -> None:
    path = _write(tmp_path)
    first = load_registered_expected_trading_dates(
        path, _registration(), as_of_utc="2026-07-21T09:00:00Z"
    )
    revised_registration = replace(
        _registration(), source_revision_id="revision-2026-07-21-b"
    )
    second = load_registered_expected_trading_dates(
        path, revised_registration, as_of_utc="2026-07-21T09:00:00Z"
    )

    assert first.registration.registration_hash != second.registration.registration_hash
    assert first.manifest.date_set_hash != second.manifest.date_set_hash


def test_explicit_compatibility_conversion_preserves_fcp_0036_authority(
    tmp_path: Path,
) -> None:
    path = _write(tmp_path)
    profile = load_registered_expected_trading_dates(
        path, _registration(), as_of_utc="2026-07-21T09:00:00Z"
    )

    compatible = to_fcp_0036_expected_date_set(profile)

    assert compatible.instrument_id == "600036.XSHG"
    assert compatible.registration.artifact_sha256 == hashlib.sha256(RAW).hexdigest()
    assert compatible.registration.rights_state == "DECLARED_LOCAL_RESEARCH"
    assert compatible.operator_registered is True
    assert compatible.natural_day_inference_allowed is False


def test_profile_rejects_registration_manifest_lineage_mismatch(
    tmp_path: Path,
) -> None:
    path = _write(tmp_path)
    profile = load_registered_expected_trading_dates(
        path, _registration(), as_of_utc="2026-07-21T09:00:00Z"
    )
    forged_manifest = replace(profile.manifest, source_revision_id="forged-revision")

    with pytest.raises(ValueError, match="manifest lineage disagree"):
        RegisteredExpectedTradingDateProfile(
            registration=profile.registration,
            dates=profile.dates,
            manifest=forged_manifest,
        )
