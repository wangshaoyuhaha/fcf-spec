from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from apps.fcp_0077_a_share_trusted_data_supply_chain_coverage_evidence_matrix_app_1 import (
    CAPABILITY_IDS,
    COVERAGE_STATES,
    GAP_IDS,
    GapCoverageRequirement,
    RegisteredImplementationEvidence,
    build_coverage_matrix,
    coverage_requirements,
    current_repository_evidence,
)


ROOT = Path(__file__).resolve().parents[2]


def _file(tmp_path: Path, name: str = "component.py", payload: bytes = b"value = 1\n"):
    path = tmp_path / "apps" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path, hashlib.sha256(payload).hexdigest()


def _evidence(tmp_path: Path, **changes) -> RegisteredImplementationEvidence:
    _, sha256 = _file(tmp_path)
    values = {
        "component_id": "component-1",
        "gap_id": "V2-FR-GAP-087",
        "repository_path": "apps/component.py",
        "artifact_sha256": sha256,
        "capabilities": ("CANONICAL_TYPED_OBSERVATION",),
        "observed_at_utc": "2026-07-23T00:00:00Z",
    }
    values.update(changes)
    return RegisteredImplementationEvidence(**values)


def test_d1_closed_gap_and_capability_vocabularies_are_exact() -> None:
    assert GAP_IDS == tuple(f"V2-FR-GAP-{number:03d}" for number in range(87, 94))
    assert CAPABILITY_IDS == tuple(sorted(CAPABILITY_IDS))
    assert COVERAGE_STATES == (
        "NO_FOUNDATION_EVIDENCE_GAP_OPEN",
        "FOUNDATION_PARTIAL_GAP_OPEN",
        "FOUNDATION_COVERED_GAP_OPEN",
    )
    requirements = coverage_requirements()
    assert tuple(item.gap_id for item in requirements) == GAP_IDS
    assert all(item.operator_review_required is True for item in requirements)


@pytest.mark.parametrize(
    ("changes", "error"),
    (
        ({"gap_id": "V2-FR-GAP-094"}, "gap_id"),
        ({"required_capabilities": ()}, "must not be empty"),
        ({"required_capabilities": ("UNKNOWN",)}, "unregistered capability"),
        ({"external_evidence_required": 1}, "must be bool"),
        ({"operator_review_required": False}, "Operator review"),
    ),
)
def test_d1_requirement_rejects_open_or_untyped_values(changes, error) -> None:
    values = {
        "gap_id": "V2-FR-GAP-087",
        "required_capabilities": ("CANONICAL_TYPED_OBSERVATION",),
        "external_evidence_required": False,
    }
    values.update(changes)
    with pytest.raises((TypeError, ValueError), match=error):
        GapCoverageRequirement(**values)


@pytest.mark.parametrize(
    ("changes", "error"),
    (
        ({"repository_path": "../outside.py"}, "repository-relative"),
        ({"repository_path": "runtime/output.py"}, "outside"),
        ({"artifact_sha256": "A" * 64}, "lowercase SHA-256"),
        ({"capabilities": ("UNKNOWN",)}, "unregistered capability"),
        ({"operator_registered": False}, "Operator registration"),
        ({"claims_data_authority": True}, "cannot establish authority"),
        ({"closes_gap": True}, "cannot establish authority"),
    ),
)
def test_d2_evidence_rejects_unsafe_or_authorizing_values(tmp_path, changes, error) -> None:
    with pytest.raises((TypeError, ValueError), match=error):
        _evidence(tmp_path, **changes)


def test_d2_evidence_hash_is_deterministic(tmp_path: Path) -> None:
    first = _evidence(tmp_path)
    second = _evidence(tmp_path)
    assert first == second
    assert first.evidence_hash == second.evidence_hash
    assert first.claims_data_authority is False
    assert first.closes_gap is False


def test_d3_exact_file_hash_is_verified(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    requirements = coverage_requirements()
    matrix = build_coverage_matrix(
        tmp_path,
        requirements,
        (evidence,),
        evaluated_at_utc="2026-07-23T01:00:00Z",
    )
    assert matrix.rows[0].coverage_state == "FOUNDATION_PARTIAL_GAP_OPEN"
    (tmp_path / "apps" / "component.py").write_text("value = 2\n", encoding="ascii")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        build_coverage_matrix(
            tmp_path,
            requirements,
            (evidence,),
            evaluated_at_utc="2026-07-23T01:00:00Z",
        )


def test_d3_future_and_untyped_evidence_fail_closed(tmp_path: Path) -> None:
    future = _evidence(tmp_path, observed_at_utc="2026-07-23T02:00:00Z")
    with pytest.raises(ValueError, match="observed in the future"):
        build_coverage_matrix(
            tmp_path,
            coverage_requirements(),
            (future,),
            evaluated_at_utc="2026-07-23T01:00:00Z",
        )
    with pytest.raises(TypeError, match="RegisteredImplementationEvidence"):
        build_coverage_matrix(
            tmp_path,
            coverage_requirements(),
            ({"gap_id": "V2-FR-GAP-087"},),
            evaluated_at_utc="2026-07-23T01:00:00Z",
        )


def test_d3_duplicate_identity_and_reordered_requirements_fail(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    with pytest.raises(ValueError, match="identity must be unique"):
        build_coverage_matrix(
            tmp_path,
            coverage_requirements(),
            (evidence, evidence),
            evaluated_at_utc="2026-07-23T01:00:00Z",
        )
    with pytest.raises(ValueError, match="exact ordered gap range"):
        build_coverage_matrix(
            tmp_path,
            tuple(reversed(coverage_requirements())),
            (evidence,),
            evaluated_at_utc="2026-07-23T01:00:00Z",
        )


def test_d4_missing_capabilities_are_exact_and_visible(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path)
    matrix = build_coverage_matrix(
        tmp_path,
        coverage_requirements(),
        (evidence,),
        evaluated_at_utc="2026-07-23T01:00:00Z",
    )
    first = matrix.rows[0]
    assert first.observed_capabilities == ("CANONICAL_TYPED_OBSERVATION",)
    assert first.missing_capabilities == ("PROVIDER_EDGE_CONVERSION",)
    assert all(row.gap_open is True for row in matrix.rows)
    assert all(row.authority_established is False for row in matrix.rows)
    assert all(row.provider_selected is False for row in matrix.rows)
    assert matrix.rows[1].coverage_state == "NO_FOUNDATION_EVIDENCE_GAP_OPEN"


def test_d4_complete_foundation_still_cannot_close_gap(tmp_path: Path) -> None:
    first = _evidence(tmp_path)
    second = replace(
        first,
        component_id="component-2",
        capabilities=("PROVIDER_EDGE_CONVERSION",),
    )
    matrix = build_coverage_matrix(
        tmp_path,
        coverage_requirements(),
        (second, first),
        evaluated_at_utc="2026-07-23T01:00:00Z",
    )
    row = matrix.rows[0]
    assert row.coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert row.missing_capabilities == ()
    assert row.gap_open is True
    assert row.authority_established is False


def test_d5_current_repository_matrix_records_real_foundation_gaps() -> None:
    evidence = current_repository_evidence(ROOT)
    matrix = build_coverage_matrix(
        ROOT,
        coverage_requirements(),
        evidence,
        evaluated_at_utc="2026-07-23T01:00:00Z",
    )
    rows = {row.requirement.gap_id: row for row in matrix.rows}
    assert rows["V2-FR-GAP-087"].coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert rows["V2-FR-GAP-088"].missing_capabilities == ("PUBLICATION_CLOCK",)
    assert rows["V2-FR-GAP-089"].missing_capabilities == (
        "CORPORATE_ACTION_LINEAGE",
        "QUERY_POLICY_LINEAGE",
    )
    assert rows["V2-FR-GAP-090"].coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert rows["V2-FR-GAP-091"].coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert rows["V2-FR-GAP-092"].coverage_state == "FOUNDATION_COVERED_GAP_OPEN"
    assert rows["V2-FR-GAP-093"].missing_capabilities == (
        "PROVIDER_PROFILE_AKSHARE",
        "PROVIDER_PROFILE_BAOSTOCK",
        "PROVIDER_PROFILE_TUSHARE",
    )
    assert matrix.status == "FOUNDATION_EVIDENCE_ONLY_GAPS_REMAIN_OPEN"
    assert matrix.changes_gap_status is False
    assert matrix.promotes_candidate_data is False
    assert matrix.provider_selected is False


def test_d5_matrix_is_independent_of_evidence_input_order() -> None:
    evidence = current_repository_evidence(ROOT)
    first = build_coverage_matrix(
        ROOT,
        coverage_requirements(),
        evidence,
        evaluated_at_utc="2026-07-23T01:00:00Z",
    )
    second = build_coverage_matrix(
        ROOT,
        coverage_requirements(),
        tuple(reversed(evidence)),
        evaluated_at_utc="2026-07-23T01:00:00Z",
    )
    assert first == second
    assert first.matrix_hash == second.matrix_hash


def test_d6_no_network_or_execution_surface_is_present() -> None:
    source = (
        ROOT
        / "apps/fcp_0077_a_share_trusted_data_supply_chain_coverage_evidence_matrix_app_1/matrix.py"
    ).read_text(encoding="ascii").lower()
    forbidden = ("requests", "urllib", "socket", "xtquant", "rqdatac", "place_order")
    assert all(term not in source for term in forbidden)
