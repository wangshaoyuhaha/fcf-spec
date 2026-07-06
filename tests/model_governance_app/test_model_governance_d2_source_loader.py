"""Tests for MODEL-GOVERNANCE-D2 read-only source loader."""

from __future__ import annotations

from pathlib import Path

from apps.model_governance_app.source_loader import (
    GovernanceSourceSpec,
    inspect_governance_source,
    load_governance_source_manifest,
    summarize_governance_source_manifest,
)


def test_model_governance_d2_inspects_existing_source_without_mutation(tmp_path: Path) -> None:
    source_file = tmp_path / "source.md"
    source_file.write_text("score_breakdown reason_codes risk_flags", encoding="utf-8")

    spec = GovernanceSourceSpec(
        source_id="sample_governance_source",
        layer_id="STOCK-APP-1",
        relative_path="source.md",
        payload_type="markdown",
        governance_category="scoring_policy_and_reason_codes",
        required=True,
    )

    before = source_file.read_text(encoding="utf-8")
    inspected = inspect_governance_source(tmp_path, spec)
    after = source_file.read_text(encoding="utf-8")

    assert before == after
    assert inspected["source_id"] == "sample_governance_source"
    assert inspected["exists"] is True
    assert inspected["status"] == "AVAILABLE"
    assert inspected["read_only"] is True
    assert inspected["score_mutation_allowed"] is False
    assert inspected["reason_code_mutation_allowed"] is False
    assert inspected["risk_flag_deletion_allowed"] is False
    assert inspected["source_content_mutation_allowed"] is False


def test_model_governance_d2_marks_missing_required_source(tmp_path: Path) -> None:
    spec = GovernanceSourceSpec(
        source_id="signal_validation_final_state",
        layer_id="SIGNAL-VALIDATION-APP-1",
        relative_path="missing.md",
        payload_type="markdown",
        governance_category="signal_validation_policy",
        required=True,
    )

    inspected = inspect_governance_source(tmp_path, spec)

    assert inspected["exists"] is False
    assert inspected["status"] == "MISSING_REQUIRED"
    assert inspected["size_bytes"] == 0
    assert inspected["preview"] == ""


def test_model_governance_d2_marks_missing_optional_source(tmp_path: Path) -> None:
    spec = GovernanceSourceSpec(
        source_id="optional_source",
        layer_id="AI-CONTEXT-1",
        relative_path="missing_optional.md",
        payload_type="markdown",
        governance_category="explanation_policy",
        required=False,
    )

    inspected = inspect_governance_source(tmp_path, spec)

    assert inspected["exists"] is False
    assert inspected["status"] == "MISSING_OPTIONAL"


def test_model_governance_d2_builds_manifest_summary(tmp_path: Path) -> None:
    (tmp_path / "required.md").write_text("required governance packet", encoding="utf-8")
    (tmp_path / "optional.md").write_text("optional governance packet", encoding="utf-8")

    specs = [
        GovernanceSourceSpec(
            "required_source",
            "SIGNAL-VALIDATION-APP-1",
            "required.md",
            "markdown",
            "signal_validation_policy",
            True,
        ),
        GovernanceSourceSpec(
            "optional_source",
            "STOCK-APP-1",
            "optional.md",
            "markdown",
            "scoring_policy_and_reason_codes",
            False,
        ),
    ]

    manifest = load_governance_source_manifest(tmp_path, specs=specs)
    summary = summarize_governance_source_manifest(manifest)

    assert manifest["app_id"] == "MODEL-GOVERNANCE-APP-1"
    assert manifest["stage_id"] == "MODEL-GOVERNANCE-D2"
    assert manifest["source_count"] == 2
    assert manifest["available_count"] == 2
    assert manifest["missing_required_count"] == 0
    assert summary["loader_status"] == "ALL_CONFIGURED_SOURCES_AVAILABLE"
    assert summary["score_mutation_allowed"] is False
    assert summary["risk_flag_deletion_allowed"] is False
    assert summary["real_execution_allowed"] is False


def test_model_governance_d2_blocks_when_required_source_missing(tmp_path: Path) -> None:
    specs = [
        GovernanceSourceSpec(
            "required_source",
            "SIGNAL-VALIDATION-APP-1",
            "missing.md",
            "markdown",
            "signal_validation_policy",
            True,
        ),
        GovernanceSourceSpec(
            "optional_source",
            "STOCK-APP-1",
            "missing_optional.md",
            "markdown",
            "scoring_policy_and_reason_codes",
            False,
        ),
    ]

    manifest = load_governance_source_manifest(tmp_path, specs=specs)
    summary = summarize_governance_source_manifest(manifest)

    assert manifest["missing_required_sources"] == ["required_source"]
    assert manifest["missing_optional_sources"] == ["optional_source"]
    assert summary["loader_status"] == "BLOCKED_MISSING_REQUIRED_SOURCE"
    assert summary["operator_review_required"] is True


def test_model_governance_d2_default_manifest_is_safe() -> None:
    manifest = load_governance_source_manifest(".")

    assert manifest["read_only"] is True
    assert manifest["paper_only"] is True
    assert manifest["sidecar_only"] is True
    assert manifest["score_mutation_allowed"] is False
    assert manifest["reason_code_mutation_allowed"] is False
    assert manifest["risk_flag_deletion_allowed"] is False
    assert manifest["source_content_mutation_allowed"] is False
    assert manifest["source_deletion_allowed"] is False
    assert manifest["source_overwrite_allowed"] is False
    assert manifest["real_execution_allowed"] is False
    assert manifest["trade_action_enabled"] is False
