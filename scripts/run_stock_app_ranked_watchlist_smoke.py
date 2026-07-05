import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.ranked_watchlist import build_candidate_report
from stock_app.contracts.ranked_watchlist import write_candidate_report


def sample_records():
    base = {
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
    }
    high = dict(base, symbol="600000", name="Sample High")
    watch = dict(base, symbol="000001", name="Sample Watch", data_quality_state="PASS_LIMITED")
    reject = dict(base, symbol="300000", name="Sample Reject", trading_status="SUSPENDED")
    return [watch, reject, high]


if __name__ == "__main__":
    records = sample_records()
    report = build_candidate_report(records, trade_date="2026-07-05", source_manifest_id="demo-manifest")
    output = Path(ROOT) / "runtime" / "stock_app" / "candidate_report_demo.json"
    written = write_candidate_report(records, output, trade_date="2026-07-05", source_manifest_id="demo-manifest")
    print(json.dumps({"report": report, "written": written}, indent=2, sort_keys=True))
