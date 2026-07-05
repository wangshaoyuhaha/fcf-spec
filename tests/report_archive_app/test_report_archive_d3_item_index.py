from report_archive_app import (
    ARCHIVE_ITEM_INDEX_STAGE_ID,
    ARCHIVE_ITEM_INDEX_STATUS,
    build_archive_item_index,
    build_archive_item_index_record,
    build_archive_source_candidate,
    discover_archive_source_candidates,
    summarize_archive_item_index,
    validate_archive_item_index,
    validate_archive_item_index_record,
)


def test_report_archive_d3_builds_index_record_from_candidate(tmp_path):
    source_file = tmp_path / "UI_APP_1_workflow_handoff.json"
    source_file.write_text("{}", encoding="utf-8")

    candidate = build_archive_source_candidate(source_file)
    record = build_archive_item_index_record(
        candidate,
        archive_item_id="ARCHIVE-ITEM-0001",
    )

    assert record.archive_item_id == "ARCHIVE-ITEM-0001"
    assert record.source_app_id == "UI-APP-1"
    assert record.source_type == "workflow_handoff"
    assert record.source_exists is True
    assert record.index_status == ARCHIVE_ITEM_INDEX_STATUS
    assert record.paper_only is True
    assert record.local_only is True
    assert record.read_only is True
    assert record.sidecar_only is True
    assert record.source_content_read_for_index is False
    assert record.source_content_mutation_allowed is False
    assert record.checksum_generated is False
    assert record.trade_action_enabled is False
    assert record.real_execution_allowed is False
    assert validate_archive_item_index_record(record) == []


def test_report_archive_d3_builds_archive_item_index(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "DATA_APP_1_closeout_summary.md").write_text("data", encoding="utf-8")
    (docs_dir / "STOCK_APP_1_workflow_handoff.json").write_text("stock", encoding="utf-8")

    candidates = discover_archive_source_candidates(tmp_path)
    index = build_archive_item_index(
        index_id="ARCHIVE-INDEX-D3",
        candidates=candidates,
    )

    assert index.index_id == "ARCHIVE-INDEX-D3"
    assert index.stage_id == ARCHIVE_ITEM_INDEX_STAGE_ID
    assert len(index.records) == 2
    assert index.records[0].archive_item_id == "ARCHIVE-INDEX-D3-ITEM-0001"
    assert index.records[1].archive_item_id == "ARCHIVE-INDEX-D3-ITEM-0002"
    assert index.paper_only is True
    assert index.local_only is True
    assert index.read_only is True
    assert index.sidecar_only is True
    assert index.source_content_read_for_index is False
    assert index.trade_action_enabled is False
    assert index.real_execution_allowed is False
    assert validate_archive_item_index(index) == []


def test_report_archive_d3_summarizes_archive_item_index(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "AI_CONTEXT_1_local_report_artifact.txt").write_text("ai", encoding="utf-8")
    (docs_dir / "OPERATOR_REVIEW_APP_1_final_handoff.md").write_text("op", encoding="utf-8")

    candidates = discover_archive_source_candidates(tmp_path)
    index = build_archive_item_index(
        index_id="ARCHIVE-INDEX-D3-SUMMARY",
        candidates=candidates,
    )

    summary = summarize_archive_item_index(index)

    assert summary["index_id"] == "ARCHIVE-INDEX-D3-SUMMARY"
    assert summary["stage_id"] == "REPORT-ARCHIVE-D3"
    assert summary["record_count"] == 2
    assert summary["by_source_app_id"]["AI-CONTEXT-1"] == 1
    assert summary["by_source_app_id"]["OPERATOR-REVIEW-APP-1"] == 1
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["sidecar_only"] is True
    assert summary["source_content_read_for_index"] is False
    assert summary["trade_action_enabled"] is False
    assert summary["real_execution_allowed"] is False


def test_report_archive_d3_rejects_index_record_that_reads_or_mutates_source(tmp_path):
    source_file = tmp_path / "DATA_APP_1_local_report_artifact.json"
    source_file.write_text("{}", encoding="utf-8")

    candidate = build_archive_source_candidate(source_file)
    record = build_archive_item_index_record(
        candidate,
        archive_item_id="ARCHIVE-ITEM-UNSAFE",
    )

    unsafe_record = record.__class__(
        archive_item_id=record.archive_item_id,
        record_type=record.record_type,
        source_app_id=record.source_app_id,
        source_type=record.source_type,
        source_path=record.source_path,
        source_exists=record.source_exists,
        file_extension=record.file_extension,
        file_size_bytes=record.file_size_bytes,
        source_content_read_for_index=True,
        source_content_mutation_allowed=True,
    )

    errors = validate_archive_item_index_record(unsafe_record)
    assert "source_content_read_for_index must be false" in errors
    assert "source_content_mutation_allowed must be false" in errors
