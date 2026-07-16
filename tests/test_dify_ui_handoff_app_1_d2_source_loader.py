from pathlib import Path

from apps.dify_ui_handoff_app_1.source_loader import (
    STAGE_ID,
    build_dify_ui_source_manifest,
    inspect_dify_ui_source,
    summarize_dify_ui_source_manifest,
    validate_dify_ui_source_manifest,
)


def test_dify_ui_handoff_d2_manifest_is_valid():
    manifest = build_dify_ui_source_manifest()
    validation = validate_dify_ui_source_manifest(manifest)

    assert manifest["stage_id"] == STAGE_ID
    assert validation["valid"] is True
    assert validation["issues"] == []
    assert manifest["missing_source_count"] == 0
    assert manifest["source_count"] == (
        manifest["existing_source_count"]
        + manifest["unavailable_optional_source_count"]
    )


def test_dify_ui_handoff_d2_sources_are_read_only():
    manifest = build_dify_ui_source_manifest()

    assert manifest["paper_only"] is True
    assert manifest["local_only"] is True
    assert manifest["read_only"] is True
    assert manifest["sidecar_only"] is True
    assert manifest["operator_review_required"] is True

    assert manifest["source_content_mutation_allowed"] is False
    assert manifest["source_deletion_allowed"] is False
    assert manifest["source_overwrite_allowed"] is False
    assert manifest["dify_api_write_allowed"] is False
    assert manifest["automated_dify_app_creation_allowed"] is False

    for source in manifest["sources"]:
        if source["required"]:
            assert source["exists"] is True
        assert source["read_only"] is True
        assert source["source_content_mutation_allowed"] is False
        assert source["source_deletion_allowed"] is False
        assert source["source_overwrite_allowed"] is False


def test_dify_ui_handoff_d2_includes_operator_console_entry():
    manifest = build_dify_ui_source_manifest()
    paths = {source["relative_path"] for source in manifest["sources"]}

    assert "runtime/operator_console/index.html" in paths
    assert "artifacts/operator_console_static_export" in paths
    assert "artifacts/operator_workflow_bundle" in paths
    assert "artifacts/paper_readable_report" in paths
    assert "artifacts/paper_governance_report" in paths


def test_dify_ui_handoff_d2_file_inspection_has_checksum():
    source = {
        "source_id": "operator_console_index",
        "source_kind": "local_static_ui",
        "relative_path": "runtime/operator_console/index.html",
    }
    inspected = inspect_dify_ui_source(root_path=".", source=source)

    assert inspected["exists"] is True
    assert inspected["is_file"] is True
    assert inspected["sha256"]
    assert inspected["size_bytes"] > 0


def test_dify_ui_handoff_d2_directory_inspection_has_child_files(tmp_path):
    bundle = tmp_path / "artifacts" / "operator_workflow_bundle"
    bundle.mkdir(parents=True)
    (bundle / "fixture.json").write_text("{}", encoding="ascii")
    source = {
        "source_id": "operator_workflow_bundle",
        "source_kind": "local_artifact_bundle",
        "relative_path": "artifacts/operator_workflow_bundle",
        "required": False,
    }
    inspected = inspect_dify_ui_source(root_path=str(tmp_path), source=source)

    assert inspected["exists"] is True
    assert inspected["is_dir"] is True
    assert inspected["child_file_count"] > 0
    assert inspected["child_total_bytes"] > 0
    assert inspected["sample_files"]


def test_dify_ui_handoff_d2_summary_is_safe():
    summary = summarize_dify_ui_source_manifest()

    assert summary["valid"] is True
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["missing_source_count"] == 0
    assert summary["dify_api_write_allowed"] is False
    assert summary["automated_dify_app_creation_allowed"] is False
