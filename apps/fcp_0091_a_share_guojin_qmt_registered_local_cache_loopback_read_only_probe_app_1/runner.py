from __future__ import annotations

import argparse
from pathlib import Path

from .contracts import render_probe_evidence_json
from .runtime import execute_registered_probe


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk-root", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = execute_registered_probe(Path(args.sdk_root))
    except (OSError, TypeError, ValueError):
        return 2
    print(render_probe_evidence_json(evidence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
