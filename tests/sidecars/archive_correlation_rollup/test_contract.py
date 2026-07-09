from fcf.sidecars.archive_correlation_rollup import (
    ALLOWED_ROLLUP_STATUSES,
    ARCHIVE_CORRELATION_ROLLUP_APP_ID,
    CORRELATION_ROLLUP_REQUIRED_LINKS,
    build_correlation_rollup_contract,
)


def test_archive_correlation_rollup_contract_identity():
    contract = build_correlation_rollup_contract()

    assert contract["app_id"] == ARCHIVE_CORRELATION_ROLLUP_APP_ID
    assert contract["stage"] == "D1"
    assert contract["rollup_contract"]["identifier"] == "correlation_id"


def test_archive_correlation_rollup_is_readonly_sidecar_index_only():
    contract = build_correlation_rollup_contract()
    mode = contract["mode"]

    assert mode["paper_only"] is True
    assert mode["local_only"] is True
    assert mode["read_only"] is True
    assert mode["sidecar_only"] is True
    assert mode["index_only"] is True
    assert mode["operator_review_required"] is True


def test_archive_correlation_rollup_preserves_core_freeze():
    contract = build_correlation_rollup_contract()
    core_policy = contract["core_policy"]

    assert core_policy["core_frozen"] is True
    assert core_policy["p1_p47_frozen"] is True
    assert core_policy["p48_forbidden"] is True
    assert core_policy["core_mutation_allowed"] is False
    assert core_policy["sidecar_extension_only"] is True


def test_archive_correlation_rollup_forbids_auto_fill_and_auto_pass():
    contract = build_correlation_rollup_contract()
    rollup = contract["rollup_contract"]

    assert rollup["auto_fill_allowed"] is False
    assert rollup["evidence_backfill_allowed"] is False
    assert rollup["placeholder_review_allowed"] is False
    assert rollup["auto_pass_allowed"] is False
    assert rollup["missing_chain_policy"] == "mark_only"


def test_archive_correlation_rollup_statuses_are_limited_to_mark_only_states():
    contract = build_correlation_rollup_contract()
    statuses = contract["rollup_contract"]["allowed_statuses"]

    assert statuses == list(ALLOWED_ROLLUP_STATUSES)
    assert set(statuses) == {"COMPLETE", "INCOMPLETE", "STALE", "UNRESOLVED"}


def test_archive_correlation_rollup_required_chain_links_are_explicit():
    contract = build_correlation_rollup_contract()
    links = contract["rollup_contract"]["required_links"]

    assert links == list(CORRELATION_ROLLUP_REQUIRED_LINKS)
    assert links == [
        "data_snapshot",
        "candidate",
        "ai_explanation",
        "ui_packet",
        "review_packet",
        "archive_packet",
        "handoff",
        "final_state",
    ]


def test_archive_correlation_rollup_forbidden_actions_cover_safety_boundary():
    contract = build_correlation_rollup_contract()
    forbidden = set(contract["forbidden_actions"])

    assert "core_mutation" in forbidden
    assert "auto_pass" in forbidden
    assert "auto_fill_correlation_id" in forbidden
    assert "placeholder_review" in forbidden
    assert "ui_dashboard_panel" in forbidden
    assert "trade_execution" in forbidden
    assert "broker_api" in forbidden
    assert "exchange_api" in forbidden
    assert "api_key" in forbidden
    assert "wallet_private_key" in forbidden
    assert "real_account" in forbidden
    assert "real_position" in forbidden
    assert "buy_sell_order" in forbidden
    assert "auto_position" in forbidden
    assert "auto_portfolio_action" in forbidden
    assert "tag" in forbidden
    assert "release" in forbidden
    assert "deploy" in forbidden
    assert "p48" in forbidden


def test_archive_correlation_rollup_contract_is_defensive_copy():
    first = build_correlation_rollup_contract()
    first["rollup_contract"]["required_links"].append("mutated")

    second = build_correlation_rollup_contract()
    assert "mutated" not in second["rollup_contract"]["required_links"]
