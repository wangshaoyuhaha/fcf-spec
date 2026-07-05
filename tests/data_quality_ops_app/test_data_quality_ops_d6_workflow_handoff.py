import json

from data_quality_ops_app import (
    DATA_QUALITY_OPS_FINAL_STAGE_ID,
    FINAL_DATA_QUALITY_OPS_CLOSEOUT_STATUS,
    build_data_quality_issue_list,
    build_data_quality_ops_checks,
    build_data_quality_ops_closeout_summary,
    build_data_quality_ops_packet,
    build_data_repair_queue,
    build_final_data_quality_ops_handoff,
    load_data_quality_ops_source,
    validate_final_data_quality_ops_handoff,
    write_final_data_quality_ops_handoff,
)


def _build_ops_packet(tmp_path):
    first = tmp_path / "limited.json"
    second = tmp_path / "fail.json"
    first.write_text(json.dumps({"data_quality_state": "PASS_LIMITED"}), encoding="utf-8")
    second.write_text(json.dumps({"data_quality_state": "FAIL_QUARANTINE"}), encoding="utf-8")

    sources = [
        load_data_quality_ops_source(first, source_app_id="DATA-APP-1", source_type="health_check_report"),
        load_data_quality_ops_source(second, source_app_id="DATA-APP-1", source_type="health_check_report"),
    ]
    checks = build_data_quality_ops_checks(sources, check_set_id="DQ-D6")
    issue_list = build_data_quality_issue_list(issue_list_id="DQ-D6-ISSUES", checks=checks)
    queue = build_data_repair_queue(queue_id="DQ-D6-REPAIR-QUEUE", issue_list=issue_list)
    return build_data_quality_ops_packet(
        packet_id="DQ-D6-PACKET",
        issue_list=issue_list,
        repair_queue=queue,
    )


def test_data_quality_ops_d6_builds_final_handoff(tmp_path):
    packet = _build_ops_packet(tmp_path)

    handoff = build_final_data_quality_ops_handoff(
        handoff_id="FINAL-DQ-D6-001",
        data_quality_ops_packet=packet,
    )

    assert handoff.handoff_id == "FINAL-DQ-D6-001"
    assert handoff.stage_id == DATA_QUALITY_OPS_FINAL_STAGE_ID
    assert handoff.source_packet_id == "DQ-D6-PACKET"
    assert handoff.closeout_status == FINAL_DATA_QUALITY_OPS_CLOSEOUT_STATUS
    assert handoff.paper_only is True
    assert handoff.local_only is True
    assert handoff.read_only is True
    assert handoff.sidecar_only is True
    assert handoff.operator_review_required is True
    assert handoff.operator_review_bypass_allowed is False
    assert validate_final_data_quality_ops_handoff(handoff) == []


def test_data_quality_ops_d6_final_handoff_forbids_execution_mutation_and_deploy(tmp_path):
    packet = _build_ops_packet(tmp_path)

    handoff = build_final_data_quality_ops_handoff(
        handoff_id="FINAL-DQ-D6-002",
        data_quality_ops_packet=packet,
    )

    assert handoff.source_content_mutation_allowed is False
    assert handoff.source_deletion_allowed is False
    assert handoff.source_overwrite_allowed is False
    assert handoff.repair_queue_is_execution_instruction is False
    assert handoff.ops_check_is_trade_instruction is False
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


def test_data_quality_ops_d6_builds_closeout_summary(tmp_path):
    packet = _build_ops_packet(tmp_path)
    handoff = build_final_data_quality_ops_handoff(
        handoff_id="FINAL-DQ-D6-003",
        data_quality_ops_packet=packet,
    )

    summary = build_data_quality_ops_closeout_summary(handoff)

    assert summary["app_id"] == "DATA-QUALITY-OPS-APP-1"
    assert summary["stage_id"] == "DATA-QUALITY-OPS-D6"
    assert summary["closeout_status"] == FINAL_DATA_QUALITY_OPS_CLOSEOUT_STATUS
    assert summary["completed_stages"] == [
        "DATA-QUALITY-OPS-D1",
        "DATA-QUALITY-OPS-D2",
        "DATA-QUALITY-OPS-D3",
        "DATA-QUALITY-OPS-D4",
        "DATA-QUALITY-OPS-D5",
        "DATA-QUALITY-OPS-D6",
    ]
    assert summary["source_content_mutation_allowed"] is False
    assert summary["repair_queue_is_execution_instruction"] is False
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
    assert summary["tag_created"] is False
    assert summary["release_created"] is False
    assert summary["deployed"] is False


def test_data_quality_ops_d6_writes_final_handoff_json(tmp_path):
    packet = _build_ops_packet(tmp_path)
    handoff = build_final_data_quality_ops_handoff(
        handoff_id="FINAL-DQ-D6-004",
        data_quality_ops_packet=packet,
    )

    output_path = tmp_path / "final_data_quality_ops_handoff.json"
    written = write_final_data_quality_ops_handoff(handoff, output_path)

    assert written == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["handoff_id"] == "FINAL-DQ-D6-004"
    assert loaded["stage_id"] == "DATA-QUALITY-OPS-D6"
    assert loaded["real_execution_allowed"] is False
    assert loaded["trade_action_enabled"] is False
    assert loaded["deployed"] is False
