from __future__ import annotations

from .contracts import (
    DEFAULT_EVIDENCE_REFERENCE,
    NEXT_ACTION_IDS,
    REVIEW_ITEM_IDS,
    LocalCacheProbeOperatorReviewPacket,
    ProbeEvidenceReference,
    ProbeOperatorReviewItem,
    canonical_bytes,
    canonical_sha256,
)


def _review_digests(reference: ProbeEvidenceReference) -> tuple[str, ...]:
    return (
        reference.terminal_snapshot_sha256,
        reference.contract_sha256,
        canonical_sha256(
            {
                "call_attempted": reference.call_attempted,
                "call_count": reference.call_count,
                "call_state": reference.call_state,
                "row_count": reference.row_count,
                "schema_state": reference.schema_state,
                "timing_class": reference.timing_class,
            }
        ),
        canonical_sha256({"blocker": "MINIQMT_ENTITLEMENT_UNPROVEN"}),
        canonical_sha256({"blocker": "RIGHTS_AND_RETENTION_UNPROVEN"}),
        reference.evidence_hash,
    )


def build_operator_review_packet(
    reference: ProbeEvidenceReference = DEFAULT_EVIDENCE_REFERENCE,
) -> LocalCacheProbeOperatorReviewPacket:
    if type(reference) is not ProbeEvidenceReference:
        raise TypeError("reference must be exact ProbeEvidenceReference")
    items = tuple(
        ProbeOperatorReviewItem(item_id, digest)
        for item_id, digest in zip(
            REVIEW_ITEM_IDS,
            _review_digests(reference),
            strict=True,
        )
    )
    return LocalCacheProbeOperatorReviewPacket(
        packet_id="qmt-local-cache-probe-review-packet-v1",
        evidence_reference=reference,
        review_items=items,
        next_action_ids=NEXT_ACTION_IDS,
    )


def render_operator_review_packet_json(
    packet: LocalCacheProbeOperatorReviewPacket,
) -> str:
    if type(packet) is not LocalCacheProbeOperatorReviewPacket:
        raise TypeError("packet must be exact LocalCacheProbeOperatorReviewPacket")
    return canonical_bytes(packet.to_record()).decode("ascii") + "\n"
