from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    instant,
)

from .contracts import (
    REQUIREMENT_IDS,
    CoverageRequirementResult,
    QmtHistoricalCoverageCompletenessEvidence,
    RegisteredCoverageSupplements,
)


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(nested) for key, nested in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(nested) for nested in value]
    return value


def _mapping(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    return {str(key): nested for key, nested in value.items()}


def _requirement(
    requirement_id: str,
    state: str,
    finding_code: str,
    *evidence_hashes: str,
) -> CoverageRequirementResult:
    return CoverageRequirementResult(
        requirement_id=requirement_id,
        state=state,
        finding_code=finding_code,
        evidence_hashes=tuple(evidence_hashes),
    )


def build_qmt_historical_coverage_completeness_evidence(
    source_record: Mapping[str, object],
    supplements: RegisteredCoverageSupplements,
    *,
    evidence_id: str,
    as_of_utc: str,
) -> QmtHistoricalCoverageCompletenessEvidence:
    if not isinstance(supplements, RegisteredCoverageSupplements):
        raise TypeError("supplements must be RegisteredCoverageSupplements")
    as_of = instant(as_of_utc, "as_of_utc")
    plain = _plain(source_record)
    if not isinstance(plain, dict):
        raise TypeError("source_record must be a mapping")
    record = dict(plain)
    source_record_sha256 = digest(record.pop("record_sha256", None), "record_sha256")
    if canonical_sha256(record) != source_record_sha256:
        raise ValueError("FCP-0050 source record SHA-256 mismatch")
    if record.get("schema_version") != 1 or record.get("operator_review_required") is not True:
        raise ValueError("FCP-0050 source record identity is invalid")
    artifact_pair = _mapping(record.get("artifact_pair"), "artifact_pair")
    raw = _mapping(artifact_pair.get("raw"), "raw")
    front = _mapping(artifact_pair.get("front"), "front")
    observation = _mapping(record.get("observation"), "observation")
    quality = _mapping(record.get("quality"), "quality")
    lineage = _mapping(record.get("lineage"), "lineage")
    if (
        artifact_pair.get("raw_provider_bytes_committed") is not False
        or artifact_pair.get("local_paths_committed") is not False
        or quality.get("historical_completeness_claimed") is not False
        or quality.get("provider_selected") is not False
        or quality.get("gap_closed") is not False
        or quality.get("sdk_used") is not False
        or quality.get("network_used") is not False
    ):
        raise ValueError("FCP-0050 source authority boundary is invalid")
    if quality.get("quality_state") != "BLOCKED_PENDING_SUPPLEMENTS":
        raise ValueError("FCP-0050 source quality blocking is missing")
    registered_at = instant(record.get("registered_at_utc"), "registered_at_utc")
    if registered_at > as_of:
        raise ValueError("coverage gate cannot precede FCP-0050 evidence")

    requested_start = str(observation.get("requested_start_date"))
    requested_end = str(observation.get("requested_end_date"))
    observed_start = str(observation.get("actual_start_date"))
    observed_end = str(observation.get("actual_end_date"))
    start_covered = observed_start <= requested_start
    end_covered = observed_end >= requested_end
    source_hashes = (source_record_sha256, supplements.supplement_hash)
    expected_registered = supplements.expected_date_set_hash is not None
    pagination_registered = supplements.pagination_evidence_hash is not None
    multi_batch_registered = supplements.multi_batch_manifest_hash is not None
    pit_registered = supplements.point_in_time_supplement_hash is not None
    cap_resolved = (
        observation.get("row_cap_state") == "BELOW_REGISTERED_CAP"
        or supplements.row_cap_resolution_hash is not None
    )
    date_set_exact = (
        multi_batch_registered
        and supplements.missing_date_count == 0
        and supplements.unexpected_date_count == 0
        and supplements.conflict_date_count == 0
    )
    requirements = (
        _requirement(
            "EXPECTED_TRADING_DATE_ARTIFACT_REGISTERED",
            "SATISFIED" if expected_registered else "UNSATISFIED",
            "EXPECTED_TRADING_DATE_ARTIFACT_MISSING",
            *(source_hashes + ((supplements.expected_date_set_hash,) if expected_registered else ())),
        ),
        _requirement(
            "FCP_0050_QUALITY_RECORD_VALID",
            "SATISFIED",
            "FCP_0050_QUALITY_RECORD_INVALID",
            source_record_sha256,
        ),
        _requirement(
            "MULTI_BATCH_COVERAGE_RECONCILED",
            "SATISFIED" if multi_batch_registered else "UNSATISFIED",
            "MULTI_BATCH_COVERAGE_RECONCILIATION_MISSING",
            *(source_hashes + ((supplements.multi_batch_manifest_hash,) if multi_batch_registered else ())),
        ),
        _requirement(
            "PAGINATION_BEHAVIOR_REGISTERED",
            "SATISFIED" if pagination_registered else "UNSATISFIED",
            "PAGINATION_BEHAVIOR_EVIDENCE_MISSING",
            *(source_hashes + ((supplements.pagination_evidence_hash,) if pagination_registered else ())),
        ),
        _requirement(
            "POINT_IN_TIME_SUPPLEMENTS_REGISTERED",
            "SATISFIED" if pit_registered else "UNSATISFIED",
            "POINT_IN_TIME_SUPPLEMENTS_MISSING",
            *(source_hashes + ((supplements.point_in_time_supplement_hash,) if pit_registered else ())),
        ),
        _requirement(
            "RECONCILED_DATE_SET_EXACT",
            "SATISFIED" if date_set_exact else "UNRESOLVED" if not multi_batch_registered else "UNSATISFIED",
            "RECONCILED_DATE_SET_NOT_EXACT",
            *source_hashes,
        ),
        _requirement(
            "REQUESTED_END_BOUNDARY_COVERED",
            "SATISFIED" if end_covered else "UNSATISFIED",
            "TRAILING_REQUEST_INTERVAL_UNCOVERED",
            source_record_sha256,
        ),
        _requirement(
            "REQUESTED_START_BOUNDARY_COVERED",
            "SATISFIED" if start_covered else "UNSATISFIED",
            "LEADING_REQUEST_INTERVAL_UNCOVERED",
            source_record_sha256,
        ),
        _requirement(
            "ROW_CAP_AMBIGUITY_RESOLVED",
            "SATISFIED" if cap_resolved else "UNSATISFIED",
            "ROW_CAP_AMBIGUITY_UNRESOLVED",
            *(source_hashes + ((supplements.row_cap_resolution_hash,) if supplements.row_cap_resolution_hash else ())),
        ),
    )
    if tuple(item.requirement_id for item in requirements) != REQUIREMENT_IDS:
        raise AssertionError("internal completeness requirement order changed")
    counts = (
        supplements.missing_date_count,
        supplements.unexpected_date_count,
        supplements.conflict_date_count,
    )
    gate_state = (
        "QUARANTINED_REGISTERED_CONFLICT"
        if supplements.conflict_date_count not in (None, 0)
        else "BLOCKED_REGISTERED_DATE_SET_MISMATCH"
        if any(value not in (None, 0) for value in counts[:2])
        else "BLOCKED_INCOMPLETE_REQUESTED_RANGE"
        if not start_covered or not end_covered
        else "COMPLETE_WITH_REGISTERED_EVIDENCE"
        if all(item.state == "SATISFIED" for item in requirements)
        else "BLOCKED_PENDING_REGISTERED_SUPPLEMENTS"
    )
    findings = tuple(
        sorted(
            {"FCP_0050_REGISTERED_EVIDENCE_BOUND"}
            | {item.finding_code for item in requirements if item.state != "SATISFIED"}
        )
    )
    row_count = observation.get("row_count")
    if isinstance(row_count, bool) or not isinstance(row_count, int):
        raise ValueError("FCP-0050 row_count must be an integer")
    return QmtHistoricalCoverageCompletenessEvidence(
        evidence_id=evidence_id,
        source_evidence_id=str(record.get("evidence_id")),
        source_record_sha256=source_record_sha256,
        raw_artifact_sha256=digest(raw.get("artifact_sha256"), "raw_artifact_sha256"),
        front_artifact_sha256=digest(front.get("artifact_sha256"), "front_artifact_sha256"),
        normalization_manifest_hash=digest(
            lineage.get("normalization_manifest_hash"), "normalization_manifest_hash"
        ),
        instrument_id=str(observation.get("instrument_id")),
        requested_start_date=requested_start,
        requested_end_date=requested_end,
        observed_start_date=observed_start,
        observed_end_date=observed_end,
        row_count=row_count,
        row_cap_state=str(observation.get("row_cap_state")),
        source_quality_state=str(quality.get("quality_state")),
        supplements=supplements,
        requirements=requirements,
        gate_state=gate_state,
        finding_codes=findings,
        as_of_utc=as_of_utc,
        historical_completeness_proven=(
            gate_state == "COMPLETE_WITH_REGISTERED_EVIDENCE"
        ),
    )


def build_qmt_historical_coverage_registered_record(
    evidence: QmtHistoricalCoverageCompletenessEvidence,
) -> dict[str, object]:
    if not isinstance(evidence, QmtHistoricalCoverageCompletenessEvidence):
        raise TypeError("evidence must be QmtHistoricalCoverageCompletenessEvidence")
    record: dict[str, object] = {
        "coverage": {
            "observed_end_date": evidence.observed_end_date,
            "observed_start_date": evidence.observed_start_date,
            "requested_end_date": evidence.requested_end_date,
            "requested_start_date": evidence.requested_start_date,
            "row_cap_state": evidence.row_cap_state,
            "row_count": evidence.row_count,
            "unresolved_intervals": list(evidence.unresolved_intervals),
        },
        "evidence_id": evidence.evidence_id,
        "finding_codes": list(evidence.finding_codes),
        "gate": {
            "gap_closed": False,
            "gate_state": evidence.gate_state,
            "historical_completeness_proven": evidence.historical_completeness_proven,
            "network_used": False,
            "operator_review_required": True,
            "provider_selected": False,
            "sdk_used": False,
        },
        "instrument_id": evidence.instrument_id,
        "lineage": {
            "evidence_hash": evidence.evidence_hash,
            "front_artifact_sha256": evidence.front_artifact_sha256,
            "normalization_manifest_hash": evidence.normalization_manifest_hash,
            "raw_artifact_sha256": evidence.raw_artifact_sha256,
            "source_evidence_id": evidence.source_evidence_id,
            "source_quality_state": evidence.source_quality_state,
            "source_record_sha256": evidence.source_record_sha256,
            "supplement_hash": evidence.supplements.supplement_hash,
        },
        "registered_at_utc": evidence.as_of_utc,
        "requirements": [
            {
                "evidence_hashes": list(item.evidence_hashes),
                "finding_code": item.finding_code,
                "requirement_hash": item.requirement_hash,
                "requirement_id": item.requirement_id,
                "state": item.state,
            }
            for item in evidence.requirements
        ],
        "schema_version": 1,
    }
    record["record_sha256"] = canonical_sha256(record)
    return record
