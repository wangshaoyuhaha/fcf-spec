from report_archive_app import (
    REPORT_ARCHIVE_APP_ID,
    REPORT_ARCHIVE_STAGE_ID,
    build_report_archive_contract,
    validate_report_archive_contract,
)


def test_report_archive_d1_contract_identity_and_source_scope():
    contract = build_report_archive_contract()

    assert contract.app_id == REPORT_ARCHIVE_APP_ID
    assert contract.stage_id == REPORT_ARCHIVE_STAGE_ID

    assert contract.allowed_source_app_ids == (
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
        "UI-APP-1",
        "OPERATOR-REVIEW-APP-1",
    )
    assert "local_report_artifact" in contract.allowed_source_types
    assert "workflow_handoff" in contract.allowed_source_types
    assert "paper_archive_packet" in contract.archive_output_types

    assert validate_report_archive_contract(contract) == []


def test_report_archive_d1_contract_preserves_sidecar_safety_boundary():
    contract = build_report_archive_contract()

    assert contract.paper_only is True
    assert contract.local_only is True
    assert contract.read_only is True
    assert contract.sidecar_only is True
    assert contract.operator_review_required is True
    assert contract.operator_review_bypass_allowed is False

    assert contract.source_content_mutation_allowed is False
    assert contract.source_deletion_allowed is False
    assert contract.source_overwrite_allowed is False
    assert contract.archive_packet_is_trade_instruction is False

    assert validate_report_archive_contract(contract) == []


def test_report_archive_d1_contract_forbids_execution_trading_and_deploy():
    contract = build_report_archive_contract()

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

    assert validate_report_archive_contract(contract) == []
