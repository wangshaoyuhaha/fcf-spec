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
    canonical_sha256,
    instant,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QMT_SOURCE_COLUMNS,
    QmtLocalDailyExportProfile,
    compare_registered_qmt_front_adjustment,
    normalize_registered_qmt_daily_export,
)

from .contracts import (
    QmtAdjustmentOffsetEntry,
    QmtDualExportQualityEvidence,
    QmtRegisteredRowCapObservation,
)


@dataclass(frozen=True)
class _EvidenceRow:
    trade_date: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    lots: int
    amount: Decimal


def _decimal(value: object, name: str, *, positive: bool = False) -> Decimal:
    if isinstance(value, (bool, float)):
        raise ValueError(f"{name} must be an exact decimal")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be an exact decimal") from exc
    if not result.is_finite() or result < 0 or (positive and result <= 0):
        raise ValueError(f"{name} is outside the allowed range")
    return result


def _registered_bytes(
    file_path: str | Path, registration: RegisteredLocalDailyExport
) -> bytes:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"registered QMT export not found: {path}")
    payload = path.read_bytes()
    if len(payload) != registration.byte_length:
        raise ValueError("registered QMT export byte length mismatch")
    if hashlib.sha256(payload).hexdigest() != registration.artifact_sha256:
        raise ValueError("registered QMT export SHA-256 mismatch")
    return payload


def _parse_registered_rows(
    file_path: str | Path,
    registration: RegisteredLocalDailyExport,
    profile: QmtLocalDailyExportProfile,
) -> tuple[_EvidenceRow, ...]:
    try:
        text = _registered_bytes(file_path, registration).decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("registered QMT export must be ASCII") from exc
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != QMT_SOURCE_COLUMNS:
        raise ValueError("registered QMT export columns are not exact")
    rows: list[_EvidenceRow] = []
    seen: set[str] = set()
    previous: str | None = None
    for source in reader:
        if None in source or any(value is None for value in source.values()):
            raise ValueError("registered QMT export row is malformed")
        try:
            trade_date = datetime.strptime(
                source["timetag"].strip(), "%Y%m%d"
            ).date().isoformat()
        except (TypeError, ValueError) as exc:
            raise ValueError("QMT timetag must be a valid YYYYMMDD date") from exc
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
        rows.append(
            _EvidenceRow(
                trade_date=trade_date,
                open=open_value,
                high=high_value,
                low=low_value,
                close=close_value,
                lots=int(lots_decimal),
                amount=_decimal(source["amount"], "amount"),
            )
        )
    if not rows:
        raise ValueError("registered QMT export must not be empty")
    return tuple(rows)


def build_qmt_dual_export_quality_evidence(
    raw_file_path: str | Path,
    raw_registration: RegisteredLocalDailyExport,
    front_file_path: str | Path,
    front_registration: RegisteredLocalDailyExport,
    profile: QmtLocalDailyExportProfile,
    row_cap_observation: QmtRegisteredRowCapObservation,
    *,
    evidence_id: str,
    normalized_artifact_id: str,
    as_of_utc: str,
) -> QmtDualExportQualityEvidence:
    if not isinstance(profile, QmtLocalDailyExportProfile):
        raise TypeError("profile must be QmtLocalDailyExportProfile")
    if not isinstance(row_cap_observation, QmtRegisteredRowCapObservation):
        raise TypeError("row_cap_observation must be QmtRegisteredRowCapObservation")
    instant(as_of_utc, "as_of_utc")
    if raw_registration.source_id != profile.source_id:
        raise ValueError("raw registration and profile source lineage disagree")
    if front_registration.source_id != profile.source_id:
        raise ValueError("front registration and profile source lineage disagree")
    normalized = normalize_registered_qmt_daily_export(
        raw_file_path,
        raw_registration,
        profile,
        output_artifact_id=normalized_artifact_id,
        as_of_utc=as_of_utc,
    )
    reference = compare_registered_qmt_front_adjustment(
        raw_file_path,
        raw_registration,
        front_file_path,
        front_registration,
        profile,
    )
    raw_rows = _parse_registered_rows(raw_file_path, raw_registration, profile)
    front_rows = _parse_registered_rows(front_file_path, front_registration, profile)
    if len(raw_rows) != len(front_rows):
        raise ValueError("QMT raw and front exports have different row counts")
    if len(raw_rows) > row_cap_observation.observed_cap_rows:
        raise ValueError("QMT row count exceeds the registered row-cap observation")
    zero_volume_rows = 0
    offsets: list[QmtAdjustmentOffsetEntry] = []
    for raw_row, front_row in zip(raw_rows, front_rows, strict=True):
        if raw_row.trade_date != front_row.trade_date:
            raise ValueError("QMT raw and front dates are not aligned")
        if raw_row.lots != front_row.lots or raw_row.amount != front_row.amount:
            raise ValueError("QMT front adjustment changed volume or amount")
        if raw_row.lots == 0:
            zero_volume_rows += 1
            if raw_row.amount != 0:
                raise ValueError("zero-volume QMT row must have zero amount")
        else:
            if raw_row.amount <= 0:
                raise ValueError("positive-volume QMT row must have positive amount")
            implied_price = raw_row.amount / Decimal(raw_row.lots * profile.volume_lot_size)
            if not raw_row.low <= implied_price <= raw_row.high:
                raise ValueError("QMT amount is inconsistent with 100-share lots")
        offsets.append(
            QmtAdjustmentOffsetEntry(
                trade_date=raw_row.trade_date,
                raw_minus_front_cash_offset=raw_row.close - front_row.close,
            )
        )
    if normalized.manifest.row_count != len(raw_rows):
        raise ValueError("upstream normalization row count mismatch")
    if reference.row_count != len(raw_rows):
        raise ValueError("upstream adjustment reference row count mismatch")
    derived_boundaries = tuple(
        current.trade_date
        for previous, current in zip(offsets, offsets[1:])
        if previous.raw_minus_front_cash_offset
        != current.raw_minus_front_cash_offset
    )
    if derived_boundaries != reference.boundary_dates:
        raise ValueError("upstream adjustment boundary lineage mismatch")
    findings = set(normalized.finding_codes)
    findings.update(
        {
            "ACTUAL_REGISTERED_ARTIFACT_PAIR_VALIDATED",
            "ADJUSTMENT_REFERENCE_ONLY",
            "EXPECTED_TRADING_CALENDAR_MISSING",
            "EXTERNAL_SDK_ENTITLEMENT_UNRESOLVED",
            "HISTORICAL_COMPLETENESS_UNPROVEN",
            "INDEPENDENT_SOURCE_RECONCILIATION_MISSING",
            "LOT_SIZE_100_NOTIONAL_RANGE_CONSISTENT",
            "MULTI_BATCH_COVERAGE_MISSING",
            "RAW_FRONT_DATE_VOLUME_AMOUNT_PARITY",
            "ROW_CAP_DOES_NOT_PROVE_COMPLETENESS",
        }
    )
    cap_state = (
        "AT_REGISTERED_CAP"
        if len(raw_rows) == row_cap_observation.observed_cap_rows
        else "BELOW_REGISTERED_CAP"
    )
    findings.add(
        "ROW_CAP_OBSERVED" if cap_state == "AT_REGISTERED_CAP" else "BELOW_REGISTERED_ROW_CAP"
    )
    return QmtDualExportQualityEvidence(
        evidence_id=evidence_id,
        raw_registration=raw_registration,
        front_registration=front_registration,
        profile_hash=profile.profile_hash,
        normalization_manifest_hash=normalized.manifest.manifest_hash,
        front_reference_hash=reference.reference_hash,
        normalized_artifact_sha256=normalized.normalized_registration.artifact_sha256,
        instrument_id=profile.instrument_id,
        requested_start_date=profile.requested_start_date,
        requested_end_date=profile.requested_end_date,
        actual_start_date=raw_rows[0].trade_date,
        actual_end_date=raw_rows[-1].trade_date,
        row_cap_observation=row_cap_observation,
        offset_entries=tuple(offsets),
        boundary_dates=derived_boundaries,
        finding_codes=tuple(sorted(findings)),
        as_of_utc=as_of_utc,
        row_count=len(raw_rows),
        lot_size_consistency_state=(
            "CONSISTENT_WITH_100_SHARE_LOTS_WITH_ZERO_VOLUME_ROWS"
            if zero_volume_rows
            else "CONSISTENT_WITH_100_SHARE_LOTS"
        ),
        row_cap_state=cap_state,
    )


def build_qmt_dual_export_registered_record(
    evidence: QmtDualExportQualityEvidence,
) -> dict[str, object]:
    if not isinstance(evidence, QmtDualExportQualityEvidence):
        raise TypeError("evidence must be QmtDualExportQualityEvidence")
    record: dict[str, object] = {
        "artifact_pair": {
            "front": {
                "artifact_id": evidence.front_registration.artifact_id,
                "artifact_sha256": evidence.front_registration.artifact_sha256,
                "byte_length": evidence.front_registration.byte_length,
                "retention_state": evidence.front_registration.retention_state,
                "rights_state": evidence.front_registration.rights_state,
            },
            "local_paths_committed": False,
            "raw": {
                "artifact_id": evidence.raw_registration.artifact_id,
                "artifact_sha256": evidence.raw_registration.artifact_sha256,
                "byte_length": evidence.raw_registration.byte_length,
                "retention_state": evidence.raw_registration.retention_state,
                "rights_state": evidence.raw_registration.rights_state,
            },
            "raw_provider_bytes_committed": False,
            "source_id": evidence.raw_registration.source_id,
        },
        "evidence_id": evidence.evidence_id,
        "lineage": {
            "evidence_hash": evidence.evidence_hash,
            "front_reference_hash": evidence.front_reference_hash,
            "normalization_manifest_hash": evidence.normalization_manifest_hash,
            "normalized_artifact_sha256": evidence.normalized_artifact_sha256,
            "profile_hash": evidence.profile_hash,
            "row_ledger_sha256": evidence.row_ledger_sha256,
        },
        "observation": {
            "actual_end_date": evidence.actual_end_date,
            "actual_start_date": evidence.actual_start_date,
            "boundary_dates": list(evidence.boundary_dates),
            "instrument_id": evidence.instrument_id,
            "lot_size_consistency_state": evidence.lot_size_consistency_state,
            "offset_distribution": [
                {
                    "raw_minus_front_cash_offset": value,
                    "row_count": count,
                }
                for value, count in evidence.offset_distribution
            ],
            "raw_front_parity_state": evidence.raw_front_parity_state,
            "requested_end_date": evidence.requested_end_date,
            "requested_start_date": evidence.requested_start_date,
            "row_cap_observation_hash": evidence.row_cap_observation.observation_hash,
            "row_cap_state": evidence.row_cap_state,
            "row_count": evidence.row_count,
            "volume_lot_size": evidence.volume_lot_size,
        },
        "operator_review_required": True,
        "quality": {
            "adjustment_factor_authority": False,
            "finding_codes": list(evidence.finding_codes),
            "gap_closed": False,
            "historical_completeness_claimed": False,
            "network_used": False,
            "provider_selected": False,
            "quality_state": evidence.quality_state,
            "sdk_used": False,
        },
        "registered_at_utc": evidence.as_of_utc,
        "schema_version": 1,
    }
    record["record_sha256"] = canonical_sha256(record)
    return record
