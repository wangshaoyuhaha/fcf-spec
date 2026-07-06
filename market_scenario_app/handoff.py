"""MARKET-SCENARIO-D6 final workflow handoff and closeout.

The final handoff summarizes MARKET-SCENARIO-APP-1 completion.
It does not merge, tag, release, deploy, trade, execute, connect to brokers,
connect to exchanges, or create order tickets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


APP_ID = "MARKET-SCENARIO-APP-1"
STAGE_ID = "MARKET-SCENARIO-D6"

COMPLETED_STAGES = [
    "MARKET-SCENARIO-D1",
    "MARKET-SCENARIO-D2",
    "MARKET-SCENARIO-D3",
    "MARKET-SCENARIO-D4",
    "MARKET-SCENARIO-D5",
    "MARKET-SCENARIO-D6",
]


@dataclass(frozen=True)
class MarketScenarioWorkflowHandoff:
    app_id: str
    stage_id: str
    completed_stages: List[str]
    branch_name: str
    handoff_summary: str
    generated_artifacts: List[str]
    downstream_allowed_uses: List[str]
    downstream_forbidden_uses: List[str]
    operator_review_required: bool
    merge_review_required: bool
    safety_flags: Dict[str, bool]
    generated_at_utc: str
    notes: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MarketScenarioCloseoutSummary:
    app_id: str
    stage_id: str
    closeout_status: str
    completed_stage_count: int
    final_validation_expected: str
    final_pytest_expected: str
    git_status_expected: str
    tag_allowed: bool
    release_allowed: bool
    deploy_allowed: bool
    main_merge_allowed_without_operator_confirmation: bool
    operator_review_required: bool
    no_execution_receipt: Dict[str, object]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_market_scenario_workflow_handoff(
    branch_name: str = "sidecar-market-scenario-app-1",
    generated_at_utc: Optional[str] = None,
    notes: str = "",
) -> MarketScenarioWorkflowHandoff:
    return MarketScenarioWorkflowHandoff(
        app_id=APP_ID,
        stage_id=STAGE_ID,
        completed_stages=list(COMPLETED_STAGES),
        branch_name=branch_name,
        handoff_summary=(
            "MARKET-SCENARIO-APP-1 completed a paper-only local market scenario "
            "review layer with contract, source metadata loader, scenario schema, "
            "assumption and risk context model, review packet, and final handoff."
        ),
        generated_artifacts=[
            "market_scenario_app/contract.py",
            "market_scenario_app/source_loader.py",
            "market_scenario_app/schema.py",
            "market_scenario_app/risk_context.py",
            "market_scenario_app/review_packet.py",
            "market_scenario_app/handoff.py",
            "docs/MARKET_SCENARIO_APP_1_D1_CONTRACT.md",
            "docs/MARKET_SCENARIO_APP_1_D2_SOURCE_LOADER.md",
            "docs/MARKET_SCENARIO_APP_1_D3_SCHEMA.md",
            "docs/MARKET_SCENARIO_APP_1_D4_RISK_CONTEXT.md",
            "docs/MARKET_SCENARIO_APP_1_D5_REVIEW_PACKET.md",
            "docs/MARKET_SCENARIO_APP_1_D6_HANDOFF_CLOSEOUT.md",
        ],
        downstream_allowed_uses=[
            "operator_review",
            "paper_only_scenario_review",
            "local_report_archive",
            "future_sidecar_read_only_consumption",
        ],
        downstream_forbidden_uses=[
            "trade_instruction",
            "order_ticket",
            "automatic_position_sizing",
            "automatic_portfolio_action",
            "live_market_order",
            "real_execution",
            "broker_connection",
            "exchange_connection",
            "api_key_storage",
            "wallet_private_key_access",
            "real_account_access",
            "real_position_access",
            "p48_core_expansion",
            "p1_p47_core_mutation",
            "tag",
            "release",
            "deploy",
        ],
        operator_review_required=True,
        merge_review_required=True,
        safety_flags={
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "merge_review_required": True,
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
        generated_at_utc=generated_at_utc or _now_utc_iso(),
        notes=notes,
    )


def build_market_scenario_closeout_summary(
    final_pytest_expected: str = "1293 passed",
) -> MarketScenarioCloseoutSummary:
    return MarketScenarioCloseoutSummary(
        app_id=APP_ID,
        stage_id=STAGE_ID,
        closeout_status="READY_FOR_OPERATOR_MERGE_REVIEW",
        completed_stage_count=len(COMPLETED_STAGES),
        final_validation_expected="ALL CHECKS PASSED",
        final_pytest_expected=final_pytest_expected,
        git_status_expected="clean",
        tag_allowed=False,
        release_allowed=False,
        deploy_allowed=False,
        main_merge_allowed_without_operator_confirmation=False,
        operator_review_required=True,
        no_execution_receipt={
            "paper_only": True,
            "local_only": True,
            "trade_action_enabled": False,
            "buy_button_enabled": False,
            "sell_button_enabled": False,
            "order_button_enabled": False,
            "real_execution_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
        },
    )


def validate_market_scenario_workflow_handoff(handoff: MarketScenarioWorkflowHandoff) -> List[str]:
    errors: List[str] = []

    if handoff.app_id != APP_ID:
        errors.append("invalid_app_id")
    if handoff.stage_id != STAGE_ID:
        errors.append("invalid_stage_id")
    if handoff.completed_stages != COMPLETED_STAGES:
        errors.append("completed_stages_mismatch")
    if not handoff.branch_name.strip():
        errors.append("branch_name_required")
    if not handoff.generated_artifacts:
        errors.append("generated_artifacts_required")
    if handoff.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")
    if handoff.merge_review_required is not True:
        errors.append("merge_review_required_must_be_true")

    for forbidden_use in [
        "trade_instruction",
        "order_ticket",
        "automatic_position_sizing",
        "automatic_portfolio_action",
        "real_execution",
        "broker_connection",
        "exchange_connection",
        "p48_core_expansion",
        "p1_p47_core_mutation",
        "tag",
        "release",
        "deploy",
    ]:
        if forbidden_use not in handoff.downstream_forbidden_uses:
            errors.append(f"missing_forbidden_use_{forbidden_use}")

    flags = handoff.safety_flags
    for key in ["paper_only", "local_only", "read_only", "sidecar_only", "operator_review_required"]:
        if flags.get(key) is not True:
            errors.append(f"{key}_must_be_true")

    for key in [
        "real_trading_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        if flags.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    return errors


def validate_market_scenario_closeout_summary(summary: MarketScenarioCloseoutSummary) -> List[str]:
    errors: List[str] = []

    if summary.app_id != APP_ID:
        errors.append("invalid_app_id")
    if summary.stage_id != STAGE_ID:
        errors.append("invalid_stage_id")
    if summary.closeout_status != "READY_FOR_OPERATOR_MERGE_REVIEW":
        errors.append("invalid_closeout_status")
    if summary.completed_stage_count != len(COMPLETED_STAGES):
        errors.append("completed_stage_count_mismatch")
    if summary.final_validation_expected != "ALL CHECKS PASSED":
        errors.append("invalid_final_validation_expected")
    if summary.git_status_expected != "clean":
        errors.append("invalid_git_status_expected")
    if summary.tag_allowed is not False:
        errors.append("tag_must_not_be_allowed")
    if summary.release_allowed is not False:
        errors.append("release_must_not_be_allowed")
    if summary.deploy_allowed is not False:
        errors.append("deploy_must_not_be_allowed")
    if summary.main_merge_allowed_without_operator_confirmation is not False:
        errors.append("main_merge_without_operator_confirmation_must_not_be_allowed")
    if summary.operator_review_required is not True:
        errors.append("operator_review_required_must_be_true")

    receipt = summary.no_execution_receipt
    for key in [
        "trade_action_enabled",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "real_execution_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
    ]:
        if receipt.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    return errors


def is_valid_market_scenario_workflow_handoff(handoff: MarketScenarioWorkflowHandoff) -> bool:
    return validate_market_scenario_workflow_handoff(handoff) == []


def is_valid_market_scenario_closeout_summary(summary: MarketScenarioCloseoutSummary) -> bool:
    return validate_market_scenario_closeout_summary(summary) == []
