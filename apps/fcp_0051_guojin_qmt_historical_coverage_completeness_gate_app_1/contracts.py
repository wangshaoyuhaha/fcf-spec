from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
    utc,
)


REQUIREMENT_IDS = (
    "EXPECTED_TRADING_DATE_ARTIFACT_REGISTERED",
    "FCP_0050_QUALITY_RECORD_VALID",
    "MULTI_BATCH_COVERAGE_RECONCILED",
    "PAGINATION_BEHAVIOR_REGISTERED",
    "POINT_IN_TIME_SUPPLEMENTS_REGISTERED",
    "RECONCILED_DATE_SET_EXACT",
    "REQUESTED_END_BOUNDARY_COVERED",
    "REQUESTED_START_BOUNDARY_COVERED",
    "ROW_CAP_AMBIGUITY_RESOLVED",
)
REQUIREMENT_STATES = frozenset({"SATISFIED", "UNSATISFIED", "UNRESOLVED"})


def _optional_digest(value: str | None, name: str) -> str | None:
    return None if value is None else digest(value, name)


def _optional_count(value: int | None, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer or None")
    return value


@dataclass(frozen=True)
class RegisteredCoverageSupplements:
    expected_date_set_hash: str | None = None
    pagination_evidence_hash: str | None = None
    multi_batch_manifest_hash: str | None = None
    missing_date_count: int | None = None
    unexpected_date_count: int | None = None
    conflict_date_count: int | None = None
    point_in_time_supplement_hash: str | None = None
    row_cap_resolution_hash: str | None = None
    operator_registered: bool = True
    natural_day_inference_allowed: bool = False
    provider_selected: bool = False
    sdk_used: bool = False
    network_used: bool = False
    supplement_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "expected_date_set_hash",
            "pagination_evidence_hash",
            "multi_batch_manifest_hash",
            "point_in_time_supplement_hash",
            "row_cap_resolution_hash",
        ):
            object.__setattr__(self, name, _optional_digest(getattr(self, name), name))
        for name in (
            "missing_date_count",
            "unexpected_date_count",
            "conflict_date_count",
        ):
            object.__setattr__(self, name, _optional_count(getattr(self, name), name))
        counts = (
            self.missing_date_count,
            self.unexpected_date_count,
            self.conflict_date_count,
        )
        if self.multi_batch_manifest_hash is None and any(value is not None for value in counts):
            raise ValueError("date-set counts require a registered multi-batch manifest")
        if self.multi_batch_manifest_hash is not None and any(value is None for value in counts):
            raise ValueError("registered multi-batch evidence requires all date-set counts")
        if self.multi_batch_manifest_hash is not None and self.expected_date_set_hash is None:
            raise ValueError("multi-batch evidence requires expected trading-date authority")
        if (
            self.operator_registered is not True
            or self.natural_day_inference_allowed is not False
            or self.provider_selected is not False
            or self.sdk_used is not False
            or self.network_used is not False
        ):
            raise ValueError("coverage supplements cannot gain inference, source, or runtime authority")
        object.__setattr__(
            self,
            "supplement_hash",
            canonical_sha256(
                {
                    "conflict_date_count": self.conflict_date_count,
                    "expected_date_set_hash": self.expected_date_set_hash,
                    "missing_date_count": self.missing_date_count,
                    "multi_batch_manifest_hash": self.multi_batch_manifest_hash,
                    "natural_day_inference_allowed": False,
                    "network_used": False,
                    "operator_registered": True,
                    "pagination_evidence_hash": self.pagination_evidence_hash,
                    "point_in_time_supplement_hash": self.point_in_time_supplement_hash,
                    "provider_selected": False,
                    "row_cap_resolution_hash": self.row_cap_resolution_hash,
                    "sdk_used": False,
                    "unexpected_date_count": self.unexpected_date_count,
                }
            ),
        )


@dataclass(frozen=True)
class CoverageRequirementResult:
    requirement_id: str
    state: str
    finding_code: str
    evidence_hashes: tuple[str, ...]
    requirement_hash: str = field(init=False)

    def __post_init__(self) -> None:
        requirement_id = identifier(self.requirement_id, "requirement_id")
        if requirement_id not in REQUIREMENT_IDS:
            raise ValueError("requirement_id is not registered")
        if self.state not in REQUIREMENT_STATES:
            raise ValueError("requirement state is not registered")
        finding = identifier(self.finding_code, "finding_code")
        hashes = tuple(sorted(set(digest(value, "evidence_hash") for value in self.evidence_hashes)))
        if not hashes:
            raise ValueError("requirement result requires immutable evidence lineage")
        object.__setattr__(self, "requirement_id", requirement_id)
        object.__setattr__(self, "finding_code", finding)
        object.__setattr__(self, "evidence_hashes", hashes)
        object.__setattr__(
            self,
            "requirement_hash",
            canonical_sha256(
                {
                    "evidence_hashes": hashes,
                    "finding_code": finding,
                    "requirement_id": requirement_id,
                    "state": self.state,
                }
            ),
        )


@dataclass(frozen=True)
class QmtHistoricalCoverageCompletenessEvidence:
    evidence_id: str
    source_evidence_id: str
    source_record_sha256: str
    raw_artifact_sha256: str
    front_artifact_sha256: str
    normalization_manifest_hash: str
    instrument_id: str
    requested_start_date: str
    requested_end_date: str
    observed_start_date: str
    observed_end_date: str
    row_count: int
    row_cap_state: str
    source_quality_state: str
    supplements: RegisteredCoverageSupplements
    requirements: tuple[CoverageRequirementResult, ...]
    gate_state: str
    finding_codes: tuple[str, ...]
    as_of_utc: str
    operator_review_required: bool = True
    historical_completeness_proven: bool = False
    gap_closed: bool = False
    provider_selected: bool = False
    sdk_used: bool = False
    network_used: bool = False
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_id", identifier(self.evidence_id, "evidence_id"))
        object.__setattr__(
            self, "source_evidence_id", identifier(self.source_evidence_id, "source_evidence_id")
        )
        for name in (
            "source_record_sha256",
            "raw_artifact_sha256",
            "front_artifact_sha256",
            "normalization_manifest_hash",
        ):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        instrument = str(self.instrument_id).strip().upper()
        if not (
            len(instrument) == 11
            and instrument[:6].isdigit()
            and instrument[6:] in {".XSHG", ".XSHE"}
        ):
            raise ValueError("instrument_id must be an A-share exchange identifier")
        object.__setattr__(self, "instrument_id", instrument)
        for name in (
            "requested_start_date",
            "requested_end_date",
            "observed_start_date",
            "observed_end_date",
        ):
            try:
                date.fromisoformat(getattr(self, name))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must be an ISO date") from exc
        if self.requested_start_date > self.requested_end_date:
            raise ValueError("requested date range is reversed")
        if self.observed_start_date > self.observed_end_date:
            raise ValueError("observed date range is reversed")
        if isinstance(self.row_count, bool) or not isinstance(self.row_count, int) or self.row_count <= 0:
            raise ValueError("row_count must be a positive integer")
        if self.row_cap_state not in {"AT_REGISTERED_CAP", "BELOW_REGISTERED_CAP"}:
            raise ValueError("row_cap_state is not registered")
        if self.source_quality_state != "BLOCKED_PENDING_SUPPLEMENTS":
            raise ValueError("source quality state must preserve FCP-0050 blocking")
        if not isinstance(self.supplements, RegisteredCoverageSupplements):
            raise TypeError("supplements must be RegisteredCoverageSupplements")
        requirements = tuple(self.requirements)
        if tuple(item.requirement_id for item in requirements) != REQUIREMENT_IDS:
            raise ValueError("requirements must use the exact registered order")
        by_id = {item.requirement_id: item for item in requirements}
        multi_batch_registered = self.supplements.multi_batch_manifest_hash is not None
        date_set_exact = (
            multi_batch_registered
            and self.supplements.missing_date_count == 0
            and self.supplements.unexpected_date_count == 0
            and self.supplements.conflict_date_count == 0
        )
        expected_requirement_states = {
            "EXPECTED_TRADING_DATE_ARTIFACT_REGISTERED": (
                "SATISFIED"
                if self.supplements.expected_date_set_hash is not None
                else "UNSATISFIED"
            ),
            "FCP_0050_QUALITY_RECORD_VALID": "SATISFIED",
            "MULTI_BATCH_COVERAGE_RECONCILED": (
                "SATISFIED" if multi_batch_registered else "UNSATISFIED"
            ),
            "PAGINATION_BEHAVIOR_REGISTERED": (
                "SATISFIED"
                if self.supplements.pagination_evidence_hash is not None
                else "UNSATISFIED"
            ),
            "POINT_IN_TIME_SUPPLEMENTS_REGISTERED": (
                "SATISFIED"
                if self.supplements.point_in_time_supplement_hash is not None
                else "UNSATISFIED"
            ),
            "RECONCILED_DATE_SET_EXACT": (
                "SATISFIED"
                if date_set_exact
                else "UNRESOLVED"
                if not multi_batch_registered
                else "UNSATISFIED"
            ),
            "REQUESTED_END_BOUNDARY_COVERED": (
                "SATISFIED"
                if self.observed_end_date >= self.requested_end_date
                else "UNSATISFIED"
            ),
            "REQUESTED_START_BOUNDARY_COVERED": (
                "SATISFIED"
                if self.observed_start_date <= self.requested_start_date
                else "UNSATISFIED"
            ),
            "ROW_CAP_AMBIGUITY_RESOLVED": (
                "SATISFIED"
                if self.row_cap_state == "BELOW_REGISTERED_CAP"
                or self.supplements.row_cap_resolution_hash is not None
                else "UNSATISFIED"
            ),
        }
        if any(
            by_id[requirement_id].state != expected_state
            for requirement_id, expected_state in expected_requirement_states.items()
        ):
            raise ValueError("requirement state disagrees with registered evidence")
        counts = (
            self.supplements.missing_date_count,
            self.supplements.unexpected_date_count,
            self.supplements.conflict_date_count,
        )
        expected_state = (
            "QUARANTINED_REGISTERED_CONFLICT"
            if self.supplements.conflict_date_count not in (None, 0)
            else "BLOCKED_REGISTERED_DATE_SET_MISMATCH"
            if any(value not in (None, 0) for value in counts[:2])
            else "BLOCKED_INCOMPLETE_REQUESTED_RANGE"
            if by_id["REQUESTED_START_BOUNDARY_COVERED"].state != "SATISFIED"
            or by_id["REQUESTED_END_BOUNDARY_COVERED"].state != "SATISFIED"
            else "COMPLETE_WITH_REGISTERED_EVIDENCE"
            if all(item.state == "SATISFIED" for item in requirements)
            else "BLOCKED_PENDING_REGISTERED_SUPPLEMENTS"
        )
        if self.gate_state != expected_state:
            raise ValueError("gate_state disagrees with exact requirements")
        complete = expected_state == "COMPLETE_WITH_REGISTERED_EVIDENCE"
        if self.historical_completeness_proven is not complete:
            raise ValueError("historical completeness claim disagrees with gate state")
        findings = tuple(sorted(set(self.finding_codes)))
        expected_findings = tuple(
            sorted(
                {"FCP_0050_REGISTERED_EVIDENCE_BOUND"}
                | {
                    item.finding_code
                    for item in requirements
                    if item.state != "SATISFIED"
                }
            )
        )
        if findings != expected_findings:
            raise ValueError("finding_codes disagree with requirement results")
        if (
            self.operator_review_required is not True
            or self.gap_closed is not False
            or self.provider_selected is not False
            or self.sdk_used is not False
            or self.network_used is not False
        ):
            raise ValueError("coverage evidence cannot gain source, runtime, or GAP authority")
        as_of = utc(self.as_of_utc, "as_of_utc")
        object.__setattr__(self, "requirements", requirements)
        object.__setattr__(self, "finding_codes", findings)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "as_of_utc": as_of,
                    "evidence_id": self.evidence_id,
                    "finding_codes": findings,
                    "front_artifact_sha256": self.front_artifact_sha256,
                    "gap_closed": False,
                    "gate_state": self.gate_state,
                    "historical_completeness_proven": complete,
                    "instrument_id": instrument,
                    "network_used": False,
                    "normalization_manifest_hash": self.normalization_manifest_hash,
                    "observed_end_date": self.observed_end_date,
                    "observed_start_date": self.observed_start_date,
                    "operator_review_required": True,
                    "provider_selected": False,
                    "raw_artifact_sha256": self.raw_artifact_sha256,
                    "requested_end_date": self.requested_end_date,
                    "requested_start_date": self.requested_start_date,
                    "requirement_hashes": tuple(item.requirement_hash for item in requirements),
                    "row_cap_state": self.row_cap_state,
                    "row_count": self.row_count,
                    "sdk_used": False,
                    "source_evidence_id": self.source_evidence_id,
                    "source_quality_state": self.source_quality_state,
                    "source_record_sha256": self.source_record_sha256,
                    "supplement_hash": self.supplements.supplement_hash,
                }
            ),
        )

    @property
    def unresolved_intervals(self) -> tuple[dict[str, str], ...]:
        intervals: list[dict[str, str]] = []
        if self.observed_start_date > self.requested_start_date:
            intervals.append(
                {
                    "end_exclusive": self.observed_start_date,
                    "kind": "LEADING",
                    "start_inclusive": self.requested_start_date,
                }
            )
        if self.observed_end_date < self.requested_end_date:
            intervals.append(
                {
                    "end_inclusive": self.requested_end_date,
                    "kind": "TRAILING",
                    "start_exclusive": self.observed_end_date,
                }
            )
        return tuple(intervals)
