import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.fund_flow_proxy import build_public_fund_flow_proxy_package


def sample_records():
    return [
        {
            "symbol": "600000",
            "name": "Sample Strong",
            "dragon_tiger_signal": True,
            "northbound_flow_score": 80,
            "etf_flow_score": 70,
            "large_trade_proxy_score": 85,
            "amount_expansion_score": 75,
            "sector_fund_heat_score": 72,
            "data_quality_state": "PASS_STRICT",
        },
        {
            "symbol": "000001",
            "name": "Sample Limited",
            "dragon_tiger_signal": "positive",
            "northbound_flow_score": 65,
            "etf_flow_score": 50,
            "large_trade_proxy_score": 64,
            "amount_expansion_score": 40,
            "sector_fund_heat_score": 58,
            "data_quality_state": "PASS_LIMITED",
        },
        {
            "symbol": "300000",
            "name": "Sample Weak",
            "dragon_tiger_signal": False,
            "northbound_flow_score": 0,
            "etf_flow_score": 0,
            "large_trade_proxy_score": 5,
            "amount_expansion_score": 0,
            "sector_fund_heat_score": 10,
            "data_quality_state": "PASS_STRICT",
        },
    ]


if __name__ == "__main__":
    result = build_public_fund_flow_proxy_package(sample_records())
    print(json.dumps(result, indent=2, sort_keys=True))
