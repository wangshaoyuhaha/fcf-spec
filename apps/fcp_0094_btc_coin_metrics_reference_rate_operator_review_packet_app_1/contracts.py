from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0093_btc_coin_metrics_reference_rate_local_csv_validation_app_1 import (
    CoinMetricsBTCReferenceCSVValidationResult,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


PHASE_ID = (
    "FCF-FCP-0094-BTC-COIN-METRICS-REFERENCE-RATE-OPERATOR-"
    "REVIEW-PACKET-APP-1"
)
REVIEW_ITEM_IDS = (
    "source-registration",
    "rights-boundary",
    "schema-integrity",
    "temporal-coverage",
    "neutral-rate-semantics",
    "non-authority-boundary",
)


def _sha256(value: object, name: str) -> str:
    text = str(value).strip().lower()
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return text


@dataclass(frozen=True)
class CoinMetricsBTCReferenceRateOperatorReviewItem:
    item_id: str
    evidence_digest: str
    review_state: str = "OPERATOR_REVIEW_REQUIRED"
    operator_review_required: bool = True
    approved: bool = False
    rejected: bool = False
    item_hash: str = field(init=False)

    def __post_init__(self) -> None:
        item_id = identifier(self.item_id, "item_id")
        if item_id not in REVIEW_ITEM_IDS:
            raise ValueError("review item is not registered")
        digest = _sha256(self.evidence_digest, "evidence_digest")
        if (
            self.review_state != "OPERATOR_REVIEW_REQUIRED"
            or self.operator_review_required is not True
            or self.approved is not False
            or self.rejected is not False
        ):
            raise ValueError("review item cannot assign a disposition")
        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(self, "evidence_digest", digest)
        object.__setattr__(
            self,
            "item_hash",
            canonical_sha256(
                {
                    "evidence_digest": digest,
                    "item_id": item_id,
                    "review_state": self.review_state,
                }
            ),
        )

    def to_record(self) -> dict[str, object]:
        return {
            "approved": False,
            "evidence_digest": self.evidence_digest,
            "item_hash": self.item_hash,
            "item_id": self.item_id,
            "operator_review_required": True,
            "rejected": False,
            "review_state": self.review_state,
        }


@dataclass(frozen=True)
class CoinMetricsBTCReferenceRateOperatorReviewPacket:
    packet_id: str
    validation_result: CoinMetricsBTCReferenceCSVValidationResult
    packet_created_at_utc: str
    review_items: tuple[CoinMetricsBTCReferenceRateOperatorReviewItem, ...]
    review_state: str = "OPERATOR_REVIEW_REQUIRED"
    acceptance_gate: str = "BLOCKED_PENDING_OPERATOR_DISPOSITION"
    operator_review_required: bool = True
    disposition_assigned: bool = False
    evidence_approved: bool = False
    evidence_rejected: bool = False
    data_promotion_allowed: bool = False
    mark_or_index_authority: bool = False
    provider_selected: bool = False
    venue_selected: bool = False
    realtime_activated: bool = False
    network_used: bool = False
    sdk_used: bool = False
    signal_authority: bool = False
    product_authority: bool = False
    account_state_allowed: bool = False
    order_allowed: bool = False
    execution_allowed: bool = False
    gap_095_status: str = "RESEARCH_REQUIRED"
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    schema_version: str = "coin-metrics-btc-reference-rate-review-packet-v1"
    validation_result_hash: str = field(init=False)
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        packet_id = identifier(self.packet_id, "packet_id")
        result = self.validation_result
        if type(result) is not CoinMetricsBTCReferenceCSVValidationResult:
            raise ValueError("review packet requires one exact typed FCP-0093 result")
        created = utc(self.packet_created_at_utc, "packet_created_at_utc")
        if instant(created) < instant(result.as_of_utc):
            raise ValueError("review packet cannot precede validation")
        items = tuple(self.review_items)
        if not all(
            type(item) is CoinMetricsBTCReferenceRateOperatorReviewItem
            for item in items
        ):
            raise ValueError("review_items must contain exact typed items")
        if tuple(item.item_id for item in items) != REVIEW_ITEM_IDS:
            raise ValueError("review_items must use the closed order")
        if len({item.item_hash for item in items}) != len(items):
            raise ValueError("review_items must be unique")
        forbidden = (
            self.disposition_assigned,
            self.evidence_approved,
            self.evidence_rejected,
            self.data_promotion_allowed,
            self.mark_or_index_authority,
            self.provider_selected,
            self.venue_selected,
            self.realtime_activated,
            self.network_used,
            self.sdk_used,
            self.signal_authority,
            self.product_authority,
            self.account_state_allowed,
            self.order_allowed,
            self.execution_allowed,
        )
        if (
            self.review_state != "OPERATOR_REVIEW_REQUIRED"
            or self.acceptance_gate != "BLOCKED_PENDING_OPERATOR_DISPOSITION"
            or self.operator_review_required is not True
            or any(forbidden)
            or self.gap_095_status != "RESEARCH_REQUIRED"
        ):
            raise ValueError("review packet cannot decide, promote, authorize, or act")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("review packet authority identities are immutable")
        if self.schema_version != "coin-metrics-btc-reference-rate-review-packet-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "packet_id", packet_id)
        object.__setattr__(self, "packet_created_at_utc", created)
        object.__setattr__(self, "review_items", items)
        object.__setattr__(self, "validation_result_hash", result.result_hash)
        object.__setattr__(
            self,
            "packet_hash",
            canonical_sha256(
                {
                    "acceptance_gate": self.acceptance_gate,
                    "packet_created_at_utc": created,
                    "packet_id": packet_id,
                    "review_item_hashes": [item.item_hash for item in items],
                    "review_state": self.review_state,
                    "schema_version": self.schema_version,
                    "validation_result_hash": result.result_hash,
                }
            ),
        )

    def to_record(self) -> dict[str, object]:
        result = self.validation_result
        return {
            "acceptance_gate": self.acceptance_gate,
            "authority": {
                "account_state_allowed": False,
                "ai_role": self.ai_role,
                "calculation_authority": self.calculation_authority,
                "data_promotion_allowed": False,
                "disposition_assigned": False,
                "evidence_approved": False,
                "evidence_authority": self.evidence_authority,
                "evidence_rejected": False,
                "execution_allowed": False,
                "mark_or_index_authority": False,
                "network_used": False,
                "operator_review_required": True,
                "order_allowed": False,
                "product_authority": False,
                "provider_selected": False,
                "realtime_activated": False,
                "sdk_used": False,
                "signal_authority": False,
                "venue_selected": False,
            },
            "gap_095_status": self.gap_095_status,
            "packet_created_at_utc": self.packet_created_at_utc,
            "packet_hash": self.packet_hash,
            "packet_id": self.packet_id,
            "phase_id": PHASE_ID,
            "review_items": [item.to_record() for item in self.review_items],
            "review_state": self.review_state,
            "schema_version": self.schema_version,
            "validation": {
                "cadence_seconds": result.cadence_seconds,
                "header_sha256": result.header_sha256,
                "observation_count": result.observation_count,
                "observation_end_utc": result.observation_end_utc,
                "observation_hashes_sha256": result.observation_hashes_sha256,
                "observation_kind": result.observation_kind,
                "observation_start_utc": result.observation_start_utc,
                "quality_state": result.quality_state,
                "result_hash": result.result_hash,
                "source_artifact_id": result.source_artifact_id,
                "source_artifact_sha256": result.source_artifact_sha256,
                "source_byte_length": result.source_byte_length,
                "source_schema_id": result.source_schema_id,
            },
        }
