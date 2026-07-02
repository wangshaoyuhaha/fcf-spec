import argparse
import json
from typing import Any

from btc_finance_platform.batch_analysis import run_paper_analysis_batch, summarize_batch_results
from btc_finance_platform.batch_file_loader import load_paper_batch_file
from btc_finance_platform.batch_report import render_batch_report
from btc_finance_platform.report_exporter import export_paper_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="btc-paper-batch",
        description="Paper-only BTC batch analysis command line entry.",
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", default="auto", choices=["auto", "json", "csv"])
    parser.add_argument("--output", default="")
    return parser


def run_batch_cli(args: argparse.Namespace) -> dict[str, Any]:
    payloads = load_paper_batch_file(args.input, args.format)
    batch = run_paper_analysis_batch(payloads)
    summary = summarize_batch_results(batch)
    report = render_batch_report(batch, summary)

    export_result = None
    if args.output:
        export_result = export_paper_report(report, args.output)

    return {
        "ok": True,
        "type": "paper_batch_cli_result",
        "batch": batch,
        "summary": summary,
        "report": report,
        "export": export_result,
        "paper_only": True,
        "real_exchange_api": False,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = run_batch_cli(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
