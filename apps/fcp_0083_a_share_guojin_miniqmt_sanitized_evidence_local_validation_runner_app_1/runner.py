from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

from apps.fcp_0082_a_share_guojin_miniqmt_python_market_data_entitlement_evidence_contract_app_1 import (
    MiniQMTEntitlementReviewPacket,
    RegisteredEntitlementEvidenceArtifact,
    evaluate_evidence,
    load_sanitized_evidence,
)


MAX_ARTIFACT_BYTES = 65536


def _plain(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _plain(nested) for key, nested in value.items()}
    if isinstance(value, tuple):
        return [_plain(nested) for nested in value]
    return value


def render_packet_json(packet: MiniQMTEntitlementReviewPacket) -> str:
    return json.dumps(
        _plain(packet.as_payload()),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def validate_local_evidence(
    artifact_path: Path,
    *,
    artifact_id: str,
    expected_sha256: str,
    expected_byte_length: int,
    as_of_utc: str,
) -> MiniQMTEntitlementReviewPacket:
    path = Path(artifact_path)
    if path.is_symlink():
        raise ValueError("artifact path must not be a symlink")
    if not path.exists() or not path.is_file():
        raise ValueError("artifact path must be an existing regular file")
    if not isinstance(expected_byte_length, int) or not 2 <= expected_byte_length <= MAX_ARTIFACT_BYTES:
        raise ValueError("expected byte length is outside the bounded limit")
    raw_bytes = path.read_bytes()
    if len(raw_bytes) > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact exceeds the bounded limit")
    artifact = RegisteredEntitlementEvidenceArtifact(
        artifact_id=artifact_id,
        artifact_path=path.name,
        artifact_sha256=expected_sha256,
        byte_length=expected_byte_length,
    )
    evidence = load_sanitized_evidence(artifact, raw_bytes)
    return evaluate_evidence(artifact, evidence, as_of_utc=as_of_utc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fcf-miniqmt-evidence-validate",
        description="Validate one registered local sanitized MiniQMT evidence artifact.",
    )
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--byte-length", required=True, type=int)
    parser.add_argument("--as-of-utc", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        packet = validate_local_evidence(
            args.artifact,
            artifact_id=args.artifact_id,
            expected_sha256=args.sha256,
            expected_byte_length=args.byte_length,
            as_of_utc=args.as_of_utc,
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        print('{"error":"LOCAL_EVIDENCE_VALIDATION_FAILED"}', file=sys.stderr)
        return 2
    print(render_packet_json(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
