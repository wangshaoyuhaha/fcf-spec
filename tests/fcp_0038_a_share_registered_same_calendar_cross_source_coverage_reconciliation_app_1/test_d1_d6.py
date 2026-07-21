from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1 import (
    AShareDailyObservation,
)
from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationPolicy,
    RegisteredCanonicalDailyDataset,
)
from apps.fcp_0037_a_share_registered_expected_trading_date_artifact_profile_app_1 import (
    RegisteredExpectedTradingDateArtifact,
    load_registered_expected_trading_dates,
)
from apps.fcp_0038_a_share_registered_same_calendar_cross_source_coverage_reconciliation_app_1 import (
    SourceRoleDataset,
    reconcile_same_calendar_cross_source_coverage,
)


RAW = b"trade_date\n2026-07-17\n2026-07-20\n2026-07-21\n"
AS_OF = "2026-07-23T10:00:00Z"


def _calendar(
    tmp_path: Path,
    rights_state: str = "DECLARED_LOCAL_RESEARCH",
):
    path = tmp_path / "calendar.csv"
    path.write_bytes(RAW)
    registration = RegisteredExpectedTradingDateArtifact(
        artifact_id="calendar-v1",
        source_id="calendar-source",
        source_revision_id="calendar-revision-v1",
        artifact_sha256=hashlib.sha256(RAW).hexdigest(),
        byte_length=len(RAW),
        market_id="XSHG",
        instrument_id="600036.XSHG",
        declared_start_date="2026-07-17",
        declared_end_date="2026-07-21",
        observed_at_utc="2026-07-21T07:00:00Z",
        available_at_utc="2026-07-21T07:05:00Z",
        registered_at_utc="2026-07-21T08:00:00Z",
        revision_at_utc="2026-07-21T08:30:00Z",
        rights_state=rights_state,
        retention_state="SESSION_ONLY",
    )
    return load_registered_expected_trading_dates(
        path, registration, as_of_utc="2026-07-21T09:00:00Z"
    )


def _observation(
    trade_date: str,
    source_hash: str,
    **changes: object,
) -> AShareDailyObservation:
    values: dict[str, object] = {
        "instrument_id": "600036.XSHG",
        "trade_date": trade_date,
        "raw_open": Decimal("10"),
        "raw_high": Decimal("12"),
        "raw_low": Decimal("9"),
        "raw_close": Decimal("11"),
        "volume": 1000,
        "amount": Decimal("10500"),
        "adjustment_factor": Decimal("1.25"),
        "factor_version": "factor-v1",
        "factor_available_at_utc": f"{trade_date}T08:01:00Z",
        "event_at_utc": f"{trade_date}T08:00:00Z",
        "available_at_utc": f"{trade_date}T08:01:00Z",
        "first_tradable_at_utc": f"{trade_date}T08:01:00Z",
        "ingested_at_utc": f"{trade_date}T08:02:00Z",
        "revision_at_utc": f"{trade_date}T09:00:00Z",
        "trading_status": "OBSERVED_TRADING",
        "source_artifact_sha256": source_hash,
    }
    values.update(changes)
    return AShareDailyObservation(**values)


def _dataset(
    suffix: str,
    dates: tuple[str, ...] = ("2026-07-17", "2026-07-20", "2026-07-21"),
    **row_changes: object,
) -> RegisteredCanonicalDailyDataset:
    source_hash = ("a" if suffix == "qmt" else "b") * 64
    rows = tuple(
        _observation(date, source_hash, **row_changes) for date in dates
    )
    return RegisteredCanonicalDailyDataset(
        dataset_id=f"dataset-{suffix}",
        source_id=f"source-{suffix}",
        observations=rows,
        as_of_utc=AS_OF,
    )


def _role(role: str, suffix: str, **changes: object) -> SourceRoleDataset:
    return SourceRoleDataset(role=role, dataset=_dataset(suffix, **changes))


def _policy() -> AShareCrossSourceReconciliationPolicy:
    return AShareCrossSourceReconciliationPolicy(policy_id="same-calendar-v1")


def test_same_calendar_identical_sources_are_consistent(tmp_path: Path) -> None:
    result = reconcile_same_calendar_cross_source_coverage(
        _role("QMT_LOCAL_EXPORT", "qmt"),
        _role("INDEPENDENT_REFERENCE", "independent"),
        _calendar(tmp_path),
        _policy(),
    )

    assert result.quality_state == "CONSISTENT"
    assert result.finding_codes == ("SAME_REGISTERED_CALENDAR_COMPARED",)
    assert result.qmt_missing_dates == result.independent_missing_dates == ()
    assert result.cross_source_result.quality_state == "CONSISTENT"
    assert result.operator_review_required is True
    assert result.source_selected is False


def test_qmt_missing_date_is_role_specific(tmp_path: Path) -> None:
    result = reconcile_same_calendar_cross_source_coverage(
        _role("QMT_LOCAL_EXPORT", "qmt", dates=("2026-07-17", "2026-07-21")),
        _role("INDEPENDENT_REFERENCE", "independent"),
        _calendar(tmp_path),
        _policy(),
    )

    assert result.qmt_missing_dates == ("2026-07-20",)
    assert result.independent_missing_dates == ()
    assert "QMT_EXPECTED_DATES_MISSING" in result.finding_codes
    assert result.quality_state == "QUARANTINE_REVIEW_REQUIRED"


def test_independent_unexpected_date_is_role_specific(tmp_path: Path) -> None:
    result = reconcile_same_calendar_cross_source_coverage(
        _role("QMT_LOCAL_EXPORT", "qmt"),
        _role(
            "INDEPENDENT_REFERENCE",
            "independent",
            dates=("2026-07-17", "2026-07-20", "2026-07-21", "2026-07-22"),
        ),
        _calendar(tmp_path),
        _policy(),
    )

    assert result.independent_unexpected_dates == ("2026-07-22",)
    assert "INDEPENDENT_UNEXPECTED_DATES_PRESENT" in result.finding_codes


def test_cross_source_value_mismatch_is_quarantined(tmp_path: Path) -> None:
    result = reconcile_same_calendar_cross_source_coverage(
        _role("QMT_LOCAL_EXPORT", "qmt"),
        _role("INDEPENDENT_REFERENCE", "independent", raw_close=Decimal("11.1")),
        _calendar(tmp_path),
        _policy(),
    )

    assert result.cross_source_result.quality_state == "QUARANTINE_REVIEW_REQUIRED"
    assert "CROSS_SOURCE_QUALITY_QUARANTINED" in result.finding_codes


def test_unresolved_calendar_rights_are_quarantined(tmp_path: Path) -> None:
    result = reconcile_same_calendar_cross_source_coverage(
        _role("QMT_LOCAL_EXPORT", "qmt"),
        _role("INDEPENDENT_REFERENCE", "independent"),
        _calendar(tmp_path, rights_state="UNRESOLVED"),
        _policy(),
    )

    assert result.calendar_quality_state == "REVIEW_REQUIRED_UNRESOLVED_RIGHTS"
    assert "CALENDAR_AUTHORITY_REVIEW_REQUIRED" in result.finding_codes
    assert result.quality_state == "QUARANTINE_REVIEW_REQUIRED"


def test_result_contract_rejects_invalid_identity_and_dates(tmp_path: Path) -> None:
    result = reconcile_same_calendar_cross_source_coverage(
        _role("QMT_LOCAL_EXPORT", "qmt"),
        _role("INDEPENDENT_REFERENCE", "independent"),
        _calendar(tmp_path),
        _policy(),
    )

    with pytest.raises(ValueError, match="A-share exchange identifier"):
        replace(result, instrument_id="unsafe")
    with pytest.raises(ValueError, match="must contain ISO dates"):
        replace(result, qmt_missing_dates=("not-a-date",))


def test_result_contract_rejects_finding_evidence_disagreement(
    tmp_path: Path,
) -> None:
    result = reconcile_same_calendar_cross_source_coverage(
        _role("QMT_LOCAL_EXPORT", "qmt"),
        _role("INDEPENDENT_REFERENCE", "independent"),
        _calendar(tmp_path),
        _policy(),
    )

    with pytest.raises(ValueError, match="finding_codes and coverage evidence disagree"):
        replace(result, finding_codes=("SAME_REGISTERED_CALENDAR_COMPARED", "EXTRA"))


def test_result_is_deterministic(tmp_path: Path) -> None:
    inputs = (
        _role("QMT_LOCAL_EXPORT", "qmt"),
        _role("INDEPENDENT_REFERENCE", "independent"),
        _calendar(tmp_path),
        _policy(),
    )
    assert reconcile_same_calendar_cross_source_coverage(
        *inputs
    ) == reconcile_same_calendar_cross_source_coverage(*inputs)


def test_roles_are_not_interchangeable(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="QMT_LOCAL_EXPORT"):
        reconcile_same_calendar_cross_source_coverage(
            _role("INDEPENDENT_REFERENCE", "qmt"),
            _role("INDEPENDENT_REFERENCE", "independent"),
            _calendar(tmp_path),
            _policy(),
        )


def test_same_source_identity_is_rejected(tmp_path: Path) -> None:
    qmt = _role("QMT_LOCAL_EXPORT", "qmt")
    independent = SourceRoleDataset(
        role="INDEPENDENT_REFERENCE",
        dataset=RegisteredCanonicalDailyDataset(
            dataset_id="dataset-independent",
            source_id=qmt.dataset.source_id,
            observations=_dataset("independent").observations,
            as_of_utc=AS_OF,
        ),
    )
    with pytest.raises(ValueError, match="distinct source identities"):
        reconcile_same_calendar_cross_source_coverage(
            qmt, independent, _calendar(tmp_path), _policy()
        )


def test_instrument_disagreement_is_rejected(tmp_path: Path) -> None:
    independent = _role(
        "INDEPENDENT_REFERENCE",
        "independent",
        instrument_id="000001.XSHE",
    )
    with pytest.raises(ValueError, match="instrument identities disagree"):
        reconcile_same_calendar_cross_source_coverage(
            _role("QMT_LOCAL_EXPORT", "qmt"),
            independent,
            _calendar(tmp_path),
            _policy(),
        )
