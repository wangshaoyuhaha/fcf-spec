import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.paper_multi_market import get_asset_class_taxonomy
from btc_finance_platform.paper_multi_market_report import build_multi_market_ui_contract


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


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def build_multi_market_adapter_registry() -> dict[str, Any]:
    taxonomy = get_asset_class_taxonomy()
    registry = {}

    for asset_class in taxonomy["supported_asset_classes"]:
        item = taxonomy["taxonomy"][asset_class]
        registry[asset_class] = {
            "asset_class": asset_class,
            "label": item["label"],
            "adapter_type": item["adapter_type"],
            "adapter_status": "paper_contract_only",
            "real_connection_enabled": False,
            "real_brokerage_enabled": False,
            "real_exchange_enabled": False,
            "allowed_data_mode": "local_fixture_or_paper_contract_only",
            "blocked_actions": [
                "real_exchange_api",
                "real_brokerage_api",
                "real_api_key",
                "wallet_private_key",
                "real_order",
                "real_execution",
                "real_balance",
                "real_position",
                "real_money_impact",
            ],
        }

    return {
        "ok": True,
        "type": "multi_market_adapter_registry",
        "registry_version": "p6_d10_adapter_registry_v1",
        "asset_classes": sorted(registry.keys()),
        "registry": registry,
        "decision": "adapter_registry_paper_only",
        **paper_flags(),
    }


def build_multi_market_readiness_gate(file_path: Any) -> dict[str, Any]:
    contract = build_multi_market_ui_contract(file_path)
    registry = build_multi_market_adapter_registry()

    checks = {
        "contract_ok": contract["ok"] is True,
        "contract_validation_ok": contract["validation"]["ok"] is True,
        "registry_ok": registry["ok"] is True,
        "has_cards": contract["count"] > 0,
        "all_asset_classes_registered": all(
            card["asset_class"] in registry["registry"] for card in contract["cards"]
        ),
        "paper_only_preserved": contract["paper_only"] is True,
        "operator_review_required": contract["operator_review_required"] is True,
        "no_real_exchange_api": contract["real_exchange_api"] is False,
        "no_real_brokerage_api": contract["real_brokerage_api"] is False,
        "no_real_api_key_required": contract["real_api_key_required"] is False,
        "no_wallet_private_key_required": contract["wallet_private_key_required"] is False,
        "no_real_order": contract["real_order"] is False,
        "no_real_execution": contract["real_execution"] is False,
        "no_real_balance": contract["real_balance"] is False,
        "no_real_position": contract["real_position"] is False,
        "no_real_money_impact": contract["real_money_impact"] is False,
        "all_registry_entries_paper_only": all(
            item["adapter_status"] == "paper_contract_only"
            for item in registry["registry"].values()
        ),
        "no_registry_real_connections": all(
            item["real_connection_enabled"] is False
            for item in registry["registry"].values()
        ),
    }

    return {
        "ok": all(checks.values()),
        "type": "multi_market_readiness_gate",
        "gate": "pass" if all(checks.values()) else "fail",
        "contract_version": contract["contract_version"],
        "registry_version": registry["registry_version"],
        "count": contract["count"],
        "symbols": contract["symbols"],
        "asset_class_counts": contract["asset_class_counts"],
        "checks": checks,
        "decision": "multi_market_readiness_paper_only",
        **paper_flags(),
    }


def build_multi_market_readiness_bundle(file_path: Any) -> dict[str, Any]:
    contract = build_multi_market_ui_contract(file_path)
    registry = build_multi_market_adapter_registry()
    readiness_gate = build_multi_market_readiness_gate(file_path)

    return {
        "ok": contract["ok"] is True and registry["ok"] is True and readiness_gate["ok"] is True,
        "type": "multi_market_readiness_bundle",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": str(Path(file_path).name),
        "contract": contract,
        "adapter_registry": registry,
        "readiness_gate": readiness_gate,
        "next_step": "P6 closeout before any further expansion",
        "decision": "multi_market_readiness_bundle_paper_only",
        **paper_flags(),
    }


def write_multi_market_readiness_bundle(file_path: Any, output_dir: Any) -> dict[str, Any]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    bundle = build_multi_market_readiness_bundle(file_path)
    bundle_path = directory / "multi_market_readiness_bundle.json"
    registry_path = directory / "multi_market_adapter_registry.json"
    gate_path = directory / "multi_market_readiness_gate.json"

    bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
    registry_path.write_text(json.dumps(bundle["adapter_registry"], indent=2, sort_keys=True), encoding="utf-8")
    gate_path.write_text(json.dumps(bundle["readiness_gate"], indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "multi_market_readiness_bundle_written",
        "output_dir": str(directory),
        "bundle_file": str(bundle_path),
        "registry_file": str(registry_path),
        "gate_file": str(gate_path),
        "bundle": bundle,
        **paper_flags(),
    }
