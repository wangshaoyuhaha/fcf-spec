import json
import os
import sys

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


def test_structured_output_preserves_read_only_boundary():
    result = build_structured_explanation_output(sample_stock_app_contract())
    assert result["app"] == "AI-CONTEXT"
    assert result["contract_version"] == "AI_CONTEXT_OUTPUT_V1"
    assert result["candidate_count"] == 1
    assert result["read_only"] is True
    assert result["real_trading_allowed"] is False


def test_structured_output_preserves_candidate_score_and_flags():
    result = build_structured_explanation_output(sample_stock_app_contract())
    item = result["explanations"][0]
    assert item["limit_up_potential_score"] == 82
    assert item["reason_codes"] == ["BASE_FILTER_PASS", "SECTOR_ACTIVE"]
    assert item["risk_flags"] == ["OPERATOR_REVIEW_REQUIRED"]


def test_operator_review_summary_blocks_forbidden_next_steps():
    structured = build_structured_explanation_output(sample_stock_app_contract())
    result = build_operator_review_summary(structured)
    assert result["operator_review_required"] is True
    assert result["high_potential_count"] == 1
    assert "real_trade_execution" in result["blocked_next_steps"]
    assert "auto_buy_sell_recommendation" in result["blocked_next_steps"]


def test_ui_workflow_handoff_is_read_only():
    structured = build_structured_explanation_output(sample_stock_app_contract())
    result = build_ui_workflow_handoff(structured)
    assert result["handoff_ready"] is True
    assert result["target"] == "UI-APP-1"
    assert "view_reason_codes" in result["ui_allowed_actions"]
    assert "buy" in result["ui_forbidden_actions"]
    assert result["real_action_blocked"] is True


def test_write_ai_context_output_creates_json_file(tmp_path):
    output = tmp_path / "ai_context_output.json"
    result = write_ai_context_output(sample_stock_app_contract(), output)
    assert result["ok"] is True
    assert output.exists()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["structured_output"]["app"] == "AI-CONTEXT"
    assert saved["operator_review_summary"]["operator_review_required"] is True
