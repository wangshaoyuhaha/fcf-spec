import os
import sys
import webbrowser
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.p13_operator_console_launcher import build_operator_console_launch_plan

if __name__ == "__main__":
    output = Path(ROOT) / "runtime" / "operator_console" / "index.html"
    result = build_operator_console_launch_plan(output)
    print(result["file_url"])
    webbrowser.open(result["file_url"])
