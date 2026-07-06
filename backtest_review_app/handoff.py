"""BACKTEST-REVIEW-D6 final workflow handoff and closeout.

The final handoff summarizes BACKTEST-REVIEW-APP-1 completion.
It does not merge, tag, release, deploy, trade, execute, connect to brokers,
connect to exchanges, access real accounts, or create order tickets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


APP_ID = "BACKTEST-REVIEW-APP-1"
STAGE_ID = "BACKTEST-REVIEW-D6"

COMPLETED_STAGES = [
    "BACKTEST-REVIEW-D1",
    "BACKTEST-REVIEW-D2",
    "BACKTEST-REVIEW-D3",
    "BACKTEST-REVIEW-D4",
    "BACKTEST-REVIEW-D5",
    "BACKTEST-REVIEW-D6",
]


@dataclass(frozen=True)
class BacktestReviewWorkflowHandoff:
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
class BacktestReviewCloseoutSummary:
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


def build_backtest_review_workflow_handoff(
    branch_name: str = "sidecar-backtest-review-app-1",
    generated_at_utc: Optional[str] = None,
    notes: str = "",
) -> BacktestReviewWorkflowHandoff:
    return BacktestReviewWorkflowHandoff(
        app_id=APP_ID,
        stage_id=STAGE_ID,
        completed_stages=list(COMPLETED_STAGES),
        branch_name=branch_name,
        handoff_summary=(
            "BACKTEST-REVIEW-APP-1 completed a paper-only local historical "
            "backtest review layer with contract, source metadata loader, review "
            "schema, result packet, risk summary, and final workflow handoff."
        ),
        generated_artifacts=[
            "backtest_review_app/contract.py",
            "backtest_review_app/source_loader.py",
            "backtest_review_app/schema.py",
            "backtest_review_app/result_packet.py",
            "backtest_review_app/risk_summary.py",
            "backtest_review_app/handoff.py",
            "docs/BACKTEST_REVIEW_APP_1_D1_CONTRACT.md",
            "docs/BACKTEST_REVIEW_APP_1_D2_SOURCE_LOADER.md",
            "docs/BACKTEST_REVIEW_APP_1_D3_SCHEMA.md",
            "docs/BACKTEST_REVIEW_APP_1_D4_RESULT_PACKET.md",
            "docs/BACKTEST_REVIEW_APP_1_D5_RISK_SUMMARY.md",
            "docs/BACKTEST_REVIEW_APP_1_D6_HANDOFF_CLOSEOUT.md",
        ],
        downstream_allowed_uses=[
            "operator_review",
            "paper_only_backtest_review",
            "local_report_archive",
            "future_sidecar_read_only_consumption",
        ],
        downstream_forbidden_uses=[
            "trade_instruction",
            "profit_guarantee",
            "future_return_prediction",
            "order_ticket",
            "automatic_position_sizing",
            "automatic_portfolio_action",
            "live_market_order",
            "real_execution",
            "real_account_access",
            "real_position_access",
            "broker_connection",
            "exchange_connection",
            "api_key_storage",
            "wallet_private_key_access",
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
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
            "tag_allowed": False,
            "release_allowed": False,
            "deploy_allowed": False,
        },
        generated_at_utc=generated_at_utc or _now_utc_iso(),
        notes=notes,
    )


def build_backtest_review_closeout_summary(
    final_pytest_expected: str = "1334 passed",
) -> BacktestReviewCloseoutSummary:
    return BacktestReviewCloseoutSummary(
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
            "real_account_access_allowed": False,
            "real_position_access_allowed": False,
            "automatic_position_sizing_allowed": False,
            "automatic_portfolio_action_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
        },
    )


def validate_backtest_review_workflow_handoff(handoff: BacktestReviewWorkflowHandoff) -> List[str]:
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
        "profit_guarantee",
        "future_return_prediction",
        "order_ticket",
        "automatic_position_sizing",
        "automatic_portfolio_action",
        "real_execution",
        "real_account_access",
        "real_position_access",
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
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        if flags.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    return errors


def validate_backtest_review_closeout_summary(summary: BacktestReviewCloseoutSummary) -> List[str]:
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
        "real_account_access_allowed",
        "real_position_access_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
    ]:
        if receipt.get(key) is not False:
            errors.append(f"{key}_must_be_false")

    return errors


def is_valid_backtest_review_workflow_handoff(handoff: BacktestReviewWorkflowHandoff) -> bool:
    return validate_backtest_review_workflow_handoff(handoff) == []


def is_valid_backtest_review_closeout_summary(summary: BacktestReviewCloseoutSummary) -> bool:
    return validate_backtest_review_closeout_summary(summary) == []
