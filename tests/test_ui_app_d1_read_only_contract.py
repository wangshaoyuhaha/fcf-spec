from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sidecars" / "ui_app_1" / "read_only_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "ui_app_read_only_contract",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ui_app_d1_contract_file_exists():
    assert MODULE_PATH.exists()


def test_ui_app_d1_contract_identity():
    module = load_module()
    contract = module.get_read_only_ui_contract()

    assert contract["app_id"] == "UI-APP-1"
    assert contract["stage_id"] == "UI-APP-D1"
    assert contract["layer_type"] == "sidecar_ui_view"


def test_ui_app_d1_contract_is_read_only_sidecar():
    module = load_module()
    contract = module.get_read_only_ui_contract()

    assert contract["paper_only"] is True
    assert contract["local_only"] is True
    assert contract["read_only"] is True
    assert contract["sidecar_only"] is True


def test_ui_app_d1_contract_blocks_core_changes():
    module = load_module()
    contract = module.get_read_only_ui_contract()

    assert contract["core_imports_allowed"] is False
    assert contract["core_mutation_allowed"] is False
    assert contract["p48_core_expansion_allowed"] is False


def test_ui_app_d1_contract_requires_operator_review():
    module = load_module()
    contract = module.get_read_only_ui_contract()

    assert contract["operator_review_required"] is True
    assert contract["operator_review_bypass_allowed"] is False


def test_ui_app_d1_contract_has_expected_upstreams():
    module = load_module()
    contract = module.get_read_only_ui_contract()

    assert set(contract["upstream_sidecars"]) == {
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
    }


def test_ui_app_d1_contract_contains_required_panels():
    module = load_module()
    contract = module.get_read_only_ui_contract()

    required_panels = set(contract["required_panels"])
    assert "candidate_pool_panel" in required_panels
    assert "ranked_watchlist_panel" in required_panels
    assert "score_breakdown_panel" in required_panels
    assert "reason_codes_panel" in required_panels
    assert "risk_flags_panel" in required_panels
    assert "operator_review_summary_panel" in required_panels


def test_ui_app_d1_contract_blocks_real_world_capabilities():
    module = load_module()
    contract = module.get_read_only_ui_contract()

    assert contract["network_connectors_allowed"] is False
    assert contract["credential_storage_allowed"] is False
    assert contract["private_secret_access_allowed"] is False
    assert contract["real_account_access_allowed"] is False
    assert contract["real_position_access_allowed"] is False
    assert contract["real_execution_allowed"] is False
    assert contract["action_buttons_allowed"] is False


def test_ui_app_d1_contract_validation_passes():
    module = load_module()
    result = module.validate_read_only_ui_contract()

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["app_id"] == "UI-APP-1"
    assert result["stage_id"] == "UI-APP-D1"
    assert result["read_only"] is True
    assert result["operator_review_required"] is True
