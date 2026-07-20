from pathlib import Path

from apps.browser_product_console_runtime_app_1 import BrowserConsoleRuntime
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    MarketDataAdapterReadinessSnapshot,
)
from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (
    CandidateSourceProfile,
    build_candidate_data_source_onboarding_runtime,
)

from .application import SanitizedSessionEvidenceApplication
from .contracts import CandidateSessionEvidence, RegisteredSessionEvidenceArtifact


def build_sanitized_session_evidence_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    snapshot: MarketDataAdapterReadinessSnapshot,
    profiles: tuple[CandidateSourceProfile, ...],
    profile: CandidateSourceProfile,
    registration: RegisteredSessionEvidenceArtifact,
    evidence: CandidateSessionEvidence,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
    locale_id: str = "zh-CN",
) -> BrowserConsoleRuntime:
    base = build_candidate_data_source_onboarding_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        snapshot=snapshot,
        profiles=profiles,
        port=port,
        title=title,
        locale_id=locale_id,
    )
    application = SanitizedSessionEvidenceApplication(
        base_application=base.application,
        profile=profile,
        registration=registration,
        evidence=evidence,
    )
    return BrowserConsoleRuntime(
        config=base.config,
        index_path=base.index_path,
        application=application,
    )
