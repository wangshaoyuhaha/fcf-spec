import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.integrated_report import render_integrated_report
from btc_finance_platform.paper_analysis import analyze_paper_market
from btc_finance_platform.paper_input import validate_paper_input
from btc_finance_platform.risk_score import score_paper_risk
from btc_finance_platform.strategy_draft import create_strategy_draft


if __name__ == "__main__":
    validated = validate_paper_input({
        "symbol": "BTCUSDT",
        "price": 65000,
        "reference_price": 64000,
    })
    analysis = analyze_paper_market(validated)
    risk = score_paper_risk(analysis)
    strategy = create_strategy_draft(analysis, risk)
    report = render_integrated_report(analysis, risk, strategy)

    print(json.dumps({
        "analysis": analysis,
        "risk": risk,
        "strategy": strategy,
        "report": report,
    }, indent=2, sort_keys=True))
