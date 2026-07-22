from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0051_guojin_qmt_historical_coverage_completeness_gate_app_1 import (
    RegisteredCoverageSupplements,
    build_qmt_historical_coverage_completeness_evidence,
    build_qmt_historical_coverage_registered_record,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / "FCF_REGISTERED_EVIDENCE_FCP_0050_GUOJIN_QMT_DUAL_EXPORT_QUALITY.json"
AS_OF = "2026-07-22T01:00:00Z"
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64
HASH_E = "e" * 64


def _source() -> dict[str, object]:
    return json.loads(SOURCE_PATH.read_text(encoding="ascii"))


def _rehash(record: dict[str, object]) -> dict[str, object]:
    record.pop("record_sha256", None)
    record["record_sha256"] = canonical_sha256(record)
    return record


def _covered_source() -> dict[str, object]:
    record = deepcopy(_source())
    observation = record["observation"]
    assert isinstance(observation, dict)
    observation["actual_start_date"] = observation["requested_start_date"]
    observation["actual_end_date"] = observation["requested_end_date"]
    return _rehash(record)


def _complete_supplements(**updates: object) -> RegisteredCoverageSupplements:
    values: dict[str, object] = {
        "expected_date_set_hash": HASH_A,
        "pagination_evidence_hash": HASH_B,
        "multi_batch_manifest_hash": HASH_C,
        "missing_date_count": 0,
        "unexpected_date_count": 0,
        "conflict_date_count": 0,
        "point_in_time_supplement_hash": HASH_D,
        "row_cap_resolution_hash": HASH_E,
    }
    values.update(updates)
    return RegisteredCoverageSupplements(**values)


def _build(
    source: dict[str, object] | MappingProxyType = None,
    supplements: RegisteredCoverageSupplements | None = None,
):
    return build_qmt_historical_coverage_completeness_evidence(
        _source() if source is None else source,
        RegisteredCoverageSupplements() if supplements is None else supplements,
        evidence_id="fcp-0051-qmt-historical-coverage-gate-v1",
        as_of_utc=AS_OF,
    )


def _freeze(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(nested) for key, nested in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(nested) for nested in value)
    return value


def test_actual_fcp_0050_record_fails_closed_on_leading_interval() -> None:
    evidence = _build()

    assert evidence.gate_state == "BLOCKED_INCOMPLETE_REQUESTED_RANGE"
    assert evidence.historical_completeness_proven is False
    assert evidence.operator_review_required is True
    assert evidence.provider_selected is False
    assert evidence.unresolved_intervals == (
        {
            "end_exclusive": "2024-06-28",
            "kind": "LEADING",
            "start_inclusive": "2021-01-01",
        },
    )
    states = {item.requirement_id: item.state for item in evidence.requirements}
    assert states["REQUESTED_START_BOUNDARY_COVERED"] == "UNSATISFIED"
    assert states["REQUESTED_END_BOUNDARY_COVERED"] == "SATISFIED"
    assert states["RECONCILED_DATE_SET_EXACT"] == "UNRESOLVED"
    assert "ROW_CAP_AMBIGUITY_UNRESOLVED" in evidence.finding_codes


def test_mapping_proxy_source_record_is_supported() -> None:
    frozen = _freeze(_source())
    assert isinstance(frozen, MappingProxyType)

    evidence = _build(frozen)

    assert evidence.source_record_sha256 == _source()["record_sha256"]


def test_source_record_tampering_is_rejected() -> None:
    record = _source()
    observation = record["observation"]
    assert isinstance(observation, dict)
    observation["row_count"] = 499

    with pytest.raises(ValueError, match="source record SHA-256 mismatch"):
        _build(record)


def test_source_authority_escalation_is_rejected() -> None:
    record = _source()
    quality = record["quality"]
    assert isinstance(quality, dict)
    quality["provider_selected"] = True
    _rehash(record)

    with pytest.raises(ValueError, match="authority boundary"):
        _build(record)


def test_covered_boundaries_without_supplements_remain_blocked() -> None:
    evidence = _build(_covered_source())

    assert evidence.gate_state == "BLOCKED_PENDING_REGISTERED_SUPPLEMENTS"
    assert evidence.unresolved_intervals == ()
    assert evidence.historical_completeness_proven is False


def test_positive_registered_proof_can_satisfy_the_gate() -> None:
    evidence = _build(_covered_source(), _complete_supplements())

    assert evidence.gate_state == "COMPLETE_WITH_REGISTERED_EVIDENCE"
    assert evidence.historical_completeness_proven is True
    assert all(item.state == "SATISFIED" for item in evidence.requirements)
    assert evidence.finding_codes == ("FCP_0050_REGISTERED_EVIDENCE_BOUND",)


def test_registered_missing_dates_block_completeness() -> None:
    evidence = _build(
        _covered_source(),
        _complete_supplements(missing_date_count=1),
    )

    assert evidence.gate_state == "BLOCKED_REGISTERED_DATE_SET_MISMATCH"
    assert evidence.historical_completeness_proven is False
    states = {item.requirement_id: item.state for item in evidence.requirements}
    assert states["RECONCILED_DATE_SET_EXACT"] == "UNSATISFIED"


def test_registered_conflict_quarantines_completeness() -> None:
    evidence = _build(
        _covered_source(),
        _complete_supplements(conflict_date_count=1),
    )

    assert evidence.gate_state == "QUARANTINED_REGISTERED_CONFLICT"
    assert evidence.historical_completeness_proven is False


def test_requirement_state_cannot_be_forged() -> None:
    evidence = _build()
    forged = tuple(
        replace(item, state="SATISFIED")
        if item.requirement_id == "REQUESTED_START_BOUNDARY_COVERED"
        else item
        for item in evidence.requirements
    )

    with pytest.raises(ValueError, match="disagrees with registered evidence"):
        replace(evidence, requirements=forged)


def test_multi_batch_counts_require_registered_manifest() -> None:
    with pytest.raises(ValueError, match="counts require"):
        RegisteredCoverageSupplements(missing_date_count=0)


def test_multi_batch_manifest_requires_all_counts_and_calendar() -> None:
    with pytest.raises(ValueError, match="requires all date-set counts"):
        RegisteredCoverageSupplements(multi_batch_manifest_hash=HASH_A)
    with pytest.raises(ValueError, match="expected trading-date authority"):
        RegisteredCoverageSupplements(
            multi_batch_manifest_hash=HASH_A,
            missing_date_count=0,
            unexpected_date_count=0,
            conflict_date_count=0,
        )


def test_natural_day_inference_and_runtime_authority_are_rejected() -> None:
    with pytest.raises(ValueError, match="cannot gain"):
        RegisteredCoverageSupplements(natural_day_inference_allowed=True)
    with pytest.raises(ValueError, match="cannot gain"):
        RegisteredCoverageSupplements(network_used=True)


def test_registered_record_is_deterministic_and_path_free() -> None:
    evidence = _build()

    first = build_qmt_historical_coverage_registered_record(evidence)
    second = build_qmt_historical_coverage_registered_record(evidence)
    text = json.dumps(first, ensure_ascii=True, sort_keys=True)

    assert first == second
    assert first["record_sha256"] == canonical_sha256(
        {key: value for key, value in first.items() if key != "record_sha256"}
    )
    assert "C:\\" not in text
    assert "price_600028.txt" not in text
    assert "timetag" not in text
    assert first["gate"]["historical_completeness_proven"] is False


def test_checked_in_registered_record_matches_the_builder_exactly() -> None:
    evidence = _build()
    expected = json.loads(
        (
            ROOT
            / "FCF_REGISTERED_EVIDENCE_FCP_0051_GUOJIN_QMT_HISTORICAL_COVERAGE_COMPLETENESS_GATE.json"
        ).read_text(encoding="ascii")
    )

    assert build_qmt_historical_coverage_registered_record(evidence) == expected


def test_gate_cannot_precede_source_registration() -> None:
    with pytest.raises(ValueError, match="cannot precede"):
        build_qmt_historical_coverage_completeness_evidence(
            _source(),
            RegisteredCoverageSupplements(),
            evidence_id="fcp-0051-qmt-historical-coverage-gate-v1",
            as_of_utc="2026-07-22T00:00:00Z",
        )
