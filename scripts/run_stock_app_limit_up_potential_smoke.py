import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.limit_up_potential import build_limit_up_potential_package


def sample_records():
    return [
        {
            "symbol": "600000",
            "name": "Sample High",
            "trading_status": "TRADING",
            "is_st": False,
            "listing_days": 5000,
            "turnover_rate": 8.0,
            "amount": 180000000,
            "open": 10.0,
            "high": 10.85,
            "low": 9.9,
            "close": 10.8,
            "prev_close": 10.0,
            "limit_up_price": 11.0,
            "volume": 3000000,
            "avg_volume_5d": 1000000,
            "avg_turnover_5d": 3.0,
            "high_20d": 10.7,
            "sector_code": "BK001",
            "sector_name": "AI Computing",
            "theme_tags": ["AI", "Computing"],
            "sector_strength_score": 88,
            "theme_heat_score": 82,
            "market_breadth_score": 76,
            "dragon_tiger_signal": True,
            "northbound_flow_score": 80,
            "etf_flow_score": 70,
            "large_trade_proxy_score": 85,
            "amount_expansion_score": 75,
            "sector_fund_heat_score": 72,
            "data_quality_state": "PASS_STRICT",
            "data_sources": ["DATA-APP", "PUBLIC_FIXTURE"],
        },
        {
            "symbol": "000001",
            "name": "Sample Watch",
            "trading_status": "TRADING",
            "is_st": False,
            "listing_days": 3000,
            "turnover_rate": 5.0,
            "amount": 90000000,
            "open": 10.0,
            "high": 10.5,
            "low": 9.9,
            "close": 10.4,
            "prev_close": 10.0,
            "limit_up_price": 11.0,
            "volume": 1600000,
            "avg_volume_5d": 1000000,
            "avg_turnover_5d": 3.0,
            "high_20d": 10.4,
            "sector_code": "BK002",
            "sector_name": "Brokerage",
            "theme_tags": "finance,brokerage",
            "sector_strength_score": 70,
            "theme_heat_score": 65,
            "market_breadth_score": 60,
            "dragon_tiger_signal": "positive",
            "northbound_flow_score": 60,
            "etf_flow_score": 45,
            "large_trade_proxy_score": 60,
            "amount_expansion_score": 45,
            "sector_fund_heat_score": 50,
            "data_quality_state": "PASS_LIMITED",
        },
    ]


if __name__ == "__main__":
    result = build_limit_up_potential_package(sample_records())
    print(json.dumps(result, indent=2, sort_keys=True))
