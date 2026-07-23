from __future__ import annotations

import json

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0093_btc_coin_metrics_reference_rate_local_csv_validation_app_1 import (
    CoinMetricsBTCReferenceCSVValidationResult,
)

from .contracts import (
    CoinMetricsBTCReferenceRateOperatorReviewItem,
    CoinMetricsBTCReferenceRateOperatorReviewPacket,
)


def build_registered_sample_validation_result(
) -> CoinMetricsBTCReferenceCSVValidationResult:
    return CoinMetricsBTCReferenceCSVValidationResult(
        source_artifact_id="coin-metrics-btc-reference-source-v1",
        source_artifact_sha256=(
            "50cc52664679f88209aba3d7f9989ec5a0957002a1d23003f59088736fd3d19a"
        ),
        source_byte_length=391,
        output_artifact_id="coin-metrics-btc-reference-validation-v1",
        header_sha256=(
            "a6a28dce7e995e1507e51880a896137bf6cc4b11971537062db2218a9ba5d6db"
        ),
        observation_hashes_sha256=(
            "62e2899ad98f12fa166997ec35ec4a7fa6f261ad0a2def9cbf2dc16b352d9b7a"
        ),
        observation_count=7,
        observation_start_utc="2026-07-22T22:00:00Z",
        observation_end_utc="2026-07-23T04:00:00Z",
        cadence_seconds=3_600,
        as_of_utc="2026-07-23T04:10:00Z",
    )


def build_operator_review_packet(
    validation_result: CoinMetricsBTCReferenceCSVValidationResult,
    *,
    packet_id: str,
    packet_created_at_utc: str,
) -> CoinMetricsBTCReferenceRateOperatorReviewPacket:
    if type(validation_result) is not CoinMetricsBTCReferenceCSVValidationResult:
        raise TypeError(
            "validation_result must be exact "
            "CoinMetricsBTCReferenceCSVValidationResult"
        )
    result = validation_result
    evidence = (
        ("source-registration", result.source_artifact_sha256),
        (
            "rights-boundary",
            canonical_sha256(
                {
                    "local_only": result.local_only,
                    "network_used": result.network_used,
                    "operator_review_required": result.operator_review_required,
                }
            ),
        ),
        (
            "schema-integrity",
            canonical_sha256(
                {
                    "header_sha256": result.header_sha256,
                    "source_schema_id": result.source_schema_id,
                }
            ),
        ),
        (
            "temporal-coverage",
            canonical_sha256(
                {
                    "cadence_seconds": result.cadence_seconds,
                    "count": result.observation_count,
                    "end_utc": result.observation_end_utc,
                    "start_utc": result.observation_start_utc,
                }
            ),
        ),
        (
            "neutral-rate-semantics",
            canonical_sha256(
                {
                    "mark_or_index_authority": result.mark_or_index_authority,
                    "observation_kind": result.observation_kind,
                }
            ),
        ),
        ("non-authority-boundary", result.result_hash),
    )
    return CoinMetricsBTCReferenceRateOperatorReviewPacket(
        packet_id=packet_id,
        validation_result=result,
        packet_created_at_utc=packet_created_at_utc,
        review_items=tuple(
            CoinMetricsBTCReferenceRateOperatorReviewItem(
                item_id=item_id,
                evidence_digest=digest,
            )
            for item_id, digest in evidence
        ),
    )


def render_operator_review_packet_json(
    packet: CoinMetricsBTCReferenceRateOperatorReviewPacket,
) -> str:
    if type(packet) is not CoinMetricsBTCReferenceRateOperatorReviewPacket:
        raise TypeError(
            "packet must be exact CoinMetricsBTCReferenceRateOperatorReviewPacket"
        )
    return json.dumps(
        packet.to_record(),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"
