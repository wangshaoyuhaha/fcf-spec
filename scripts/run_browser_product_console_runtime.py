from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.browser_product_console_runtime_app_1 import (  # noqa: E402
    serve_browser_console_runtime,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the FCF paper-only browser product console on 127.0.0.1."
        )
    )
    parser.add_argument(
        "--allowed-root",
        required=True,
        type=Path,
        help="Local registered-artifact root directory.",
    )
    parser.add_argument(
        "--index",
        required=True,
        type=Path,
        help="Registered browser console artifact index.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Loopback port between 1024 and 65535.",
    )
    parser.add_argument(
        "--title",
        default="FCF Browser Product Console",
        help="Local browser page title.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    print(
        f"FCF browser console: http://127.0.0.1:{args.port}",
        flush=True,
    )
    print(
        "Paper-only / Local loopback / Operator review required",
        flush=True,
    )
    serve_browser_console_runtime(
        allowed_root=args.allowed_root,
        index_path=args.index,
        port=args.port,
        title=args.title,
    )


if __name__ == "__main__":
    main()
