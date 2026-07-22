import csv
import json
from dataclasses import FrozenInstanceError, asdict, replace
from pathlib import Path

import pytest

import apps.fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1 as fcp_0075
from apps.fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1 import (
    QUARANTINE_REASONS,
    scan_candidate_daily_corpus,
)
from apps.fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1.scanner import (
    EXPECTED_HEADER,
    HEADER_HASH,
)


OBSERVED_AT = "2026-07-23T00:30:00Z"


def _row(
    code,
    trade_date,
    *,
    open_price=10.0,
    high=11.0,
    low=9.0,
    close=10.0,
    previous_close=10.0,
    volume=100.0,
    amount=1000.0,
    float_market_value=10000.0,
    total_market_value=20000.0,
    reported_return=0.0,
    ratio=1.0,
):
    return (
        code,
        "Sample",
        trade_date,
        open_price,
        high,
        low,
        close,
        previous_close,
        volume,
        amount,
        float_market_value,
        total_market_value,
        reported_return,
        close * ratio,
        open_price * ratio,
        high * ratio,
        low * ratio,
    )


def _write(path, rows, header=EXPECTED_HEADER):
    with path.open("w", encoding="gb18030", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)


def _corpus(tmp_path):
    _write(
        tmp_path / "sh600000.csv",
        (
            _row("sh600000", "2024-04-22"),
            _row(
                "sh600000",
                "2024-04-23",
                high=12.0,
                low=10.0,
                close=11.0,
                reported_return=0.1,
                ratio=2.0,
            ),
        ),
    )
    _write(tmp_path / "sz000001.csv", (_row("sz000001", "2024-04-24"),))
    return tmp_path


def _scan(tmp_path):
    return scan_candidate_daily_corpus(_corpus(tmp_path), observed_at_utc=OBSERVED_AT)


def test_closed_quarantine_reasons_are_exact():
    assert QUARANTINE_REASONS == (
        "PROVIDER_UNVERIFIED",
        "RIGHTS_UNVERIFIED",
        "REVISION_LINEAGE_MISSING",
        "CORPORATE_ACTION_LINEAGE_MISSING",
        "ADJUSTMENT_FACTOR_AUTHORITY_MISSING",
        "TRADING_STATUS_AUTHORITY_MISSING",
        "EXPECTED_CALENDAR_MISSING",
        "POINT_IN_TIME_AVAILABILITY_MISSING",
    )


def test_valid_corpus_produces_path_free_quarantine_evidence(tmp_path):
    evidence = _scan(tmp_path)
    assert evidence.status == "QUARANTINED_UNVERIFIED_EXTERNAL_CANDIDATE"
    assert evidence.file_count == 2
    assert evidence.row_count == 3
    assert evidence.market_file_counts == (("bj", 0), ("sh", 1), ("sz", 1), ("other", 0))
    assert evidence.earliest_trade_date == "2024-04-22"
    assert evidence.latest_trade_date == "2024-04-24"
    assert evidence.latest_terminal_date == "2024-04-24"
    assert evidence.latest_terminal_file_count == 1
    assert evidence.stale_terminal_file_count == 1
    assert evidence.first_adjustment_ratio_unit_file_count == 2
    assert evidence.terminal_adjustment_ratio_nonunit_file_count == 1
    assert evidence.header_hash == HEADER_HASH
    serialized = repr(asdict(evidence))
    assert str(tmp_path) not in serialized
    assert "sh600000.csv" not in serialized


def test_scan_is_deterministic_for_same_corpus_and_clock(tmp_path):
    first = _scan(tmp_path)
    second = scan_candidate_daily_corpus(tmp_path, observed_at_utc=OBSERVED_AT)
    assert first == second


def test_registered_evidence_replays_exact_contract_hash():
    path = Path(
        "FCF_REGISTERED_EVIDENCE_FCP_0075_A_SHARE_EXTERNAL_CANDIDATE_DAILY_"
        "CORPUS_QUALITY_QUARANTINE.json"
    )
    payload = json.loads(path.read_text(encoding="ascii"))
    expected_hash = payload.pop("evidence_hash")
    evidence = fcp_0075.CandidateDailyCorpusQualityEvidence(**payload)
    assert evidence.evidence_hash == expected_hash
    assert evidence.quarantine_reasons == QUARANTINE_REASONS


def test_manifest_changes_when_candidate_bytes_change(tmp_path):
    first = _scan(tmp_path)
    _write(tmp_path / "sz000001.csv", (_row("sz000001", "2024-04-24", volume=101.0),))
    second = scan_candidate_daily_corpus(tmp_path, observed_at_utc=OBSERVED_AT)
    assert first.manifest_hash != second.manifest_hash
    assert first.evidence_hash != second.evidence_hash


def test_header_filename_and_unexpected_entries_are_counted(tmp_path):
    _write(tmp_path / "bad-name.csv", (_row("sh600000", "2024-04-22"),))
    _write(tmp_path / "sz000001.csv", (_row("sz000001", "2024-04-22"),), header=("bad",))
    (tmp_path / "notes.txt").write_text("not market data", encoding="ascii")
    evidence = scan_candidate_daily_corpus(tmp_path, observed_at_utc=OBSERVED_AT)
    assert evidence.file_count == 2
    assert evidence.invalid_filename_count == 1
    assert evidence.header_mismatch_file_count == 1
    assert evidence.unexpected_entry_count == 1


def test_code_duplicate_and_non_monotonic_dates_are_counted(tmp_path):
    _write(
        tmp_path / "sh600000.csv",
        (
            _row("sz000001", "2024-04-23"),
            _row("sh600000", "2024-04-23"),
            _row("sh600000", "2024-04-22"),
        ),
    )
    evidence = scan_candidate_daily_corpus(tmp_path, observed_at_utc=OBSERVED_AT)
    assert evidence.code_mismatch_row_count == 1
    assert evidence.duplicate_date_count == 1
    assert evidence.non_monotonic_date_count == 1


def test_numeric_quality_failures_are_counted_without_promotion(tmp_path):
    bad = list(
        _row(
            "sh600000",
            "2024-04-22",
            high=8.0,
            low=12.0,
            close=11.0,
            previous_close=10.0,
            volume=0.0,
            amount=-1.0,
            reported_return=0.0,
        )
    )
    bad[13:17] = (22.0, 10.0, 16.0, 24.0)
    _write(tmp_path / "sh600000.csv", (bad,))
    evidence = scan_candidate_daily_corpus(tmp_path, observed_at_utc=OBSERVED_AT)
    assert evidence.invalid_ohlc_row_count == 1
    assert evidence.negative_numeric_row_count == 1
    assert evidence.return_mismatch_row_count == 1
    assert evidence.adjustment_ratio_mismatch_row_count == 1
    assert evidence.zero_volume_row_count == 1
    assert evidence.registered_evidence_promotion_allowed is False
    assert evidence.factor_calculation_allowed is False
    assert evidence.training_label_allowed is False


@pytest.mark.parametrize(
    "rows",
    (
        (("too", "short"),),
        ((_row("sh600000", "2024-04-22")[:3] + ("not-a-number",) * 14),),
    ),
)
def test_malformed_rows_are_counted(tmp_path, rows):
    _write(tmp_path / "sh600000.csv", rows)
    _write(tmp_path / "sz000001.csv", (_row("sz000001", "2024-04-22"),))
    evidence = scan_candidate_daily_corpus(tmp_path, observed_at_utc=OBSERVED_AT)
    assert evidence.malformed_row_count == 1


def test_empty_or_invalid_root_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="no valid daily observations"):
        scan_candidate_daily_corpus(tmp_path, observed_at_utc=OBSERVED_AT)
    with pytest.raises(ValueError, match="real local directory"):
        scan_candidate_daily_corpus(tmp_path / "missing", observed_at_utc=OBSERVED_AT)


@pytest.mark.parametrize(
    "field,value",
    (
        ("status", "TRUSTED"),
        ("registered_evidence_promotion_allowed", True),
        ("factor_calculation_allowed", True),
        ("training_label_allowed", True),
        ("provider_selection_allowed", True),
        ("raw_rows_embedded", True),
    ),
)
def test_evidence_rejects_authority_escalation(tmp_path, field, value):
    with pytest.raises(ValueError, match="cannot be promoted or authoritative"):
        replace(_scan(tmp_path), **{field: value})


def test_evidence_rejects_quarantine_reason_substitution(tmp_path):
    with pytest.raises(ValueError, match="closed and mandatory"):
        replace(_scan(tmp_path), quarantine_reasons=QUARANTINE_REASONS[:-1])


def test_evidence_is_frozen(tmp_path):
    with pytest.raises(FrozenInstanceError):
        _scan(tmp_path).status = "changed"


def test_package_exports_are_closed():
    assert fcp_0075.__all__ == [
        "QUARANTINE_REASONS",
        "CandidateDailyCorpusQualityEvidence",
        "scan_candidate_daily_corpus",
    ]
