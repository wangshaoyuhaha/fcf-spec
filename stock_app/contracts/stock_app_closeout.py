"""STOCK-APP-1 final closeout contract.

Sidecar-only closeout summary for STOCK-APP-1.
No core modification, no real trading, no deploy.
"""


def build_stock_app_1_completion_summary():
    return {
        "app": "STOCK-APP",
        "stage": "STOCK-APP-1",
        "status": "completed",
        "branch": "sidecar-stock-app-1",
        "baseline_before_closeout": 1109,
        "completed_steps": [
            "D1 base candidate filter",
            "D2 sector theme linkage",
            "D3 volume price anomaly rules",
            "D4 public fund flow proxy",
            "D5 limit up potential scoring",
            "D6 ranked watchlist handoff",
        ],
        "outputs": [
            "ranked_watchlist",
            "candidate_report",
            "score_breakdown",
            "reason_codes",
            "risk_flags",
            "data_quality_state",
            "confidence_level",
            "data_sources",
            "operator_review_required",
        ],
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }


def build_stock_app_1_boundary_summary():
    return {
        "sidecar_only": True,
        "core_import_allowed": False,
        "core_modified": False,
        "p48_core_expansion": False,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "guaranteed_limit_up_claim_allowed": False,
        "real_trading_allowed": False,
        "exchange_api_allowed": False,
        "brokerage_api_allowed": False,
        "api_key_required": False,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_balance_position_read_allowed": False,
        "real_money_impact_allowed": False,
        "operator_review_required": True,
    }


def build_stock_app_1_handoff_packet():
    return {
        "app": "STOCK-APP",
        "stage": "STOCK-APP-1",
        "handoff_status": "ready_for_operator_review",
        "ready_for_merge_review": True,
        "auto_merge_allowed": False,
        "auto_tag_allowed": False,
        "auto_release_allowed": False,
        "auto_deploy_allowed": False,
        "next_recommended_phase": "AI-CONTEXT-1 after merge review",
        "completion_summary": build_stock_app_1_completion_summary(),
        "boundary_summary": build_stock_app_1_boundary_summary(),
    }
