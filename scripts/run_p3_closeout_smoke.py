import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.platform_closeout import get_fcf_architecture_anchor
from btc_finance_platform.platform_closeout import get_p3_closeout_summary
from btc_finance_platform.platform_closeout import get_p3_safety_acceptance
from btc_finance_platform.platform_closeout import get_platform_direction_statement


if __name__ == "__main__":
    result = {
        "architecture_anchor": get_fcf_architecture_anchor(),
        "p3_closeout_summary": get_p3_closeout_summary(),
        "p3_safety_acceptance": get_p3_safety_acceptance(),
        "platform_direction": get_platform_direction_statement(),
    }

    print(json.dumps(result, indent=2, sort_keys=True))
