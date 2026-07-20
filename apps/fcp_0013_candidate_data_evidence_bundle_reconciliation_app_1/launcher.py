from pathlib import Path

from apps.browser_product_console_runtime_app_1 import BrowserConsoleRuntime
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    MarketDataAdapterReadinessSnapshot,
)
from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (
    CandidateSourceProfile,
)
from apps.fcp_0012_sanitized_candidate_data_session_evidence_intake_app_1 import (
    CandidateSessionEvidence,
    RegisteredSessionEvidenceArtifact,
    build_sanitized_session_evidence_runtime,
)

from .application import CandidateEvidenceBundleApplication
from .contracts import CandidateEvidenceBundle


def build_candidate_evidence_bundle_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    snapshot: MarketDataAdapterReadinessSnapshot,
    profiles: tuple[CandidateSourceProfile, ...],
    profile: CandidateSourceProfile,
    registration: RegisteredSessionEvidenceArtifact,
    evidence: CandidateSessionEvidence,
    bundle: CandidateEvidenceBundle,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
    locale_id: str = "zh-CN",
) -> BrowserConsoleRuntime:
    base = build_sanitized_session_evidence_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        snapshot=snapshot,
        profiles=profiles,
        profile=profile,
        registration=registration,
        evidence=evidence,
        port=port,
        title=title,
        locale_id=locale_id,
    )
    application = CandidateEvidenceBundleApplication(
        base_application=base.application,
        bundle=bundle,
    )
    return BrowserConsoleRuntime(config=base.config, index_path=base.index_path, application=application)
