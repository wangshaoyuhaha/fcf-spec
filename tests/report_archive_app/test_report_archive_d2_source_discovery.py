from pathlib import Path

from report_archive_app import (
    build_archive_source_candidate,
    discover_archive_source_candidates,
    infer_source_app_id,
    infer_source_type,
    summarize_archive_source_candidates,
    validate_archive_source_candidate,
)


def test_report_archive_d2_infers_source_app_id_and_type():
    path = Path("docs/OPERATOR_REVIEW_APP_1_FINAL_HANDOFF.md")

    assert infer_source_app_id(path) == "OPERATOR-REVIEW-APP-1"
    assert infer_source_type(path) == "final_handoff"

    ui_path = Path("runtime/ui_app/local_report_artifact.json")
    assert infer_source_app_id(ui_path) == "UI-APP-1"
    assert infer_source_type(ui_path) == "local_report_artifact"


def test_report_archive_d2_builds_read_only_candidate(tmp_path):
    source_file = tmp_path / "ui_app_workflow_handoff.json"
    source_file.write_text("{}", encoding="utf-8")

    candidate = build_archive_source_candidate(source_file)

    assert candidate.source_app_id == "UI-APP-1"
    assert candidate.source_type == "workflow_handoff"
    assert candidate.source_exists is True
    assert candidate.file_extension == ".json"
    assert candidate.file_size_bytes >= 0
    assert candidate.paper_only is True
    assert candidate.local_only is True
    assert candidate.read_only is True
    assert candidate.source_content_mutation_allowed is False
    assert candidate.source_deletion_allowed is False
    assert candidate.source_overwrite_allowed is False
    assert candidate.archive_packet_is_trade_instruction is False
    assert candidate.trade_action_enabled is False
    assert candidate.real_execution_allowed is False
    assert validate_archive_source_candidate(candidate) == []


def test_report_archive_d2_discovers_local_candidates_without_reading_contents(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "DATA_APP_1_closeout_summary.md").write_text("data", encoding="utf-8")
    (docs_dir / "STOCK_APP_1_workflow_handoff.json").write_text("stock", encoding="utf-8")
    (docs_dir / "AI_CONTEXT_1_local_report_artifact.txt").write_text("ai", encoding="utf-8")
    (docs_dir / "random_notes.md").write_text("ignore", encoding="utf-8")
    (docs_dir / "operator_review_script.py").write_text("ignore", encoding="utf-8")

    candidates = discover_archive_source_candidates(tmp_path)

    assert len(candidates) == 3
    assert {item.source_app_id for item in candidates} == {
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
    }
    assert all(item.read_only is True for item in candidates)
    assert all(item.source_content_mutation_allowed is False for item in candidates)


def test_report_archive_d2_summarizes_candidates_by_app_and_type(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "UI_APP_1_local_report_artifact.json").write_text("{}", encoding="utf-8")
    (docs_dir / "OPERATOR_REVIEW_APP_1_final_handoff.json").write_text("{}", encoding="utf-8")

    candidates = discover_archive_source_candidates(tmp_path)
    summary = summarize_archive_source_candidates(candidates)

    assert summary["candidate_count"] == 2
    assert summary["by_source_app_id"]["UI-APP-1"] == 1
    assert summary["by_source_app_id"]["OPERATOR-REVIEW-APP-1"] == 1
    assert summary["by_source_type"]["local_report_artifact"] == 1
    assert summary["by_source_type"]["final_handoff"] == 1
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["trade_action_enabled"] is False
    assert summary["real_execution_allowed"] is False
