import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_analysis import analyze_paper_market, assert_paper_market_analysis
from btc_finance_platform.paper_input import validate_paper_input
from btc_finance_platform.report_renderer import render_paper_report


if __name__ == "__main__":
    validated = validate_paper_input({
        "symbol": "BTCUSDT",
        "price": 65000,
        "reference_price": 64000,
    })
    analysis = analyze_paper_market(validated)
    assert_paper_market_analysis(analysis)
    report = render_paper_report(analysis)

    print(json.dumps({
        "validated": validated,
        "analysis": analysis,
        "report": report,
    }, indent=2, sort_keys=True))
