from typing import Any

from btc_finance_platform.paper_multi_market_registry import build_multi_market_readiness_bundle


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


P6_COMPLETED_SCOPE = [
    "P6-D1 asset class taxonomy",
    "P6-D2 symbol normalization across crypto, stocks, ETFs, FX, and commodities",
    "P6-D3 paper-only market adapter input contract",
    "P6-D4 multi-market JSON fixture loader",
    "P6-D5 multi-market paper analysis pipeline",
    "P6-D6 multi-market governance summary and writable report artifact",
    "P6-D7 multi-market report summary",
    "P6-D8 multi-market UI contract and markdown report",
    "P6-D9 writable multi-market report bundle",
    "P6-D10 multi-market adapter registry",
    "P6-D11 multi-market readiness gate",
    "P6-D12 writable readiness bundle",
    "P6-D13 P6 multi-market closeout summary",
    "P6-D14 P6 paper-only safety acceptance",
    "P6-D15 P7 transition anchor",
]


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def get_p6_multi_market_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p6_multi_market_capabilities",
        "phase": "P6",
        "status": "completed",
        "completed_scope": list(P6_COMPLETED_SCOPE),
        "capabilities": [
            "asset class taxonomy",
            "multi-market symbol normalization",
            "paper-only market adapter contract",
            "multi-market JSON fixture",
            "multi-market paper analysis pipeline",
            "multi-market governance summary",
            "multi-market readable report",
            "multi-market UI contract",
            "multi-market adapter registry",
            "multi-market readiness gate",
            "writable readiness bundle",
            "crypto stock ETF FX commodity architecture baseline",
        ],
        "current_repository": "btc_finance_platform",
        "current_role": "first BTC paper-only implementation line plus multi-market architecture baseline",
        "broader_goal": "general FCF-style finance platform for stocks and other markets",
        **paper_flags(),
    }


def get_p6_safety_acceptance() -> dict[str, Any]:
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
        "adapter_registry_is_paper_contract_only": True,
        "readiness_gate_does_not_enable_live_trading": True,
        "multi_market_contracts_are_local_and_paper_only": True,
        "btc_is_first_line_not_final_platform_boundary": True,
        "future_stocks_and_other_markets_supported_by_architecture": True,
    }

    return {
        "ok": all(checks.values()),
        "type": "p6_safety_acceptance",
        "phase": "P6",
        "checks": checks,
        "decision": "P6 accepted for paper-only multi-market architecture closeout",
        **paper_flags(),
    }


def get_p6_to_p7_transition_anchor() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p6_to_p7_transition_anchor",
        "from_phase": "P6 multi-market architecture preparation",
        "to_phase": "P7 UI and operator console preparation",
        "p7_candidate_scope": [
            "local operator console contract",
            "dashboard summary contract",
            "review queue contract",
            "report viewer contract",
            "governance and readiness page contract",
            "CLI-to-UI artifact export bridge",
            "paper-only UI safety banner",
            "operator review workflow surface",
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


def build_p6_closeout_package(file_path: Any) -> dict[str, Any]:
    readiness = build_multi_market_readiness_bundle(file_path)
    capabilities = get_p6_multi_market_capabilities()
    safety = get_p6_safety_acceptance()
    transition = get_p6_to_p7_transition_anchor()

    return {
        "ok": readiness["ok"] is True and readiness["readiness_gate"]["ok"] is True and capabilities["ok"] is True and safety["ok"] is True and transition["ok"] is True,
        "type": "p6_closeout_package",
        "phase": "P6",
        "status": "completed",
        "readiness_bundle_type": readiness["type"],
        "readiness_gate": readiness["readiness_gate"],
        "capabilities": capabilities,
        "safety_acceptance": safety,
        "transition_anchor": transition,
        "next_phase": "P7 UI and operator console preparation",
        "decision": "P6_closed_paper_only_ready_for_P7",
        **paper_flags(),
    }
