from __future__ import annotations

from decimal import Decimal

from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtFrontAdjustmentReference,
)
from apps.fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1 import (
    QmtLocalExportCoverageEvidence,
    build_reference_evidence as build_reference_coverage,
)

from .contracts import (
    OfflineSdkAbiObservation,
    QmtDualExportOfflineCompatibilityEvidence,
)


def build_compatibility_evidence(
    coverage: QmtLocalExportCoverageEvidence,
    adjustment: QmtFrontAdjustmentReference,
    sdk_observation: OfflineSdkAbiObservation,
    *,
    evidence_id: str,
    observed_at_utc: str,
) -> QmtDualExportOfflineCompatibilityEvidence:
    return QmtDualExportOfflineCompatibilityEvidence(
        evidence_id=evidence_id,
        observed_at_utc=observed_at_utc,
        coverage_evidence=coverage,
        adjustment_reference=adjustment,
        sdk_observation=sdk_observation,
    )


def build_reference_evidence() -> QmtDualExportOfflineCompatibilityEvidence:
    coverage = build_reference_coverage()
    observation = coverage.observations[0]
    adjustment = QmtFrontAdjustmentReference(
        raw_artifact_sha256=observation.source_artifact_sha256,
        front_artifact_sha256="4" * 64,
        profile_hash=coverage.profile_hash,
        row_count=observation.row_count,
        boundary_dates=("2026-07-21",),
        latest_cash_offset=Decimal("0.42"),
    )
    sdk = OfflineSdkAbiObservation(
        observation_id="qmt-offline-sdk-reference-v1",
        observed_at_utc="2026-07-22T23:38:00Z",
        python_version="3.11.9",
        architecture_bits=64,
        native_module_name="xtpythonclient.cp311-win_amd64.pyd",
        native_module_sha256="5" * 64,
        native_module_byte_length=1147904,
        native_loaded=True,
        rpc_client_present=True,
    )
    return build_compatibility_evidence(
        coverage,
        adjustment,
        sdk,
        evidence_id="qmt-dual-export-offline-sdk-reference-v1",
        observed_at_utc="2026-07-22T23:40:00Z",
    )
