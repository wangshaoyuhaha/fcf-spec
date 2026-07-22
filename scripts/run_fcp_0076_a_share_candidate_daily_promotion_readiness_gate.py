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
    CandidateDailyCorpusQualityEvidence,
)
from apps.fcp_0076_a_share_candidate_daily_promotion_readiness_gate_app_1 import (  # noqa: E402
    evaluate_candidate_daily_promotion_readiness,
)


QUALITY_EVIDENCE_PATH = ROOT / (
    "FCF_REGISTERED_EVIDENCE_FCP_0075_A_SHARE_EXTERNAL_CANDIDATE_DAILY_"
    "CORPUS_QUALITY_QUARANTINE.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate the registered A-share candidate daily readiness gate."
    )
    parser.add_argument("--evaluated-at-utc", required=True)
    arguments = parser.parse_args()
    payload = json.loads(QUALITY_EVIDENCE_PATH.read_text(encoding="ascii"))
    payload.pop("evidence_hash")
    quality_evidence = CandidateDailyCorpusQualityEvidence(**payload)
    gate = evaluate_candidate_daily_promotion_readiness(
        quality_evidence,
        (),
        evaluated_at_utc=arguments.evaluated_at_utc,
    )
    print(json.dumps(asdict(gate), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
