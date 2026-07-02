import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.data_schema import (
    validate_paper_batch_schema,
    validate_paper_input_schema,
)


if __name__ == "__main__":
    fixture_path = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
    payloads = json.loads(fixture_path.read_text(encoding="utf-8-sig"))

    single = validate_paper_input_schema(payloads[0])
    batch = validate_paper_batch_schema(payloads)

    print(json.dumps({
        "single": single,
        "batch": batch,
    }, indent=2, sort_keys=True))

