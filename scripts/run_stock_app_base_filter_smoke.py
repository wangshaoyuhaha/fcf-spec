import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.base_candidate_filter import build_base_candidate_pool


def sample_records():
    return [
        {
            "symbol": "600000",
            "name": "Sample Bank",
            "trading_status": "TRADING",
            "is_st": False,
            "listing_days": 5000,
            "turnover_rate": 2.5,
            "amount": 120000000,
            "close": 10.5,
            "limit_up_price": 11.55,
            "data_quality_state": "PASS_STRICT",
        },
        {
            "symbol": "000001",
            "name": "Sample Watch",
            "trading_status": "TRADING",
            "is_st": False,
            "listing_days": 3000,
            "turnover_rate": 1.2,
            "amount": 80000000,
            "close": 12.0,
            "limit_up_price": 13.2,
            "data_quality_state": "PASS_LIMITED",
        },
        {
            "symbol": "300000",
            "name": "Sample Bad",
            "trading_status": "SUSPENDED",
            "is_st": True,
            "listing_days": 20,
            "turnover_rate": 0,
            "amount": 0,
            "close": 0,
            "limit_up_price": 0,
            "data_quality_state": "FAIL_QUARANTINE",
        },
    ]


if __name__ == "__main__":
    result = build_base_candidate_pool(sample_records())
    print(json.dumps(result, indent=2, sort_keys=True))
