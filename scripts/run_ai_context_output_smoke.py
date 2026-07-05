import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ai_context.contracts.explanation_output import build_operator_review_summary
from ai_context.contracts.explanation_output import build_structured_explanation_output
from ai_context.contracts.explanation_output import build_ui_workflow_handoff
from ai_context.contracts.explanation_output import write_ai_context_output


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
                "score_breakdown": {"final_score": 82},
                "reason_codes": ["BASE_FILTER_PASS", "SECTOR_ACTIVE"],
                "risk_flags": ["OPERATOR_REVIEW_REQUIRED"],
                "data_quality_state": "PASS_STRICT",
                "confidence_level": "HIGH",
                "data_sources": ["ranked_watchlist"],
                "operator_review_required": True,
            }
        ],
    }


if __name__ == "__main__":
    contract = sample_stock_app_contract()
    structured = build_structured_explanation_output(contract)
    summary = build_operator_review_summary(structured)
    handoff = build_ui_workflow_handoff(structured)
    written = write_ai_context_output(contract, Path(ROOT) / "runtime" / "ai_context" / "ai_context_output_smoke.json")
    print(json.dumps({
        "status": "completed",
        "structured": structured,
        "summary": summary,
        "handoff": handoff,
        "written_ok": written["ok"],
    }, indent=2, sort_keys=True))
