from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtLocalDailyExportProfile,
)
from apps.fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1 import (
    QmtRegisteredBatchSpec,
    build_reference_evidence,
    render_evidence_json,
    run_coverage_probe,
)


HEADER = b"timetag,open,high,low,close,volumn,amount\n"


def _content(*dates: str) -> bytes:
    rows = [HEADER]
    for index, value in enumerate(dates, start=1):
        price = 10 + index
        rows.append(
            f"{value},{price},{price + 1},{price - 1},{price},100,1000\n".encode(
                "ascii"
            )
        )
    return b"".join(rows)


def _profile(start: str = "2026-07-17", end: str = "2026-07-21"):
    return QmtLocalDailyExportProfile(
        profile_id="qmt-sh-600028-profile-v1",
        source_id="guojin-qmt-local-export",
        instrument_id="600028.XSHG",
        requested_start_date=start,
        requested_end_date=end,
    )


def _spec(path: Path, batch_id: str, sequence: int) -> QmtRegisteredBatchSpec:
    data = path.read_bytes()
    return QmtRegisteredBatchSpec(
        batch_id=batch_id,
        sequence=sequence,
        local_path=path,
        artifact_id=f"{batch_id}-artifact",
        artifact_sha256=hashlib.sha256(data).hexdigest(),
        byte_length=len(data),
    )


def _probe(tmp_path: Path):
    path = tmp_path / "raw.txt"
    path.write_bytes(_content("20260717", "20260720", "20260721"))
    return run_coverage_probe(
        (_spec(path, "qmt-batch-1", 1),),
        _profile(),
        evidence_id="qmt-sh-600028-coverage-probe-v1",
        observed_at_utc="2026-07-22T21:35:27Z",
    )


def test_d1_probe_is_immutable_and_non_authorizing(tmp_path: Path):
    evidence = _probe(tmp_path)
    assert evidence.status == "BLOCKED_PENDING_REGISTERED_EXPECTED_DATES"
    assert evidence.outcome == "INSUFFICIENT_EVIDENCE"
    assert evidence.raw_rows_embedded is False
    assert evidence.normalized_rows_embedded is False
    assert evidence.local_paths_embedded is False
    assert evidence.registered_evidence_promotion_allowed is False
    assert evidence.provider_selection_allowed is False
    assert evidence.factor_calculation_allowed is False
    assert evidence.product_authority_allowed is False
    with pytest.raises(FrozenInstanceError):
        evidence.outcome = "UNSAFE"


def test_d2_probe_delegates_to_fcp35_and_keeps_rows_out(tmp_path: Path):
    evidence = _probe(tmp_path)
    observation = evidence.observations[0]
    assert observation.row_count == 3
    assert observation.actual_start_date == "2026-07-17"
    assert observation.actual_end_date == "2026-07-21"
    rendered = render_evidence_json(evidence)
    assert str(tmp_path) not in rendered
    assert '"open"' not in rendered
    assert "1000" not in rendered
    rendered.encode("ascii")
    source = (
        Path(__file__).resolve().parents[2]
        / "apps/fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1/runner.py"
    ).read_text(encoding="ascii")
    assert "normalize_registered_qmt_daily_export" in source
    assert "import csv" not in source


def test_d3_missing_expected_dates_and_fcp36_remain_visible(tmp_path: Path):
    evidence = _probe(tmp_path)
    assert "EXPECTED_DATE_ARTIFACT_MISSING" in evidence.finding_codes
    assert "FCP36_RECONCILIATION_NOT_RUN" in evidence.finding_codes
    assert "PAGINATION_NOT_PROVEN" in evidence.finding_codes
    assert "ADJUSTMENT_FACTOR_MISSING" in evidence.finding_codes
    assert "TRADING_STATUS_UNKNOWN" in evidence.finding_codes


def test_d4_requested_range_mismatch_comes_from_fcp35(tmp_path: Path):
    path = tmp_path / "raw.txt"
    path.write_bytes(_content("20260720", "20260721"))
    evidence = run_coverage_probe(
        (_spec(path, "qmt-batch-1", 1),),
        _profile(),
        evidence_id="qmt-sh-600028-coverage-probe-v1",
        observed_at_utc="2026-07-22T21:35:27Z",
    )
    assert "REQUESTED_RANGE_START_MISMATCH" in evidence.finding_codes


def test_d4_rows_outside_explicit_request_are_rejected(tmp_path: Path):
    path = tmp_path / "raw.txt"
    path.write_bytes(_content("20260716", "20260721"))
    with pytest.raises(ValueError):
        run_coverage_probe(
            (_spec(path, "qmt-batch-1", 1),),
            _profile(),
            evidence_id="qmt-sh-600028-coverage-probe-v1",
            observed_at_utc="2026-07-22T21:35:27Z",
        )


def test_d4_equal_batch_counts_are_only_observed_bounds(tmp_path: Path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_bytes(_content("20260717", "20260718"))
    second.write_bytes(_content("20260720", "20260721"))
    evidence = run_coverage_probe(
        (
            _spec(first, "qmt-batch-1", 1),
            _spec(second, "qmt-batch-2", 2),
        ),
        _profile(),
        evidence_id="qmt-sh-600028-coverage-probe-v1",
        observed_at_utc="2026-07-22T21:35:27Z",
    )
    assert evidence.repeated_observed_row_count_bound is True
    assert "PAGINATION_NOT_PROVEN" in evidence.finding_codes
    assert evidence.outcome == "INSUFFICIENT_EVIDENCE"


def test_d5_output_is_canonical_and_deterministic(tmp_path: Path):
    first = _probe(tmp_path)
    second = _probe(tmp_path)
    rendered = render_evidence_json(first)
    assert rendered == render_evidence_json(second)
    assert json.dumps(
        json.loads(rendered), ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ) == rendered
    assert first.evidence_hash == second.evidence_hash
    assert build_reference_evidence().evidence_hash == (
        "a4d0f5164c98db1d03c6fdc6d87bb8b3c9ccae8f8ef5b3a8c854370629abbf8a"
    )


@pytest.mark.parametrize("field", ["digest", "length"])
def test_d5_registered_metadata_mismatch_is_rejected(tmp_path: Path, field: str):
    path = tmp_path / "raw.txt"
    path.write_bytes(_content("20260721"))
    spec = _spec(path, "qmt-batch-1", 1)
    if field == "digest":
        spec = QmtRegisteredBatchSpec(
            spec.batch_id,
            spec.sequence,
            spec.local_path,
            spec.artifact_id,
            "0" * 64,
            spec.byte_length,
        )
    else:
        spec = QmtRegisteredBatchSpec(
            spec.batch_id,
            spec.sequence,
            spec.local_path,
            spec.artifact_id,
            spec.artifact_sha256,
            spec.byte_length + 1,
        )
    with pytest.raises(ValueError):
        run_coverage_probe(
            (spec,),
            _profile("2026-07-21", "2026-07-21"),
            evidence_id="qmt-sh-600028-coverage-probe-v1",
            observed_at_utc="2026-07-22T21:35:27Z",
        )


def test_d5_sequence_directory_and_symlink_are_rejected(tmp_path: Path):
    path = tmp_path / "raw.txt"
    path.write_bytes(_content("20260721"))
    wrong_sequence = _spec(path, "qmt-batch-1", 2)
    with pytest.raises(ValueError):
        run_coverage_probe(
            (wrong_sequence,),
            _profile("2026-07-21", "2026-07-21"),
            evidence_id="qmt-sh-600028-coverage-probe-v1",
            observed_at_utc="2026-07-22T21:35:27Z",
        )
    directory = QmtRegisteredBatchSpec(
        "qmt-batch-1", 1, tmp_path, "qmt-dir-artifact", "0" * 64, 1
    )
    with pytest.raises(ValueError):
        run_coverage_probe(
            (directory,),
            _profile("2026-07-21", "2026-07-21"),
            evidence_id="qmt-sh-600028-coverage-probe-v1",
            observed_at_utc="2026-07-22T21:35:27Z",
        )
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(path)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    link_spec = _spec(link, "qmt-link-batch", 1)
    with pytest.raises(ValueError):
        run_coverage_probe(
            (link_spec,),
            _profile("2026-07-21", "2026-07-21"),
            evidence_id="qmt-sh-600028-coverage-probe-v1",
            observed_at_utc="2026-07-22T21:35:27Z",
        )
