from copy import deepcopy

from apps.watchlist_lifecycle_app_1.lifecycle_schema import (
    ACTIVE_WATCH,
    DROP_REVIEW,
    ENTRY_REVIEW,
    REVIEW_REQUIRED,
    STALE_REVIEW,
    create_lifecycle_record,
    get_lifecycle_state_schemas,
    is_transition_allowed,
    validate_lifecycle_record,
    validate_state_schema_catalog,
)


def _sample_record(current_state=ENTRY_REVIEW, previous_state=None):
    return create_lifecycle_record(
        lifecycle_record_id="wl-life-001",
        candidate_id="candidate-001",
        symbol="BTCUSDT",
        current_state=current_state,
        previous_state=previous_state,
        state_reason="paper lifecycle review only",
        source_app_ids=["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
        source_manifest_id="manifest-001",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )


def test_d3_state_schema_catalog_is_complete_and_review_only():
    schemas = get_lifecycle_state_schemas()

    assert set(schemas.keys()) == {
        ENTRY_REVIEW,
        ACTIVE_WATCH,
        REVIEW_REQUIRED,
        STALE_REVIEW,
        DROP_REVIEW,
    }

    validation = validate_state_schema_catalog(schemas)

    assert validation["valid"] is True
    assert validation["issues"] == []

    assert schemas[DROP_REVIEW]["terminal"] is True
    assert schemas[ENTRY_REVIEW]["terminal"] is False


def test_d3_allowed_transitions_are_explicit_and_no_drop_exit():
    assert is_transition_allowed(None, ENTRY_REVIEW) is True
    assert is_transition_allowed(ENTRY_REVIEW, ACTIVE_WATCH) is True
    assert is_transition_allowed(ACTIVE_WATCH, STALE_REVIEW) is True
    assert is_transition_allowed(STALE_REVIEW, REVIEW_REQUIRED) is True
    assert is_transition_allowed(REVIEW_REQUIRED, DROP_REVIEW) is True

    assert is_transition_allowed(None, ACTIVE_WATCH) is False
    assert is_transition_allowed(DROP_REVIEW, ACTIVE_WATCH) is False
    assert is_transition_allowed(ACTIVE_WATCH, ENTRY_REVIEW) is False


def test_d3_lifecycle_record_defaults_disable_trade_position_and_mutation_surfaces():
    record = _sample_record()

    assert record["operator_review_required"] is True
    assert record["transition_allowed"] is True

    for key in [
        "operator_review_bypass_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "position_management_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
    ]:
        assert record[key] is False


def test_d3_lifecycle_record_validator_accepts_valid_paper_record():
    record = _sample_record(current_state=STALE_REVIEW, previous_state=ACTIVE_WATCH)
    validation = validate_lifecycle_record(record)

    assert validation["valid"] is True
    assert validation["issues"] == []
    assert validation["current_state"] == STALE_REVIEW
    assert validation["previous_state"] == ACTIVE_WATCH


def test_d3_lifecycle_record_validator_rejects_trade_or_invalid_transition():
    record = _sample_record(current_state=ENTRY_REVIEW, previous_state=ACTIVE_WATCH)
    record["trade_action_allowed"] = True
    record["automatic_position_sizing_allowed"] = True

    validation = validate_lifecycle_record(record)

    assert validation["valid"] is False
    assert "transition is not allowed" in validation["issues"]
    assert "trade_action_allowed must be false" in validation["issues"]
    assert "automatic_position_sizing_allowed must be false" in validation["issues"]


def test_d3_state_schema_catalog_validator_rejects_schema_mutation():
    schemas = get_lifecycle_state_schemas()
    mutated = deepcopy(schemas)
    mutated[DROP_REVIEW]["allowed_next_states"] = [ACTIVE_WATCH]
    mutated[ENTRY_REVIEW]["required_reason_codes"] = []

    validation = validate_state_schema_catalog(mutated)

    assert validation["valid"] is False
    assert "DROP_REVIEW allowed_next_states mismatch" in validation["issues"]
    assert "ENTRY_REVIEW required_reason_codes must not be empty" in validation["issues"]
