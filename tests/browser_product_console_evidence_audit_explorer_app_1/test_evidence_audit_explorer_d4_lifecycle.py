from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    ConsoleArtifactRecord,
    ConsoleReadModel,
    EvidenceRelation,
    build_evidence_artifact_graph,
    build_evidence_lifecycle_dossier,
)


def _record(
    artifact_id: str,
    artifact_type: str,
    payload: dict,
) -> ConsoleArtifactRecord:
    return ConsoleArtifactRecord(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        relative_path=f"registered/{artifact_id}.json",
        content_sha256="c" * 64,
        payload=payload,
    )


def _model(
    records: tuple[ConsoleArtifactRecord, ...],
) -> ConsoleReadModel:
    return ConsoleReadModel(
        correlation_id="corr-d4",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=tuple(
            record.artifact_id for record in records
        ),
        artifact_records=records,
    )


def _dossier(
    records: tuple[ConsoleArtifactRecord, ...],
):
    model = _model(records)
    graph = build_evidence_artifact_graph(model)
    return build_evidence_lifecycle_dossier(
        model,
        graph,
    )


def _complete_records():
    return (
        _record(
            "validation-1",
            "paper_validation",
            {
                "validation_status": "PASS_WITH_REVIEW",
                "validated_at_utc": "2026-07-14T01:00:00Z",
            },
        ),
        _record(
            "shadow-1",
            "shadow_observation",
            {
                "observation_status": "OBSERVED",
                "observed_at_utc": "2026-07-14T02:00:00Z",
                "derived_from_artifact_id": "validation-1",
            },
        ),
        _record(
            "review-1",
            "operator_review",
            {
                "review_status": "REVIEW_REQUIRED",
                "reviewed_at_utc": "2026-07-14T03:00:00Z",
                "review_for_artifact_id": "shadow-1",
            },
        ),
        _record(
            "archive-1",
            "report_archive",
            {
                "archive_status": "ARCHIVED",
                "archived_at_utc": "2026-07-14T04:00:00Z",
                "archive_for_artifact_id": "review-1",
            },
        ),
    )


def test_d4_builds_complete_lifecycle_dossier():
    dossier = _dossier(_complete_records())

    assert dossier.state == "AVAILABLE"
    assert tuple(
        item.artifact_id for item in dossier.items
    ) == (
        "validation-1",
        "shadow-1",
        "review-1",
        "archive-1",
    )
    assert tuple(
        item.stage for item in dossier.items
    ) == (
        "PAPER_VALIDATION",
        "SHADOW_OBSERVATION",
        "OPERATOR_REVIEW",
        "REPORT_ARCHIVE",
    )
    assert dossier.missing_artifact_types == ()
    assert dossier.unresolved_artifact_ids == ()


def test_d4_preserves_explicit_status_and_time():
    dossier = _dossier(_complete_records())

    assert tuple(
        (item.status, item.observed_at)
        for item in dossier.items
    ) == (
        (
            "PASS_WITH_REVIEW",
            "2026-07-14T01:00:00Z",
        ),
        (
            "OBSERVED",
            "2026-07-14T02:00:00Z",
        ),
        (
            "REVIEW_REQUIRED",
            "2026-07-14T03:00:00Z",
        ),
        (
            "ARCHIVED",
            "2026-07-14T04:00:00Z",
        ),
    )


def test_d4_builds_registered_typed_links():
    dossier = _dossier(_complete_records())

    assert tuple(
        (
            link.source_artifact_id,
            link.relation,
            link.target_artifact_id,
        )
        for link in dossier.links
    ) == (
        (
            "shadow-1",
            EvidenceRelation.DERIVED_FROM,
            "validation-1",
        ),
        (
            "review-1",
            EvidenceRelation.REVIEWS,
            "shadow-1",
        ),
        (
            "archive-1",
            EvidenceRelation.ARCHIVES,
            "review-1",
        ),
    )
    assert dict(dossier.relation_counts) == {
        "ARCHIVES": 1,
        "DERIVED_FROM": 1,
        "REVIEWS": 1,
    }


def test_d4_stage_counts_are_deterministic():
    dossier = _dossier(_complete_records())

    assert dict(dossier.stage_counts) == {
        "OPERATOR_REVIEW": 1,
        "PAPER_VALIDATION": 1,
        "REPORT_ARCHIVE": 1,
        "SHADOW_OBSERVATION": 1,
    }


def test_d4_incomplete_when_lifecycle_type_missing():
    dossier = _dossier(
        _complete_records()[:-1]
    )

    assert dossier.state == "INCOMPLETE"
    assert dossier.missing_artifact_types == (
        "report_archive",
    )


def test_d4_empty_when_no_registered_lifecycle_evidence():
    dossier = _dossier(
        (
            _record(
                "manifest-1",
                "manifest",
                {"status": "READY"},
            ),
        )
    )

    assert dossier.state == (
        "NO_REGISTERED_LIFECYCLE_EVIDENCE"
    )
    assert dossier.items == ()
    assert dossier.links == ()
    assert dossier.missing_artifact_types == (
        "operator_review",
        "paper_validation",
        "report_archive",
        "shadow_observation",
    )


def test_d4_unresolved_registered_reference_marks_incomplete():
    records = list(_complete_records())
    records[3] = _record(
        "archive-1",
        "report_archive",
        {
            "archive_status": "ARCHIVED",
            "archive_for_artifact_id": "missing-review",
        },
    )
    dossier = _dossier(tuple(records))

    assert dossier.state == "INCOMPLETE"
    assert dossier.unresolved_artifact_ids == (
        "missing-review",
    )
    assert all(
        link.target_artifact_id != "missing-review"
        for link in dossier.links
    )


def test_d4_exposes_evidence_keys_not_mutable_payload():
    dossier = _dossier(_complete_records())
    validation = dossier.items[0]

    assert validation.evidence_keys == (
        "validated_at_utc",
        "validation_status",
    )
    assert not hasattr(validation, "payload")


def test_d4_ignores_non_lifecycle_artifact_types():
    dossier = _dossier(
        (
            _record(
                "note-1",
                "ai_explanation",
                {
                    "status": "GENERATED",
                    "review_for_artifact_id": "missing-1",
                },
            ),
        )
    )

    assert dossier.items == ()
    assert dossier.state == (
        "NO_REGISTERED_LIFECYCLE_EVIDENCE"
    )


def test_d4_rejects_graph_read_model_artifact_mismatch():
    model_a = _model(
        (
            _record(
                "validation-a",
                "paper_validation",
                {"status": "PASS"},
            ),
        )
    )
    model_b = _model(
        (
            _record(
                "validation-b",
                "paper_validation",
                {"status": "PASS"},
            ),
        )
    )
    graph_b = build_evidence_artifact_graph(model_b)

    with pytest.raises(
        ValueError,
        match="artifact mismatch",
    ):
        build_evidence_lifecycle_dossier(
            model_a,
            graph_b,
        )


def test_d4_rejects_graph_read_model_correlation_mismatch():
    model = _model(_complete_records())
    graph = build_evidence_artifact_graph(model)
    other = ConsoleReadModel(
        correlation_id="corr-other",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=model.source_artifact_ids,
        artifact_records=model.artifact_records,
    )

    with pytest.raises(
        ValueError,
        match="correlation mismatch",
    ):
        build_evidence_lifecycle_dossier(
            other,
            graph,
        )


def test_d4_boundary_flags_remain_enabled():
    dossier = _dossier(_complete_records())

    assert dossier.registered_artifact_only is True
    assert dossier.read_only is True
    assert dossier.operator_review_required is True
    assert dossier.deterministic_authority is True
    assert dossier.paper_only is True
    assert all(
        item.registered_artifact_only
        and item.read_only
        and item.operator_review_required
        and item.deterministic_authority
        for item in dossier.items
    )


def test_d4_unsafe_payload_keys_are_not_exposed():
    dossier = _dossier(
        (
            _record(
                "validation-1",
                "paper_validation",
                {
                    "status": "PASS",
                    "../unsafe": "hidden",
                },
            ),
        )
    )

    assert dossier.items[0].evidence_keys == (
        "status",
    )
