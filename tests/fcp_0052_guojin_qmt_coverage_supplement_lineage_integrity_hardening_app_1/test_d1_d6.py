from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0036_guojin_qmt_registered_local_daily_batch_coverage_reconciliation_app_1 import (
    QmtBatchCoverageManifest,
)
from apps.fcp_0037_a_share_registered_expected_trading_date_artifact_profile_app_1 import (
    RegisteredExpectedTradingDateArtifact,
    RegisteredExpectedTradingDateProfile,
    TradingDateArtifactManifest,
)
from apps.fcp_0051_guojin_qmt_historical_coverage_completeness_gate_app_1 import (
    RegisteredCoverageSupplements,
    build_qmt_historical_coverage_completeness_evidence,
)
from apps.fcp_0052_guojin_qmt_coverage_supplement_lineage_integrity_hardening_app_1 import (
    PaginationBehaviorEvidence,
    PointInTimeSupplementEvidence,
    RowCapResolutionEvidence,
    build_coverage_supplement_lineage_bundle,
)


ROOT = Path(__file__).resolve().parents[2]
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64
HASH_F = "f" * 64


def _gate():
    source = json.loads(
        (
            ROOT / "FCF_REGISTERED_EVIDENCE_FCP_0050_GUOJIN_QMT_DUAL_EXPORT_QUALITY.json"
        ).read_text(encoding="ascii")
    )
    return build_qmt_historical_coverage_completeness_evidence(
        source_record=source,
        supplements=RegisteredCoverageSupplements(),
        evidence_id="fcp-0052-source-gate-v1",
        as_of_utc="2026-07-22T01:30:00Z",
    )


def _calendar(instrument: str = "600028.XSHG"):
    registration = RegisteredExpectedTradingDateArtifact(
        artifact_id="fcp-0052-calendar-v1",
        source_id="registered-calendar-source",
        source_revision_id="calendar-revision-v1",
        artifact_sha256=HASH_A,
        byte_length=42,
        market_id=instrument[7:],
        instrument_id=instrument,
        declared_start_date="2021-01-01",
        declared_end_date="2026-07-21",
        observed_at_utc="2026-07-21T15:00:00Z",
        available_at_utc="2026-07-21T15:01:00Z",
        registered_at_utc="2026-07-21T15:02:00Z",
        revision_at_utc="2026-07-21T15:03:00Z",
        rights_state="DECLARED_LOCAL_RESEARCH",
        retention_state="LOCAL_DERIVED_ONLY",
    )
    dates = ("2021-01-01", "2026-07-21")
    date_set_hash = canonical_sha256(
        {
            "dates": dates,
            "instrument_id": instrument,
            "market_id": instrument[7:],
            "registration_hash": registration.registration_hash,
            "source_id": registration.source_id,
            "source_revision_id": registration.source_revision_id,
        }
    )
    manifest = TradingDateArtifactManifest(
        registration_hash=registration.registration_hash,
        artifact_sha256=registration.artifact_sha256,
        source_id=registration.source_id,
        source_revision_id=registration.source_revision_id,
        market_id=registration.market_id,
        instrument_id=registration.instrument_id,
        start_date=dates[0],
        end_date=dates[-1],
        date_count=len(dates),
        date_set_hash=date_set_hash,
        rights_state=registration.rights_state,
        retention_state=registration.retention_state,
        quality_state="REGISTERED_EXPECTED_DATES_READY",
        finding_codes=("REGISTERED_EXPECTED_DATES_READY",),
    )
    return RegisteredExpectedTradingDateProfile(
        registration=registration,
        dates=dates,
        manifest=manifest,
    )


def _batch(calendar, *, batch_hashes=(HASH_B, HASH_C), expected_hash=None):
    return QmtBatchCoverageManifest(
        instrument_id=calendar.registration.instrument_id,
        profile_hash=HASH_D,
        expected_date_set_hash=expected_hash or calendar.manifest.date_set_hash,
        expected_artifact_sha256=calendar.manifest.artifact_sha256,
        ordered_batch_hashes=batch_hashes,
        ordered_source_artifact_sha256s=tuple(HASH_E for _ in batch_hashes),
        ordered_normalization_manifest_hashes=tuple(HASH_F for _ in batch_hashes),
        merged_artifact_sha256=HASH_B,
        row_count=2,
        expected_date_count=2,
        identical_overlap_count=0,
        missing_dates=(),
        unexpected_dates=(),
        conflict_dates=(),
        row_cap_batch_ids=("batch-01",),
        finding_codes=("ROW_CAP_OBSERVED",),
    )


def _inputs():
    gate = _gate()
    calendar = _calendar()
    batch = _batch(calendar)
    pagination = PaginationBehaviorEvidence(
        evidence_id="fcp-0052-pagination-v1",
        instrument_id=gate.instrument_id,
        requested_start_date=gate.requested_start_date,
        requested_end_date=gate.requested_end_date,
        behavior="EXPLICIT_MULTI_EXPORT",
        batch_count=2,
        maximum_rows_per_batch=500,
    )
    point_in_time = PointInTimeSupplementEvidence(
        evidence_id="fcp-0052-pit-v1",
        instrument_id=gate.instrument_id,
        coverage_start_date=gate.requested_start_date,
        coverage_end_date=gate.requested_end_date,
        adjustment_lineage_hash=HASH_A,
        trading_status_lineage_hash=HASH_B,
        availability_lineage_hash=HASH_C,
        revision_lineage_hash=HASH_D,
        first_tradable_lineage_hash=HASH_E,
    )
    row_cap = RowCapResolutionEvidence(
        evidence_id="fcp-0052-row-cap-v1",
        instrument_id=gate.instrument_id,
        requested_start_date=gate.requested_start_date,
        requested_end_date=gate.requested_end_date,
        observed_row_cap=gate.row_count,
        pagination_evidence_hash=pagination.evidence_hash,
        multi_batch_manifest_hash=batch.manifest_hash,
    )
    return gate, calendar, batch, pagination, point_in_time, row_cap


def _build(values=None):
    values = values or _inputs()
    return build_coverage_supplement_lineage_bundle(
        gate=values[0],
        calendar=values[1],
        multi_batch_manifest=values[2],
        pagination=values[3],
        point_in_time=values[4],
        row_cap_resolution=values[5],
    )


def test_derives_all_fcp_0051_supplements_from_typed_lineage() -> None:
    bundle = _build()
    assert bundle.supplements.expected_date_set_hash == bundle.calendar.manifest.date_set_hash
    assert bundle.supplements.multi_batch_manifest_hash == bundle.multi_batch_manifest.manifest_hash
    assert bundle.supplements.missing_date_count == 0
    assert bundle.supplements.unexpected_date_count == 0
    assert bundle.supplements.conflict_date_count == 0
    assert bundle.supplements.pagination_evidence_hash == bundle.pagination.evidence_hash
    assert bundle.supplements.point_in_time_supplement_hash == bundle.point_in_time.evidence_hash
    assert bundle.supplements.row_cap_resolution_hash == bundle.row_cap_resolution.evidence_hash


def test_bundle_is_deterministic() -> None:
    values = _inputs()
    assert _build(values).bundle_hash == _build(values).bundle_hash


def test_cross_instrument_lineage_is_rejected() -> None:
    values = list(_inputs())
    values[3] = replace(values[3], instrument_id="000001.XSHE")
    with pytest.raises(ValueError, match="instruments disagree"):
        _build(tuple(values))


def test_cross_range_lineage_is_rejected() -> None:
    values = list(_inputs())
    values[3] = replace(values[3], requested_start_date="2022-01-01")
    with pytest.raises(ValueError, match="requested ranges disagree"):
        _build(tuple(values))


def test_calendar_date_set_mismatch_is_rejected() -> None:
    values = list(_inputs())
    values[2] = _batch(values[1], expected_hash=HASH_F)
    with pytest.raises(ValueError, match="date-set hashes disagree"):
        _build(tuple(values))


def test_one_batch_cannot_claim_multi_batch_evidence() -> None:
    values = list(_inputs())
    values[2] = _batch(values[1], batch_hashes=(HASH_B,))
    with pytest.raises(ValueError, match="at least two"):
        _build(tuple(values))


def test_pagination_batch_count_must_match_manifest() -> None:
    values = list(_inputs())
    values[3] = replace(values[3], batch_count=3)
    with pytest.raises(ValueError, match="batch count disagrees"):
        _build(tuple(values))


def test_row_cap_must_bind_exact_pagination_and_batch_manifest() -> None:
    values = list(_inputs())
    values[5] = replace(values[5], pagination_evidence_hash=HASH_A)
    with pytest.raises(ValueError, match="pagination lineage disagrees"):
        _build(tuple(values))
    values = list(_inputs())
    values[5] = replace(values[5], multi_batch_manifest_hash=HASH_A)
    with pytest.raises(ValueError, match="batch lineage disagrees"):
        _build(tuple(values))


def test_point_in_time_evidence_must_cover_requested_range() -> None:
    values = list(_inputs())
    values[4] = replace(values[4], coverage_start_date="2022-01-01")
    with pytest.raises(ValueError, match="does not cover"):
        _build(tuple(values))


def test_runtime_and_provider_authority_are_rejected() -> None:
    with pytest.raises(ValueError, match="runtime or provider authority"):
        PaginationBehaviorEvidence(
            evidence_id="unsafe-pagination",
            instrument_id="600028.XSHG",
            requested_start_date="2021-01-01",
            requested_end_date="2026-07-21",
            behavior="EXPLICIT_MULTI_EXPORT",
            batch_count=2,
            maximum_rows_per_batch=500,
            network_used=True,
        )
