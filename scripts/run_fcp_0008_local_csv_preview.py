from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (  # noqa: E402
    RegisteredLocalCSVArtifact,
    inspect_registered_local_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect one exactly registered local CSV without modifying it."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--byte-length", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        registration = RegisteredLocalCSVArtifact(
            artifact_id=args.artifact_id,
            source_id=args.source_id,
            artifact_sha256=args.sha256,
            byte_length=args.byte_length,
        )
        preview = inspect_registered_local_csv(args.path, registration)
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        print(f"LOCAL_CSV_PREVIEW_BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(dict(preview.as_mapping()), ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
