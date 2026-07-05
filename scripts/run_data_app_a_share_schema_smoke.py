import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.a_share_schema import build_a_share_schema_contract
from data_app.a_share_schema import validate_a_share_schema_row


if __name__ == "__main__":
    sample = {
        "date": "2026-07-05",
        "symbol": "000001.SZ",
        "name": "SAMPLE",
        "open": 10.0,
        "high": 10.5,
        "low": 9.8,
        "close": 10.2,
        "prev_close": 10.0,
        "volume": 1000000,
        "amount": 10200000,
        "turnover_rate": 2.5,
        "float_market_cap": 1000000000,
        "total_market_cap": 1200000000,
        "listing_days": 1000,
        "is_st": False,
        "limit_up_price": 11.0,
        "limit_down_price": 9.0,
        "sector_code": "BK_SAMPLE",
        "sector_name": "Sample Sector",
        "trading_status": "trading",
    }
    print(json.dumps({
        "status": "completed",
        "runner": "data_app_a_share_schema_smoke",
        "contract": build_a_share_schema_contract(),
        "validation": validate_a_share_schema_row(sample),
    }, indent=2, sort_keys=True))
