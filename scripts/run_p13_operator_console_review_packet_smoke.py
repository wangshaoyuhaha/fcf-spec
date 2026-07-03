import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_review_packet import write_operator_review_packet


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "index.html"
    packet = Path(ROOT) / "runtime" / "operator_console" / "operator_review_packet.json"

    result = write_operator_review_packet(output, packet)

    review_packet = result["packet"]

    if review_packet["review_status"] != "WAITING_FOR_OPERATOR_REVIEW":
        raise SystemExit("review packet must wait for operator review")

    if review_packet["safe_to_execute_real_money"] is not False:
        raise SystemExit("real money execution must remain false")

    if review_packet["trading_buttons_enabled"] is not False:
        raise SystemExit("trading buttons must remain disabled")

    if review_packet["operator_review_required"] is not True:
        raise SystemExit("operator review must remain required")

    print(json.dumps(result, indent=2, sort_keys=True))
