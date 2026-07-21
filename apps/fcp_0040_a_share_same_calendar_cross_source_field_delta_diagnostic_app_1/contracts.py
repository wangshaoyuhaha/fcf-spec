from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_decimal,
    canonical_sha256,
    decimal_value,
    digest,
    identifier,
)


NUMERIC_FIELDS = (
    "adjustment_factor",
    "amount",
    "raw_close",
    "raw_high",
    "raw_low",
    "raw_open",
    "volume",
)
CLOCK_FIELDS = (
    "available_at_utc",
    "factor_available_at_utc",
    "first_tradable_at_utc",
    "revision_at_utc",
)


@dataclass(frozen=True)
class NumericDeltaSummary:
    field_name: str
    observation_count: int
    nonzero_count: int
    total_abs_delta: Decimal
    max_abs_delta: Decimal
    summary_hash: str = field(init=False)

    def __post_init__(self) -> None:
        name = identifier(self.field_name, "field_name")
        if name not in NUMERIC_FIELDS:
            raise ValueError("numeric diagnostic field is not registered")
        counts = (self.observation_count, self.nonzero_count)
        if any(isinstance(item, bool) or not isinstance(item, int) for item in counts):
            raise ValueError("numeric diagnostic counts must be integers")
        if not 0 <= self.nonzero_count <= self.observation_count:
            raise ValueError("numeric diagnostic counts are inconsistent")
        total = decimal_value(self.total_abs_delta, "total_abs_delta")
        maximum = decimal_value(self.max_abs_delta, "max_abs_delta")
        if maximum > total or (self.nonzero_count == 0) != (total == maximum == 0):
            raise ValueError("numeric diagnostic magnitudes are inconsistent")
        object.__setattr__(self, "field_name", name)
        object.__setattr__(self, "total_abs_delta", total)
        object.__setattr__(self, "max_abs_delta", maximum)
        object.__setattr__(
            self,
            "summary_hash",
            canonical_sha256(
                {
                    "field_name": name,
                    "max_abs_delta": canonical_decimal(maximum),
                    "nonzero_count": self.nonzero_count,
                    "observation_count": self.observation_count,
                    "total_abs_delta": canonical_decimal(total),
                }
            ),
        )


@dataclass(frozen=True)
class ClockDeltaSummary:
    field_name: str
    observation_count: int
    nonzero_count: int
    total_abs_seconds: int
    max_abs_seconds: int
    summary_hash: str = field(init=False)

    def __post_init__(self) -> None:
        name = identifier(self.field_name, "field_name")
        if name not in CLOCK_FIELDS:
            raise ValueError("clock diagnostic field is not registered")
        values = (
            self.observation_count,
            self.nonzero_count,
            self.total_abs_seconds,
            self.max_abs_seconds,
        )
        if any(isinstance(item, bool) or not isinstance(item, int) for item in values):
            raise ValueError("clock diagnostic values must be integers")
        if not 0 <= self.nonzero_count <= self.observation_count:
            raise ValueError("clock diagnostic counts are inconsistent")
        if self.total_abs_seconds < 0 or not 0 <= self.max_abs_seconds <= self.total_abs_seconds:
            raise ValueError("clock diagnostic magnitudes are inconsistent")
        if (self.nonzero_count == 0) != (
            self.total_abs_seconds == self.max_abs_seconds == 0
        ):
            raise ValueError("clock diagnostic zero state is inconsistent")
        object.__setattr__(self, "field_name", name)
        object.__setattr__(
            self,
            "summary_hash",
            canonical_sha256(
                {
                    "field_name": name,
                    "max_abs_seconds": self.max_abs_seconds,
                    "nonzero_count": self.nonzero_count,
                    "observation_count": self.observation_count,
                    "total_abs_seconds": self.total_abs_seconds,
                }
            ),
        )


@dataclass(frozen=True)
class SameCalendarCrossSourceFieldDeltaDiagnostic:
    coverage_result_hash: str
    qmt_role_hash: str
    independent_role_hash: str
    artifact_independence_proof_hash: str
    overlap_key_count: int
    numeric_summaries: tuple[NumericDeltaSummary, ...]
    clock_summaries: tuple[ClockDeltaSummary, ...]
    factor_missing_pair_count: int
    factor_version_mismatch_count: int
    trading_status_mismatch_count: int
    diagnostic_state: str = "READ_ONLY_DIAGNOSTIC_ONLY"
    operator_review_required: bool = True
    threshold_set: bool = False
    source_ranked: bool = False
    source_selected: bool = False
    diagnostic_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "coverage_result_hash",
            "qmt_role_hash",
            "independent_role_hash",
            "artifact_independence_proof_hash",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if self.qmt_role_hash == self.independent_role_hash:
            raise ValueError("diagnostic role hashes must be distinct")
        if (
            isinstance(self.overlap_key_count, bool)
            or not isinstance(self.overlap_key_count, int)
            or self.overlap_key_count <= 0
        ):
            raise ValueError("diagnostic requires positive overlap")
        numeric = tuple(self.numeric_summaries)
        clocks = tuple(self.clock_summaries)
        if tuple(item.field_name for item in numeric) != NUMERIC_FIELDS:
            raise ValueError("numeric summaries must use the closed field order")
        if tuple(item.field_name for item in clocks) != CLOCK_FIELDS:
            raise ValueError("clock summaries must use the closed field order")
        if any(item.observation_count > self.overlap_key_count for item in numeric + clocks):
            raise ValueError("summary count exceeds overlap")
        counts = (
            self.factor_missing_pair_count,
            self.factor_version_mismatch_count,
            self.trading_status_mismatch_count,
        )
        if any(
            isinstance(item, bool)
            or not isinstance(item, int)
            or not 0 <= item <= self.overlap_key_count
            for item in counts
        ):
            raise ValueError("diagnostic mismatch counts are inconsistent")
        if self.diagnostic_state != "READ_ONLY_DIAGNOSTIC_ONLY":
            raise ValueError("diagnostic state is immutable")
        if (
            self.operator_review_required is not True
            or self.threshold_set is not False
            or self.source_ranked is not False
            or self.source_selected is not False
        ):
            raise ValueError("diagnostic cannot decide or select a source")
        object.__setattr__(self, "numeric_summaries", numeric)
        object.__setattr__(self, "clock_summaries", clocks)
        object.__setattr__(
            self,
            "diagnostic_hash",
            canonical_sha256(
                {
                    "artifact_independence_proof_hash": self.artifact_independence_proof_hash,
                    "clock_summary_hashes": [item.summary_hash for item in clocks],
                    "coverage_result_hash": self.coverage_result_hash,
                    "diagnostic_state": self.diagnostic_state,
                    "factor_missing_pair_count": self.factor_missing_pair_count,
                    "factor_version_mismatch_count": self.factor_version_mismatch_count,
                    "independent_role_hash": self.independent_role_hash,
                    "numeric_summary_hashes": [item.summary_hash for item in numeric],
                    "overlap_key_count": self.overlap_key_count,
                    "qmt_role_hash": self.qmt_role_hash,
                    "trading_status_mismatch_count": self.trading_status_mismatch_count,
                }
            ),
        )
