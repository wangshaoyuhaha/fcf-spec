from apps.dify_ui_handoff_app_1.contract import (
    APP_ID,
    STAGE_ID,
    get_dify_ui_handoff_contract,
    summarize_dify_ui_handoff_contract,
    validate_dify_ui_handoff_contract,
)


def test_dify_ui_handoff_d1_contract_is_valid():
    contract = get_dify_ui_handoff_contract()
    validation = validate_dify_ui_handoff_contract(contract)

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID
    assert validation["valid"] is True
    assert validation["issues"] == []


def test_dify_ui_handoff_d1_preserves_safety_boundary():
    contract = get_dify_ui_handoff_contract()
    flags = contract["safety_flags"]

    assert flags["paper_only"] is True
    assert flags["local_only"] is True
    assert flags["read_only"] is True
    assert flags["sidecar_only"] is True
    assert flags["operator_review_required"] is True

    assert flags["real_execution_allowed"] is False
    assert flags["trade_action_enabled"] is False
    assert flags["buy_button_enabled"] is False
    assert flags["sell_button_enabled"] is False
    assert flags["order_button_enabled"] is False
    assert flags["broker_connection_allowed"] is False
    assert flags["exchange_connection_allowed"] is False
    assert flags["api_key_storage_allowed"] is False
    assert flags["wallet_private_key_access_allowed"] is False
    assert flags["workflow_auto_approval_allowed"] is False
    assert flags["llm_trade_instruction_allowed"] is False


def test_dify_ui_handoff_d1_reads_existing_ui_and_report_artifacts():
    contract = get_dify_ui_handoff_contract()
    paths = {source["relative_path"] for source in contract["upstream_read_sources"]}
    requirements = {
        source["relative_path"]: source["required"]
        for source in contract["upstream_read_sources"]
    }

    assert "runtime/operator_console/index.html" in paths
    assert "artifacts/operator_console_static_export" in paths
    assert "artifacts/operator_workflow_bundle" in paths
    assert "artifacts/paper_readable_report" in paths
    assert "artifacts/paper_governance_report" in paths
    assert requirements["runtime/operator_console/index.html"] is True
    assert requirements["artifacts/operator_workflow_bundle"] is False


def test_dify_ui_handoff_d1_forbids_trade_outputs():
    contract = get_dify_ui_handoff_contract()
    forbidden = set(contract["forbidden_dify_outputs"])

    assert "buy instruction" in forbidden
    assert "sell instruction" in forbidden
    assert "order instruction" in forbidden
    assert "api key request" in forbidden
    assert "operator review bypass" in forbidden
    assert "profit guarantee" in forbidden


def test_dify_ui_handoff_d1_summary_is_operator_safe():
    summary = summarize_dify_ui_handoff_contract()

    assert summary["valid"] is True
    assert summary["paper_only"] is True
    assert summary["local_only"] is True
    assert summary["read_only"] is True
    assert summary["operator_review_required"] is True
    assert summary["manual_dify_configuration_required"] is True
    assert summary["real_execution_allowed"] is False
    assert summary["trade_action_enabled"] is False
