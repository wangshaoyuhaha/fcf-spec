import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ai_context.contracts.explanation_contract import build_ai_context_report
from ai_context.contracts.explanation_contract import build_candidate_explanation
from ai_context.contracts.explanation_contract import explain_reason_code
from ai_context.contracts.explanation_contract import explain_risk_flag
from ai_context.contracts.explanation_contract import validate_no_ai_mutation


def sample_candidate():
    return {
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


def test_candidate_explanation_preserves_score_reason_codes_and_risk_flags():
    candidate = sample_candidate()
    result = build_candidate_explanation(candidate)
    assert result["limit_up_potential_score"] == candidate["limit_up_potential_score"]
    assert result["score_breakdown"] == candidate["score_breakdown"]
    assert result["reason_codes"] == candidate["reason_codes"]
    assert result["risk_flags"] == candidate["risk_flags"]
    assert result["operator_review_required"] is True


def test_candidate_explanation_blocks_trading_actions():
    result = build_candidate_explanation(sample_candidate())
    assert result["paper_only"] is True
    assert result["read_only"] is True
    assert result["buy_sell_instruction_allowed"] is False
    assert result["limit_up_guarantee_allowed"] is False
    assert result["real_trading_allowed"] is False
    assert result["real_action_blocked"] is True


def test_reason_and_risk_dictionary_known_and_unknown_codes():
    assert explain_reason_code("BASE_FILTER_PASS")["known"] is True
    assert explain_reason_code("UNKNOWN_CODE")["known"] is False
    assert explain_risk_flag("OPERATOR_REVIEW_REQUIRED")["known"] is True
    assert explain_risk_flag("UNKNOWN_RISK")["known"] is False


def test_ai_context_report_reads_stock_app_ranked_watchlist_contract():
    contract = {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_A_SHARE_V1",
        "market": "A_SHARE",
        "trade_date": "2026-07-05",
        "input_manifest_id": "manifest-demo",
        "ranked_watchlist": [sample_candidate()],
    }
    result = build_ai_context_report(contract)
    assert result["app"] == "AI-CONTEXT"
    assert result["source_app"] == "STOCK-APP"
    assert result["candidate_count"] == 1
    assert result["mutation_guard"]["ok"] is True
    assert result["operator_review_summary"]["operator_review_required"] is True


def test_validate_no_ai_mutation_detects_preserved_fields():
    candidate = sample_candidate()
    explanation = build_candidate_explanation(candidate)
    result = validate_no_ai_mutation(candidate, explanation)
    assert result["ok"] is True
    assert result["checks"]["score_preserved"] is True
    assert result["checks"]["reason_codes_preserved"] is True
    assert result["checks"]["risk_flags_preserved"] is True
