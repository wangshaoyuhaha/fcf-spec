import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.paper_operator_console_report import build_operator_console_markdown_report
from btc_finance_platform.paper_operator_console_report import build_operator_console_ui_manifest
from btc_finance_platform.paper_operator_console_report import write_operator_console_static_export_bundle

if __name__ == "__main__":
    root = Path(ROOT)
    fixture = root / "fixtures" / "sample_multi_market_batch.json"
    output_dir = root / "artifacts" / "operator_console_static_export"
    actions = {"BTCUSDT": "approved", "AAPL": "pending", "SPY": "rejected"}
    report = build_operator_console_markdown_report(fixture, actions)
    manifest = build_operator_console_ui_manifest(fixture, actions)
    bundle = write_operator_console_static_export_bundle(fixture, output_dir, actions)
    print(json.dumps({
        "report": {
            "ok": report["ok"],
            "type": report["type"],
            "summary": report["summary"],
            "paper_only": report["paper_only"],
        },
        "manifest": {
            "ok": manifest["ok"],
            "type": manifest["type"],
            "manifest_version": manifest["manifest_version"],
            "validation": manifest["validation"],
        },
        "bundle": {
            "ok": bundle["ok"],
            "type": bundle["type"],
            "output_dir": bundle["output_dir"],
            "manifest_file": bundle["manifest_file"],
            "report_file": bundle["report_file"],
        },
    }, indent=2, sort_keys=True))
