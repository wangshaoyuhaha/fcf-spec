from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    RegisteredLocalDailyExport,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtLocalDailyExportProfile,
    normalize_registered_qmt_daily_export,
)

from .contracts import (
    FINDING_ORDER,
    QmtBatchCompatibilityObservation,
    QmtLocalExportCoverageEvidence,
)


@dataclass(frozen=True)
class QmtRegisteredBatchSpec:
    batch_id: str
    sequence: int
    local_path: Path
    artifact_id: str
    artifact_sha256: str
    byte_length: int
    rights_state: str = "UNRESOLVED"
    retention_state: str = "SESSION_ONLY"


def run_coverage_probe(
    specs: tuple[QmtRegisteredBatchSpec, ...],
    profile: QmtLocalDailyExportProfile,
    *,
    evidence_id: str,
    observed_at_utc: str,
) -> QmtLocalExportCoverageEvidence:
    if not specs or len(specs) > 32:
        raise ValueError("specs must contain one to 32 batches")
    if tuple(item.sequence for item in specs) != tuple(range(1, len(specs) + 1)):
        raise ValueError("batch sequence must be ordered and contiguous")
    if len({item.batch_id for item in specs}) != len(specs):
        raise ValueError("batch identifiers must be unique")

    observations: list[QmtBatchCompatibilityObservation] = []
    combined_findings = {
        "EXPECTED_DATE_ARTIFACT_MISSING",
        "FCP36_RECONCILIATION_NOT_RUN",
        "PAGINATION_NOT_PROVEN",
    }
    for spec in specs:
        path = Path(spec.local_path)
        if path.is_symlink() or not path.is_file():
            raise ValueError("batch must be an existing regular non-symlink file")
        registration = RegisteredLocalDailyExport(
            artifact_id=spec.artifact_id,
            source_id=profile.source_id,
            artifact_sha256=spec.artifact_sha256,
            byte_length=spec.byte_length,
            registered_at_utc=observed_at_utc,
            rights_state=spec.rights_state,
            retention_state=spec.retention_state,
        )
        normalized = normalize_registered_qmt_daily_export(
            path,
            registration,
            profile,
            output_artifact_id=f"{spec.artifact_id}-normalized-probe",
            as_of_utc=observed_at_utc,
        )
        source_findings = set(normalized.manifest.finding_codes)
        if normalized.manifest.row_count == 500:
            source_findings.add("OBSERVED_500_ROW_BATCH")
        combined_findings.update(source_findings)
        observations.append(
            QmtBatchCompatibilityObservation(
                batch_id=spec.batch_id,
                sequence=spec.sequence,
                source_artifact_sha256=registration.artifact_sha256,
                source_byte_length=registration.byte_length,
                normalization_manifest_hash=normalized.manifest.manifest_hash,
                normalized_artifact_sha256=(
                    normalized.manifest.normalized_artifact_sha256
                ),
                row_count=normalized.manifest.row_count,
                actual_start_date=normalized.manifest.actual_start_date,
                actual_end_date=normalized.manifest.actual_end_date,
                finding_codes=tuple(
                    item for item in FINDING_ORDER if item in source_findings
                ),
            )
        )

    row_counts = {item.row_count for item in observations}
    repeated_bound = len(observations) > 1 and len(row_counts) == 1
    return QmtLocalExportCoverageEvidence(
        evidence_id=evidence_id,
        observed_at_utc=observed_at_utc,
        instrument_id=profile.instrument_id,
        profile_hash=profile.profile_hash,
        requested_start_date=profile.requested_start_date,
        requested_end_date=profile.requested_end_date,
        observations=tuple(observations),
        observed_start_date=min(item.actual_start_date for item in observations),
        observed_end_date=max(item.actual_end_date for item in observations),
        repeated_observed_row_count_bound=repeated_bound,
        finding_codes=tuple(
            item for item in FINDING_ORDER if item in combined_findings
        ),
    )


def render_evidence_json(evidence: QmtLocalExportCoverageEvidence) -> str:
    return json.dumps(
        asdict(evidence),
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    )
