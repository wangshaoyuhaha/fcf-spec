import hashlib

from report_archive_app import (
    INTEGRITY_STATUS_READY,
    INTEGRITY_STATUS_SOURCE_MISSING,
    build_archive_integrity_record,
    build_archive_integrity_summary,
    build_archive_item_index,
    build_archive_item_index_record,
    build_archive_source_candidate,
    summarize_archive_integrity_summary,
    validate_archive_integrity_record,
    validate_archive_integrity_summary,
)


def test_report_archive_d4_builds_checksum_record(tmp_path):
    source_file = tmp_path / "UI_APP_1_workflow_handoff.json"
    source_file.write_text("hello archive", encoding="utf-8")

    candidate = build_archive_source_candidate(source_file)
    index_record = build_archive_item_index_record(
        candidate,
        archive_item_id="ARCHIVE-D4-ITEM-0001",
    )

    integrity = build_archive_integrity_record(index_record)

    expected_checksum = hashlib.sha256(b"hello archive").hexdigest()

    assert integrity.archive_item_id == "ARCHIVE-D4-ITEM-0001"
    assert integrity.integrity_status == INTEGRITY_STATUS_READY
    assert integrity.checksum_sha256 == expected_checksum
    assert integrity.checksum_generated is True
    assert integrity.source_content_read_for_checksum is True
    assert integrity.paper_only is True
    assert integrity.local_only is True
    assert integrity.read_only is True
    assert integrity.sidecar_only is True
    assert integrity.source_content_mutation_allowed is False
    assert integrity.trade_action_enabled is False
    assert integrity.real_execution_allowed is False
    assert validate_archive_integrity_record(integrity) == []


def test_report_archive_d4_builds_integrity_summary(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    first = docs_dir / "DATA_APP_1_closeout_summary.md"
    second = docs_dir / "STOCK_APP_1_workflow_handoff.json"
    first.write_text("data", encoding="utf-8")
    second.write_text("stock", encoding="utf-8")

    candidates = [
        build_archive_source_candidate(first),
        build_archive_source_candidate(second),
    ]
    item_index = build_archive_item_index(
        index_id="ARCHIVE-D4-INDEX",
        candidates=candidates,
    )

    summary = build_archive_integrity_summary(
        summary_id="ARCHIVE-D4-INTEGRITY",
        item_index=item_index,
    )

    assert summary.summary_id == "ARCHIVE-D4-INTEGRITY"
    assert summary.source_index_id == "ARCHIVE-D4-INDEX"
    assert len(summary.records) == 2
    assert all(record.integrity_status == INTEGRITY_STATUS_READY for record in summary.records)
    assert all(record.checksum_generated is True for record in summary.records)
    assert summary.paper_only is True
    assert summary.local_only is True
    assert summary.read_only is True
    assert summary.sidecar_only is True
    assert summary.trade_action_enabled is False
    assert summary.real_execution_allowed is False
    assert validate_archive_integrity_summary(summary) == []


def test_report_archive_d4_summarizes_integrity_summary(tmp_path):
    source_file = tmp_path / "AI_CONTEXT_1_local_report_artifact.txt"
    source_file.write_text("ai", encoding="utf-8")

    candidate = build_archive_source_candidate(source_file)
    item_index = build_archive_item_index(
        index_id="ARCHIVE-D4-SUMMARY-INDEX",
        candidates=[candidate],
    )
    summary = build_archive_integrity_summary(
        summary_id="ARCHIVE-D4-SUMMARY",
        item_index=item_index,
    )

    compact = summarize_archive_integrity_summary(summary)

    assert compact["summary_id"] == "ARCHIVE-D4-SUMMARY"
    assert compact["source_index_id"] == "ARCHIVE-D4-SUMMARY-INDEX"
    assert compact["record_count"] == 1
    assert compact["status_counts"][INTEGRITY_STATUS_READY] == 1
    assert compact["all_ready"] is True
    assert compact["paper_only"] is True
    assert compact["local_only"] is True
    assert compact["read_only"] is True
    assert compact["trade_action_enabled"] is False
    assert compact["real_execution_allowed"] is False


def test_report_archive_d4_marks_missing_source_without_execution(tmp_path):
    missing_file = tmp_path / "OPERATOR_REVIEW_APP_1_final_handoff.json"

    candidate = build_archive_source_candidate(missing_file)
    index_record = build_archive_item_index_record(
        candidate,
        archive_item_id="ARCHIVE-D4-MISSING",
    )

    integrity = build_archive_integrity_record(index_record)

    assert integrity.integrity_status == INTEGRITY_STATUS_SOURCE_MISSING
    assert integrity.checksum_sha256 == ""
    assert integrity.checksum_generated is False
    assert integrity.source_content_read_for_checksum is False
    assert integrity.trade_action_enabled is False
    assert integrity.real_execution_allowed is False
    assert validate_archive_integrity_record(integrity) == []
