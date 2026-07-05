from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sidecars" / "ui_app_1" / "final_handoff.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "ui_app_final_handoff",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ui_app_d6_final_handoff_file_exists():
    assert MODULE_PATH.exists()


def test_ui_app_d6_final_handoff_identity():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert handoff["app_id"] == "UI-APP-1"
    assert handoff["stage_id"] == "UI-APP-D6"
    assert handoff["status"] == "CLOSED_OUT"


def test_ui_app_d6_final_handoff_is_read_only_sidecar():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True


def test_ui_app_d6_final_handoff_blocks_real_actions():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert handoff["trade_action_enabled"] is False
    assert handoff["buy_button_enabled"] is False
    assert handoff["sell_button_enabled"] is False
    assert handoff["order_button_enabled"] is False
    assert handoff["broker_connection_allowed"] is False
    assert handoff["exchange_connection_allowed"] is False
    assert handoff["real_execution_allowed"] is False


def test_ui_app_d6_final_handoff_blocks_credentials_and_accounts():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert handoff["credential_storage_allowed"] is False
    assert handoff["wallet_private_key_access_allowed"] is False
    assert handoff["real_account_access_allowed"] is False
    assert handoff["real_position_access_allowed"] is False


def test_ui_app_d6_final_handoff_blocks_core_expansion():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert handoff["core_mutation_allowed"] is False
    assert handoff["p48_core_expansion_allowed"] is False


def test_ui_app_d6_final_handoff_release_boundary():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False


def test_ui_app_d6_final_handoff_completed_steps():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert len(handoff["completed_steps"]) == 6
    assert "UI-APP-D6 final workflow handoff closeout" in handoff["completed_steps"]


def test_ui_app_d6_final_handoff_upstreams():
    module = load_module()
    handoff = module.get_ui_app_d6_final_handoff()

    assert set(handoff["upstream_sidecars"]) == {
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
    }


def test_ui_app_d6_final_handoff_validation_passes():
    module = load_module()
    result = module.validate_ui_app_d6_final_handoff()

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["app_id"] == "UI-APP-1"
    assert result["stage_id"] == "UI-APP-D6"
    assert result["status"] == "CLOSED_OUT"
