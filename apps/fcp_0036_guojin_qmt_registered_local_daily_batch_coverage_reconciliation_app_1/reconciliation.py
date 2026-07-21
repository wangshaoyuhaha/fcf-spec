from __future__ import annotations

import csv
import hashlib
import io
from datetime import date
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    instant,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    NORMALIZED_COLUMNS,
    QmtLocalDailyExportProfile,
    normalize_registered_qmt_daily_export,
)

from .contracts import (
    EXPECTED_DATE_COLUMNS,
    QmtBatchCoverageManifest,
    QmtBatchCoverageReconciliationResult,
    RegisteredExpectedTradingDateSet,
    RegisteredQmtDailyBatch,
)


def _verify_registered_bytes(
    file_path: str | Path,
    registration: RegisteredLocalDailyExport,
) -> bytes:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered local artifact not found: {path}")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered local artifact byte length mismatch")
    if hashlib.sha256(raw).hexdigest() != registration.artifact_sha256:
        raise ValueError("registered local artifact SHA-256 mismatch")
    return raw


def _parse_expected_dates(
    file_path: str | Path,
    expected: RegisteredExpectedTradingDateSet,
) -> tuple[str, ...]:
    raw = _verify_registered_bytes(file_path, expected.registration)
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("expected trading-date artifact must be ASCII") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != EXPECTED_DATE_COLUMNS:
        raise ValueError("expected trading-date columns are not exact")
    values: list[str] = []
    for row in reader:
        if None in row or row.get("trade_date") is None:
            raise ValueError("expected trading-date row is malformed")
        value = row["trade_date"].strip()
        try:
            parsed = date.fromisoformat(value).isoformat()
        except (TypeError, ValueError) as exc:
            raise ValueError("expected trade_date must be an ISO date") from exc
        values.append(parsed)
    if not values:
        raise ValueError("expected trading-date artifact must not be empty")
    if values != sorted(set(values)):
        raise ValueError("expected trading dates must be unique and ordered")
    return tuple(values)


def _normalized_rows(raw: bytes) -> tuple[tuple[str, ...], ...]:
    text = raw.decode("ascii")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != NORMALIZED_COLUMNS:
        raise ValueError("normalized batch columns are not exact")
    rows: list[tuple[str, ...]] = []
    for row in reader:
        if None in row or any(row.get(column) is None for column in NORMALIZED_COLUMNS):
            raise ValueError("normalized batch row is malformed")
        rows.append(tuple(row[column] for column in NORMALIZED_COLUMNS))
    if not rows:
        raise ValueError("normalized batch must not be empty")
    return tuple(rows)


def reconcile_registered_qmt_daily_batches(
    batches: tuple[RegisteredQmtDailyBatch, ...],
    profile: QmtLocalDailyExportProfile,
    expected_dates_file_path: str | Path,
    expected_dates: RegisteredExpectedTradingDateSet,
    *,
    output_artifact_id: str,
    as_of_utc: str,
    declared_row_cap: int = 500,
) -> QmtBatchCoverageReconciliationResult:
    if not isinstance(profile, QmtLocalDailyExportProfile):
        raise TypeError("profile must be QmtLocalDailyExportProfile")
    if not isinstance(expected_dates, RegisteredExpectedTradingDateSet):
        raise TypeError("expected_dates must be RegisteredExpectedTradingDateSet")
    if expected_dates.instrument_id != profile.instrument_id:
        raise ValueError("expected dates and QMT profile instrument disagree")
    if (
        isinstance(declared_row_cap, bool)
        or not isinstance(declared_row_cap, int)
        or declared_row_cap <= 0
    ):
        raise ValueError("declared_row_cap must be a positive integer")
    instant(as_of_utc, "as_of_utc")
    if not isinstance(batches, tuple) or not batches:
        raise ValueError("batches must be a nonempty tuple")
    if not all(isinstance(batch, RegisteredQmtDailyBatch) for batch in batches):
        raise TypeError("batches must contain RegisteredQmtDailyBatch values")
    sequences = tuple(batch.sequence for batch in batches)
    if sequences != tuple(range(1, len(batches) + 1)):
        raise ValueError("batch sequence must be ordered and contiguous")
    batch_ids = tuple(batch.batch_id for batch in batches)
    if len(batch_ids) != len(set(batch_ids)):
        raise ValueError("batch identifiers must be unique")
    if any(batch.registration.source_id != profile.source_id for batch in batches):
        raise ValueError("batch source lineage disagrees with QMT profile")

    expected = _parse_expected_dates(expected_dates_file_path, expected_dates)
    expected_set = set(expected)
    selected: dict[str, tuple[str, ...]] = {}
    conflicts: set[str] = set()
    duplicate_count = 0
    row_cap_batches: list[str] = []
    normalization_manifest_hashes: list[str] = []
    findings = {
        "ADJUSTMENT_FACTOR_MISSING",
        "POINT_IN_TIME_SUPPLEMENTS_MISSING",
        "TRADING_STATUS_UNKNOWN",
    }

    for batch in batches:
        normalized = normalize_registered_qmt_daily_export(
            batch.file_path,
            batch.registration,
            profile,
            output_artifact_id=f"{output_artifact_id}-batch-{batch.sequence}",
            as_of_utc=as_of_utc,
        )
        normalization_manifest_hashes.append(normalized.manifest.manifest_hash)
        if normalized.manifest.row_count == declared_row_cap:
            row_cap_batches.append(batch.batch_id)
        for row in _normalized_rows(normalized.normalized_csv):
            trade_date = row[2]
            if trade_date in conflicts:
                continue
            previous = selected.get(trade_date)
            if previous is None:
                selected[trade_date] = row
            elif previous == row:
                duplicate_count += 1
            else:
                conflicts.add(trade_date)
                selected.pop(trade_date, None)

    actual_dates = set(selected)
    missing = tuple(sorted(expected_set - actual_dates))
    unexpected = tuple(sorted(actual_dates - expected_set))
    if duplicate_count:
        findings.add("IDENTICAL_OVERLAP_DEDUPLICATED")
    if row_cap_batches:
        findings.add("DECLARED_ROW_CAP_OBSERVED")
    if missing:
        findings.add("EXPECTED_TRADING_DATES_MISSING")
    if unexpected:
        findings.add("UNREGISTERED_TRADING_DATES_PRESENT")
    if conflicts:
        findings.add("CONFLICTING_OVERLAP_QUARANTINED")

    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(NORMALIZED_COLUMNS)
    for trade_date in sorted(selected):
        writer.writerow(selected[trade_date])
    merged = stream.getvalue().encode("ascii")
    merged_sha256 = hashlib.sha256(merged).hexdigest()
    merged_registration = RegisteredLocalDailyExport(
        artifact_id=output_artifact_id,
        source_id=profile.source_id,
        artifact_sha256=merged_sha256,
        byte_length=len(merged),
        registered_at_utc=as_of_utc,
        rights_state=(
            "DECLARED_LOCAL_RESEARCH"
            if all(
                batch.registration.rights_state == "DECLARED_LOCAL_RESEARCH"
                for batch in batches
            )
            and expected_dates.registration.rights_state
            == "DECLARED_LOCAL_RESEARCH"
            else "UNRESOLVED"
        ),
        retention_state="LOCAL_DERIVED_ONLY",
    )
    manifest = QmtBatchCoverageManifest(
        instrument_id=profile.instrument_id,
        profile_hash=profile.profile_hash,
        expected_date_set_hash=expected_dates.date_set_hash,
        expected_artifact_sha256=expected_dates.registration.artifact_sha256,
        ordered_batch_hashes=tuple(batch.batch_hash for batch in batches),
        ordered_source_artifact_sha256s=tuple(
            batch.registration.artifact_sha256 for batch in batches
        ),
        ordered_normalization_manifest_hashes=tuple(normalization_manifest_hashes),
        merged_artifact_sha256=merged_sha256,
        row_count=len(selected),
        expected_date_count=len(expected),
        identical_overlap_count=duplicate_count,
        missing_dates=missing,
        unexpected_dates=unexpected,
        conflict_dates=tuple(sorted(conflicts)),
        row_cap_batch_ids=tuple(row_cap_batches),
        finding_codes=tuple(findings),
    )
    quality_state = (
        "QUARANTINED_CONFLICT"
        if conflicts
        else "BLOCKED_COVERAGE_MISMATCH"
        if missing or unexpected
        else "COVERAGE_RECONCILED_CANONICAL_SUPPLEMENTS_REQUIRED"
    )
    return QmtBatchCoverageReconciliationResult(
        merged_csv=merged,
        merged_registration=merged_registration,
        bridge_profile=profile.bridge_profile(),
        manifest=manifest,
        quality_state=quality_state,
        finding_codes=tuple(findings),
    )
