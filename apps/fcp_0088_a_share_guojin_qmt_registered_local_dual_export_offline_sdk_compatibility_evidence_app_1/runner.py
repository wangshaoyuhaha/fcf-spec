from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtLocalDailyExportProfile,
    compare_registered_qmt_front_adjustment,
)
from apps.fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1 import (
    QmtRegisteredBatchSpec,
    run_coverage_probe,
)

from .builder import build_compatibility_evidence
from .contracts import (
    OfflineSdkAbiObservation,
    QmtDualExportOfflineCompatibilityEvidence,
)


@dataclass(frozen=True)
class QmtRegisteredDualExportSpec:
    raw_path: Path
    raw_artifact_id: str
    raw_artifact_sha256: str
    raw_byte_length: int
    front_path: Path
    front_artifact_id: str
    front_artifact_sha256: str
    front_byte_length: int
    rights_state: str = "UNRESOLVED"
    retention_state: str = "SESSION_ONLY"


def run_registered_local_compatibility(
    spec: QmtRegisteredDualExportSpec,
    profile: QmtLocalDailyExportProfile,
    sdk_observation: OfflineSdkAbiObservation,
    *,
    evidence_id: str,
    observed_at_utc: str,
) -> QmtDualExportOfflineCompatibilityEvidence:
    if type(spec) is not QmtRegisteredDualExportSpec:
        raise TypeError("spec must be exact registered dual-export metadata")
    if type(profile) is not QmtLocalDailyExportProfile:
        raise TypeError("profile must be exact FCP-0035 profile")
    raw_registration = RegisteredLocalDailyExport(
        artifact_id=spec.raw_artifact_id,
        source_id=profile.source_id,
        artifact_sha256=spec.raw_artifact_sha256,
        byte_length=spec.raw_byte_length,
        registered_at_utc=observed_at_utc,
        rights_state=spec.rights_state,
        retention_state=spec.retention_state,
    )
    front_registration = RegisteredLocalDailyExport(
        artifact_id=spec.front_artifact_id,
        source_id=profile.source_id,
        artifact_sha256=spec.front_artifact_sha256,
        byte_length=spec.front_byte_length,
        registered_at_utc=observed_at_utc,
        rights_state=spec.rights_state,
        retention_state=spec.retention_state,
    )
    coverage = run_coverage_probe(
        (
            QmtRegisteredBatchSpec(
                batch_id=f"{spec.raw_artifact_id}-batch",
                sequence=1,
                local_path=Path(spec.raw_path),
                artifact_id=spec.raw_artifact_id,
                artifact_sha256=spec.raw_artifact_sha256,
                byte_length=spec.raw_byte_length,
                rights_state=spec.rights_state,
                retention_state=spec.retention_state,
            ),
        ),
        profile,
        evidence_id=f"{evidence_id}-coverage",
        observed_at_utc=observed_at_utc,
    )
    adjustment = compare_registered_qmt_front_adjustment(
        spec.raw_path,
        raw_registration,
        spec.front_path,
        front_registration,
        profile,
    )
    return build_compatibility_evidence(
        coverage,
        adjustment,
        sdk_observation,
        evidence_id=evidence_id,
        observed_at_utc=observed_at_utc,
    )
