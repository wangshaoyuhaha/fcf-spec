import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.boundary import ALLOWED_INPUT_TYPES
from data_app.boundary import FORBIDDEN_CAPABILITIES
from data_app.boundary import build_data_app_sidecar_boundary
from data_app.boundary import validate_data_app_sidecar_boundary


def test_data_app_boundary_preserves_core_freeze():
    result = build_data_app_sidecar_boundary()

    assert result["layer"] == "sidecar"
    assert result["core_freeze_respected"] is True
    assert result["p48_core_expansion"] is False
    assert result["core_import_allowed"] is False
    assert result["core_mutation_allowed"] is False
    assert result["core_audit_write_allowed"] is False


def test_data_app_boundary_blocks_real_world_actions():
    result = build_data_app_sidecar_boundary()

    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order_allowed"] is False
    assert result["real_execution_allowed"] is False
    assert result["real_balance_allowed"] is False
    assert result["real_position_allowed"] is False
    assert result["real_money_impact_allowed"] is False
    assert result["trading_app_enabled"] is False
    assert result["operator_review_required"] is True


def test_validate_data_app_sidecar_boundary_passes():
    result = validate_data_app_sidecar_boundary()

    assert result["ok"] is True
    assert result["app"] == "DATA-APP"
    assert result["contract_version"] == "DATA_APP_SIDECAR_D1"
    assert all(result["checks"].values())


def test_data_app_boundary_declares_inputs_and_forbidden_capabilities():
    result = build_data_app_sidecar_boundary()

    assert "csv" in ALLOWED_INPUT_TYPES
    assert "excel" in ALLOWED_INPUT_TYPES
    assert "public_read_only_data" in ALLOWED_INPUT_TYPES
    assert "real_exchange_api" in FORBIDDEN_CAPABILITIES
    assert "real_execution" in FORBIDDEN_CAPABILITIES
    assert result["next_layer"] == "STOCK-APP"
    assert result["allowed_input_types"] == list(ALLOWED_INPUT_TYPES)
    assert result["forbidden_capabilities"] == list(FORBIDDEN_CAPABILITIES)
