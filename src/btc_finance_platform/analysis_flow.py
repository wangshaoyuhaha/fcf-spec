from typing import Any

from btc_finance_platform.integrated_report import render_integrated_report
from btc_finance_platform.paper_analysis import analyze_paper_market, assert_paper_market_analysis
from btc_finance_platform.paper_input import validate_paper_input
from btc_finance_platform.paper_run_record import create_paper_run_record, assert_paper_run_record
from btc_finance_platform.risk_score import score_paper_risk
from btc_finance_platform.strategy_draft import create_strategy_draft


def run_paper_analysis_flow(payload: dict[str, Any]) -> dict[str, Any]:
    validated = validate_paper_input(payload)
    analysis = analyze_paper_market(validated)
    assert_paper_market_analysis(analysis)

    risk = score_paper_risk(analysis)
    strategy = create_strategy_draft(analysis, risk)
    report = render_integrated_report(analysis, risk, strategy)
    record = create_paper_run_record(analysis, risk, strategy, report)
    assert_paper_run_record(record)

    return {
        "ok": True,
        "type": "paper_analysis_flow_result",
        "validated": validated,
        "analysis": analysis,
        "risk": risk,
        "strategy": strategy,
        "report": report,
        "record": record,
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }
