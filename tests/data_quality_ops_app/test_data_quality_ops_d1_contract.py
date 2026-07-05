from data_quality_ops_app import (
    DATA_QUALITY_OPS_APP_ID,
    DATA_QUALITY_OPS_STAGE_ID,
    build_data_quality_ops_contract,
    validate_data_quality_ops_contract,
)


def test_data_quality_ops_d1_contract_identity_and_source_scope():
    contract = build_data_quality_ops_contract()

    assert contract.app_id == DATA_QUALITY_OPS_APP_ID
    assert contract.stage_id == DATA_QUALITY_OPS_STAGE_ID

    assert contract.allowed_source_app_ids == (
        "DATA-APP-1",
        "REPORT-ARCHIVE-APP-1",
        "OPERATOR-REVIEW-APP-1",
    )
    assert "health_check_report" in contract.allowed_source_types
    assert "quarantine_report" in contract.allowed_source_types
    assert "archive_manifest" in contract.allowed_source_types
    assert "data_quality_issue_list" in contract.ops_output_types
    assert "data_repair_queue" in contract.ops_output_types

    assert validate_data_quality_ops_contract(contract) == []


def test_data_quality_ops_d1_contract_preserves_safety_boundary():
    contract = build_data_quality_ops_contract()

    assert contract.paper_only is True
    assert contract.local_only is True
    assert contract.read_only is True
    assert contract.sidecar_only is True
    assert contract.operator_review_required is True
    assert contract.operator_review_bypass_allowed is False

    assert contract.source_content_mutation_allowed is False
    assert contract.source_deletion_allowed is False
    assert contract.source_overwrite_allowed is False
    assert contract.repair_queue_is_execution_instruction is False
    assert contract.ops_check_is_trade_instruction is False

    assert validate_data_quality_ops_contract(contract) == []


def test_data_quality_ops_d1_contract_forbids_trading_core_and_deploy():
    contract = build_data_quality_ops_contract()

    assert contract.real_execution_allowed is False
    assert contract.trade_action_enabled is False
    assert contract.buy_button_enabled is False
    assert contract.sell_button_enabled is False
    assert contract.order_button_enabled is False
    assert contract.broker_connection_allowed is False
    assert contract.exchange_connection_allowed is False
    assert contract.credential_storage_allowed is False
    assert contract.wallet_private_key_access_allowed is False
    assert contract.real_account_access_allowed is False
    assert contract.real_position_access_allowed is False
    assert contract.core_mutation_allowed is False
    assert contract.p48_core_expansion_allowed is False
    assert contract.tag_created is False
    assert contract.release_created is False
    assert contract.deployed is False

    assert validate_data_quality_ops_contract(contract) == []
