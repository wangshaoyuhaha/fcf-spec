from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field


PHASE_ID = (
    "FCF-FCP-0092-A-SHARE-GUOJIN-QMT-LOCAL-CACHE-PROBE-OPERATOR-"
    "REVIEW-PACKET-APP-1"
)
SOURCE_PHASE_ID = (
    "FCF-FCP-0091-A-SHARE-GUOJIN-QMT-REGISTERED-LOCAL-CACHE-LOOPBACK-"
    "READ-ONLY-PROBE-APP-1"
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
REVIEW_ITEM_IDS = (
    "terminal-liveness",
    "sdk-lineage",
    "probe-call-state",
    "entitlement",
    "rights-retention",
    "market-data-availability",
)
NEXT_ACTION_IDS = (
    "START_REGISTERED_QMT_TERMINAL_OUT_OF_BAND",
    "RERUN_FCP_0091_EXACT_PROBE",
    "REVIEW_NEW_REGISTERED_EVIDENCE",
)
SOURCE_BLOCKERS = (
    "MINIQMT_ENTITLEMENT_UNPROVEN",
    "QMT_TERMINAL_NOT_OBSERVED",
    "RIGHTS_AND_RETENTION_UNPROVEN",
)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def exact_sha256(value: str, field_name: str) -> str:
    normalized = str(value).lower()
    if not SHA256.fullmatch(normalized):
        raise ValueError(f"{field_name} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class ProbeEvidenceReference:
    source_phase_id: str
    source_delivery_id: str
    contract_sha256: str
    terminal_snapshot_sha256: str
    evidence_hash: str
    call_state: str
    call_attempted: bool
    call_count: int
    row_count: int
    schema_state: str
    timing_class: str
    blockers: tuple[str, ...]
    reference_hash: str = field(init=False)

    def __post_init__(self) -> None:
        exact = (
            self.source_phase_id == SOURCE_PHASE_ID,
            self.source_delivery_id
            == "fcp-0091-registered-local-cache-probe-delivered-v1",
            self.contract_sha256
            == "da5b77a26f14446303ffd62b5b75a94230837a99afeff1c4e0c49ecab4bdb6d4",
            self.terminal_snapshot_sha256
            == "5fac5f12b854bddf477a48bac42d0178277b2c2878c85aa10039248f81b7b153",
            self.evidence_hash
            == "ede7dc35af027edd3025be947d728075ea41964a807a00bf749ac873fb2b30bf",
            self.call_state == "NOT_RUN",
            self.call_attempted is False,
            self.call_count == 0,
            self.row_count == 0,
            self.schema_state == "NOT_INSPECTED",
            self.timing_class == "NOT_MEASURED",
            self.blockers == SOURCE_BLOCKERS,
        )
        if not all(exact):
            raise ValueError("probe evidence reference must match FCP-0091 delivery")
        for field_name in (
            "contract_sha256",
            "terminal_snapshot_sha256",
            "evidence_hash",
        ):
            object.__setattr__(
                self,
                field_name,
                exact_sha256(getattr(self, field_name), field_name),
            )
        payload = self.to_record(include_hash=False)
        object.__setattr__(self, "reference_hash", canonical_sha256(payload))

    def to_record(self, *, include_hash: bool = True) -> dict[str, object]:
        payload = {
            "blockers": list(self.blockers),
            "call_attempted": self.call_attempted,
            "call_count": self.call_count,
            "call_state": self.call_state,
            "contract_sha256": self.contract_sha256,
            "evidence_hash": self.evidence_hash,
            "row_count": self.row_count,
            "schema_state": self.schema_state,
            "source_delivery_id": self.source_delivery_id,
            "source_phase_id": self.source_phase_id,
            "terminal_snapshot_sha256": self.terminal_snapshot_sha256,
            "timing_class": self.timing_class,
        }
        if include_hash:
            payload["reference_hash"] = self.reference_hash
        return payload


DEFAULT_EVIDENCE_REFERENCE = ProbeEvidenceReference(
    source_phase_id=SOURCE_PHASE_ID,
    source_delivery_id="fcp-0091-registered-local-cache-probe-delivered-v1",
    contract_sha256="da5b77a26f14446303ffd62b5b75a94230837a99afeff1c4e0c49ecab4bdb6d4",
    terminal_snapshot_sha256="5fac5f12b854bddf477a48bac42d0178277b2c2878c85aa10039248f81b7b153",
    evidence_hash="ede7dc35af027edd3025be947d728075ea41964a807a00bf749ac873fb2b30bf",
    call_state="NOT_RUN",
    call_attempted=False,
    call_count=0,
    row_count=0,
    schema_state="NOT_INSPECTED",
    timing_class="NOT_MEASURED",
    blockers=SOURCE_BLOCKERS,
)


@dataclass(frozen=True)
class ProbeOperatorReviewItem:
    item_id: str
    evidence_digest: str
    review_state: str = "OPERATOR_REVIEW_REQUIRED"
    operator_review_required: bool = True
    approved: bool = False
    rejected: bool = False
    item_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.item_id not in REVIEW_ITEM_IDS:
            raise ValueError("review item is not registered")
        digest = exact_sha256(self.evidence_digest, "evidence_digest")
        if (
            self.review_state != "OPERATOR_REVIEW_REQUIRED"
            or self.operator_review_required is not True
            or self.approved is not False
            or self.rejected is not False
        ):
            raise ValueError("review item cannot assign a disposition")
        object.__setattr__(self, "evidence_digest", digest)
        object.__setattr__(
            self,
            "item_hash",
            canonical_sha256(
                {
                    "evidence_digest": digest,
                    "item_id": self.item_id,
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
class LocalCacheProbeOperatorReviewPacket:
    packet_id: str
    evidence_reference: ProbeEvidenceReference
    review_items: tuple[ProbeOperatorReviewItem, ...]
    next_action_ids: tuple[str, ...]
    review_state: str = "OPERATOR_ACTION_REQUIRED"
    acceptance_gate: str = "BLOCKED_PENDING_REGISTERED_TERMINAL_PROBE"
    operator_review_required: bool = True
    disposition_assigned: bool = False
    evidence_accepted: bool = False
    evidence_rejected: bool = False
    sdk_used: bool = False
    network_used: bool = False
    credentials_used: bool = False
    account_api_used: bool = False
    trading_api_used: bool = False
    provider_selected: bool = False
    realtime_activated: bool = False
    data_promotion_allowed: bool = False
    product_authority: bool = False
    execution_authority: bool = False
    gap_104_status: str = "RESEARCH_REQUIRED"
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    schema_version: str = "qmt-local-cache-probe-operator-review-packet-v1"
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.packet_id != "qmt-local-cache-probe-review-packet-v1":
            raise ValueError("packet_id is not registered")
        if type(self.evidence_reference) is not ProbeEvidenceReference:
            raise ValueError("packet requires exact typed evidence reference")
        items = tuple(self.review_items)
        if not all(type(item) is ProbeOperatorReviewItem for item in items):
            raise ValueError("review_items must contain exact typed items")
        if tuple(item.item_id for item in items) != REVIEW_ITEM_IDS:
            raise ValueError("review_items must use the closed order")
        if len({item.item_hash for item in items}) != len(items):
            raise ValueError("review_items must be unique")
        if self.next_action_ids != NEXT_ACTION_IDS:
            raise ValueError("next_action_ids must use the closed order")
        forbidden = (
            self.disposition_assigned,
            self.evidence_accepted,
            self.evidence_rejected,
            self.sdk_used,
            self.network_used,
            self.credentials_used,
            self.account_api_used,
            self.trading_api_used,
            self.provider_selected,
            self.realtime_activated,
            self.data_promotion_allowed,
            self.product_authority,
            self.execution_authority,
        )
        if (
            self.review_state != "OPERATOR_ACTION_REQUIRED"
            or self.acceptance_gate != "BLOCKED_PENDING_REGISTERED_TERMINAL_PROBE"
            or self.operator_review_required is not True
            or any(forbidden)
            or self.gap_104_status != "RESEARCH_REQUIRED"
        ):
            raise ValueError("review packet cannot decide, activate, promote, or act")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("review packet authority identities are immutable")
        if self.schema_version != "qmt-local-cache-probe-operator-review-packet-v1":
            raise ValueError("schema_version is not registered")
        object.__setattr__(self, "review_items", items)
        object.__setattr__(
            self,
            "packet_hash",
            canonical_sha256(self.to_record(include_hash=False)),
        )

    def to_record(self, *, include_hash: bool = True) -> dict[str, object]:
        payload = {
            "acceptance_gate": self.acceptance_gate,
            "authority": {
                "ai_role": self.ai_role,
                "calculation_authority": self.calculation_authority,
                "data_promotion_allowed": False,
                "disposition_assigned": False,
                "evidence_accepted": False,
                "evidence_authority": self.evidence_authority,
                "evidence_rejected": False,
                "execution_authority": False,
                "operator_review_required": True,
                "product_authority": False,
                "provider_selected": False,
                "realtime_activated": False,
            },
            "evidence_reference": self.evidence_reference.to_record(),
            "gap_104_status": self.gap_104_status,
            "next_action_ids": list(self.next_action_ids),
            "packet_id": self.packet_id,
            "phase_id": PHASE_ID,
            "review_items": [item.to_record() for item in self.review_items],
            "review_state": self.review_state,
            "runtime_use": {
                "account_api_used": False,
                "credentials_used": False,
                "network_used": False,
                "sdk_used": False,
                "trading_api_used": False,
            },
            "schema_version": self.schema_version,
        }
        if include_hash:
            payload["packet_hash"] = self.packet_hash
        return payload
