import json

from report_archive_app import (
    FINAL_ARCHIVE_CLOSEOUT_STATUS,
    REPORT_ARCHIVE_FINAL_STAGE_ID,
    build_archive_integrity_summary,
    build_archive_item_index,
    build_archive_manifest,
    build_archive_source_candidate,
    build_final_report_archive_handoff,
    build_paper_archive_packet,
    build_report_archive_closeout_summary,
    validate_final_report_archive_handoff,
    write_final_report_archive_handoff,
)


def _build_paper_archive_packet(tmp_path):
    first = tmp_path / "DATA_APP_1_closeout_summary.md"
    second = tmp_path / "OPERATOR_REVIEW_APP_1_final_handoff.json"
    first.write_text("data closeout", encoding="utf-8")
    second.write_text("operator handoff", encoding="utf-8")

    candidates = [
        build_archive_source_candidate(first),
        build_archive_source_candidate(second),
    ]
    item_index = build_archive_item_index(
        index_id="ARCHIVE-D6-INDEX",
        candidates=candidates,
    )
    integrity_summary = build_archive_integrity_summary(
        summary_id="ARCHIVE-D6-INTEGRITY",
        item_index=item_index,
    )
    manifest = build_archive_manifest(
        manifest_id="ARCHIVE-D6-MANIFEST",
        integrity_summary=integrity_summary,
    )
    return build_paper_archive_packet(
        packet_id="PAPER-ARCHIVE-D6-PACKET",
        archive_manifest=manifest,
        integrity_summary=integrity_summary,
    )


def test_report_archive_d6_builds_final_handoff(tmp_path):
    packet = _build_paper_archive_packet(tmp_path)

    handoff = build_final_report_archive_handoff(
        handoff_id="FINAL-REPORT-ARCHIVE-D6-001",
        paper_archive_packet=packet,
    )

    assert handoff.handoff_id == "FINAL-REPORT-ARCHIVE-D6-001"
    assert handoff.stage_id == REPORT_ARCHIVE_FINAL_STAGE_ID
    assert handoff.source_packet_id == "PAPER-ARCHIVE-D6-PACKET"
    assert handoff.closeout_status == FINAL_ARCHIVE_CLOSEOUT_STATUS
    assert handoff.paper_only is True
    assert handoff.local_only is True
    assert handoff.read_only is True
    assert handoff.sidecar_only is True
    assert handoff.operator_review_required is True
    assert handoff.operator_review_bypass_allowed is False
    assert validate_final_report_archive_handoff(handoff) == []


def test_report_archive_d6_final_handoff_forbids_execution_source_mutation_and_deploy(tmp_path):
    packet = _build_paper_archive_packet(tmp_path)

    handoff = build_final_report_archive_handoff(
        handoff_id="FINAL-REPORT-ARCHIVE-D6-002",
        paper_archive_packet=packet,
    )

    assert handoff.source_content_mutation_allowed is False
    assert handoff.source_deletion_allowed is False
    assert handoff.source_overwrite_allowed is False
    assert handoff.archive_packet_is_trade_instruction is False
    assert handoff.real_execution_allowed is False
    assert handoff.trade_action_enabled is False
    assert handoff.buy_button_enabled is False
    assert handoff.sell_button_enabled is False
    assert handoff.order_button_enabled is False
    assert handoff.broker_connection_allowed is False
    assert handoff.exchange_connection_allowed is False
    assert handoff.credential_storage_allowed is False
    assert handoff.wallet_private_key_access_allowed is False
    assert handoff.real_account_access_allowed is False
    assert handoff.real_position_access_allowed is False
    assert handoff.core_mutation_allowed is False
    assert handoff.p48_core_expansion_allowed is False
    assert handoff.tag_created is False
    assert handoff.release_created is False
    assert handoff.deployed is False


def test_report_archive_d6_builds_closeout_summary(tmp_path):
    packet = _build_paper_archive_packet(tmp_path)
    handoff = build_final_report_archive_handoff(
        handoff_id="FINAL-REPORT-ARCHIVE-D6-003",
        paper_archive_packet=packet,
    )

    summary = build_report_archive_closeout_summary(handoff)

    assert summary["app_id"] == "REPORT-ARCHIVE-APP-1"
    assert summary["stage_id"] == "REPORT-ARCHIVE-D6"
    assert summary["closeout_status"] == FINAL_ARCHIVE_CLOSEOUT_STATUS
    assert summary["completed_stages"] == [
        "REPORT-ARCHIVE-D1",
        "REPORT-ARCHIVE-D2",
        "REPORT-ARCHIVE-D3",
        "REPORT-ARCHIVE-D4",
        "REPORT-ARCHIVE-D5",
        "REPORT-ARCHIVE-D6",
    ]
    assert summary["source_content_mutation_allowed"] is False
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
    assert summary["tag_created"] is False
    assert summary["release_created"] is False
    assert summary["deployed"] is False


def test_report_archive_d6_writes_final_handoff_json(tmp_path):
    packet = _build_paper_archive_packet(tmp_path)
    handoff = build_final_report_archive_handoff(
        handoff_id="FINAL-REPORT-ARCHIVE-D6-004",
        paper_archive_packet=packet,
    )

    output_path = tmp_path / "final_report_archive_handoff.json"
    written = write_final_report_archive_handoff(handoff, output_path)

    assert written == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["handoff_id"] == "FINAL-REPORT-ARCHIVE-D6-004"
    assert loaded["stage_id"] == "REPORT-ARCHIVE-D6"
    assert loaded["real_execution_allowed"] is False
    assert loaded["trade_action_enabled"] is False
    assert loaded["deployed"] is False
