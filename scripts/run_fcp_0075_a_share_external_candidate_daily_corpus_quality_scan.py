from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1 import (  # noqa: E402
    scan_candidate_daily_corpus,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scan an unverified local A-share daily candidate corpus."
    )
    parser.add_argument("root", type=Path)
    parser.add_argument("--observed-at-utc", required=True)
    arguments = parser.parse_args()
    evidence = scan_candidate_daily_corpus(
        arguments.root,
        observed_at_utc=arguments.observed_at_utc,
    )
    print(json.dumps(asdict(evidence), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
