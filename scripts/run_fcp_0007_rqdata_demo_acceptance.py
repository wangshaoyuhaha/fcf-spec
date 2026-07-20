from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from apps.fcp_0007_a_share_rqdata_demo_artifact_intake_replay_acceptance_app_1 import (
    RegisteredRQDataDemoArtifact,
    build_rqdata_demo_acceptance_packet,
    evaluate_rqdata_demo_acceptance,
    load_registered_rqdata_demo,
    validate_rqdata_demo_packet,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate one exact registered RQData A-share daily demo artifact."
    )
    parser.add_argument("--path", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--byte-length", required=True, type=int)
    parser.add_argument("--registered-at-utc", required=True)
    parser.add_argument(
        "--artifact-id",
        default="rqdata-a-share-daily-demo-f229fdf9",
    )
    parser.add_argument("--source-id", default="rqdata-official-demo")
    return parser


def build_report(arguments: argparse.Namespace) -> dict[str, object]:
    registration = RegisteredRQDataDemoArtifact(
        artifact_id=arguments.artifact_id,
        source_id=arguments.source_id,
        artifact_sha256=arguments.sha256,
        byte_length=arguments.byte_length,
        registered_at_utc=arguments.registered_at_utc,
    )
    loaded = load_registered_rqdata_demo(Path(arguments.path), registration)
    result = evaluate_rqdata_demo_acceptance(loaded)
    packet = build_rqdata_demo_acceptance_packet(loaded, result)
    checks = validate_rqdata_demo_packet(packet)
    return {
        "artifact": dict(packet.payload["artifact"]),
        "checks": dict(checks),
        "columns": loaded.columns,
        "date_max": result.date_max,
        "date_min": result.date_min,
        "finding_codes": result.finding_codes,
        "instrument_ids": result.instrument_ids,
        "missing_required_field_ids": result.missing_required_field_ids,
        "normalized_csv_sha256": result.normalized_csv_sha256,
        "observed_field_ids": result.observed_field_ids,
        "repeated_bom_count": loaded.repeated_bom_count,
        "replay_sha256": result.replay_sha256,
        "result_sha256": result.result_sha256,
        "row_count": result.row_count,
        "rowset_sha256": result.rowset_sha256,
        "schema_state": result.schema_state,
    }


def main() -> int:
    report = build_report(build_parser().parse_args())
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
