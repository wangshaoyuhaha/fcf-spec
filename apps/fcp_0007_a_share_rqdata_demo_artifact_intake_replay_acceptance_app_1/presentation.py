from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import FCP_0007_BOUNDARY
from .contracts import RQDataDemoAcceptanceResult, RQDataDemoLoadResult


@dataclass(frozen=True)
class RQDataDemoAcceptancePacket:
    payload: Mapping[str, object]
    read_only: bool = True
    registered_artifact_only: bool = True
    operator_review_required: bool = True
    provider_selection_allowed: bool = False
    product_phase_authorization_allowed: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("RQData demo acceptance packet must be immutable")
        if not self.read_only or not self.registered_artifact_only:
            raise ValueError("RQData demo acceptance packet must remain read-only")
        if self.operator_review_required is not True:
            raise ValueError("RQData demo acceptance requires Operator review")
        if self.provider_selection_allowed or self.product_phase_authorization_allowed:
            raise ValueError("RQData demo packet cannot authorize product state")


def build_rqdata_demo_acceptance_packet(
    loaded: RQDataDemoLoadResult,
    result: RQDataDemoAcceptanceResult,
) -> RQDataDemoAcceptancePacket:
    artifact = MappingProxyType(
        {
            "artifact_id": loaded.artifact.artifact_id,
            "artifact_sha256": loaded.artifact.artifact_sha256,
            "byte_length": loaded.artifact.byte_length,
            "entitlement_state": loaded.artifact.entitlement_state,
            "raw_repository_storage_allowed": False,
            "redistribution_allowed": False,
            "retention_state": loaded.artifact.retention_state,
            "source_id": loaded.artifact.source_id,
            "usage_scope": loaded.artifact.usage_scope,
        }
    )
    return RQDataDemoAcceptancePacket(
        MappingProxyType(
            {
                "artifact": artifact,
                "date_max": result.date_max,
                "date_min": result.date_min,
                "fcp_0005_readiness_claimed": False,
                "finding_codes": result.finding_codes,
                "instrument_ids": result.instrument_ids,
                "missing_required_field_ids": result.missing_required_field_ids,
                "network_allowed": False,
                "normalized_csv_sha256": result.normalized_csv_sha256,
                "observed_field_ids": result.observed_field_ids,
                "operator_review_required": True,
                "product_evidence_state": result.product_evidence_state,
                "product_phase_authorized": False,
                "provider_selection_claimed": False,
                "read_only": True,
                "registered_artifact_only": True,
                "repeated_bom_count": loaded.repeated_bom_count,
                "replay_sha256": result.replay_sha256,
                "result_sha256": result.result_sha256,
                "row_count": result.row_count,
                "rowset_sha256": result.rowset_sha256,
                "schema_state": result.schema_state,
                "source_artifact_sha256": result.source_artifact_sha256,
            }
        )
    )


def validate_rqdata_demo_packet(
    packet: RQDataDemoAcceptancePacket,
) -> Mapping[str, bool]:
    checks = MappingProxyType(
        {
            "authority_preserved": (
                FCP_0007_BOUNDARY.deterministic_authority_preserved
                and FCP_0007_BOUNDARY.registered_evidence_authority_preserved
                and FCP_0007_BOUNDARY.ai_advisory_only
            ),
            "commercial_rights_unresolved": (
                packet.payload["artifact"]["entitlement_state"] == "UNRESOLVED"
            ),
            "network_denied": packet.payload["network_allowed"] is False,
            "operator_review_required": (
                packet.payload["operator_review_required"] is True
            ),
            "product_evidence_blocked": (
                packet.payload["product_evidence_state"] == "BLOCKED"
            ),
            "product_phase_denied": (
                packet.payload["product_phase_authorized"] is False
            ),
            "provider_selection_denied": (
                packet.payload["provider_selection_claimed"] is False
            ),
            "raw_redistribution_denied": (
                packet.payload["artifact"]["redistribution_allowed"] is False
                and packet.payload["artifact"]["raw_repository_storage_allowed"] is False
            ),
            "read_only_registered_artifact": (
                packet.payload["read_only"] is True
                and packet.payload["registered_artifact_only"] is True
            ),
            "schema_replay_ready": (
                packet.payload["schema_state"] == "READY_FOR_LOCAL_SCHEMA_REPLAY"
            ),
        }
    )
    if not all(checks.values()):
        raise ValueError("RQData demo packet acceptance failed")
    return checks
