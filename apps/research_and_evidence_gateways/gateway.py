from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable, Mapping

from .boundary import RESEARCH_AND_EVIDENCE_BOUNDARY
from .contracts import CrossVerificationStatus, ResearchQuery, ResearchSource, require_identifier, require_utc


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ResearchSourceRegistry:
    def __init__(self, sources: Iterable[ResearchSource]) -> None:
        supplied = tuple(sources)
        if not supplied:
            raise ValueError("research source registry must not be empty")
        if not all(isinstance(item, ResearchSource) for item in supplied):
            raise TypeError("registry entries must be ResearchSource values")
        records = tuple(sorted(supplied, key=lambda item: item.source_id))
        for values, name in ((tuple(x.source_id for x in records), "source_id"), (tuple(x.source_url for x in records), "source_url"), (tuple(x.evidence_id for x in records), "evidence_id")):
            if len(values) != len(set(values)):
                raise ValueError(f"duplicate research source {name}")
        self.sources = records
        self._by_id = MappingProxyType({item.source_id: item for item in records})

    def require(self, source_id: str) -> ResearchSource:
        try:
            return self._by_id[source_id]
        except KeyError as exc:
            raise KeyError(f"unregistered research source: {source_id}") from exc

    @property
    def registry_sha256(self) -> str:
        payload = [dict(item.as_payload()) for item in self.sources]
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class RetrievalReceipt:
    receipt_id: str
    query_id: str
    source_id: str
    evidence_id: str
    registered_artifact_id: str
    content_sha256: str
    publication_at_utc: str
    retrieved_at_utc: str
    quoted_location: str
    credential_material_present: bool = False
    network_transport_performed: bool = False

    def __post_init__(self) -> None:
        for name in ("receipt_id", "query_id", "source_id", "evidence_id", "registered_artifact_id", "quoted_location"):
            object.__setattr__(self, name, require_identifier(getattr(self, name), name))
        digest = str(self.content_sha256).lower()
        if _SHA256.fullmatch(digest) is None:
            raise ValueError("content_sha256 must be a SHA-256 digest")
        object.__setattr__(self, "content_sha256", digest)
        object.__setattr__(self, "publication_at_utc", require_utc(self.publication_at_utc, "publication_at_utc"))
        object.__setattr__(self, "retrieved_at_utc", require_utc(self.retrieved_at_utc, "retrieved_at_utc"))
        if self.credential_material_present or self.network_transport_performed:
            raise ValueError("receipt must be imported metadata without credentials or transport")


@dataclass(frozen=True)
class EvidenceTrace:
    receipt: RetrievalReceipt
    source: ResearchSource
    cross_verification_status: CrossVerificationStatus
    supporting_evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.receipt.source_id != self.source.source_id or self.receipt.evidence_id != self.source.evidence_id:
            raise ValueError("evidence trace source linkage mismatch")
        object.__setattr__(self, "cross_verification_status", CrossVerificationStatus(self.cross_verification_status))
        evidence = tuple(sorted({require_identifier(x, "supporting_evidence_id") for x in self.supporting_evidence_ids}))
        if self.cross_verification_status is CrossVerificationStatus.VERIFIED and not evidence:
            raise ValueError("verified trace requires supporting evidence")
        object.__setattr__(self, "supporting_evidence_ids", evidence)


@dataclass(frozen=True)
class ResearchGatewayOutcome:
    query: ResearchQuery
    traces: tuple[EvidenceTrace, ...]
    registry_sha256: str
    status: str
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False


@dataclass(frozen=True)
class ResearchReviewPacket:
    payload: Mapping[str, object]


class ResearchGatewayService:
    def __init__(self, registry: ResearchSourceRegistry) -> None:
        if not isinstance(registry, ResearchSourceRegistry):
            raise TypeError("registry must be a ResearchSourceRegistry")
        self._registry = registry

    def evaluate(self, query: ResearchQuery, traces: Iterable[EvidenceTrace]) -> ResearchGatewayOutcome:
        if not isinstance(query, ResearchQuery):
            raise TypeError("query must be a ResearchQuery")
        records = tuple(sorted(tuple(traces), key=lambda item: item.receipt.receipt_id))
        if not records or not all(isinstance(item, EvidenceTrace) for item in records):
            raise ValueError("research gateway requires evidence traces")
        allowed = set(query.approved_source_ids)
        for source_id in allowed:
            self._registry.require(source_id)
        if any(item.receipt.query_id != query.query_id or item.source.source_id not in allowed for item in records):
            raise ValueError("research trace query or approval linkage mismatch")
        statuses = {item.cross_verification_status for item in records}
        status = "READY_FOR_OPERATOR_REVIEW" if statuses == {CrossVerificationStatus.VERIFIED} else "DEGRADED"
        return ResearchGatewayOutcome(query, records, self._registry.registry_sha256, status)

    def build_review_packet(self, outcome: ResearchGatewayOutcome) -> ResearchReviewPacket:
        traces = tuple(MappingProxyType({
            "content_sha256": item.receipt.content_sha256,
            "cross_verification_status": item.cross_verification_status.value,
            "evidence_id": item.receipt.evidence_id,
            "publication_at_utc": item.receipt.publication_at_utc,
            "quoted_location": item.receipt.quoted_location,
            "retrieved_at_utc": item.receipt.retrieved_at_utc,
            "source_class": item.source.source_class.value,
            "source_id": item.source.source_id,
            "source_url": item.source.source_url,
            "supporting_evidence_ids": item.supporting_evidence_ids,
            "trust_level": item.source.trust_level,
        }) for item in outcome.traces)
        return ResearchReviewPacket(MappingProxyType({
            "automatic_activation_allowed": False,
            "credential_material_present": False,
            "operator_review_required": True,
            "query_id": outcome.query.query_id,
            "query_text": outcome.query.query_text,
            "read_only": True,
            "registry_sha256": outcome.registry_sha256,
            "status": outcome.status,
            "traces": traces,
        }))


def validate_research_acceptance(outcome: ResearchGatewayOutcome, packet: ResearchReviewPacket) -> str:
    if packet.payload["query_id"] != outcome.query.query_id or not packet.payload["traces"]:
        raise ValueError("research acceptance linkage failed")
    if packet.payload["credential_material_present"] or packet.payload["automatic_activation_allowed"]:
        raise ValueError("research acceptance boundary failed")
    boundary = RESEARCH_AND_EVIDENCE_BOUNDARY
    if boundary.arbitrary_network_transport_allowed or boundary.real_execution_allowed:
        raise ValueError("research runtime boundary failed")
    return "PASS"
