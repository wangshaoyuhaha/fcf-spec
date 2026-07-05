import json

from data_quality_ops_app import (
    REPAIR_PRIORITY_HIGH,
    REPAIR_PRIORITY_MEDIUM,
    build_data_quality_issue_list,
    build_data_quality_ops_check,
    build_data_quality_ops_checks,
    build_data_quality_ops_packet,
    build_data_repair_queue,
    build_data_repair_queue_item,
    load_data_quality_ops_source,
    validate_data_quality_ops_packet,
    validate_data_repair_queue,
    validate_data_repair_queue_item,
    write_data_quality_ops_packet,
)


def _build_issue_list(tmp_path):
    first = tmp_path / "limited.json"
    second = tmp_path / "fail.json"
    first.write_text(json.dumps({"data_quality_state": "PASS_LIMITED"}), encoding="utf-8")
    second.write_text(json.dumps({"data_quality_state": "FAIL_QUARANTINE"}), encoding="utf-8")

    sources = [
        load_data_quality_ops_source(first, source_app_id="DATA-APP-1", source_type="health_check_report"),
        load_data_quality_ops_source(second, source_app_id="DATA-APP-1", source_type="health_check_report"),
    ]
    checks = build_data_quality_ops_checks(sources, check_set_id="DQ-D5")
    return build_data_quality_issue_list(issue_list_id="DQ-D5-ISSUES", checks=checks)


def test_data_quality_ops_d5_builds_repair_queue_item(tmp_path):
    issue_list = _build_issue_list(tmp_path)
    issue = issue_list.issues[0]

    item = build_data_repair_queue_item(issue, repair_item_id="REPAIR-001")

    assert item.repair_item_id == "REPAIR-001"
    assert item.source_issue_id == issue.issue_id
    assert item.repair_priority == REPAIR_PRIORITY_MEDIUM
    assert item.paper_only is True
    assert item.local_only is True
    assert item.read_only is True
    assert item.sidecar_only is True
    assert item.repair_queue_is_execution_instruction is False
    assert item.suggested_action_is_execution_instruction is False
    assert item.source_content_mutation_allowed is False
    assert item.trade_action_enabled is False
    assert item.real_execution_allowed is False
    assert validate_data_repair_queue_item(item) == []


def test_data_quality_ops_d5_builds_high_priority_item_for_error(tmp_path):
    issue_list = _build_issue_list(tmp_path)
    error_issue = issue_list.issues[1]

    item = build_data_repair_queue_item(error_issue, repair_item_id="REPAIR-ERROR")

    assert item.repair_priority == REPAIR_PRIORITY_HIGH
    assert item.source_deletion_allowed is False
    assert item.source_overwrite_allowed is False
    assert validate_data_repair_queue_item(item) == []


def test_data_quality_ops_d5_builds_repair_queue_and_packet(tmp_path):
    issue_list = _build_issue_list(tmp_path)

    queue = build_data_repair_queue(
        queue_id="DQ-D5-REPAIR-QUEUE",
        issue_list=issue_list,
    )
    packet = build_data_quality_ops_packet(
        packet_id="DQ-D5-PACKET",
        issue_list=issue_list,
        repair_queue=queue,
    )

    assert len(queue.repair_items) == 2
    assert queue.repair_items[0].repair_item_id == "DQ-D5-REPAIR-QUEUE-REPAIR-0001"
    assert queue.repair_items[1].repair_item_id == "DQ-D5-REPAIR-QUEUE-REPAIR-0002"
    assert queue.repair_queue_is_execution_instruction is False
    assert queue.source_content_mutation_allowed is False
    assert queue.trade_action_enabled is False
    assert queue.real_execution_allowed is False
    assert packet.packet_id == "DQ-D5-PACKET"
    assert packet.issue_summary["issue_count"] == 2
    assert packet.tag_created is False
    assert packet.release_created is False
    assert packet.deployed is False
    assert validate_data_repair_queue(queue) == []
    assert validate_data_quality_ops_packet(packet) == []


def test_data_quality_ops_d5_writes_local_ops_packet_json(tmp_path):
    issue_list = _build_issue_list(tmp_path)
    queue = build_data_repair_queue(
        queue_id="DQ-D5-REPAIR-QUEUE-2",
        issue_list=issue_list,
    )
    packet = build_data_quality_ops_packet(
        packet_id="DQ-D5-PACKET-2",
        issue_list=issue_list,
        repair_queue=queue,
    )

    output_path = tmp_path / "data_quality_ops_packet.json"
    written = write_data_quality_ops_packet(packet, output_path)

    assert written == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["packet_id"] == "DQ-D5-PACKET-2"
    assert loaded["repair_queue"]["repair_queue_is_execution_instruction"] is False
    assert loaded["source_content_mutation_allowed"] is False
    assert loaded["trade_action_enabled"] is False
    assert loaded["real_execution_allowed"] is False
