import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_multi_market import build_multi_market_batch_contract
from btc_finance_platform.paper_multi_market import build_multi_market_paper_input
from btc_finance_platform.paper_multi_market import build_paper_market_adapter_contract
from btc_finance_platform.paper_multi_market import extract_analysis_compatible_items
from btc_finance_platform.paper_multi_market import get_asset_class_taxonomy
from btc_finance_platform.paper_multi_market import normalize_symbol_for_asset_class
from btc_finance_platform.paper_multi_market import validate_asset_class


MULTI_MARKET_FIXTURE = Path(ROOT) / "fixtures" / "sample_multi_market_batch.json"


def load_fixture_items():
    return json.loads(MULTI_MARKET_FIXTURE.read_text(encoding="utf-8-sig"))


def test_asset_class_taxonomy_contains_crypto_stock_and_etf():
    result = get_asset_class_taxonomy()

    assert result["ok"] is True
    assert result["type"] == "asset_class_taxonomy"
    assert "crypto" in result["supported_asset_classes"]
    assert "stock" in result["supported_asset_classes"]
    assert "etf" in result["supported_asset_classes"]


def test_validate_asset_class_rejects_unknown_asset_class():
    with pytest.raises(ValueError, match="unsupported asset_class"):
        validate_asset_class("live_magic_market")


def test_normalize_crypto_symbol_removes_separators():
    result = normalize_symbol_for_asset_class("btc/usdt", "crypto")

    assert result["ok"] is True
    assert result["symbol"] == "BTCUSDT"
    assert result["asset_class"] == "crypto"


def test_normalize_stock_symbol_uppercases_symbol():
    result = normalize_symbol_for_asset_class("aapl", "stock")

    assert result["ok"] is True
    assert result["symbol"] == "AAPL"
    assert result["asset_class"] == "stock"


def test_paper_market_adapter_contract_blocks_real_integrations():
    result = build_paper_market_adapter_contract("stock", "paper us equity")

    assert result["ok"] is True
    assert result["asset_class"] == "stock"
    assert result["market"] == "paper_us_equity"
    assert "real_brokerage_api" in result["blocked_real_world_integrations"]
    assert "real_order" in result["blocked_real_world_integrations"]


def test_multi_market_paper_input_preserves_safety_flags():
    result = build_multi_market_paper_input("BTC/USDT", "crypto", "paper binance", 65000, 64000)

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_build_multi_market_batch_contract_from_fixture():
    result = build_multi_market_batch_contract(load_fixture_items())

    assert result["ok"] is True
    assert result["type"] == "multi_market_batch_contract"
    assert result["count"] == 3
    assert result["symbols"] == ["BTCUSDT", "AAPL", "SPY"]
    assert result["asset_class_counts"]["crypto"] == 1
    assert result["asset_class_counts"]["stock"] == 1
    assert result["asset_class_counts"]["etf"] == 1


def test_extract_analysis_compatible_items_from_multi_market_contract():
    contract = build_multi_market_batch_contract(load_fixture_items())
    result = extract_analysis_compatible_items(contract)

    assert len(result) == 3
    assert result[0] == {
        "symbol": "BTCUSDT",
        "price": 65000.0,
        "reference_price": 64000.0,
    }
    assert set(result[1].keys()) == {"symbol", "price", "reference_price"}


def test_extract_analysis_compatible_items_rejects_bad_contract_type():
    with pytest.raises(ValueError, match="batch_contract type is invalid"):
        extract_analysis_compatible_items({"ok": True, "type": "bad"})
