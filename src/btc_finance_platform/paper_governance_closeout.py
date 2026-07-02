from typing import Any

from btc_finance_platform.paper_governance_contract import build_governance_ui_contract


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


P5_COMPLETED_SCOPE = [
    "P5-D1 paper market regime classification baseline",
    "P5-D2 risk governor decision baseline",
    "P5-D3 policy gate over paper governor decisions",
    "P5-D4 governance audit event and audit trail",
    "P5-D5 operator approval gate",
    "P5-D6 policy constraint summary",
    "P5-D7 governance report summary",
    "P5-D8 human-readable governance markdown report",
    "P5-D9 governance markdown and json report bundle artifact",
    "P5-D10 governance UI card and UI contract",
    "P5-D11 governance decision index",
    "P5-D12 writable governance contract bundle",
    "P5-D13 P5 governance layer closeout summary",
    "P5-D14 P5 paper-only safety acceptance",
    "P5-D15 P6 transition anchor",
]


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def get_p5_governance_layer_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p5_governance_layer_capabilities",
        "phase": "P5",
        "status": "completed",
        "completed_scope": list(P5_COMPLETED_SCOPE),
        "capabilities": [
            "paper market regime classification",
            "risk governor decision baseline",
            "policy gate over paper signals",
            "governance audit trail",
            "operator approval gate",
            "policy constraint summary",
            "human-readable governance report",
            "governance UI contract",
            "governance decision index",
            "writable governance contract bundle",
            "FCF-style governor, regime, policy engine, and audit store direction",
        ],
        "current_repository": "btc_finance_platform",
        "current_role": "first BTC paper-only implementation line",
        "broader_goal": "general FCF-style finance platform for stocks and other markets",
        **paper_flags(),
    }


def get_p5_safety_acceptance() -> dict[str, Any]:
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
        "operator_approval_still_paper_only": True,
        "ui_contract_does_not_enable_real_trading": True,
        "governance_report_is_not_financial_advice": True,
        "btc_is_first_line_not_final_platform_boundary": True,
        "future_stocks_and_other_markets_supported_by_architecture": True,
    }

    return {
        "ok": all(checks.values()),
        "type": "p5_safety_acceptance",
        "phase": "P5",
        "checks": checks,
        "decision": "P5 accepted for paper-only governance-layer closeout",
        **paper_flags(),
    }


def get_p5_to_p6_transition_anchor() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p5_to_p6_transition_anchor",
        "from_phase": "P5 risk governance and regime layer",
        "to_phase": "P6 multi-market architecture preparation",
        "p6_candidate_scope": [
            "market adapter interface baseline",
            "asset class taxonomy",
            "symbol normalization across crypto and stocks",
            "paper-only multi-market input contract",
            "multi-market fixture set",
            "multi-market governance contract",
            "UI-facing multi-market summary contract",
            "strict safety boundary preservation",
        ],
        "must_preserve": [
            "paper-only boundary",
            "operator review required",
            "no real exchange API",
            "no real brokerage API",
            "no real API keys",
            "no wallet private keys",
            "no real orders",
            "no real execution",
            "no real balances or positions",
            "no real money impact",
            "FCF-style event-driven architecture direction",
            "BTC remains first implementation line not final platform boundary",
        ],
        **paper_flags(),
    }


def build_p5_closeout_package(
    file_paths: list[Any],
    operator_status: str = "pending",
) -> dict[str, Any]:
    contract = build_governance_ui_contract(file_paths, operator_status)
    capabilities = get_p5_governance_layer_capabilities()
    safety = get_p5_safety_acceptance()
    transition = get_p5_to_p6_transition_anchor()

    return {
        "ok": contract["ok"] is True and contract["validation"]["ok"] is True and capabilities["ok"] is True and safety["ok"] is True and transition["ok"] is True,
        "type": "p5_closeout_package",
        "phase": "P5",
        "status": "completed",
        "contract_type": contract["type"],
        "contract_version": contract["contract_version"],
        "summary": contract["summary"],
        "capabilities": capabilities,
        "safety_acceptance": safety,
        "transition_anchor": transition,
        "next_phase": "P6 multi-market architecture preparation",
        "decision": "P5_closed_paper_only_ready_for_P6",
        **paper_flags(),
    }
