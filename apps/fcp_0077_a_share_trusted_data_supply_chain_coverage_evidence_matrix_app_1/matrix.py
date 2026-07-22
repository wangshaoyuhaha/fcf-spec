from __future__ import annotations

import hashlib
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import instant

from .contracts import (
    GAP_IDS,
    GapCoverageRequirement,
    GapCoverageRow,
    RegisteredImplementationEvidence,
    TrustedDataSupplyChainCoverageMatrix,
)


def coverage_requirements() -> tuple[GapCoverageRequirement, ...]:
    definitions = (
        (87, ("CANONICAL_TYPED_OBSERVATION", "PROVIDER_EDGE_CONVERSION"), False),
        (
            88,
            (
                "FIRST_TRADABLE_CLOCK",
                "INGEST_CLOCK",
                "POINT_IN_TIME_AVAILABILITY",
                "PUBLICATION_CLOCK",
                "REVISION_CLOCK",
            ),
            True,
        ),
        (
            89,
            (
                "ADJUSTMENT_FACTOR_LINEAGE",
                "CORPORATE_ACTION_LINEAGE",
                "QUERY_POLICY_LINEAGE",
                "RAW_PRICE_LINEAGE",
                "REVISION_CLOCK",
            ),
            True,
        ),
        (90, ("MISSING_BAR_SUSPENSION_POLICY", "TRADING_STATUS_SCHEMA"), True),
        (
            91,
            (
                "RAW_NORMALIZED_RESEARCH_LAYERS",
                "REVISION_CLOCK",
                "RIGHTS_RETENTION_MANIFEST",
            ),
            True,
        ),
        (
            92,
            (
                "CROSS_SOURCE_CONFLICT_QUARANTINE",
                "CROSS_SOURCE_COVERAGE",
                "CROSS_SOURCE_DUPLICATE_OUTLIER",
                "CROSS_SOURCE_UNIT_CLOCK_RECONCILIATION",
            ),
            True,
        ),
        (
            93,
            (
                "PROVIDER_PROFILE_AKSHARE",
                "PROVIDER_PROFILE_BAOSTOCK",
                "PROVIDER_PROFILE_MINIQMT",
                "PROVIDER_PROFILE_RQDATA",
                "PROVIDER_PROFILE_TUSHARE",
            ),
            True,
        ),
    )
    return tuple(
        GapCoverageRequirement(
            gap_id=f"V2-FR-GAP-{number:03d}",
            required_capabilities=capabilities,
            external_evidence_required=external,
        )
        for number, capabilities, external in definitions
    )


def _verified_bytes(root: Path, evidence: RegisteredImplementationEvidence) -> bytes:
    root = root.resolve()
    path = root.joinpath(*evidence.repository_path.split("/"))
    if path.is_symlink():
        raise ValueError("implementation evidence cannot reference a symlink")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("implementation evidence escapes the repository root") from exc
    if not resolved.is_file():
        raise ValueError("implementation evidence must reference a file")
    payload = resolved.read_bytes()
    if hashlib.sha256(payload).hexdigest() != evidence.artifact_sha256:
        raise ValueError("implementation evidence SHA-256 mismatch")
    return payload


def build_coverage_matrix(
    repository_root: str | Path,
    requirements: tuple[GapCoverageRequirement, ...],
    evidence: tuple[RegisteredImplementationEvidence, ...],
    *,
    evaluated_at_utc: str,
) -> TrustedDataSupplyChainCoverageMatrix:
    if not isinstance(requirements, tuple) or not all(
        isinstance(item, GapCoverageRequirement) for item in requirements
    ):
        raise TypeError("requirements must contain GapCoverageRequirement")
    if tuple(item.gap_id for item in requirements) != GAP_IDS:
        raise ValueError("requirements must cover the exact ordered gap range")
    if not isinstance(evidence, tuple) or not all(
        isinstance(item, RegisteredImplementationEvidence) for item in evidence
    ):
        raise TypeError("evidence must contain RegisteredImplementationEvidence")
    evaluated = instant(evaluated_at_utc, "evaluated_at_utc")
    identities = tuple((item.gap_id, item.component_id) for item in evidence)
    if len(set(identities)) != len(identities):
        raise ValueError("implementation evidence identity must be unique")
    root = Path(repository_root)
    for item in evidence:
        if instant(item.observed_at_utc, "observed_at_utc") > evaluated:
            raise ValueError("implementation evidence cannot be observed in the future")
        _verified_bytes(root, item)
    rows = []
    for requirement in requirements:
        matching = tuple(
            sorted(
                (item for item in evidence if item.gap_id == requirement.gap_id),
                key=lambda item: item.component_id,
            )
        )
        observed = tuple(sorted({cap for item in matching for cap in item.capabilities}))
        missing = tuple(
            capability
            for capability in requirement.required_capabilities
            if capability not in observed
        )
        state = (
            "NO_FOUNDATION_EVIDENCE_GAP_OPEN"
            if not matching
            else "FOUNDATION_PARTIAL_GAP_OPEN"
            if missing
            else "FOUNDATION_COVERED_GAP_OPEN"
        )
        rows.append(
            GapCoverageRow(
                requirement=requirement,
                evidence=matching,
                observed_capabilities=observed,
                missing_capabilities=missing,
                coverage_state=state,
            )
        )
    return TrustedDataSupplyChainCoverageMatrix(
        rows=tuple(rows),
        evaluated_at_utc=evaluated_at_utc,
    )


_CURRENT_SPECS = (
    (
        "gap087-canonical-schema",
        87,
        "apps/fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1/contracts.py",
        ("CANONICAL_TYPED_OBSERVATION",),
    ),
    (
        "gap087-local-export-edge",
        87,
        "apps/fcp_0019_a_share_local_export_canonicalization_bridge_app_1/bridge.py",
        ("PROVIDER_EDGE_CONVERSION",),
    ),
    (
        "gap088-clock-foundation",
        88,
        "apps/fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1/contracts.py",
        (
            "FIRST_TRADABLE_CLOCK",
            "INGEST_CLOCK",
            "POINT_IN_TIME_AVAILABILITY",
            "REVISION_CLOCK",
        ),
    ),
    (
        "gap089-price-factor-lineage",
        89,
        "apps/fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1/contracts.py",
        ("ADJUSTMENT_FACTOR_LINEAGE", "RAW_PRICE_LINEAGE", "REVISION_CLOCK"),
    ),
    (
        "gap090-trading-status-contract",
        90,
        "apps/fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1/contracts.py",
        ("MISSING_BAR_SUSPENSION_POLICY", "TRADING_STATUS_SCHEMA"),
    ),
    (
        "gap091-layer-manifest-contract",
        91,
        "apps/fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1/contracts.py",
        (
            "RAW_NORMALIZED_RESEARCH_LAYERS",
            "REVISION_CLOCK",
            "RIGHTS_RETENTION_MANIFEST",
        ),
    ),
    (
        "gap092-cross-source-reconciliation",
        92,
        "apps/fcp_0021_a_share_cross_source_quality_reconciliation_app_1/reconciliation.py",
        ("CROSS_SOURCE_COVERAGE", "CROSS_SOURCE_UNIT_CLOCK_RECONCILIATION"),
    ),
    (
        "gap092-quarantine-scanner",
        92,
        "apps/fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1/scanner.py",
        ("CROSS_SOURCE_CONFLICT_QUARANTINE", "CROSS_SOURCE_DUPLICATE_OUTLIER"),
    ),
    (
        "gap093-rqdata-profile",
        93,
        "apps/fcp_0007_a_share_rqdata_demo_artifact_intake_replay_acceptance_app_1/loader.py",
        ("PROVIDER_PROFILE_RQDATA",),
    ),
    (
        "gap093-miniqmt-profile",
        93,
        "apps/fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1/adapter.py",
        ("PROVIDER_PROFILE_MINIQMT",),
    ),
)


def current_repository_evidence(
    repository_root: str | Path,
    *,
    observed_at_utc: str = "2026-07-23T00:00:00Z",
) -> tuple[RegisteredImplementationEvidence, ...]:
    root = Path(repository_root).resolve()
    items = []
    for component_id, number, relative, capabilities in _CURRENT_SPECS:
        payload = root.joinpath(*relative.split("/")).read_bytes()
        items.append(
            RegisteredImplementationEvidence(
                component_id=component_id,
                gap_id=f"V2-FR-GAP-{number:03d}",
                repository_path=relative,
                artifact_sha256=hashlib.sha256(payload).hexdigest(),
                capabilities=capabilities,
                observed_at_utc=observed_at_utc,
            )
        )
    return tuple(items)
