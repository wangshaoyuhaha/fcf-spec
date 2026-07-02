from btc_finance_platform.platform_closeout import get_fcf_architecture_anchor
from btc_finance_platform.platform_closeout import get_p3_closeout_summary
from btc_finance_platform.platform_closeout import get_p3_safety_acceptance
from btc_finance_platform.platform_closeout import get_platform_direction_statement


def test_fcf_architecture_anchor_preserves_original_skeleton():
    result = get_fcf_architecture_anchor()

    assert result["ok"] is True
    assert result["type"] == "fcf_architecture_anchor"
    assert result["original_skeleton"]["source_project"] == "fcf_full_skeleton"
    assert "fcf/core/event_bus.py" in result["original_skeleton"]["core"]
    assert "fcf/core/event_model.py" in result["original_skeleton"]["core"]
    assert "fcf/core/policy_engine.py" in result["original_skeleton"]["core"]


def test_fcf_architecture_anchor_keeps_general_finance_direction():
    result = get_fcf_architecture_anchor()

    assert result["current_repository"] == "btc_finance_platform"
    assert result["current_role"] == "first BTC paper-only implementation line"
    assert result["broader_goal"] == "general finance platform for stocks and other markets"
    assert "audit_store_and_reproducible_history" in result["architecture_principles"]


def test_p3_closeout_summary_marks_p3_completed():
    result = get_p3_closeout_summary()

    assert result["ok"] is True
    assert result["phase"] == "P3"
    assert result["status"] == "completed"
    assert result["next_phase"] == "P4 paper analysis logic enhancement"
    assert len(result["completed_scope"]) == 15


def test_p3_closeout_summary_includes_local_data_handoff_stack():
    result = get_p3_closeout_summary()

    assert "local paper data schema" in result["current_capability"]
    assert "local JSON and CSV loader" in result["current_capability"]
    assert "manifest and sha256 audit" in result["current_capability"]
    assert "analysis handoff package" in result["current_capability"]


def test_p3_safety_acceptance_passes_all_checks():
    result = get_p3_safety_acceptance()

    assert result["ok"] is True
    assert result["decision"] == "P3 accepted for paper-only closeout"
    assert all(result["checks"].values())


def test_p3_safety_acceptance_blocks_real_world_effects():
    result = get_p3_safety_acceptance()

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_platform_direction_statement_says_btc_is_not_final_boundary():
    result = get_platform_direction_statement()

    assert result["ok"] is True
    assert result["not_a_real_trading_bot"] is True
    assert result["not_limited_to_btc_long_term"] is True
    assert result["must_keep_operator_review"] is True
    assert "general FCF-style finance platform" in result["statement"]
