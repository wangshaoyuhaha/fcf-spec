from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationResult,
    RegisteredCanonicalDailyDataset,
)


ROLES = ("QMT_LOCAL_EXPORT", "INDEPENDENT_REFERENCE")
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE)$")
_CALENDAR_QUALITY_STATES = {
    "REGISTERED_EXPECTED_DATES_READY",
    "REVIEW_REQUIRED_UNRESOLVED_RIGHTS",
}


@dataclass(frozen=True)
class SourceRoleDataset:
    role: str
    dataset: RegisteredCanonicalDailyDataset
    role_hash: str = field(init=False)

    def __post_init__(self) -> None:
        role = str(self.role).strip().upper()
        if role not in ROLES:
            raise ValueError("source role is not registered")
        if not isinstance(self.dataset, RegisteredCanonicalDailyDataset):
            raise TypeError("dataset must be RegisteredCanonicalDailyDataset")
        object.__setattr__(self, "role", role)
        object.__setattr__(
            self,
            "role_hash",
            canonical_sha256(
                {
                    "dataset_hash": self.dataset.dataset_hash,
                    "dataset_id": self.dataset.dataset_id,
                    "role": role,
                    "source_id": self.dataset.source_id,
                }
            ),
        )


@dataclass(frozen=True)
class SameCalendarCrossSourceCoverageResult:
    instrument_id: str
    calendar_manifest_hash: str
    calendar_quality_state: str
    qmt_role_hash: str
    independent_role_hash: str
    qmt_missing_dates: tuple[str, ...]
    qmt_unexpected_dates: tuple[str, ...]
    independent_missing_dates: tuple[str, ...]
    independent_unexpected_dates: tuple[str, ...]
    cross_source_result: AShareCrossSourceReconciliationResult
    finding_codes: tuple[str, ...]
    quality_state: str
    operator_review_required: bool = True
    source_selected: bool = False
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        instrument = str(self.instrument_id).strip().upper()
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        for name in (
            "calendar_manifest_hash",
            "qmt_role_hash",
            "independent_role_hash",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        if self.qmt_role_hash == self.independent_role_hash:
            raise ValueError("cross-source role hashes must be distinct")
        if self.calendar_quality_state not in _CALENDAR_QUALITY_STATES:
            raise ValueError("calendar_quality_state is not registered")
        if not isinstance(
            self.cross_source_result, AShareCrossSourceReconciliationResult
        ):
            raise TypeError("cross_source_result must be typed")
        date_fields = (
            "qmt_missing_dates",
            "qmt_unexpected_dates",
            "independent_missing_dates",
            "independent_unexpected_dates",
        )
        for name in date_fields:
            try:
                values = tuple(
                    sorted({date.fromisoformat(str(item)).isoformat() for item in getattr(self, name)})
                )
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must contain ISO dates") from exc
            object.__setattr__(self, name, values)
        findings = tuple(sorted(set(self.finding_codes)))
        expected_findings = {"SAME_REGISTERED_CALENDAR_COMPARED"}
        for present, code in (
            (self.qmt_missing_dates, "QMT_EXPECTED_DATES_MISSING"),
            (self.qmt_unexpected_dates, "QMT_UNEXPECTED_DATES_PRESENT"),
            (
                self.independent_missing_dates,
                "INDEPENDENT_EXPECTED_DATES_MISSING",
            ),
            (
                self.independent_unexpected_dates,
                "INDEPENDENT_UNEXPECTED_DATES_PRESENT",
            ),
        ):
            if present:
                expected_findings.add(code)
        if self.cross_source_result.quality_state != "CONSISTENT":
            expected_findings.add("CROSS_SOURCE_QUALITY_QUARANTINED")
        if self.calendar_quality_state != "REGISTERED_EXPECTED_DATES_READY":
            expected_findings.add("CALENDAR_AUTHORITY_REVIEW_REQUIRED")
        if findings != tuple(sorted(expected_findings)):
            raise ValueError("finding_codes and coverage evidence disagree")
        object.__setattr__(self, "finding_codes", findings)
        blocked = any(getattr(self, name) for name in date_fields) or (
            self.cross_source_result.quality_state != "CONSISTENT"
        ) or (
            self.calendar_quality_state != "REGISTERED_EXPECTED_DATES_READY"
        )
        expected = "QUARANTINE_REVIEW_REQUIRED" if blocked else "CONSISTENT"
        if self.quality_state != expected:
            raise ValueError("quality_state and coverage evidence disagree")
        if self.operator_review_required is not True or self.source_selected is not False:
            raise ValueError("coverage reconciliation cannot select a source")
        object.__setattr__(
            self,
            "result_hash",
            canonical_sha256(
                {
                    "calendar_manifest_hash": self.calendar_manifest_hash,
                    "calendar_quality_state": self.calendar_quality_state,
                    "cross_source_result_hash": self.cross_source_result.result_hash,
                    "finding_codes": findings,
                    "independent_missing_dates": self.independent_missing_dates,
                    "independent_role_hash": self.independent_role_hash,
                    "independent_unexpected_dates": self.independent_unexpected_dates,
                    "instrument_id": self.instrument_id,
                    "qmt_missing_dates": self.qmt_missing_dates,
                    "qmt_role_hash": self.qmt_role_hash,
                    "qmt_unexpected_dates": self.qmt_unexpected_dates,
                    "quality_state": self.quality_state,
                }
            ),
        )
