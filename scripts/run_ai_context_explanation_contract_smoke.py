import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ai_context.contracts.explanation_contract import build_ai_context_report


def sample_stock_app_contract():
    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_A_SHARE_V1",
        "market": "A_SHARE",
        "trade_date": "2026-07-05",
        "input_manifest_id": "manifest-demo",
        "ranked_watchlist": [
            {
                "symbol": "000001.SZ",
                "name": "Sample Bank",
                "rank": 1,
                "limit_up_potential_score": 82,
                "potential_level": "HIGH_POTENTIAL",
                "score_breakdown": {
                    "data_quality_score": 20,
                    "base_filter_score": 15,
                    "sector_theme_score": 12,
                    "volume_price_score": 20,
                    "fund_flow_proxy_score": 15,
                    "risk_penalty": 0,
                    "final_score": 82,
                },
                "reason_codes": ["BASE_FILTER_PASS", "SECTOR_ACTIVE", "VOLUME_EXPANSION"],
                "risk_flags": ["OPERATOR_REVIEW_REQUIRED"],
                "data_quality_state": "PASS_STRICT",
                "confidence_level": "HIGH",
                "data_sources": ["clean_universe", "ranked_watchlist"],
                "operator_review_required": True,
            }
        ],
    }


if __name__ == "__main__":
    report = build_ai_context_report(sample_stock_app_contract())
    print(json.dumps(report, indent=2, sort_keys=True))
