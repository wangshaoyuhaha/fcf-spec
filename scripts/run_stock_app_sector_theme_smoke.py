import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from stock_app.contracts.sector_theme_linkage import build_sector_theme_linkage_package


def sample_records():
    return [
        {
            "symbol": "600000",
            "name": "Sample Strong",
            "sector_code": "BK001",
            "sector_name": "AI Computing",
            "theme_tags": ["AI", "Computing"],
            "sector_strength_score": 88,
            "theme_heat_score": 82,
            "market_breadth_score": 76,
            "data_quality_state": "PASS_STRICT",
        },
        {
            "symbol": "000001",
            "name": "Sample Limited",
            "sector_code": "BK002",
            "sector_name": "Brokerage",
            "theme_tags": "finance,brokerage",
            "sector_strength_score": 72,
            "theme_heat_score": 70,
            "market_breadth_score": 62,
            "data_quality_state": "PASS_LIMITED",
        },
        {
            "symbol": "300000",
            "name": "Sample Weak",
            "sector_code": "",
            "sector_name": "",
            "theme_tags": [],
            "sector_strength_score": 10,
            "theme_heat_score": 5,
            "market_breadth_score": 10,
            "data_quality_state": "PASS_STRICT",
        },
    ]


if __name__ == "__main__":
    result = build_sector_theme_linkage_package(sample_records())
    print(json.dumps(result, indent=2, sort_keys=True))
