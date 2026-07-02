import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.batch_cli import main


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = Path(temp_dir) / "batch.json"
        input_path.write_text(json.dumps([
            {"symbol": "BTCUSDT", "price": 65000, "reference_price": 64000},
            {"symbol": "ETHUSDT", "price": 3500, "reference_price": 3600},
        ]), encoding="utf-8")

        raise SystemExit(main(["--input", str(input_path)]))
