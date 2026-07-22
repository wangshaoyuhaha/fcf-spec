from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import utc


FINDING_ORDER = (
    "REQUESTED_RANGE_START_MISMATCH",
    "REQUESTED_RANGE_END_MISMATCH",
    "ADJUSTMENT_FACTOR_MISSING",
    "POINT_IN_TIME_SUPPLEMENTS_MISSING",
    "TRADING_STATUS_UNKNOWN",
    "OBSERVED_500_ROW_BATCH",
    "EXPECTED_DATE_ARTIFACT_MISSING",
    "FCP36_RECONCILIATION_NOT_RUN",
    "PAGINATION_NOT_PROVEN",
)
STATUS = "BLOCKED_PENDING_REGISTERED_EXPECTED_DATES"
OUTCOME = "INSUFFICIENT_EVIDENCE"
SCHEMA_VERSION = "a-share-guojin-qmt-local-export-coverage-probe-v1"


def _date(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO date")
    try:
        normalized = date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date") from exc
    if normalized != value:
        raise ValueError(f"{field_name} must be normalized")
    return normalized


def _positive(value: int, field_name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


@dataclass(frozen=True)
class QmtBatchCompatibilityObservation:
    batch_id: str
    sequence: int
    source_artifact_sha256: str
    source_byte_length: int
    normalization_manifest_hash: str
    normalized_artifact_sha256: str
    row_count: int
    actual_start_date: str
    actual_end_date: str
    finding_codes: tuple[str, ...]
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        batch_id = identifier(self.batch_id, "batch_id")
        sequence = _positive(self.sequence, "sequence")
        source_hash = digest(
            self.source_artifact_sha256, "source_artifact_sha256"
        )
        manifest_hash = digest(
            self.normalization_manifest_hash, "normalization_manifest_hash"
        )
        normalized_hash = digest(
            self.normalized_artifact_sha256, "normalized_artifact_sha256"
        )
        byte_length = _positive(self.source_byte_length, "source_byte_length")
        row_count = _positive(self.row_count, "row_count")
        start = _date(self.actual_start_date, "actual_start_date")
        end = _date(self.actual_end_date, "actual_end_date")
        if date.fromisoformat(start) > date.fromisoformat(end):
            raise ValueError("actual date bounds are reversed")
        findings = tuple(self.finding_codes)
        if findings != tuple(item for item in FINDING_ORDER if item in findings):
            raise ValueError("finding_codes must use closed deterministic order")
        if len(findings) != len(set(findings)):
            raise ValueError("finding_codes must be unique")
        object.__setattr__(self, "batch_id", batch_id)
        object.__setattr__(self, "sequence", sequence)
        object.__setattr__(self, "source_artifact_sha256", source_hash)
        object.__setattr__(self, "normalization_manifest_hash", manifest_hash)
        object.__setattr__(self, "normalized_artifact_sha256", normalized_hash)
        object.__setattr__(self, "actual_start_date", start)
        object.__setattr__(self, "actual_end_date", end)
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "actual_end_date": end,
                    "actual_start_date": start,
                    "batch_id": batch_id,
                    "finding_codes": list(findings),
                    "normalization_manifest_hash": manifest_hash,
                    "normalized_artifact_sha256": normalized_hash,
                    "row_count": row_count,
                    "sequence": sequence,
                    "source_artifact_sha256": source_hash,
                    "source_byte_length": byte_length,
                }
            ),
        )


@dataclass(frozen=True)
class QmtLocalExportCoverageEvidence:
    evidence_id: str
    observed_at_utc: str
    instrument_id: str
    profile_hash: str
    requested_start_date: str
    requested_end_date: str
    observations: tuple[QmtBatchCompatibilityObservation, ...]
    observed_start_date: str
    observed_end_date: str
    repeated_observed_row_count_bound: bool
    finding_codes: tuple[str, ...]
    status: str = STATUS
    outcome: str = OUTCOME
    raw_rows_embedded: bool = False
    normalized_rows_embedded: bool = False
    local_paths_embedded: bool = False
    registered_evidence_promotion_allowed: bool = False
    provider_selection_allowed: bool = False
    factor_calculation_allowed: bool = False
    product_authority_allowed: bool = False
    schema_version: str = SCHEMA_VERSION
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        evidence_id = identifier(self.evidence_id, "evidence_id")
        instrument_id = str(self.instrument_id).strip().upper()
        if len(instrument_id) != 11 or instrument_id[6] != ".":
            raise ValueError("instrument_id is not canonical")
        observed_at = utc(self.observed_at_utc, "observed_at_utc")
        profile_hash = digest(self.profile_hash, "profile_hash")
        requested_start = _date(
            self.requested_start_date, "requested_start_date"
        )
        requested_end = _date(self.requested_end_date, "requested_end_date")
        observed_start = _date(self.observed_start_date, "observed_start_date")
        observed_end = _date(self.observed_end_date, "observed_end_date")
        if requested_start > requested_end or observed_start > observed_end:
            raise ValueError("coverage date bounds are reversed")
        observations = tuple(self.observations)
        if not observations or len(observations) > 32:
            raise ValueError("observations must contain one to 32 batches")
        if tuple(item.sequence for item in observations) != tuple(
            range(1, len(observations) + 1)
        ):
            raise ValueError("observation sequence must be contiguous")
        if len({item.batch_id for item in observations}) != len(observations):
            raise ValueError("batch identifiers must be unique")
        findings = tuple(self.finding_codes)
        if findings != tuple(item for item in FINDING_ORDER if item in findings):
            raise ValueError("finding_codes must use closed deterministic order")
        mandatory = {
            "EXPECTED_DATE_ARTIFACT_MISSING",
            "FCP36_RECONCILIATION_NOT_RUN",
            "PAGINATION_NOT_PROVEN",
        }
        if not mandatory.issubset(findings):
            raise ValueError("coverage probe must preserve mandatory blockers")
        forbidden = (
            self.raw_rows_embedded,
            self.normalized_rows_embedded,
            self.local_paths_embedded,
            self.registered_evidence_promotion_allowed,
            self.provider_selection_allowed,
            self.factor_calculation_allowed,
            self.product_authority_allowed,
        )
        if self.status != STATUS or self.outcome != OUTCOME or any(forbidden):
            raise ValueError("coverage probe cannot become authoritative")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "evidence_id", evidence_id)
        object.__setattr__(self, "instrument_id", instrument_id)
        object.__setattr__(self, "observed_at_utc", observed_at)
        object.__setattr__(self, "profile_hash", profile_hash)
        object.__setattr__(self, "requested_start_date", requested_start)
        object.__setattr__(self, "requested_end_date", requested_end)
        object.__setattr__(self, "observed_start_date", observed_start)
        object.__setattr__(self, "observed_end_date", observed_end)
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "evidence_id": evidence_id,
                    "finding_codes": list(findings),
                    "instrument_id": instrument_id,
                    "observation_hashes": [
                        item.observation_hash for item in observations
                    ],
                    "observed_at_utc": observed_at,
                    "observed_end_date": observed_end,
                    "observed_start_date": observed_start,
                    "outcome": self.outcome,
                    "profile_hash": profile_hash,
                    "repeated_observed_row_count_bound": (
                        self.repeated_observed_row_count_bound
                    ),
                    "requested_end_date": requested_end,
                    "requested_start_date": requested_start,
                    "schema_version": self.schema_version,
                    "status": self.status,
                }
            ),
        )


def build_reference_evidence() -> QmtLocalExportCoverageEvidence:
    observation = QmtBatchCompatibilityObservation(
        batch_id="qmt-reference-batch-1",
        sequence=1,
        source_artifact_sha256=(
            "1c2800f80f5e030f0d620aac10a36b021da70c49c160e32cf028f351158e6b22"
        ),
        source_byte_length=131,
        normalization_manifest_hash=(
            "6f5c506950989d194e431854fd871306185cd0c83b20841e4e484be2d0a997f7"
        ),
        normalized_artifact_sha256=(
            "137dc4119c0d402a4018931e4ec1255de28a7fcb9d516c0914f0564f5161069d"
        ),
        row_count=3,
        actual_start_date="2026-07-17",
        actual_end_date="2026-07-21",
        finding_codes=(
            "ADJUSTMENT_FACTOR_MISSING",
            "POINT_IN_TIME_SUPPLEMENTS_MISSING",
            "TRADING_STATUS_UNKNOWN",
        ),
    )
    return QmtLocalExportCoverageEvidence(
        evidence_id="qmt-reference-coverage-probe-v1",
        observed_at_utc="2026-07-22T21:35:27Z",
        instrument_id="600028.XSHG",
        profile_hash=(
            "96c4931f75a1336985b28ffa43ecb89cf4d56afdd1faff5a996fce6e45741c1d"
        ),
        requested_start_date="2026-07-17",
        requested_end_date="2026-07-21",
        observations=(observation,),
        observed_start_date="2026-07-17",
        observed_end_date="2026-07-21",
        repeated_observed_row_count_bound=False,
        finding_codes=(
            "ADJUSTMENT_FACTOR_MISSING",
            "POINT_IN_TIME_SUPPLEMENTS_MISSING",
            "TRADING_STATUS_UNKNOWN",
            "EXPECTED_DATE_ARTIFACT_MISSING",
            "FCP36_RECONCILIATION_NOT_RUN",
            "PAGINATION_NOT_PROVEN",
        ),
    )
