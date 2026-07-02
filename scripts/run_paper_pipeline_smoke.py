import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_pipeline import (
    assert_paper_pipeline_result,
    run_paper_pipeline,
)


if __name__ == "__main__":
    result = run_paper_pipeline("BTCUSDT", 65000.0)
    assert_paper_pipeline_result(result)
    print(json.dumps(result, indent=2, sort_keys=True))
