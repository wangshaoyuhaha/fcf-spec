import argparse
import json
from typing import Any

from btc_finance_platform.analysis_flow import run_paper_analysis_flow
from btc_finance_platform.report_exporter import export_paper_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="btc-paper-analysis",
        description="Paper-only BTC analysis flow command line entry.",
    )
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--price", type=float, required=True)
    parser.add_argument("--reference-price", type=float, required=True)
    parser.add_argument("--output", default="")
    return parser


def run_analysis_cli(args: argparse.Namespace) -> dict[str, Any]:
    result = run_paper_analysis_flow({
        "symbol": args.symbol,
        "price": args.price,
        "reference_price": args.reference_price,
    })

    export_result = None
    if args.output:
        export_result = export_paper_report(result["report"], args.output)

    return {
        "ok": True,
        "type": "paper_analysis_cli_result",
        "analysis_flow": result,
        "export": export_result,
        "paper_only": True,
        "real_order": False,
        "real_execution": False,
        "real_money_impact": False,
        "operator_review_required": True,
        "bypass_operator_review": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = run_analysis_cli(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
