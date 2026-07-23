from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

from .contracts import (
    RuntimeFootprintEvidence,
    RuntimeFootprintRegistration,
    build_runtime_footprint_evidence,
)
from .scanner import scan_top_level_metadata


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_plain(nested) for nested in value]
    return value


def render_evidence_json(evidence: RuntimeFootprintEvidence) -> str:
    return json.dumps(
        _plain(evidence.as_payload()),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def scan_runtime_footprint(
    directory: Path,
    *,
    artifact_id: str,
    max_top_level_entries: int = 64,
) -> RuntimeFootprintEvidence:
    registration = RuntimeFootprintRegistration(
        artifact_id=artifact_id,
        max_top_level_entries=max_top_level_entries,
    )
    snapshot = scan_top_level_metadata(
        Path(directory),
        max_top_level_entries=registration.max_top_level_entries,
    )
    return build_runtime_footprint_evidence(registration, snapshot)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fcf-qmt-runtime-footprint-scan",
        description="Scan bounded path-free Guojin QMT runtime footprint metadata.",
    )
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--max-top-level-entries", type=int, default=64)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = scan_runtime_footprint(
            args.directory,
            artifact_id=args.artifact_id,
            max_top_level_entries=args.max_top_level_entries,
        )
    except (OSError, TypeError, ValueError):
        print('{"error":"LOCAL_RUNTIME_FOOTPRINT_SCAN_FAILED"}', file=sys.stderr)
        return 2
    print(render_evidence_json(evidence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
