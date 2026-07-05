"""DATA-APP-D1 sidecar boundary contract.

This module defines the read-only DATA-APP sidecar boundary.
It does not import core modules and it does not perform trading actions.
"""

from __future__ import annotations

from typing import Any


ALLOWED_INPUT_TYPES = (
    "csv",
    "excel",
    "json",
    "local_database",
    "public_read_only_data",
)

FORBIDDEN_CAPABILITIES = (
    "real_exchange_api",
    "real_brokerage_api",
    "api_key_storage",
    "wallet_private_key_access",
    "real_order_creation",
    "real_execution",
    "real_balance_read",
    "real_position_read",
    "real_money_impact",
    "auto_trading",
)


def build_data_app_sidecar_boundary() -> dict[str, Any]:
    return {
        "app": "DATA-APP",
        "contract_version": "DATA_APP_SIDECAR_D1",
        "layer": "sidecar",
        "purpose": "read_only_data_ingestion_boundary",
        "core_freeze_respected": True,
        "p48_core_expansion": False,
        "core_import_allowed": False,
        "core_mutation_allowed": False,
        "core_audit_write_allowed": False,
        "can_call_stable_core_contracts": True,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "api_key_required": False,
        "wallet_private_key_required": False,
        "real_order_allowed": False,
        "real_execution_allowed": False,
        "real_balance_allowed": False,
        "real_position_allowed": False,
        "real_money_impact_allowed": False,
        "trading_app_enabled": False,
        "operator_review_required": True,
        "allowed_input_types": list(ALLOWED_INPUT_TYPES),
        "forbidden_capabilities": list(FORBIDDEN_CAPABILITIES),
        "next_layer": "STOCK-APP",
    }


def validate_data_app_sidecar_boundary(
    boundary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item = build_data_app_sidecar_boundary() if boundary is None else boundary
    checks = {
        "app_is_data_app": item.get("app") == "DATA-APP",
        "is_sidecar_layer": item.get("layer") == "sidecar",
        "core_freeze_respected": item.get("core_freeze_respected") is True,
        "no_p48_core_expansion": item.get("p48_core_expansion") is False,
        "no_core_import": item.get("core_import_allowed") is False,
        "no_core_mutation": item.get("core_mutation_allowed") is False,
        "no_core_audit_write": item.get("core_audit_write_allowed") is False,
        "paper_only": item.get("paper_only") is True,
        "local_only": item.get("local_only") is True,
        "read_only": item.get("read_only") is True,
        "no_real_exchange_api": item.get("real_exchange_api") is False,
        "no_real_brokerage_api": item.get("real_brokerage_api") is False,
        "no_api_key_required": item.get("api_key_required") is False,
        "no_wallet_private_key_required": item.get("wallet_private_key_required") is False,
        "no_real_order": item.get("real_order_allowed") is False,
        "no_real_execution": item.get("real_execution_allowed") is False,
        "no_real_balance": item.get("real_balance_allowed") is False,
        "no_real_position": item.get("real_position_allowed") is False,
        "no_real_money_impact": item.get("real_money_impact_allowed") is False,
        "trading_app_disabled": item.get("trading_app_enabled") is False,
        "operator_review_required": item.get("operator_review_required") is True,
    }
    return {
        "ok": all(checks.values()),
        "app": item.get("app"),
        "contract_version": item.get("contract_version"),
        "checks": checks,
        "allowed_input_types": list(item.get("allowed_input_types", [])),
        "forbidden_capabilities": list(item.get("forbidden_capabilities", [])),
    }
