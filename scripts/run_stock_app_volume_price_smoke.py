import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.volume_price_anomaly import build_volume_price_anomaly_package


def sample_records():
    return [
        {
            "symbol": "600000",
            "name": "Sample Strong",
            "close": 10.8,
            "prev_close": 10.0,
            "high": 10.85,
            "low": 9.9,
            "limit_up_price": 11.0,
            "volume": 3000000,
            "avg_volume_5d": 1000000,
            "turnover_rate": 8.0,
            "avg_turnover_5d": 3.0,
            "high_20d": 10.7,
            "data_quality_state": "PASS_STRICT",
        },
        {
            "symbol": "000001",
            "name": "Sample Limited",
            "close": 10.5,
            "prev_close": 10.0,
            "high": 10.55,
            "low": 9.9,
            "limit_up_price": 11.0,
            "volume": 1800000,
            "avg_volume_5d": 1000000,
            "turnover_rate": 4.0,
            "avg_turnover_5d": 3.0,
            "high_20d": 10.4,
            "data_quality_state": "PASS_LIMITED",
        },
        {
            "symbol": "300000",
            "name": "Sample Weak",
            "close": 10.1,
            "prev_close": 10.0,
            "high": 10.2,
            "low": 9.9,
            "limit_up_price": 11.0,
            "volume": 900000,
            "avg_volume_5d": 1000000,
            "turnover_rate": 2.0,
            "avg_turnover_5d": 2.0,
            "high_20d": 11.0,
            "data_quality_state": "PASS_STRICT",
        },
    ]


if __name__ == "__main__":
    result = build_volume_price_anomaly_package(sample_records())
    print(json.dumps(result, indent=2, sort_keys=True))
