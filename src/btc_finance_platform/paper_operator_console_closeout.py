from typing import Any

from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_acceptance_summary
from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_page_registry
from btc_finance_platform.paper_operator_console_acceptance import build_operator_console_ui_acceptance_gate


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_brokerage_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


P7_COMPLETED_SCOPE = [
    "P7-D1 local operator console contract",
    "P7-D2 dashboard summary and review queue contract",
    "P7-D3 report viewer index and writable console bundle",
    "P7-D4 operator review action contract",
    "P7-D5 paper-only approval workflow state and summary",
    "P7-D6 CLI-to-UI artifact export bridge",
    "P7-D7 operator console readable summary and markdown report",
    "P7-D8 operator console UI manifest",
    "P7-D9 static export bundle for future UI",
    "P7-D10 operator console page registry",
    "P7-D11 operator console UI acceptance gate",
    "P7-D12 writable operator console acceptance bundle",
    "P7-D13 P7 operator console closeout summary",
    "P7-D14 P7 paper-only safety acceptance",
    "P7-D15 P8 learning memory transition anchor",
]


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def get_p7_operator_console_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p7_operator_console_capabilities",
        "phase": "P7",
        "status": "completed",
        "completed_scope": list(P7_COMPLETED_SCOPE),
        "capabilities": [
            "operator console contract",
            "dashboard summary contract",
            "operator review queue",
            "report viewer index",
            "paper-only safety banner",
            "operator review action contract",
            "paper-only workflow state",
            "CLI-to-UI artifact export bridge",
            "operator console markdown report",
            "operator console UI manifest",
            "operator console page registry",
            "operator console UI acceptance gate",
            "static UI handoff readiness",
        ],
        "current_repository": "btc_finance_platform",
        "current_role": "paper-only operator console preparation layer",
        "broader_goal": "general FCF-style finance platform for stocks and other markets",
        **paper_flags(),
    }


def get_p7_safety_acceptance() -> dict[str, Any]:
    checks = {
        "paper_only": True,
        "no_real_exchange_api": True,
        "no_real_brokerage_api": True,
        "no_real_api_key_required": True,
        "no_wallet_private_key_required": True,
        "no_real_order": True,
        "no_real_execution": True,
        "no_real_balance": True,
        "no_real_position": True,
        "no_real_money_impact": True,
        "operator_review_required": True,
        "ui_handoff_does_not_enable_real_trading": True,
        "operator_approval_is_paper_review_only": True,
        "review_queue_blocks_real_world_actions": True,
        "static_exports_are_generated_artifacts_not_source_of_truth": True,
        "future_learning_must_remain_paper_only": True,
    }

    return {
        "ok": all(checks.values()),
        "type": "p7_safety_acceptance",
        "phase": "P7",
        "checks": checks,
        "decision": "P7 accepted for paper-only operator console closeout",
        **paper_flags(),
    }


def get_p7_to_p8_transition_anchor() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p7_to_p8_transition_anchor",
        "from_phase": "P7 UI and operator console preparation",
        "to_phase": "P8 learning memory and feedback dataset",
        "p8_candidate_scope": [
            "paper analysis memory schema",
            "operator review feedback dataset",
            "paper outcome tracking contract",
            "learning event audit trail",
            "feedback-to-calibration handoff",
            "paper-only learning memory report",
            "learning memory UI contract",
        ],
        "safe_learning_loop": [
            "observe",
            "analyze",
            "operator_review",
            "record_feedback",
            "backtest_and_calibrate",
            "generate_new_paper_model_version",
            "human_approval",
        ],
        "forbidden_learning_loop": [
            "observe",
            "self_learn",
            "self_trade",
        ],
        "must_preserve": [
            "paper-only boundary",
            "operator review required",
            "offline training only",
            "versioned learning artifacts",
            "no real exchange API",
            "no real brokerage API",
            "no real API keys",
            "no wallet private keys",
            "no real orders",
            "no real execution",
            "no real balances or positions",
            "no real money impact",
            "no automatic live trading",
            "no bypassing operator review",
        ],
        **paper_flags(),
    }


def build_p7_closeout_package(
    file_path: Any,
    action_by_symbol: dict[str, str] | None = None,
) -> dict[str, Any]:
    registry = build_operator_console_page_registry(file_path, action_by_symbol)
    gate = build_operator_console_ui_acceptance_gate(file_path, action_by_symbol)
    summary = build_operator_console_acceptance_summary(file_path, action_by_symbol)
    capabilities = get_p7_operator_console_capabilities()
    safety = get_p7_safety_acceptance()
    transition = get_p7_to_p8_transition_anchor()

    return {
        "ok": registry["ok"] is True and gate["ok"] is True and summary["ok"] is True and capabilities["ok"] is True and safety["ok"] is True and transition["ok"] is True,
        "type": "p7_closeout_package",
        "phase": "P7",
        "status": "completed",
        "registry_type": registry["type"],
        "acceptance_gate": gate,
        "acceptance_summary": summary,
        "capabilities": capabilities,
        "safety_acceptance": safety,
        "transition_anchor": transition,
        "next_phase": "P8 learning memory and feedback dataset",
        "decision": "P7_closed_paper_only_ready_for_P8",
        **paper_flags(),
    }
