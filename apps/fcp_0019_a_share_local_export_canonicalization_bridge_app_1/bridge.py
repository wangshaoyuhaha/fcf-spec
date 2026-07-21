from __future__ import annotations

import csv
import hashlib
import io
import re
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    CANONICAL_COLUMNS,
    AShareDailyObservation,
    RegisteredDailyArtifact,
    canonical_decimal,
    canonical_sha256,
    instant,
)

from .contracts import (
    AShareDailyRowSupplement,
    LocalDailyExportBridgeManifest,
    LocalDailyExportBridgeResult,
    LocalDailyExportProfile,
    RegisteredLocalDailyExport,
)


_CODE = re.compile(r"^[0-9]{6}$")
_EXCHANGES = {
    "SH": "XSHG",
    "SSE": "XSHG",
    "XSHG": "XSHG",
    "SZ": "XSHE",
    "SZSE": "XSHE",
    "XSHE": "XSHE",
}


def _integer(value: object, name: str) -> int:
    normalized = str(value).strip()
    if not normalized.isdigit():
        raise ValueError(f"{name} must be a nonnegative integer")
    return int(normalized)


def _instrument(row: dict[str, str], profile: LocalDailyExportProfile) -> str:
    mapping = profile.canonical_to_source
    if profile.instrument_format == "CANONICAL":
        return row[mapping["instrument_id"]].strip().upper()
    code = row[mapping["instrument_code"]].strip()
    exchange = _EXCHANGES.get(row[mapping["exchange"]].strip().upper())
    if _CODE.fullmatch(code) is None or exchange is None:
        raise ValueError("source instrument code or exchange is invalid")
    return f"{code}.{exchange}"


def canonicalize_registered_local_daily_export(
    file_path: str | Path,
    registration: RegisteredLocalDailyExport,
    profile: LocalDailyExportProfile,
    supplements: tuple[AShareDailyRowSupplement, ...],
    *,
    output_artifact_id: str,
    as_of_utc: str,
) -> LocalDailyExportBridgeResult:
    if not isinstance(registration, RegisteredLocalDailyExport):
        raise TypeError("registration must be RegisteredLocalDailyExport")
    if not isinstance(profile, LocalDailyExportProfile):
        raise TypeError("profile must be LocalDailyExportProfile")
    if profile.source_id != registration.source_id:
        raise ValueError("profile and export source lineage disagree")
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered local export not found: {path}")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered local export byte length mismatch")
    source_sha256 = hashlib.sha256(raw).hexdigest()
    if source_sha256 != registration.artifact_sha256:
        raise ValueError("registered local export SHA-256 mismatch")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("registered local export must be UTF-8") from exc
    warnings: list[str] = []
    if text.startswith("\ufeff"):
        text = text[1:]
        warnings.append("SOURCE_UTF8_BOM_NORMALIZED")
    if "\ufeff" in text:
        raise ValueError("registered local export contains an embedded BOM")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != profile.source_columns:
        raise ValueError("registered local export columns do not match profile")

    supplement_rows = tuple(supplements)
    if not supplement_rows or not all(
        isinstance(item, AShareDailyRowSupplement) for item in supplement_rows
    ):
        raise ValueError("explicit typed row supplements are required")
    supplement_map = {item.key: item for item in supplement_rows}
    if len(supplement_map) != len(supplement_rows):
        raise ValueError("row supplement keys must be unique")
    as_of = instant(as_of_utc, "as_of_utc")
    rows: list[AShareDailyObservation] = []
    observed_keys: set[tuple[str, str]] = set()
    mapping = profile.canonical_to_source
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("registered local export row is malformed")
        instrument_id = _instrument(row, profile)
        trade_date = row[mapping["trade_date"]].strip()
        key = (instrument_id, trade_date)
        if key in observed_keys:
            raise ValueError("registered local export contains duplicate keys")
        observed_keys.add(key)
        supplement = supplement_map.get(key)
        if supplement is None:
            raise ValueError("registered local export row lacks point-in-time supplement")
        if instant(supplement.revision_at_utc, "revision_at_utc") > as_of:
            raise ValueError("bridge cannot consume a future revision")
        if (
            supplement.factor_available_at_utc is not None
            and instant(supplement.factor_available_at_utc, "factor_available_at_utc")
            > as_of
        ):
            raise ValueError("bridge cannot consume a future adjustment factor")
        rows.append(
            AShareDailyObservation(
                instrument_id=instrument_id,
                trade_date=trade_date,
                raw_open=row[mapping["raw_open"]],
                raw_high=row[mapping["raw_high"]],
                raw_low=row[mapping["raw_low"]],
                raw_close=row[mapping["raw_close"]],
                volume=_integer(row[mapping["volume"]], "volume"),
                amount=row[mapping["amount"]],
                adjustment_factor=supplement.adjustment_factor,
                factor_version=supplement.factor_version,
                factor_available_at_utc=supplement.factor_available_at_utc,
                event_at_utc=supplement.event_at_utc,
                available_at_utc=supplement.available_at_utc,
                first_tradable_at_utc=supplement.first_tradable_at_utc,
                ingested_at_utc=supplement.ingested_at_utc,
                revision_at_utc=supplement.revision_at_utc,
                trading_status=supplement.trading_status,
                source_artifact_sha256=source_sha256,
            )
        )
    if not rows:
        raise ValueError("registered local export must not be empty")
    if set(supplement_map) != observed_keys:
        raise ValueError("row supplements contain unobserved export keys")
    rows.sort(key=lambda item: (item.instrument_id, item.trade_date))

    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=CANONICAL_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "instrument_id": row.instrument_id,
                "trade_date": row.trade_date,
                "raw_open": canonical_decimal(row.raw_open),
                "raw_high": canonical_decimal(row.raw_high),
                "raw_low": canonical_decimal(row.raw_low),
                "raw_close": canonical_decimal(row.raw_close),
                "volume": row.volume,
                "amount": canonical_decimal(row.amount),
                "adjustment_factor": (
                    canonical_decimal(row.adjustment_factor)
                    if row.adjustment_factor is not None
                    else ""
                ),
                "factor_version": row.factor_version or "",
                "factor_available_at_utc": row.factor_available_at_utc or "",
                "event_at_utc": row.event_at_utc,
                "available_at_utc": row.available_at_utc,
                "first_tradable_at_utc": row.first_tradable_at_utc,
                "ingested_at_utc": row.ingested_at_utc,
                "revision_at_utc": row.revision_at_utc,
                "trading_status": row.trading_status,
            }
        )
    canonical_csv = stream.getvalue().encode("ascii")
    canonical_sha256_digest = hashlib.sha256(canonical_csv).hexdigest()
    findings: list[str] = []
    if registration.rights_state == "UNRESOLVED":
        findings.append("COMMERCIAL_RIGHTS_UNRESOLVED")
    if registration.retention_state == "UNRESOLVED":
        findings.append("RETENTION_RIGHTS_UNRESOLVED")
    if any(item.adjustment_factor is None for item in rows):
        findings.append("ADJUSTMENT_FACTOR_MISSING")
    if any(item.trading_status == "UNKNOWN" for item in rows):
        findings.append("TRADING_STATUS_UNKNOWN")
    supplement_hash = canonical_sha256(
        [item.supplement_hash for item in sorted(supplement_rows, key=lambda item: item.key)]
    )
    canonical_registration = RegisteredDailyArtifact(
        artifact_id=output_artifact_id,
        source_id=profile.source_id,
        artifact_sha256=canonical_sha256_digest,
        byte_length=len(canonical_csv),
        registered_at_utc=as_of_utc,
        rights_state=registration.rights_state,
        retention_state="LOCAL_DERIVED_ONLY",
    )
    manifest = LocalDailyExportBridgeManifest(
        source_artifact_sha256=source_sha256,
        profile_hash=profile.profile_hash,
        supplement_set_hash=supplement_hash,
        canonical_artifact_sha256=canonical_sha256_digest,
        row_count=len(rows),
        warning_codes=tuple(warnings),
    )
    return LocalDailyExportBridgeResult(
        canonical_csv=canonical_csv,
        canonical_registration=canonical_registration,
        manifest=manifest,
        quality_state="BLOCKED" if findings else "READY_FOR_CALIBRATION",
        finding_codes=tuple(findings),
    )
