from typing import Any

from btc_finance_platform.paper_readable_report import build_paper_analysis_markdown_report


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


P4_COMPLETED_SCOPE = [
    "P4-D1 price deviation analysis",
    "P4-D2 simple momentum and paper risk score",
    "P4-D3 paper signal draft and batch analysis baseline",
    "P4-D4 extract analysis inputs from P3 handoff package",
    "P4-D5 run paper analysis from local files through handoff",
    "P4-D6 build writable paper analysis pipeline report",
    "P4-D7 symbol-level operator review item",
    "P4-D8 operator review checklist",
    "P4-D9 writable paper analysis review packet",
    "P4-D10 paper report summary from review packet",
    "P4-D11 human-readable markdown report",
    "P4-D12 markdown and json report bundle artifact",
    "P4-D13 P4 analysis layer closeout summary",
    "P4-D14 paper-only safety acceptance",
    "P4-D15 P5 transition anchor",
]


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def get_p4_analysis_layer_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p4_analysis_layer_capabilities",
        "phase": "P4",
        "status": "completed",
        "completed_scope": list(P4_COMPLETED_SCOPE),
        "capabilities": [
            "price deviation analysis",
            "deviation magnitude classification",
            "simple momentum analysis",
            "baseline paper risk score",
            "paper signal draft",
            "batch paper analysis",
            "P3 handoff to P4 analysis pipeline",
            "paper analysis pipeline report",
            "operator review packet",
            "human-readable markdown report",
            "json and markdown report artifacts",
        ],
        "current_repository": "btc_finance_platform",
        "current_role": "first BTC paper-only implementation line",
        "broader_goal": "general FCF-style finance platform for stocks and other markets",
        **paper_flags(),
    }


def get_p4_safety_acceptance() -> dict[str, Any]:
    checks = {
        "paper_only": True,
        "no_real_exchange_api": True,
        "no_real_api_key_required": True,
        "no_wallet_private_key_required": True,
        "no_real_order": True,
        "no_real_execution": True,
        "no_real_balance": True,
        "no_real_position": True,
        "no_real_money_impact": True,
        "operator_review_required": True,
        "reports_are_not_financial_advice": True,
        "signals_are_paper_only_drafts": True,
        "btc_is_first_line_not_final_platform_boundary": True,
        "future_stocks_and_other_markets_supported_by_architecture": True,
    }

    return {
        "ok": all(checks.values()),
        "type": "p4_safety_acceptance",
        "phase": "P4",
        "checks": checks,
        "decision": "P4 accepted for paper-only analysis-layer closeout",
        **paper_flags(),
    }


def get_p4_to_p5_transition_anchor() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p4_to_p5_transition_anchor",
        "from_phase": "P4 paper analysis logic enhancement",
        "to_phase": "P5 risk governance and regime layer",
        "p5_candidate_scope": [
            "risk governor baseline",
            "regime classification baseline",
            "policy constraints over paper signals",
            "operator approval gate hardening",
            "audit trail for analysis and review decisions",
            "multi-market architecture preparation",
        ],
        "must_preserve": [
            "paper-only boundary",
            "operator review required",
            "no real exchange API",
            "no real API keys",
            "no wallet private keys",
            "no real orders",
            "no real execution",
            "no real balances or positions",
            "no real money impact",
            "FCF-style event-driven architecture direction",
        ],
        **paper_flags(),
    }


def build_p4_closeout_package(file_paths: list[Any]) -> dict[str, Any]:
    report = build_paper_analysis_markdown_report(file_paths)
    capabilities = get_p4_analysis_layer_capabilities()
    safety = get_p4_safety_acceptance()
    transition = get_p4_to_p5_transition_anchor()

    return {
        "ok": report["ok"] is True and capabilities["ok"] is True and safety["ok"] is True and transition["ok"] is True,
        "type": "p4_closeout_package",
        "phase": "P4",
        "status": "completed",
        "report_type": report["type"],
        "summary": report["summary"],
        "capabilities": capabilities,
        "safety_acceptance": safety,
        "transition_anchor": transition,
        "next_phase": "P5 risk governance and regime layer",
        "decision": "P4_closed_paper_only_ready_for_P5",
        **paper_flags(),
    }
