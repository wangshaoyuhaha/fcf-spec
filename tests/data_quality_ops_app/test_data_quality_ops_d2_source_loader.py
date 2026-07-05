import json

from data_quality_ops_app import (
    load_data_quality_ops_source,
    summarize_data_quality_ops_sources,
    validate_data_quality_ops_source,
)


def test_data_quality_ops_d2_loads_json_metadata_source(tmp_path):
    source_file = tmp_path / "health_check_report.json"
    source_file.write_text(
        json.dumps(
            {
                "data_quality_state": "PASS_LIMITED",
                "issue_count": 2,
                "operator_review_required": True,
            }
        ),
        encoding="utf-8",
    )

    source = load_data_quality_ops_source(
        source_file,
        source_app_id="DATA-APP-1",
        source_type="health_check_report",
    )

    assert source.source_exists is True
    assert source.file_extension == ".json"
    assert source.payload["data_quality_state"] == "PASS_LIMITED"
    assert source.payload["issue_count"] == 2
    assert source.paper_only is True
    assert source.local_only is True
    assert source.read_only is True
    assert source.sidecar_only is True
    assert source.source_content_mutation_allowed is False
    assert source.trade_action_enabled is False
    assert source.real_execution_allowed is False
    assert validate_data_quality_ops_source(source) == []


def test_data_quality_ops_d2_loads_text_metadata_preview(tmp_path):
    source_file = tmp_path / "archive_manifest.md"
    source_file.write_text("archive manifest notes", encoding="utf-8")

    source = load_data_quality_ops_source(
        source_file,
        source_app_id="REPORT-ARCHIVE-APP-1",
        source_type="archive_manifest",
    )

    assert source.source_exists is True
    assert source.file_extension == ".md"
    assert source.payload["raw_text_preview"] == "archive manifest notes"
    assert source.payload["raw_text_length"] == len("archive manifest notes")
    assert source.source_content_mutation_allowed is False
    assert source.source_deletion_allowed is False
    assert source.source_overwrite_allowed is False
    assert validate_data_quality_ops_source(source) == []


def test_data_quality_ops_d2_rejects_disallowed_source_type_without_execution(tmp_path):
    source_file = tmp_path / "bad.json"
    source_file.write_text("{}", encoding="utf-8")

    source = load_data_quality_ops_source(
        source_file,
        source_app_id="DATA-APP-1",
        source_type="trade_instruction",
    )

    assert source.source_exists is True
    assert any("source_type is not allowed" in item for item in source.load_errors)
    assert source.trade_action_enabled is False
    assert source.real_execution_allowed is False


def test_data_quality_ops_d2_summarizes_loaded_sources(tmp_path):
    first = tmp_path / "health_check_report.json"
    second = tmp_path / "paper_archive_packet.json"
    first.write_text("{}", encoding="utf-8")
    second.write_text("{}", encoding="utf-8")

    sources = [
        load_data_quality_ops_source(
            first,
            source_app_id="DATA-APP-1",
            source_type="health_check_report",
        ),
        load_data_quality_ops_source(
            second,
            source_app_id="REPORT-ARCHIVE-APP-1",
            source_type="paper_archive_packet",
        ),
    ]

    summary = summarize_data_quality_ops_sources(sources)

    assert summary["source_count"] == 2
    assert summary["load_error_count"] == 0
    assert summary["by_source_app_id"]["DATA-APP-1"] == 1
    assert summary["by_source_app_id"]["REPORT-ARCHIVE-APP-1"] == 1
    assert summary["by_source_type"]["health_check_report"] == 1
    assert summary["by_source_type"]["paper_archive_packet"] == 1
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["trade_action_enabled"] is False
    assert summary["real_execution_allowed"] is False
