import argparse
import json

from btc_finance_platform.paper_pipeline import (
    assert_paper_pipeline_result,
    run_paper_pipeline,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="btc-finance-platform",
        description="Paper-only BTC finance platform command line entry.",
    )
    parser.add_argument("--symbol", default="BTCUSDT")
    parser.add_argument("--price", type=float, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = run_paper_pipeline(args.symbol, args.price)
    assert_paper_pipeline_result(result)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
