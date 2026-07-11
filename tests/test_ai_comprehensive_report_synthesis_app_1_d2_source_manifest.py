from copy import deepcopy
from typing import Any

import pytest

from apps.ai_comprehensive_report_synthesis_app_1 import (
    ManifestViolation,
    REQUIRED_ARTIFACT_TYPES,
    SourceRecordViolation,
    build_source_manifest,
    build_source_record,
    build_version_lock,
    require_valid_source_manifest,
    validate_source_manifest,
    validate_source_record,
)


def _digest(index: int) -> str:
    return f"{index:064x}"


def _record(
    artifact_type: str,
    index: int,
    *,
    correlation_id: str = "corr-report-001",
    research_run_id: str = "research-run-001",
) -> dict[str, Any]:
    return build_source_record(
        artifact_id=f"artifact-{index:02d}",
        artifact_type=artifact_type,
        artifact_version=f"1.0.{index}",
        correlation_id=correlation_id,
        research_run_id=research_run_id,
        source_stage_id=f"SOURCE-D{index}",
        source_path=f"artifacts/source_{index:02d}.json",
        locked_sha256=_digest(index),
        source_conclusion_state="PRESERVED",
        validation_state="VALIDATED",
        requirement_level=(
            "REQUIRED"
            if artifact_type in REQUIRED_ARTIFACT_TYPES
            else "OPTIONAL"
        ),
    )


def _required_records() -> list[dict[str, Any]]:
    return [
        _record(artifact_type, index)
        for index, artifact_type in enumerate(
            REQUIRED_ARTIFACT_TYPES,
            start=1,
        )
    ]


def test_d2_source_record_contains_version_lock_fields() -> None:
    record = _record("MARKET_NARRATIVE_CONTEXT", 1)

    assert record["artifact_id"] == "artifact-01"
    assert record["artifact_version"] == "1.0.1"
    assert record["correlation_id"] == "corr-report-001"
    assert record["research_run_id"] == "research-run-001"
    assert record["locked_sha256"] == _digest(1)
    assert record["source_artifact_preserved"] is True
    assert record["original_conclusion_preserved"] is True


def test_d2_source_record_rejects_runtime_source_path() -> None:
    with pytest.raises(ValueError):
        build_source_record(
            artifact_id="runtime-source",
            artifact_type="MARKET_NARRATIVE_CONTEXT",
            artifact_version="1.0.0",
            correlation_id="corr-report-001",
            research_run_id="research-run-001",
            source_stage_id="SOURCE-D1",
            source_path="runtime/generated.json",
            locked_sha256=_digest(1),
            source_conclusion_state="PRESERVED",
            validation_state="VALIDATED",
            requirement_level="REQUIRED",
        )


def test_d2_source_record_rejects_invalid_digest() -> None:
    record = _record("CAUSAL_REASONING_CHAIN", 2)
    record["locked_sha256"] = "not-a-sha256"

    errors = validate_source_record(record)

    assert errors
    assert any("locked_sha256" in error for error in errors)

    with pytest.raises(SourceRecordViolation):
        build_version_lock(record)


def test_d2_manifest_is_deterministic_and_sorted() -> None:
    records = list(reversed(_required_records()))

    first = build_source_manifest(
        manifest_id="manifest-001",
        sources=records,
    )
    second = build_source_manifest(
        manifest_id="manifest-001",
        sources=records,
    )

    assert first == second
    assert first is not second

    sort_keys = [
        (source["artifact_type"], source["artifact_id"])
        for source in first["sources"]
    ]

    assert sort_keys == sorted(sort_keys)
    assert first["status"] == "VERSION_LOCKED"
    assert first["report_synthesis_started"] is False


def test_d2_manifest_requires_all_required_source_types() -> None:
    records = _required_records()
    records.pop()

    with pytest.raises(ManifestViolation) as exc_info:
        build_source_manifest(
            manifest_id="manifest-missing-source",
            sources=records,
        )

    assert "required artifact type is missing" in str(exc_info.value)


def test_d2_manifest_rejects_mixed_correlation_ids() -> None:
    records = _required_records()
    records[0] = _record(
        REQUIRED_ARTIFACT_TYPES[0],
        1,
        correlation_id="corr-other",
    )

    with pytest.raises(ManifestViolation) as exc_info:
        build_source_manifest(
            manifest_id="manifest-mixed-correlation",
            sources=records,
        )

    assert "one correlation_id" in str(exc_info.value)


def test_d2_manifest_rejects_mixed_research_runs() -> None:
    records = _required_records()
    records[0] = _record(
        REQUIRED_ARTIFACT_TYPES[0],
        1,
        research_run_id="research-run-other",
    )

    with pytest.raises(ManifestViolation) as exc_info:
        build_source_manifest(
            manifest_id="manifest-mixed-run",
            sources=records,
        )

    assert "one research_run_id" in str(exc_info.value)


def test_d2_manifest_rejects_duplicate_artifact_ids() -> None:
    manifest = build_source_manifest(
        manifest_id="manifest-duplicate",
        sources=_required_records(),
    )

    manifest["sources"][1]["artifact_id"] = (
        manifest["sources"][0]["artifact_id"]
    )

    errors = validate_source_manifest(manifest)

    assert any(
        "artifact_id values must be unique" in error
        for error in errors
    )


def test_d2_manifest_rejects_unknown_artifact_type() -> None:
    record = _record("MARKET_NARRATIVE_CONTEXT", 1)
    record["artifact_type"] = "UNREGISTERED_SOURCE_TYPE"

    errors = validate_source_record(record)

    assert any("artifact_type" in error for error in errors)


def test_d2_version_locks_match_registered_sources() -> None:
    manifest = build_source_manifest(
        manifest_id="manifest-locks",
        sources=_required_records(),
    )

    assert manifest["version_locks"] == [
        build_version_lock(source)
        for source in manifest["sources"]
    ]


def test_d2_manifest_rejects_silent_version_replacement() -> None:
    manifest = build_source_manifest(
        manifest_id="manifest-version-change",
        sources=_required_records(),
    )

    manifest["sources"][0]["artifact_version"] = "9.9.9"

    errors = validate_source_manifest(manifest)

    assert any(
        "version_locks do not match" in error
        for error in errors
    )


def test_d2_registered_manifest_is_valid_and_independent() -> None:
    manifest = build_source_manifest(
        manifest_id="manifest-valid",
        sources=_required_records(),
    )
    copied = deepcopy(manifest)

    assert validate_source_manifest(manifest) == ()
    assert require_valid_source_manifest(manifest) is manifest
    assert copied == manifest