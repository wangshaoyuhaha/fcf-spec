from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


QUARANTINE_REASONS = (
    "PROVIDER_UNVERIFIED",
    "RIGHTS_UNVERIFIED",
    "REVISION_LINEAGE_MISSING",
    "CORPORATE_ACTION_LINEAGE_MISSING",
    "ADJUSTMENT_FACTOR_AUTHORITY_MISSING",
    "TRADING_STATUS_AUTHORITY_MISSING",
    "EXPECTED_CALENDAR_MISSING",
    "POINT_IN_TIME_AVAILABILITY_MISSING",
)


def _nonnegative(value: int, field_name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field_name} must be a nonnegative integer")
    return value


def _iso_date(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date") from exc
    normalized = parsed.isoformat()
    if normalized != value:
        raise ValueError(f"{field_name} must be normalized")
    return normalized


@dataclass(frozen=True)
class CandidateDailyCorpusQualityEvidence:
    evidence_id: str
    observed_at_utc: str
    manifest_hash: str
    header_hash: str
    file_count: int
    total_bytes: int
    row_count: int
    market_file_counts: tuple[tuple[str, int], ...]
    header_mismatch_file_count: int
    invalid_filename_count: int
    unexpected_entry_count: int
    malformed_file_count: int
    malformed_row_count: int
    code_mismatch_row_count: int
    non_monotonic_date_count: int
    duplicate_date_count: int
    invalid_ohlc_row_count: int
    negative_numeric_row_count: int
    return_mismatch_row_count: int
    adjustment_ratio_mismatch_row_count: int
    zero_volume_row_count: int
    earliest_trade_date: str
    latest_trade_date: str
    latest_terminal_date: str
    latest_terminal_file_count: int
    stale_terminal_file_count: int
    first_adjustment_ratio_unit_file_count: int
    terminal_adjustment_ratio_nonunit_file_count: int
    quarantine_reasons: tuple[str, ...] = QUARANTINE_REASONS
    status: str = "QUARANTINED_UNVERIFIED_EXTERNAL_CANDIDATE"
    registered_evidence_promotion_allowed: bool = False
    factor_calculation_allowed: bool = False
    training_label_allowed: bool = False
    provider_selection_allowed: bool = False
    raw_rows_embedded: bool = False
    schema_version: str = "a-share-external-candidate-daily-corpus-quality-v1"
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        evidence_id = identifier(self.evidence_id, "evidence_id")
        observed_at_utc = utc(self.observed_at_utc, "observed_at_utc")
        manifest_hash = digest(self.manifest_hash, "manifest_hash")
        header_hash = digest(self.header_hash, "header_hash")
        metric_names = (
            "file_count",
            "total_bytes",
            "row_count",
            "header_mismatch_file_count",
            "invalid_filename_count",
            "unexpected_entry_count",
            "malformed_file_count",
            "malformed_row_count",
            "code_mismatch_row_count",
            "non_monotonic_date_count",
            "duplicate_date_count",
            "invalid_ohlc_row_count",
            "negative_numeric_row_count",
            "return_mismatch_row_count",
            "adjustment_ratio_mismatch_row_count",
            "zero_volume_row_count",
            "latest_terminal_file_count",
            "stale_terminal_file_count",
            "first_adjustment_ratio_unit_file_count",
            "terminal_adjustment_ratio_nonunit_file_count",
        )
        metrics = {name: _nonnegative(getattr(self, name), name) for name in metric_names}
        market_counts = tuple(self.market_file_counts)
        if tuple(name for name, _ in market_counts) != ("bj", "sh", "sz", "other"):
            raise ValueError("market_file_counts must use the closed market order")
        if any(type(count) is not int or count < 0 for _, count in market_counts):
            raise ValueError("market file counts must be nonnegative integers")
        if sum(count for _, count in market_counts) != metrics["file_count"]:
            raise ValueError("market file counts must equal file_count")
        earliest = _iso_date(self.earliest_trade_date, "earliest_trade_date")
        latest = _iso_date(self.latest_trade_date, "latest_trade_date")
        terminal = _iso_date(self.latest_terminal_date, "latest_terminal_date")
        if date.fromisoformat(earliest) > date.fromisoformat(latest):
            raise ValueError("trade date boundaries are reversed")
        if date.fromisoformat(terminal) > date.fromisoformat(latest):
            raise ValueError("terminal date cannot exceed latest trade date")
        if metrics["latest_terminal_file_count"] + metrics["stale_terminal_file_count"] > metrics["file_count"]:
            raise ValueError("terminal file counts cannot exceed file_count")
        if tuple(self.quarantine_reasons) != QUARANTINE_REASONS:
            raise ValueError("quarantine reasons are closed and mandatory")
        forbidden = (
            self.registered_evidence_promotion_allowed,
            self.factor_calculation_allowed,
            self.training_label_allowed,
            self.provider_selection_allowed,
            self.raw_rows_embedded,
        )
        if self.status != "QUARANTINED_UNVERIFIED_EXTERNAL_CANDIDATE" or any(forbidden):
            raise ValueError("candidate corpus evidence cannot be promoted or authoritative")
        if self.schema_version != "a-share-external-candidate-daily-corpus-quality-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "evidence_id", evidence_id)
        object.__setattr__(self, "observed_at_utc", observed_at_utc)
        object.__setattr__(self, "manifest_hash", manifest_hash)
        object.__setattr__(self, "header_hash", header_hash)
        object.__setattr__(self, "market_file_counts", market_counts)
        object.__setattr__(self, "quarantine_reasons", QUARANTINE_REASONS)
        object.__setattr__(self, "earliest_trade_date", earliest)
        object.__setattr__(self, "latest_trade_date", latest)
        object.__setattr__(self, "latest_terminal_date", terminal)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "evidence_id": evidence_id,
                    "observed_at_utc": observed_at_utc,
                    "manifest_hash": manifest_hash,
                    "header_hash": header_hash,
                    "metrics": metrics,
                    "market_file_counts": [list(item) for item in market_counts],
                    "earliest_trade_date": earliest,
                    "latest_trade_date": latest,
                    "latest_terminal_date": terminal,
                    "quarantine_reasons": list(QUARANTINE_REASONS),
                    "status": self.status,
                    "schema_version": self.schema_version,
                }
            ),
        )
