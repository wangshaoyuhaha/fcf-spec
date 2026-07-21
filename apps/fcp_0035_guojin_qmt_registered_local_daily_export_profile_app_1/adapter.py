from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    instant,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)

from .contracts import (
    NORMALIZED_COLUMNS,
    QMT_SOURCE_COLUMNS,
    QmtFrontAdjustmentReference,
    QmtLocalDailyExportProfile,
    QmtLocalDailyNormalizationManifest,
    QmtLocalDailyNormalizationResult,
)


@dataclass(frozen=True)
class _QmtRow:
    trade_date: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    lots: int
    amount: Decimal


def _decimal(value: object, name: str, *, positive: bool = False) -> Decimal:
    normalized = str(value).strip()
    try:
        result = Decimal(normalized)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be a finite decimal") from exc
    if not result.is_finite() or result < 0 or (positive and result <= 0):
        raise ValueError(f"{name} is outside the allowed range")
    return result


def _verify_bytes(
    file_path: str | Path, registration: RegisteredLocalDailyExport
) -> bytes:
    if not isinstance(registration, RegisteredLocalDailyExport):
        raise TypeError("registration must be RegisteredLocalDailyExport")
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered QMT export not found: {path}")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered QMT export byte length mismatch")
    if hashlib.sha256(raw).hexdigest() != registration.artifact_sha256:
        raise ValueError("registered QMT export SHA-256 mismatch")
    return raw


def _parse(raw: bytes, profile: QmtLocalDailyExportProfile) -> tuple[_QmtRow, ...]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("registered QMT export must be ASCII") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != QMT_SOURCE_COLUMNS:
        raise ValueError("registered QMT export columns are not exact")
    rows: list[_QmtRow] = []
    seen: set[str] = set()
    previous: str | None = None
    for source in reader:
        if None in source or any(value is None for value in source.values()):
            raise ValueError("registered QMT export row is malformed")
        try:
            parsed_date = datetime.strptime(source["timetag"].strip(), "%Y%m%d").date()
        except (TypeError, ValueError) as exc:
            raise ValueError("QMT timetag must be a valid YYYYMMDD date") from exc
        trade_date = parsed_date.isoformat()
        if not profile.requested_start_date <= trade_date <= profile.requested_end_date:
            raise ValueError("QMT row is outside the registered requested range")
        if trade_date in seen:
            raise ValueError("registered QMT export contains duplicate dates")
        if previous is not None and trade_date <= previous:
            raise ValueError("registered QMT export is not ordered by date")
        seen.add(trade_date)
        previous = trade_date
        open_value = _decimal(source["open"], "open", positive=True)
        high_value = _decimal(source["high"], "high", positive=True)
        low_value = _decimal(source["low"], "low", positive=True)
        close_value = _decimal(source["close"], "close", positive=True)
        if high_value < max(open_value, low_value, close_value):
            raise ValueError("QMT high price violates OHLC invariants")
        if low_value > min(open_value, high_value, close_value):
            raise ValueError("QMT low price violates OHLC invariants")
        lots_decimal = _decimal(source["volumn"], "volumn")
        if lots_decimal != lots_decimal.to_integral_value():
            raise ValueError("QMT volumn must contain integral lots")
        lots = int(lots_decimal)
        amount = _decimal(source["amount"], "amount")
        rows.append(
            _QmtRow(
                trade_date=trade_date,
                open=open_value,
                high=high_value,
                low=low_value,
                close=close_value,
                lots=lots,
                amount=amount,
            )
        )
    if not rows:
        raise ValueError("registered QMT export must not be empty")
    return tuple(rows)


def normalize_registered_qmt_daily_export(
    file_path: str | Path,
    registration: RegisteredLocalDailyExport,
    profile: QmtLocalDailyExportProfile,
    *,
    output_artifact_id: str,
    as_of_utc: str,
) -> QmtLocalDailyNormalizationResult:
    if not isinstance(profile, QmtLocalDailyExportProfile):
        raise TypeError("profile must be QmtLocalDailyExportProfile")
    if registration.source_id != profile.source_id:
        raise ValueError("QMT profile and export source lineage disagree")
    instant(as_of_utc, "as_of_utc")
    raw = _verify_bytes(file_path, registration)
    rows = _parse(raw, profile)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=NORMALIZED_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "code": profile.code,
                "exchange": profile.exchange,
                "date": row.trade_date,
                "open": canonical_decimal(row.open),
                "high": canonical_decimal(row.high),
                "low": canonical_decimal(row.low),
                "close": canonical_decimal(row.close),
                "volume": row.lots * profile.volume_lot_size,
                "amount": canonical_decimal(row.amount),
            }
        )
    normalized = stream.getvalue().encode("ascii")
    normalized_sha256 = hashlib.sha256(normalized).hexdigest()
    findings = {
        "ADJUSTMENT_FACTOR_MISSING",
        "POINT_IN_TIME_SUPPLEMENTS_MISSING",
        "TRADING_STATUS_UNKNOWN",
    }
    actual_start = rows[0].trade_date
    actual_end = rows[-1].trade_date
    if actual_start != profile.requested_start_date:
        findings.add("REQUESTED_RANGE_START_MISMATCH")
    if actual_end != profile.requested_end_date:
        findings.add("REQUESTED_RANGE_END_MISMATCH")
    normalized_registration = RegisteredLocalDailyExport(
        artifact_id=output_artifact_id,
        source_id=profile.source_id,
        artifact_sha256=normalized_sha256,
        byte_length=len(normalized),
        registered_at_utc=as_of_utc,
        rights_state=registration.rights_state,
        retention_state="LOCAL_DERIVED_ONLY",
    )
    manifest = QmtLocalDailyNormalizationManifest(
        source_artifact_sha256=registration.artifact_sha256,
        profile_hash=profile.profile_hash,
        normalized_artifact_sha256=normalized_sha256,
        row_count=len(rows),
        actual_start_date=actual_start,
        actual_end_date=actual_end,
        finding_codes=tuple(findings),
    )
    return QmtLocalDailyNormalizationResult(
        normalized_csv=normalized,
        normalized_registration=normalized_registration,
        bridge_profile=profile.bridge_profile(),
        manifest=manifest,
        quality_state="BLOCKED_PENDING_SUPPLEMENTS",
        finding_codes=tuple(findings),
    )


def compare_registered_qmt_front_adjustment(
    raw_file_path: str | Path,
    raw_registration: RegisteredLocalDailyExport,
    front_file_path: str | Path,
    front_registration: RegisteredLocalDailyExport,
    profile: QmtLocalDailyExportProfile,
) -> QmtFrontAdjustmentReference:
    if raw_registration.source_id != profile.source_id:
        raise ValueError("raw QMT source lineage disagrees with profile")
    if front_registration.source_id != profile.source_id:
        raise ValueError("front QMT source lineage disagrees with profile")
    raw_bytes = _verify_bytes(raw_file_path, raw_registration)
    front_bytes = _verify_bytes(front_file_path, front_registration)
    raw_rows = _parse(raw_bytes, profile)
    front_rows = _parse(front_bytes, profile)
    if len(raw_rows) != len(front_rows):
        raise ValueError("QMT raw and front exports have different row counts")
    boundaries: list[str] = []
    previous_offset: Decimal | None = None
    for raw_row, front_row in zip(raw_rows, front_rows, strict=True):
        if raw_row.trade_date != front_row.trade_date:
            raise ValueError("QMT raw and front dates are not aligned")
        if raw_row.lots != front_row.lots or raw_row.amount != front_row.amount:
            raise ValueError("QMT front adjustment changed volume or amount")
        offsets = (
            raw_row.open - front_row.open,
            raw_row.high - front_row.high,
            raw_row.low - front_row.low,
            raw_row.close - front_row.close,
        )
        if max(offsets) - min(offsets) > Decimal("0.01"):
            raise ValueError("QMT front adjustment is not a consistent cash offset")
        offset = raw_row.close - front_row.close
        if previous_offset is not None and offset != previous_offset:
            boundaries.append(raw_row.trade_date)
        previous_offset = offset
    if previous_offset is None:
        raise ValueError("QMT adjustment comparison requires rows")
    return QmtFrontAdjustmentReference(
        raw_artifact_sha256=raw_registration.artifact_sha256,
        front_artifact_sha256=front_registration.artifact_sha256,
        profile_hash=profile.profile_hash,
        row_count=len(raw_rows),
        boundary_dates=tuple(boundaries),
        latest_cash_offset=previous_offset,
    )
