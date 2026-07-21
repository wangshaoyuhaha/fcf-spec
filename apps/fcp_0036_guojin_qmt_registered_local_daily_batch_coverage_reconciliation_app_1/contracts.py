from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    LocalDailyExportProfile,
    RegisteredLocalDailyExport,
)


EXPECTED_DATE_COLUMNS = ("trade_date",)
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE)$")


@dataclass(frozen=True)
class RegisteredExpectedTradingDateSet:
    registration: RegisteredLocalDailyExport
    instrument_id: str
    operator_registered: bool = True
    natural_day_inference_allowed: bool = False
    date_set_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.registration, RegisteredLocalDailyExport):
            raise TypeError("registration must be RegisteredLocalDailyExport")
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        if (
            self.operator_registered is not True
            or self.natural_day_inference_allowed is not False
        ):
            raise ValueError("expected dates require explicit Operator registration")
        object.__setattr__(
            self,
            "date_set_hash",
            canonical_sha256(
                {
                    "artifact_id": self.registration.artifact_id,
                    "artifact_sha256": self.registration.artifact_sha256,
                    "byte_length": self.registration.byte_length,
                    "instrument_id": instrument,
                    "natural_day_inference_allowed": False,
                    "operator_registered": True,
                    "registered_at_utc": self.registration.registered_at_utc,
                    "retention_state": self.registration.retention_state,
                    "rights_state": self.registration.rights_state,
                    "source_id": self.registration.source_id,
                    "usage_scope": self.registration.usage_scope,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredQmtDailyBatch:
    batch_id: str
    sequence: int
    file_path: str | Path
    registration: RegisteredLocalDailyExport
    batch_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "batch_id", identifier(self.batch_id, "batch_id"))
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
            raise ValueError("sequence must be an integer")
        if self.sequence <= 0:
            raise ValueError("sequence must be positive")
        path = Path(self.file_path)
        if not str(path).strip():
            raise ValueError("file_path must be nonempty")
        object.__setattr__(self, "file_path", path)
        if not isinstance(self.registration, RegisteredLocalDailyExport):
            raise TypeError("registration must be RegisteredLocalDailyExport")
        object.__setattr__(
            self,
            "batch_hash",
            canonical_sha256(
                {
                    "artifact_id": self.registration.artifact_id,
                    "artifact_sha256": self.registration.artifact_sha256,
                    "batch_id": self.batch_id,
                    "byte_length": self.registration.byte_length,
                    "sequence": self.sequence,
                    "source_id": self.registration.source_id,
                }
            ),
        )


@dataclass(frozen=True)
class QmtBatchCoverageManifest:
    instrument_id: str
    profile_hash: str
    expected_date_set_hash: str
    expected_artifact_sha256: str
    ordered_batch_hashes: tuple[str, ...]
    ordered_source_artifact_sha256s: tuple[str, ...]
    ordered_normalization_manifest_hashes: tuple[str, ...]
    merged_artifact_sha256: str
    row_count: int
    expected_date_count: int
    identical_overlap_count: int
    missing_dates: tuple[str, ...]
    unexpected_dates: tuple[str, ...]
    conflict_dates: tuple[str, ...]
    row_cap_batch_ids: tuple[str, ...]
    finding_codes: tuple[str, ...]
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        for name in (
            "profile_hash",
            "expected_date_set_hash",
            "expected_artifact_sha256",
            "merged_artifact_sha256",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        for name in (
            "ordered_batch_hashes",
            "ordered_source_artifact_sha256s",
            "ordered_normalization_manifest_hashes",
        ):
            values = tuple(digest(value, name) for value in getattr(self, name))
            if not values:
                raise ValueError(f"{name} must be nonempty")
            object.__setattr__(self, name, values)
        if not (
            len(self.ordered_batch_hashes)
            == len(self.ordered_source_artifact_sha256s)
            == len(self.ordered_normalization_manifest_hashes)
        ):
            raise ValueError("ordered batch lineage lengths disagree")
        for name in ("row_count", "expected_date_count", "identical_overlap_count"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        for name in ("missing_dates", "unexpected_dates", "conflict_dates"):
            values = tuple(sorted(set(getattr(self, name))))
            for value in values:
                try:
                    date.fromisoformat(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"{name} must contain ISO dates") from exc
            object.__setattr__(self, name, values)
        row_cap_batches = tuple(sorted(set(self.row_cap_batch_ids)))
        object.__setattr__(self, "row_cap_batch_ids", row_cap_batches)
        findings = tuple(sorted(set(self.finding_codes)))
        if not findings:
            raise ValueError("coverage manifest requires visible findings")
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(
            self,
            "manifest_hash",
            canonical_sha256(
                {
                    "conflict_dates": self.conflict_dates,
                    "expected_artifact_sha256": self.expected_artifact_sha256,
                    "expected_date_count": self.expected_date_count,
                    "expected_date_set_hash": self.expected_date_set_hash,
                    "finding_codes": findings,
                    "identical_overlap_count": self.identical_overlap_count,
                    "instrument_id": instrument,
                    "merged_artifact_sha256": self.merged_artifact_sha256,
                    "missing_dates": self.missing_dates,
                    "ordered_batch_hashes": self.ordered_batch_hashes,
                    "ordered_normalization_manifest_hashes": self.ordered_normalization_manifest_hashes,
                    "ordered_source_artifact_sha256s": self.ordered_source_artifact_sha256s,
                    "profile_hash": self.profile_hash,
                    "row_cap_batch_ids": row_cap_batches,
                    "row_count": self.row_count,
                    "unexpected_dates": self.unexpected_dates,
                }
            ),
        )


@dataclass(frozen=True)
class QmtBatchCoverageReconciliationResult:
    merged_csv: bytes
    merged_registration: RegisteredLocalDailyExport
    bridge_profile: LocalDailyExportProfile
    manifest: QmtBatchCoverageManifest
    quality_state: str
    finding_codes: tuple[str, ...]
    operator_review_required: bool = True
    provider_selected: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.merged_csv, bytes) or not self.merged_csv:
            raise ValueError("merged_csv must be immutable nonempty bytes")
        if not isinstance(self.merged_registration, RegisteredLocalDailyExport):
            raise TypeError("merged_registration must be RegisteredLocalDailyExport")
        if not isinstance(self.bridge_profile, LocalDailyExportProfile):
            raise TypeError("bridge_profile must be LocalDailyExportProfile")
        actual_sha256 = hashlib.sha256(self.merged_csv).hexdigest()
        if self.merged_registration.artifact_sha256 != actual_sha256:
            raise ValueError("merged registration SHA-256 mismatch")
        if self.merged_registration.byte_length != len(self.merged_csv):
            raise ValueError("merged registration byte length mismatch")
        if self.manifest.merged_artifact_sha256 != actual_sha256:
            raise ValueError("coverage manifest SHA-256 mismatch")
        lines = self.merged_csv.decode("ascii").splitlines()
        if not lines or lines[0] != ",".join(
            (
                "code",
                "exchange",
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "amount",
            )
        ):
            raise ValueError("merged CSV header is not exact")
        if len(lines) - 1 != self.manifest.row_count:
            raise ValueError("merged CSV row count disagrees with manifest")
        findings = tuple(sorted(set(self.finding_codes)))
        if findings != self.manifest.finding_codes:
            raise ValueError("result and manifest findings disagree")
        allowed = {
            "COVERAGE_RECONCILED_CANONICAL_SUPPLEMENTS_REQUIRED",
            "BLOCKED_COVERAGE_MISMATCH",
            "QUARANTINED_CONFLICT",
        }
        if self.quality_state not in allowed:
            raise ValueError("quality_state is not registered")
        if self.operator_review_required is not True or self.provider_selected is not False:
            raise ValueError("coverage result must remain reviewed and provider-unselected")
        object.__setattr__(self, "finding_codes", findings)
