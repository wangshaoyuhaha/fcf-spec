"""BACKTEST-REVIEW-D1 contract.

This module defines the paper-only sidecar boundary for BACKTEST-REVIEW-APP-1.
It does not import or mutate the frozen FCF core.
A backtest review is not a trade instruction, profit guarantee, order ticket,
execution request, or real account analysis.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


APP_ID = "BACKTEST-REVIEW-APP-1"
STAGE_ID = "BACKTEST-REVIEW-D1"


@dataclass(frozen=True)
class BacktestReviewContract:
    app_id: str
    stage_id: str
    purpose: str
    allowed_input_sources: List[str]
    allowed_outputs: List[str]
    required_safety_flags: Dict[str, bool]
    forbidden_capabilities: Dict[str, bool]
    backtest_forbidden_scope: Dict[str, bool]
    operator_review_required: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def build_backtest_review_contract() -> BacktestReviewContract:
    return BacktestReviewContract(
        app_id=APP_ID,
        stage_id=STAGE_ID,
        purpose="paper_only_local_historical_backtest_review_layer",
        allowed_input_sources=[
            "report_archive_outputs",
            "market_scenario_outputs",
            "operator_review_outputs",
            "data_quality_ops_outputs",
            "ui_ai_stock_handoff_metadata",
        ],
        allowed_outputs=[
            "backtest_review_contract",
            "backtest_source_loader_contract",
            "backtest_review_schema",
            "backtest_result_packet",
            "backtest_risk_summary",
            "paper_only_backtest_review_packet",
            "final_workflow_handoff",
        ],
        required_safety_flags={
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
        },
        forbidden_capabilities={
            "p48_core_expansion_allowed": False,
            "p1_p47_core_mutation_allowed": False,
            "source_content_mutation_allowed": False,
            "source_deletion_allowed": False,
            "source_overwrite_allowed": False,
            "real_trading_allowed": False,
            "real_execution_allowed": False,
            "broker_connection_allowed": False,
            "exchange_connection_allowed": False,
            "api_key_storage_allowed": False,
            "wallet_private_key_access_allowed": False,
            "real_account_access_allowed": False,
            "real_position_access_allowed": False,
            "buy_button_enabled": False,
            "sell_button_enabled": False,
            "order_button_enabled": False,
            "tag_allowed": False,
            "release_allowed": False,
            "deploy_allowed": False,
        },
        backtest_forbidden_scope={
            "backtest_result_as_profit_guarantee": False,
            "backtest_metric_as_trade_instruction": False,
            "backtest_review_status_bypass_operator_review": False,
            "backtest_packet_as_order_ticket": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "live_market_order_allowed": False,
            "real_account_state_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
        },
        operator_review_required=True,
    )
