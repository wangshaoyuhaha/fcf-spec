from __future__ import annotations

import csv
import hashlib
import io
from datetime import date
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    instant,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)
from apps.fcp_0036_guojin_qmt_registered_local_daily_batch_coverage_reconciliation_app_1 import (
    RegisteredExpectedTradingDateSet,
)

from .contracts import (
    EXPECTED_DATE_COLUMNS,
    RegisteredExpectedTradingDateArtifact,
    RegisteredExpectedTradingDateProfile,
    TradingDateArtifactManifest,
)


def _read_exact_bytes(
    file_path: str | Path,
    registration: RegisteredExpectedTradingDateArtifact,
) -> bytes:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered trading-date artifact not found: {path}")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered trading-date artifact byte length mismatch")
    if hashlib.sha256(raw).hexdigest() != registration.artifact_sha256:
        raise ValueError("registered trading-date artifact SHA-256 mismatch")
    return raw


def _parse_dates(raw: bytes) -> tuple[str, ...]:
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("trading-date artifact must be ASCII") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != EXPECTED_DATE_COLUMNS:
        raise ValueError("trading-date artifact columns are not exact")
    values: list[str] = []
    for row in reader:
        if None in row or row.get("trade_date") is None:
            raise ValueError("trading-date artifact row is malformed")
        raw_date = row["trade_date"]
        if raw_date != raw_date.strip():
            raise ValueError("trade_date must use canonical ISO text")
        try:
            parsed = date.fromisoformat(raw_date).isoformat()
        except (TypeError, ValueError) as exc:
            raise ValueError("trade_date must be an ISO date") from exc
        if parsed != raw_date:
            raise ValueError("trade_date must use canonical ISO text")
        values.append(parsed)
    if not values:
        raise ValueError("trading-date artifact must not be empty")
    if values != sorted(set(values)):
        raise ValueError("trading dates must be ordered and unique")
    return tuple(values)


def load_registered_expected_trading_dates(
    file_path: str | Path,
    registration: RegisteredExpectedTradingDateArtifact,
    *,
    as_of_utc: str,
) -> RegisteredExpectedTradingDateProfile:
    if not isinstance(registration, RegisteredExpectedTradingDateArtifact):
        raise TypeError("registration must be RegisteredExpectedTradingDateArtifact")
    as_of = instant(as_of_utc, "as_of_utc")
    if instant(registration.revision_at_utc, "revision_at_utc") > as_of:
        raise ValueError("calendar profile cannot consume a future revision")
    raw = _read_exact_bytes(file_path, registration)
    dates = _parse_dates(raw)
    if (
        dates[0] != registration.declared_start_date
        or dates[-1] != registration.declared_end_date
    ):
        raise ValueError("declared coverage range disagrees with artifact dates")
    date_set_hash = canonical_sha256(
        {
            "dates": dates,
            "instrument_id": registration.instrument_id,
            "market_id": registration.market_id,
            "registration_hash": registration.registration_hash,
            "source_id": registration.source_id,
            "source_revision_id": registration.source_revision_id,
        }
    )
    findings = {"EXACT_REGISTERED_TRADING_DATES"}
    quality_state = "REGISTERED_EXPECTED_DATES_READY"
    if registration.rights_state == "UNRESOLVED":
        findings.add("RIGHTS_UNRESOLVED")
        quality_state = "REVIEW_REQUIRED_UNRESOLVED_RIGHTS"
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
        quality_state=quality_state,
        finding_codes=tuple(findings),
    )
    return RegisteredExpectedTradingDateProfile(
        registration=registration,
        dates=dates,
        manifest=manifest,
    )


def to_fcp_0036_expected_date_set(
    profile: RegisteredExpectedTradingDateProfile,
) -> RegisteredExpectedTradingDateSet:
    if not isinstance(profile, RegisteredExpectedTradingDateProfile):
        raise TypeError("profile must be RegisteredExpectedTradingDateProfile")
    registration = profile.registration
    legacy_registration = RegisteredLocalDailyExport(
        artifact_id=registration.artifact_id,
        source_id=registration.source_id,
        artifact_sha256=registration.artifact_sha256,
        byte_length=registration.byte_length,
        registered_at_utc=registration.registered_at_utc,
        rights_state=registration.rights_state,
        retention_state=registration.retention_state,
        usage_scope=registration.usage_scope,
    )
    return RegisteredExpectedTradingDateSet(
        registration=legacy_registration,
        instrument_id=registration.instrument_id,
    )
