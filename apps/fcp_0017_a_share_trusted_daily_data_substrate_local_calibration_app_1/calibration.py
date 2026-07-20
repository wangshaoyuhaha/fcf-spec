from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path

from .contracts import (
    CANONICAL_COLUMNS,
    AShareDailyObservation,
    DailyCalibrationResult,
    DailyLayerManifest,
    RegisteredDailyArtifact,
    canonical_sha256,
    instant,
)


def _integer(value: object, name: str) -> int:
    normalized = str(value).strip()
    if not normalized.isdigit():
        raise ValueError(f"{name} must be a nonnegative integer")
    return int(normalized)


def calibrate_registered_a_share_daily_csv(
    file_path: str | Path,
    registration: RegisteredDailyArtifact,
    *,
    as_of_utc: str,
) -> DailyCalibrationResult:
    if not isinstance(registration, RegisteredDailyArtifact):
        raise TypeError("registration must be RegisteredDailyArtifact")
    as_of = instant(as_of_utc, "as_of_utc")
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered local daily artifact not found: {path}")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered artifact byte length mismatch")
    raw_sha256 = hashlib.sha256(raw).hexdigest()
    if raw_sha256 != registration.artifact_sha256:
        raise ValueError("registered artifact SHA-256 mismatch")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("canonical daily calibration CSV must be ASCII") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != CANONICAL_COLUMNS:
        raise ValueError("canonical daily calibration columns are not exact")
    rows: list[AShareDailyObservation] = []
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("canonical daily calibration row is malformed")
        factor_text = row["adjustment_factor"].strip()
        factor_version = row["factor_version"].strip() or None
        observation = AShareDailyObservation(
            instrument_id=row["instrument_id"],
            trade_date=row["trade_date"],
            raw_open=row["raw_open"],
            raw_high=row["raw_high"],
            raw_low=row["raw_low"],
            raw_close=row["raw_close"],
            volume=_integer(row["volume"], "volume"),
            amount=row["amount"],
            adjustment_factor=factor_text or None,
            factor_version=factor_version,
            factor_available_at_utc=row["factor_available_at_utc"].strip() or None,
            event_at_utc=row["event_at_utc"],
            available_at_utc=row["available_at_utc"],
            first_tradable_at_utc=row["first_tradable_at_utc"],
            ingested_at_utc=row["ingested_at_utc"],
            revision_at_utc=row["revision_at_utc"],
            trading_status=row["trading_status"],
            source_artifact_sha256=raw_sha256,
        )
        if instant(observation.available_at_utc, "available_at_utc") > as_of:
            raise ValueError("point-in-time calibration cannot read future availability")
        if observation.factor_available_at_utc is not None and instant(
            observation.factor_available_at_utc,
            "factor_available_at_utc",
        ) > as_of:
            raise ValueError("point-in-time calibration cannot read a future adjustment factor")
        if instant(observation.revision_at_utc, "revision_at_utc") > as_of:
            raise ValueError("point-in-time calibration cannot read a future revision")
        rows.append(observation)
    if not rows:
        raise ValueError("canonical daily calibration CSV must not be empty")
    keys = tuple((item.instrument_id, item.trade_date) for item in rows)
    if len(keys) != len(set(keys)):
        raise ValueError("canonical daily calibration contains duplicate keys")
    if keys != tuple(sorted(keys)):
        raise ValueError("canonical daily calibration rows are not deterministically ordered")

    raw_payloads = [dict(item.raw_payload()) for item in rows]
    normalized_sha256 = canonical_sha256(raw_payloads)
    findings: list[str] = []
    if registration.rights_state == "UNRESOLVED":
        findings.append("COMMERCIAL_RIGHTS_UNRESOLVED")
    if registration.retention_state == "UNRESOLVED":
        findings.append("RETENTION_RIGHTS_UNRESOLVED")
    if any(item.adjustment_factor is None for item in rows):
        findings.append("ADJUSTMENT_FACTOR_MISSING")
    if any(item.trading_status == "UNKNOWN" for item in rows):
        findings.append("TRADING_STATUS_UNKNOWN")
    research_payloads = (
        [dict(item.research_payload()) for item in rows]
        if not any(item.adjustment_factor is None for item in rows)
        else []
    )
    research_sha256 = canonical_sha256(
        research_payloads if research_payloads else {"state": "BLOCKED", "findings": sorted(findings)}
    )
    manifests = (
        DailyLayerManifest(
            layer="RAW",
            artifact_id=registration.artifact_id,
            content_sha256=raw_sha256,
            parent_sha256=raw_sha256,
            record_count=len(rows),
            schema_version="a-share-daily-v1",
            transform_id="registered-local-bytes-v1",
            rights_state=registration.rights_state,
            retention_state=registration.retention_state,
        ),
        DailyLayerManifest(
            layer="NORMALIZED",
            artifact_id=f"{registration.artifact_id}-normalized",
            content_sha256=normalized_sha256,
            parent_sha256=raw_sha256,
            record_count=len(rows),
            schema_version="a-share-daily-v1",
            transform_id="exact-daily-normalization-v1",
            rights_state=registration.rights_state,
            retention_state="LOCAL_DERIVED_ONLY",
        ),
        DailyLayerManifest(
            layer="RESEARCH",
            artifact_id=f"{registration.artifact_id}-research",
            content_sha256=research_sha256,
            parent_sha256=normalized_sha256,
            record_count=len(research_payloads),
            schema_version="a-share-daily-v1",
            transform_id="forward-adjusted-view-v1",
            rights_state=registration.rights_state,
            retention_state="LOCAL_DERIVED_ONLY",
        ),
    )
    return DailyCalibrationResult(
        observations=tuple(rows),
        manifests=manifests,
        quality_state="BLOCKED" if findings else "READY_FOR_RESEARCH",
        finding_codes=tuple(findings),
        as_of_utc=as_of_utc,
    )
