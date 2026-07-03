import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p14_final_operator_acceptance_packet import default_operator_acceptance_items
from btc_finance_platform.p14_final_operator_acceptance_packet import write_final_operator_acceptance_packet


if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "learning_engine" / "p14_final_operator_acceptance_packet.json"

    result = write_final_operator_acceptance_packet(
        source_branch="p13-operator-console",
        target_branch="main",
        acceptance_items=default_operator_acceptance_items(),
        validation_passed_count=583,
        path=output,
    )

    packet = result["packet"]

    if packet["acceptance_status"] != "READY_FOR_FINAL_OPERATOR_ACCEPTANCE":
        raise SystemExit("final acceptance packet must be ready only for operator acceptance")

    if packet["acceptance_policy"]["merge_auto_execute_allowed"] is not False:
        raise SystemExit("merge auto execute must remain false")

    if packet["real_world_actions_allowed"] is not False:
        raise SystemExit("real world actions must remain blocked")

    print(json.dumps(result, indent=2, sort_keys=True))
