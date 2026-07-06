"""Tests for SIGNAL-VALIDATION-D2 read-only source loader."""

from __future__ import annotations

from pathlib import Path

from apps.signal_validation_app.source_loader import (
    SignalSourceSpec,
    inspect_signal_source,
    load_signal_source_manifest,
    summarize_signal_source_manifest,
)


def test_signal_validation_d2_inspects_existing_source_without_mutation(tmp_path: Path) -> None:
    source_file = tmp_path / "source.md"
    source_file.write_text("paper only source packet", encoding="utf-8")

    spec = SignalSourceSpec(
        source_id="sample_source",
        layer_id="SAMPLE-LAYER",
        relative_path="source.md",
        payload_type="markdown",
        required=True,
    )

    before = source_file.read_text(encoding="utf-8")
    inspected = inspect_signal_source(tmp_path, spec)
    after = source_file.read_text(encoding="utf-8")

    assert before == after
    assert inspected["source_id"] == "sample_source"
    assert inspected["exists"] is True
    assert inspected["status"] == "AVAILABLE"
    assert inspected["read_only"] is True
    assert inspected["source_content_mutation_allowed"] is False
    assert inspected["source_deletion_allowed"] is False
    assert inspected["source_overwrite_allowed"] is False


def test_signal_validation_d2_marks_missing_required_source(tmp_path: Path) -> None:
    spec = SignalSourceSpec(
        source_id="required_missing",
        layer_id="BACKTEST-REVIEW-APP-1",
        relative_path="missing.md",
        payload_type="markdown",
        required=True,
    )

    inspected = inspect_signal_source(tmp_path, spec)

    assert inspected["exists"] is False
    assert inspected["status"] == "MISSING_REQUIRED"
    assert inspected["size_bytes"] == 0
    assert inspected["preview"] == ""


def test_signal_validation_d2_marks_missing_optional_source(tmp_path: Path) -> None:
    spec = SignalSourceSpec(
        source_id="optional_missing",
        layer_id="STOCK-APP-1",
        relative_path="missing_optional.md",
        payload_type="markdown",
        required=False,
    )

    inspected = inspect_signal_source(tmp_path, spec)

    assert inspected["exists"] is False
    assert inspected["status"] == "MISSING_OPTIONAL"


def test_signal_validation_d2_builds_manifest_summary(tmp_path: Path) -> None:
    (tmp_path / "required.md").write_text("required packet", encoding="utf-8")
    (tmp_path / "optional.md").write_text("optional packet", encoding="utf-8")

    specs = [
        SignalSourceSpec("required_source", "BACKTEST-REVIEW-APP-1", "required.md", "markdown", True),
        SignalSourceSpec("optional_source", "MARKET-SCENARIO-APP-1", "optional.md", "markdown", False),
    ]

    manifest = load_signal_source_manifest(tmp_path, specs=specs)
    summary = summarize_signal_source_manifest(manifest)

    assert manifest["app_id"] == "SIGNAL-VALIDATION-APP-1"
    assert manifest["stage_id"] == "SIGNAL-VALIDATION-D2"
    assert manifest["source_count"] == 2
    assert manifest["available_count"] == 2
    assert manifest["missing_required_count"] == 0
    assert summary["loader_status"] == "ALL_CONFIGURED_SOURCES_AVAILABLE"
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False


def test_signal_validation_d2_blocks_when_required_source_missing(tmp_path: Path) -> None:
    specs = [
        SignalSourceSpec("required_source", "BACKTEST-REVIEW-APP-1", "missing.md", "markdown", True),
        SignalSourceSpec("optional_source", "MARKET-SCENARIO-APP-1", "missing_optional.md", "markdown", False),
    ]

    manifest = load_signal_source_manifest(tmp_path, specs=specs)
    summary = summarize_signal_source_manifest(manifest)

    assert manifest["missing_required_sources"] == ["required_source"]
    assert manifest["missing_optional_sources"] == ["optional_source"]
    assert summary["loader_status"] == "BLOCKED_MISSING_REQUIRED_SOURCE"
    assert summary["operator_review_required"] is True


def test_signal_validation_d2_default_manifest_is_safe() -> None:
    manifest = load_signal_source_manifest(".")

    assert manifest["read_only"] is True
    assert manifest["paper_only"] is True
    assert manifest["sidecar_only"] is True
    assert manifest["source_content_mutation_allowed"] is False
    assert manifest["source_deletion_allowed"] is False
    assert manifest["source_overwrite_allowed"] is False
    assert manifest["real_execution_allowed"] is False
    assert manifest["trade_action_enabled"] is False
