"""MARKET-SCENARIO-D1 contract.

This module defines the paper-only sidecar boundary for MARKET-SCENARIO-APP-1.
It does not import or mutate the frozen FCF core.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


APP_ID = "MARKET-SCENARIO-APP-1"
STAGE_ID = "MARKET-SCENARIO-D1"


@dataclass(frozen=True)
class MarketScenarioContract:
    app_id: str
    stage_id: str
    purpose: str
    allowed_input_sources: List[str]
    allowed_outputs: List[str]
    required_safety_flags: Dict[str, bool]
    forbidden_capabilities: Dict[str, bool]
    scenario_forbidden_scope: Dict[str, bool]
    operator_review_required: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def build_market_scenario_contract() -> MarketScenarioContract:
    return MarketScenarioContract(
        app_id=APP_ID,
        stage_id=STAGE_ID,
        purpose="paper_only_local_market_scenario_review_layer",
        allowed_input_sources=[
            "report_archive_outputs",
            "data_quality_ops_outputs",
            "operator_review_outputs",
            "ui_ai_stock_handoff_metadata",
        ],
        allowed_outputs=[
            "market_scenario_contract",
            "scenario_source_loader_contract",
            "scenario_definition_schema",
            "scenario_assumption_model",
            "risk_context_model",
            "paper_only_scenario_review_packet",
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
        scenario_forbidden_scope={
            "scenario_label_as_trade_instruction": False,
            "scenario_score_as_trade_instruction": False,
            "scenario_review_status_bypass_operator_review": False,
            "scenario_packet_as_order_ticket": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "live_market_order_allowed": False,
            "real_account_state_allowed": False,
        },
        operator_review_required=True,
    )
