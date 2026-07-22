from __future__ import annotations

import json

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0085_btc_registered_local_export_validation_runner_app_1.contracts import (
    BTCLocalExportValidationResult,
)

from .contracts import (
    BTCLocalExportOperatorReviewItem,
    BTCLocalExportOperatorReviewPacket,
)


def build_operator_review_packet(
    validation_result: BTCLocalExportValidationResult,
    *,
    packet_id: str,
    packet_created_at_utc: str,
) -> BTCLocalExportOperatorReviewPacket:
    if type(validation_result) is not BTCLocalExportValidationResult:
        raise TypeError("validation_result must be exact BTCLocalExportValidationResult")
    result = validation_result
    evidence = (
        ("source-lineage", result.source_artifact_sha256),
        ("profile-lineage", result.profile_hash),
        ("observation-coverage", result.observation_hashes_sha256),
        (
            "sequence-bounds",
            canonical_sha256([result.sequence_min, result.sequence_max]),
        ),
        (
            "clock-bounds",
            canonical_sha256(
                {
                    "event": [result.event_start_utc, result.event_end_utc],
                    "ingested": [result.ingested_start_utc, result.ingested_end_utc],
                    "received": [result.received_start_utc, result.received_end_utc],
                }
            ),
        ),
        ("local-only-authority", result.result_hash),
    )
    return BTCLocalExportOperatorReviewPacket(
        packet_id=packet_id,
        validation_result=result,
        packet_created_at_utc=packet_created_at_utc,
        review_items=tuple(
            BTCLocalExportOperatorReviewItem(item_id=item_id, evidence_digest=digest)
            for item_id, digest in evidence
        ),
    )


def render_operator_review_packet_json(
    packet: BTCLocalExportOperatorReviewPacket,
) -> str:
    if type(packet) is not BTCLocalExportOperatorReviewPacket:
        raise TypeError("packet must be exact BTCLocalExportOperatorReviewPacket")
    return json.dumps(
        packet.to_record(),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"
