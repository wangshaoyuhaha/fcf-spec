from __future__ import annotations

import hashlib
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import canonical_sha256
from apps.fcp_0077_a_share_trusted_data_supply_chain_coverage_evidence_matrix_app_1 import (
    RegisteredImplementationEvidence,
    build_coverage_matrix,
    coverage_requirements,
    current_repository_evidence,
)
from apps.fcp_0078_a_share_publication_availability_clock_contract_app_1 import publication_clock_implementation_evidence
from apps.fcp_0079_a_share_corporate_action_query_policy_lineage_contract_app_1 import price_lineage_implementation_evidence

from .profiles import PROVIDERS, CandidateProviderCompatibilityProfile, candidate_provider_profiles


_PROFILE_PATH = "apps/fcp_0080_a_share_open_candidate_provider_compatibility_profile_app_1/profiles.py"


def provider_profile_set_hash(profiles: tuple[CandidateProviderCompatibilityProfile, ...]) -> str:
    if not isinstance(profiles, tuple) or not all(isinstance(item, CandidateProviderCompatibilityProfile) for item in profiles):
        raise TypeError("profiles must contain CandidateProviderCompatibilityProfile")
    if tuple(item.provider for item in profiles) != PROVIDERS:
        raise ValueError("profiles must cover exact deterministic provider order")
    if len({item.profile_hash for item in profiles}) != len(profiles):
        raise ValueError("provider profile hashes must be unique")
    if any(item.promotion_ready or item.provider_selected or item.claims_data_authority for item in profiles):
        raise ValueError("candidate provider profiles must remain non-authorizing")
    return canonical_sha256({"profile_hashes": [item.profile_hash for item in profiles], "providers": list(PROVIDERS)})


def provider_profile_implementation_evidence(repository_root: str | Path, *, observed_at_utc: str) -> RegisteredImplementationEvidence:
    root = Path(repository_root).resolve()
    path = root.joinpath(*_PROFILE_PATH.split("/"))
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("provider profile evidence escapes repository root") from exc
    if resolved.is_symlink() or not resolved.is_file():
        raise ValueError("provider profile evidence must be a regular tracked file")
    provider_profile_set_hash(candidate_provider_profiles())
    return RegisteredImplementationEvidence(
        component_id="gap093-open-candidate-provider-profiles",
        gap_id="V2-FR-GAP-093",
        repository_path=_PROFILE_PATH,
        artifact_sha256=hashlib.sha256(resolved.read_bytes()).hexdigest(),
        capabilities=("PROVIDER_PROFILE_AKSHARE", "PROVIDER_PROFILE_BAOSTOCK", "PROVIDER_PROFILE_TUSHARE"),
        observed_at_utc=observed_at_utc,
    )


def build_augmented_coverage_matrix(repository_root: str | Path, *, evaluated_at_utc: str):
    return build_coverage_matrix(
        repository_root,
        coverage_requirements(),
        current_repository_evidence(repository_root, observed_at_utc=evaluated_at_utc)
        + (
            publication_clock_implementation_evidence(repository_root, observed_at_utc=evaluated_at_utc),
            price_lineage_implementation_evidence(repository_root, observed_at_utc=evaluated_at_utc),
            provider_profile_implementation_evidence(repository_root, observed_at_utc=evaluated_at_utc),
        ),
        evaluated_at_utc=evaluated_at_utc,
    )
