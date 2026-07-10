"""Tests for the dashboard contradiction scanner source loader."""

from copy import deepcopy

import pytest

from fcf.sidecars.dashboard_contradiction_scanner import (
    build_source_manifest,
    load_source_record,
)


def _source(
    artifact_id: str = "artifact-001",
    artifact_type: str = "DASHBOARD_STATUS_PACKET",
) -> dict[str, object]:
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "correlation_id": "corr-001",
        "research_run_id": "run-001",
        "validation_baseline_id": "baseline-001",
        "source_artifact_ids": ["source-001"],
        "risk_flags": ["HIGH_VOLATILITY"],
        "reason_codes": ["PRICE_VOLUME_DIVERGENCE"],
        "validation_state": "PASS",
        "review_state": "REVIEW_REQUIRED",
        "lifecycle_state": "ACTIVE",
        "archive_state": "PENDING",
        "summary": "Paper-only dashboard summary.",
    }


def test_load_source_record_preserves_traceability() -> None:
    loaded = load_source_record(_source())

    assert loaded["artifact_id"] == "artifact-001"
    assert loaded["correlation_id"] == "corr-001"
    assert loaded["research_run_id"] == "run-001"
    assert loaded["validation_baseline_id"] == "baseline-001"
    assert loaded["risk_flags"] == ["HIGH_VOLATILITY"]
    assert loaded["read_only"] is True
    assert loaded["operator_review_required"] is True
    assert len(loaded["source_record_hash"]) == 64


def test_loader_does_not_mutate_source() -> None:
    source = _source()
    before = deepcopy(source)

    load_source_record(source)

    assert source == before


def test_unsupported_source_type_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported_artifact_type",
    ):
        load_source_record(_source(artifact_type="TRADE_ORDER"))


def test_missing_trace_field_is_rejected() -> None:
    source = _source()
    source.pop("correlation_id")

    with pytest.raises(
        ValueError,
        match="missing_or_invalid_field:correlation_id",
    ):
        load_source_record(source)


def test_manifest_is_deterministic_and_sorted() -> None:
    manifest = build_source_manifest(
        [
            _source("artifact-002"),
            _source("artifact-001"),
        ]
    )

    assert manifest["source_count"] == 2
    assert manifest["artifact_ids"] == [
        "artifact-001",
        "artifact-002",
    ]
    assert len(manifest["manifest_hash"]) == 64
    assert manifest["read_only"] is True


def test_duplicate_artifact_id_is_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate_artifact_id"):
        build_source_manifest(
            [
                _source("artifact-001"),
                _source("artifact-001"),
            ]
        )


def test_risk_flags_must_be_a_list() -> None:
    source = _source()
    source["risk_flags"] = "HIGH_VOLATILITY"

    with pytest.raises(
        ValueError,
        match="invalid_list_field:risk_flags",
    ):
        load_source_record(source)
