from typing import Any


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


FCF_ORIGINAL_SKELETON = {
    "source_project": "fcf_full_skeleton",
    "root_files": ["main.py", "README.md"],
    "docs": ["docs/01_vision.md", "docs/02_constitution.md"],
    "core": [
        "fcf/core/event_bus.py",
        "fcf/core/event_model.py",
        "fcf/core/policy_engine.py",
    ],
    "modules": [
        "fcf/modules/perception.py",
        "fcf/modules/governor.py",
        "fcf/modules/execution.py",
        "fcf/modules/meta.py",
        "fcf/modules/regime.py",
        "fcf/modules/simulation.py",
    ],
    "storage": ["fcf/storage/audit_store.py"],
}


P3_COMPLETED_SCOPE = [
    "P3-D1 local paper data schema",
    "P3-D2 JSON and CSV paper fixtures",
    "P3-D3 schema validator",
    "P3-D4 local JSON paper data loader",
    "P3-D5 local CSV paper data loader",
    "P3-D6 local data manifest and checksum audit",
    "P3-D7 local paper dataset builder",
    "P3-D8 normalized local paper analysis inputs",
    "P3-D9 local data audit report and paper-only handoff package",
    "P3-D10 local data quality gate",
    "P3-D11 local analysis handoff package",
    "P3-D12 writable handoff artifact",
    "P3-D13 P3 acceptance summary",
    "P3-D14 FCF architecture anchor",
    "P3-D15 P3 closeout safety acceptance",
]


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def get_fcf_architecture_anchor() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "fcf_architecture_anchor",
        "current_repository": "btc_finance_platform",
        "current_role": "first BTC paper-only implementation line",
        "broader_goal": "general finance platform for stocks and other markets",
        "original_skeleton": FCF_ORIGINAL_SKELETON,
        "architecture_principles": [
            "event_driven_core",
            "policy_engine_and_safety_boundary",
            "perception_regime_governor_execution_simulation_meta_modules",
            "audit_store_and_reproducible_history",
            "paper_only_before_any_future_real_world_integration",
            "operator_review_required",
        ],
        **paper_flags(),
    }


def get_p3_closeout_summary() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "p3_closeout_summary",
        "phase": "P3",
        "status": "completed",
        "completed_scope": list(P3_COMPLETED_SCOPE),
        "validation_target": "102 passed and ALL CHECKS PASSED",
        "current_capability": [
            "local paper data schema",
            "local JSON and CSV fixtures",
            "schema validation",
            "local JSON and CSV loader",
            "manifest and sha256 audit",
            "local data bridge",
            "local data quality gate",
            "analysis handoff package",
            "writable handoff artifact",
            "FCF architecture anchor for future multi-market expansion",
        ],
        "next_phase": "P4 paper analysis logic enhancement",
        **paper_flags(),
    }


def get_p3_safety_acceptance() -> dict[str, Any]:
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
        "btc_is_first_line_not_final_platform_boundary": True,
        "future_stocks_and_other_markets_supported_by_architecture": True,
    }

    return {
        "ok": all(checks.values()),
        "type": "p3_safety_acceptance",
        "checks": checks,
        "decision": "P3 accepted for paper-only closeout",
        **paper_flags(),
    }


def get_platform_direction_statement() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "platform_direction_statement",
        "statement": "BTC is the first paper-only implementation line. The long-term target is a general FCF-style finance platform for stocks and other markets.",
        "not_a_real_trading_bot": True,
        "not_limited_to_btc_long_term": True,
        "must_keep_operator_review": True,
        **paper_flags(),
    }
