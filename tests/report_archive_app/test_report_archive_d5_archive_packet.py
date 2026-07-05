import json

from report_archive_app import (
    ARCHIVE_MANIFEST_STAGE_ID,
    INTEGRITY_STATUS_READY,
    build_archive_integrity_summary,
    build_archive_item_index,
    build_archive_manifest,
    build_archive_source_candidate,
    build_paper_archive_packet,
    validate_archive_manifest,
    validate_paper_archive_packet,
    write_paper_archive_packet,
)


def _build_integrity_summary(tmp_path):
    first = tmp_path / "UI_APP_1_local_report_artifact.json"
    second = tmp_path / "OPERATOR_REVIEW_APP_1_final_handoff.md"
    first.write_text("ui", encoding="utf-8")
    second.write_text("operator", encoding="utf-8")

    candidates = [
        build_archive_source_candidate(first),
        build_archive_source_candidate(second),
    ]
    item_index = build_archive_item_index(
        index_id="ARCHIVE-D5-INDEX",
        candidates=candidates,
    )
    return build_archive_integrity_summary(
        summary_id="ARCHIVE-D5-INTEGRITY",
        item_index=item_index,
    )


def test_report_archive_d5_builds_archive_manifest(tmp_path):
    integrity_summary = _build_integrity_summary(tmp_path)

    manifest = build_archive_manifest(
        manifest_id="ARCHIVE-D5-MANIFEST",
        integrity_summary=integrity_summary,
    )

    assert manifest.manifest_id == "ARCHIVE-D5-MANIFEST"
    assert manifest.stage_id == ARCHIVE_MANIFEST_STAGE_ID
    assert manifest.source_integrity_summary_id == "ARCHIVE-D5-INTEGRITY"
    assert manifest.source_index_id == "ARCHIVE-D5-INDEX"
    assert manifest.archive_item_count == 2
    assert manifest.checksum_ready_count == 2
    assert manifest.checksum_missing_count == 0
    assert manifest.checksum_unreadable_count == 0
    assert manifest.integrity_summary["status_counts"][INTEGRITY_STATUS_READY] == 2
    assert manifest.paper_only is True
    assert manifest.local_only is True
    assert manifest.read_only is True
    assert manifest.sidecar_only is True
    assert manifest.trade_action_enabled is False
    assert manifest.real_execution_allowed is False
    assert validate_archive_manifest(manifest) == []


def test_report_archive_d5_builds_paper_archive_packet(tmp_path):
    integrity_summary = _build_integrity_summary(tmp_path)
    manifest = build_archive_manifest(
        manifest_id="ARCHIVE-D5-MANIFEST-2",
        integrity_summary=integrity_summary,
    )

    packet = build_paper_archive_packet(
        packet_id="PAPER-ARCHIVE-D5-PACKET",
        archive_manifest=manifest,
        integrity_summary=integrity_summary,
    )

    assert packet.packet_id == "PAPER-ARCHIVE-D5-PACKET"
    assert packet.stage_id == "REPORT-ARCHIVE-D5"
    assert packet.archive_manifest.manifest_id == "ARCHIVE-D5-MANIFEST-2"
    assert packet.paper_only is True
    assert packet.local_only is True
    assert packet.read_only is True
    assert packet.sidecar_only is True
    assert packet.archive_packet_is_trade_instruction is False
    assert packet.trade_action_enabled is False
    assert packet.real_execution_allowed is False
    assert packet.tag_created is False
    assert packet.release_created is False
    assert packet.deployed is False
    assert validate_paper_archive_packet(packet) == []


def test_report_archive_d5_writes_paper_archive_packet_json(tmp_path):
    integrity_summary = _build_integrity_summary(tmp_path)
    manifest = build_archive_manifest(
        manifest_id="ARCHIVE-D5-MANIFEST-3",
        integrity_summary=integrity_summary,
    )
    packet = build_paper_archive_packet(
        packet_id="PAPER-ARCHIVE-D5-PACKET-3",
        archive_manifest=manifest,
        integrity_summary=integrity_summary,
    )

    output_path = tmp_path / "paper_archive_packet.json"
    written = write_paper_archive_packet(packet, output_path)

    assert written == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["packet_id"] == "PAPER-ARCHIVE-D5-PACKET-3"
    assert loaded["archive_manifest"]["archive_item_count"] == 2
    assert loaded["trade_action_enabled"] is False
    assert loaded["real_execution_allowed"] is False
    assert loaded["deployed"] is False


def test_report_archive_d5_rejects_manifest_that_enables_trade(tmp_path):
    integrity_summary = _build_integrity_summary(tmp_path)
    manifest = build_archive_manifest(
        manifest_id="ARCHIVE-D5-MANIFEST-4",
        integrity_summary=integrity_summary,
    )

    unsafe_manifest = manifest.__class__(
        manifest_id=manifest.manifest_id,
        manifest_type=manifest.manifest_type,
        stage_id=manifest.stage_id,
        source_integrity_summary_id=manifest.source_integrity_summary_id,
        source_index_id=manifest.source_index_id,
        archive_item_count=manifest.archive_item_count,
        checksum_ready_count=manifest.checksum_ready_count,
        checksum_missing_count=manifest.checksum_missing_count,
        checksum_unreadable_count=manifest.checksum_unreadable_count,
        integrity_summary=manifest.integrity_summary,
        trade_action_enabled=True,
    )

    assert "trade_action_enabled must be false" in validate_archive_manifest(unsafe_manifest)
