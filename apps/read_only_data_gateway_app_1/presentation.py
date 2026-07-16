from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from .registry import RegisteredArtifactRegistry
from .service import GatewayQueryOutcome, SourcePolicyStatus, evaluate_source_policy


@dataclass(frozen=True)
class GatewaySourcePresentation:
    source_id: str
    evidence_id: str
    artifact_format: str
    policy_status: str
    record_count: int | None
    artifact_sha256: str | None
    normalized_records_sha256: str | None
    blocking_reasons: tuple[str, ...]
    degradation_reasons: tuple[str, ...]
    operator_review_required: bool = True

    def as_payload(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "artifact_format": self.artifact_format,
            "artifact_sha256": self.artifact_sha256,
            "blocking_reasons": self.blocking_reasons,
            "degradation_reasons": self.degradation_reasons,
            "evidence_id": self.evidence_id,
            "normalized_records_sha256": self.normalized_records_sha256,
            "operator_review_required": self.operator_review_required,
            "policy_status": self.policy_status,
            "record_count": self.record_count,
            "source_id": self.source_id,
        })


@dataclass(frozen=True)
class GatewayPresentationModel:
    registry_sha256: str
    sources: tuple[GatewaySourcePresentation, ...]
    status_counts: Mapping[str, int]
    read_only: bool = True
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status_counts", MappingProxyType(dict(sorted(self.status_counts.items())))
        )
        if not self.read_only or not self.operator_review_required:
            raise ValueError("presentation must remain read-only and reviewed")
        if self.automatic_activation_allowed:
            raise ValueError("automatic activation is prohibited")


@dataclass(frozen=True)
class GatewayOperatorReviewPacket:
    packet_id: str
    registry_sha256: str
    source_ids: tuple[str, ...]
    ready_count: int
    degraded_count: int
    blocked_count: int
    allowed_operator_actions: tuple[str, ...] = (
        "ACKNOWLEDGE_SOURCE_REVIEW",
        "REJECT_SOURCE",
        "REQUEST_SOURCE_REPAIR",
    )
    operator_decision_status: str = "PENDING"
    automatic_activation_allowed: bool = False
    write_operation_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.packet_id.strip() or not self.source_ids:
            raise ValueError("review packet identity and sources are required")
        if self.automatic_activation_allowed or self.write_operation_allowed:
            raise ValueError("review packet cannot authorize automatic or write actions")


def build_gateway_presentation_model(
    registry: RegisteredArtifactRegistry,
    outcomes: tuple[GatewayQueryOutcome, ...] = (),
) -> GatewayPresentationModel:
    outcome_by_source = {item.request.source_id: item for item in outcomes}
    if len(outcome_by_source) != len(outcomes):
        raise ValueError("duplicate query outcome source_id")
    unknown = set(outcome_by_source).difference(registry.source_ids)
    if unknown:
        raise ValueError("query outcome references an unregistered source")
    sources: list[GatewaySourcePresentation] = []
    counts = {status.value: 0 for status in SourcePolicyStatus}
    for source in registry.sources:
        outcome = outcome_by_source.get(source.source_id)
        decision = evaluate_source_policy(source) if outcome is None else outcome.policy_decision
        counts[decision.status.value] += 1
        envelope = None if outcome is None else outcome.envelope
        sources.append(GatewaySourcePresentation(
            source_id=source.source_id,
            evidence_id=source.evidence_id,
            artifact_format=source.artifact_format.value,
            policy_status=decision.status.value,
            record_count=None if envelope is None else envelope.record_count,
            artifact_sha256=None if envelope is None else envelope.artifact_sha256,
            normalized_records_sha256=(
                None if envelope is None else envelope.normalized_records_sha256
            ),
            blocking_reasons=decision.blocking_reasons,
            degradation_reasons=decision.degradation_reasons,
        ))
    return GatewayPresentationModel(
        registry_sha256=registry.registry_sha256,
        sources=tuple(sources),
        status_counts=counts,
    )


def build_gateway_operator_review_packet(
    packet_id: str,
    model: GatewayPresentationModel,
) -> GatewayOperatorReviewPacket:
    counts = model.status_counts
    return GatewayOperatorReviewPacket(
        packet_id=packet_id,
        registry_sha256=model.registry_sha256,
        source_ids=tuple(item.source_id for item in model.sources),
        ready_count=counts[SourcePolicyStatus.READY_FOR_OPERATOR_REVIEW.value],
        degraded_count=counts[SourcePolicyStatus.DEGRADED.value],
        blocked_count=counts[SourcePolicyStatus.BLOCKED.value],
    )
