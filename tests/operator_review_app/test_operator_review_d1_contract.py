from operator_review_app import (
    OPERATOR_REVIEW_APP_ID,
    OPERATOR_REVIEW_STAGE_ID,
    build_paper_review_contract,
    validate_paper_review_contract,
)


def test_operator_review_d1_contract_identity_and_boundary_flags():
    contract = build_paper_review_contract()

    assert contract.app_id == OPERATOR_REVIEW_APP_ID
    assert contract.stage_id == OPERATOR_REVIEW_STAGE_ID

    assert contract.paper_only is True
    assert contract.local_only is True
    assert contract.read_only is True
    assert contract.sidecar_only is True
    assert contract.operator_review_required is True
    assert contract.operator_review_bypass_allowed is False

    assert validate_paper_review_contract(contract) == []


def test_operator_review_d1_contract_forbids_execution_and_trade_actions():
    contract = build_paper_review_contract()

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

    assert contract.review_status_is_trade_action is False
    assert contract.paper_decision_label_is_trade_action is False


def test_operator_review_d1_contract_forbids_core_expansion_and_mutation():
    contract = build_paper_review_contract()

    assert contract.core_mutation_allowed is False
    assert contract.p48_core_expansion_allowed is False
    assert "ui_app_local_report_artifact" in contract.source_types
    assert "ui_app_workflow_handoff" in contract.source_types
    assert "operator_review_handoff_packet" in contract.output_record_types
